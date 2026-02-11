"""
Biphoton state generation via cascade emission from Morse oscillator.

Implements the Liu-Chen-Ao model:
  |2> -> |1> + gamma_1 -> |0> + gamma_1 + gamma_2

Computes:
  - Two-photon amplitude C_{lambda1, lambda2}
  - Schmidt decomposition and entanglement entropy
  - Joint spectral intensity
  - Thickness dependence of entanglement
"""

import numpy as np
from scipy.linalg import svd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    HBAR, EPSILON_0, C_LIGHT, EV_TO_J,
    N_MYELIN, OMEGA_10, OMEGA_21, OMEGA_20,
    DIPOLE_10, DIPOLE_21,
    GAMMA_10_FREE, GAMMA_21_FREE,
    GAMMA_DEPH,
    AXON_RADIUS_TYPICAL, MYELIN_THICKNESS_TYPICAL, INTERNODE_LENGTH_TYPICAL,
)
from cavity_qed import (
    cavity_q_factor, mode_volume_cylindrical_shell,
    vacuum_rabi_coupling, cavity_decay_rate,
)


def generate_cavity_modes(a: float, d: float, L: float,
                           n_modes: int = 30,
                           omega_center: float = None,
                           omega_range: float = None) -> np.ndarray:
    """Generate a set of cavity mode frequencies.

    For a long cylindrical cavity of length L, longitudinal modes are
    spaced by Delta_omega = pi * c / (n * L). We generate modes around
    the transition frequencies.

    Parameters
    ----------
    a : float
        Axon radius [m].
    d : float
        Myelin thickness [m].
    L : float
        Internode length [m].
    n_modes : int
        Number of modes per transition.
    omega_center : float
        Center frequency [rad/s].
    omega_range : float
        Frequency range [rad/s].

    Returns
    -------
    np.ndarray
        Array of mode frequencies [rad/s].
    """
    # Free spectral range (longitudinal mode spacing)
    fsr = np.pi * C_LIGHT / (N_MYELIN * L)

    if omega_center is None:
        omega_center = (OMEGA_10 + OMEGA_21) / 2.0

    if omega_range is None:
        omega_range = abs(OMEGA_10 - OMEGA_21) * 3.0

    # Generate modes centered on omega_center
    p_min = int((omega_center - omega_range / 2) / fsr)
    p_max = int((omega_center + omega_range / 2) / fsr)

    # Select n_modes modes around center
    p_center = int(omega_center / fsr)
    p_indices = np.arange(p_center - n_modes // 2, p_center + n_modes // 2 + 1)
    p_indices = p_indices[p_indices > 0]

    return p_indices * fsr


def biphoton_amplitude(omega1: float, omega2: float,
                        g1: float, g2: float,
                        Gamma_2: float, Gamma_1: float) -> complex:
    """Two-photon amplitude for cascade emission.

    C(omega1, omega2) = g1 * g2 / [
        (omega_21 - omega1 + i*Gamma_2/2) *
        (omega_20 - omega1 - omega2 + i*(Gamma_1+Gamma_2)/2)
    ]

    Parameters
    ----------
    omega1, omega2 : float
        Photon frequencies [rad/s].
    g1, g2 : float
        Coupling constants for |2>->|1> and |1>->|0> transitions.
    Gamma_2, Gamma_1 : float
        Decay widths of levels |2> and |1>.

    Returns
    -------
    complex
        Two-photon amplitude.
    """
    denom1 = (OMEGA_21 - omega1) + 1j * Gamma_2 / 2.0
    denom2 = (OMEGA_20 - omega1 - omega2) + 1j * (Gamma_1 + Gamma_2) / 2.0
    return g1 * g2 / (denom1 * denom2)


def joint_spectral_amplitude(omega1_array: np.ndarray,
                              omega2_array: np.ndarray,
                              g1: float, g2: float,
                              Gamma_2: float, Gamma_1: float) -> np.ndarray:
    """Compute joint spectral amplitude on a 2D frequency grid.

    Parameters
    ----------
    omega1_array, omega2_array : np.ndarray
        1D arrays of mode frequencies for photon 1 and 2.
    g1, g2 : float
        Coupling constants.
    Gamma_2, Gamma_1 : float
        Decay widths.

    Returns
    -------
    np.ndarray
        2D array of amplitudes C[i, j] = C(omega1[i], omega2[j]).
    """
    N1 = len(omega1_array)
    N2 = len(omega2_array)
    C = np.zeros((N1, N2), dtype=complex)

    for i, w1 in enumerate(omega1_array):
        for j, w2 in enumerate(omega2_array):
            C[i, j] = biphoton_amplitude(w1, w2, g1, g2, Gamma_2, Gamma_1)

    return C


def schmidt_decomposition(C_matrix: np.ndarray) -> dict:
    """Perform Schmidt decomposition of the two-photon amplitude matrix.

    Parameters
    ----------
    C_matrix : np.ndarray
        Joint spectral amplitude matrix C[i, j].

    Returns
    -------
    dict
        'coefficients': Schmidt coefficients (sorted, descending),
        'entropy': entanglement entropy (log2),
        'K': Schmidt number (effective number of modes),
        'U', 'Vh': left and right Schmidt bases.
    """
    U, sigma, Vh = svd(C_matrix, full_matrices=False)

    # Normalize to get probabilities
    sigma_sq = sigma**2
    total = np.sum(sigma_sq)
    if total < 1e-30:
        return {
            'coefficients': sigma_sq,
            'entropy': 0.0,
            'K': 1.0,
            'U': U, 'Vh': Vh,
        }

    lambda_n = sigma_sq / total

    # Entanglement entropy
    mask = lambda_n > 1e-15
    S = -np.sum(lambda_n[mask] * np.log2(lambda_n[mask]))

    # Schmidt number K = 1 / sum(lambda_n^2)
    K = 1.0 / np.sum(lambda_n**2)

    return {
        'coefficients': lambda_n,
        'entropy': S,
        'K': K,
        'U': U, 'Vh': Vh,
    }


def entanglement_vs_thickness(d_array: np.ndarray,
                                a: float = AXON_RADIUS_TYPICAL,
                                L: float = INTERNODE_LENGTH_TYPICAL,
                                n_modes: int = 30,
                                alpha_abs: float = 300.0) -> dict:
    """Compute entanglement entropy as a function of myelin thickness.

    This is the central result of the Liu-Chen-Ao model.

    Parameters
    ----------
    d_array : np.ndarray
        Array of myelin thicknesses [m].
    a : float
        Axon radius [m].
    L : float
        Internode length [m].
    n_modes : int
        Number of cavity modes per photon.
    alpha_abs : float
        Absorption coefficient [m^-1].

    Returns
    -------
    dict
        'd': thickness array,
        'S': entanglement entropy array,
        'K': Schmidt number array,
        'Q_10', 'Q_21': Q factor arrays,
        'g2_0': predicted g^(2)(0) at each thickness.
    """
    N = len(d_array)
    S_arr = np.zeros(N)
    K_arr = np.zeros(N)
    Q10_arr = np.zeros(N)
    Q21_arr = np.zeros(N)
    g2_0_arr = np.zeros(N)

    for idx, d in enumerate(d_array):
        # Cavity parameters
        V = mode_volume_cylindrical_shell(a, d, L)
        Q10 = cavity_q_factor(d, OMEGA_10, alpha_abs)
        Q21 = cavity_q_factor(d, OMEGA_21, alpha_abs)
        Q10_arr[idx] = Q10
        Q21_arr[idx] = Q21

        g1 = vacuum_rabi_coupling(DIPOLE_21, OMEGA_21, V)
        g2 = vacuum_rabi_coupling(DIPOLE_10, OMEGA_10, V)

        kappa10 = cavity_decay_rate(Q10, OMEGA_10)
        kappa21 = cavity_decay_rate(Q21, OMEGA_21)

        # Effective linewidths include cavity loss + dephasing
        Gamma_2 = GAMMA_21_FREE + kappa21 + GAMMA_DEPH
        Gamma_1 = GAMMA_10_FREE + kappa10 + GAMMA_DEPH

        # Generate mode grids around each transition
        modes_1 = generate_cavity_modes(a, d, L, n_modes, OMEGA_21)
        modes_2 = generate_cavity_modes(a, d, L, n_modes, OMEGA_10)

        if len(modes_1) < 2 or len(modes_2) < 2:
            S_arr[idx] = 0.0
            K_arr[idx] = 1.0
            continue

        # Compute joint spectral amplitude
        C = joint_spectral_amplitude(modes_1, modes_2, g1, g2, Gamma_2, Gamma_1)

        # Schmidt decomposition
        result = schmidt_decomposition(C)
        S_arr[idx] = result['entropy']
        K_arr[idx] = result['K']

        # g^(2)(0) for the biphoton state
        # For a two-mode squeezed state or biphoton: g^(2)(0) > 2
        # Simple estimate based on Schmidt number
        if result['K'] > 1.0:
            g2_0_arr[idx] = 1.0 + 1.0 / result['K']
        else:
            g2_0_arr[idx] = 2.0

    return {
        'd': d_array,
        'S': S_arr,
        'K': K_arr,
        'Q_10': Q10_arr,
        'Q_21': Q21_arr,
        'g2_0': g2_0_arr,
    }


def biphoton_density_matrix(C_matrix: np.ndarray, dim: int = None) -> np.ndarray:
    """Construct the two-photon density matrix from the joint spectral amplitude.

    rho = |psi_bph><psi_bph| where |psi_bph> = sum C_{ij} |1_i, 1_j>

    For the reduced density matrix of photon 1:
    rho_1 = Tr_2[|psi><psi|] = C @ C^dag (properly normalized)

    Returns
    -------
    np.ndarray
        Reduced density matrix for photon 1.
    """
    # Normalize
    norm = np.sqrt(np.sum(np.abs(C_matrix)**2))
    if norm < 1e-30:
        if dim is None:
            dim = C_matrix.shape[0]
        return np.eye(dim) / dim

    C_norm = C_matrix / norm
    rho_1 = C_norm @ C_norm.conj().T
    return rho_1


def von_neumann_entropy(rho: np.ndarray) -> float:
    """Von Neumann entropy S = -Tr[rho * log2(rho)]."""
    eigenvalues = np.real(np.linalg.eigvalsh(rho))
    eigenvalues = eigenvalues[eigenvalues > 1e-15]
    return -np.sum(eigenvalues * np.log2(eigenvalues))


def concurrence_2qubit(rho: np.ndarray) -> float:
    """Concurrence for a two-qubit density matrix.

    C(rho) = max(0, sqrt(mu1) - sqrt(mu2) - sqrt(mu3) - sqrt(mu4))
    where mu_i are eigenvalues of rho * (sy x sy) * rho* * (sy x sy)
    in decreasing order.
    """
    if rho.shape != (4, 4):
        raise ValueError("Concurrence requires 4x4 density matrix")

    sigma_y = np.array([[0, -1j], [1j, 0]])
    sy_sy = np.kron(sigma_y, sigma_y)

    rho_tilde = sy_sy @ rho.conj() @ sy_sy
    product = rho @ rho_tilde

    eigenvalues = np.sort(np.real(np.linalg.eigvals(product)))[::-1]
    eigenvalues = np.maximum(eigenvalues, 0.0)

    sqrt_eigs = np.sqrt(eigenvalues)
    C = max(0.0, sqrt_eigs[0] - sqrt_eigs[1] - sqrt_eigs[2] - sqrt_eigs[3])
    return C


if __name__ == "__main__":
    print("=== Biphoton State Generation Model ===\n")

    a = AXON_RADIUS_TYPICAL
    d = MYELIN_THICKNESS_TYPICAL
    L = INTERNODE_LENGTH_TYPICAL

    # Compute for typical parameters
    V = mode_volume_cylindrical_shell(a, d, L)
    g1 = vacuum_rabi_coupling(DIPOLE_21, OMEGA_21, V)
    g2 = vacuum_rabi_coupling(DIPOLE_10, OMEGA_10, V)

    Q10 = cavity_q_factor(d, OMEGA_10, 300.0)
    Q21 = cavity_q_factor(d, OMEGA_21, 300.0)
    kappa10 = cavity_decay_rate(Q10, OMEGA_10)
    kappa21 = cavity_decay_rate(Q21, OMEGA_21)

    Gamma_2 = GAMMA_21_FREE + kappa21 + GAMMA_DEPH
    Gamma_1 = GAMMA_10_FREE + kappa10 + GAMMA_DEPH

    print(f"Coupling constants: g1 = {g1:.2e}, g2 = {g2:.2e} rad/s")
    print(f"Effective linewidths: Gamma_2 = {Gamma_2:.2e}, Gamma_1 = {Gamma_1:.2e} rad/s")
    print(f"Gamma dominated by dephasing ({GAMMA_DEPH:.2e} rad/s)")

    # Generate modes and compute JSA
    modes_1 = generate_cavity_modes(a, d, L, 30, OMEGA_21)
    modes_2 = generate_cavity_modes(a, d, L, 30, OMEGA_10)
    print(f"\nCavity modes: {len(modes_1)} around omega_21, {len(modes_2)} around omega_10")

    fsr = np.pi * C_LIGHT / (N_MYELIN * L)
    print(f"Free spectral range: {fsr:.2e} rad/s = {fsr/(2*np.pi)*1e-9:.2f} GHz")

    C = joint_spectral_amplitude(modes_1, modes_2, g1, g2, Gamma_2, Gamma_1)
    result = schmidt_decomposition(C)

    print(f"\n--- Schmidt Decomposition ---")
    print(f"Entanglement entropy S = {result['entropy']:.4f} bits")
    print(f"Schmidt number K = {result['K']:.2f}")
    print(f"Top 5 Schmidt coefficients: {result['coefficients'][:5]}")

    # Thickness scan
    print(f"\n--- Entanglement vs Thickness ---")
    d_scan = np.linspace(0.3e-6, 2.5e-6, 50)
    ent = entanglement_vs_thickness(d_scan, n_modes=20)

    i_max = np.argmax(ent['S'])
    print(f"Peak entropy S = {ent['S'][i_max]:.4f} bits at d = {ent['d'][i_max]*1e6:.2f} um")
    print(f"Corresponding Schmidt number K = {ent['K'][i_max]:.2f}")
