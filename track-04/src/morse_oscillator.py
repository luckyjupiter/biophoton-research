"""
Morse oscillator model for C-H bond vibrations in myelin lipids.

Provides:
  - Analytical energy levels
  - Transition dipole matrix elements (harmonic approximation for matrix elements)
  - Wigner function for quantum states
  - Anharmonicity analysis

Note: The Morse wavefunction in Laguerre polynomial form is numerically unstable
for large s (~24 for C-H). We use the harmonic oscillator wavefunctions for
matrix element evaluation, which is accurate for v << s. The key physics ---
anharmonic energy spacings --- comes from the exact Morse eigenvalues.
"""

import math
import numpy as np
from scipy.special import genlaguerre, gamma as gamma_func, eval_laguerre, hermite
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    HBAR, OMEGA_E_RAD, D_E_J, MU_CH, ALPHA_MORSE, R_EQ,
    EV_TO_J, morse_energy_level
)


def morse_parameter_s() -> float:
    """Dimensionless Morse parameter s = sqrt(2*mu*D_e) / (alpha*hbar)."""
    return np.sqrt(2.0 * MU_CH * D_E_J) / (ALPHA_MORSE * HBAR)


def max_vibrational_quantum_number() -> int:
    """Maximum bound-state quantum number v_max."""
    s = morse_parameter_s()
    return int(s - 0.5)


def harmonic_length_scale() -> float:
    """Characteristic length scale x_0 = sqrt(hbar / (mu * omega))."""
    return np.sqrt(HBAR / (MU_CH * OMEGA_E_RAD))


def transition_dipole_harmonic(v_lower: int, v_upper: int) -> float:
    """Transition dipole matrix element in harmonic approximation.

    For a harmonic oscillator, <v|x|v+1> = sqrt((v+1)/2) * x_0.
    Selection rule: Delta v = +/- 1 only (fundamental transitions).
    Overtones (|Delta v| > 1) are zero in harmonic approx; in the anharmonic
    Morse potential they are nonzero but suppressed by ~(omega_e*chi_e/omega_e)^|Dv|.

    Returns
    -------
    float
        Matrix element <v_lower|x - x_eq|v_upper> in meters.
    """
    x0 = harmonic_length_scale()
    dv = abs(v_upper - v_lower)

    if dv == 1:
        v_min = min(v_lower, v_upper)
        return x0 * np.sqrt((v_min + 1) / 2.0)
    elif dv == 2:
        # First anharmonic correction: overtone ~(chi/omega_e) * harmonic
        chi_ratio = 62.5 / 2950.0  # omega_e*chi_e / omega_e
        v_min = min(v_lower, v_upper)
        return chi_ratio * x0 * np.sqrt((v_min + 1) * (v_min + 2)) / 2.0
    else:
        return 0.0


def anharmonicity_analysis(v_max: int = 6) -> dict:
    """Compute energy levels, spacings, and anharmonic corrections."""
    s = morse_parameter_s()
    v_limit = min(v_max, max_vibrational_quantum_number())
    vs = np.arange(v_limit + 1)
    energies = np.array([morse_energy_level(v) / EV_TO_J for v in vs])

    spacings = np.diff(energies)
    harmonic_spacing = HBAR * OMEGA_E_RAD / EV_TO_J
    anharmonic_shifts = spacings - harmonic_spacing

    return {
        'v': vs,
        'E_eV': energies,
        'spacing_eV': spacings,
        'harmonic_spacing_eV': harmonic_spacing,
        'anharmonic_shift_eV': anharmonic_shifts,
        's': s,
        'v_max': int(s - 0.5),
    }


def wigner_function_fock(v: int, x_arr: np.ndarray,
                         p_arr: np.ndarray) -> np.ndarray:
    """Wigner function for Fock state |v> of harmonic oscillator.

    W_n(x,p) = (-1)^n / pi * exp(-2(x^2+p^2)) * L_n(4(x^2+p^2))

    Parameters
    ----------
    v : int
        Fock state number.
    x_arr, p_arr : np.ndarray
        Dimensionless quadratures.

    Returns
    -------
    np.ndarray
        Wigner function W(x, p).
    """
    X, P = np.meshgrid(x_arr, p_arr)
    eta = 2.0 * (X**2 + P**2)
    W = ((-1)**v / np.pi) * np.exp(-eta / 2.0) * eval_laguerre(v, eta)
    return W


def wigner_function_coherent(alpha: complex, x_arr: np.ndarray,
                              p_arr: np.ndarray) -> np.ndarray:
    """Wigner function for coherent state |alpha>.

    Gaussian centered at (Re(alpha)*sqrt(2), Im(alpha)*sqrt(2)).
    """
    X, P = np.meshgrid(x_arr, p_arr)
    x0 = np.sqrt(2) * alpha.real
    p0 = np.sqrt(2) * alpha.imag
    W = (1.0 / np.pi) * np.exp(-((X - x0)**2 + (P - p0)**2))
    return W


def wigner_function_squeezed(r_squeeze: float, theta: float,
                               x_arr: np.ndarray,
                               p_arr: np.ndarray) -> np.ndarray:
    """Wigner function for squeezed vacuum S(xi)|0>.

    Parameters
    ----------
    r_squeeze : float
        Squeeze parameter r.
    theta : float
        Squeeze angle.
    """
    X, P = np.meshgrid(x_arr, p_arr)
    ct = np.cos(theta / 2)
    st = np.sin(theta / 2)
    Xr = X * ct + P * st
    Pr = -X * st + P * ct

    W = (1.0 / np.pi) * np.exp(
        -Xr**2 * np.exp(2 * r_squeeze)
        - Pr**2 * np.exp(-2 * r_squeeze)
    )
    return W


def wigner_function_thermal(n_bar: float, x_arr: np.ndarray,
                             p_arr: np.ndarray) -> np.ndarray:
    """Wigner function for thermal state with mean photon number n_bar.

    W(x,p) = 1/(pi*(2*n_bar+1)) * exp(-(x^2+p^2)/(n_bar+1/2))
    """
    X, P = np.meshgrid(x_arr, p_arr)
    sigma2 = n_bar + 0.5
    W = (1.0 / (np.pi * 2 * sigma2)) * np.exp(-(X**2 + P**2) / (2 * sigma2))
    return W


def density_matrix_fock(v: int, dim: int = 5) -> np.ndarray:
    """Density matrix for pure Fock state |v><v|."""
    rho = np.zeros((dim, dim), dtype=complex)
    if v < dim:
        rho[v, v] = 1.0
    return rho


def density_matrix_coherent(alpha: complex, dim: int = 10) -> np.ndarray:
    """Density matrix for coherent state |alpha><alpha|."""
    coeffs = np.zeros(dim, dtype=complex)
    for n in range(dim):
        coeffs[n] = np.exp(-abs(alpha)**2 / 2) * alpha**n / np.sqrt(float(math.factorial(n)))
    rho = np.outer(coeffs, coeffs.conj())
    return rho


def density_matrix_thermal(n_bar: float, dim: int = 10) -> np.ndarray:
    """Density matrix for thermal state."""
    rho = np.zeros((dim, dim), dtype=complex)
    for n in range(dim):
        p_n = (n_bar / (1 + n_bar))**n / (1 + n_bar)
        rho[n, n] = p_n
    return rho


if __name__ == "__main__":
    print("=== Morse Oscillator Analysis ===")
    info = anharmonicity_analysis()
    print(f"Morse parameter s = {info['s']:.2f}")
    print(f"Maximum bound state v_max = {info['v_max']}")
    print(f"Harmonic length scale x_0 = {harmonic_length_scale():.4e} m")
    print(f"\nEnergy levels:")
    for v, e in zip(info['v'], info['E_eV']):
        print(f"  v={v}: E = {e:.4f} eV")
    print(f"\nTransition spacings:")
    for i, (sp, ah) in enumerate(zip(info['spacing_eV'], info['anharmonic_shift_eV'])):
        print(f"  v={i}->v={i+1}: dE = {sp:.4f} eV, shift = {ah*1000:.2f} meV")

    x0 = harmonic_length_scale()
    d_10 = transition_dipole_harmonic(0, 1)
    d_21 = transition_dipole_harmonic(1, 2)
    d_20 = transition_dipole_harmonic(0, 2)
    print(f"\nTransition dipole elements (harmonic approx):")
    print(f"  <0|x|1> = {d_10:.4e} m = {d_10/x0:.4f} x_0")
    print(f"  <1|x|2> = {d_21:.4e} m = {d_21/x0:.4f} x_0")
    print(f"  <0|x|2> = {d_20:.4e} m = {d_20/x0:.4f} x_0 (overtone)")
