"""
Visualization functions for biophoton demyelination simulation results.

All functions return matplotlib Figure objects for flexible display/saving.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt

from . import constants as C
from .axon import AxonGeometry
from .demyelination import DemyelinationState, hill_response
from .emission import ros_spectrum, disease_emission, waveguide_filtered_emission

if TYPE_CHECKING:
    from .cuprizone import CuprizoneExperiment


def plot_spectrum(
    axon: AxonGeometry,
    state: DemyelinationState | None = None,
    show_components: bool = True,
) -> plt.Figure:
    """Plot emission spectrum: healthy vs. demyelinated (if state provided).

    Shows the waveguide-filtered emission that a detector would see.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    lam = C.DEFAULT_LAMBDA_RANGE_NM

    # Healthy baseline
    healthy = DemyelinationState(0, 0, 0)
    healthy_spectrum = waveguide_filtered_emission(axon, healthy, lam)
    ax.plot(lam, healthy_spectrum, "b-", linewidth=2, label="Healthy", alpha=0.8)

    # Demyelinated
    if state is not None and not state.is_healthy:
        disease_spectrum = waveguide_filtered_emission(axon, state, lam)
        ax.plot(lam, disease_spectrum, "r-", linewidth=2,
                label=f"Demyelinated ({state})", alpha=0.8)

        # Shade the difference
        ax.fill_between(lam, healthy_spectrum, disease_spectrum,
                        alpha=0.15, color="red", label="Excess emission")

    # ROS component markers
    if show_components:
        for center, _fwhm, _amp, species in C.ROS_COMPONENTS:
            ax.axvline(center, color="gray", linestyle=":", alpha=0.3, linewidth=0.5)
            ax.text(center, ax.get_ylim()[1] * 0.95, species.split("(")[0].strip(),
                    rotation=90, fontsize=6, alpha=0.5, va="top", ha="right")

    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Detected photons / cm² / s / nm")
    ax.set_title(f"Biophoton Emission Spectrum — {axon}")
    ax.legend()
    ax.set_xlim(300, 800)
    fig.tight_layout()
    return fig


def plot_timeline(
    experiment: CuprizoneExperiment,
    uncertainty_results: dict | None = None,
) -> plt.Figure:
    """Plot cuprizone experiment results: counts, significance, and damage over weeks.

    Parameters
    ----------
    uncertainty_results : dict or None
        Output from experiment.run_with_uncertainty(). When provided, plots
        credible bands instead of single-line estimates.
    """
    if not experiment.timepoints:
        raise ValueError("Run the experiment first with experiment.run()")

    weeks = [tp.week for tp in experiment.timepoints]
    mean_treated = [np.mean(tp.detected_counts) for tp in experiment.timepoints]
    std_treated = [np.std(tp.detected_counts) for tp in experiment.timepoints]
    mean_control = [np.mean(tp.background_counts) for tp in experiment.timepoints]
    alphas = [tp.state.alpha for tp in experiment.timepoints]

    n_panels = 4 if uncertainty_results else 3
    fig, axes = plt.subplots(n_panels, 1, figsize=(10, 3 * n_panels + 1), sharex=True)

    # Panel 1: Photon counts
    ax1 = axes[0]
    ax1.errorbar(weeks, mean_treated, yerr=std_treated, fmt="ro-",
                 linewidth=2, capsize=4, label="Treated")
    ax1.plot(weeks, mean_control, "b^--", linewidth=1.5, label="Control")
    ax1.set_ylabel("Mean detected counts")
    ax1.legend()
    ax1.set_title(f"Cuprizone Experiment — {experiment.detector.name} detector, "
                  f"{experiment.n_mice} mice/group")

    # Panel 2: Effect size (Cohen's d) with CI
    ax2 = axes[1]
    effect_sizes = [tp.effect_size for tp in experiment.timepoints]
    p_values = [tp.p_value for tp in experiment.timepoints]

    if uncertainty_results and "effect_sizes_by_week" in uncertainty_results:
        es_medians = [uncertainty_results["effect_sizes_by_week"].get(w, {}).get("median", 0)
                      for w in weeks]
        es_lo = [uncertainty_results["effect_sizes_by_week"].get(w, {}).get("ci_90", (0, 0))[0]
                 for w in weeks]
        es_hi = [uncertainty_results["effect_sizes_by_week"].get(w, {}).get("ci_90", (0, 0))[1]
                 for w in weeks]
        ax2.fill_between(weeks, es_lo, es_hi, alpha=0.2, color="steelblue", label="90% CI")
        ax2.plot(weeks, es_medians, "b-o", linewidth=2, label="Median effect size")
    else:
        ax2.plot(weeks, effect_sizes, "b-o", linewidth=2, label="Cohen's d")
        # Error bars from single-run CI
        es_err_lo = [tp.effect_size - tp.effect_size_ci[0] for tp in experiment.timepoints]
        es_err_hi = [tp.effect_size_ci[1] - tp.effect_size for tp in experiment.timepoints]
        ax2.errorbar(weeks, effect_sizes, yerr=[es_err_lo, es_err_hi],
                     fmt="none", ecolor="steelblue", capsize=3, alpha=0.5)

    ax2.axhline(0.8, color="orange", linestyle="--", alpha=0.5, label="Large effect (0.8)")
    ax2.set_ylabel("Effect size (Cohen's d)")
    ax2.legend(fontsize=8)

    # Panel 3: Demyelination state
    ax3 = axes[2]
    ax3.plot(weeks, alphas, "k-o", linewidth=2, label="α (thickness loss)")
    gammas = [tp.state.gamma for tp in experiment.timepoints]
    rhos = [tp.state.rho for tp in experiment.timepoints]
    ax3.plot(weeks, gammas, "g-s", linewidth=1.5, label="γ (gap fraction)")
    ax3.plot(weeks, rhos, "m-d", linewidth=1.5, label="ρ (irregularity)")
    ax3.set_ylabel("Damage parameter")
    ax3.legend()
    ax3.set_ylim(-0.05, 1.05)

    # Panel 4: Power curve (fraction significant over MC iterations)
    if uncertainty_results and "p_values_by_week" in uncertainty_results:
        ax4 = axes[3]
        power = [uncertainty_results["p_values_by_week"].get(w, {}).get("fraction_significant", 0)
                 for w in weeks]
        ax4.bar(weeks, power, width=0.6, color="darkgreen", alpha=0.7)
        ax4.axhline(0.8, color="red", linestyle="--", alpha=0.5, label="80% power")
        ax4.set_ylabel("Statistical power")
        ax4.set_ylim(0, 1.05)
        ax4.legend()

    axes[-1].set_xlabel("Week")
    fig.tight_layout()
    return fig


def plot_roc(roc_result: dict[str, np.ndarray | float]) -> plt.Figure:
    """Plot ROC curve with AUC annotation."""
    fig, ax = plt.subplots(figsize=(7, 7))

    ax.plot(roc_result["fpr"], roc_result["tpr"], "b-", linewidth=2,
            label=f'ROC (AUC = {roc_result["auc"]:.3f})')
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Random classifier")
    ax.fill_between(roc_result["fpr"], 0, roc_result["tpr"], alpha=0.1, color="blue")

    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity)")
    ax.set_title("ROC Curve: Healthy vs. Demyelinated Classification")
    ax.legend(loc="lower right")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal")
    fig.tight_layout()
    return fig


def plot_prediction_intervals(
    weeks: np.ndarray | list[float],
    median: np.ndarray | list[float],
    ci_50_lo: np.ndarray | list[float],
    ci_50_hi: np.ndarray | list[float],
    ci_90_lo: np.ndarray | list[float],
    ci_90_hi: np.ndarray | list[float],
    ylabel: str = "Predicted value",
    title: str = "Prediction with uncertainty",
) -> plt.Figure:
    """Fan chart showing median prediction + 50%/90% credible bands."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.fill_between(weeks, ci_90_lo, ci_90_hi, alpha=0.15, color="steelblue",
                    label="90% credible interval")
    ax.fill_between(weeks, ci_50_lo, ci_50_hi, alpha=0.3, color="steelblue",
                    label="50% credible interval")
    ax.plot(weeks, median, "b-", linewidth=2, label="Median prediction")

    ax.set_xlabel("Week")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_tornado(tornado_data: dict) -> plt.Figure:
    """Sensitivity tornado chart showing which parameters matter most.

    Parameters
    ----------
    tornado_data : dict
        Output from uncertainty.tornado_plot_data(). Must have keys:
        param_names, low_values, high_values, nominal_value.
    """
    names = tornado_data["param_names"]
    lows = tornado_data["low_values"]
    highs = tornado_data["high_values"]
    nominal = tornado_data["nominal_value"]

    fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.5 + 1)))
    y_pos = np.arange(len(names))

    # Bars extending from nominal
    left_bars = [min(l, nominal) for l in lows]
    right_bars = [max(h, nominal) for h in highs]

    for i, (name, lo, hi) in enumerate(zip(names, lows, highs)):
        ax.barh(i, hi - nominal, left=nominal, color="steelblue", alpha=0.7,
                height=0.6, edgecolor="navy")
        ax.barh(i, lo - nominal, left=nominal, color="coral", alpha=0.7,
                height=0.6, edgecolor="darkred")

    ax.axvline(nominal, color="black", linewidth=1.5, linestyle="-")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([n.replace("_", " ").title() for n in names])
    ax.set_xlabel("Predicted emission rate")
    ax.set_title("Parameter Sensitivity (Tornado Chart)")
    ax.invert_yaxis()
    fig.tight_layout()
    return fig


def plot_dose_response(
    s_base: float = 1.0,
    s_max: float = 10.0,
    n_values: list[float] | None = None,
    k: float = 0.5,
) -> plt.Figure:
    """Plot Hill dose-response curves for different Hill coefficients."""
    if n_values is None:
        n_values = [1.0, 2.0, 3.0, 5.0]

    fig, ax = plt.subplots(figsize=(8, 5))
    damage = np.linspace(0, 1, 200)

    for n in n_values:
        response = np.array([hill_response(d, s_base, s_max, n, k) for d in damage])
        ax.plot(damage, response, linewidth=2, label=f"n = {n:.1f}")

    ax.axhline((s_base + s_max) / 2, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(k, color="gray", linestyle=":", alpha=0.5,
               label=f"K₅₀ = {k}")

    ax.set_xlabel("Demyelination severity")
    ax.set_ylabel("Biophoton signal (relative)")
    ax.set_title("Hill Dose-Response: Emission vs. Demyelination")
    ax.legend()
    fig.tight_layout()
    return fig


def plot_waveguide_modes(axon: AxonGeometry) -> plt.Figure:
    """Visualize the mode structure of the myelin waveguide across wavelengths."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    lam = np.linspace(200, 950, 300)

    # V-number vs wavelength
    v_numbers = np.array([axon.v_number(l) for l in lam])
    ax1.plot(lam, v_numbers, "b-", linewidth=2)
    ax1.axhline(2.405, color="red", linestyle="--", alpha=0.7, label="Single-mode cutoff")
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("V-number")
    ax1.set_title(f"Waveguide V-number — {axon}")
    ax1.legend()

    # Number of modes vs wavelength
    modes = np.array([axon.num_modes(l) for l in lam])
    ax2.semilogy(lam, modes, "g-", linewidth=2)
    ax2.set_xlabel("Wavelength (nm)")
    ax2.set_ylabel("Number of guided modes")
    ax2.set_title("Mode count vs. wavelength")

    fig.tight_layout()
    return fig
