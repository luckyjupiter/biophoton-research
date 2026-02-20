#!/usr/bin/env python3
"""
Relay model visualization suite.

Generates publication-quality figures showing:
1. Relay vs pure-loss signal across nodes (the core prediction)
2. Steady-state convergence for different transmission values
3. Cuprizone timeline: dual-signature (external up, internal down)
4. Parameter sensitivity: how T affects steady-state

All figures are grounded in math and measured parameters.
No speculative spectral predictions.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'viz_output')
os.makedirs(OUT, exist_ok=True)

# ─── Style ───
plt.rcParams.update({
    'figure.facecolor': '#0a0a0a',
    'axes.facecolor': '#111111',
    'axes.edgecolor': '#444444',
    'axes.labelcolor': '#cccccc',
    'text.color': '#cccccc',
    'xtick.color': '#999999',
    'ytick.color': '#999999',
    'grid.color': '#222222',
    'grid.alpha': 0.5,
    'font.size': 11,
    'axes.titlesize': 13,
    'legend.fontsize': 9,
    'legend.facecolor': '#1a1a1a',
    'legend.edgecolor': '#333333',
})


def fig1_relay_vs_pure_loss():
    """The core figure: relay converges to steady state, pure-loss decays to zero."""
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    T_values = [0.95, 0.90, 0.80, 0.70]
    colors = ['#00ffaa', '#44aaff', '#ff8844', '#ff4466']
    E = 1.0  # normalized emission per node
    n_nodes = 30
    
    # Left: relay model
    ax = axes[0]
    for T, c in zip(T_values, colors):
        signal = np.zeros(n_nodes + 1)
        signal[0] = E
        for i in range(1, n_nodes + 1):
            signal[i] = signal[i-1] * T + E
        steady = E / (1 - T)
        ax.plot(range(n_nodes + 1), signal, color=c, linewidth=2, 
                label=f'T={T:.2f} → SS={steady:.1f}')
        ax.axhline(steady, color=c, linestyle='--', alpha=0.4, linewidth=1)
    
    ax.set_xlabel('Node number')
    ax.set_ylabel('Signal (normalized to single-node emission)')
    ax.set_title('Relay Model: E/(1-T) Steady State')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, n_nodes)
    
    # Right: pure-loss model (no re-emission)
    ax = axes[1]
    for T, c in zip(T_values, colors):
        signal = np.zeros(n_nodes + 1)
        signal[0] = E
        for i in range(1, n_nodes + 1):
            signal[i] = signal[i-1] * T  # no +E
        ax.plot(range(n_nodes + 1), signal, color=c, linewidth=2,
                label=f'T={T:.2f}')
    
    ax.set_xlabel('Node number')
    ax.set_ylabel('Signal (normalized)')
    ax.set_title('Pure-Loss Model: Exponential Decay')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, n_nodes)
    ax.set_ylim(0, max(1.2, ax.get_ylim()[1]))
    
    fig.suptitle('Node-to-Node Photon Relay vs Passive Loss', fontsize=15, y=1.02)
    fig.tight_layout()
    path = os.path.join(OUT, 'relay_vs_pure_loss.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


def fig2_convergence_rate():
    """How fast does the relay reach steady state? Depends on T."""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    E = 1.0
    n_nodes = 50
    
    T_values = np.arange(0.50, 1.00, 0.05)
    cmap = plt.cm.viridis
    
    for i, T in enumerate(T_values):
        signal = np.zeros(n_nodes + 1)
        signal[0] = E
        for j in range(1, n_nodes + 1):
            signal[j] = signal[j-1] * T + E
        steady = E / (1 - T)
        # Normalize to steady state so we can see convergence
        ax.plot(range(n_nodes + 1), signal / steady, 
                color=cmap(i / len(T_values)), linewidth=1.5, alpha=0.8)
    
    # Annotate a few
    for T, pos in [(0.50, 3), (0.70, 6), (0.90, 18), (0.95, 35)]:
        signal = np.zeros(n_nodes + 1)
        signal[0] = E
        for j in range(1, n_nodes + 1):
            signal[j] = signal[j-1] * T + E
        steady = E / (1 - T)
        frac_95 = None
        for j in range(n_nodes + 1):
            if signal[j] / steady >= 0.95:
                frac_95 = j
                break
        if frac_95:
            ax.annotate(f'T={T:.2f}\n95% at node {frac_95}', 
                       xy=(frac_95, 0.95), fontsize=8,
                       color='#ffffff', ha='center',
                       bbox=dict(boxstyle='round,pad=0.3', fc='#333333', ec='#666666'))
    
    ax.axhline(0.95, color='#ff4466', linestyle=':', alpha=0.5, linewidth=1)
    ax.axhline(1.0, color='#ffffff', linestyle='-', alpha=0.2, linewidth=1)
    ax.set_xlabel('Node number')
    ax.set_ylabel('Fraction of steady state reached')
    ax.set_title('Relay Convergence: Higher T = Slower Convergence but Higher Steady State')
    ax.set_xlim(0, n_nodes)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0.50, 0.95))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, label='Internode transmission T')
    
    fig.tight_layout()
    path = os.path.join(OUT, 'relay_convergence.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


def fig3_cuprizone_dual_signature():
    """
    Qualitative prediction: during demyelination, 
    external leakage goes UP while internal guided signal goes DOWN.
    
    Uses cuprizone timeline with g-ratio changing over 12 weeks.
    """
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    weeks = np.linspace(0, 12, 200)
    
    # Cuprizone g-ratio model (qualitative):
    # Weeks 0-1: normal (g=0.78)
    # Weeks 1-6: progressive demyelination (g increases toward 0.95)
    # Weeks 6-12: remyelination (g decreases, but only to ~0.85 — remyelinated myelin is thinner)
    g_ratio = np.piecewise(weeks, 
        [weeks <= 1, (weeks > 1) & (weeks <= 6), weeks > 6],
        [0.78,
         lambda w: 0.78 + (0.95 - 0.78) * ((w - 1) / 5) ** 1.5,  # accelerating damage
         lambda w: 0.95 - (0.95 - 0.85) * ((w - 6) / 6) ** 0.8]   # partial recovery
    )
    
    E = 1.0  # baseline emission per node (normalized)
    n_nodes = 10
    
    # For each timepoint, compute relay signal and external leakage
    internal = np.zeros_like(weeks)
    external = np.zeros_like(weeks)
    
    for idx, g in enumerate(g_ratio):
        # T depends on g-ratio: thinner myelin → more leakage → lower T
        # Simple model: T = T_base * (1 - g)^alpha where thicker myelin = higher T
        # At g=0.78 (healthy): T~0.95, at g=0.95 (demyelinated): T~0.70
        myelin_thickness_norm = 1 - g  # 0.22 at healthy, 0.05 at demyelinated
        T = 0.50 + 0.47 * (myelin_thickness_norm / 0.22)  # maps 0.78→0.95, 0.95→0.71
        T = np.clip(T, 0.50, 0.97)
        
        # Relay steady state (internal guided signal)
        steady = E / (1 - T)
        
        # External leakage per node ∝ E * (1-T) from each node + fraction of guided signal
        # More precisely: at each node, fraction (1-T) of passing signal leaks out
        # At steady state: leakage = steady_state * (1 - T) = E  (constant!)
        # BUT: ROS emission increases during demyelination (Smith & Lassmann)
        # ROS factor: increases ~10× during active demyelination
        if weeks[idx] <= 1:
            ros_factor = 1.0
        elif weeks[idx] <= 6:
            ros_factor = 1.0 + 9.0 * ((weeks[idx] - 1) / 5) ** 1.5
        else:
            ros_factor = 10.0 - 7.0 * ((weeks[idx] - 6) / 6) ** 0.8
        
        internal[idx] = steady
        # External = leakage from guided signal + direct ROS escaping at nodes
        external[idx] = (steady * (1 - T)) + E * (ros_factor - 1) * 0.5
    
    # Normalize to baseline
    internal_norm = internal / internal[0]
    external_norm = external / external[0]
    
    # Top: dual signature
    ax = axes[0]
    ax.fill_between(weeks, 1, internal_norm, where=internal_norm < 1, 
                     color='#ff4466', alpha=0.15)
    ax.fill_between(weeks, 1, external_norm, where=external_norm > 1,
                     color='#00ffaa', alpha=0.15)
    ax.plot(weeks, internal_norm, color='#44aaff', linewidth=2.5, label='Internal guided signal')
    ax.plot(weeks, external_norm, color='#ff8844', linewidth=2.5, label='External emission (detectable)')
    ax.axhline(1.0, color='#666666', linestyle='--', alpha=0.5)
    ax.axvline(6.0, color='#ff4466', linestyle=':', alpha=0.4, label='Cuprizone removed')
    ax.set_ylabel('Signal (normalized to baseline)')
    ax.set_title('Dual Signature Prediction: Demyelination Simultaneously\nDecreases Internal Signal and Increases External Emission')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Bottom: g-ratio timeline
    ax = axes[1]
    ax.plot(weeks, g_ratio, color='#ff4466', linewidth=2.5)
    ax.fill_between(weeks, 0.78, g_ratio, where=g_ratio > 0.78,
                     color='#ff4466', alpha=0.15)
    ax.axhline(0.78, color='#00ffaa', linestyle='--', alpha=0.4, label='Healthy g-ratio')
    ax.axvline(6.0, color='#ff4466', linestyle=':', alpha=0.4)
    ax.set_xlabel('Weeks')
    ax.set_ylabel('g-ratio')
    ax.set_title('Cuprizone Demyelination / Remyelination Timeline')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.75, 1.0)
    
    # Annotations
    axes[0].annotate('Demyelination\n(weeks 1-6)', xy=(3.5, 0.5), fontsize=10,
                     color='#ff6666', ha='center', style='italic')
    axes[0].annotate('Remyelination\n(weeks 6-12)', xy=(9, 0.85), fontsize=10,
                     color='#66ff66', ha='center', style='italic')
    
    fig.tight_layout()
    path = os.path.join(OUT, 'cuprizone_dual_signature.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


def fig4_steady_state_surface():
    """
    Steady state E/(1-T) as a function of T.
    Shows the nonlinear amplification near T=1.
    This is why even small myelin changes matter.
    """
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    T = np.linspace(0.01, 0.99, 500)
    SS = 1.0 / (1.0 - T)  # normalized to E=1
    
    ax.plot(T, SS, color='#00ffaa', linewidth=2.5)
    ax.fill_between(T, 0, SS, alpha=0.1, color='#00ffaa')
    
    # Mark key regimes
    for t_val, label, color in [
        (0.70, 'Severe demyelination\nSS = 3.3×', '#ff4466'),
        (0.85, 'Mild demyelination\nSS = 6.7×', '#ff8844'),
        (0.95, 'Healthy myelin\nSS = 20×', '#00ffaa'),
    ]:
        ss = 1 / (1 - t_val)
        ax.plot(t_val, ss, 'o', color=color, markersize=10, zorder=5)
        ax.annotate(label, xy=(t_val, ss), xytext=(t_val - 0.12, ss + 2),
                   fontsize=9, color=color,
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5),
                   bbox=dict(boxstyle='round,pad=0.3', fc='#1a1a1a', ec=color))
    
    ax.set_xlabel('Internode transmission T')
    ax.set_ylabel('Steady-state signal (× single node emission)')
    ax.set_title('Relay Amplification: E/(1-T)\nSmall changes in T near 1.0 → large signal changes')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 40)
    ax.grid(True, alpha=0.3)
    
    # Inset: zoom on the sensitive region
    axins = ax.inset_axes([0.15, 0.5, 0.35, 0.4])
    T_zoom = np.linspace(0.90, 0.99, 100)
    SS_zoom = 1.0 / (1.0 - T_zoom)
    axins.plot(T_zoom, SS_zoom, color='#00ffaa', linewidth=2)
    axins.set_xlabel('T', fontsize=8, color='#999999')
    axins.set_ylabel('SS', fontsize=8, color='#999999')
    axins.set_title('T = 0.90-0.99', fontsize=8, color='#cccccc')
    axins.set_facecolor('#111111')
    axins.tick_params(colors='#999999', labelsize=7)
    for spine in axins.spines.values():
        spine.set_color('#444444')
    axins.grid(True, alpha=0.3, color='#222222')
    
    fig.tight_layout()
    path = os.path.join(OUT, 'steady_state_amplification.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


def fig5_relay_with_real_model():
    """Use actual model code to show relay at a representative wavelength."""
    
    from models.axon import AxonGeometry
    from models.node_emission import propagate_with_relay
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    lam = np.array([500.0, 600.0, 700.0, 800.0])
    colors = {'500': '#8844ff', '600': '#00ff88', '700': '#ff8844', '800': '#ff4444'}
    
    # Healthy vs demyelinated
    for ax, (g, title) in zip(axes, [(0.78, 'Healthy Myelin (g=0.78)'), 
                                       (0.92, 'Demyelinated (g=0.92)')]):
        axon = AxonGeometry(1.0, g)
        result = propagate_with_relay(axon, lam, n_nodes=30)
        
        for i, w in enumerate(lam):
            signal = result['total_signal'][:, i]
            ss = result['steady_state'][i]
            ax.plot(range(len(signal)), signal / signal[0], 
                    color=colors[str(int(w))], linewidth=2,
                    label=f'{int(w)}nm (SS={ss/signal[0]:.1f}×)')
            ax.axhline(ss / signal[0], color=colors[str(int(w))], 
                       linestyle='--', alpha=0.3)
        
        ax.set_xlabel('Node number')
        ax.set_ylabel('Signal (× node 0 emission)')
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    fig.suptitle('Relay Model with Physical Parameters (Zangari + Waveguide)', fontsize=14, y=1.02)
    fig.tight_layout()
    path = os.path.join(OUT, 'relay_physical_model.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')
    return path


if __name__ == '__main__':
    print("Generating relay model figures...\n")
    paths = []
    paths.append(fig1_relay_vs_pure_loss())
    paths.append(fig2_convergence_rate())
    paths.append(fig3_cuprizone_dual_signature())
    paths.append(fig4_steady_state_surface())
    paths.append(fig5_relay_with_real_model())
    print(f"\nDone. {len(paths)} figures in {OUT}/")
