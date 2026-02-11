"""
MS subtype modeling: RRMS, SPMS, PPMS biophoton signatures.

Different MS patterns produce different spatial/temporal patterns of
demyelination. This module models each subtype and predicts distinct
biophoton signatures.

Usage:
    python src/ms_subtypes.py
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from constants import (
    RRMS_RELAPSE_RATE_PER_YEAR, RRMS_RELAPSE_DURATION_WEEKS,
    RRMS_RECOVERY_FRACTION,
    SPMS_ANNUAL_MYELIN_LOSS_FRACTION, SPMS_INFLAMMATION_LEVEL,
    PPMS_ANNUAL_MYELIN_LOSS_FRACTION, PPMS_INFLAMMATION_LEVEL,
    N_LAYERS_HEALTHY, WAVELENGTH_SHIFT_PER_LAYER_NM,
    HEALTHY_OPERATING_WAVELENGTH_NM,
    KAPPA_HEALTHY, G_PHI_PSI, PSI_AMPLITUDE,
    BASAL_EMISSION_RATE, INFLAMMATORY_EMISSION_FACTOR_HIGH,
)


# ---------------------------------------------------------------------------
# RRMS: relapsing-remitting
# ---------------------------------------------------------------------------

def rrms_myelin_trajectory(
    t_years: np.ndarray,
    relapse_rate: float = RRMS_RELAPSE_RATE_PER_YEAR,
    relapse_duration_weeks: float = RRMS_RELAPSE_DURATION_WEEKS,
    recovery_fraction: float = RRMS_RECOVERY_FRACTION,
    seed: int = 42,
) -> dict:
    """Simulate RRMS myelin integrity over time.

    Relapses are modelled as Poisson-distributed acute demyelination episodes,
    each followed by partial remyelination. The net effect is a step-wise decline
    with sawtooth character.

    Parameters
    ----------
    t_years : ndarray
        Time axis in years.
    relapse_rate : float
        Mean relapses per year.
    relapse_duration_weeks : float
        Duration of acute demyelination per relapse.
    recovery_fraction : float
        Fraction of myelin recovered during remission.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    dict with 't_years', 'myelin_integrity', 'inflammation', 'relapse_times'
    """
    rng = np.random.default_rng(seed)
    dt_yr = t_years[1] - t_years[0]
    n = len(t_years)

    myelin = np.ones(n)        # fraction of intact myelin
    inflammation = np.zeros(n)  # inflammation level

    # Generate relapse onset times via Poisson process
    total_years = t_years[-1] - t_years[0]
    n_relapses = rng.poisson(relapse_rate * total_years)
    relapse_onset_years = np.sort(rng.uniform(t_years[0], t_years[-1], n_relapses))

    relapse_dur_yr = relapse_duration_weeks / 52.0
    # Myelin loss per relapse event (fraction of remaining myelin)
    loss_per_relapse = 0.15

    current_myelin = 1.0
    relapse_idx = 0
    in_relapse = False
    relapse_end = -1.0
    recovery_target = 1.0

    for i, t in enumerate(t_years):
        # Check for new relapse
        if relapse_idx < n_relapses and t >= relapse_onset_years[relapse_idx]:
            in_relapse = True
            relapse_end = t + relapse_dur_yr
            # Acute myelin loss
            lost = loss_per_relapse * current_myelin
            current_myelin -= lost
            recovery_target = current_myelin + lost * recovery_fraction
            relapse_idx += 1

        # During relapse: inflammation is high, myelin stays low
        if in_relapse and t < relapse_end:
            inflammation[i] = 0.8 + 0.2 * rng.random()
        elif in_relapse and t >= relapse_end:
            # Remission: partial recovery
            in_relapse = False
            current_myelin = recovery_target

        myelin[i] = current_myelin
        if not in_relapse:
            # Low-level between-relapse inflammation
            inflammation[i] = 0.05 * rng.random()

    return {
        "t_years": t_years,
        "myelin_integrity": myelin,
        "inflammation": inflammation,
        "relapse_times": relapse_onset_years,
    }


# ---------------------------------------------------------------------------
# SPMS: secondary progressive
# ---------------------------------------------------------------------------

def spms_myelin_trajectory(
    t_years: np.ndarray,
    annual_loss: float = SPMS_ANNUAL_MYELIN_LOSS_FRACTION,
    inflammation: float = SPMS_INFLAMMATION_LEVEL,
    initial_myelin: float = 0.65,
    seed: int = 42,
) -> dict:
    """Simulate SPMS: gradual progression with chronic low-grade inflammation.

    Parameters
    ----------
    t_years : ndarray
        Time axis (years since SPMS onset).
    annual_loss : float
        Fraction of remaining myelin lost per year.
    inflammation : float
        Chronic low-grade inflammation level.
    initial_myelin : float
        Starting myelin integrity (post-RRMS damage).

    Returns
    -------
    dict with keys 't_years', 'myelin_integrity', 'inflammation'
    """
    rng = np.random.default_rng(seed)
    n = len(t_years)
    myelin = np.zeros(n)
    inflam = np.zeros(n)

    current = initial_myelin
    for i, t in enumerate(t_years):
        dt = t_years[1] - t_years[0] if i > 0 else 0
        # Exponential decay
        current *= (1.0 - annual_loss) ** dt
        myelin[i] = current
        # Chronic low-grade inflammation with fluctuations
        inflam[i] = inflammation * (1.0 + 0.3 * rng.standard_normal())
        inflam[i] = max(0, inflam[i])

    return {
        "t_years": t_years,
        "myelin_integrity": myelin,
        "inflammation": inflam,
    }


# ---------------------------------------------------------------------------
# PPMS: primary progressive
# ---------------------------------------------------------------------------

def ppms_myelin_trajectory(
    t_years: np.ndarray,
    annual_loss: float = PPMS_ANNUAL_MYELIN_LOSS_FRACTION,
    inflammation: float = PPMS_INFLAMMATION_LEVEL,
    seed: int = 42,
) -> dict:
    """Simulate PPMS: steady progressive decline from onset.

    Parameters
    ----------
    t_years : ndarray
        Time axis (years since PPMS onset).
    annual_loss : float
        Fraction of remaining myelin lost per year.
    inflammation : float
        Minimal diffuse inflammation.

    Returns
    -------
    dict with keys 't_years', 'myelin_integrity', 'inflammation'
    """
    rng = np.random.default_rng(seed)
    n = len(t_years)
    myelin = np.zeros(n)
    inflam = np.zeros(n)

    current = 1.0  # starts at full myelin
    for i in range(n):
        dt = t_years[1] - t_years[0] if i > 0 else 0
        current *= (1.0 - annual_loss) ** dt
        myelin[i] = current
        inflam[i] = inflammation * (1.0 + 0.2 * rng.standard_normal())
        inflam[i] = max(0, inflam[i])

    return {
        "t_years": t_years,
        "myelin_integrity": myelin,
        "inflammation": inflam,
    }


# ---------------------------------------------------------------------------
# Biophoton signature computation
# ---------------------------------------------------------------------------

def compute_biophoton_signatures(trajectory: dict) -> dict:
    """Compute predicted biophoton observables from a myelin trajectory.

    Parameters
    ----------
    trajectory : dict
        Must contain 'myelin_integrity' and 'inflammation' arrays.

    Returns
    -------
    dict with biophoton observables.
    """
    m = trajectory["myelin_integrity"]
    infl = trajectory["inflammation"]

    # Operating wavelength
    layers_remaining = m * N_LAYERS_HEALTHY
    layers_lost = N_LAYERS_HEALTHY - layers_remaining
    wavelength = HEALTHY_OPERATING_WAVELENGTH_NM - layers_lost * WAVELENGTH_SHIFT_PER_LAYER_NM

    # Lateral emission: increases with myelin loss + inflammation
    # Base scattering: proportional to (1 - m)
    scattering_component = BASAL_EMISSION_RATE * 5.0 * (1.0 - m)
    # Inflammatory component
    inflammatory_component = BASAL_EMISSION_RATE * INFLAMMATORY_EMISSION_FACTOR_HIGH * infl
    total_emission = BASAL_EMISSION_RATE + scattering_component + inflammatory_component

    # Effective kappa
    kappa = KAPPA_HEALTHY / np.maximum(m ** 2, 0.01)
    kappa += 0.5 * infl  # inflammation adds decoherence

    # Coherence field steady-state: Lambda_ss = g * |Psi|^2 * Phi / kappa
    Lambda_ss = G_PHI_PSI * PSI_AMPLITUDE**2 / kappa

    # Singlet-O2 / carbonyl ratio (inflammatory marker)
    # High in autoimmune attacks (MPO), low in quiescent tissue
    so2_carbonyl_ratio = 0.2 + 2.0 * infl

    return {
        "wavelength_nm": wavelength,
        "total_emission": total_emission,
        "kappa": kappa,
        "Lambda_ss": Lambda_ss,
        "so2_carbonyl_ratio": so2_carbonyl_ratio,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_ms_subtypes(save_path: str = "../figures/ms_subtype_comparison.png"):
    """Generate comparison figure for all three MS subtypes."""
    t_rrms = np.linspace(0, 20, 2000)
    t_spms = np.linspace(0, 15, 1500)
    t_ppms = np.linspace(0, 20, 2000)

    traj_rrms = rrms_myelin_trajectory(t_rrms)
    traj_spms = spms_myelin_trajectory(t_spms)
    traj_ppms = ppms_myelin_trajectory(t_ppms)

    sig_rrms = compute_biophoton_signatures(traj_rrms)
    sig_spms = compute_biophoton_signatures(traj_spms)
    sig_ppms = compute_biophoton_signatures(traj_ppms)

    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    subtypes = [
        ("RRMS", t_rrms, traj_rrms, sig_rrms, "tab:blue"),
        ("SPMS", t_spms, traj_spms, sig_spms, "tab:orange"),
        ("PPMS", t_ppms, traj_ppms, sig_ppms, "tab:red"),
    ]

    for col, (name, t, traj, sig, color) in enumerate(subtypes):
        # Row 1: Myelin integrity + inflammation
        ax = axes[0, col]
        ax.plot(t, traj["myelin_integrity"], color=color, linewidth=1.5,
                label="Myelin integrity")
        ax2 = ax.twinx()
        ax2.plot(t, traj["inflammation"], color="gray", alpha=0.5, linewidth=0.5,
                 label="Inflammation")
        ax2.set_ylabel("Inflammation", color="gray", fontsize=9)
        ax2.set_ylim(0, 1.2)
        ax.set_ylabel("Myelin Integrity")
        ax.set_title(f"{name}", fontsize=12, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)
        if name == "RRMS":
            for rt in traj.get("relapse_times", []):
                ax.axvline(x=rt, color="red", alpha=0.2, linewidth=0.5)

        # Row 2: Wavelength shift + emission intensity
        ax = axes[1, col]
        ax.plot(t, sig["wavelength_nm"], color=color, linewidth=1.5)
        ax.axhline(y=HEALTHY_OPERATING_WAVELENGTH_NM, color="green",
                    linestyle="--", alpha=0.4)
        ax.set_ylabel("Operating Wavelength (nm)")
        ax.grid(True, alpha=0.3)

        # Row 3: Coherence field
        ax = axes[2, col]
        ax.plot(t, sig["Lambda_ss"], color=color, linewidth=1.5)
        ax.set_xlabel("Time (years)")
        ax.set_ylabel(r"Coherence $\Lambda_{ss}$")
        ax.grid(True, alpha=0.3)

    fig.suptitle("MS Subtype Biophoton Signature Predictions",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_ms_overlay(save_path: str = "../figures/ms_subtype_overlay.png"):
    """Overlay all three subtypes on shared axes for direct comparison."""
    t = np.linspace(0, 20, 2000)

    traj_rrms = rrms_myelin_trajectory(t)
    traj_spms = spms_myelin_trajectory(t, initial_myelin=0.65)
    traj_ppms = ppms_myelin_trajectory(t)

    sig_rrms = compute_biophoton_signatures(traj_rrms)
    sig_spms = compute_biophoton_signatures(traj_spms)
    sig_ppms = compute_biophoton_signatures(traj_ppms)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Myelin integrity
    ax = axes[0, 0]
    ax.plot(t, traj_rrms["myelin_integrity"], "b-", linewidth=1.5, label="RRMS")
    ax.plot(t, traj_spms["myelin_integrity"], "orange", linewidth=1.5, label="SPMS")
    ax.plot(t, traj_ppms["myelin_integrity"], "r-", linewidth=1.5, label="PPMS")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Myelin Integrity")
    ax.set_title("Myelin Integrity Over Time")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Wavelength
    ax = axes[0, 1]
    ax.plot(t, sig_rrms["wavelength_nm"], "b-", linewidth=1.5, label="RRMS")
    ax.plot(t, sig_spms["wavelength_nm"], "orange", linewidth=1.5, label="SPMS")
    ax.plot(t, sig_ppms["wavelength_nm"], "r-", linewidth=1.5, label="PPMS")
    ax.axhline(y=HEALTHY_OPERATING_WAVELENGTH_NM, color="green",
                linestyle="--", alpha=0.4, label="Healthy")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Operating Wavelength (nm)")
    ax.set_title("Predicted Spectral Shift")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Total emission
    ax = axes[1, 0]
    ax.semilogy(t, sig_rrms["total_emission"], "b-", linewidth=1, alpha=0.8, label="RRMS")
    ax.semilogy(t, sig_spms["total_emission"], "orange", linewidth=1.5, label="SPMS")
    ax.semilogy(t, sig_ppms["total_emission"], "r-", linewidth=1.5, label="PPMS")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Total Emission (photons/s/cm$^2$)")
    ax.set_title("Predicted Biophoton Emission")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Coherence field
    ax = axes[1, 1]
    ax.plot(t, sig_rrms["Lambda_ss"], "b-", linewidth=1.5, label="RRMS")
    ax.plot(t, sig_spms["Lambda_ss"], "orange", linewidth=1.5, label="SPMS")
    ax.plot(t, sig_ppms["Lambda_ss"], "r-", linewidth=1.5, label="PPMS")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel(r"Steady-state $\Lambda$")
    ax.set_title("Predicted Coherence Field")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.suptitle("MS Subtype Comparison: Biophoton Predictions",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    os.makedirs("../figures", exist_ok=True)

    plot_ms_subtypes()
    plot_ms_overlay()

    # Print summary statistics
    t = np.linspace(0, 20, 2000)
    for name, func, kwargs in [
        ("RRMS", rrms_myelin_trajectory, {}),
        ("SPMS", spms_myelin_trajectory, {"initial_myelin": 0.65}),
        ("PPMS", ppms_myelin_trajectory, {}),
    ]:
        traj = func(t, **kwargs)
        sig = compute_biophoton_signatures(traj)
        m_final = traj["myelin_integrity"][-1]
        wl_final = sig["wavelength_nm"][-1]
        lam_final = sig["Lambda_ss"][-1]
        print(f"\n{name} at year 20:")
        print(f"  Myelin integrity: {m_final:.3f}")
        print(f"  Wavelength:       {wl_final:.1f} nm (shift = {HEALTHY_OPERATING_WAVELENGTH_NM - wl_final:.1f} nm)")
        print(f"  Lambda_ss:        {lam_final:.6f}")
