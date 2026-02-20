#!/usr/bin/env python3
"""
Biophoton Research Visualizer
==============================
Generates publication-quality figures from simulation data and saves as PNG.
Run: python3 tools/viz.py <command> [options]

Commands:
  spectrum [--damage 0.5]          Emission spectrum (healthy vs demyelinated)
  timeline                         Cuprizone experiment timeline
  roc                              ROC curve for biomarker classification
  waveguide                        Waveguide mode structure
  sensitivity                      Tornado chart — which parameters matter
  dose_response                    Hill dose-response curves
  dashboard                        All-in-one summary dashboard
  discord_decay [--internodes 10]  Discord vs entanglement decay through waveguide
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Project imports
from models import constants as C
from models.axon import AxonGeometry
from models.demyelination import DemyelinationState
from models.emission import waveguide_filtered_emission
from models.detection import Detector
from models.cuprizone import CuprizoneExperiment
from models.visualization import (
    plot_spectrum, plot_timeline, plot_roc,
    plot_waveguide_modes, plot_dose_response
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "viz_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {path}")
    return path


def cmd_spectrum(args):
    axon = AxonGeometry(1.0, 0.75)
    state = DemyelinationState(args.damage, args.damage * 0.6, args.damage * 0.3) if args.damage > 0 else None
    fig = plot_spectrum(axon, state)
    return save(fig, f"spectrum_damage_{args.damage:.1f}")


def cmd_timeline(args):
    axon = AxonGeometry(1.0, 0.75)
    detector = Detector.pmt()
    exp = CuprizoneExperiment(axon=axon, detector=detector, n_mice=10)
    exp.run()
    fig = plot_timeline(exp)
    return save(fig, "cuprizone_timeline")


def cmd_roc(args):
    """Generate ROC curves for multiple biomarkers."""
    from models.simulate import run_roc_analysis
    results = run_roc_analysis()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set2(np.linspace(0, 1, len(results)))
    
    for (name, result), color in zip(results.items(), colors):
        ax.plot(result["fpr"], result["tpr"], linewidth=2, color=color,
                label=f'{name} (AUC={result["auc"]:.3f})')
    
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("Biomarker ROC Curves: Healthy vs Demyelinated", fontsize=14)
    ax.legend(loc="lower right", fontsize=10)
    ax.set_aspect("equal")
    fig.tight_layout()
    return save(fig, "roc_multimarker")


def cmd_waveguide(args):
    axon = AxonGeometry(1.0, 0.75)
    fig = plot_waveguide_modes(axon)
    return save(fig, "waveguide_modes")


def cmd_dose_response(args):
    fig = plot_dose_response()
    return save(fig, "dose_response")


def cmd_discord_decay(args):
    """
    Theoretical comparison: entanglement vs discord decay through lossy myelin waveguide.
    Models amplitude damping channel with parameters from Track 04.
    """
    n_internodes = np.arange(0, args.internodes + 1)
    
    # Per-internode transmission (from Track 07: node coupling dominates)
    # T_node ~ 0.3 per node-of-Ranvier crossing, absorption loss per internode ~ 0.85
    T_node = 0.3
    T_absorption = 0.85
    T_per_internode = T_node * T_absorption  # ~0.255
    
    # Cumulative transmission
    eta = np.array([T_per_internode ** n for n in n_internodes])
    
    # Entanglement (concurrence) under amplitude damping
    # For initial Bell state: C(η) = max(0, 2η - 1) — sudden death at η = 0.5
    concurrence = np.maximum(0, 2 * eta - 1)
    
    # Discord under amplitude damping (two-sided)
    # For Werner states under amplitude damping: discord decays as ~ η² but never hits zero
    # D(η) ≈ η² * D₀ for amplitude damping (Werlang et al. 2009)
    # More precisely, for X-states: discord is nonzero for any η > 0
    discord_initial = 0.06  # bits, from Track 04
    discord = discord_initial * eta**2  # conservative estimate — actual decay is slower
    
    # Also compute a more optimistic discord (phase damping only)
    # Under pure dephasing: discord ~ (1-p)² where p is dephasing probability
    # Dephasing per internode from vibrational modes
    p_deph = 0.1  # 10% dephasing per internode (conservative for 0.5-2ps timescale)
    discord_phase = discord_initial * np.array([(1 - p_deph) ** (2 * n) for n in n_internodes])
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Panel 1: Transmission
    ax1.semilogy(n_internodes, eta, "k-o", linewidth=2, markersize=4)
    ax1.set_ylabel("Cumulative transmission η", fontsize=12)
    ax1.set_title("Photon Propagation Through Myelin Waveguide", fontsize=14)
    ax1.axhline(0.5, color="red", linestyle="--", alpha=0.5, label="η = 0.5 (entanglement death)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Entanglement vs Discord
    ax2.plot(n_internodes, concurrence, "r-s", linewidth=2, markersize=5, label="Entanglement (concurrence)")
    ax2.plot(n_internodes, discord * 1000, "b-o", linewidth=2, markersize=5, label="Discord × 1000 (amplitude damping)")
    ax2.plot(n_internodes, discord_phase * 1000, "g-^", linewidth=2, markersize=5, label="Discord × 1000 (phase damping only)")
    ax2.axvline(1, color="orange", linestyle=":", alpha=0.5)
    ax2.annotate("Entanglement\nsudden death", xy=(1, 0), fontsize=9, color="red",
                ha="center", va="bottom")
    ax2.set_ylabel("Quantum correlations", fontsize=12)
    ax2.set_title("Entanglement Dies — Does Discord Survive?", fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Ratio discord/entanglement (where both nonzero)
    mask = concurrence > 0
    ratio = np.zeros_like(n_internodes, dtype=float)
    ratio[mask] = (discord[mask]) / (concurrence[mask] + 1e-20)
    
    ax3.semilogy(n_internodes[mask], ratio[mask], "m-D", linewidth=2, markersize=5)
    ax3.set_xlabel("Number of internodes traversed", fontsize=12)
    ax3.set_ylabel("Discord / Concurrence ratio", fontsize=12)
    ax3.set_title("Discord Becomes Dominant Correlation", fontsize=14)
    ax3.grid(True, alpha=0.3)
    
    # Add annotation about the gap
    fig.text(0.5, 0.01, 
             f"Parameters: T_node={T_node}, T_absorption={T_absorption:.2f}, "
             f"initial discord={discord_initial} bits (Track 04)\n"
             f"After {args.internodes} internodes: η={eta[-1]:.2e}, "
             f"concurrence={concurrence[-1]:.4f}, discord={discord[-1]:.2e} bits",
             ha="center", fontsize=9, style="italic", color="gray")
    
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    return save(fig, f"discord_vs_entanglement_{args.internodes}int")


def cmd_dashboard(args):
    """All-in-one research summary dashboard."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("Biophoton Research — Simulation Dashboard", fontsize=16, fontweight="bold")
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    axon = AxonGeometry(1.0, 0.75)
    
    # 1. Spectrum
    ax1 = fig.add_subplot(gs[0, 0])
    lam = C.DEFAULT_LAMBDA_RANGE_NM
    healthy = DemyelinationState(0, 0, 0)
    demyelinated = DemyelinationState(0.5, 0.3, 0.15)
    h_spec = waveguide_filtered_emission(axon, healthy, lam)
    d_spec = waveguide_filtered_emission(axon, demyelinated, lam)
    ax1.plot(lam, h_spec, "b-", linewidth=1.5, label="Healthy")
    ax1.plot(lam, d_spec, "r-", linewidth=1.5, label="50% demyel.")
    ax1.fill_between(lam, h_spec, d_spec, alpha=0.15, color="red")
    ax1.set_xlabel("λ (nm)")
    ax1.set_ylabel("Photons/cm²/s/nm")
    ax1.set_title("Emission Spectrum")
    ax1.legend(fontsize=8)
    
    # 2. Dose response
    ax2 = fig.add_subplot(gs[0, 1])
    from models.demyelination import hill_response
    damage = np.linspace(0, 1, 100)
    for n in [1, 2, 3, 5]:
        resp = [hill_response(d, 1.0, 10.0, n, 0.5) for d in damage]
        ax2.plot(damage, resp, linewidth=1.5, label=f"n={n}")
    ax2.set_xlabel("Damage severity")
    ax2.set_ylabel("Signal (relative)")
    ax2.set_title("Dose-Response")
    ax2.legend(fontsize=8)
    
    # 3. Waveguide V-number
    ax3 = fig.add_subplot(gs[0, 2])
    wl = np.linspace(200, 950, 200)
    v = [axon.v_number(l) for l in wl]
    ax3.plot(wl, v, "g-", linewidth=1.5)
    ax3.axhline(2.405, color="red", linestyle="--", alpha=0.7, label="Single-mode")
    ax3.set_xlabel("λ (nm)")
    ax3.set_ylabel("V-number")
    ax3.set_title("Waveguide Modes")
    ax3.legend(fontsize=8)
    
    # 4. Discord vs Entanglement (compact)
    ax4 = fig.add_subplot(gs[1, 0])
    n_int = np.arange(0, 11)
    T = 0.255
    eta = T ** n_int
    conc = np.maximum(0, 2 * eta - 1)
    disc = 0.06 * eta**2
    ax4.plot(n_int, conc, "r-s", markersize=4, linewidth=1.5, label="Entanglement")
    ax4.plot(n_int, disc * 100, "b-o", markersize=4, linewidth=1.5, label="Discord ×100")
    ax4.set_xlabel("Internodes")
    ax4.set_ylabel("Correlation")
    ax4.set_title("Entanglement vs Discord")
    ax4.legend(fontsize=8)
    
    # 5. Sensitivity bars (from Track 07 findings)
    ax5 = fig.add_subplot(gs[1, 1])
    params = ["n_internodes", "node_T", "κ (abs)", "j_leak", "g_ΦΨ", "α_myelin", "coupling_K"]
    sensitivities = [52840, 3844, 133, 105, 100, 51, 2]
    colors = ["#d32f2f" if s > 1000 else "#1976d2" if s > 50 else "#78909c" for s in sensitivities]
    ax5.barh(range(len(params)), sensitivities, color=colors, alpha=0.8)
    ax5.set_yticks(range(len(params)))
    ax5.set_yticklabels(params, fontsize=9)
    ax5.set_xlabel("Sensitivity (%)")
    ax5.set_title("Parameter Sensitivity")
    ax5.set_xscale("log")
    ax5.invert_yaxis()
    
    # 6. Key numbers text box
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis("off")
    summary = (
        "KEY FINDINGS\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Cavity Q-factor:  ~5\n"
        "Cooperativity C:  ~10⁻³\n"
        "Entanglement:     0.06 bits\n"
        "Peak emission:    456 nm\n"
        "50% demyel:       9.3× enhancement\n"
        "ROC AUC:          1.000\n"
        "First detection:  Week 1 (3σ)\n"
        "Bottleneck:       Node-of-Ranvier\n"
        "                  transmission\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "OPEN QUESTION:\n"
        "Does quantum discord\n"
        "survive the waveguide?"
    )
    ax6.text(0.05, 0.95, summary, transform=ax6.transAxes, fontsize=10,
             verticalalignment="top", fontfamily="monospace",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f5f5f5", edgecolor="#333"))
    
    return save(fig, "dashboard")


def main():
    parser = argparse.ArgumentParser(description="Biophoton Research Visualizer")
    sub = parser.add_subparsers(dest="command")
    
    sp = sub.add_parser("spectrum")
    sp.add_argument("--damage", type=float, default=0.5)
    
    sub.add_parser("timeline")
    sub.add_parser("roc")
    sub.add_parser("waveguide")
    sub.add_parser("dose_response")
    sub.add_parser("dashboard")
    
    dp = sub.add_parser("discord_decay")
    dp.add_argument("--internodes", type=int, default=10)
    
    sub.add_parser("all")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "spectrum": cmd_spectrum,
        "timeline": cmd_timeline,
        "waveguide": cmd_waveguide,
        "dose_response": cmd_dose_response,
        "discord_decay": cmd_discord_decay,
        "dashboard": cmd_dashboard,
    }
    
    if args.command == "all":
        for name, fn in commands.items():
            print(f"\n--- {name} ---")
            try:
                # Create args with defaults for each command
                if name == "spectrum":
                    args.damage = 0.5
                elif name == "discord_decay":
                    args.internodes = 10
                fn(args)
            except Exception as e:
                print(f"  ERROR: {e}")
    elif args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
