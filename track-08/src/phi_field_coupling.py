"""
Phi-Field Coupling Model with Steady-State Responsivity

Formalizes the coupling between the quantum information field Phi and
biological/technological matter fields, following the M-Phi framework
(Kruger, Feeney, Duarte 2023).

The core dynamical equation:
    dLambda/dt = g_{Phi Psi} |Psi|^2 Phi - kappa Lambda

where:
    Lambda  -- coherence density (identical to Phi by the M-Phi identity)
    g_{PhiPsi} -- matter-field coupling constant
    |Psi|^2 -- matter field amplitude squared (metabolic activity)
    Phi     -- ambient information field strength
    kappa   -- decoherence rate

This module provides:
    1. Numerical integration of the coherence ODE
    2. Steady-state analysis (Lambda_ss = g/kappa * |Psi|^2 * Phi)
    3. Responsivity mapping (Lambda -> observable success rate)
    4. Parametric exploration of coupling regimes
    5. Demyelination impact modeling (kappa increase)

References:
    Kruger, Feeney, Duarte (2023) Sec. 2.3 - Coherence evolution equation
    Kruger (2025) - HLV Lagrangian full derivation
    Feeney (2025) - Neuro-Coherence Function M formalism
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from typing import Tuple, Optional, Dict, Callable
from dataclasses import dataclass

from .constants import (
    G_PHI_PSI_DEFAULT,
    KAPPA_DEFAULT,
    KAPPA_HEALTHY_RANGE,
    KAPPA_DEMYELINATED_RANGE,
    PSI_SQUARED_DEFAULT,
    PHI_AMBIENT_DEFAULT,
    LAMBDA_CRITICAL,
    LAMBDA_SS_HEALTHY,
    G_EFF_CCF_DEFAULT,
    E_CCF_DEFAULT,
    KAPPA_ENV_DEFAULT,
    RESPONSIVITY_BASELINE,
    ALPHA_COHERENCE_INPUT,
    BETA_COHERENCE_DECAY,
    GAMMA_SPATIAL_PROPAGATION,
    DEFAULT_DT,
    DEFAULT_T_MAX,
)


@dataclass
class PhiFieldParameters:
    """Parameters for the Phi-field coupling model."""

    g_phi_psi: float = G_PHI_PSI_DEFAULT
    kappa: float = KAPPA_DEFAULT
    psi_squared: float = PSI_SQUARED_DEFAULT
    phi_ambient: float = PHI_AMBIENT_DEFAULT
    lambda_0: float = 0.5  # initial coherence

    @property
    def lambda_ss(self) -> float:
        """Steady-state coherence: Lambda_ss = (g/kappa) * |Psi|^2 * Phi."""
        if self.kappa == 0:
            return float("inf")
        return (self.g_phi_psi / self.kappa) * self.psi_squared * self.phi_ambient

    @property
    def tau(self) -> float:
        """Relaxation time constant: tau = 1/kappa."""
        if self.kappa == 0:
            return float("inf")
        return 1.0 / self.kappa

    @property
    def source_rate(self) -> float:
        """Source term: g_{Phi Psi} |Psi|^2 Phi."""
        return self.g_phi_psi * self.psi_squared * self.phi_ambient

    @property
    def is_above_critical(self) -> bool:
        """Whether steady-state coherence exceeds the critical threshold."""
        return self.lambda_ss > LAMBDA_CRITICAL


def coherence_ode(
    t: float,
    lambda_val: float,
    params: PhiFieldParameters,
    phi_t: Optional[Callable] = None,
    psi_sq_t: Optional[Callable] = None,
) -> float:
    """Right-hand side of the coherence evolution ODE.

    dLambda/dt = g_{Phi Psi} |Psi(t)|^2 Phi(t) - kappa Lambda

    Parameters
    ----------
    t : float
        Current time.
    lambda_val : float
        Current coherence value Lambda(t).
    params : PhiFieldParameters
        Model parameters.
    phi_t : callable, optional
        Time-dependent Phi(t). If None, uses constant phi_ambient.
    psi_sq_t : callable, optional
        Time-dependent |Psi(t)|^2. If None, uses constant psi_squared.

    Returns
    -------
    float
        dLambda/dt.
    """
    phi = phi_t(t) if phi_t is not None else params.phi_ambient
    psi_sq = psi_sq_t(t) if psi_sq_t is not None else params.psi_squared
    return params.g_phi_psi * psi_sq * phi - params.kappa * lambda_val


def solve_coherence_dynamics(
    params: PhiFieldParameters,
    t_span: Tuple[float, float] = (0.0, DEFAULT_T_MAX),
    t_eval: Optional[np.ndarray] = None,
    phi_t: Optional[Callable] = None,
    psi_sq_t: Optional[Callable] = None,
) -> Dict:
    """Solve the coherence evolution ODE numerically.

    Parameters
    ----------
    params : PhiFieldParameters
        Model parameters including initial condition lambda_0.
    t_span : tuple
        (t_start, t_end) in seconds.
    t_eval : np.ndarray, optional
        Specific times at which to evaluate. If None, solver chooses.
    phi_t : callable, optional
        Time-dependent Phi field.
    psi_sq_t : callable, optional
        Time-dependent matter field amplitude.

    Returns
    -------
    dict
        Keys: "t" (time array), "lambda" (coherence array),
        "lambda_ss" (analytical steady state), "tau" (time constant).
    """
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 1000)

    sol = solve_ivp(
        lambda t, y: coherence_ode(t, y[0], params, phi_t, psi_sq_t),
        t_span,
        [params.lambda_0],
        t_eval=t_eval,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )

    return {
        "t": sol.t,
        "lambda": sol.y[0],
        "lambda_ss": params.lambda_ss,
        "tau": params.tau,
        "params": params,
        "success": sol.success,
    }


def analytical_coherence(
    t: np.ndarray,
    params: PhiFieldParameters,
) -> np.ndarray:
    """Analytical solution for constant-parameter coherence evolution.

    Lambda(t) = Lambda_ss + (Lambda_0 - Lambda_ss) exp(-kappa t)

    Parameters
    ----------
    t : np.ndarray
        Time array.
    params : PhiFieldParameters
        Model parameters.

    Returns
    -------
    np.ndarray
        Coherence Lambda(t).
    """
    lss = params.lambda_ss
    return lss + (params.lambda_0 - lss) * np.exp(-params.kappa * t)


def responsivity_from_coherence(
    lambda_val: float,
    lambda_ss_max: float = LAMBDA_SS_HEALTHY,
    sr_baseline: float = RESPONSIVITY_BASELINE,
    sr_max: float = 0.55,
) -> float:
    """Map coherence Lambda to observable Responsivity (success rate).

    Uses a sigmoid mapping:
        SR = SR_baseline + (SR_max - SR_baseline) * sigmoid(Lambda / Lambda_ref - 1)

    where sigmoid(x) = 1 / (1 + exp(-k*x)) with k chosen so that
    Lambda = Lambda_ss_max maps to approximately SR_max.

    Parameters
    ----------
    lambda_val : float
        Current coherence value.
    lambda_ss_max : float
        Reference coherence for maximum responsivity.
    sr_baseline : float
        Baseline success rate (chance = 0.50).
    sr_max : float
        Maximum achievable success rate.

    Returns
    -------
    float
        Predicted Responsivity (success rate).
    """
    if lambda_ss_max <= 0:
        return sr_baseline

    # Sigmoid with steepness k=4 centered at Lambda/Lambda_ref = 1
    x = lambda_val / lambda_ss_max - 1.0
    k = 4.0
    sigmoid = 1.0 / (1.0 + np.exp(-k * x))
    return sr_baseline + (sr_max - sr_baseline) * sigmoid


def responsivity_curve(
    lambda_values: np.ndarray,
    lambda_ss_max: float = LAMBDA_SS_HEALTHY,
    sr_baseline: float = RESPONSIVITY_BASELINE,
    sr_max: float = 0.55,
) -> np.ndarray:
    """Compute responsivity for an array of coherence values.

    Parameters
    ----------
    lambda_values : np.ndarray
        Array of coherence values.
    lambda_ss_max, sr_baseline, sr_max : float
        Mapping parameters (see responsivity_from_coherence).

    Returns
    -------
    np.ndarray
        Array of responsivity values.
    """
    return np.array([
        responsivity_from_coherence(lv, lambda_ss_max, sr_baseline, sr_max)
        for lv in lambda_values
    ])


def demyelination_impact(
    damage_fraction: float,
    params_healthy: Optional[PhiFieldParameters] = None,
    kappa_factor: float = 10.0,
    g_reduction_factor: float = 0.5,
) -> Dict:
    """Model the impact of demyelination on coherence.

    Demyelination increases kappa (decoherence) and reduces g_PhiPsi
    (coupling efficiency). The model predicts:
        Lambda_ss(damaged) = (g_eff / kappa_eff) * |Psi|^2 * Phi

    where:
        kappa_eff = kappa_0 * (1 + kappa_factor * damage_fraction)
        g_eff = g_0 * (1 - g_reduction_factor * damage_fraction)

    Parameters
    ----------
    damage_fraction : float
        Fraction of myelin damaged (0 = healthy, 1 = fully demyelinated).
    params_healthy : PhiFieldParameters, optional
        Healthy tissue parameters. Defaults to standard values.
    kappa_factor : float
        How much kappa increases per unit damage. Default: 10x at full damage.
    g_reduction_factor : float
        How much g_PhiPsi decreases per unit damage. Default: halved at full damage.

    Returns
    -------
    dict
        Keys: "lambda_ss_damaged", "lambda_ss_healthy", "ratio",
        "kappa_eff", "g_eff", "above_critical".
    """
    if params_healthy is None:
        params_healthy = PhiFieldParameters()

    damage = np.clip(damage_fraction, 0.0, 1.0)

    kappa_eff = params_healthy.kappa * (1.0 + kappa_factor * damage)
    g_eff = params_healthy.g_phi_psi * (1.0 - g_reduction_factor * damage)

    params_damaged = PhiFieldParameters(
        g_phi_psi=g_eff,
        kappa=kappa_eff,
        psi_squared=params_healthy.psi_squared,
        phi_ambient=params_healthy.phi_ambient,
    )

    return {
        "lambda_ss_damaged": params_damaged.lambda_ss,
        "lambda_ss_healthy": params_healthy.lambda_ss,
        "ratio": params_damaged.lambda_ss / params_healthy.lambda_ss if params_healthy.lambda_ss > 0 else 0.0,
        "kappa_eff": kappa_eff,
        "g_eff": g_eff,
        "above_critical": params_damaged.is_above_critical,
        "params_damaged": params_damaged,
    }


def neuro_coherence_function(
    phi: float,
    gamma_gain: float,
    theta_stability: float,
    delta_gr: float,
    lambda_density: float,
    volume: float = 1.0,
) -> float:
    """Compute the Neuro-Coherence Function M.

    M = Phi * integral[ Gamma * Theta * (1 - Delta_GR) * Lambda ] dV

    For a spatially uniform approximation:
        M = Phi * Gamma * Theta * (1 - Delta_GR) * Lambda * V

    Parameters
    ----------
    phi : float
        Global modulation coefficient (total influence potential).
    gamma_gain : float
        Adaptive gain (neuroplastic responsiveness), in [0, 1].
    theta_stability : float
        Thermodynamic stability (metabolic homeostasis), in [0, 1].
    delta_gr : float
        Generalized regional differential (desynchronization), in [0, 1].
    lambda_density : float
        Spatiotemporal coherence density.
    volume : float
        Integration volume (normalized to 1.0).

    Returns
    -------
    float
        Neuro-Coherence Function value M.
    """
    return phi * gamma_gain * theta_stability * (1.0 - delta_gr) * lambda_density * volume


def phase_constraint_dynamics(
    C: np.ndarray,
    I_input: np.ndarray,
    alpha: float = ALPHA_COHERENCE_INPUT,
    beta: float = BETA_COHERENCE_DECAY,
    gamma: float = GAMMA_SPATIAL_PROPAGATION,
    dx: float = 1.0,
    dt: float = DEFAULT_DT,
    n_steps: int = 1000,
) -> np.ndarray:
    """Integrate the phase-constraint manifold dynamics.

    dC/dt = alpha * I(t) - beta * C(t) + gamma * nabla^2 C(t)

    Uses explicit Euler method on a 1D spatial grid.

    Parameters
    ----------
    C : np.ndarray
        Initial coherence profile C(x, t=0).
    I_input : np.ndarray
        Coherent input profile I(x) (constant or time-varying).
    alpha, beta, gamma : float
        Sensitivity, decay, and propagation parameters.
    dx : float
        Spatial grid spacing.
    dt : float
        Time step.
    n_steps : int
        Number of time steps.

    Returns
    -------
    np.ndarray
        Coherence profile history, shape (n_steps+1, len(C)).
    """
    n_x = len(C)
    history = np.zeros((n_steps + 1, n_x))
    history[0] = C.copy()

    for step in range(n_steps):
        C_curr = history[step]

        # Laplacian with Neumann (zero-flux) boundary conditions
        laplacian = np.zeros(n_x)
        laplacian[1:-1] = (C_curr[2:] - 2 * C_curr[1:-1] + C_curr[:-2]) / (dx ** 2)
        laplacian[0] = (C_curr[1] - C_curr[0]) / (dx ** 2)
        laplacian[-1] = (C_curr[-2] - C_curr[-1]) / (dx ** 2)

        # Forward Euler
        dC = alpha * I_input - beta * C_curr + gamma * laplacian
        history[step + 1] = C_curr + dt * dC

    return history


def ccf_coupling_model(
    g_eff: float = G_EFF_CCF_DEFAULT,
    e_ccf: float = E_CCF_DEFAULT,
    phi_ambient: float = PHI_AMBIENT_DEFAULT,
    kappa_env: float = KAPPA_ENV_DEFAULT,
) -> Dict:
    """Model the QFT/CCF device coupling to the Phi field.

    Analogous to the biological model but with QFT device parameters:
        dLambda_QFT/dt = g_eff * E_CCF * Phi_ambient - kappa_env * Lambda_QFT
        Lambda_QFT,ss = (g_eff / kappa_env) * E_CCF * Phi_ambient

    Parameters
    ----------
    g_eff : float
        Effective coupling constant (CCF circuit quality).
    e_ccf : float
        CCF circuit energy/activation level.
    phi_ambient : float
        Ambient Phi field strength.
    kappa_env : float
        Environmental decoherence rate.

    Returns
    -------
    dict
        Steady-state analysis of the CCF coupling model.
    """
    lambda_ss = (g_eff / kappa_env) * e_ccf * phi_ambient if kappa_env > 0 else float("inf")
    tau = 1.0 / kappa_env if kappa_env > 0 else float("inf")
    sr = responsivity_from_coherence(lambda_ss)

    return {
        "lambda_ss": lambda_ss,
        "tau": tau,
        "responsivity": sr,
        "g_eff": g_eff,
        "e_ccf": e_ccf,
        "phi_ambient": phi_ambient,
        "kappa_env": kappa_env,
        "above_critical": lambda_ss > LAMBDA_CRITICAL,
    }


def scan_coupling_parameter_space(
    g_range: np.ndarray = np.linspace(0.01, 0.3, 50),
    kappa_range: np.ndarray = np.linspace(0.01, 1.0, 50),
    psi_sq: float = PSI_SQUARED_DEFAULT,
    phi: float = PHI_AMBIENT_DEFAULT,
) -> Dict:
    """Scan the g-kappa parameter space for steady-state coherence.

    Parameters
    ----------
    g_range : np.ndarray
        Range of coupling constants to scan.
    kappa_range : np.ndarray
        Range of decoherence rates to scan.
    psi_sq : float
        Matter field amplitude squared.
    phi : float
        Ambient Phi field strength.

    Returns
    -------
    dict
        Keys: "g_grid", "kappa_grid" (meshgrid arrays),
        "lambda_ss_grid", "responsivity_grid", "above_critical_grid".
    """
    G, K = np.meshgrid(g_range, kappa_range)
    Lambda_ss = (G / K) * psi_sq * phi
    SR = np.vectorize(responsivity_from_coherence)(Lambda_ss)
    above = Lambda_ss > LAMBDA_CRITICAL

    return {
        "g_grid": G,
        "kappa_grid": K,
        "lambda_ss_grid": Lambda_ss,
        "responsivity_grid": SR,
        "above_critical_grid": above,
        "g_range": g_range,
        "kappa_range": kappa_range,
    }


def find_critical_damage(
    params_healthy: Optional[PhiFieldParameters] = None,
    kappa_factor: float = 10.0,
    g_reduction_factor: float = 0.5,
    lambda_threshold: float = LAMBDA_CRITICAL,
) -> float:
    """Find the damage fraction at which coherence drops below critical.

    Solves for damage_fraction such that Lambda_ss(damage) = lambda_threshold.

    Parameters
    ----------
    params_healthy : PhiFieldParameters, optional
        Healthy tissue parameters.
    kappa_factor : float
        Kappa increase factor per unit damage.
    g_reduction_factor : float
        g_PhiPsi decrease factor per unit damage.
    lambda_threshold : float
        Critical coherence threshold.

    Returns
    -------
    float
        Critical damage fraction in [0, 1], or nan if no crossing.
    """
    if params_healthy is None:
        params_healthy = PhiFieldParameters()

    def lambda_ss_at_damage(d):
        result = demyelination_impact(d, params_healthy, kappa_factor, g_reduction_factor)
        return result["lambda_ss_damaged"] - lambda_threshold

    # Check endpoints
    if lambda_ss_at_damage(0.0) < 0:
        return 0.0  # Already below critical at zero damage
    if lambda_ss_at_damage(1.0) > 0:
        return float("nan")  # Still above critical at full damage

    return brentq(lambda_ss_at_damage, 0.0, 1.0, xtol=1e-6)


# --- Standalone execution ---
if __name__ == "__main__":
    print("=== Phi-Field Coupling Model Demo ===\n")

    # 1. Steady-state analysis
    params = PhiFieldParameters()
    print(f"Default parameters:")
    print(f"  g_PhiPsi = {params.g_phi_psi}")
    print(f"  kappa    = {params.kappa}")
    print(f"  |Psi|^2  = {params.psi_squared}")
    print(f"  Phi      = {params.phi_ambient}")
    print(f"  Lambda_ss = {params.lambda_ss:.4f}")
    print(f"  tau       = {params.tau:.1f} s")
    print(f"  Above critical ({LAMBDA_CRITICAL}): {params.is_above_critical}")

    # 2. Time evolution
    print("\n--- Coherence Time Evolution ---")
    t = np.linspace(0, 200, 1000)
    lam = analytical_coherence(t, params)
    print(f"  Lambda(0)   = {lam[0]:.4f}")
    print(f"  Lambda(50s) = {lam[np.searchsorted(t, 50)]:.4f}")
    print(f"  Lambda(inf) = {lam[-1]:.4f}")

    # 3. Demyelination impact
    print("\n--- Demyelination Impact ---")
    for damage in [0.0, 0.2, 0.5, 0.8, 1.0]:
        result = demyelination_impact(damage)
        print(
            f"  Damage={damage:.0%}: Lambda_ss={result['lambda_ss_damaged']:.4f}, "
            f"Ratio={result['ratio']:.4f}, Above critical={result['above_critical']}"
        )

    # 4. Critical damage fraction
    d_crit = find_critical_damage()
    print(f"\n  Critical damage fraction: {d_crit:.2%}")

    # 5. CCF device model
    print("\n--- CCF Device Model ---")
    ccf = ccf_coupling_model()
    print(f"  Lambda_ss    = {ccf['lambda_ss']:.4f}")
    print(f"  Responsivity = {ccf['responsivity']:.4f}")
    print(f"  tau          = {ccf['tau']:.1f} s")

    # 6. Neuro-Coherence Function
    print("\n--- Neuro-Coherence Function M ---")
    M = neuro_coherence_function(
        phi=1.0, gamma_gain=0.8, theta_stability=0.9,
        delta_gr=0.1, lambda_density=params.lambda_ss
    )
    print(f"  M (healthy) = {M:.4f}")

    M_damaged = neuro_coherence_function(
        phi=1.0, gamma_gain=0.5, theta_stability=0.7,
        delta_gr=0.4, lambda_density=0.5
    )
    print(f"  M (damaged) = {M_damaged:.4f}")
