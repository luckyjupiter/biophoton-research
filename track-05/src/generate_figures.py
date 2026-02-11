"""
Figure Generation for Track 05: Signal-to-Noise & Detection Theory
===================================================================
Generates all figures for the track: SNR maps, ROC curves, detector
comparisons, QE curves, feasibility boundaries, and artifact characterizations.

Usage: python src/generate_figures.py
"""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.detectors import QE_CURVES, ALL_DETECTORS, simulate_detector
from src.snr_calculator import (
    snr_photon_counting, compute_snr_map, DETECTOR_CONFIGS,
    compute_feasibility_table, integration_time_for_significance,
    poisson_confidence_interval, feldman_cousins_interval,
    cowan_discovery_significance
)
from src.roc_analysis import compute_roc_poisson, analyze_scenario, SCENARIOS
from src.artifacts import (
    simulate_afterpulse_g2_contamination, simulate_delayed_luminescence,
    simulate_cosmic_ray_events
)

FIGDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(FIGDIR, exist_ok=True)


def fig_qe_curves():
    """Plot quantum efficiency curves for all detector types."""
    fig, ax = plt.subplots(figsize=(10, 6))
    wl = np.linspace(300, 1000, 500)
    labels = {
        "bialkali": "PMT (Bialkali)",
        "gaas": "PMT (GaAsP)",
        "si_spad": "SPAD (Si)",
        "back_illuminated_ccd": "EM-CCD (BI)",
        "snspd": "SNSPD",
    }
    colors = {"bialkali": "C0", "gaas": "C1", "si_spad": "C2",
              "back_illuminated_ccd": "C3", "snspd": "C4"}
    for key, func in QE_CURVES.items():
        ax.plot(wl, func(wl), label=labels.get(key, key), color=colors.get(key),
                linewidth=2)
    # Shade UPE emission range
    ax.axvspan(400, 700, alpha=0.1, color="yellow", label="UPE range")
    ax.set_xlabel("Wavelength (nm)", fontsize=12)
    ax.set_ylabel("Quantum Efficiency", fontsize=12)
    ax.set_title("Detector Quantum Efficiency Curves", fontsize=14)
    ax.legend(fontsize=10)
    ax.set_xlim(300, 1000)
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "qe_curves.png"), dpi=150)
    plt.close(fig)
    print("  Saved qe_curves.png")


def fig_snr_maps():
    """Plot SNR as a function of signal rate and integration time for each detector."""
    signal_rates = np.logspace(-1, 3, 50)  # 0.1 to 1000 ph/cm2/s
    int_times = np.logspace(0, 5, 50)  # 1s to 100000s

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, (det_name, config) in enumerate(DETECTOR_CONFIGS.items()):
        if idx >= 5:
            break
        snr_map = compute_snr_map(signal_rates, int_times, config)
        ax = axes[idx]
        # SNR map
        im = ax.pcolormesh(int_times / 3600, signal_rates, snr_map,
                           norm=LogNorm(vmin=0.1, vmax=1000), cmap="viridis",
                           shading="auto")
        # 5-sigma contour
        ax.contour(int_times / 3600, signal_rates, snr_map, levels=[5],
                   colors="red", linewidths=2)
        # 3-sigma contour
        ax.contour(int_times / 3600, signal_rates, snr_map, levels=[3],
                   colors="orange", linewidths=1.5, linestyles="dashed")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Integration time (hr)")
        ax.set_ylabel("Signal rate (ph/cm2/s)")
        ax.set_title(det_name, fontsize=11)
        plt.colorbar(im, ax=ax, label="SNR")

    # Remove unused subplot
    axes[5].set_visible(False)

    fig.suptitle("SNR Maps: Feasibility Boundaries for Biophoton Detection", fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "snr_maps.png"), dpi=150)
    plt.close(fig)
    print("  Saved snr_maps.png")


def fig_integration_times():
    """Plot required integration time vs signal rate for each detector."""
    signal_rates = np.logspace(-1, 3, 100)
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["C0", "C1", "C2", "C3", "C4"]
    for idx, (det_name, config) in enumerate(DETECTOR_CONFIGS.items()):
        times = []
        for sr in signal_rates:
            pr = sr * config.collection_area
            t = integration_time_for_significance(pr, config.dark_rate, config.qe, 5.0)
            times.append(t)
        times = np.array(times)
        ax.plot(signal_rates, times / 3600, label=det_name, color=colors[idx],
                linewidth=2)

    # Reference lines
    ax.axhline(1, color="gray", linestyle=":", alpha=0.5, label="1 hour")
    ax.axhline(24, color="gray", linestyle="--", alpha=0.5, label="1 day")
    ax.axhline(24 * 7, color="gray", linestyle="-.", alpha=0.5, label="1 week")

    # UPE range
    ax.axvspan(1, 1000, alpha=0.05, color="green")
    ax.text(30, 1e-3, "UPE range", fontsize=10, color="green", alpha=0.7)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Signal rate (photons/cm2/s)", fontsize=12)
    ax.set_ylabel("Integration time for 5-sigma (hours)", fontsize=12)
    ax.set_title("Required Integration Time vs Signal Rate", fontsize=14)
    ax.legend(fontsize=9)
    ax.set_xlim(0.1, 1000)
    ax.set_ylim(1e-4, 1e6)
    ax.grid(True, alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "integration_times.png"), dpi=150)
    plt.close(fig)
    print("  Saved integration_times.png")


def fig_roc_curves():
    """Plot ROC curves for selected biophoton detection scenarios."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: favorable scenarios
    ax = axes[0]
    favorable = [s for s in SCENARIOS if s.name in
                 ["PMT bright 10m", "PMT moderate 1h", "PMT faint 1h"]]
    for sc in favorable:
        r = analyze_scenario(sc)
        ax.plot(r["fpr"], r["tpr"], label="%s (AUC=%.3f)" % (sc.name, r["auc"]),
                linewidth=2)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Random")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC: PMT Scenarios", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)

    # Right: challenging scenarios
    ax = axes[1]
    challenging = [s for s in SCENARIOS if s.name in
                   ["SPAD moderate 1h", "EMCCD moderate 1h",
                    "SNSPD faint 1h", "SNSPD moderate 1h"]]
    for sc in challenging:
        r = analyze_scenario(sc)
        ax.plot(r["fpr"], r["tpr"], label="%s (AUC=%.3f)" % (sc.name, r["auc"]),
                linewidth=2)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Random")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC: Alternative Detectors", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)

    fig.suptitle("Receiver Operating Characteristic for Biophoton Detection", fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "roc_curves.png"), dpi=150)
    plt.close(fig)
    print("  Saved roc_curves.png")


def fig_detector_comparison():
    """Bar chart comparing key detector metrics."""
    detectors = list(ALL_DETECTORS.keys())
    det_labels = [ALL_DETECTORS[d].name for d in detectors]
    qe = [ALL_DETECTORS[d].qe_scalar for d in detectors]
    dark = [ALL_DETECTORS[d].dark_count_rate for d in detectors]
    area = [ALL_DETECTORS[d].collection_area for d in detectors]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # QE
    axes[0].barh(det_labels, qe, color=["C0", "C1", "C2", "C3", "C4"])
    axes[0].set_xlabel("Quantum Efficiency")
    axes[0].set_title("Quantum Efficiency")
    axes[0].set_xlim(0, 1)

    # Dark count rate (log scale)
    axes[1].barh(det_labels, dark, color=["C0", "C1", "C2", "C3", "C4"])
    axes[1].set_xlabel("Dark Count Rate (counts/s)")
    axes[1].set_title("Dark Count Rate")
    axes[1].set_xscale("log")

    # Collection area (log scale)
    axes[2].barh(det_labels, area, color=["C0", "C1", "C2", "C3", "C4"])
    axes[2].set_xlabel("Collection Area (cm2)")
    axes[2].set_title("Collection Area")
    axes[2].set_xscale("log")

    fig.suptitle("Detector Comparison for Biophoton Research", fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "detector_comparison.png"), dpi=150)
    plt.close(fig)
    print("  Saved detector_comparison.png")


def fig_afterpulse_contamination():
    """Plot afterpulse g(2) contamination vs time lag."""
    fig, ax = plt.subplots(figsize=(10, 6))
    taus = np.logspace(-9, -5, 200)

    for rate, p_ap, tau_ap, label in [
        (50, 0.02, 50e-9, "PMT: R=50/s, P_ap=2%"),
        (100, 0.02, 50e-9, "PMT: R=100/s, P_ap=2%"),
        (50, 0.05, 40e-9, "SPAD: R=50/s, P_ap=5%"),
        (100, 0.05, 40e-9, "SPAD: R=100/s, P_ap=5%"),
    ]:
        g2 = simulate_afterpulse_g2_contamination(rate, p_ap, tau_ap, taus)
        ax.plot(taus * 1e9, g2 - 1, label=label, linewidth=2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Time lag (ns)", fontsize=12)
    ax.set_ylabel("g(2)(tau) - 1 (excess)", fontsize=12)
    ax.set_title("Afterpulse Contamination of g(2) Measurement", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, which="both")
    ax.axhline(1e-3, color="red", linestyle=":", alpha=0.5)
    ax.text(1e4, 1.5e-3, "1e-3 precision target", color="red", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "afterpulse_g2_contamination.png"), dpi=150)
    plt.close(fig)
    print("  Saved afterpulse_g2_contamination.png")


def fig_poisson_intervals():
    """Plot Poisson confidence intervals vs observed count."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ns = np.arange(0, 51)
    lowers, uppers = [], []
    for n in ns:
        lo, hi = poisson_confidence_interval(n, 0.90)
        lowers.append(lo)
        uppers.append(hi)
    lowers = np.array(lowers)
    uppers = np.array(uppers)

    ax.fill_between(ns, lowers, uppers, alpha=0.3, color="C0", label="90% CI")
    ax.plot(ns, ns, "k--", alpha=0.5, label="n_obs = mu (diagonal)")
    ax.plot(ns, lowers, "C0-", linewidth=1)
    ax.plot(ns, uppers, "C0-", linewidth=1)
    ax.set_xlabel("Observed count n", fontsize=12)
    ax.set_ylabel("Poisson mean mu", fontsize=12)
    ax.set_title("Exact Poisson 90% Confidence Intervals (Garwood)", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "poisson_confidence_intervals.png"), dpi=150)
    plt.close(fig)
    print("  Saved poisson_confidence_intervals.png")


def fig_discovery_significance():
    """Plot Cowan discovery significance as function of signal and background."""
    fig, ax = plt.subplots(figsize=(10, 6))
    s_vals = np.linspace(0.1, 100, 200)
    for b in [1, 3, 10, 30, 100]:
        z = [cowan_discovery_significance(s, b) for s in s_vals]
        ax.plot(s_vals, z, label="b = %d" % b, linewidth=2)
    ax.axhline(5, color="red", linestyle=":", label="5-sigma")
    ax.axhline(3, color="orange", linestyle=":", label="3-sigma")
    ax.set_xlabel("Expected signal counts", fontsize=12)
    ax.set_ylabel("Discovery significance (sigma)", fontsize=12)
    ax.set_title("Cowan Discovery Significance vs Signal (Poisson)", fontsize=14)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 20)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "discovery_significance.png"), dpi=150)
    plt.close(fig)
    print("  Saved discovery_significance.png")


def main():
    print("Generating figures for Track 05...")
    fig_qe_curves()
    fig_snr_maps()
    fig_integration_times()
    fig_roc_curves()
    fig_detector_comparison()
    fig_afterpulse_contamination()
    fig_poisson_intervals()
    fig_discovery_significance()
    print("All figures saved to %s" % FIGDIR)


if __name__ == "__main__":
    main()
