"""
Network-level coherence aggregation.

Kuramoto-type phase coupling between biophotonic fields in neighboring
axons, and computation of the M-Phi neuro-coherence function.

Extracted from track-07/src/network_coherence.py to be the single
source of truth for network-level biophoton coherence modeling.

References:
    Kuramoto (1984) Chemical Oscillations, Waves, and Turbulence
    Kruger, Feeney, Duarte (2023) "Physical Basis of Coherence"
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from . import constants as C


def kuramoto_odes(t: float, phases: np.ndarray,
                  natural_freqs: np.ndarray,
                  coupling_matrix: np.ndarray,
                  K: float) -> np.ndarray:
    """Kuramoto model for phase-coupled oscillators.

    d(theta_i)/dt = omega_i + (K/N) * sum_j A_ij * sin(theta_j - theta_i)
    """
    N = len(phases)
    # Vectorized coupling computation
    sin_diff = np.sin(phases[np.newaxis, :] - phases[:, np.newaxis])
    coupling_sum = np.sum(coupling_matrix * sin_diff, axis=1)
    return natural_freqs + (K / N) * coupling_sum


def kuramoto_order_parameter(phases: np.ndarray) -> tuple[float, float]:
    """Compute Kuramoto order parameter r*exp(i*psi) = (1/N) sum exp(i*theta_j).

    Returns (r, psi) where r in [0,1] measures synchronization.
    """
    z = np.mean(np.exp(1j * phases))
    return float(np.abs(z)), float(np.angle(z))


def build_coupling_matrix(n_axons: int, topology: str = "nearest_neighbor",
                          k_neighbors: int = 6,
                          seed: int = 42) -> np.ndarray:
    """Build axon-axon coupling adjacency matrix.

    Parameters
    ----------
    n_axons : int
        Number of axons in bundle.
    topology : str
        'nearest_neighbor', 'random', or 'all_to_all'.
    k_neighbors : int
        Neighbors per axon for nearest_neighbor / random topologies.
    seed : int
        Random seed for reproducible random topology.

    Returns
    -------
    A : ndarray of shape (n_axons, n_axons)
        Symmetric adjacency matrix.
    """
    A = np.zeros((n_axons, n_axons))

    if topology == "all_to_all":
        A = np.ones((n_axons, n_axons)) - np.eye(n_axons)

    elif topology == "nearest_neighbor":
        for i in range(n_axons):
            for dk in range(1, k_neighbors // 2 + 1):
                j = (i + dk) % n_axons
                A[i, j] = 1.0
                A[j, i] = 1.0

    elif topology == "random":
        rng = np.random.default_rng(seed)
        for i in range(n_axons):
            neighbors = rng.choice(
                [j for j in range(n_axons) if j != i],
                size=min(k_neighbors, n_axons - 1),
                replace=False,
            )
            for j in neighbors:
                A[i, j] = 1.0
                A[j, i] = 1.0

    return A


def compute_m_function(lambda_field: np.ndarray, gamma: np.ndarray,
                       theta: np.ndarray, delta_gr: np.ndarray,
                       phi_global: float = 1.0) -> float:
    """Compute the M-Phi neuro-coherence function.

    M = Phi * integral( Gamma * Theta * (1 - Delta_GR) * Lambda ) dV

    For discrete axons, the integral becomes a sum.

    Parameters
    ----------
    lambda_field : ndarray (N,)
        Coherence density per axon.
    gamma : ndarray (N,)
        Adaptive gain per axon, in [0, 1].
    theta : ndarray (N,)
        Thermodynamic stability per axon, in [0, 1].
    delta_gr : ndarray (N,)
        Desynchronization measure per axon, in [0, 1].
    phi_global : float
        Global modulation coefficient.

    Returns
    -------
    M : float
        Neuro-coherence function value.
    """
    integrand = gamma * theta * (1 - delta_gr) * lambda_field
    return float(phi_global * np.sum(integrand))


def simulate_network_synchronization(
    n_axons: int = 50,
    t_span: tuple[float, float] = (0, 100),
    K: float = C.PHASE_COUPLING_K,
    topology: str = "nearest_neighbor",
    freq_spread: float = 0.1,
    seed: int = 42,
) -> dict:
    """Simulate Kuramoto phase synchronization in an axon bundle.

    Returns time series of order parameter and final phase distribution.
    """
    rng = np.random.default_rng(seed)

    omega_0 = 1.0
    natural_freqs = omega_0 + freq_spread * rng.standard_normal(n_axons)
    phases_0 = rng.uniform(0, 2 * np.pi, n_axons)
    A = build_coupling_matrix(n_axons, topology, seed=seed)

    t_eval = np.linspace(t_span[0], t_span[1], 500)
    sol = solve_ivp(
        kuramoto_odes, t_span, phases_0, t_eval=t_eval,
        args=(natural_freqs, A, K),
        method="RK45", rtol=1e-6,
    )

    r_t = np.array([kuramoto_order_parameter(sol.y[:, i])[0]
                     for i in range(len(sol.t))])

    return {
        "t": sol.t,
        "phases": sol.y,
        "order_parameter": r_t,
        "coupling_matrix": A,
        "natural_freqs": natural_freqs,
    }


def axon_coherence_from_sync(
    order_parameter: float,
    g: float = C.G_PHI_PSI_DEFAULT,
    psi2: float = C.PSI_SQUARED_DEFAULT,
    phi: float = C.PHI_AMBIENT_DEFAULT,
    kappa: float = C.KAPPA_HEALTHY,
) -> float:
    """Map network synchronization to coherence field Lambda.

    At steady state: Lambda_ss = (g * |Psi|^2 * Phi) / kappa
    Modulated by synchronization: Lambda_network = r * Lambda_ss
    where r is the Kuramoto order parameter.
    """
    lambda_ss = g * psi2 * phi / kappa
    return order_parameter * lambda_ss
