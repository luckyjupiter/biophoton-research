"""
Kappa decomposition model.

The decoherence rate kappa in the M-Phi framework equation
    dLambda/dt = g * |Psi|^2 * Phi  -  kappa * Lambda
is decomposed into physical contributors:
    kappa = kappa_thermal + kappa_structural + kappa_ROS + kappa_inflammatory

Each contributor is modelled as a function of measurable biological parameters.

Usage:
    python src/kappa_decomposition.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from constants import (
    KAPPA_THERMAL, KAPPA_STRUCTURAL, KAPPA_ROS_HEALTHY, KAPPA_INFLAMMATORY,
    KAPPA_HEALTHY, G_PHI_PSI, PSI_AMPLITUDE,
)


# ---------------------------------------------------------------------------
# Temperature-dependent thermal decoherence
# ---------------------------------------------------------------------------

def kappa_thermal(T_celsius: np.ndarray, T_ref: float = 37.0,
                  kappa_ref: float = KAPPA_THERMAL) -> np.ndarray:
    """Thermal decoherence rate.

    Modelled as Arrhenius-like scaling: kappa ~ exp(E_a / k_B * (1/T_ref - 1/T)).
    For small deviations around 37 C, linear approximation is adequate.

    Parameters
    ----------
    T_celsius : ndarray
        Temperature in Celsius.
    T_ref : float
        Reference temperature (37 C).
    kappa_ref : float
        kappa_thermal at reference temperature.

    Returns
    -------
    kappa_th : ndarray
    """
    # Activation energy / k_B ~ 4000 K (typical for protein conformational dynamics)
    E_over_kB = 4000.0  # Kelvin
    T_K = T_celsius + 273.15
    T_ref_K = T_ref + 273.15
    return kappa_ref * np.exp(E_over_kB * (1.0 / T_ref_K - 1.0 / T_K))


# ---------------------------------------------------------------------------
# Structural disorder
# ---------------------------------------------------------------------------

def kappa_structural(myelin_integrity: np.ndarray,
                     kappa_base: float = KAPPA_STRUCTURAL) -> np.ndarray:
    """Structural decoherence from myelin disorder.

    Increases as 1/m^2 where m is myelin integrity (0 to 1).
    Physical basis: disordered myelin scatters coherent photons
    into incoherent modes, each scattering event destroys phase.

    Parameters
    ----------
    myelin_integrity : ndarray
        Fraction of intact myelin (1 = healthy, 0 = demyelinated).
    kappa_base : float
        Baseline structural decoherence in healthy tissue.

    Returns
    -------
    kappa_str : ndarray
    """
    m = np.maximum(myelin_integrity, 0.01)
    return kappa_base / m**2


# ---------------------------------------------------------------------------
# ROS-mediated decoherence
# ---------------------------------------------------------------------------

def kappa_ros(ros_level: np.ndarray,
              kappa_base: float = KAPPA_ROS_HEALTHY) -> np.ndarray:
    """ROS-mediated decoherence.

    Reactive oxygen species damage chromophores and disrupt the
    electronic states that support coherent photon emission.
    Linear scaling with ROS concentration.

    Parameters
    ----------
    ros_level : ndarray
        Relative ROS level (1 = basal healthy, > 1 elevated).
    kappa_base : float
        kappa_ROS at basal level.

    Returns
    -------
    kappa_r : ndarray
    """
    return kappa_base * ros_level


# ---------------------------------------------------------------------------
# Inflammatory decoherence
# ---------------------------------------------------------------------------

def kappa_inflammatory(inflammation: np.ndarray,
                       kappa_scale: float = 0.5) -> np.ndarray:
    """Inflammatory decoherence.

    Active immune infiltrates produce cytokines (TNF-alpha, IFN-gamma,
    IL-1beta) that disrupt cellular homeostasis and increase local
    temperature, osmolarity fluctuations, and mechanical stress --
    all of which degrade coherence.

    Modelled as a Hill-like activation with threshold.

    Parameters
    ----------
    inflammation : ndarray
        Inflammation level (0 = none, 1 = maximal).
    kappa_scale : float
        Maximum inflammatory contribution to kappa.

    Returns
    -------
    kappa_inf : ndarray
    """
    # Hill equation with K=0.3, n=2
    K = 0.3
    n = 2.0
    return kappa_scale * inflammation**n / (inflammation**n + K**n)


# ---------------------------------------------------------------------------
# Composite kappa
# ---------------------------------------------------------------------------

def kappa_total(T_celsius: np.ndarray,
                myelin_integrity: np.ndarray,
                ros_level: np.ndarray,
                inflammation: np.ndarray) -> dict:
    """Compute total decoherence rate and all components.

    Parameters
    ----------
    T_celsius, myelin_integrity, ros_level, inflammation : ndarray
        All must be broadcastable arrays.

    Returns
    -------
    dict with 'total', 'thermal', 'structural', 'ros', 'inflammatory'
    """
    k_th = kappa_thermal(T_celsius)
    k_str = kappa_structural(myelin_integrity)
    k_ros = kappa_ros(ros_level)
    k_inf = kappa_inflammatory(inflammation)
    k_total = k_th + k_str + k_ros + k_inf

    return {
        "total": k_total,
        "thermal": k_th,
        "structural": k_str,
        "ros": k_ros,
        "inflammatory": k_inf,
    }


def coherence_steady_state(kappa_val: np.ndarray,
                           g: float = G_PHI_PSI,
                           psi: float = PSI_AMPLITUDE,
                           phi: float = 1.0) -> np.ndarray:
    """Steady-state coherence: Lambda_ss = g * |Psi|^2 * Phi / kappa."""
    return g * psi**2 * phi / kappa_val


# ---------------------------------------------------------------------------
# Scenario simulations
# ---------------------------------------------------------------------------

def scenario_healthy_vs_disease():
    """Compare kappa decomposition for healthy, mild, moderate, severe demyelination."""
    scenarios = {
        "Healthy": {
            "T": 37.0, "myelin": 1.0, "ros": 1.0, "inflammation": 0.0,
        },
        "Mild (early MS)": {
            "T": 37.5, "myelin": 0.85, "ros": 2.0, "inflammation": 0.2,
        },
        "Moderate (active MS)": {
            "T": 38.0, "myelin": 0.60, "ros": 5.0, "inflammation": 0.6,
        },
        "Severe (late MS)": {
            "T": 37.2, "myelin": 0.30, "ros": 3.0, "inflammation": 0.3,
        },
        "Acute relapse": {
            "T": 38.5, "myelin": 0.50, "ros": 15.0, "inflammation": 0.9,
        },
    }

    results = {}
    for name, params in scenarios.items():
        k = kappa_total(
            T_celsius=np.array([params["T"]]),
            myelin_integrity=np.array([params["myelin"]]),
            ros_level=np.array([params["ros"]]),
            inflammation=np.array([params["inflammation"]]),
        )
        # Extract scalar values
        results[name] = {key: float(val[0]) for key, val in k.items()}
        results[name]["Lambda_ss"] = float(coherence_steady_state(k["total"])[0])

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_kappa_decomposition(save_path: str = "../figures/kappa_decomposition.png"):
    """Stacked bar chart of kappa components across disease scenarios."""
    scenarios = scenario_healthy_vs_disease()

    names = list(scenarios.keys())
    components = ["thermal", "structural", "ros", "inflammatory"]
    colors = ["#2196F3", "#FF9800", "#F44336", "#9C27B0"]
    labels = ["Thermal", "Structural disorder", "ROS", "Inflammatory"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Stacked bar chart
    x = np.arange(len(names))
    bottoms = np.zeros(len(names))

    for comp, color, label in zip(components, colors, labels):
        vals = [scenarios[n][comp] for n in names]
        ax1.bar(x, vals, bottom=bottoms, color=color, label=label, width=0.6)
        bottoms += np.array(vals)

    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=25, ha="right", fontsize=9)
    ax1.set_ylabel(r"Decoherence Rate $\kappa$ (s$^{-1}$)")
    ax1.set_title("Kappa Decomposition by Disease State")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3, axis="y")

    # Coherence field comparison
    lambda_vals = [scenarios[n]["Lambda_ss"] for n in names]
    bars = ax2.bar(x, lambda_vals, color=["green", "gold", "orange", "red", "darkred"],
                   width=0.6)
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=25, ha="right", fontsize=9)
    ax2.set_ylabel(r"Steady-state Coherence $\Lambda_{ss}$")
    ax2.set_title("Predicted Coherence Field")
    ax2.grid(True, alpha=0.3, axis="y")

    # Annotate bars with values
    for bar, val in zip(bars, lambda_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{val:.4f}", ha="center", va="bottom", fontsize=8)

    fig.suptitle("Track 06: Kappa Decomposition Model",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_kappa_sensitivity(save_path: str = "../figures/kappa_sensitivity.png"):
    """Sensitivity analysis: how each parameter affects total kappa."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Temperature sensitivity
    ax = axes[0, 0]
    T_range = np.linspace(33, 42, 100)
    k_th = kappa_thermal(T_range)
    ax.plot(T_range, k_th, "b-", linewidth=2)
    ax.axvline(x=37, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("Temperature (C)")
    ax.set_ylabel(r"$\kappa_{thermal}$ (s$^{-1}$)")
    ax.set_title("Thermal Decoherence vs Temperature")
    ax.grid(True, alpha=0.3)

    # Myelin integrity sensitivity
    ax = axes[0, 1]
    m_range = np.linspace(0.05, 1.0, 100)
    k_str = kappa_structural(m_range)
    ax.semilogy(m_range, k_str, "orange", linewidth=2)
    ax.set_xlabel("Myelin Integrity")
    ax.set_ylabel(r"$\kappa_{structural}$ (s$^{-1}$)")
    ax.set_title("Structural Decoherence vs Myelin Integrity")
    ax.grid(True, alpha=0.3)

    # ROS sensitivity
    ax = axes[1, 0]
    ros_range = np.linspace(0.5, 20.0, 100)
    k_ros_vals = kappa_ros(ros_range)
    ax.plot(ros_range, k_ros_vals, "r-", linewidth=2)
    ax.set_xlabel("ROS Level (relative to basal)")
    ax.set_ylabel(r"$\kappa_{ROS}$ (s$^{-1}$)")
    ax.set_title("ROS Decoherence vs Oxidative Stress")
    ax.grid(True, alpha=0.3)

    # Inflammation sensitivity
    ax = axes[1, 1]
    infl_range = np.linspace(0, 1, 100)
    k_inf = kappa_inflammatory(infl_range)
    ax.plot(infl_range, k_inf, "purple", linewidth=2)
    ax.set_xlabel("Inflammation Level")
    ax.set_ylabel(r"$\kappa_{inflammatory}$ (s$^{-1}$)")
    ax.set_title("Inflammatory Decoherence vs Inflammation")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Kappa Component Sensitivity Analysis",
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

    # Print scenario results
    scenarios = scenario_healthy_vs_disease()
    print("Kappa Decomposition Across Disease States:")
    print("=" * 80)
    header = f"{'Scenario':<22} {'Thermal':>8} {'Struct':>8} {'ROS':>8} {'Inflam':>8} {'Total':>8} {'Lambda':>10}"
    print(header)
    print("-" * 80)
    for name, vals in scenarios.items():
        print(f"{name:<22} {vals['thermal']:8.4f} {vals['structural']:8.4f} "
              f"{vals['ros']:8.4f} {vals['inflammatory']:8.4f} "
              f"{vals['total']:8.4f} {vals['Lambda_ss']:10.6f}")

    plot_kappa_decomposition()
    plot_kappa_sensitivity()
