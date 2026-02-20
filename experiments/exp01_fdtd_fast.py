#!/usr/bin/env python3
"""
FDTD Electromagnetic Simulation of Myelin Waveguide — Optimized.
2D TE mode (Ez, Hx, Hy) with PML boundaries.
All geometry built with vectorized numpy operations.

Measured refractive indices:
  Myelin: 1.44 (de Campos Vidal 1980, Kocsis 1982)
  Axoplasm: 1.38 
  ISF/node: 1.34
"""

import os, sys, time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT, exist_ok=True)

C0 = 3e8
EPS0 = 8.854e-12
MU0 = 4 * np.pi * 1e-7
N_MYELIN = 1.44
N_AXOPLASM = 1.38
N_ISF = 1.34

plt.rcParams.update({
    'figure.facecolor': '#0a0a0a', 'axes.facecolor': '#111111',
    'axes.edgecolor': '#444444', 'axes.labelcolor': '#cccccc',
    'text.color': '#cccccc', 'xtick.color': '#999999', 'ytick.color': '#999999',
    'grid.color': '#222222', 'font.size': 11,
    'legend.facecolor': '#1a1a1a', 'legend.edgecolor': '#333333',
})


class FDTD2D:
    """Minimal vectorized 2D TE FDTD with CPML."""
    
    def __init__(self, nx, ny, dx):
        self.nx, self.ny, self.dx = nx, ny, dx
        self.dt = dx / (C0 * np.sqrt(2)) * 0.99
        self.Ez = np.zeros((nx, ny))
        self.Hx = np.zeros((nx, ny))
        self.Hy = np.zeros((nx, ny))
        self.eps_r = np.ones((nx, ny))
        
        # PML
        pml = 15
        self.pml = pml
        sigma_max = 0.8 * 4 / (dx * np.sqrt(MU0 / EPS0))
        sigma = np.zeros((nx, ny))
        for i in range(pml):
            v = sigma_max * ((pml - i) / pml) ** 3
            sigma[i, :] += v; sigma[-(i+1), :] += v
            sigma[:, i] += v; sigma[:, -(i+1)] += v
        
        self._s = sigma
        self._ca = None  # lazy compute
    
    def _compute_coeffs(self):
        s = self._s
        dt, dx = self.dt, self.dx
        self._ca = (1 - s * dt / (2 * EPS0 * self.eps_r)) / \
                   (1 + s * dt / (2 * EPS0 * self.eps_r))
        self._cb = (dt / (EPS0 * self.eps_r * dx)) / \
                   (1 + s * dt / (2 * EPS0 * self.eps_r))
    
    def step(self):
        if self._ca is None:
            self._compute_coeffs()
        dt, dx = self.dt, self.dx
        self.Hx[:, :-1] -= dt / MU0 * (self.Ez[:, 1:] - self.Ez[:, :-1]) / dx
        self.Hy[:-1, :] += dt / MU0 * (self.Ez[1:, :] - self.Ez[:-1, :]) / dx
        self.Ez[1:, 1:] = self._ca[1:, 1:] * self.Ez[1:, 1:] + \
            self._cb[1:, 1:] * ((self.Hy[1:, 1:] - self.Hy[:-1, 1:]) - \
                                 (self.Hx[1:, 1:] - self.Hx[1:, :-1]))


def build_axon(sim, axon_d_um, g_ratio, segments, center_y=None):
    """
    Build axon geometry. segments = list of ('internode', length_um) or ('node', length_um).
    Returns dict with segment pixel ranges.
    """
    dx_um = sim.dx * 1e6
    if center_y is None:
        center_y = sim.ny // 2
    
    ax_r = int(round(axon_d_um / 2 / dx_um))
    outer_r = int(round(axon_d_um / (2 * g_ratio) / dx_um))
    
    # Y distance arrays
    y = np.arange(sim.ny)
    dy = np.abs(y - center_y)
    
    x = sim.pml + 10
    seg_info = []
    
    for seg_type, length_um in segments:
        length_px = max(1, int(round(length_um / dx_um)))
        x_end = min(x + length_px, sim.nx)
        
        if seg_type == 'internode':
            # Axoplasm core
            mask_core = dy[np.newaxis, :] <= ax_r
            sim.eps_r[x:x_end, :] = np.where(mask_core[:x_end-x], N_AXOPLASM**2, sim.eps_r[x:x_end, :])
            # Myelin sheath
            mask_myelin = (dy[np.newaxis, :] > ax_r) & (dy[np.newaxis, :] <= outer_r)
            sim.eps_r[x:x_end, :] = np.where(mask_myelin[:x_end-x], N_MYELIN**2, sim.eps_r[x:x_end, :])
        elif seg_type == 'node':
            mask_core = dy[np.newaxis, :] <= ax_r
            sim.eps_r[x:x_end, :] = np.where(mask_core[:x_end-x], N_ISF**2, sim.eps_r[x:x_end, :])
        
        seg_info.append((seg_type, x, x_end))
        x = x_end
    
    sim._ca = None  # force recompute
    return {'segments': seg_info, 'center_y': center_y, 'ax_r': ax_r, 'outer_r': outer_r}


def guided_flux(sim, x_pos, center_y, radius):
    y_lo = max(0, center_y - radius)
    y_hi = min(sim.ny, center_y + radius + 1)
    return np.sum(sim.Ez[x_pos, y_lo:y_hi] ** 2)


def run_sim(sim, geo, src_positions, wl_m, n_steps, measure_positions):
    """Run FDTD and return time-averaged flux at measurement positions."""
    freq = C0 / wl_m
    omega = 2 * np.pi * freq
    cy = geo['center_y']
    ar = geo['ax_r']
    
    # Source y-slice
    y_lo = max(0, cy - ar)
    y_hi = min(sim.ny, cy + ar + 1)
    
    flux_accum = {mp: 0.0 for mp in measure_positions}
    n_accum = 0
    warmup = n_steps // 3  # skip transient
    
    for step in range(n_steps):
        t = step * sim.dt
        
        # CW source (with ramp-up)
        ramp = min(1.0, t * freq / 10)
        val = ramp * np.sin(omega * t) * 0.1
        
        for sx in src_positions:
            sim.Ez[sx, y_lo:y_hi] += val
        
        sim.step()
        
        if step >= warmup:
            for mp in measure_positions:
                flux_accum[mp] += guided_flux(sim, mp, cy, ar)
            n_accum += 1
    
    return {mp: flux_accum[mp] / n_accum for mp in measure_positions}


# ============================================================
# EXPERIMENT 1: Transmission vs g-ratio
# ============================================================
def exp_transmission_vs_gratio():
    print("=" * 60)
    print("EXP 1: Waveguide Transmission vs Myelin Thickness (FDTD)")
    print("=" * 60)
    
    dx = 0.03e-6  # 30nm grid
    wl = 600e-9
    internode_um = 15.0
    axon_d = 1.0
    
    g_ratios = [0.60, 0.70, 0.78, 0.85, 0.90, 0.95]
    results = {}
    
    for g in g_ratios:
        nx = int(internode_um / (dx*1e6)) + 60
        ny = 150
        sim = FDTD2D(nx, ny, dx)
        geo = build_axon(sim, axon_d, g, [('internode', internode_um)])
        
        seg = geo['segments'][0]
        src_x = seg[1] + 5
        meas_in = seg[1] + int(0.2 * (seg[2] - seg[1]))
        meas_out = seg[2] - 5
        
        t0 = time.time()
        flux = run_sim(sim, geo, [src_x], wl, 3000, [meas_in, meas_out])
        elapsed = time.time() - t0
        
        T = flux[meas_out] / flux[meas_in] if flux[meas_in] > 0 else 0
        results[g] = T
        myelin_um = axon_d / (2*g) - axon_d / 2
        print(f"  g={g:.2f} (myelin={myelin_um:.3f}μm): T={T:.4f} [{elapsed:.1f}s]")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    gs = sorted(results.keys())
    ax.plot(gs, [results[g] for g in gs], 'o-', color='#ff8844', linewidth=2, markersize=10)
    ax.set_xlabel('g-ratio (higher = thinner myelin)')
    ax.set_ylabel('Guided transmission (30nm FDTD)')
    ax.set_title(f'FDTD: Myelin Waveguide Transmission\nλ=600nm, axon Ø={axon_d}μm, L={internode_um}μm')
    ax.axvline(0.78, color='#00ffaa', ls='--', alpha=0.5, label='Healthy CNS (g≈0.78)')
    ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, 'exp1_transmission_vs_gratio.png')
    fig.savefig(path, dpi=150, bbox_inches='tight'); plt.close()
    print(f"  → {path}")
    return results


# ============================================================
# EXPERIMENT 2: Transmission vs wavelength  
# ============================================================
def exp_transmission_vs_wavelength():
    print("\n" + "=" * 60)
    print("EXP 2: Waveguide Transmission vs Wavelength (FDTD)")
    print("=" * 60)
    
    dx = 0.03e-6
    internode_um = 15.0
    axon_d = 1.0
    g = 0.78
    
    wavelengths = [400, 500, 600, 700, 800, 1000]
    results = {}
    
    for wl_nm in wavelengths:
        wl = wl_nm * 1e-9
        nx = int(internode_um / (dx*1e6)) + 60
        ny = 150
        sim = FDTD2D(nx, ny, dx)
        geo = build_axon(sim, axon_d, g, [('internode', internode_um)])
        
        seg = geo['segments'][0]
        src_x = seg[1] + 5
        meas_in = seg[1] + int(0.2 * (seg[2] - seg[1]))
        meas_out = seg[2] - 5
        
        t0 = time.time()
        flux = run_sim(sim, geo, [src_x], wl, 3000, [meas_in, meas_out])
        elapsed = time.time() - t0
        
        T = flux[meas_out] / flux[meas_in] if flux[meas_in] > 0 else 0
        results[wl_nm] = T
        print(f"  λ={wl_nm}nm: T={T:.4f} [{elapsed:.1f}s]")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    wls = sorted(results.keys())
    ax.plot(wls, [results[w] for w in wls], 'o-', color='#44aaff', linewidth=2, markersize=10)
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Guided transmission')
    ax.set_title(f'FDTD: Wavelength-Dependent Waveguide Transmission\naxon Ø={axon_d}μm, g={g}, L={internode_um}μm')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, 'exp2_transmission_vs_wavelength.png')
    fig.savefig(path, dpi=150, bbox_inches='tight'); plt.close()
    print(f"  → {path}")
    return results


# ============================================================
# EXPERIMENT 3: Node gap transmission
# ============================================================
def exp_node_gap():
    print("\n" + "=" * 60)
    print("EXP 3: Transmission Through Node of Ranvier (FDTD)")
    print("=" * 60)
    
    dx = 0.03e-6
    wl = 600e-9
    axon_d = 1.0
    g = 0.78
    int_len = 10.0
    
    node_lengths = [0.5, 1.0, 1.5, 2.0, 3.0]
    results = {}
    
    # Control: no node (continuous myelin)
    nx = int(2 * int_len / (dx*1e6)) + 60
    ny = 150
    sim = FDTD2D(nx, ny, dx)
    geo = build_axon(sim, axon_d, g, [('internode', 2 * int_len)])
    seg = geo['segments'][0]
    src_x = seg[1] + 5
    mid = (seg[1] + seg[2]) // 2
    meas_out = seg[2] - 5
    flux = run_sim(sim, geo, [src_x], wl, 3000, [mid, meas_out])
    T_control = flux[meas_out] / flux[mid] if flux[mid] > 0 else 0
    print(f"  Control (no node): T={T_control:.4f}")
    
    for nl in node_lengths:
        total_um = 2 * int_len + nl
        nx = int(total_um / (dx*1e6)) + 60
        sim = FDTD2D(nx, ny, dx)
        geo = build_axon(sim, axon_d, g, [
            ('internode', int_len), ('node', nl), ('internode', int_len)
        ])
        
        segs = geo['segments']
        src_x = segs[0][1] + 5
        meas_before = segs[0][2] - 3  # just before node
        meas_after = segs[2][1] + 3    # just after node
        
        t0 = time.time()
        flux = run_sim(sim, geo, [src_x], wl, 4000, [meas_before, meas_after])
        elapsed = time.time() - t0
        
        T = flux[meas_after] / flux[meas_before] if flux[meas_before] > 0 else 0
        results[nl] = T
        print(f"  Node={nl}μm: T={T:.4f} (loss={1-T:.1%}) [{elapsed:.1f}s]")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    nls = sorted(results.keys())
    ax.plot(nls, [results[n] for n in nls], 'o-', color='#ff4466', linewidth=2, markersize=10)
    ax.axhline(T_control, color='#00ffaa', ls='--', alpha=0.5, label=f'No node (control): {T_control:.3f}')
    ax.set_xlabel('Node of Ranvier gap (μm)')
    ax.set_ylabel('Transmission across node')
    ax.set_title(f'FDTD: How Much Light Survives the Node Gap?\nλ=600nm, axon Ø={axon_d}μm, g={g}')
    ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, 'exp3_node_gap.png')
    fig.savefig(path, dpi=150, bbox_inches='tight'); plt.close()
    print(f"  → {path}")
    return results


# ============================================================
# EXPERIMENT 4: RELAY vs PASSIVE (the key test)
# ============================================================
def exp_relay_vs_passive():
    print("\n" + "=" * 60)
    print("EXP 4: RELAY vs PASSIVE — Maxwell's Equations Decide")
    print("=" * 60)
    
    dx = 0.03e-6
    wl = 600e-9
    axon_d = 1.0
    g = 0.78
    int_len = 10.0
    node_len = 1.0
    n_int = 5
    
    # Build segment list
    segs = []
    for i in range(n_int):
        segs.append(('internode', int_len))
        if i < n_int - 1:
            segs.append(('node', node_len))
    
    total_um = n_int * int_len + (n_int - 1) * node_len
    nx = int(total_um / (dx*1e6)) + 60
    ny = 150
    
    all_results = {}
    
    for mode in ['passive', 'relay']:
        print(f"\n  --- {mode.upper()} ---")
        sim = FDTD2D(nx, ny, dx)
        geo = build_axon(sim, axon_d, g, segs)
        
        # Source positions
        src_first = geo['segments'][0][1] + 3
        node_srcs = [((s[1]+s[2])//2) for s in geo['segments'] if s[0] == 'node']
        
        if mode == 'passive':
            sources = [src_first]
        else:
            sources = [src_first] + node_srcs
        
        # Measure at center of each internode
        meas = []
        for s in geo['segments']:
            if s[0] == 'internode':
                meas.append((s[1] + s[2]) // 2)
        
        t0 = time.time()
        flux = run_sim(sim, geo, sources, wl, 5000, meas)
        elapsed = time.time() - t0
        
        # Normalize to first internode
        f0 = flux[meas[0]]
        normed = []
        for i, mp in enumerate(meas):
            val = flux[mp] / f0 if f0 > 0 else 0
            normed.append(val)
            print(f"    Internode {i+1}: {val:.3f}×")
        
        all_results[mode] = normed
        print(f"    [{elapsed:.1f}s]")
    
    # Also compute theoretical predictions
    # Get actual T from the passive data
    passive = all_results['passive']
    if len(passive) >= 2 and passive[0] > 0:
        # T_eff per internode+node from passive decay
        T_eff = (passive[-1] / passive[0]) ** (1 / (len(passive) - 1)) if passive[0] > 0 else 0.5
        print(f"\n  Effective T per segment (from passive): {T_eff:.3f}")
        
        # Theoretical relay: S_n = E*(1-T^(n+1))/(1-T), normalized to S_0=E
        n_nodes = len(passive)
        E = 1.0
        theory_relay = [E * (1 - T_eff**(n+1)) / (1 - T_eff) for n in range(n_nodes)]
        theory_relay = [t / theory_relay[0] for t in theory_relay]
        
        theory_passive = [T_eff**n for n in range(n_nodes)]
    else:
        theory_relay = None
        theory_passive = None
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 7))
    x_nodes = list(range(1, len(passive) + 1))
    
    ax.plot(x_nodes, all_results['passive'], 'v-', color='#ff4466', linewidth=2, 
            markersize=12, label='FDTD: Passive (source at start only)')
    ax.plot(x_nodes, all_results['relay'], '^-', color='#00ffaa', linewidth=2,
            markersize=12, label='FDTD: Relay (source at every node)')
    
    if theory_passive:
        ax.plot(x_nodes, theory_passive, '--', color='#ff4466', alpha=0.5, linewidth=1.5,
                label=f'Theory: T^n (T={T_eff:.3f})')
        ax.plot(x_nodes, theory_relay, '--', color='#00ffaa', alpha=0.5, linewidth=1.5,
                label=f'Theory: E(1-T^n)/(1-T)')
    
    ax.set_xlabel('Internode number', fontsize=13)
    ax.set_ylabel('Guided flux (normalized to internode 1)', fontsize=13)
    ax.set_title('FDTD Electromagnetic Simulation: Relay vs Passive Propagation\n'
                 f'{n_int} internodes, λ=600nm, axon Ø={axon_d}μm, g={g}', fontsize=14)
    ax.legend(fontsize=11, loc='center right')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(x_nodes)
    
    fig.tight_layout()
    path = os.path.join(OUT, 'exp4_relay_vs_passive.png')
    fig.savefig(path, dpi=150, bbox_inches='tight'); plt.close()
    print(f"\n  → {path}")
    
    return all_results


# ============================================================
if __name__ == '__main__':
    t_total = time.time()
    print("BIOPHOTON WAVEGUIDE — FDTD EXPERIMENTS")
    print("Maxwell's equations, 2D TE mode, PML boundaries")
    print(f"Measured refractive indices: myelin={N_MYELIN}, axoplasm={N_AXOPLASM}, ISF={N_ISF}")
    print()
    
    r1 = exp_transmission_vs_gratio()
    r2 = exp_transmission_vs_wavelength()
    r3 = exp_node_gap()
    r4 = exp_relay_vs_passive()
    
    print(f"\nTotal time: {time.time()-t_total:.0f}s")
    print(f"Results: {OUT}/")
