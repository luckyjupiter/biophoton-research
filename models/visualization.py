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


def plot_timeline(experiment: CuprizoneExperiment) -> plt.Figure:
    """Plot cuprizone experiment results: counts and significance over weeks."""
    if not experiment.timepoints:
        raise ValueError("Run the experiment first with experiment.run()")

    weeks = [tp.week for tp in experiment.timepoints]
    mean_treated = [np.mean(tp.detected_counts) for tp in experiment.timepoints]
    std_treated = [np.std(tp.detected_counts) for tp in experiment.timepoints]
    mean_control = [np.mean(tp.background_counts) for tp in experiment.timepoints]
    sigmas = [tp.li_ma_sigma for tp in experiment.timepoints]
    alphas = [tp.state.alpha for tp in experiment.timepoints]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    # Panel 1: Photon counts
    ax1.errorbar(weeks, mean_treated, yerr=std_treated, fmt="ro-",
                 linewidth=2, capsize=4, label="Treated")
    ax1.plot(weeks, mean_control, "b^--", linewidth=1.5, label="Control")
    ax1.set_ylabel("Mean detected counts")
    ax1.legend()
    ax1.set_title(f"Cuprizone Experiment — {experiment.detector.name} detector, "
                  f"{experiment.n_mice} mice/group")

    # Panel 2: Li-Ma significance
    ax2.bar(weeks, sigmas, width=0.6, color="steelblue", alpha=0.7)
    ax2.axhline(3.0, color="orange", linestyle="--", label="3σ threshold")
    ax2.axhline(5.0, color="red", linestyle="--", label="5σ threshold")
    ax2.set_ylabel("Li-Ma significance (σ)")
    ax2.legend()

    # Panel 3: Demyelination state
    ax3.plot(weeks, alphas, "k-o", linewidth=2, label="α (thickness loss)")
    gammas = [tp.state.gamma for tp in experiment.timepoints]
    rhos = [tp.state.rho for tp in experiment.timepoints]
    ax3.plot(weeks, gammas, "g-s", linewidth=1.5, label="γ (gap fraction)")
    ax3.plot(weeks, rhos, "m-d", linewidth=1.5, label="ρ (irregularity)")
    ax3.set_ylabel("Damage parameter")
    ax3.set_xlabel("Week")
    ax3.legend()
    ax3.set_ylim(-0.05, 1.05)

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
