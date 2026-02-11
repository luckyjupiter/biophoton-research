"""
Figure Generation for Track 01: Photocount Statistics
=====================================================

Generates publication-quality figures illustrating the key results
of the photocount statistics analysis.

Author: Track 01 -- Quantum Optics Statistician
"""

from __future__ import annotations

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import cm

from photocount_distributions import (
    poisson_distribution, bose_einstein_distribution,
    negative_binomial_distribution, squeezed_state_distribution,
    distribution_moments, squeezed_state_moments,
    generate_samples, convolve_with_dark_counts,
)
from statistical_tests import (
    estimate_fano_factor, power_analysis_fano,
    fano_factor_detectable, measured_fano_with_artifacts,
)
from detector_model import DetectorModel, COOLED_PMT, SNSPD

FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def fig_distribution_comparison():
    """Figure 1: Compare photocount distributions at mu=5 and mu=50."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, mu in zip(axes, [5.0, 50.0]):
        n_max = int(mu * 3 + 10)
        n = np.arange(n_max + 1)

        P_pois = poisson_distribution(n_max, mu)
        P_be = bose_einstein_distribution(n_max, mu)
        P_nb10 = negative_binomial_distribution(n_max, mu, 10)

        alpha_val = np.sqrt(mu * 0.9) + 0j
        P_sq = squeezed_state_distribution(n_max, alpha_val, 0.5, 0.0)

        ax.bar(n - 0.3, P_pois, width=0.2, alpha=0.8, label="Poisson (coherent)", color="C0")
        ax.bar(n - 0.1, P_nb10, width=0.2, alpha=0.8, label="NB (M=10 thermal)", color="C1")
        ax.bar(n + 0.1, P_sq, width=0.2, alpha=0.8, label="Squeezed (r=0.5)", color="C2")
        if mu < 20:
            ax.bar(n + 0.3, P_be, width=0.2, alpha=0.6, label="Bose-Einstein (M=1)", color="C3")

        ax.set_xlabel("Photon count n")
        ax.set_ylabel("P(n)")
        ax.set_title(f"$\\langle n \\rangle = {mu:.0f}$")
        ax.legend(fontsize=8)
        ax.set_xlim(-0.5, min(n_max, mu * 2.5))

    fig.suptitle("Photocount Distributions: Coherent vs. Thermal vs. Squeezed", fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig01_distribution_comparison.png"), dpi=150)
    plt.close(fig)
    print("  Created fig01_distribution_comparison.png")


def fig_fano_vs_modes():
    """Figure 2: Fano factor and Mandel Q as function of mode number M."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    mode_numbers = np.logspace(0, 6, 200)
    mu_values = [1, 5, 10, 50, 100]

    for mu in mu_values:
        F = 1.0 + mu / mode_numbers
        Q = mu / mode_numbers
        ax1.loglog(mode_numbers, F - 1, label=f"$\\mu={mu}$")
        ax2.loglog(mode_numbers, Q, label=f"$\\mu={mu}$")

    # Detection threshold line for N=10000
    delta_min = fano_factor_detectable(10000, alpha=0.05)
    ax1.axhline(y=delta_min, color="red", linestyle="--", linewidth=2,
                label=f"Detection threshold (N=10$^4$)")
    ax2.axhline(y=delta_min, color="red", linestyle="--", linewidth=2,
                label=f"Detection threshold (N=10$^4$)")

    # Biophoton regime
    ax1.axvspan(1e10, 1e15, alpha=0.1, color="gray", label="Biophoton regime")
    ax2.axvspan(1e10, 1e15, alpha=0.1, color="gray", label="Biophoton regime")

    ax1.set_xlabel("Number of modes M")
    ax1.set_ylabel("F - 1")
    ax1.set_title("Fano Factor Departure vs. Mode Number")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.set_ylim(1e-15, 1e2)

    ax2.set_xlabel("Number of modes M")
    ax2.set_ylabel("Mandel Q")
    ax2.set_title("Mandel Q Parameter vs. Mode Number")
    ax2.legend(fontsize=8, loc="upper right")
    ax2.set_ylim(1e-15, 1e2)

    fig.suptitle("Why Broadband Thermal Light Looks Poissonian", fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig02_fano_vs_modes.png"), dpi=150)
    plt.close(fig)
    print("  Created fig02_fano_vs_modes.png")


def fig_detector_artifact_chain():
    """Figure 3: How detector artifacts transform the Fano factor."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # (a) Efficiency degrades sub-Poissonian
    ax = axes[0, 0]
    etas = np.linspace(0.01, 1.0, 100)
    for F_true in [0.2, 0.5, 0.7, 0.9]:
        F_meas = etas * (F_true - 1.0) + 1.0
        ax.plot(etas, F_meas, label=f"$F_{{true}}={F_true}$")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Detector efficiency $\\eta$")
    ax.set_ylabel("Measured Fano factor")
    ax.set_title("(a) Effect of Detection Efficiency")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.1)

    # (b) Dark counts mask everything
    ax = axes[0, 1]
    dark_means = np.linspace(0, 20, 100)
    mu_det = 5.0  # detected signal mean
    for F1 in [0.5, 0.8, 1.0, 1.5, 2.0]:
        F2 = (mu_det * F1 + dark_means) / (mu_det + dark_means)
        ax.plot(dark_means, F2, label=f"$F_{{after\\_eff}}={F1}$")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Dark counts per interval")
    ax.set_ylabel("Measured Fano factor")
    ax.set_title(f"(b) Dark Count Dilution ($\\mu_{{det}}={mu_det}$)")
    ax.legend(fontsize=9)

    # (c) Full chain for sub-Poissonian source
    ax = axes[1, 0]
    signal_rates = np.logspace(0, 2.5, 100)
    detectors = {
        "Cooled PMT ($\\eta$=0.15, dark=2/s)": (0.15, 2.0),
        "Room-temp PMT ($\\eta$=0.12, dark=20/s)": (0.12, 20.0),
        "SNSPD ($\\eta$=0.85, dark=0.1/s)": (0.85, 0.1),
    }
    for label, (eta, dark) in detectors.items():
        F_meas = np.array([
            measured_fano_with_artifacts(0.5, r_s, eta, dark, 1e-6, 0.01)
            for r_s in signal_rates
        ])
        ax.semilogx(signal_rates, F_meas, label=label)
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    ax.axhline(y=0.5, color="red", linestyle="--", alpha=0.5, label="True $F=0.5$")
    ax.set_xlabel("Signal rate (photons/s)")
    ax.set_ylabel("Measured Fano factor")
    ax.set_title("(c) Sub-Poissonian Source Through Different Detectors")
    ax.legend(fontsize=8)
    ax.set_ylim(0.4, 1.05)

    # (d) Required N vs signal-to-dark ratio
    ax = axes[1, 1]
    sd_ratios = np.logspace(-1, 2, 100)
    for F_true, ls in [(0.5, "-"), (0.7, "--"), (0.9, ":")]:
        for eta_val, color in [(0.15, "C0"), (0.85, "C1")]:
            F_meas = np.array([
                measured_fano_with_artifacts(F_true, 10 * sdr, eta_val, 10.0)
                for sdr in sd_ratios
            ])
            delta = np.abs(F_meas - 1.0)
            N_req = np.where(delta > 1e-8,
                             2 * (1.645 + 0.842) ** 2 / delta ** 2,
                             np.inf)
            label = f"$F={F_true}$, $\\eta={eta_val}$" if ls == "-" else None
            ax.loglog(sd_ratios, N_req, linestyle=ls, color=color, label=label)
    ax.set_xlabel("Signal-to-dark ratio")
    ax.set_ylabel("Required N intervals (80% power)")
    ax.set_title("(d) Sample Size vs. Signal-to-Dark Ratio")
    ax.legend(fontsize=9)
    ax.set_ylim(1e1, 1e8)
    ax.axhline(y=36000, color="gray", linestyle="-.", alpha=0.5, label="10-hour measurement")

    fig.suptitle("Detector Artifacts and Their Impact on Photocount Statistics", fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig03_detector_artifacts.png"), dpi=150)
    plt.close(fig)
    print("  Created fig03_detector_artifacts.png")


def fig_squeezed_detection_landscape():
    """Figure 4: Squeezed state detection landscape."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    squeeze_rs = np.linspace(0.01, 1.5, 100)

    configs = [
        ("Cooled PMT", 0.15, 2.0, "C0"),
        ("SNSPD", 0.85, 0.1, "C1"),
        ("Room-temp PMT", 0.12, 20.0, "C2"),
    ]

    # (a) Source vs measured Fano
    ax = axes[0]
    for name, eta, dark, color in configs:
        F_source = []
        F_measured = []
        for r in squeeze_rs:
            alpha_val = np.sqrt(10.0) + 0j
            m = squeezed_state_moments(alpha_val, r, 0.0)
            F_source.append(m["fano_factor"])
            F_m = measured_fano_with_artifacts(
                m["fano_factor"], m["mean"], eta, dark, 1e-6, 0.01
            )
            F_measured.append(F_m)

        if name == "Cooled PMT":
            ax.plot(squeeze_rs, F_source, "k--", label="Source F", linewidth=2)
        ax.plot(squeeze_rs, F_measured, color=color, label=f"Measured ({name})")

    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Squeeze parameter r")
    ax.set_ylabel("Fano factor")
    ax.set_title("(a) Squeezing Degradation by Detector")
    ax.legend(fontsize=8)

    # (b) Required measurement time
    ax = axes[1]
    for name, eta, dark, color in configs:
        times = []
        for r in squeeze_rs:
            alpha_val = np.sqrt(10.0) + 0j
            m = squeezed_state_moments(alpha_val, r, 0.0)
            F_m = measured_fano_with_artifacts(
                m["fano_factor"], m["mean"], eta, dark, 1e-6, 0.01
            )
            delta = abs(F_m - 1.0)
            if delta > 1e-8 and F_m < 1.0:
                N = power_analysis_fano(delta, 0.05, 0.80)
                times.append(N / 3600)
            else:
                times.append(np.inf)
        times = np.array(times)
        mask = np.isfinite(times) & (times < 1e5)
        if np.any(mask):
            ax.semilogy(squeeze_rs[mask], times[mask], color=color, label=name)

    ax.set_xlabel("Squeeze parameter r")
    ax.set_ylabel("Required measurement time (hours)")
    ax.set_title("(b) Time to Detect Sub-Poissonian Statistics")
    ax.legend(fontsize=9)
    ax.axhline(y=1, color="gray", linestyle="--", alpha=0.3, label="1 hour")
    ax.axhline(y=10, color="gray", linestyle="-.", alpha=0.3, label="10 hours")

    # (c) Minimum detectable squeeze parameter vs |alpha|^2
    ax = axes[2]
    alpha_sqs = np.logspace(0, 3, 50)
    for name, eta, dark, color in configs:
        min_r = []
        for a2 in alpha_sqs:
            found_r = np.nan
            for r in np.linspace(0.01, 2.0, 200):
                alpha_val = np.sqrt(a2) + 0j
                m = squeezed_state_moments(alpha_val, r, 0.0)
                F_m = measured_fano_with_artifacts(
                    m["fano_factor"], m["mean"], eta, dark, 1e-6, 0.01
                )
                delta = abs(F_m - 1.0)
                if delta > 1e-8 and F_m < 1.0:
                    N = power_analysis_fano(delta, 0.05, 0.80)
                    if N < 36000:  # 10 hours at 1-s intervals
                        found_r = r
                        break
            min_r.append(found_r)
        min_r = np.array(min_r)
        mask = np.isfinite(min_r)
        if np.any(mask):
            ax.semilogx(alpha_sqs[mask], min_r[mask], color=color, label=name)

    ax.set_xlabel("$|\\alpha|^2$ (coherent photon number)")
    ax.set_ylabel("Minimum detectable squeeze parameter r")
    ax.set_title("(c) Min. Detectable Squeezing (10-hr budget)")
    ax.legend(fontsize=9)

    fig.suptitle("Can Biophoton Squeezing Be Detected?", fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig04_squeezed_detection.png"), dpi=150)
    plt.close(fig)
    print("  Created fig04_squeezed_detection.png")


def fig_dark_count_masking():
    """Figure 5: Dark count masking heatmaps."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    signal_rates = np.logspace(0, 2, 40)
    dark_rates = np.logspace(-0.3, 1.7, 40)

    for ax, F_true, title in [
        (axes[0], 2.0, "Super-Poissonian ($F_{true}=2.0$)"),
        (axes[1], 0.5, "Sub-Poissonian ($F_{true}=0.5$)"),
    ]:
        F_map = np.zeros((len(dark_rates), len(signal_rates)))
        for i, dr in enumerate(dark_rates):
            for j, sr in enumerate(signal_rates):
                F_map[i, j] = measured_fano_with_artifacts(
                    F_true, sr, 0.15, dr
                )

        im = ax.pcolormesh(signal_rates, dark_rates, F_map,
                           cmap="RdBu_r", vmin=0.5, vmax=1.5,
                           shading="auto")
        ax.set_xscale("log")
        ax.set_yscale("log")
        cs = ax.contour(signal_rates, dark_rates, F_map,
                        levels=[0.95, 0.99, 1.0, 1.01, 1.05],
                        colors="k", linewidths=0.8)
        ax.clabel(cs, fontsize=8, fmt="%.2f")
        ax.set_xlabel("Signal rate (photons/s)")
        ax.set_ylabel("Dark count rate (counts/s)")
        ax.set_title(title)
        plt.colorbar(im, ax=ax, label="Measured Fano factor")

    fig.suptitle("Dark Count Masking of Non-Poissonian Statistics ($\\eta=0.15$)",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig05_dark_count_masking.png"), dpi=150)
    plt.close(fig)
    print("  Created fig05_dark_count_masking.png")


def fig_nonstationarity_effects():
    """Figure 6: Nonstationarity and false positives."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Load precomputed results if available
    ns_file = os.path.join(RESULTS_DIR, "nonstationarity_fpr.npz")
    if os.path.exists(ns_file):
        data = np.load(ns_file)
        depths = data["depths"]
        fpr = data["fpr"]
    else:
        # Compute on the fly (smaller MC)
        from sensitivity_analysis import nonstationarity_false_positive_rate
        depths = np.linspace(0, 0.3, 15)
        fpr = nonstationarity_false_positive_rate(
            5000, 10.0, depths, 100.0, n_mc=200,
            rng=np.random.default_rng(42))

    # (a) False positive rate vs modulation depth
    ax = axes[0]
    ax.plot(depths * 100, fpr * 100, "o-", color="C0", linewidth=2)
    ax.axhline(y=5, color="red", linestyle="--", label="5% threshold")
    ax.set_xlabel("Rate modulation depth (%)")
    ax.set_ylabel("False positive rate (%)")
    ax.set_title("(a) Spurious Super-Poissonian Detections")
    ax.legend()
    ax.set_xlim(0, 30)

    # (b) Example: Poisson process with slowly varying rate
    ax = axes[1]
    rng = np.random.default_rng(123)
    T = 1000
    t = np.arange(T)
    rate_base = 10.0
    # Stationary
    counts_stat = rng.poisson(rate_base, T)
    # 10% modulation
    rates_mod = rate_base * (1 + 0.1 * np.sin(2 * np.pi * t / 100))
    counts_mod = rng.poisson(rates_mod)

    ax.plot(t[:200], counts_stat[:200], alpha=0.5, label="Stationary ($F$={:.3f})".format(
        counts_stat.var(ddof=1)/counts_stat.mean()))
    ax.plot(t[:200], counts_mod[:200], alpha=0.5, label="10% modulated ($F$={:.3f})".format(
        counts_mod.var(ddof=1)/counts_mod.mean()))
    ax.set_xlabel("Interval index")
    ax.set_ylabel("Counts per interval")
    ax.set_title("(b) Stationary vs. Modulated Poisson Process")
    ax.legend(fontsize=9)

    fig.suptitle("Nonstationarity Creates Spurious Super-Poissonian Signatures",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig06_nonstationarity.png"), dpi=150)
    plt.close(fig)
    print("  Created fig06_nonstationarity.png")


def fig_power_analysis_landscape():
    """Figure 7: Required measurement time landscape."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    # Grid: signal rate vs desired Fano departure
    signal_rates = np.logspace(0, 2, 50)
    deltas = np.array([0.01, 0.02, 0.05, 0.10, 0.20])

    colors = cm.viridis(np.linspace(0.2, 0.9, len(deltas)))

    for delta, color in zip(deltas, colors):
        N_needed = power_analysis_fano(delta, alpha=0.01, power=0.80)
        hours = N_needed / 3600  # at 1-s intervals

        # But we also need signal >> dark for the departure to be measurable
        # F_measured departure = eta * delta * mu / (eta*mu + dark)
        # approximately delta * (S/D) / (1 + S/D)
        dark = 5.0
        eta = 0.15
        effective_delta = delta * eta * signal_rates / (eta * signal_rates + dark)
        N_effective = np.where(
            effective_delta > 1e-8,
            2 * (2.326 + 0.842) ** 2 / effective_delta ** 2,
            np.inf
        )
        hours_eff = N_effective / 3600

        ax.semilogy(signal_rates, hours_eff, color=color, linewidth=2,
                    label=f"|$\\Delta F$| = {delta}")

    ax.axhline(y=1, color="gray", linestyle="--", alpha=0.3)
    ax.axhline(y=10, color="gray", linestyle="-.", alpha=0.3)
    ax.text(1.5, 1.2, "1 hour", fontsize=8, color="gray")
    ax.text(1.5, 12, "10 hours", fontsize=8, color="gray")

    ax.set_xlabel("Signal rate (photons/s at source)")
    ax.set_ylabel("Required measurement time (hours)")
    ax.set_title("Measurement Time to Detect Fano Factor Departure\n"
                 "($\\eta=0.15$, dark=5/s, $\\alpha=0.01$, power=80%)")
    ax.legend(fontsize=9, title="True |F - 1|")
    ax.set_xlim(1, 100)
    ax.set_ylim(0.01, 1e6)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig07_power_analysis.png"), dpi=150)
    plt.close(fig)
    print("  Created fig07_power_analysis.png")


def fig_bayesian_discrimination():
    """Figure 8: Bayesian model comparison Monte Carlo."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    rng = np.random.default_rng(42)
    N_intervals = 5000

    # (a) Distribution of Fano estimates for different sources
    ax = axes[0]
    n_mc = 500

    sources = {
        "Poisson ($\\mu=10$)": ("poisson", {"mean_count": 10.0}),
        "NB ($\\mu=10$, $M=50$)": ("multimode_thermal", {"mean_count": 10.0, "num_modes": 50}),
        "NB ($\\mu=10$, $M=5$)": ("multimode_thermal", {"mean_count": 10.0, "num_modes": 5}),
    }

    for label, (stype, sparams) in sources.items():
        fano_vals = []
        for _ in range(n_mc):
            data = generate_samples(stype, N_intervals, sparams, rng=rng)
            result = estimate_fano_factor(data)
            fano_vals.append(result["fano"])
        ax.hist(fano_vals, bins=30, alpha=0.5, density=True, label=label)

    ax.axvline(x=1.0, color="red", linestyle="--", label="$F=1$ (Poisson)")
    ax.set_xlabel("Estimated Fano factor")
    ax.set_ylabel("Density")
    ax.set_title(f"(a) Fano Factor Distributions (N={N_intervals})")
    ax.legend(fontsize=8)

    # (b) Detection power vs N for different F_true
    ax = axes[1]
    N_values = [100, 500, 1000, 2000, 5000, 10000]
    F_true_vals = [1.0, 1.02, 1.05, 1.1, 1.2, 1.5, 2.0]
    n_mc_power = 200

    power_matrix = np.zeros((len(F_true_vals), len(N_values)))

    for i, F_true in enumerate(F_true_vals):
        for j, N in enumerate(N_values):
            rejects = 0
            for _ in range(n_mc_power):
                if F_true == 1.0:
                    data = rng.poisson(10.0, size=N)
                else:
                    M = 10.0 / (F_true - 1.0)
                    data = generate_samples("multimode_thermal", N,
                                           {"mean_count": 10.0, "num_modes": M},
                                           rng=rng)
                result = estimate_fano_factor(data)
                if result["p_value_super"] < 0.05:
                    rejects += 1
            power_matrix[i, j] = rejects / n_mc_power

    for i, F_true in enumerate(F_true_vals):
        ax.plot(N_values, power_matrix[i, :], "o-",
                label=f"$F_{{true}}={F_true}$")

    ax.axhline(y=0.05, color="gray", linestyle=":", alpha=0.5, label="Size ($\\alpha=0.05$)")
    ax.axhline(y=0.80, color="gray", linestyle="--", alpha=0.5, label="80% power")
    ax.set_xlabel("Number of counting intervals N")
    ax.set_ylabel("Rejection rate (power)")
    ax.set_title("(b) Power of Fano Factor Test ($\\mu=10$)")
    ax.legend(fontsize=7, ncol=2)
    ax.set_xscale("log")

    fig.suptitle("Statistical Discrimination Between Source Models", fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig08_discrimination_power.png"), dpi=150)
    plt.close(fig)
    print("  Created fig08_discrimination_power.png")


def generate_all_figures():
    """Generate all figures."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    print("Generating figures...")

    fig_distribution_comparison()
    fig_fano_vs_modes()
    fig_detector_artifact_chain()
    fig_squeezed_detection_landscape()
    fig_dark_count_masking()
    fig_nonstationarity_effects()
    fig_power_analysis_landscape()
    fig_bayesian_discrimination()

    print(f"\nAll figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    generate_all_figures()
