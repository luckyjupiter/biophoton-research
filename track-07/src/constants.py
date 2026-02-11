"""Physical constants and default parameters for the unified model."""

import numpy as np

# --- Fundamental constants ---
HBAR = 1.0546e-34       # J·s
C_LIGHT = 3.0e8          # m/s
K_B = 1.381e-23          # J/K
BODY_TEMP = 310.0         # K (37°C)

# --- Biophoton wavelength range ---
LAMBDA_MIN = 350e-9       # m (UV edge)
LAMBDA_MAX = 700e-9       # m (red edge)
LAMBDA_PEAK = 520e-9      # m (green, typical biophoton peak)

# --- Scale 1: Molecular generation (ROS cascade) ---
# ETC leakage
J_LEAK_FRACTION = 0.01    # 1% of O2 consumption leaks as superoxide
O2_CONSUMPTION_RATE = 1e-4  # mol/s per gram mitochondria (order of magnitude)

# Enzyme rates (M^-1 s^-1)
K_SOD = 2e9               # superoxide dismutase
K_CAT = 1e7               # catalase
K_FENTON = 76.0           # Fe2+ + H2O2 -> OH. + OH- + Fe3+
K_LH = 5e8               # OH. + PUFA H-abstraction
K_RUSSELL = 1e7           # Russell mechanism 2 LOO. -> products
K_PROP = 50.0             # LOO. propagation
K_O2_LIPID = 3e8          # L. + O2 -> LOO.

# Quantum yields
PHI_TRIPLET = 0.01        # triplet carbonyl yield from Russell mechanism
PHI_SINGLET_O2 = 0.005    # singlet oxygen yield
PHI_RADIATIVE_TRIPLET = 1e-9  # radiative yield of triplet carbonyl
PHI_RADIATIVE_SINGLET = 1e-7  # radiative yield of singlet oxygen (1270nm)

# Steady-state concentrations (M, in neural tissue)
CONC_SOD = 1e-5           # ~10 uM
CONC_FE2 = 1e-6           # ~1 uM labile iron
CONC_LH = 1e-2            # ~10 mM PUFA in membranes (effective)
CONC_O2 = 30e-6           # ~30 uM dissolved O2

# --- Scale 2: Waveguide transport ---
# Myelin geometry
AXON_RADIUS = 0.5e-6      # m (0.5 um, small myelinated axon)
MYELIN_THICKNESS = 1.0e-6  # m (wraps, total ~1 um)
G_RATIO = 0.7              # axon_radius / (axon_radius + myelin_thickness)
LAMELLA_THICKNESS = 12e-9  # m (single lipid bilayer + water layer)
N_LAMELLAE = 80            # typical wrap count

# Refractive indices at ~520nm
N_AXOPLASM = 1.36
N_MYELIN_LIPID = 1.46
N_MYELIN_WATER = 1.34
N_EXTRACELLULAR = 1.335

# Absorption coefficient in myelin (m^-1)
ALPHA_MYELIN = 100.0       # order of magnitude for lipid absorption at 520nm

# Internode length and node properties
INTERNODE_LENGTH = 500e-6  # m (500 um between nodes of Ranvier)
NODE_TRANSMISSION = 0.3    # fraction transmitted through a node gap

# --- Scale 3: Network coherence ---
# M-Phi framework parameters
G_PHI_PSI = 1e-3           # matter-field coupling (dimensionless, normalized)
KAPPA_BASE = 0.1            # base decoherence rate (s^-1)
PSI_SQUARED = 1.0           # normalized matter field density for active tissue

# Network topology
TYPICAL_AXON_COUNT = 1000   # axons in a small nerve bundle
COUPLING_RANGE = 5e-6       # m, inter-axon photonic coupling range
PHASE_COUPLING_K = 0.01     # Kuramoto coupling strength

# --- Derived quantities ---
PHOTON_ENERGY_520NM = HBAR * 2 * np.pi * C_LIGHT / LAMBDA_PEAK  # ~3.8e-19 J
