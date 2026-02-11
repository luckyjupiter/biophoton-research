"""Physical constants and default parameters for the unified model.

Values updated with literature-backed measurements (Deep Research, Feb 2026).
Sources cited inline. Previous values noted where corrected.
"""

import numpy as np

# --- Fundamental constants ---
HBAR = 1.0546e-34        # J·s
C_LIGHT = 2.998e8         # m/s
K_B = 1.381e-23           # J/K
BODY_TEMP = 310.0          # K (37°C)

# --- Biophoton wavelength range ---
LAMBDA_MIN = 200e-9        # m (UV edge, Cifra & Pospisil full UPE range)
LAMBDA_MAX = 800e-9        # m (near-IR edge)
LAMBDA_PEAK = 520e-9       # m (green, typical biophoton peak)

# --- Scale 1: Molecular generation (ROS cascade) ---
# ETC leakage — Murphy 2009: physiological rate is ~0.15%, NOT 1-4% (in vitro artifact)
J_LEAK_FRACTION = 0.0015   # 0.15% of O2 consumption (was 0.01)
O2_CONSUMPTION_RATE = 1e-4  # mol/s per gram mitochondria (order of magnitude)

# Brain mitochondria H2O2 production (Kudin et al. 2004):
#   Basal (glu+mal): 0.04 nmol H2O2/min/mg protein
#   Complex I max (rotenone): 0.68 nmol/min/mg
#   Complex III max (antimycin A): 0.14 nmol/min/mg

# Enzyme rates (M^-1 s^-1)
K_SOD = 2e9                # superoxide dismutase (McCord & Fridovich 1969, confirmed)
K_CAT = 1e7                # catalase (Chance 1948, saturating)
K_FENTON = 76.0            # Fe2+ + H2O2 (Wardman & Candeias 1996, confirmed)
K_LH = 8e9                 # OH. + PUFA H-abstraction (Buxton 1988; was 5e8)
K_RUSSELL = 1e7            # Russell mechanism 2 LOO. -> products
K_O2_LIPID = 3e8           # L. + O2 -> LOO.

# Lipid peroxidation propagation rates — Pratt et al. 2011 (PMC3124811)
K_PROP = 334.0             # DHA (22:6), dominant brain PUFA (was 50.0)
K_PROP_LINOLEIC = 62.0     # Linoleic acid (18:2)
K_PROP_ARACHIDONIC = 197.0 # Arachidonic acid (20:4)
K_PROP_EPA = 249.0         # EPA (20:5)
K_PROP_DHA = 334.0         # DHA (22:6) — default for brain tissue
K_PROP_7DHC = 2260.0       # 7-dehydrocholesterol (Smith-Lemli-Opitz relevance)

# Quantum yields — updated with Pospisil 2014 (PMC6681336), Miyamoto 2003
PHI_TRIPLET = 0.03         # triplet carbonyl yield from Russell (was 0.01; range 1-5%)
PHI_SINGLET_O2 = 0.08      # singlet oxygen yield (was 0.005; Miyamoto: 3-14%, mean ~8%)
PHI_RADIATIVE_TRIPLET = 1e-3  # radiative branching ratio (was 1e-9; ~10^3 / 10^6 s^-1)
PHI_RADIATIVE_SINGLET = 1e-7  # singlet O2 monomol (1270nm) emission yield

# Overall per-reaction photon yield (visible range): ~3e-5 (Pospisil 2014)
PHI_PHOTON_PER_REACTION = 3e-5

# Steady-state concentrations (M, in neural tissue)
CONC_SOD = 1e-5            # ~10 uM
CONC_FE2 = 1e-6            # ~1 uM labile iron
CONC_LH = 1e-2             # ~10 mM PUFA in membranes (effective)
CONC_O2 = 30e-6            # ~30 uM dissolved O2

# Measured biophoton generation rates
RATE_GENERAL_TISSUE = 100.0      # photons/s/cm^2 (range: 1-1000, Cifra & Pospisil)
RATE_NEURAL_CELLS = 12.0         # photons/s (Neuro-2a cells, Bhatt 2025)
RATE_PER_NEURON = 1.0 / 60.0     # photons/s per neuron (~1/min, Tang & Dai 2014)
RATE_HUMAN_CHEEK_PEAK = 3000.0   # photons/s/cm^2 (Kobayashi 2009)

# --- Scale 2: Waveguide transport ---
# Myelin geometry (Kumar et al. 2016, Scientific Reports 6:36508)
AXON_RADIUS = 0.5e-6       # m (0.5 um, small myelinated axon)
MYELIN_THICKNESS = 1.0e-6   # m (wraps, total ~1 um)
G_RATIO = 0.7               # axon_radius / (axon_radius + myelin_thickness)
LAMELLA_THICKNESS = 12e-9   # m (single lipid bilayer + water layer)
N_LAMELLAE = 80             # typical wrap count

# Refractive indices — multi-source compilation
# See Track 03 deep research for full table
N_AXOPLASM = 1.38           # Kumar 2016 consensus (Antonov 1983: 1.34, Wang 2017: 1.358)
N_MYELIN_LIPID = 1.46       # De Campos Vidal 1980, Marangoni 2017 (Wang 2017 in vivo: 1.47)
N_MYELIN_WATER = 1.34
N_EXTRACELLULAR = 1.35      # Wang 2017 in vivo (was 1.335)

# Absorption coefficient in myelin (m^-1)
ALPHA_MYELIN = 100.0        # order of magnitude for lipid absorption at 520nm

# Internode length and node properties
INTERNODE_LENGTH = 500e-6   # m (500 um between nodes of Ranvier)
NODE_TRANSMISSION = 0.85    # at ARROW anti-resonance (was 0.3; Kumar 2016: 0.46-0.96)

# --- Scale 3: Network coherence ---
# M-Phi framework parameters
G_PHI_PSI = 1e-3            # matter-field coupling (dimensionless, normalized)
KAPPA_BASE = 0.1             # base decoherence rate (s^-1)
PSI_SQUARED = 1.0            # normalized matter field density for active tissue

# Network topology
TYPICAL_AXON_COUNT = 1000    # axons in a small nerve bundle
COUPLING_RANGE = 5e-6        # m, inter-axon photonic coupling range

# Kuramoto coupling — Sadilek & Thurner 2015
# Critical coupling K_c ~ 2*gamma (Lorentzian) or ~1.6*sigma (Gaussian)
# For gamma-band (30-80 Hz), sigma ~ 5-10 Hz -> K_c ~ 8-16 Hz
# Normalized: K_c/omega_0 ~ 0.2-0.4
PHASE_COUPLING_K = 0.3      # normalized (was 0.01; now near critical coupling)

# Zarkeshian et al. 2022 parameters (photonic neural network)
ZARKESHIAN_P_PHOTON = 0.01  # photon emission probability per event
ZARKESHIAN_ACCURACY_AT_001 = 0.91  # MNIST accuracy at p=0.01, 1000 hidden units
ZARKESHIAN_ACCURACY_AT_005 = 0.94  # at p=0.05
ZARKESHIAN_ACCURACY_AT_100 = 0.98  # at p=1.0 (standard backprop limit)

# --- Derived quantities ---
PHOTON_ENERGY_520NM = HBAR * 2 * np.pi * C_LIGHT / LAMBDA_PEAK  # ~3.8e-19 J
