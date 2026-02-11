"""
Physical constants and parameters for biophoton demyelination modeling.

This is the single authoritative source of constants for the entire biophoton
research program. All track-specific code should import from here rather than
redefining values locally.

Sources:
- Refractive indices: Sun et al. (2012) J Biomed Opt; Binding et al. (2011) Cytometry A
- Myelin dimensions: Waxman & Bangalore (1992); Chomiak & Bhairavnath (2009)
- ROS emission: Cifra & Pospíšil (2014) J Photochem Photobiol B
- Biophoton baseline: Kobayashi et al. (2009) J Photochem Photobiol B
- Detector specs: Hadfield (2009) Nature Photonics; Hamamatsu PMT handbook
- Morse oscillator: Herzberg (1950) Molecular Spectra
- M-Phi framework: Kruger, Feeney, Duarte (2023)
- Cauchy dispersion: Fitted to measured values, typical biological dispersion
- QTrainerAI BU parameters: Scott's directives (Jan-Feb 2026)
- Network parameters: derived from axon bundle geometry estimates
"""

import numpy as np

# ===========================================================================
# Fundamental physical constants (CODATA 2018)
# ===========================================================================
HBAR = 1.054571817e-34        # reduced Planck constant [J s]
C_LIGHT = 2.99792458e8        # speed of light in vacuum [m/s]
EPSILON_0 = 8.854187817e-12   # vacuum permittivity [F/m]
K_B = 1.380649e-23            # Boltzmann constant [J/K]
H_PLANCK = 6.626e-34          # Planck constant [J*s]
EV_TO_J = 1.602176634e-19     # electron-volt to joule
CM_INV_TO_J = 1.98644568e-23  # wavenumber (cm^-1) to joule
AMU = 1.66053906660e-27       # atomic mass unit [kg]

# ===========================================================================
# Refractive indices at visible wavelengths (~550 nm reference)
# ===========================================================================
N_MYELIN = 1.44               # compact myelin sheath (lipid-rich)
N_AXON = 1.38                 # axoplasm (cytoplasm-like)
N_ECF = 1.34                  # extracellular fluid
N_VACUUM = 1.0
N_PERIAXONAL = 1.34           # periaxonal space (thin fluid layer)
N_LIPID_BILAYER = 1.48        # individual lipid bilayer within myelin
N_CYTOPLASM_INTRA = 1.35      # intra-myelin cytoplasmic layers

# Numerical apertures (derived)
NA_MYELIN_AXON = float(np.sqrt(N_MYELIN**2 - N_AXON**2))   # ~0.411
NA_MYELIN_ECF = float(np.sqrt(N_MYELIN**2 - N_ECF**2))     # ~0.527

# ===========================================================================
# Cauchy dispersion coefficients
# n(lambda) = A + B/lambda^2 + C/lambda^4
# Fitted to n=1.44 at 550nm with typical biological dispersion
# ===========================================================================
CAUCHY_A_MYELIN = 1.4270
CAUCHY_B_MYELIN = 3.96e-15    # [m^2]
CAUCHY_A_AXOPLASM = 1.3680
CAUCHY_B_AXOPLASM = 3.63e-15
CAUCHY_A_ECF = 1.3280
CAUCHY_B_ECF = 3.63e-15


def n_cauchy(wavelength_m, A, B, C=0.0):
    """Cauchy dispersion relation: n(lambda) = A + B/lambda^2 + C/lambda^4."""
    lam = np.asarray(wavelength_m, dtype=float)
    return A + B / lam**2 + C / lam**4


def n_myelin_dispersive(wavelength_nm):
    """Refractive index of myelin with Cauchy dispersion."""
    return n_cauchy(np.asarray(wavelength_nm, dtype=float) * 1e-9,
                    CAUCHY_A_MYELIN, CAUCHY_B_MYELIN)


def n_axoplasm_dispersive(wavelength_nm):
    """Refractive index of axoplasm with Cauchy dispersion."""
    return n_cauchy(np.asarray(wavelength_nm, dtype=float) * 1e-9,
                    CAUCHY_A_AXOPLASM, CAUCHY_B_AXOPLASM)

# ===========================================================================
# Myelin structural geometry
# ===========================================================================
LIPID_BILAYER_THICKNESS_NM = 10.0    # single myelin wrap ~10 nm
LIPID_BILAYER_THICKNESS_M = 10e-9
MYELIN_PERIOD_NM = 17.0              # full lamella periodicity [nm]

# Biological geometry
G_RATIO_CNS = 0.75                   # typical CNS g-ratio
G_RATIO_PNS = 0.6                    # typical PNS g-ratio
G_RATIO_OPTIMAL_OPTICAL = 0.7        # optimal for waveguiding (Babini et al. 2022)
NODE_LENGTH_UM = 1.0                 # Node of Ranvier length [um]
INTERNODE_LENGTH_MM = 1.0            # typical internode length [mm]

# ===========================================================================
# Wavelength range (nm)
# ===========================================================================
LAMBDA_MIN_NM = 200
LAMBDA_MAX_NM = 950
DEFAULT_LAMBDA_RANGE_NM = np.linspace(LAMBDA_MIN_NM, LAMBDA_MAX_NM, 751)

# ===========================================================================
# ROS spectral components
# Each entry: (center_nm, fwhm_nm, relative_amplitude, species)
# ===========================================================================
ROS_COMPONENTS = [
    (380, 60, 0.15, "lipid peroxidation (dioxetane)"),
    (460, 80, 0.25, "excited carbonyl"),
    (535, 50, 0.20, "singlet O2 dimol (1Δg+1Δg)"),
    (580, 40, 0.10, "excited carbonyl tail"),
    (634, 15, 0.08, "singlet O2 (1Δg→3Σg) 0-1"),
    (703, 15, 0.07, "singlet O2 (1Δg→3Σg) 0-0"),
    (760, 20, 0.05, "singlet O2 dimol 2×703"),
]

# Singlet oxygen specific peaks (for spectral fingerprinting)
SINGLET_O2_MONOMOL_PEAKS_NM = [634.0, 703.0]
SINGLET_O2_DIMOL_PEAKS_NM = [478.0, 534.0, 634.0]
SINGLET_O2_NIR_NM = 1270.0
TRIPLET_CARBONYL_RANGE_NM = (350.0, 550.0)
EXCITED_PIGMENT_RANGE_NM = (550.0, 750.0)

# ===========================================================================
# Baseline emission
# ===========================================================================
BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S = 100.0   # ~1-1000 typical range
BIOPHOTON_RATE_LOW = 1.0       # lower bound of typical UPE
BIOPHOTON_RATE_HIGH = 1000.0   # upper bound of typical UPE

# Inflammatory amplification factors
INFLAMMATORY_EMISSION_FACTOR_LOW = 10.0
INFLAMMATORY_EMISSION_FACTOR_HIGH = 100.0

# ===========================================================================
# Absorption/scattering in neural tissue
# ===========================================================================
ABSORPTION_COEFF_PER_CM = 2.0       # approximate tissue absorption at ~500 nm
SCATTER_COEFF_PER_CM = 10.0         # Rayleigh + Mie scattering
BEND_LOSS_PER_CM = 1.0              # bending losses in curved axons
# Total attenuation: 4–40 dB/cm depending on wavelength and geometry

# ===========================================================================
# Spectral tuning coefficients (Sefati/Zeng model)
# ===========================================================================
SPECTRAL_SHIFT_PER_LAYER_NM = 52.3          # +52.3 nm per myelin wrap
SPECTRAL_SHIFT_PER_UM_DIAMETER_NM = -94.5   # -94.5 nm per μm axon diameter

# ===========================================================================
# Detector specifications
# ===========================================================================
DETECTOR_SPECS = {
    "PMT": {
        "dark_rate_hz": 30.0,
        "quantum_efficiency": 0.25,
        "timing_jitter_ns": 0.3,
        "excess_noise_sq": 1.0,
        "collection_area_cm2": 5.0,
        "description": "Photomultiplier tube (e.g. Hamamatsu H7421-40)",
    },
    "EMCCD": {
        "dark_rate_hz": 0.001,   # cooled EM-CCD, per pixel
        "quantum_efficiency": 0.90,
        "timing_jitter_ns": None,  # frame-based, not single-photon
        "excess_noise_sq": 2.0,
        "collection_area_cm2": 0.002,
        "description": "Electron-multiplying CCD (e.g. Andor iXon)",
    },
    "SPAD": {
        "dark_rate_hz": 25.0,
        "quantum_efficiency": 0.50,
        "timing_jitter_ns": 0.05,
        "excess_noise_sq": 1.0,
        "collection_area_cm2": 0.002,
        "description": "Single-photon avalanche diode",
    },
    "SNSPD": {
        "dark_rate_hz": 0.01,
        "quantum_efficiency": 0.93,
        "timing_jitter_ns": 0.003,
        "excess_noise_sq": 1.0,
        "collection_area_cm2": 0.0003,
        "description": "Superconducting nanowire (cryogenic)",
    },
}

# ===========================================================================
# Hill equation defaults
# ===========================================================================
HILL_COEFFICIENT_DEFAULT = 3.0   # cooperative binding/damage sigmoid
HILL_K_HALF_DEFAULT = 0.5       # half-maximal effect at 50% damage
HILL_K_EMISSION = 0.20          # EC50 at 20% demyelination
HILL_N_EMISSION = 2.0
HILL_K_SPECTRAL = 0.50
HILL_N_SPECTRAL = 1.0

# ===========================================================================
# Disease-specific timescales
# ===========================================================================
# EAE (MOG-induced in C57BL/6)
EAE_ONSET_DAY = 10
EAE_PEAK_DAY = 16
EAE_CHRONIC_DAY = 28

# Cuprizone model (weeks)
CUPRIZONE_DEMYELINATION_WEEKS = 6
CUPRIZONE_REMYELINATION_START_WEEK = 7
CUPRIZONE_REMYELINATION_END_WEEK = 12

# LPC focal lesion (days)
LPC_DEMYELINATION_PEAK_DAY = 3.0
LPC_REMYELINATION_COMPLETE_DAY = 21.0

# Wallerian degeneration PNS (days)
WALLERIAN_MYELIN_FRAGMENTATION_DAY = 3.0
WALLERIAN_CLEARANCE_COMPLETE_DAY = 21.0

# MS subtype parameters
RRMS_RELAPSE_RATE_PER_YEAR = 1.0
RRMS_RELAPSE_DURATION_WEEKS = 6.0
RRMS_RECOVERY_FRACTION = 0.85
SPMS_ANNUAL_MYELIN_LOSS_FRACTION = 0.03
PPMS_ANNUAL_MYELIN_LOSS_FRACTION = 0.04

# ===========================================================================
# Physiological temperature
# ===========================================================================
T_PHYSIOL = 310.0     # 37 C in Kelvin
KBT = K_B * T_PHYSIOL


def n_thermal(omega, T=T_PHYSIOL):
    """Mean thermal photon number (Bose-Einstein distribution)."""
    x = HBAR * omega / (K_B * T)
    if x > 500:
        return 0.0
    return 1.0 / (np.exp(x) - 1.0)


# ===========================================================================
# Kappa subcomponents (decoherence contributors)
# ===========================================================================
KAPPA_THERMAL = 0.02       # thermal fluctuations at 37 C
KAPPA_STRUCTURAL = 0.01    # baseline structural disorder
KAPPA_ROS_HEALTHY = 0.01   # basal ROS in healthy tissue
KAPPA_INFLAMMATORY = 0.01  # no inflammation in healthy tissue
KAPPA_HEALTHY = KAPPA_THERMAL + KAPPA_STRUCTURAL + KAPPA_ROS_HEALTHY + KAPPA_INFLAMMATORY

# ===========================================================================
# Molecular generation (ROS cascade) constants
# ===========================================================================
# Enzyme rates (M^-1 s^-1)
K_SOD = 2e9               # superoxide dismutase
K_CAT = 1e7               # catalase
K_FENTON = 76.0           # Fe2+ + H2O2 -> OH. + OH- + Fe3+

# Quantum yields
PHI_TRIPLET = 0.01        # triplet carbonyl yield from Russell mechanism
PHI_SINGLET_O2 = 0.005    # singlet oxygen yield
PHI_RADIATIVE_TRIPLET = 1e-9
PHI_RADIATIVE_SINGLET = 1e-7

# ===========================================================================
# Statistical constants
# ===========================================================================
Z_SCORE_95 = 1.645
Z_SCORE_99 = 2.326
Z_SCORE_3SIGMA = 3.0
Z_SCORE_5SIGMA = 5.0

# Abramowitz-Stegun CDF coefficients (matching QTrainerAI scott_cdf_z_score)
AS_CDF_C1 = 2.506628275
AS_CDF_C7 = 0.2316419
AS_CDF_C8 = 0.319381530
AS_CDF_C9 = -0.356563782
AS_CDF_C10 = 1.781477937
AS_CDF_C11 = -1.821255978
AS_CDF_C12 = 1.330274429

# ===========================================================================
# M-Phi framework parameters
# ===========================================================================
G_PHI_PSI_DEFAULT = 0.1          # matter-field coupling constant (dimensionless)
KAPPA_DEFAULT = 0.05             # default decoherence rate (s^-1)
KAPPA_HEALTHY_RANGE = (0.01, 0.05)
KAPPA_DEMYELINATED_RANGE = (0.1, 1.0)
PSI_SQUARED_DEFAULT = 1.0       # |Psi|^2 for healthy active tissue
PHI_AMBIENT_DEFAULT = 1.0       # ambient Phi field strength
LAMBDA_CRITICAL = 0.3           # below this, function degrades
LAMBDA_SS_HEALTHY = 2.0         # steady-state for healthy tissue

# Phase coherence dynamics (dC/dt = alpha*I - beta*C + gamma*nabla^2 C)
ALPHA_COHERENCE_INPUT = 0.08
BETA_COHERENCE_DECAY = 0.04
GAMMA_SPATIAL_PROPAGATION = 0.02

# ===========================================================================
# Network coherence parameters
# ===========================================================================
TYPICAL_AXON_COUNT = 1000        # axons in a small nerve bundle
COUPLING_RANGE = 5e-6            # m, inter-axon photonic coupling range
PHASE_COUPLING_K = 0.01          # Kuramoto coupling strength

# ===========================================================================
# Molecular generation (ROS cascade) — extended rate constants
# ===========================================================================
K_LH = 5e8                      # OH. + PUFA H-abstraction
K_RUSSELL = 1e7                  # Russell mechanism 2 LOO. -> products
K_PROP = 50.0                   # LOO. propagation
K_O2_LIPID = 3e8                # L. + O2 -> LOO.

# Steady-state concentrations (M, in neural tissue)
CONC_SOD = 1e-5                 # ~10 uM
CONC_FE2 = 1e-6                # ~1 uM labile iron
CONC_LH = 1e-2                 # ~10 mM PUFA in membranes (effective)
CONC_O2 = 30e-6                # ~30 uM dissolved O2

# Electron transport chain leakage
J_LEAK_FRACTION = 0.01          # 1% of O2 consumption leaks as superoxide
O2_CONSUMPTION_RATE = 1e-4      # mol/s per gram mitochondria

# ===========================================================================
# Biophoton wavelength range (extended)
# ===========================================================================
BIOPHOTON_RATE_NEURAL = 100.0   # typical neural tissue UPE (photons/cm^2/s)
BIOPHOTON_WAVELENGTH_PEAK_NM = 865.0   # near-IR peak in neural tissue
BIOPHOTON_WAVELENGTH_RANGE_NM = (300.0, 900.0)

# ===========================================================================
# Waveguide-specific parameters (from track-06)
# ===========================================================================
JUNCTION_LOSS_DB_TYPICAL = 6.0   # scattering loss per fragmentation boundary
ALPHA_0_DB_PER_MM = 0.5          # intrinsic propagation loss in healthy myelin
HEALTHY_OPERATING_WAVELENGTH_NM = 612.0   # for ~30-layer myelin
WAVEGUIDE_BANDWIDTH_NM = 10.0            # narrow bandwidth per Zeng et al.

# ===========================================================================
# Bayesian Updating parameters (QTrainerAI / Scott directives)
# ===========================================================================
BU_INITIAL_PRIOR = 0.51         # Scott directive: 0.51, NOT 0.515
BU_LIKELIHOOD_SR = 0.515        # success rate per observation
BU_OBS_HIT = 1
BU_OBS_MISS = 0

QTRAINER_METHODS = [
    "mv", "rwba", "ac1", "ac2", "ra1", "ra2", "ra3", "ra4", "ra5",
    "ca7", "ca15", "ca23", "lzt", "ks", "m2", "m3", "m4",
]
N_QTRAINER_METHODS = len(QTRAINER_METHODS)
METHOD_CALIBRATIONS = {m: 1.0 for m in QTRAINER_METHODS}
QRNG_ODD_CHANNELS = [1, 3, 7, 13, 23, 47, 95, 127]

# ===========================================================================
# QFT / MMI device parameters (track-08)
# ===========================================================================
G_EFF_CCF_DEFAULT = 0.05         # effective CCF circuit coupling
E_CCF_DEFAULT = 1.0              # CCF activation level
KAPPA_ENV_DEFAULT = 0.1          # environmental decoherence for QFT device
RESPONSIVITY_BASELINE = 0.50     # chance level
RESPONSIVITY_TYPICAL = 0.515     # observed in active MMI sessions
RESPONSIVITY_HIGH = 0.53         # optimized conditions

# ===========================================================================
# Simulation defaults
# ===========================================================================
DEFAULT_N_TRIALS = 1000
DEFAULT_N_SUBTRIALS = 96
DEFAULT_DT = 0.01               # seconds
DEFAULT_T_MAX = 100.0           # seconds
RNG_SEED = 42
