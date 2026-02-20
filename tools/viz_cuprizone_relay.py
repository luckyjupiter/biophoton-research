#!/usr/bin/env python3
"""Visualize cuprizone experiment with relay model predictions."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from models.axon import AxonGeometry
from models.cuprizone_relay import run_cuprizone_relay

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "viz_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    axon = AxonGeometry(1.0, 0.75)
    
    print("Running cuprizone relay experiment...")
    tps = run_cuprizone_relay(axon=axon, n_mice=10, weeks=12)
    
    weeks = [tp.week for tp in tps]
    external_enhancement = [tp.external_enhancement for tp in tps]
    relay_reduction = [tp.relay_reduction for tp in tps]
    alpha = [tp.state.alpha for tp in tps]
    gamma = [tp.state.gamma for tp in tps]
    p_values = [tp.p_value for tp in tps]
    effect_sizes = [tp.effect_size for tp in tps]
    relay_t = [tp.relay_transmission for tp in tps]
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
    fig.suptitle('Cuprizone Experiment: Dual-Signature Prediction\n'
                 'External leakage UP + Internal relay DOWN = unique demyelination fingerprint',
                 fontsize=14, fontweight='bold')
    
    # Panel 1: The dual signature
    ax1 = axes[0]
    ax1_r = ax1.twinx()
    
    l1, = ax1.plot(weeks, external_enhancement, 'r-o', markersize=6, linewidth=2,
                   label='External emission (×baseline)')
    l2, = ax1_r.plot(weeks, relay_reduction, 'b-s', markersize=6, linewidth=2,
                     label='Relay signal (fraction of healthy)')
    
    ax1.set_ylabel('External emission enhancement', color='red', fontsize=12)
    ax1_r.set_ylabel('Relay signal (fraction)', color='blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1_r.tick_params(axis='y', labelcolor='blue')
    
    # Shade the demyelination phase
    ax1.axvspan(0, 6, alpha=0.05, color='orange', label='Cuprizone feeding')
    ax1.axvspan(6, 12, alpha=0.05, color='green', label='Recovery phase')
    
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center left', fontsize=10)
    ax1.set_title('DUAL SIGNATURE: External ↑ while Internal ↓', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Damage parameters
    ax2 = axes[1]
    ax2.plot(weeks, alpha, 'k-o', markersize=4, linewidth=2, label='α (thickness loss)')
    ax2.plot(weeks, gamma, 'g-s', markersize=4, linewidth=1.5, label='γ (gap fraction)')
    ax2.set_ylabel('Damage parameter', fontsize=12)
    ax2.set_title('Demyelination Progression', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Statistical significance
    ax3 = axes[2]
    colors = ['green' if p < 0.05 else 'gray' for p in p_values]
    ax3.bar(weeks, effect_sizes, color=colors, alpha=0.7, width=0.8)
    ax3.axhline(0.8, color='orange', linestyle='--', alpha=0.5, label="Large effect (0.8)")
    ax3.set_ylabel("Cohen's d (effect size)", fontsize=12)
    ax3.set_title('Detection Power (green = p < 0.05)', fontsize=12)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Panel 4: Waveguide transmission degradation
    ax4 = axes[3]
    ax4.plot(weeks, relay_t, 'purple', marker='D', markersize=5, linewidth=2)
    ax4.set_xlabel('Week', fontsize=12)
    ax4.set_ylabel('T per internode', fontsize=12)
    ax4.set_title('Waveguide Transmission Degradation', fontsize=12)
    ax4.grid(True, alpha=0.3)
    
    # Parameters annotation
    fig.text(0.5, 0.01,
             'Model: Zangari nanoantenna (2018) + ROS chemiluminescence | '
             'Axon: 1.0μm CNS, g=0.75 | 10 mice/group | PMT detector | '
             '5-min exposure | 10 Hz AP rate',
             ha='center', fontsize=9, style='italic', color='gray')
    
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    path = os.path.join(OUTPUT_DIR, "cuprizone_relay_dual_signature.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {path}")
    
    # Print summary
    print("\n=== Cuprizone Relay Predictions ===")
    print(f"{'Week':>5} {'α':>5} {'Ext ×':>7} {'Relay %':>8} {'T/node':>8} {'p-value':>10} {'Cohen d':>8}")
    print("-" * 60)
    for tp in tps:
        print(f"{tp.week:5.0f} {tp.state.alpha:5.2f} {tp.external_enhancement:7.2f} "
              f"{tp.relay_reduction*100:7.1f}% {tp.relay_transmission:8.4f} "
              f"{tp.p_value:10.4f} {tp.effect_size:8.2f}")


if __name__ == "__main__":
    main()
