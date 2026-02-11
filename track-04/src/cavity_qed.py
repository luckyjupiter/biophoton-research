"""
Cavity QED model for myelin sheath as optical microcavity.

Models:
  - Cylindrical shell cavity mode structure
  - Purcell enhancement
  - Cavity Q factors
  - Mode volumes
  - Vacuum Rabi coupling
"""

import numpy as np
from scipy.special import jn_zeros, jnp_zeros, jv, yv
from scipy.optimize import brentq
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    HBAR, C_LIGHT, EPSILON_0, EV_TO_J,
    N_MYELIN, N_AXON, N_ISF,
    AXON_RADIUS_TYPICAL, MYELIN_THICKNESS_TYPICAL,
    INTERNODE_LENGTH_TYPICAL,
    OMEGA_10, OMEGA_21, OMEGA_20,
    LAMBDA_10, LAMBDA_21,
    DIPOLE_10, DIPOLE_21,
    GAMMA_10_FREE, GAMMA_21_FREE,
    N_CAVITY_MODES
)


def cavity_mode_frequencies_simple(a: float, d: float, L: float,
                                    n_eff: float = N_MYELIN,
                                    m_max: int = 3, n_max: int = 5,
                                    p_max: int = 10) -> dict:
    """Compute cavity mode frequencies for cylindrical shell cavity.

    Simplified model: approximate the myelin shell as a cylindrical cavity
    of effective radius R = a + d/2 with perfectly reflecting walls.
    This gives a lower bound on the mode density.

    Parameters
    ----------
    a : float
        Inner radius (axon) [m].
    d : float
        Myelin thickness [m].
    L : float
        Cavity length (internode) [m].
    n_eff : float
        Effective refractive index.
    m_max, n_max, p_max : int
        Max azimuthal, radial, longitudinal mode indices.

    Returns
    -------
    dict with 'frequencies' (rad/s), 'wavelengths' (m), 'mode_indices' (m, n, p),
    'mode_volumes' (m^3).
    """
    R = a + d / 2.0  # effective radius
    b = a + d         # outer radius

    freqs = []
    wavelengths = []
    indices = []
    volumes = []

    for m in range(m_max + 1):
        # TM modes: zeros of J_m
        x_mn = jn_zeros(m, n_max)
        for n_idx, x in enumerate(x_mn):
            k_perp = x / R
            for p in range(p_max + 1):
                k_z = p * np.pi / L if p > 0 else 0.0
                k_total = np.sqrt(k_perp**2 + k_z**2)
                omega = C_LIGHT * k_total / n_eff
                lam = 2.0 * np.pi * C_LIGHT / omega if omega > 0 else np.inf

                # Mode volume estimate: shell cross-section * length / mode overlap
                V_shell = np.pi * (b**2 - a**2) * L
                # Effective mode volume is roughly V_shell / N_modes_in_volume
                V_mode = V_shell  # conservative estimate

                freqs.append(omega)
                wavelengths.append(lam)
                indices.append(('TM', m, n_idx + 1, p))
                volumes.append(V_mode)

    # Sort by frequency
    order = np.argsort(freqs)
    freqs = np.array(freqs)[order]
    wavelengths = np.array(wavelengths)[order]
    indices = [indices[i] for i in order]
    volumes = np.array(volumes)[order]

    return {
        'frequencies': freqs,
        'wavelengths': wavelengths,
        'mode_indices': indices,
        'mode_volumes': volumes,
    }


def modes_near_frequency(mode_dict: dict, omega_target: float,
                          delta_omega: float) -> dict:
    """Extract modes within delta_omega of target frequency."""
    freqs = mode_dict['frequencies']
    mask = np.abs(freqs - omega_target) < delta_omega
    return {
        'frequencies': freqs[mask],
        'wavelengths': mode_dict['wavelengths'][mask],
        'mode_indices': [mode_dict['mode_indices'][i] for i in range(len(freqs)) if mask[i]],
        'mode_volumes': mode_dict['mode_volumes'][mask],
        'count': int(np.sum(mask)),
    }


def cavity_q_factor(d: float, omega: float,
                     alpha_abs: float = 100.0) -> float:
    """Estimate cavity quality factor.

    The Q factor is limited by:
    1. Absorption losses in the lipid medium
    2. Radiation leakage at interfaces
    3. Scattering from inhomogeneities

    Parameters
    ----------
    d : float
        Myelin thickness [m].
    omega : float
        Mode frequency [rad/s].
    alpha_abs : float
        Absorption coefficient [m^-1] (typical mid-IR in lipid: 100-1000 /m).

    Returns
    -------
    float
        Estimated Q factor.
    """
    # Round-trip path in the radial direction
    path_length = 2.0 * d

    # Fresnel reflectivity at myelin-axon and myelin-ISF interfaces
    R1 = ((N_MYELIN - N_AXON) / (N_MYELIN + N_AXON))**2
    R2 = ((N_MYELIN - N_ISF) / (N_MYELIN + N_ISF))**2

    # Mirror loss per round trip
    loss_mirror = 1.0 - np.sqrt(R1 * R2)

    # Absorption loss per round trip
    loss_abs = 1.0 - np.exp(-alpha_abs * path_length)

    # Total loss per round trip
    total_loss = loss_mirror + loss_abs

    # Q = omega * round-trip-time / total_loss
    round_trip_time = path_length * N_MYELIN / C_LIGHT
    Q = omega * round_trip_time / max(total_loss, 1e-10)

    return Q


def purcell_factor(Q: float, V_mode: float, wavelength: float,
                    n: float = N_MYELIN) -> float:
    """Purcell enhancement factor.

    F_P = (3 / (4 * pi^2)) * (lambda/n)^3 * Q / V

    Parameters
    ----------
    Q : float
        Cavity quality factor.
    V_mode : float
        Mode volume [m^3].
    wavelength : float
        Resonance wavelength [m].
    n : float
        Refractive index.

    Returns
    -------
    float
        Purcell factor.
    """
    lam_n = wavelength / n
    return (3.0 / (4.0 * np.pi**2)) * lam_n**3 * Q / V_mode


def vacuum_rabi_coupling(dipole: float, omega: float, V_mode: float,
                          epsilon_r: float = N_MYELIN**2) -> float:
    """Vacuum Rabi frequency g = d * sqrt(omega / (2 * eps_0 * eps_r * V * hbar)).

    Parameters
    ----------
    dipole : float
        Transition dipole moment [C m].
    omega : float
        Cavity mode frequency [rad/s].
    V_mode : float
        Mode volume [m^3].
    epsilon_r : float
        Relative permittivity.

    Returns
    -------
    float
        Vacuum Rabi frequency [rad/s].
    """
    return dipole / HBAR * np.sqrt(HBAR * omega / (2.0 * EPSILON_0 * epsilon_r * V_mode))


def cavity_decay_rate(Q: float, omega: float) -> float:
    """Cavity photon decay rate kappa = omega / (2*Q)."""
    return omega / (2.0 * Q)


def cooperativity(g: float, kappa: float, gamma: float) -> float:
    """Single-emitter cooperativity C = g^2 / (kappa * gamma)."""
    return g**2 / (kappa * gamma)


def strong_coupling_criterion(g: float, kappa: float, gamma: float) -> bool:
    """Check if system is in strong coupling: g > (kappa + gamma) / 4."""
    return g > (kappa + gamma) / 4.0


def mode_volume_cylindrical_shell(a: float, d: float, L: float,
                                    m: int = 0, n: int = 1) -> float:
    """Effective mode volume for low-order mode in cylindrical shell.

    Approximate: for the (m, n) mode, the transverse confinement
    is of order (lambda / n_eff) in each transverse direction,
    and L in the longitudinal direction.

    A more physical estimate: the mode is confined to the myelin
    shell cross-section pi*(b^2 - a^2) over a length L.
    """
    b = a + d
    V_geom = np.pi * (b**2 - a**2) * L
    # For low-order modes, effective volume is comparable to geometric
    # For higher-order, it can be smaller (mode localization)
    return V_geom


def thickness_scan(a: float = AXON_RADIUS_TYPICAL,
                    L: float = INTERNODE_LENGTH_TYPICAL,
                    d_array: np.ndarray = None,
                    alpha_abs: float = 300.0) -> dict:
    """Scan myelin thickness and compute cavity QED parameters.

    Returns
    -------
    dict with arrays: 'd', 'Q_10', 'Q_21', 'F_P_10', 'F_P_21',
    'g_10', 'g_21', 'kappa_10', 'kappa_21', 'cooperativity_10', 'cooperativity_21'.
    """
    if d_array is None:
        d_array = np.linspace(0.3e-6, 3.0e-6, 100)

    results = {k: np.zeros(len(d_array)) for k in [
        'Q_10', 'Q_21', 'F_P_10', 'F_P_21',
        'g_10', 'g_21', 'kappa_10', 'kappa_21',
        'C_10', 'C_21', 'V_mode'
    ]}
    results['d'] = d_array

    for i, d in enumerate(d_array):
        V = mode_volume_cylindrical_shell(a, d, L)
        results['V_mode'][i] = V

        Q10 = cavity_q_factor(d, OMEGA_10, alpha_abs)
        Q21 = cavity_q_factor(d, OMEGA_21, alpha_abs)
        results['Q_10'][i] = Q10
        results['Q_21'][i] = Q21

        results['F_P_10'][i] = purcell_factor(Q10, V, LAMBDA_10)
        results['F_P_21'][i] = purcell_factor(Q21, V, LAMBDA_21)

        g10 = vacuum_rabi_coupling(DIPOLE_10, OMEGA_10, V)
        g21 = vacuum_rabi_coupling(DIPOLE_21, OMEGA_21, V)
        results['g_10'][i] = g10
        results['g_21'][i] = g21

        kappa10 = cavity_decay_rate(Q10, OMEGA_10)
        kappa21 = cavity_decay_rate(Q21, OMEGA_21)
        results['kappa_10'][i] = kappa10
        results['kappa_21'][i] = kappa21

        results['C_10'][i] = cooperativity(g10, kappa10, GAMMA_10_FREE)
        results['C_21'][i] = cooperativity(g21, kappa21, GAMMA_21_FREE)

    return results


if __name__ == "__main__":
    print("=== Cavity QED Model for Myelin Sheath ===\n")

    a = AXON_RADIUS_TYPICAL
    d = MYELIN_THICKNESS_TYPICAL
    L = INTERNODE_LENGTH_TYPICAL
    b = a + d

    print(f"Geometry: a = {a*1e6:.1f} um, d = {d*1e6:.1f} um, L = {L*1e6:.0f} um")
    print(f"Refractive indices: n_myelin={N_MYELIN}, n_axon={N_AXON}, n_isf={N_ISF}\n")

    V = mode_volume_cylindrical_shell(a, d, L)
    print(f"Mode volume (geometric): {V:.3e} m^3 = {V*1e18:.1f} um^3")

    for label, omega, lam, dipole, gamma_free in [
        ("|1>->|0>", OMEGA_10, LAMBDA_10, DIPOLE_10, GAMMA_10_FREE),
        ("|2>->|1>", OMEGA_21, LAMBDA_21, DIPOLE_21, GAMMA_21_FREE),
    ]:
        Q = cavity_q_factor(d, omega, alpha_abs=300.0)
        Fp = purcell_factor(Q, V, lam)
        g = vacuum_rabi_coupling(dipole, omega, V)
        kappa = cavity_decay_rate(Q, omega)
        C = cooperativity(g, kappa, gamma_free)
        sc = strong_coupling_criterion(g, kappa, gamma_free)

        print(f"\nTransition {label} (lambda = {lam*1e6:.2f} um):")
        print(f"  Q factor    = {Q:.1f}")
        print(f"  Purcell F_P = {Fp:.2e}")
        print(f"  g (Rabi)    = {g:.2e} rad/s")
        print(f"  kappa       = {kappa:.2e} rad/s")
        print(f"  gamma_free  = {gamma_free:.2e} s^-1")
        print(f"  Cooperativity C = {C:.2e}")
        print(f"  Strong coupling: {'YES' if sc else 'NO'} (g vs (kappa+gamma)/4 = {(kappa+gamma_free)/4:.2e})")
