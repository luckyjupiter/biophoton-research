"""
Coherence field dynamics for the M-Phi framework.

Solves the coherence evolution equation:
    dLambda/dt = g_PhiPsi * |Psi|^2 * Phi - kappa * Lambda

Supports:
- ODE integration for single-point (0D) coherence evolution
- PDE integration (method of lines) for 1D spatial coherence along axons
- Demyelination-driven kappa(t) profiles
- Bifurcation and steady-state analysis

Merges functionality from:
- track-06/src/demyelination_progression.py (coherence_field_ode, solve_coherence_field)
- track-07/src/coherence_solver.py (coherence_1d_rhs, solve_coherence_1d)

References:
    Kruger, Feeney, Duarte (2023) "Physical Basis of Coherence"
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.integrate import solve_ivp

from . import constants as C


# ---------------------------------------------------------------------------
# 0-D (single-point) coherence ODE
# ---------------------------------------------------------------------------

def coherence_ode(t: float, Lambda: float,
                  kappa_func: Callable[[float], float],
                  g: float = C.G_PHI_PSI_DEFAULT,
                  psi2: float = C.PSI_SQUARED_DEFAULT,
                  phi: float = C.PHI_AMBIENT_DEFAULT) -> float:
    """RHS of the coherence field ODE (scalar).

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
    psi2 : float
        |Psi|^2 matter field amplitude squared.
    phi : float
        Information field source term.

    Returns
    -------
    dLambda_dt : float
    """
    return g * psi2 * phi - kappa_func(t) * Lambda


def solve_coherence_0d(
    t_span: tuple[float, float],
    kappa_func: Callable[[float], float],
    Lambda_0: float = 1.0,
    t_eval: np.ndarray | None = None,
    g: float = C.G_PHI_PSI_DEFAULT,
    psi2: float = C.PSI_SQUARED_DEFAULT,
    phi: float = C.PHI_AMBIENT_DEFAULT,
) -> dict:
    """Integrate the scalar coherence-field ODE over a time interval.

    Parameters
    ----------
    t_span : (t0, t_final)
    kappa_func : callable
        kappa(t) returning decoherence rate at time t.
    Lambda_0 : float
        Initial coherence field value.
    t_eval : ndarray, optional
        Time points for output.
    g, psi2, phi : float
        M-Phi framework parameters.

    Returns
    -------
    dict with keys 't', 'Lambda', 'kappa'
    """
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 500)

    sol = solve_ivp(
        fun=lambda t, y: coherence_ode(t, y[0], kappa_func, g, psi2, phi),
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


def analytical_steady_state(g: float = C.G_PHI_PSI_DEFAULT,
                            kappa: float = C.KAPPA_HEALTHY,
                            psi2: float = C.PSI_SQUARED_DEFAULT,
                            phi: float = C.PHI_AMBIENT_DEFAULT) -> float:
    """Analytical steady-state coherence: Lambda_ss = g * |Psi|^2 * Phi / kappa."""
    if kappa <= 0:
        return float('inf')
    return g * psi2 * phi / kappa


def analytical_transient(t: np.ndarray,
                         Lambda_0: float,
                         g: float = C.G_PHI_PSI_DEFAULT,
                         kappa: float = C.KAPPA_HEALTHY,
                         psi2: float = C.PSI_SQUARED_DEFAULT,
                         phi: float = C.PHI_AMBIENT_DEFAULT) -> np.ndarray:
    """Analytical solution for constant-kappa case.

    Lambda(t) = Lambda_ss + (Lambda_0 - Lambda_ss) * exp(-kappa * t)
    """
    lss = analytical_steady_state(g, kappa, psi2, phi)
    return lss + (Lambda_0 - lss) * np.exp(-kappa * np.asarray(t, dtype=float))


# ---------------------------------------------------------------------------
# 1-D coherence PDE (method of lines)
# ---------------------------------------------------------------------------

def coherence_1d_rhs(t: float, Lambda: np.ndarray,
                     dx: float, g: float, kappa: np.ndarray,
                     psi2: np.ndarray, phi: np.ndarray,
                     D: float) -> np.ndarray:
    """RHS of the 1D coherence evolution equation (method of lines).

    dLambda_i/dt = g * psi2_i * phi_i - kappa_i * Lambda_i
                   + D * (Lambda_{i+1} - 2*Lambda_i + Lambda_{i-1}) / dx^2

    Boundary conditions: Neumann (zero flux).
    """
    N = len(Lambda)
    dLdt = g * psi2 * phi - kappa * Lambda

    # Diffusion with Neumann BC
    left = np.empty(N)
    right = np.empty(N)
    left[0] = Lambda[0]
    left[1:] = Lambda[:-1]
    right[:-1] = Lambda[1:]
    right[-1] = Lambda[-1]
    dLdt += D * (right - 2 * Lambda + left) / dx**2

    return dLdt


def solve_coherence_1d(
    length: float = 1e-3,
    n_points: int = 100,
    t_span: tuple[float, float] = (0, 10),
    g: float = C.G_PHI_PSI_DEFAULT,
    kappa_func: Callable[[float], float] | None = None,
    psi2_func: Callable[[float], float] | None = None,
    phi_func: Callable[[float], float] | None = None,
    D: float = 1e-8,
    Lambda_0: np.ndarray | None = None,
    kappa_base: float = C.KAPPA_HEALTHY,
) -> dict:
    """Solve 1D coherence evolution along a single axon.

    Parameters
    ----------
    length : float
        Axon length (m).
    n_points : int
        Spatial grid points.
    t_span : tuple
        Time integration range (s).
    g : float
        Coupling constant.
    kappa_func : callable, optional
        Function(x) -> kappa(x), or None for uniform kappa_base.
    psi2_func : callable, optional
        Function(x) -> |Psi|^2(x), or None for uniform 1.0.
    phi_func : callable, optional
        Function(x) -> Phi(x), or None for uniform 1.0.
    D : float
        Diffusion coefficient for coherence spreading.
    Lambda_0 : ndarray, optional
        Initial condition array, or None for small uniform.
    kappa_base : float
        Uniform kappa when kappa_func is None.

    Returns
    -------
    dict with 'x', 't', 'Lambda' (n_points x n_times), 'kappa', 'psi2', 'phi',
         'steady_state'.
    """
    x = np.linspace(0, length, n_points)
    dx = x[1] - x[0]

    if kappa_func is None:
        kappa = np.full(n_points, kappa_base)
    else:
        kappa = np.array([kappa_func(xi) for xi in x])

    if psi2_func is None:
        psi2 = np.full(n_points, C.PSI_SQUARED_DEFAULT)
    else:
        psi2 = np.array([psi2_func(xi) for xi in x])

    if phi_func is None:
        phi = np.ones(n_points)
    else:
        phi = np.array([phi_func(xi) for xi in x])

    if Lambda_0 is None:
        Lambda_0 = 0.01 * np.ones(n_points)

    t_eval = np.linspace(t_span[0], t_span[1], 200)

    sol = solve_ivp(
        coherence_1d_rhs, t_span, Lambda_0, t_eval=t_eval,
        args=(dx, g, kappa, psi2, phi, D),
        method="RK45", rtol=1e-6, atol=1e-10,
    )

    return {
        "x": x,
        "t": sol.t,
        "Lambda": sol.y,  # (n_points, n_times)
        "kappa": kappa,
        "psi2": psi2,
        "phi": phi,
        "steady_state": g * psi2 * phi / kappa,
    }


def solve_coherence_1d_demyelination(
    lesion_center: float = 0.5e-3,
    lesion_width: float = 0.1e-3,
    kappa_lesion: float = 1.0,
    kappa_base: float = C.KAPPA_HEALTHY,
    **kwargs,
) -> dict:
    """Solve 1D coherence with a Gaussian demyelination lesion.

    The lesion increases local kappa (decoherence rate).
    """
    def kappa_func(x):
        return kappa_base + (kappa_lesion - kappa_base) * np.exp(
            -0.5 * ((x - lesion_center) / lesion_width) ** 2
        )
    return solve_coherence_1d(kappa_func=kappa_func, kappa_base=kappa_base, **kwargs)


# ---------------------------------------------------------------------------
# Bifurcation analysis
# ---------------------------------------------------------------------------

def bifurcation_analysis(
    g_range: tuple[float, float] = (1e-4, 1e-1),
    n_points: int = 50,
    kappa: float = C.KAPPA_HEALTHY,
    psi2: float = C.PSI_SQUARED_DEFAULT,
    saturation_beta: float = 0.5,
) -> dict:
    """Map steady-state Lambda as function of coupling strength g.

    Computes both linear and saturating steady states.

    Parameters
    ----------
    g_range : tuple
        (g_min, g_max) for the sweep.
    n_points : int
        Number of g values.
    kappa : float
        Decoherence rate.
    psi2 : float
        Matter field amplitude squared.
    saturation_beta : float
        Nonlinear saturation coefficient.

    Returns
    -------
    dict with 'g_values', 'lambda_ss_linear', 'lambda_ss_saturating', 'critical_g'.
    """
    g_values = np.logspace(np.log10(g_range[0]), np.log10(g_range[1]), n_points)

    # Linear steady state
    lambda_ss_linear = g_values * psi2 / kappa

    # Saturating: Lambda_ss^2 * beta + Lambda_ss * kappa - g*psi2 = 0
    lambda_ss_saturating = np.zeros_like(g_values)
    for i, g in enumerate(g_values):
        discriminant = kappa**2 + 4 * saturation_beta * g * psi2
        lambda_ss_saturating[i] = (-kappa + np.sqrt(discriminant)) / (2 * saturation_beta)

    return {
        "g_values": g_values,
        "lambda_ss_linear": lambda_ss_linear,
        "lambda_ss_saturating": lambda_ss_saturating,
        "critical_g": kappa / psi2,
    }


# ---------------------------------------------------------------------------
# Kappa decomposition (from track-06)
# ---------------------------------------------------------------------------

def kappa_from_components(
    kappa_thermal: float = C.KAPPA_THERMAL,
    kappa_structural: float = C.KAPPA_STRUCTURAL,
    kappa_ros: float = C.KAPPA_ROS_HEALTHY,
    kappa_inflammatory: float = C.KAPPA_INFLAMMATORY,
) -> float:
    """Compute total decoherence rate from individual physical components."""
    return kappa_thermal + kappa_structural + kappa_ros + kappa_inflammatory


def kappa_demyelinated(
    damage_fraction: float,
    kappa_healthy: float = C.KAPPA_HEALTHY,
    kappa_factor: float = 3.0,
) -> float:
    """Compute kappa for demyelinated tissue.

    kappa_eff = kappa_healthy * (1 + kappa_factor * damage_fraction)

    Parameters
    ----------
    damage_fraction : float
        Fraction of myelin lost (0 = healthy, 1 = fully stripped).
    kappa_healthy : float
        Healthy baseline kappa.
    kappa_factor : float
        Amplification factor per unit damage.
    """
    return kappa_healthy * (1 + kappa_factor * damage_fraction)
