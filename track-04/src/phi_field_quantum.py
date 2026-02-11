"""
Phi-field quantum representation: mapping the M-Phi framework's
coherence field onto standard quantum optics states.

The M-Phi framework (Kruger, Feeney, Duarte 2023) describes a coherence
field Lambda = Phi that governs neural coordination. This module provides
a precise quantum-optical representation of Phi in terms of:

  1. Coherent states (Glauber): Phi ~ |alpha> (classical-like coherence)
  2. Squeezed states: Phi ~ S(xi)|alpha> (sub-classical noise)
  3. Entangled biphoton states: Phi ~ sum C_{ij} |1_i, 1_j> (quantum correlations)
  4. Mixed thermal + coherent: realistic biological scenario

The key question: what quantum state best represents Lambda, and what
observable signatures distinguish different representations?
"""

import math
import numpy as np
from scipy.linalg import expm, logm
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    HBAR, K_B, T_PHYSIOL, KBT,
    OMEGA_10, OMEGA_21,
    G_PHI_PSI, KAPPA_DECOHERENCE,
    EV_TO_J, N_CAVITY_MODES, FOCK_TRUNCATION,
)
from morse_oscillator import (
    density_matrix_coherent, density_matrix_thermal, density_matrix_fock,
    wigner_function_fock, wigner_function_coherent,
    wigner_function_squeezed, wigner_function_thermal,
)


# ---- Phi field state representations ----

class PhiFieldState:
    """Represents the Phi coherence field in a quantum optics basis.

    The M-Phi framework's Lambda/Phi field is parameterized by:
      - M: neuro-coherence function (0 to 1)
      - Psi: matter field amplitude
      - g_PhiPsi: coupling constant

    We map these to quantum optical parameters:
      - alpha: coherent state amplitude (related to M * Psi)
      - r: squeeze parameter (related to fluctuations around M)
      - n_thermal: thermal background (related to decoherence)
    """

    def __init__(self, M: float = 0.5, Psi: float = 1.0,
                 g_coupling: float = G_PHI_PSI,
                 kappa: float = KAPPA_DECOHERENCE,
                 dim: int = FOCK_TRUNCATION + 1):
        """Initialize Phi field state.

        Parameters
        ----------
        M : float
            Neuro-coherence function (0 = decoherent, 1 = fully coherent).
        Psi : float
            Matter field amplitude (dimensionless).
        g_coupling : float
            Matter-field coupling.
        kappa : float
            Decoherence rate [rad/s].
        dim : int
            Hilbert space truncation dimension.
        """
        self.M = M
        self.Psi = Psi
        self.g = g_coupling
        self.kappa = kappa
        self.dim = dim

        # Map to quantum optical parameters
        self._compute_quantum_params()

    def _compute_quantum_params(self):
        """Map M-Phi parameters to quantum optics parameters."""
        # Coherent amplitude: proportional to M * Psi
        # At M=1, the field is a coherent state with amplitude ~ Psi
        # At M=0, the field is in the vacuum or thermal state
        self.alpha = complex(self.M * self.Psi * self.g * 100.0)

        # Squeeze parameter: quantum fluctuations below vacuum level
        # Higher M -> more squeezing (sub-classical coherence)
        # r = 0 for classical coherent state, r > 0 for quantum advantage
        self.r_squeeze = self.M * 0.3  # max squeeze ~ 0.3 (modest)

        # Thermal contribution: decoherence adds thermal noise
        # n_thermal ~ kappa * T / omega (simplified)
        self.n_thermal = (1.0 - self.M) * 0.1  # noise decreases with M

    def density_matrix(self) -> np.ndarray:
        """Construct the density matrix for the Phi field state.

        The state is a displaced squeezed thermal state:
        rho = D(alpha) S(xi) rho_th S^dag(xi) D^dag(alpha)
        """
        dim = self.dim

        # Start with thermal state
        rho = density_matrix_thermal(self.n_thermal, dim)

        # Apply squeezing (in Fock basis, approximate for small r)
        if self.r_squeeze > 0.01:
            S = self._squeeze_operator(self.r_squeeze)
            rho = S @ rho @ S.conj().T

        # Apply displacement
        if abs(self.alpha) > 0.01:
            D = self._displacement_operator(self.alpha)
            rho = D @ rho @ D.conj().T

        # Normalize
        rho /= np.trace(rho)
        return rho

    def _displacement_operator(self, alpha: complex) -> np.ndarray:
        """Displacement operator D(alpha) in truncated Fock space."""
        dim = self.dim
        a = np.zeros((dim, dim), dtype=complex)
        for n in range(dim - 1):
            a[n, n + 1] = np.sqrt(n + 1)
        a_dag = a.conj().T

        # D(alpha) = exp(alpha * a^dag - alpha* * a)
        arg = alpha * a_dag - alpha.conjugate() * a
        return expm(arg)

    def _squeeze_operator(self, r: float, theta: float = 0.0) -> np.ndarray:
        """Squeeze operator S(xi) in truncated Fock space."""
        dim = self.dim
        a = np.zeros((dim, dim), dtype=complex)
        for n in range(dim - 1):
            a[n, n + 1] = np.sqrt(n + 1)
        a_dag = a.conj().T

        xi = r * np.exp(1j * theta)
        arg = 0.5 * (xi.conjugate() * a @ a - xi * a_dag @ a_dag)
        return expm(arg)

    def mean_photon_number(self) -> float:
        """<n> = Tr[n * rho]."""
        rho = self.density_matrix()
        n_op = np.diag(np.arange(self.dim, dtype=complex))
        return np.real(np.trace(n_op @ rho))

    def photon_number_variance(self) -> float:
        """Var(n) = <n^2> - <n>^2."""
        rho = self.density_matrix()
        n_op = np.diag(np.arange(self.dim, dtype=complex))
        n2_op = n_op @ n_op
        mean_n = np.real(np.trace(n_op @ rho))
        mean_n2 = np.real(np.trace(n2_op @ rho))
        return mean_n2 - mean_n**2

    def mandel_Q(self) -> float:
        """Mandel Q parameter: Q = (Var(n) - <n>) / <n>.

        Q < 0: sub-Poissonian (nonclassical)
        Q = 0: Poissonian (coherent)
        Q > 0: super-Poissonian (thermal or classical)
        """
        mean_n = self.mean_photon_number()
        if mean_n < 1e-10:
            return 0.0
        var_n = self.photon_number_variance()
        return (var_n - mean_n) / mean_n

    def purity(self) -> float:
        """Tr[rho^2]."""
        rho = self.density_matrix()
        return np.real(np.trace(rho @ rho))

    def von_neumann_entropy(self) -> float:
        """S = -Tr[rho * log2(rho)]."""
        rho = self.density_matrix()
        eigenvalues = np.real(np.linalg.eigvalsh(rho))
        eigenvalues = eigenvalues[eigenvalues > 1e-15]
        return -np.sum(eigenvalues * np.log2(eigenvalues))

    def g2_zero(self) -> float:
        """Second-order correlation at zero delay.

        g^(2)(0) = <a^dag a^dag a a> / <a^dag a>^2
                 = (<n^2> - <n>) / <n>^2
        """
        rho = self.density_matrix()
        n_op = np.diag(np.arange(self.dim, dtype=complex))
        mean_n = np.real(np.trace(n_op @ rho))
        if mean_n < 1e-10:
            return 0.0
        n2_op = n_op @ n_op
        mean_n2 = np.real(np.trace(n2_op @ rho))
        return (mean_n2 - mean_n) / mean_n**2


def phi_field_vs_coherence(M_array: np.ndarray = None) -> dict:
    """Compute Phi field properties as function of neuro-coherence M.

    Returns
    -------
    dict
        'M': coherence values,
        'mean_n': mean photon number,
        'Q': Mandel Q parameter,
        'g2_0': g^(2)(0),
        'purity': state purity,
        'entropy': von Neumann entropy.
    """
    if M_array is None:
        M_array = np.linspace(0.0, 1.0, 50)

    results = {k: np.zeros(len(M_array)) for k in
               ['mean_n', 'Q', 'g2_0', 'purity', 'entropy']}
    results['M'] = M_array

    for i, M in enumerate(M_array):
        phi = PhiFieldState(M=M, dim=8)
        results['mean_n'][i] = phi.mean_photon_number()
        results['Q'][i] = phi.mandel_Q()
        results['g2_0'][i] = phi.g2_zero()
        results['purity'][i] = phi.purity()
        results['entropy'][i] = phi.von_neumann_entropy()

    return results


def classify_quantum_state(g2_0: float, Q: float) -> str:
    """Classify a quantum state based on its correlation properties.

    Returns
    -------
    str
        Classification: 'sub-Poissonian', 'Poissonian', 'super-Poissonian',
        'thermal', 'bunched-beyond-thermal', etc.
    """
    if Q < -0.01:
        return "sub-Poissonian (nonclassical)"
    elif abs(Q) < 0.01:
        return "Poissonian (coherent-like)"
    elif Q > 0.01 and g2_0 < 1.95:
        return "super-Poissonian (classical excess noise)"
    elif abs(g2_0 - 2.0) < 0.05:
        return "thermal (chaotic light)"
    elif g2_0 > 2.05:
        return "super-thermal (bunching beyond thermal)"
    else:
        return "intermediate"


if __name__ == "__main__":
    print("=== Phi-Field Quantum Representation ===\n")

    print("--- Phi field state at different coherence levels ---")
    for M in [0.0, 0.2, 0.5, 0.8, 1.0]:
        phi = PhiFieldState(M=M, dim=8)
        q_class = classify_quantum_state(phi.g2_zero(), phi.mandel_Q())
        print(f"\nM = {M:.1f}:")
        print(f"  alpha = {phi.alpha:.4f}")
        print(f"  r_squeeze = {phi.r_squeeze:.3f}")
        print(f"  n_thermal = {phi.n_thermal:.3f}")
        print(f"  <n> = {phi.mean_photon_number():.4f}")
        print(f"  Mandel Q = {phi.mandel_Q():.4f}")
        print(f"  g^(2)(0) = {phi.g2_zero():.4f}")
        print(f"  Purity = {phi.purity():.4f}")
        print(f"  S(vN) = {phi.von_neumann_entropy():.4f} bits")
        print(f"  Classification: {q_class}")

    print("\n--- M-Phi to Quantum Optics Mapping ---")
    print("M=0 (decoherent)  -> near-vacuum with thermal noise")
    print("M=0.5 (partial)   -> displaced squeezed thermal")
    print("M=1 (coherent)    -> displaced squeezed state (near-coherent)")
    print("\nKey insight: the Phi field interpolates between thermal")
    print("(classical, incoherent) and squeezed-coherent (quantum) states.")
    print("Sub-Poissonian statistics (Q < 0) arise for high M,")
    print("providing a measurable signature of M-Phi coherence.")
