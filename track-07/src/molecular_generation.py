"""Scale 1: Molecular photon generation via the ROS cascade.

Models the biochemical chain from mitochondrial electron leakage through
lipid peroxidation to triplet carbonyl / singlet oxygen photon emission.
"""

import numpy as np
from scipy.integrate import solve_ivp
from .constants import (
    K_SOD, K_FENTON, K_LH, K_RUSSELL, K_PROP, K_O2_LIPID,
    CONC_SOD, CONC_FE2, CONC_LH, CONC_O2,
    PHI_TRIPLET, PHI_RADIATIVE_TRIPLET,
    J_LEAK_FRACTION, O2_CONSUMPTION_RATE,
)


def ros_cascade_odes(t: float, y: np.ndarray, params: dict) -> np.ndarray:
    """ROS cascade ODE system.

    State vector y = [O2.-, H2O2, OH., L., LOO., 3C*]

    Returns dy/dt.
    """
    superoxide, h2o2, oh_radical, l_radical, loo_radical, triplet = y
    p = params

    j_leak = p.get("j_leak", J_LEAK_FRACTION * O2_CONSUMPTION_RATE)
    k_sod = p.get("k_sod", K_SOD)
    sod = p.get("conc_sod", CONC_SOD)
    k_fenton = p.get("k_fenton", K_FENTON)
    fe2 = p.get("conc_fe2", CONC_FE2)
    k_lh = p.get("k_lh", K_LH)
    lh = p.get("conc_lh", CONC_LH)
    k_o2 = p.get("k_o2_lipid", K_O2_LIPID)
    o2 = p.get("conc_o2", CONC_O2)
    k_russell = p.get("k_russell", K_RUSSELL)
    k_prop = p.get("k_prop", K_PROP)
    phi_c = p.get("phi_triplet", PHI_TRIPLET)

    # Radiative + non-radiative decay of triplet carbonyl (~1e6 s^-1 total)
    k_triplet_decay = p.get("k_triplet_decay", 1e6)

    d_superoxide = j_leak - k_sod * sod * superoxide
    d_h2o2 = k_sod * sod * superoxide - k_fenton * fe2 * h2o2
    d_oh = k_fenton * fe2 * h2o2 - k_lh * oh_radical * lh
    d_l = k_lh * oh_radical * lh - k_o2 * l_radical * o2
    d_loo = k_o2 * l_radical * o2 - k_prop * loo_radical * lh - 2 * k_russell * loo_radical**2
    d_triplet = phi_c * k_russell * loo_radical**2 - k_triplet_decay * triplet

    return np.array([d_superoxide, d_h2o2, d_oh, d_l, d_loo, d_triplet])


def compute_photon_rate(triplet_conc: float, volume: float,
                        phi_rad: float = PHI_RADIATIVE_TRIPLET) -> float:
    """Photon emission rate (photons/s) from triplet carbonyl concentration.

    Args:
        triplet_conc: Steady-state [3C*] in mol/L
        volume: Emitting volume in liters
        phi_rad: Radiative quantum yield
    """
    avogadro = 6.022e23
    k_total_decay = 1e6  # s^-1
    rate = phi_rad * k_total_decay * triplet_conc * volume * avogadro
    return rate


def steady_state_ros(params: dict | None = None) -> dict:
    """Compute steady-state ROS concentrations analytically (approximate).

    Uses sequential steady-state assumption: each species equilibrates
    fast relative to downstream species.
    """
    p = params or {}
    j_leak = p.get("j_leak", J_LEAK_FRACTION * O2_CONSUMPTION_RATE)
    k_sod = p.get("k_sod", K_SOD)
    sod = p.get("conc_sod", CONC_SOD)
    k_fenton = p.get("k_fenton", K_FENTON)
    fe2 = p.get("conc_fe2", CONC_FE2)
    k_lh = p.get("k_lh", K_LH)
    lh = p.get("conc_lh", CONC_LH)
    k_o2 = p.get("k_o2_lipid", K_O2_LIPID)
    o2 = p.get("conc_o2", CONC_O2)
    k_russell = p.get("k_russell", K_RUSSELL)
    k_prop = p.get("k_prop", K_PROP)
    phi_c = p.get("phi_triplet", PHI_TRIPLET)
    k_triplet_decay = p.get("k_triplet_decay", 1e6)

    # Sequential steady state
    ss_superoxide = j_leak / (k_sod * sod)
    ss_h2o2 = k_sod * sod * ss_superoxide / (k_fenton * fe2)
    ss_oh = k_fenton * fe2 * ss_h2o2 / (k_lh * lh)
    ss_l = k_lh * ss_oh * lh / (k_o2 * o2)

    # LOO. from quadratic: k_o2*[L]*[O2] = k_prop*[LOO]*[LH] + 2*k_russell*[LOO]^2
    # Approximate: if Russell term dominates at high [LOO.]
    source_loo = k_o2 * ss_l * o2
    # Solve 2*k_russell*x^2 + k_prop*lh*x - source = 0
    a = 2 * k_russell
    b = k_prop * lh
    c_term = -source_loo
    ss_loo = (-b + np.sqrt(b**2 - 4 * a * c_term)) / (2 * a)

    ss_triplet = phi_c * k_russell * ss_loo**2 / k_triplet_decay

    return {
        "superoxide": ss_superoxide,
        "h2o2": ss_h2o2,
        "oh_radical": ss_oh,
        "l_radical": ss_l,
        "loo_radical": ss_loo,
        "triplet_carbonyl": ss_triplet,
    }


def simulate_ros_cascade(t_span: tuple = (0, 1e-3), n_points: int = 1000,
                         params: dict | None = None) -> dict:
    """Run the full ROS cascade ODE simulation.

    Args:
        t_span: (t_start, t_end) in seconds
        n_points: Number of output time points
        params: Override default rate constants

    Returns:
        Dict with 't', 'y' (state array), 'species_names', 'photon_rate'
    """
    p = params or {}
    y0 = np.array([1e-12, 1e-9, 1e-15, 1e-15, 1e-12, 1e-18])
    t_eval = np.linspace(t_span[0], t_span[1], n_points)

    sol = solve_ivp(ros_cascade_odes, t_span, y0, t_eval=t_eval,
                    args=(p,), method="LSODA", rtol=1e-8, atol=1e-15)

    species = ["superoxide", "h2o2", "oh_radical", "l_radical",
               "loo_radical", "triplet_carbonyl"]

    # Photon rate from triplet concentration over time
    volume = 1e-12  # 1 pL emitting volume (single axon segment)
    photon_rates = np.array([compute_photon_rate(tc, volume) for tc in sol.y[5]])

    return {
        "t": sol.t,
        "y": sol.y,
        "species_names": species,
        "photon_rate": photon_rates,
        "success": sol.success,
    }
