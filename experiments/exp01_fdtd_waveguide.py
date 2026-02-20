#!/usr/bin/env python3
"""
EXPERIMENT 01: FDTD Electromagnetic Simulation of Myelin Waveguide

Solve Maxwell's equations directly on a 2D grid to determine:
1. Whether a myelin sheath actually guides light (mode confinement)
2. Transmission as a function of wavelength and myelin thickness
3. What happens at a node of Ranvier (gap in the sheath)
4. Relay vs passive: does adding a source at the node change propagation?

This is REAL electromagnetic simulation, not transfer matrix approximation.
Uses the fdtd library (finite-difference time-domain).

All parameters from measured values:
- Myelin refractive index: 1.44 (Kocsis et al. 1982; de Campos Vidal et al. 1980)
- Axoplasm refractive index: 1.38 (similar to cytoplasm)
- Interstitial fluid: 1.34 (close to water)
- Axon diameter: 0.5-2.0 μm (CNS myelinated axons)
- Myelin thickness: determined by g-ratio
- Internode length: ~100-1000 μm (we use scaled versions for computational feasibility)
- Node of Ranvier length: 0.7-1.4 μm
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'experiments', 'results')
os.makedirs(OUT, exist_ok=True)

# ============================================================
# We'll build our own 2D FDTD from scratch for full control.
# The fdtd library is 3D and overkill — a clean 2D TE solver
# gives us exactly what we need with much less compute.
# ============================================================

# Physical constants
C0 = 3e8           # speed of light (m/s)
EPS0 = 8.854e-12   # vacuum permittivity
MU0 = 4 * np.pi * 1e-7  # vacuum permeability

# Material properties (measured values)
N_MYELIN = 1.44     # Kocsis et al. 1982
N_AXOPLASM = 1.38   # cytoplasm-like
N_ISF = 1.34        # interstitial fluid (near water)
N_NODE = 1.36       # node of Ranvier (exposed axon membrane + ECF)


def eps_r(n):
    """Relative permittivity from refractive index."""
    return n ** 2


class FDTD2D_TE:
    """
    2D Finite-Difference Time-Domain solver (TE polarization: Ez, Hx, Hy).
    
    Uses Yee grid with PML absorbing boundary conditions.
    """
    
    def __init__(self, nx, ny, dx, pml_thick=20):
        self.nx = nx
        self.ny = ny
        self.dx = dx  # grid spacing (m)
        self.dy = dx  # square grid
        self.dt = dx / (C0 * np.sqrt(2)) * 0.99  # Courant stability
        self.pml_thick = pml_thick
        
        # Fields
        self.Ez = np.zeros((nx, ny))
        self.Hx = np.zeros((nx, ny))
        self.Hy = np.zeros((nx, ny))
        
        # Material grid (relative permittivity)
        self.eps_r = np.ones((nx, ny))
        
        # PML conductivity profiles
        self.sigma_x = np.zeros((nx, ny))
        self.sigma_y = np.zeros((nx, ny))
        self._setup_pml()
        
        # Coefficients (computed after setting materials)
        self._coefficients_dirty = True
    
    def _setup_pml(self):
        """Polynomial graded PML absorbing boundaries."""
        sigma_max = 0.8 * (3 + 1) / (self.dx * np.sqrt(MU0 / EPS0))
        p = 3  # polynomial order
        
        for i in range(self.pml_thick):
            val = sigma_max * ((self.pml_thick - i) / self.pml_thick) ** p
            self.sigma_x[i, :] = val
            self.sigma_x[-(i+1), :] = val
            self.sigma_y[:, i] = val
            self.sigma_y[:, -(i+1)] = val
    
    def _update_coefficients(self):
        """Precompute update coefficients including PML."""
        s = self.sigma_x + self.sigma_y
        self.ca = (1 - s * self.dt / (2 * EPS0 * self.eps_r)) / \
                  (1 + s * self.dt / (2 * EPS0 * self.eps_r))
        self.cb = (self.dt / (EPS0 * self.eps_r * self.dx)) / \
                  (1 + s * self.dt / (2 * EPS0 * self.eps_r))
        self._coefficients_dirty = False
    
    def set_material(self, mask, n):
        """Set refractive index n in region defined by boolean mask."""
        self.eps_r[mask] = eps_r(n)
        self._coefficients_dirty = True
    
    def step(self):
        """Advance one timestep."""
        if self._coefficients_dirty:
            self._update_coefficients()
        
        # Update H fields
        self.Hx[:, :-1] -= self.dt / MU0 * (self.Ez[:, 1:] - self.Ez[:, :-1]) / self.dy
        self.Hy[:-1, :] += self.dt / MU0 * (self.Ez[1:, :] - self.Ez[:-1, :]) / self.dx
        
        # Update E field
        self.Ez[1:, 1:] = self.ca[1:, 1:] * self.Ez[1:, 1:] + \
                           self.cb[1:, 1:] * ((self.Hy[1:, 1:] - self.Hy[:-1, 1:]) - \
                                               (self.Hx[1:, 1:] - self.Hx[1:, :-1]))
    
    def add_source(self, x, y, value):
        """Add soft source at (x, y)."""
        self.Ez[x, y] += value


def build_axon_geometry(sim, center_y, axon_diameter_um, g_ratio, 
                         internode_length_um, node_length_um=1.0,
                         n_internodes=1, include_node=True):
    """
    Build a myelinated axon on the FDTD grid.
    
    Axon runs along x-axis centered at center_y.
    Returns dict with geometry info.
    """
    dx_um = sim.dx * 1e6  # grid spacing in μm
    
    axon_radius_px = int(round(axon_diameter_um / 2 / dx_um))
    outer_radius_px = int(round(axon_diameter_um / (2 * g_ratio) / dx_um))
    node_length_px = max(1, int(round(node_length_um / dx_um)))
    internode_length_px = int(round(internode_length_um / dx_um))
    
    pml = sim.pml_thick
    start_x = pml + 10  # buffer after PML
    
    segments = []
    x = start_x
    
    for seg in range(n_internodes):
        # Internode (myelinated)
        for ix in range(x, x + internode_length_px):
            if ix >= sim.nx:
                break
            for iy in range(sim.ny):
                dy = abs(iy - center_y)
                if dy <= axon_radius_px:
                    sim.eps_r[ix, iy] = eps_r(N_AXOPLASM)
                elif dy <= outer_radius_px:
                    sim.eps_r[ix, iy] = eps_r(N_MYELIN)
        
        segments.append(('internode', x, x + internode_length_px))
        x += internode_length_px
        
        # Node of Ranvier (gap)
        if include_node and seg < n_internodes - 1:
            for ix in range(x, x + node_length_px):
                if ix >= sim.nx:
                    break
                for iy in range(sim.ny):
                    dy = abs(iy - center_y)
                    if dy <= axon_radius_px:
                        sim.eps_r[ix, iy] = eps_r(N_NODE)
            segments.append(('node', x, x + node_length_px))
            x += node_length_px
    
    sim._coefficients_dirty = True
    
    return {
        'segments': segments,
        'start_x': start_x,
        'end_x': x,
        'center_y': center_y,
        'axon_radius_px': axon_radius_px,
        'outer_radius_px': outer_radius_px,
    }


def measure_flux(sim, x_pos, center_y, radius_px):
    """Measure total |Ez|² within the axon core at position x."""
    y_lo = max(0, center_y - radius_px)
    y_hi = min(sim.ny, center_y + radius_px + 1)
    return np.sum(sim.Ez[x_pos, y_lo:y_hi] ** 2)


def measure_external_flux(sim, x_pos, center_y, outer_radius_px, extent=10):
    """Measure |Ez|² outside the myelin sheath at position x."""
    y_above = min(sim.ny, center_y + outer_radius_px + extent)
    y_below = max(0, center_y - outer_radius_px - extent)
    
    flux = np.sum(sim.Ez[x_pos, center_y + outer_radius_px:y_above] ** 2)
    flux += np.sum(sim.Ez[x_pos, y_below:center_y - outer_radius_px] ** 2)
    return flux


# ============================================================
# EXPERIMENT 1A: Single internode transmission vs wavelength
# ============================================================
def exp1a_transmission_vs_wavelength():
    """
    Measure how much light a single internode transmits at different wavelengths.
    This is the fundamental measurement — does myelin actually guide light?
    """
    print("=" * 60)
    print("EXP 1A: Single Internode Transmission vs Wavelength")
    print("=" * 60)
    
    # Grid parameters — scale down for computational feasibility
    # Real internode is ~1mm; we simulate 50μm (scaling is valid for
    # modes that depend on cross-section, not length)
    dx = 0.02e-6  # 20nm grid spacing (need ~λ/20 for accuracy)
    internode_length_um = 30.0
    axon_diameter_um = 1.0
    g_ratio = 0.78
    
    nx = int(internode_length_um / (dx * 1e6)) + 80  # + PML buffer
    ny = 200  # enough for cross-section
    
    wavelengths_nm = [400, 500, 600, 700, 800, 900, 1000]
    results = {}
    
    for wl_nm in wavelengths_nm:
        wl = wl_nm * 1e-9  # convert to meters
        freq = C0 / wl
        omega = 2 * np.pi * freq
        
        print(f"\n  λ = {wl_nm}nm (grid: {nx}x{ny}, dx={dx*1e9:.0f}nm)")
        
        sim = FDTD2D_TE(nx, ny, dx)
        center_y = ny // 2
        
        geo = build_axon_geometry(sim, center_y, axon_diameter_um, g_ratio,
                                   internode_length_um, include_node=False, n_internodes=1)
        
        # Source: gaussian pulse at start of internode, within axon core
        src_x = geo['start_x'] + 5
        measure_in_x = geo['start_x'] + int(0.3 * (geo['end_x'] - geo['start_x']))
        measure_out_x = geo['end_x'] - 10
        
        n_steps = int(internode_length_um * 1e-6 / C0 * N_MYELIN * 4 / sim.dt)
        n_steps = min(n_steps, 8000)  # cap for speed
        
        flux_in = []
        flux_out = []
        
        for step in range(n_steps):
            t = step * sim.dt
            
            # Gaussian-modulated sinusoidal source (within axon core)
            pulse_width = 5 / freq  # 5 cycles
            t_center = 2 * pulse_width
            envelope = np.exp(-((t - t_center) / pulse_width) ** 2)
            src_val = envelope * np.sin(omega * t)
            
            for dy in range(-geo['axon_radius_px'], geo['axon_radius_px'] + 1):
                sim.add_source(src_x, center_y + dy, src_val * 0.1)
            
            sim.step()
            
            # Record flux at input and output planes
            flux_in.append(measure_flux(sim, measure_in_x, center_y, geo['axon_radius_px']))
            flux_out.append(measure_flux(sim, measure_out_x, center_y, geo['axon_radius_px']))
        
        # Transmission = integrated output / integrated input
        total_in = np.sum(flux_in)
        total_out = np.sum(flux_out)
        T = total_out / total_in if total_in > 0 else 0
        
        results[wl_nm] = {
            'transmission': T,
            'flux_in': np.array(flux_in),
            'flux_out': np.array(flux_out),
        }
        print(f"    T = {T:.4f} ({T*100:.1f}%)")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    wls = sorted(results.keys())
    Ts = [results[w]['transmission'] for w in wls]
    
    ax = axes[0]
    ax.plot(wls, Ts, 'o-', color='#00ffaa', linewidth=2, markersize=8)
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmission')
    ax.set_title(f'Single Internode Transmission (FDTD)\n'
                 f'axon Ø={axon_diameter_um}μm, g={g_ratio}, L={internode_length_um}μm')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.1)
    
    # Time traces for a few wavelengths
    ax = axes[1]
    for wl_nm in [400, 600, 800]:
        if wl_nm in results:
            t_arr = np.arange(len(results[wl_nm]['flux_out'])) * sim.dt * 1e15  # femtoseconds
            ax.plot(t_arr, results[wl_nm]['flux_out'] / max(results[wl_nm]['flux_out'].max(), 1e-30),
                    label=f'{wl_nm}nm', linewidth=1.5)
    ax.set_xlabel('Time (fs)')
    ax.set_ylabel('Normalized flux at output')
    ax.set_title('Pulse arrival at output plane')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    path = os.path.join(OUT, 'exp1a_transmission_vs_wavelength.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {path}")
    
    return results


# ============================================================
# EXPERIMENT 1B: Transmission vs g-ratio (myelin thickness)
# ============================================================
def exp1b_transmission_vs_gratio():
    """
    At a fixed wavelength, how does transmission change with myelin thickness?
    This is the key test: does demyelination (higher g-ratio) reduce transmission?
    """
    print("\n" + "=" * 60)
    print("EXP 1B: Transmission vs G-Ratio at λ=600nm")
    print("=" * 60)
    
    dx = 0.02e-6
    internode_length_um = 30.0
    axon_diameter_um = 1.0
    wl = 600e-9
    freq = C0 / wl
    omega = 2 * np.pi * freq
    
    g_ratios = [0.60, 0.70, 0.78, 0.85, 0.90, 0.95, 0.99]
    results = {}
    
    ny = 200
    
    for g in g_ratios:
        nx = int(internode_length_um / (dx * 1e6)) + 80
        
        sim = FDTD2D_TE(nx, ny, dx)
        center_y = ny // 2
        
        geo = build_axon_geometry(sim, center_y, axon_diameter_um, g,
                                   internode_length_um, include_node=False, n_internodes=1)
        
        src_x = geo['start_x'] + 5
        measure_in_x = geo['start_x'] + int(0.3 * (geo['end_x'] - geo['start_x']))
        measure_out_x = geo['end_x'] - 10
        
        n_steps = 6000
        flux_in = []
        flux_out = []
        
        for step in range(n_steps):
            t = step * sim.dt
            pulse_width = 5 / freq
            t_center = 2 * pulse_width
            envelope = np.exp(-((t - t_center) / pulse_width) ** 2)
            src_val = envelope * np.sin(omega * t)
            
            for dy in range(-geo['axon_radius_px'], geo['axon_radius_px'] + 1):
                sim.add_source(src_x, center_y + dy, src_val * 0.1)
            
            sim.step()
            flux_in.append(measure_flux(sim, measure_in_x, center_y, geo['axon_radius_px']))
            flux_out.append(measure_flux(sim, measure_out_x, center_y, geo['axon_radius_px']))
        
        total_in = np.sum(flux_in)
        total_out = np.sum(flux_out)
        T = total_out / total_in if total_in > 0 else 0
        
        # Also measure external leakage
        ext_flux = []
        for step_x in range(geo['start_x'], geo['end_x'], 20):
            ext_flux.append(measure_external_flux(sim, step_x, center_y, geo['outer_radius_px']))
        
        results[g] = {
            'transmission': T,
            'external_leakage': np.mean(ext_flux) if ext_flux else 0,
        }
        myelin_um = axon_diameter_um / (2 * g) - axon_diameter_um / 2
        print(f"  g={g:.2f} (myelin={myelin_um:.3f}μm): T={T:.4f} ({T*100:.1f}%)")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    gs = sorted(results.keys())
    Ts = [results[g]['transmission'] for g in gs]
    
    ax.plot(gs, Ts, 'o-', color='#ff8844', linewidth=2, markersize=8)
    ax.set_xlabel('g-ratio (higher = thinner myelin)')
    ax.set_ylabel('Transmission through 30μm internode')
    ax.set_title('FDTD: Does Thinner Myelin Reduce Waveguide Transmission?\n'
                 f'λ=600nm, axon Ø={axon_diameter_um}μm')
    ax.grid(True, alpha=0.3)
    ax.axvline(0.78, color='#00ffaa', linestyle='--', alpha=0.5, label='Healthy g=0.78')
    ax.legend()
    
    fig.tight_layout()
    path = os.path.join(OUT, 'exp1b_transmission_vs_gratio.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {path}")
    
    return results


# ============================================================
# EXPERIMENT 1C: Node of Ranvier — gap transmission
# ============================================================
def exp1c_node_gap():
    """
    What happens when light hits a node of Ranvier (gap in the myelin)?
    How much passes through vs leaks out?
    """
    print("\n" + "=" * 60)
    print("EXP 1C: Transmission Through Node of Ranvier Gap")
    print("=" * 60)
    
    dx = 0.02e-6
    axon_diameter_um = 1.0
    g_ratio = 0.78
    wl = 600e-9
    freq = C0 / wl
    omega = 2 * np.pi * freq
    
    # Two internodes with a node gap between them
    internode_length_um = 20.0
    node_lengths_um = [0.5, 1.0, 1.5, 2.0]
    
    ny = 200
    results = {}
    
    for node_len in node_lengths_um:
        total_um = 2 * internode_length_um + node_len
        nx = int(total_um / (dx * 1e6)) + 80
        
        sim = FDTD2D_TE(nx, ny, dx)
        center_y = ny // 2
        
        geo = build_axon_geometry(sim, center_y, axon_diameter_um, g_ratio,
                                   internode_length_um, node_length_um=node_len,
                                   n_internodes=2, include_node=True)
        
        src_x = geo['start_x'] + 5
        
        # Measure before and after node
        node_seg = [s for s in geo['segments'] if s[0] == 'node']
        if not node_seg:
            continue
        node_start = node_seg[0][1]
        node_end = node_seg[0][2]
        
        measure_before = node_start - 5
        measure_after = node_end + 5
        
        n_steps = 8000
        flux_before = []
        flux_after = []
        
        for step in range(n_steps):
            t = step * sim.dt
            pulse_width = 5 / freq
            t_center = 2 * pulse_width
            envelope = np.exp(-((t - t_center) / pulse_width) ** 2)
            src_val = envelope * np.sin(omega * t)
            
            for dy in range(-geo['axon_radius_px'], geo['axon_radius_px'] + 1):
                sim.add_source(src_x, center_y + dy, src_val * 0.1)
            
            sim.step()
            flux_before.append(measure_flux(sim, measure_before, center_y, geo['axon_radius_px']))
            flux_after.append(measure_flux(sim, measure_after, center_y, geo['axon_radius_px']))
        
        total_before = np.sum(flux_before)
        total_after = np.sum(flux_after)
        T_node = total_after / total_before if total_before > 0 else 0
        
        results[node_len] = {
            'transmission': T_node,
        }
        print(f"  Node gap={node_len}μm: T_node={T_node:.4f} ({T_node*100:.1f}%)")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    nls = sorted(results.keys())
    Ts = [results[n]['transmission'] for n in nls]
    
    ax.plot(nls, Ts, 'o-', color='#44aaff', linewidth=2, markersize=8)
    ax.set_xlabel('Node of Ranvier gap length (μm)')
    ax.set_ylabel('Transmission through node')
    ax.set_title('FDTD: How Much Light Survives the Node Gap?\n'
                 f'λ=600nm, axon Ø={axon_diameter_um}μm, g={g_ratio}')
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    path = os.path.join(OUT, 'exp1c_node_gap_transmission.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {path}")
    
    return results


# ============================================================
# EXPERIMENT 1D: The Relay Test
# ============================================================
def exp1d_relay_vs_passive():
    """
    THE KEY EXPERIMENT.
    
    Simulate 3 internodes + 2 nodes.
    Case A (passive): Source at node 0 only. Measure decay.
    Case B (relay): Source at ALL nodes. Measure buildup.
    
    If the relay model is correct, Case B should show signal
    increasing and plateauing. Case A should show decay.
    """
    print("\n" + "=" * 60)
    print("EXP 1D: RELAY vs PASSIVE — The Key Test")
    print("=" * 60)
    
    dx = 0.02e-6
    axon_diameter_um = 1.0
    g_ratio = 0.78
    wl = 600e-9
    freq = C0 / wl
    omega = 2 * np.pi * freq
    
    internode_length_um = 20.0
    node_length_um = 1.0
    n_internodes = 4
    
    total_um = n_internodes * internode_length_um + (n_internodes - 1) * node_length_um
    ny = 200
    nx = int(total_um / (dx * 1e6)) + 80
    
    # Run twice: passive and relay
    for mode in ['passive', 'relay']:
        print(f"\n  --- {mode.upper()} MODE ---")
        
        sim = FDTD2D_TE(nx, ny, dx)
        center_y = ny // 2
        
        geo = build_axon_geometry(sim, center_y, axon_diameter_um, g_ratio,
                                   internode_length_um, node_length_um=node_length_um,
                                   n_internodes=n_internodes, include_node=True)
        
        # Identify source positions (at each node)
        node_positions = []
        for seg_type, seg_start, seg_end in geo['segments']:
            if seg_type == 'node':
                node_positions.append((seg_start + seg_end) // 2)
        
        # First source always at beginning of first internode
        first_src = geo['start_x'] + 5
        
        # Measurement points: middle of each internode
        measure_points = []
        for seg_type, seg_start, seg_end in geo['segments']:
            if seg_type == 'internode':
                measure_points.append((seg_start + seg_end) // 2)
        
        n_steps = 10000
        flux_history = {mp: [] for mp in measure_points}
        
        for step in range(n_steps):
            t = step * sim.dt
            pulse_width = 8 / freq
            t_center = 2 * pulse_width
            envelope = np.exp(-((t - t_center) / pulse_width) ** 2)
            # Use continuous sinusoid after initial pulse
            if t > 4 * pulse_width:
                src_val = 0.1 * np.sin(omega * t)
            else:
                src_val = 0.1 * envelope * np.sin(omega * t)
            
            # Source at first position always
            for dy in range(-geo['axon_radius_px'], geo['axon_radius_px'] + 1):
                sim.add_source(first_src, center_y + dy, src_val)
            
            # In relay mode, add sources at each node
            if mode == 'relay':
                for np_x in node_positions:
                    for dy in range(-geo['axon_radius_px'], geo['axon_radius_px'] + 1):
                        sim.add_source(np_x, center_y + dy, src_val)
            
            sim.step()
            
            for mp in measure_points:
                flux_history[mp].append(
                    measure_flux(sim, mp, center_y, geo['axon_radius_px']))
        
        # Time-averaged flux at each measurement point (use last 30%)
        avg_flux = {}
        for i, mp in enumerate(measure_points):
            fh = np.array(flux_history[mp])
            n30 = int(0.3 * len(fh))
            avg_flux[i] = np.mean(fh[-n30:])
        
        # Normalize to first internode
        norm = avg_flux[0] if avg_flux[0] > 0 else 1
        for i in avg_flux:
            print(f"    Internode {i+1}: {avg_flux[i]/norm:.3f}× (relative to first)")
        
        if mode == 'passive':
            passive_flux = {i: avg_flux[i]/norm for i in avg_flux}
        else:
            relay_flux = {i: avg_flux[i]/norm for i in avg_flux}
    
    # Plot comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    nodes = sorted(passive_flux.keys())
    ax.plot([n+1 for n in nodes], [passive_flux[n] for n in nodes], 
            'o-', color='#ff4466', linewidth=2, markersize=10, label='Passive (source at node 0 only)')
    ax.plot([n+1 for n in nodes], [relay_flux[n] for n in nodes],
            's-', color='#00ffaa', linewidth=2, markersize=10, label='Relay (source at every node)')
    
    ax.set_xlabel('Internode number')
    ax.set_ylabel('Time-averaged guided flux (normalized)')
    ax.set_title('FDTD Experiment: Relay vs Passive Propagation\n'
                 f'{n_internodes} internodes, λ=600nm, g={g_ratio}')
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xticks([n+1 for n in nodes])
    
    fig.tight_layout()
    path = os.path.join(OUT, 'exp1d_relay_vs_passive.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {path}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("BIOPHOTON WAVEGUIDE FDTD EXPERIMENTS")
    print("Solving Maxwell's equations on a 2D Yee grid")
    print("All parameters from measured values in literature")
    print()
    
    r1a = exp1a_transmission_vs_wavelength()
    r1b = exp1b_transmission_vs_gratio()
    r1c = exp1c_node_gap()
    exp1d_relay_vs_passive()
    
    print("\n" + "=" * 60)
    print("ALL EXPERIMENTS COMPLETE")
    print(f"Results in: {OUT}/")
    print("=" * 60)
