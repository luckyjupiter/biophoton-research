"""
Coherence propagation model for biophotons in myelin waveguide.

Models how quantum coherence (g1, g2 correlation functions) evolves
as biophotons propagate through lossy, noisy myelin waveguides.

Computes:
  - First-order coherence g^(1)(tau)
  - Second-order correlation g^(2)(tau) for different source states
  - Decoherence length as a function of loss
  - Entanglement sudden death analysis
  - Lindblad master equation evolution for cavity + waveguide system
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    HBAR, C_LIGHT, K_B, EPSILON_0,
    N_MYELIN, N_AXON,
    T_PHYSIOL, KBT,
    OMEGA_10, OMEGA_21,
    LAMBDA_10, LAMBDA_21,
    GAMMA_DEPH,
)


# ---- Loss parameters for mid-IR in myelin ----

def absorption_coefficient(wavelength: float) -> float:
    """Estimate absorption coefficient in myelin at given wavelength.

    Mid-IR absorption in biological lipid is dominated by C-H stretch,
    water overtones, and C-C modes.

    Parameters
    ----------
    wavelength : float
        Wavelength [m].

    Returns
    -------
    float
        Absorption coefficient [m^-1].
    """
    lam_um = wavelength * 1e6
    # Simplified model based on lipid IR spectroscopy
    # Strong absorption at C-H stretch (~3.4 um) and O-H (~2.9 um)
    alpha_base = 200.0  # baseline [m^-1]

    # C-H stretch band centered at 3.4 um, FWHM ~ 0.3 um
    alpha_ch = 2000.0 * np.exp(-((lam_um - 3.4) / 0.15)**2)

    # Water O-H overtone near 2.9 um
    alpha_oh = 5000.0 * np.exp(-((lam_um - 2.9) / 0.2)**2)

    return alpha_base + alpha_ch + alpha_oh


def scattering_coefficient(wavelength: float, d_myelin: float = 1e-6) -> float:
    """Rayleigh-like scattering from myelin structural inhomogeneities.

    Parameters
    ----------
    wavelength : float
        Wavelength [m].
    d_myelin : float
        Characteristic inhomogeneity size [m].

    Returns
    -------
    float
        Scattering coefficient [m^-1].
    """
    lam_um = wavelength * 1e6
    # Rayleigh: alpha_scat ~ 1/lambda^4 * (delta_n)^2 * density
    delta_n = 0.02  # refractive index fluctuation
    # Characteristic scattering length ~ lambda^4 / (delta_n^2 * a^3)
    a = 20e-9  # characteristic scatterer size (protein inclusions)
    alpha_scat = (2 * np.pi / wavelength)**4 * a**3 * delta_n**2 * 1e6
    return min(alpha_scat, 100.0)  # cap at physically reasonable value


def total_loss_coefficient(wavelength: float) -> float:
    """Total loss (absorption + scattering) [m^-1]."""
    return absorption_coefficient(wavelength) + scattering_coefficient(wavelength)


def decoherence_length(wavelength: float, Q: float = 10.0) -> float:
    """Estimate the length over which quantum coherence is maintained.

    The photon coherence length is limited by:
    1. Cavity Q factor -> spectral width -> coherence time
    2. Absorption -> exponential decay of amplitude

    Parameters
    ----------
    wavelength : float
        Photon wavelength [m].
    Q : float
        Cavity quality factor.

    Returns
    -------
    float
        Decoherence length [m].
    """
    omega = 2 * np.pi * C_LIGHT / wavelength

    # Coherence length from cavity linewidth
    l_coh_cavity = C_LIGHT * Q / (N_MYELIN * omega)

    # 1/e amplitude decay from absorption
    alpha = total_loss_coefficient(wavelength)
    l_abs = 1.0 / alpha if alpha > 0 else np.inf

    # The effective decoherence length is the minimum
    return min(l_coh_cavity, l_abs)


def g1_coherence(tau: np.ndarray, omega: float,
                  kappa: float, n_bar: float = 0.0) -> np.ndarray:
    """First-order coherence function g^(1)(tau).

    For a damped cavity mode:
    g^(1)(tau) = exp(-i*omega*tau - kappa*|tau|/2)

    Parameters
    ----------
    tau : np.ndarray
        Time delays [s].
    omega : float
        Mode frequency [rad/s].
    kappa : float
        Decay rate [s^-1].
    n_bar : float
        Mean thermal photon number.

    Returns
    -------
    np.ndarray
        Complex g^(1)(tau).
    """
    return np.exp(-1j * omega * tau - kappa * np.abs(tau) / 2.0)


def g2_correlation(tau: np.ndarray, state_type: str = 'thermal',
                    kappa: float = 1e12, n_bar: float = 1.0,
                    omega: float = None) -> np.ndarray:
    """Second-order correlation function g^(2)(tau).

    Parameters
    ----------
    tau : np.ndarray
        Time delays [s].
    state_type : str
        'thermal', 'coherent', 'fock_1', 'squeezed', or 'biphoton'.
    kappa : float
        Decay rate [s^-1].
    n_bar : float
        Mean photon number (for thermal/coherent).
    omega : float
        Frequency (used for some state types).

    Returns
    -------
    np.ndarray
        g^(2)(tau) values.
    """
    if state_type == 'thermal':
        # Bunching: g^(2)(tau) = 1 + |g^(1)(tau)|^2
        return 1.0 + np.exp(-kappa * np.abs(tau))

    elif state_type == 'coherent':
        # Poissonian: g^(2)(tau) = 1 for all tau
        return np.ones_like(tau)

    elif state_type == 'fock_1':
        # Anti-bunching: g^(2)(0) = 0
        # g^(2)(tau) = 1 - exp(-kappa*|tau|) for single Fock state
        return 1.0 - np.exp(-kappa * np.abs(tau))

    elif state_type == 'squeezed':
        # Super-bunching: g^(2)(0) > 2
        r = 0.5  # squeeze parameter
        n_sq = np.sinh(r)**2
        g2_0 = 3.0 + 1.0 / n_sq  # for squeezed vacuum
        decay = np.exp(-kappa * np.abs(tau))
        return 1.0 + (g2_0 - 1.0) * decay

    elif state_type == 'biphoton':
        # For biphoton (cascade): g^(2)(0) >> 1 for heralded detection
        # Decays as double exponential due to cascade timing
        Gamma = kappa  # effective rate
        return 1.0 + 100.0 * np.exp(-Gamma * np.abs(tau))

    else:
        raise ValueError(f"Unknown state type: {state_type}")


def propagate_density_matrix(rho_0: np.ndarray, t_array: np.ndarray,
                              omega: float, kappa: float,
                              n_thermal: float = 0.0,
                              gamma_deph: float = 0.0) -> list:
    """Propagate density matrix under Lindblad master equation.

    drho/dt = -i*[H, rho] + kappa*(n+1)*D[a] + kappa*n*D[a^dag] + gamma_deph*D[a^dag*a]

    where D[O]rho = O*rho*O^dag - 1/2 * {O^dag*O, rho}

    Parameters
    ----------
    rho_0 : np.ndarray
        Initial density matrix (dim x dim).
    t_array : np.ndarray
        Time points [s].
    omega : float
        Cavity frequency [rad/s].
    kappa : float
        Cavity decay rate [s^-1].
    n_thermal : float
        Thermal photon number.
    gamma_deph : float
        Additional dephasing rate [s^-1].

    Returns
    -------
    list of np.ndarray
        Density matrices at each time point.
    """
    dim = rho_0.shape[0]

    # Operators
    a = np.zeros((dim, dim), dtype=complex)
    for n in range(dim - 1):
        a[n, n + 1] = np.sqrt(n + 1)
    a_dag = a.conj().T
    n_op = a_dag @ a
    I = np.eye(dim, dtype=complex)

    def lindblad_dissipator(L, rho):
        """D[L]rho = L*rho*L^dag - 1/2 * {L^dag*L, rho}"""
        return L @ rho @ L.conj().T - 0.5 * (L.conj().T @ L @ rho + rho @ L.conj().T @ L)

    # Hamiltonian (rotating frame -> H = 0 for single mode)
    H = np.zeros((dim, dim), dtype=complex)

    def drho_dt(t, rho_flat):
        rho = rho_flat.reshape((dim, dim))

        # Unitary part
        drho = -1j * (H @ rho - rho @ H)

        # Dissipation
        drho += kappa * (n_thermal + 1) * lindblad_dissipator(a, rho)
        drho += kappa * n_thermal * lindblad_dissipator(a_dag, rho)
        if gamma_deph > 0:
            drho += gamma_deph * lindblad_dissipator(n_op, rho)

        return drho.flatten()

    # Solve
    rho_flat_0 = rho_0.flatten()
    sol = solve_ivp(drho_dt, [t_array[0], t_array[-1]], rho_flat_0,
                    t_eval=t_array, method='RK45', rtol=1e-8, atol=1e-10)

    rho_list = [sol.y[:, i].reshape((dim, dim)) for i in range(len(t_array))]
    return rho_list


def entanglement_decay_vs_distance(d_array: np.ndarray,
                                     wavelength: float = None,
                                     initial_concurrence: float = 0.8) -> dict:
    """Model entanglement decay as biphoton propagates through waveguide.

    Simple exponential model: C(z) = C_0 * exp(-z / l_ent)
    where l_ent is the entanglement decay length.

    For amplitude damping channel on each photon, entanglement sudden death
    can occur at finite distance.

    Parameters
    ----------
    d_array : np.ndarray
        Propagation distances [m].
    wavelength : float
        Photon wavelength [m].
    initial_concurrence : float
        Initial concurrence C_0.

    Returns
    -------
    dict
        'd': distances, 'concurrence': concurrence values,
        'esd_distance': entanglement sudden death distance (if any).
    """
    if wavelength is None:
        wavelength = LAMBDA_10

    alpha = total_loss_coefficient(wavelength)
    # Transmission amplitude at distance z
    eta = np.exp(-alpha * d_array / 2.0)  # amplitude transmission

    # For amplitude damping on both qubits with parameter eta:
    # Concurrence of Werner-like state decays as:
    # C(z) = max(0, 2*eta^2 - 1) for maximally entangled input
    # C(z) = max(0, C_0 * eta^2 - (1 - eta^2)) for partial entanglement
    concurrence = np.maximum(0.0, initial_concurrence * eta**2 - (1.0 - eta**2))

    # Find ESD distance (where concurrence first hits 0)
    esd_idx = np.argmax(concurrence == 0)
    esd_distance = d_array[esd_idx] if concurrence[esd_idx] == 0 and esd_idx > 0 else np.inf

    return {
        'd': d_array,
        'concurrence': concurrence,
        'esd_distance': esd_distance,
        'loss_coefficient': alpha,
        'wavelength': wavelength,
    }


def coherence_length_survey() -> dict:
    """Survey decoherence lengths across biophoton-relevant wavelengths."""
    wavelengths_um = np.linspace(0.5, 5.0, 200)
    wavelengths_m = wavelengths_um * 1e-6

    l_coh = np.array([decoherence_length(w) for w in wavelengths_m])
    alpha_total = np.array([total_loss_coefficient(w) for w in wavelengths_m])
    alpha_abs = np.array([absorption_coefficient(w) for w in wavelengths_m])
    alpha_scat = np.array([scattering_coefficient(w) for w in wavelengths_m])

    return {
        'wavelength_um': wavelengths_um,
        'wavelength_m': wavelengths_m,
        'l_coh_m': l_coh,
        'l_coh_um': l_coh * 1e6,
        'alpha_total': alpha_total,
        'alpha_abs': alpha_abs,
        'alpha_scat': alpha_scat,
    }


if __name__ == "__main__":
    print("=== Coherence Propagation Model ===\n")

    # Decoherence lengths at key wavelengths
    for label, lam in [("lambda_10 (3.54 um)", LAMBDA_10),
                        ("lambda_21 (3.70 um)", LAMBDA_21),
                        ("visible (0.63 um)", 0.63e-6),
                        ("near-IR (0.85 um)", 0.85e-6)]:
        l_coh = decoherence_length(lam)
        alpha = total_loss_coefficient(lam)
        print(f"{label}:")
        print(f"  alpha_total = {alpha:.1f} m^-1")
        print(f"  1/e length = {1/alpha*1e6:.1f} um")
        print(f"  decoherence length = {l_coh*1e6:.2f} um")

    # g^(2)(0) for different states
    print(f"\n--- g^(2)(0) values ---")
    tau_0 = np.array([0.0])
    for st in ['thermal', 'coherent', 'fock_1', 'squeezed', 'biphoton']:
        g2 = g2_correlation(tau_0, st)
        print(f"  {st:12s}: g^(2)(0) = {g2[0]:.2f}")

    # Entanglement decay
    print(f"\n--- Entanglement Decay ---")
    dists = np.linspace(0, 50e-6, 200)
    for C0 in [0.9, 0.5, 0.2]:
        result = entanglement_decay_vs_distance(dists, LAMBDA_10, C0)
        print(f"  C_0 = {C0:.1f}: ESD at {result['esd_distance']*1e6:.1f} um "
              f"(alpha = {result['loss_coefficient']:.0f} m^-1)")

    # Lindblad evolution
    print(f"\n--- Lindblad Evolution (Fock |1> in lossy cavity) ---")
    dim = 5
    rho_0 = np.zeros((dim, dim), dtype=complex)
    rho_0[1, 1] = 1.0  # |1> state

    kappa = 1e12  # cavity decay rate
    t_arr = np.linspace(0, 5e-12, 50)
    rho_list = propagate_density_matrix(rho_0, t_arr, OMEGA_10, kappa)

    print(f"  Initial <n> = {np.real(np.trace(np.diag(np.arange(dim)) @ rho_list[0])):.3f}")
    print(f"  Final   <n> = {np.real(np.trace(np.diag(np.arange(dim)) @ rho_list[-1])):.3f}")
    purity_0 = np.real(np.trace(rho_list[0] @ rho_list[0]))
    purity_f = np.real(np.trace(rho_list[-1] @ rho_list[-1]))
    print(f"  Initial purity = {purity_0:.4f}")
    print(f"  Final   purity = {purity_f:.4f}")
