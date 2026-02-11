"""
Demyelination progression model.

Models how myelin degradation (thinning, gap formation, inflammation) degrades
the coherence field Lambda over time. Implements the parametric waveguide model
from Track 06 Section 4.1 and the coherence-field ODE from the M-Phi framework.

Usage:
    python src/demyelination_progression.py
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Optional

from constants import (
    N_MYELIN, N_AXOPLASM, N_ECF,
    N_LAYERS_HEALTHY, WAVELENGTH_SHIFT_PER_LAYER_NM,
    HEALTHY_OPERATING_WAVELENGTH_NM, WAVEGUIDE_BANDWIDTH_NM,
    JUNCTION_LOSS_DB_TYPICAL, ALPHA_0_DB_PER_MM, INTERNODE_LENGTH_UM,
    G_PHI_PSI, PSI_AMPLITUDE, KAPPA_HEALTHY,
    BASAL_EMISSION_RATE, INFLAMMATORY_EMISSION_FACTOR_HIGH,
    HILL_K_EMISSION, HILL_N_EMISSION, HILL_K_SPECTRAL, HILL_N_SPECTRAL,
)


# ---------------------------------------------------------------------------
# Pathological parameter trajectories
# ---------------------------------------------------------------------------

def thickness_factor(t: np.ndarray, rate: float = 0.1,
                     onset: float = 5.0) -> np.ndarray:
    """Fraction of normal myelin thickness remaining: alpha(t) in [0, 1].

    Modelled as a sigmoid decay starting at *onset* with steepness *rate*.

    Parameters
    ----------
    t : array-like
        Time (arbitrary units, e.g. weeks).
    rate : float
        Logistic decay rate.
    onset : float
        Midpoint of the sigmoid (time of 50 % thickness loss).

    Returns
    -------
    alpha : ndarray
        Thickness factor in [0, 1].
    """
    return 1.0 / (1.0 + np.exp(rate * (t - onset)))


def continuity_factor(t: np.ndarray, frag_onset: float = 3.0,
                      frag_rate: float = 0.15) -> np.ndarray:
    """Fraction of internode length with intact (continuous) myelin: gamma(t).

    Fragmentation begins at *frag_onset* and increases sigmoidally.

    Parameters
    ----------
    t : array-like
        Time (arbitrary units).
    frag_onset : float
        Midpoint of fragmentation sigmoid.
    frag_rate : float
        Sigmoid steepness.

    Returns
    -------
    gamma : ndarray
        Continuity factor in [0, 1].
    """
    return 1.0 / (1.0 + np.exp(frag_rate * (t - frag_onset)))


def regularity_factor(t: np.ndarray, irreg_onset: float = 4.0,
                      irreg_rate: float = 0.12) -> np.ndarray:
    """Uniformity of remaining myelin: rho(t) in [0, 1].

    Parameters
    ----------
    t : array-like
        Time (arbitrary units).
    irreg_onset : float
        Midpoint of irregularity sigmoid.
    irreg_rate : float
        Sigmoid steepness.

    Returns
    -------
    rho : ndarray
        Regularity factor in [0, 1].
    """
    return 1.0 / (1.0 + np.exp(irreg_rate * (t - irreg_onset)))


# ---------------------------------------------------------------------------
# Waveguide-derived observables
# ---------------------------------------------------------------------------

def effective_refractive_index(alpha: np.ndarray,
                               rho: np.ndarray) -> np.ndarray:
    """Effective refractive index of pathological myelin.

    n_eff = n_ECF + alpha * rho * (n_myelin - n_ECF)
    """
    return N_ECF + alpha * rho * (N_MYELIN - N_ECF)


def operating_wavelength(alpha: np.ndarray) -> np.ndarray:
    """Predicted operating wavelength (nm) as function of thickness factor.

    Each lost layer blueshifts by 52.3 nm (Zeng et al. 2022).
    """
    layers_remaining = alpha * N_LAYERS_HEALTHY
    layers_lost = N_LAYERS_HEALTHY - layers_remaining
    return HEALTHY_OPERATING_WAVELENGTH_NM - layers_lost * WAVELENGTH_SHIFT_PER_LAYER_NM


def propagation_loss_db_per_mm(alpha: np.ndarray, gamma: np.ndarray,
                               rho: np.ndarray) -> np.ndarray:
    """Effective propagation loss (dB/mm) under pathological conditions.

    alpha_prop = alpha_0 / (alpha * gamma * rho)
                 + L_junction * (1 - gamma) / l_internode
    """
    # Avoid division by zero
    agr = np.maximum(alpha * gamma * rho, 1e-6)
    intrinsic = ALPHA_0_DB_PER_MM / agr
    # Number of fragmentation boundaries per mm
    l_int_mm = INTERNODE_LENGTH_UM / 1000.0
    n_junctions_per_mm = (1.0 - gamma) / l_int_mm
    junction_contrib = JUNCTION_LOSS_DB_TYPICAL * n_junctions_per_mm
    return intrinsic + junction_contrib


def transmission_fraction(loss_db_per_mm: np.ndarray,
                          length_mm: float = 1.0) -> np.ndarray:
    """Convert propagation loss to linear transmission fraction."""
    return 10.0 ** (-loss_db_per_mm * length_mm / 10.0)


# ---------------------------------------------------------------------------
# Coherence field dynamics
# ---------------------------------------------------------------------------

def coherence_field_ode(t: float, Lambda: float,
                        kappa_func, g: float = G_PHI_PSI,
                        psi: float = PSI_AMPLITUDE,
                        phi: float = 1.0) -> float:
    """RHS of the coherence field ODE.

    dLambda/dt = g * |Psi|^2 * Phi  -  kappa(t) * Lambda

    Parameters
    ----------
    t : float
        Time.
    Lambda : float
        Current coherence field value.
    kappa_func : callable
        kappa(t) -- time-dependent decoherence rate.
    g : float
        Matter-field coupling constant.
    psi : float
        Matter field amplitude.
    phi : float
        Information field source term.

    Returns
    -------
    dLambda_dt : float
    """
    return g * psi**2 * phi - kappa_func(t) * Lambda


def solve_coherence_field(t_span: tuple, kappa_func,
                          Lambda_0: float = 1.0,
                          t_eval: Optional[np.ndarray] = None,
                          **kwargs) -> dict:
    """Integrate the coherence-field ODE over a time interval.

    Parameters
    ----------
    t_span : (t0, t_final)
    kappa_func : callable
        kappa(t) returning decoherence rate at time t.
    Lambda_0 : float
        Initial coherence field value.
    t_eval : ndarray, optional
        Time points for output.

    Returns
    -------
    dict with keys 't', 'Lambda', 'kappa'
    """
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 500)

    sol = solve_ivp(
        fun=lambda t, y: coherence_field_ode(t, y[0], kappa_func, **kwargs),
        t_span=t_span,
        y0=[Lambda_0],
        t_eval=t_eval,
        method="RK45",
        rtol=1e-8, atol=1e-10,
    )
    return {
        "t": sol.t,
        "Lambda": sol.y[0],
        "kappa": np.array([kappa_func(ti) for ti in sol.t]),
    }


# ---------------------------------------------------------------------------
# Dose-response (Hill equation)
# ---------------------------------------------------------------------------

def hill_response(D: np.ndarray, S_base: float, S_max: float,
                  K: float, n: float) -> np.ndarray:
    """Sigmoidal dose-response: signal S as function of demyelination fraction D.

    S(D) = S_base + (S_max - S_base) * D^n / (D^n + K^n)
    """
    Dn = np.power(np.maximum(D, 0.0), n)
    Kn = K ** n
    return S_base + (S_max - S_base) * Dn / (Dn + Kn)


# ---------------------------------------------------------------------------
# Composite demyelination progression
# ---------------------------------------------------------------------------

def run_demyelination_progression(
    t_weeks: np.ndarray,
    alpha_rate: float = 0.1,
    alpha_onset: float = 5.0,
    gamma_rate: float = 0.15,
    gamma_onset: float = 3.0,
    rho_rate: float = 0.12,
    rho_onset: float = 4.0,
    length_mm: float = 1.0,
) -> dict:
    """Compute full suite of observables over a demyelination timeline.

    Parameters
    ----------
    t_weeks : ndarray
        Time axis in weeks.
    alpha_rate, alpha_onset : float
        Parameters for thickness factor sigmoid.
    gamma_rate, gamma_onset : float
        Parameters for continuity factor sigmoid.
    rho_rate, rho_onset : float
        Parameters for regularity factor sigmoid.
    length_mm : float
        Axon segment length for transmission calculation.

    Returns
    -------
    dict of ndarrays keyed by observable name.
    """
    alpha = thickness_factor(t_weeks, alpha_rate, alpha_onset)
    gamma = continuity_factor(t_weeks, gamma_onset, gamma_rate)
    rho = regularity_factor(t_weeks, rho_onset, rho_rate)

    n_eff = effective_refractive_index(alpha, rho)
    wl = operating_wavelength(alpha)
    loss = propagation_loss_db_per_mm(alpha, gamma, rho)
    trans = transmission_fraction(loss, length_mm)

    # Lateral (escaped) emission: proportional to (1 - transmission)
    lateral_emission = BASAL_EMISSION_RATE * (1.0 - trans)

    # Demyelination fraction for dose-response
    D = 1.0 - alpha

    # Hill dose-response for total emission intensity
    emission_hill = hill_response(
        D, S_base=BASAL_EMISSION_RATE,
        S_max=BASAL_EMISSION_RATE * 10.0,
        K=HILL_K_EMISSION, n=HILL_N_EMISSION,
    )

    return {
        "t": t_weeks,
        "alpha": alpha,
        "gamma": gamma,
        "rho": rho,
        "n_eff": n_eff,
        "wavelength_nm": wl,
        "loss_db_per_mm": loss,
        "transmission": trans,
        "lateral_emission": lateral_emission,
        "emission_hill": emission_hill,
        "D": D,
    }


# ---------------------------------------------------------------------------
# Standalone figure generation
# ---------------------------------------------------------------------------

def plot_demyelination_progression(results: dict,
                                   save_path: str = "../figures/demyelination_progression.png"):
    """Generate a 2x3 panel figure showing demyelination progression."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    t = results["t"]

    # Panel 1: Pathological parameters
    ax = axes[0, 0]
    ax.plot(t, results["alpha"], "b-", linewidth=2, label=r"$\alpha$ (thickness)")
    ax.plot(t, results["gamma"], "r--", linewidth=2, label=r"$\gamma$ (continuity)")
    ax.plot(t, results["rho"], "g:", linewidth=2, label=r"$\rho$ (regularity)")
    ax.set_xlabel("Time (weeks)")
    ax.set_ylabel("Factor (0 = destroyed, 1 = healthy)")
    ax.set_title("Myelin Pathological Parameters")
    ax.legend(fontsize=9)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    # Panel 2: Effective refractive index
    ax = axes[0, 1]
    ax.plot(t, results["n_eff"], "k-", linewidth=2)
    ax.axhline(y=1.44, color="b", linestyle="--", alpha=0.5, label="n_myelin = 1.44")
    ax.axhline(y=1.34, color="r", linestyle="--", alpha=0.5, label="n_ECF = 1.34")
    ax.set_xlabel("Time (weeks)")
    ax.set_ylabel("Effective Refractive Index")
    ax.set_title("Myelin Effective Refractive Index")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 3: Operating wavelength
    ax = axes[0, 2]
    ax.plot(t, results["wavelength_nm"], "m-", linewidth=2)
    ax.axhline(y=HEALTHY_OPERATING_WAVELENGTH_NM, color="g", linestyle="--",
               alpha=0.5, label=f"Healthy = {HEALTHY_OPERATING_WAVELENGTH_NM} nm")
    ax.set_xlabel("Time (weeks)")
    ax.set_ylabel("Operating Wavelength (nm)")
    ax.set_title("Spectral Blueshift with Demyelination")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 4: Propagation loss
    ax = axes[1, 0]
    ax.semilogy(t, results["loss_db_per_mm"], "r-", linewidth=2)
    ax.set_xlabel("Time (weeks)")
    ax.set_ylabel("Propagation Loss (dB/mm)")
    ax.set_title("Waveguide Propagation Loss")
    ax.grid(True, alpha=0.3)

    # Panel 5: Transmission
    ax = axes[1, 1]
    ax.plot(t, results["transmission"], "b-", linewidth=2, label="Axial transmission")
    ax.plot(t, 1.0 - results["transmission"], "r--", linewidth=2, label="Lateral escape")
    ax.set_xlabel("Time (weeks)")
    ax.set_ylabel("Fraction")
    ax.set_title("Photon Transmission vs Lateral Escape")
    ax.legend(fontsize=9)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    # Panel 6: Dose-response (Hill)
    ax = axes[1, 2]
    ax.plot(results["D"], results["emission_hill"], "k-", linewidth=2)
    ax.set_xlabel("Demyelination Fraction D")
    ax.set_ylabel("Lateral Emission (photons/s/cm$^2$)")
    ax.set_title("Dose-Response: Emission vs Demyelination")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Track 06: Demyelination Progression Model", fontsize=14, fontweight="bold")
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

    t = np.linspace(0, 20, 500)
    results = run_demyelination_progression(t)
    plot_demyelination_progression(results)

    # Also solve coherence field ODE
    # kappa increases as myelin degrades
    alpha_interp = interp1d(results["t"], results["alpha"],
                            bounds_error=False, fill_value=(1.0, 0.0))

    def kappa_dynamic(t_val):
        a = float(alpha_interp(t_val))
        # kappa increases as 1/alpha^2 when myelin thins
        return KAPPA_HEALTHY / max(a**2, 0.01)

    coh = solve_coherence_field(
        t_span=(0, 20),
        kappa_func=kappa_dynamic,
        Lambda_0=1.0,
        t_eval=t,
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(coh["t"], coh["Lambda"], "b-", linewidth=2)
    ax1.set_xlabel("Time (weeks)")
    ax1.set_ylabel(r"Coherence Field $\Lambda$")
    ax1.set_title("Coherence Field Degradation")
    ax1.grid(True, alpha=0.3)

    ax2.semilogy(coh["t"], coh["kappa"], "r-", linewidth=2)
    ax2.set_xlabel("Time (weeks)")
    ax2.set_ylabel(r"Decoherence Rate $\kappa$ (s$^{-1}$)")
    ax2.set_title("Effective Decoherence Rate")
    ax2.grid(True, alpha=0.3)

    fig.suptitle("Coherence Field Under Progressive Demyelination",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("../figures/coherence_field_degradation.png", dpi=150,
                bbox_inches="tight")
    plt.close()
    print("Saved: ../figures/coherence_field_degradation.png")

    print("\nDemyelination progression model complete.")
    print(f"  Healthy wavelength: {HEALTHY_OPERATING_WAVELENGTH_NM:.1f} nm")
    print(f"  Layers healthy: {N_LAYERS_HEALTHY}")
    print(f"  Max blueshift (full loss): {N_LAYERS_HEALTHY * WAVELENGTH_SHIFT_PER_LAYER_NM:.0f} nm")
    print(f"  Lambda at t=0:  {coh['Lambda'][0]:.4f}")
    print(f"  Lambda at t=20: {coh['Lambda'][-1]:.4f}")
