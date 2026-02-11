"""
Physical constants and parameters for demyelination-biophoton modeling.

All values sourced from Track 03 waveguide analysis, Track 06 pathology document,
and the published literature cited therein.

Notation follows project conventions:
  Lambda, Phi  -- coherence/information field
  g_PhiPsi     -- matter-field coupling constant
  kappa        -- decoherence rate
  Psi          -- matter field amplitude
"""

import numpy as np

# ---------------------------------------------------------------------------
# Refractive indices (dimensionless)
# ---------------------------------------------------------------------------
N_MYELIN: float = 1.44       # compact myelin lamellae
N_AXOPLASM: float = 1.38     # axon interior
N_ECF: float = 1.34          # extracellular / interstitial fluid

# Numerical apertures
NA_MYELIN_AXON: float = float(np.sqrt(N_MYELIN**2 - N_AXOPLASM**2))   # ~0.411
NA_MYELIN_ECF: float = float(np.sqrt(N_MYELIN**2 - N_ECF**2))         # ~0.527
NA_BARE_AXON: float = float(np.sqrt(N_AXOPLASM**2 - N_ECF**2))        # ~0.330

# ---------------------------------------------------------------------------
# Myelin geometry
# ---------------------------------------------------------------------------
BILAYER_THICKNESS_NM: float = 14.5      # single bilayer repeat distance (nm), range 12-17
G_RATIO_HEALTHY: float = 0.70           # typical healthy CNS g-ratio
INTERNODE_LENGTH_UM: float = 300.0      # typical internode length (um)
AXON_RADIUS_UM: float = 1.0            # typical axon radius (um)
OUTER_RADIUS_UM: float = AXON_RADIUS_UM / G_RATIO_HEALTHY  # ~1.43 um

# Derived: number of myelin wraps in healthy sheath
MYELIN_THICKNESS_UM: float = OUTER_RADIUS_UM - AXON_RADIUS_UM
N_LAYERS_HEALTHY: int = int(round(MYELIN_THICKNESS_UM * 1000 / BILAYER_THICKNESS_NM))  # ~30

# ---------------------------------------------------------------------------
# Waveguide-optics parameters
# ---------------------------------------------------------------------------
WAVELENGTH_SHIFT_PER_LAYER_NM: float = 52.3   # Zeng et al. 2022
HEALTHY_OPERATING_WAVELENGTH_NM: float = 612.0  # approximate for ~30-layer myelin
WAVEGUIDE_BANDWIDTH_NM: float = 10.0           # narrow bandwidth per Zeng et al.

# Junction scattering loss at each fragmentation boundary (dB)
JUNCTION_LOSS_DB_LOW: float = 3.0
JUNCTION_LOSS_DB_HIGH: float = 10.0
JUNCTION_LOSS_DB_TYPICAL: float = 6.0   # geometric mean

# Intrinsic propagation loss in healthy myelin (dB/mm)
ALPHA_0_DB_PER_MM: float = 0.5   # estimated, low-loss regime

# ---------------------------------------------------------------------------
# Coherence-field (M-Phi framework) parameters
# ---------------------------------------------------------------------------
# dLambda/dt = g * |Psi|^2 * Phi  -  kappa * Lambda
G_PHI_PSI: float = 1.0e-3          # matter-field coupling (arbitrary units)
PSI_AMPLITUDE: float = 1.0         # normalised matter-field amplitude
KAPPA_HEALTHY: float = 0.05        # baseline decoherence rate (s^-1) in healthy myelin

# ---------------------------------------------------------------------------
# Oxidative-stress photon emission parameters
# ---------------------------------------------------------------------------
SINGLET_O2_MONOMOL_PEAKS_NM: list = [634.0, 703.0]
SINGLET_O2_DIMOL_PEAKS_NM: list = [478.0, 534.0, 634.0]
SINGLET_O2_NIR_NM: float = 1270.0
TRIPLET_CARBONYL_RANGE_NM: tuple = (350.0, 550.0)
EXCITED_PIGMENT_RANGE_NM: tuple = (550.0, 750.0)

# Baseline biophoton emission rate (photons / s / cm^2 tissue surface)
BASAL_EMISSION_RATE: float = 10.0   # order-of-magnitude, ultra-weak regime

# Inflammatory amplification factors
INFLAMMATORY_EMISSION_FACTOR_LOW: float = 10.0
INFLAMMATORY_EMISSION_FACTOR_HIGH: float = 100.0

# ---------------------------------------------------------------------------
# Disease-specific timescales
# ---------------------------------------------------------------------------
# EAE (MOG-induced in C57BL/6)
EAE_ONSET_DAY: int = 10
EAE_PEAK_DAY: int = 16
EAE_CHRONIC_DAY: int = 28

# Cuprizone model (weeks)
CUPRIZONE_DEMYELINATION_WEEKS: int = 6
CUPRIZONE_REMYELINATION_START_WEEK: int = 7
CUPRIZONE_REMYELINATION_END_WEEK: int = 12

# Wallerian degeneration PNS (days)
WALLERIAN_MYELIN_FRAGMENTATION_DAY: float = 3.0
WALLERIAN_CLEARANCE_COMPLETE_DAY: float = 21.0

# LPC focal lesion (days)
LPC_DEMYELINATION_PEAK_DAY: float = 3.0
LPC_REMYELINATION_COMPLETE_DAY: float = 21.0

# ---------------------------------------------------------------------------
# MS subtype parameters
# ---------------------------------------------------------------------------
RRMS_RELAPSE_RATE_PER_YEAR: float = 1.0
RRMS_RELAPSE_DURATION_WEEKS: float = 6.0
RRMS_RECOVERY_FRACTION: float = 0.85

SPMS_ANNUAL_MYELIN_LOSS_FRACTION: float = 0.03
SPMS_INFLAMMATION_LEVEL: float = 0.3

PPMS_ANNUAL_MYELIN_LOSS_FRACTION: float = 0.04
PPMS_INFLAMMATION_LEVEL: float = 0.2

# ---------------------------------------------------------------------------
# Kappa subcomponents (decoherence contributors)
# ---------------------------------------------------------------------------
KAPPA_THERMAL: float = 0.02       # thermal fluctuations at 37 C
KAPPA_STRUCTURAL: float = 0.01    # baseline structural disorder
KAPPA_ROS_HEALTHY: float = 0.01   # basal ROS in healthy tissue
KAPPA_INFLAMMATORY: float = 0.01  # no inflammation in healthy tissue
# Sum = KAPPA_HEALTHY = 0.05

# ---------------------------------------------------------------------------
# Diagnostic / ROC parameters
# ---------------------------------------------------------------------------
MEASUREMENT_INTEGRATION_TIME_S: float = 3600.0   # 1 hour
DETECTOR_DARK_COUNT_RATE: float = 0.5             # counts/s (cooled EM-CCD)
DETECTOR_QE: float = 0.90                         # quantum efficiency at 500-700 nm

# ---------------------------------------------------------------------------
# Dose-response (Hill equation) parameters
# ---------------------------------------------------------------------------
HILL_K_EMISSION: float = 0.20     # EC50 at 20% demyelination
HILL_N_EMISSION: float = 2.0
HILL_K_SPECTRAL: float = 0.50
HILL_N_SPECTRAL: float = 1.0
HILL_K_RATIO: float = 0.07
HILL_N_RATIO: float = 3.0
