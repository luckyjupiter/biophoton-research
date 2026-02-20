#!/usr/bin/env python3
"""
Visualize the node-to-node relay model.

Generates:
1. Relay signal buildup — total signal vs pure-loss model across nodes
2. Nanoantenna emission spectrum — what each node radiates
3. AP vs photon timing — photons arrive before the action potential
4. Spectral comparison — ROS emission vs nanoantenna emission

Usage:
    python3 tools/viz_relay.py [all|relay|spectrum|timing|compare]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from models.axon import AxonGeometry
from models import constants as C
from models.node_emission import (
    NodeEmission, propagate_with_relay, ap_timing,
    NA_CHANNEL_LENGTH_M,
)
from models.waveguide import propagate_multi_node
from models.emission import ros_spectrum

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "viz_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {path}")
    return path


def plot_relay(axon=None, n_nodes=20):
    """Compare relay model vs pure-loss model with source breakdown."""
    if axon is None:
        axon = AxonGeometry(1.0, 0.75)
    
    lam = np.array([500.0])
    
    # Relay model
    relay = propagate_with_relay(axon, lam, n_nodes=n_nodes)
    total_signal = relay['total_signal'][:, 0]
    surviving = relay['surviving_original'][:, 0]
    ss = relay['steady_state'][0]
    
    # Pure-loss model (existing)
    pure_loss = np.zeros(n_nodes + 1)
    initial = total_signal[0]
    t = float(relay['transmission_per_internode'][0])
    for i in range(n_nodes + 1):
        pure_loss[i] = initial * t**i
    
    nodes = np.arange(n_nodes + 1)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14))
    
    # Panel 1: Linear comparison
    ax1.plot(nodes, total_signal, 'b-o', markersize=5, linewidth=2,
             label='Relay model (node re-emission)')
    ax1.plot(nodes, pure_loss, 'r--s', markersize=4, linewidth=1.5,
             label='Pure-loss model')
    ax1.axhline(ss, color='blue', linestyle=':', alpha=0.4, 
                label=f'Steady state = {ss:.2e}')
    ax1.set_ylabel('Signal (photons/s/nm)', fontsize=12)
    ax1.set_title('Node-to-Node Relay vs Pure Loss (λ=500nm, 10 Hz AP rate)\n'
                  'Sources: Zangari 2018 (nanoantenna) + Cifra 2014 (ROS)',
                  fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Log scale
    ax2.semilogy(nodes, total_signal, 'b-o', markersize=5, linewidth=2,
                 label='Relay total')
    ax2.semilogy(nodes, pure_loss, 'r--s', markersize=4, linewidth=1.5,
                 label='Pure-loss')
    ax2.semilogy(nodes, surviving, 'gray', linestyle=':', linewidth=1,
                 label='Original photons surviving')
    ax2.set_xlabel('Node number', fontsize=12)
    ax2.set_ylabel('Signal (log scale)', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Source breakdown
    ant = relay['sources']['antenna_per_s'][0] * 0.3  # with coupling
    ros = relay['sources']['ros_guided'][0]
    labels = ['Nanoantenna\n(EM from ion currents)', 'ROS\n(chemiluminescence)']
    values = [ant, ros]
    colors = ['#1976d2', '#d32f2f']
    bars = ax3.bar(labels, values, color=colors, alpha=0.8, width=0.5)
    ax3.set_ylabel('Guided photons/s/nm per node', fontsize=12)
    ax3.set_title('Emission Source Breakdown at Each Node', fontsize=13)
    for bar, val in zip(bars, values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{val:.2e}', ha='center', va='bottom', fontsize=11)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Parameters box
    node = relay['node_emission']
    fig.text(0.99, 0.01,
             f'Parameters (all from literature):\n'
             f'Na⁺ density: {node.channel_density:.0f}/μm² | '
             f'Channels: {node.n_channels} | '
             f'V_df: {node.driving_voltage*1e3:.0f} mV | '
             f'Dipole: {NA_CHANNEL_LENGTH_M*1e9:.0f} nm\n'
             f'AP rate: {relay["ap_rate_hz"]} Hz | '
             f'T/internode: {t:.4f} | '
             f'Baseline UPE: {C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S:.0f} ph/cm²/s '
             f'(Kobayashi 2009)',
             ha='right', fontsize=8, style='italic', color='gray')
    
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    return save(fig, 'relay_vs_pure_loss')


def plot_node_spectrum(axon=None):
    """Nanoantenna emission spectrum from a single node."""
    if axon is None:
        axon = AxonGeometry(1.0, 0.75)
    
    node = NodeEmission(axon)
    lam = np.linspace(300, 1600, 500)
    
    # Nanoantenna spectrum
    antenna_spec = node.emission_spectrum(lam)
    
    # ROS spectrum (for comparison)
    ros = ros_spectrum(lam)
    ros_scaled = ros * np.max(antenna_spec) * 0.5  # scale for visual comparison
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(lam, antenna_spec, 'b-', linewidth=2,
            label=f'Nanoantenna emission (N={node.n_channels} channels)')
    ax.plot(lam, ros_scaled, 'r--', linewidth=1.5,
            label='ROS emission (scaled, for shape comparison)')
    
    # Mark key regions
    ax.axvspan(300, 700, alpha=0.05, color='violet', label='Visible range')
    ax.axvspan(700, 1600, alpha=0.05, color='red', label='IR range')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Photons per AP per nm', fontsize=12)
    ax.set_title(f'Node of Ranvier Emission Spectrum\n'
                 f'(Zangari nanoantenna model, {node.channel_density:.0f} ch/μm²)',
                 fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Annotate total photons
    total = np.trapz(antenna_spec, lam)
    ax.text(0.95, 0.95,
            f'Total: {total:.2e} photons/AP\n'
            f'Peak current: {node.peak_total_current_A*1e9:.1f} nA\n'
            f'Channels: {node.n_channels}\n'
            f'Node area: {node.node_area_um2:.2f} μm²',
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    fig.tight_layout()
    return save(fig, 'node_emission_spectrum')


def plot_timing(axon=None, n_nodes=10):
    """Show that photons arrive before the action potential."""
    if axon is None:
        axon = AxonGeometry(1.0, 0.75)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))
    
    # Multiple conduction velocities
    velocities = [20, 50, 100]
    colors = ['#d32f2f', '#1976d2', '#388e3c']
    
    for v, c in zip(velocities, colors):
        timing = ap_timing(axon, n_nodes=n_nodes, conduction_velocity_ms=v)
        
        ax1.plot(timing['nodes'], timing['ap_arrival_s'] * 1e6,
                f'-o', color=c, markersize=4, linewidth=2,
                label=f'AP arrival (v={v} m/s)')
    
    # Photon arrival (same for all — it's at c/n)
    timing = ap_timing(axon, n_nodes=n_nodes, conduction_velocity_ms=50)
    ax1.plot(timing['nodes'], timing['photon_arrival_from_origin_s'] * 1e9,
            'k--', linewidth=1, label='Photon arrival (×1000, at c/n)')
    
    ax1.set_ylabel('Time (μs)', fontsize=12)
    ax1.set_title('Action Potential vs Photon Transit Time\n'
                  'Photons arrive ~μs before the AP at each node', fontsize=14)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Photon advantage
    for v, c in zip(velocities, colors):
        timing = ap_timing(axon, n_nodes=n_nodes, conduction_velocity_ms=v)
        ax2.bar(timing['nodes'] + (v-50)/200, 
                np.ones(n_nodes+1) * timing['photon_advantage_us'],
                width=0.25, color=c, alpha=0.7,
                label=f'v={v} m/s: {timing["photon_advantage_us"]:.1f} μs advantage')
    
    ax2.set_xlabel('Node number', fontsize=12)
    ax2.set_ylabel('Photon time advantage (μs)', fontsize=12)
    ax2.set_title('How much earlier photons arrive at each node vs the AP', fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    return save(fig, 'ap_vs_photon_timing')


def plot_spectral_comparison(axon=None, n_nodes=10):
    """Compare total signal spectrum: relay vs pure-loss at multiple nodes."""
    if axon is None:
        axon = AxonGeometry(1.0, 0.75)
    
    lam = np.linspace(300, 900, 300)
    
    relay = propagate_with_relay(axon, lam, n_nodes=n_nodes)
    pure_loss = propagate_multi_node(axon, lam, n_nodes=n_nodes)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    check_nodes = [0, 3, 6, n_nodes]
    for ax, n in zip(axes.flat, check_nodes):
        if n <= n_nodes:
            relay_signal = relay['total_signal'][n]
            
            # Pure loss from node 0
            initial = relay['total_signal'][0]
            t = relay['transmission_per_internode']
            pure = initial * t**n
            
            ax.plot(lam, relay_signal, 'b-', linewidth=2, label='Relay model')
            ax.plot(lam, pure, 'r--', linewidth=1.5, label='Pure-loss model')
            ax.set_title(f'Node {n}', fontsize=12)
            ax.set_xlabel('λ (nm)')
            ax.set_ylabel('Signal')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
    
    fig.suptitle(f'Spectral Evolution Through {n_nodes}-Node Chain\n'
                 f'Relay model preserves signal; pure-loss collapses',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    return save(fig, 'spectral_relay_evolution')


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    axon = AxonGeometry(1.0, 0.75)  # typical CNS
    
    commands = {
        'relay': lambda: plot_relay(axon),
        'spectrum': lambda: plot_node_spectrum(axon),
        'timing': lambda: plot_timing(axon),
        'compare': lambda: plot_spectral_comparison(axon),
    }
    
    if cmd == 'all':
        for name, fn in commands.items():
            print(f"\n--- {name} ---")
            try:
                fn()
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()
    elif cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands.keys())}, all")


if __name__ == "__main__":
    main()
