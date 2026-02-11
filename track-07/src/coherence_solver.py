"""Coherence evolution PDE solver.

Solves dLambda/dt = g_PhiPsi * |Psi|^2 * Phi - kappa * Lambda + D * d^2Lambda/dx^2

Method of lines: discretize space, solve resulting ODE system.
"""

import numpy as np
from scipy.integrate import solve_ivp
from .constants import G_PHI_PSI, KAPPA_BASE, PSI_SQUARED


def coherence_1d_rhs(t: float, Lambda: np.ndarray,
                     dx: float, g: float, kappa: np.ndarray,
                     psi2: np.ndarray, phi: np.ndarray,
                     D: float) -> np.ndarray:
    """RHS of the 1D coherence evolution equation (method of lines).

    dLambda_i/dt = g * psi2_i * phi_i - kappa_i * Lambda_i
                   + D * (Lambda_{i+1} - 2*Lambda_i + Lambda_{i-1}) / dx^2
    """
    N = len(Lambda)
    dLdt = np.zeros(N)

    # Source and decay
    dLdt = g * psi2 * phi - kappa * Lambda

    # Diffusion (Neumann BC: zero flux at boundaries)
    for i in range(N):
        left = Lambda[i - 1] if i > 0 else Lambda[i]
        right = Lambda[i + 1] if i < N - 1 else Lambda[i]
        dLdt[i] += D * (right - 2 * Lambda[i] + left) / dx**2

    return dLdt


def solve_coherence_1d(length: float = 1e-3,
                       n_points: int = 100,
                       t_span: tuple = (0, 10),
                       g: float = G_PHI_PSI,
                       kappa_func=None,
                       psi2_func=None,
                       phi_func=None,
                       D: float = 1e-8,
                       Lambda_0=None) -> dict:
    """Solve 1D coherence evolution along a single axon.

    Args:
        length: Axon length (m)
        n_points: Spatial grid points
        t_span: Time integration range (s)
        g: Coupling constant
        kappa_func: Function(x) -> kappa(x), or None for uniform
        psi2_func: Function(x) -> |Psi|^2(x), or None for uniform
        phi_func: Function(x) -> Phi(x), or None for uniform
        D: Diffusion coefficient for coherence spreading
        Lambda_0: Initial condition array, or None for small random
    """
    x = np.linspace(0, length, n_points)
    dx = x[1] - x[0]

    # Parameter fields
    if kappa_func is None:
        kappa = np.full(n_points, KAPPA_BASE)
    else:
        kappa = np.array([kappa_func(xi) for xi in x])

    if psi2_func is None:
        psi2 = np.full(n_points, PSI_SQUARED)
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
        method="RK45", rtol=1e-6, atol=1e-10
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


def solve_coherence_1d_demyelination(lesion_center: float = 0.5e-3,
                                      lesion_width: float = 0.1e-3,
                                      kappa_lesion: float = 1.0,
                                      **kwargs) -> dict:
    """Solve 1D coherence with a demyelination lesion.

    Lesion increases local kappa (decoherence rate) in a Gaussian profile.
    """
    def kappa_func(x):
        return KAPPA_BASE + (kappa_lesion - KAPPA_BASE) * np.exp(
            -0.5 * ((x - lesion_center) / lesion_width)**2
        )

    return solve_coherence_1d(kappa_func=kappa_func, **kwargs)


def bifurcation_analysis(g_range: tuple = (1e-4, 1e-1), n_points: int = 50,
                         kappa: float = KAPPA_BASE) -> dict:
    """Map steady-state Lambda as function of coupling strength g.

    Identifies regimes: subcritical (Lambda -> 0) vs supercritical (Lambda > 0).
    For the linear model, Lambda_ss = g * |Psi|^2 * Phi / kappa (always > 0),
    but with nonlinear saturation terms the behavior changes.
    """
    g_values = np.logspace(np.log10(g_range[0]), np.log10(g_range[1]), n_points)

    # Linear steady state
    lambda_ss_linear = g_values * PSI_SQUARED / kappa

    # With saturation: Lambda_ss = g*psi2*phi / (kappa + beta*Lambda_ss)
    # => Lambda_ss^2 * beta + Lambda_ss * kappa - g*psi2*phi = 0
    beta = 0.5  # saturation coefficient
    lambda_ss_saturating = np.zeros_like(g_values)
    for i, g in enumerate(g_values):
        # Quadratic: beta*x^2 + kappa*x - g*psi2 = 0
        discriminant = kappa**2 + 4 * beta * g * PSI_SQUARED
        lambda_ss_saturating[i] = (-kappa + np.sqrt(discriminant)) / (2 * beta)

    return {
        "g_values": g_values,
        "lambda_ss_linear": lambda_ss_linear,
        "lambda_ss_saturating": lambda_ss_saturating,
        "critical_g": kappa / PSI_SQUARED,  # where Lambda_ss = 1 (normalized)
    }
