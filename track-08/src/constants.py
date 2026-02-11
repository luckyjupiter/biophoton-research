"""
Shared physical, statistical, and framework constants for Track 08.

Sources:
- M-Phi framework: Kruger, Feeney, Duarte (2023) "Physical Basis of Coherence"
- QTrainerAI BU parameters: Scott's directives (Jan-Feb 2026)
- Biophoton rates: Cifra & Pospisil (2014), Casey et al. (2025)
- Detector specs: inherited from models/constants.py
- Myelin parameters: Kumar et al. (2016), Liu et al. (2019)
"""

import numpy as np
from typing import Dict, List, Tuple

# ============================================================================
# Bayesian Updating Parameters (from QTrainerAI / Scott directives)
# ============================================================================

INITIAL_PRIOR: float = 0.51
"""Initial prior probability for BU. Scott directive: 0.51, NOT 0.515."""

LIKELIHOOD_SR: float = 0.515
"""Likelihood (success rate) per observation. Scott directive: 0.515."""

BU_OBS_HIT: int = 1
"""Observation code for a hit (positive outcome)."""

BU_OBS_MISS: int = 0
"""Observation code for a miss (negative outcome)."""

# ============================================================================
# QTrainerAI 17-Method Suite
# ============================================================================

QTRAINER_METHODS: List[str] = [
    "mv",    # Majority Vote
    "rwba",  # Random Walk Bias Amplification
    "ac1",   # Autocorrelation lag-1
    "ac2",   # Autocorrelation lag-2
    "ra1",   # Running Average window 1
    "ra2",   # Running Average window 2
    "ra3",   # Running Average window 3
    "ra4",   # Running Average window 4
    "ra5",   # Running Average window 5
    "ca7",   # Cumulative Advantage window 7
    "ca15",  # Cumulative Advantage window 15
    "ca23",  # Cumulative Advantage window 23
    "lzt",   # Lempel-Ziv complexity Test
    "ks",    # Kolmogorov-Smirnov test
    "m2",    # Method 2 (higher-order)
    "m3",    # Method 3 (higher-order)
    "m4",    # Method 4 (higher-order)
]
"""All 17 QTrainerAI methods. Scott: no exclusions, all methods in Combined BU."""

N_METHODS: int = len(QTRAINER_METHODS)
"""Number of methods in the QTrainerAI combined BU framework."""

# Per-method calibration weights (Scott Feb 1 2026: "Please make all 1.0")
METHOD_CALIBRATIONS: Dict[str, float] = {m: 1.0 for m in QTRAINER_METHODS}

# QRNG odd channels (for multi-channel streaming)
QRNG_ODD_CHANNELS: List[int] = [1, 3, 7, 13, 23, 47, 95, 127]

# ============================================================================
# M-Phi Framework Parameters
# ============================================================================

G_PHI_PSI_DEFAULT: float = 0.1
"""Default matter-field coupling constant g_{Phi Psi} (dimensionless).
   This is a free parameter of the M-Phi framework; 0.1 is a working estimate
   calibrated so that steady-state Lambda falls in biologically plausible range."""

KAPPA_DEFAULT: float = 0.05
"""Default decoherence rate kappa (s^{-1}).
   Represents thermal noise, inflammatory load, oxidative stress.
   Healthy myelin: ~0.01-0.05; demyelinated: 0.1-1.0."""

KAPPA_HEALTHY_RANGE: Tuple[float, float] = (0.01, 0.05)
"""Decoherence rate range for healthy myelinated tissue."""

KAPPA_DEMYELINATED_RANGE: Tuple[float, float] = (0.1, 1.0)
"""Decoherence rate range for demyelinated tissue."""

PSI_SQUARED_DEFAULT: float = 1.0
"""|Psi|^2: matter field amplitude squared. Normalized to 1.0 for healthy
   metabolically active tissue. Decreases with metabolic stress."""

PHI_AMBIENT_DEFAULT: float = 1.0
"""Ambient Phi field strength. Normalized to 1.0 for standard conditions."""

# ============================================================================
# Coherence Thresholds
# ============================================================================

LAMBDA_CRITICAL: float = 0.3
"""Critical coherence threshold Lambda_c. Below this, stable conscious
   function degrades. From M-Phi framework analysis."""

LAMBDA_SS_HEALTHY: float = 2.0
"""Approximate steady-state coherence for healthy tissue:
   Lambda_ss = (g/kappa) * |Psi|^2 * Phi = (0.1/0.05) * 1.0 * 1.0 = 2.0"""

# ============================================================================
# Phase Coherence Dynamics
# ============================================================================

ALPHA_COHERENCE_INPUT: float = 0.08
"""Sensitivity to coherent input in dC/dt = alpha*I - beta*C + gamma*nabla^2 C."""

BETA_COHERENCE_DECAY: float = 0.04
"""Coherence decay rate in the phase-constraint manifold dynamics."""

GAMMA_SPATIAL_PROPAGATION: float = 0.02
"""Spatial propagation coefficient for coherence diffusion."""

# ============================================================================
# Biophoton Physical Constants
# ============================================================================

BIOPHOTON_RATE_LOW: float = 1.0
"""Lower bound of typical UPE: 1 photon/cm^2/s."""

BIOPHOTON_RATE_HIGH: float = 1000.0
"""Upper bound of typical UPE: 1000 photons/cm^2/s."""

BIOPHOTON_RATE_NEURAL: float = 100.0
"""Typical neural tissue UPE rate: ~100 photons/cm^2/s (Casey et al. 2025)."""

BIOPHOTON_WAVELENGTH_PEAK_NM: float = 865.0
"""Peak biophoton wavelength in human neural tissue (Wang et al. 2016 PNAS)."""

BIOPHOTON_WAVELENGTH_RANGE_NM: Tuple[float, float] = (300.0, 900.0)
"""Broadband UPE emission range."""

# ============================================================================
# Myelin Waveguide Parameters (from models/constants.py, repeated for clarity)
# ============================================================================

N_MYELIN: float = 1.44
"""Refractive index of compact myelin sheath."""

N_AXON: float = 1.38
"""Refractive index of axoplasm."""

N_ECF: float = 1.34
"""Refractive index of extracellular fluid."""

G_RATIO_OPTIMAL: float = 0.65
"""Optimal g-ratio (inner/outer radius) for myelin waveguide, range 0.6-0.7."""

SPECTRAL_SHIFT_PER_LAYER_NM: float = 52.3
"""Wavelength shift per myelin wrap (Zeng et al. 2022)."""

# ============================================================================
# Detector Specifications (for experimental protocol design)
# ============================================================================

DETECTOR_DARK_RATE_PMT_HZ: float = 30.0
"""PMT dark count rate (Hamamatsu H7421-40)."""

DETECTOR_QE_PMT: float = 0.25
"""PMT quantum efficiency at ~500 nm."""

DETECTOR_DARK_RATE_SPAD_HZ: float = 25.0
"""SPAD dark count rate."""

DETECTOR_QE_SPAD: float = 0.50
"""SPAD quantum efficiency."""

DETECTOR_DARK_RATE_SNSPD_HZ: float = 0.01
"""SNSPD dark count rate (cryogenic)."""

DETECTOR_QE_SNSPD: float = 0.93
"""SNSPD quantum efficiency."""

# ============================================================================
# Statistical Constants
# ============================================================================

Z_SCORE_95: float = 1.645
"""One-tailed z-score for 95% confidence."""

Z_SCORE_99: float = 2.326
"""One-tailed z-score for 99% confidence."""

Z_SCORE_3SIGMA: float = 3.0
"""3-sigma threshold."""

Z_SCORE_5SIGMA: float = 5.0
"""5-sigma discovery threshold (particle physics convention)."""

# Abramowitz-Stegun CDF coefficients (matching QTrainerAI scott_cdf_z_score)
AS_CDF_C1: float = 2.506628275
AS_CDF_C7: float = 0.2316419
AS_CDF_C8: float = 0.319381530
AS_CDF_C9: float = -0.356563782
AS_CDF_C10: float = 1.781477937
AS_CDF_C11: float = -1.821255978
AS_CDF_C12: float = 1.330274429

# ============================================================================
# QFT Device Parameters (for cross-prediction modeling)
# ============================================================================

G_EFF_CCF_DEFAULT: float = 0.05
"""Effective coupling constant for CCF circuit (analogous to g_PhiPsi)."""

E_CCF_DEFAULT: float = 1.0
"""CCF circuit energy/activation level (analogous to |Psi|^2)."""

KAPPA_ENV_DEFAULT: float = 0.1
"""Environmental decoherence rate for QFT device."""

RESPONSIVITY_BASELINE: float = 0.50
"""Baseline responsivity (chance level, no coupling)."""

RESPONSIVITY_TYPICAL: float = 0.515
"""Typical observed responsivity in active MMI sessions."""

RESPONSIVITY_HIGH: float = 0.53
"""High responsivity observed in optimized conditions."""

# ============================================================================
# Simulation Defaults
# ============================================================================

DEFAULT_N_TRIALS: int = 1000
"""Default number of trials for simulations."""

DEFAULT_N_SUBTRIALS: int = 96
"""Default number of subtrials per trial (QTrainerAI standard)."""

DEFAULT_DT: float = 0.01
"""Default time step for ODE integration (seconds)."""

DEFAULT_T_MAX: float = 100.0
"""Default maximum simulation time (seconds)."""

RNG_SEED: int = 42
"""Default random seed for reproducible simulations."""
