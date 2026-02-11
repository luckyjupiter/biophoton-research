"""
Physical constants and myelin-specific parameters for quantum optics modeling.

All SI units unless otherwise noted.
Notation follows the project conventions in root CLAUDE.md.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Fundamental constants (CODATA 2018)
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34        # reduced Planck constant [J s]
C_LIGHT = 2.99792458e8        # speed of light [m/s]
EPSILON_0 = 8.854187817e-12   # vacuum permittivity [F/m]
K_B = 1.380649e-23            # Boltzmann constant [J/K]
EV_TO_J = 1.602176634e-19     # electron-volt to joule
CM_INV_TO_J = 1.98644568e-23  # wavenumber (cm^-1) to joule
CM_INV_TO_EV = 1.23984193e-4  # wavenumber (cm^-1) to eV
AMU = 1.66053906660e-27       # atomic mass unit [kg]

# ---------------------------------------------------------------------------
# Myelin sheath geometry and optical parameters
# ---------------------------------------------------------------------------
N_MYELIN = 1.44               # myelin sheath (lipid-rich)
N_AXON = 1.38                 # axon interior (aqueous cytoplasm)
N_ISF = 1.34                  # interstitial fluid (external medium)

AXON_RADIUS_MIN = 0.5e-6     # [m]
AXON_RADIUS_MAX = 5.0e-6     # [m]
AXON_RADIUS_TYPICAL = 1.0e-6 # [m]

MYELIN_THICKNESS_MIN = 0.45e-6  # [m]
MYELIN_THICKNESS_MAX = 3.0e-6   # [m]
MYELIN_THICKNESS_TYPICAL = 1.0e-6  # [m] peak entanglement region

BILAYER_PERIOD = 16e-9        # [m]
INTERNODE_LENGTH_MIN = 200e-6   # [m]
INTERNODE_LENGTH_MAX = 2000e-6  # [m]
INTERNODE_LENGTH_TYPICAL = 500e-6  # [m]

# ---------------------------------------------------------------------------
# C-H Morse oscillator parameters
# ---------------------------------------------------------------------------
OMEGA_E_CM = 2950.0           # harmonic frequency [cm^-1]
OMEGA_E_CHI_CM = 62.5         # anharmonicity constant [cm^-1]
D_E_EV = 4.4                  # dissociation energy [eV]
D_E_J = D_E_EV * EV_TO_J     # dissociation energy [J]
OMEGA_E_RAD = OMEGA_E_CM * CM_INV_TO_J / HBAR   # [rad/s]

M_CARBON = 12.0 * AMU
M_HYDROGEN = 1.008 * AMU
MU_CH = M_CARBON * M_HYDROGEN / (M_CARBON + M_HYDROGEN)

ALPHA_MORSE = OMEGA_E_RAD * np.sqrt(MU_CH / (2.0 * D_E_J))
R_EQ = 1.09e-10               # [m] C-H equilibrium bond length

# Transition dipole moments
DIPOLE_10 = 0.03 * 3.33564e-30  # [C m] ~0.03 Debye
DIPOLE_21 = 0.02 * 3.33564e-30  # [C m] ~0.02 Debye


def morse_energy_level(v: int) -> float:
    """Morse oscillator energy level in Joules.

    Parameters
    ----------
    v : int
        Vibrational quantum number.

    Returns
    -------
    float
        Energy in Joules.
    """
    e_harmonic = HBAR * OMEGA_E_RAD * (v + 0.5)
    e_anharmonic = e_harmonic**2 / (4.0 * D_E_J)
    return e_harmonic - e_anharmonic


E0 = morse_energy_level(0)
E1 = morse_energy_level(1)
E2 = morse_energy_level(2)

# Transition frequencies [rad/s]
OMEGA_10 = (E1 - E0) / HBAR
OMEGA_21 = (E2 - E1) / HBAR
OMEGA_20 = (E2 - E0) / HBAR

# Corresponding wavelengths [m]
LAMBDA_10 = 2.0 * np.pi * C_LIGHT / OMEGA_10
LAMBDA_21 = 2.0 * np.pi * C_LIGHT / OMEGA_21
LAMBDA_20 = 2.0 * np.pi * C_LIGHT / OMEGA_20

# ---------------------------------------------------------------------------
# Physiological temperature
# ---------------------------------------------------------------------------
T_PHYSIOL = 310.0
KBT = K_B * T_PHYSIOL


def n_thermal(omega: float, T: float = T_PHYSIOL) -> float:
    """Mean thermal photon number (Bose-Einstein)."""
    x = HBAR * omega / (K_B * T)
    if x > 500:
        return 0.0
    return 1.0 / (np.exp(x) - 1.0)


N_TH_10 = n_thermal(OMEGA_10)
N_TH_21 = n_thermal(OMEGA_21)

# ---------------------------------------------------------------------------
# Decoherence parameters
# ---------------------------------------------------------------------------
T2_STAR = 1.0e-12             # [s] vibrational dephasing time
GAMMA_DEPH = 1.0 / T2_STAR

def free_space_decay_rate(omega: float, dipole: float) -> float:
    """Spontaneous emission rate in free space [s^-1]."""
    return omega**3 * dipole**2 / (3.0 * np.pi * EPSILON_0 * HBAR * C_LIGHT**3)


GAMMA_10_FREE = free_space_decay_rate(OMEGA_10, DIPOLE_10)
GAMMA_21_FREE = free_space_decay_rate(OMEGA_21, DIPOLE_21)

CH_DENSITY = 1.0e15           # C-H bonds per um of internode length

# ---------------------------------------------------------------------------
# M-Phi framework coupling
# ---------------------------------------------------------------------------
G_PHI_PSI = 1.0e-3            # matter-field coupling [dimensionless]
KAPPA_DECOHERENCE = 1.0e12    # decoherence rate [rad/s]

# Simulation defaults
N_CAVITY_MODES = 20
FOCK_TRUNCATION = 4
N_THICKNESS_POINTS = 100


if __name__ == "__main__":
    print("=== Track 04: Physical Constants & Parameters ===")
    print(f"Morse E0 = {E0/EV_TO_J:.4f} eV")
    print(f"Morse E1 = {E1/EV_TO_J:.4f} eV")
    print(f"Morse E2 = {E2/EV_TO_J:.4f} eV")
    print(f"|1>->|0>: omega = {OMEGA_10:.3e} rad/s, lambda = {LAMBDA_10*1e6:.3f} um")
    print(f"|2>->|1>: omega = {OMEGA_21:.3e} rad/s, lambda = {LAMBDA_21*1e6:.3f} um")
    print(f"|2>->|0>: omega = {OMEGA_20:.3e} rad/s, lambda = {LAMBDA_20*1e6:.3f} um")
    print(f"n_th(omega_10) = {N_TH_10:.2e}")
    print(f"n_th(omega_21) = {N_TH_21:.2e}")
    print(f"gamma_10_free = {GAMMA_10_FREE:.2e} s^-1")
    print(f"gamma_21_free = {GAMMA_21_FREE:.2e} s^-1")
    print(f"dephasing rate = {GAMMA_DEPH:.2e} s^-1")
