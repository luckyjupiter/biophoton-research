"""
Physical constants and parameters for biophoton demyelination modeling.

Sources:
- Refractive indices: Sun et al. (2012) J Biomed Opt; Binding et al. (2011) Cytometry A
- Myelin dimensions: Waxman & Bangalore (1992); Chomiak & Bhairavnath (2009)
- ROS emission: Cifra & Pospíšil (2014) J Photochem Photobiol B
- Biophoton baseline: Kobayashi et al. (2009) J Photochem Photobiol B
- Detector specs: Hadfield (2009) Nature Photonics; Hamamatsu PMT handbook
"""

import numpy as np

# --- Refractive indices ---
N_MYELIN = 1.44       # compact myelin sheath (lipid-rich)
N_AXON = 1.38         # axoplasm (cytoplasm-like)
N_ECF = 1.34          # extracellular fluid
N_VACUUM = 1.0

# --- Myelin geometry ---
LIPID_BILAYER_THICKNESS_NM = 10.0    # single myelin wrap ~10 nm
LIPID_BILAYER_THICKNESS_M = 10e-9

# --- Wavelength range (nm) ---
LAMBDA_MIN_NM = 200
LAMBDA_MAX_NM = 950
DEFAULT_LAMBDA_RANGE_NM = np.linspace(LAMBDA_MIN_NM, LAMBDA_MAX_NM, 751)

# --- ROS spectral components ---
# Each entry: (center_nm, fwhm_nm, relative_amplitude, species)
ROS_COMPONENTS = [
    (380, 60, 0.15, "lipid peroxidation (dioxetane)"),
    (460, 80, 0.25, "excited carbonyl"),
    (535, 50, 0.20, "singlet O2 dimol (1Δg+1Δg)"),
    (580, 40, 0.10, "excited carbonyl tail"),
    (634, 15, 0.08, "singlet O2 (1Δg→3Σg) 0-1"),
    (703, 15, 0.07, "singlet O2 (1Δg→3Σg) 0-0"),
    (760, 20, 0.05, "singlet O2 dimol 2×703"),
]

# --- Baseline emission ---
BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S = 100.0   # ~1-1000 typical range

# --- Absorption/scattering in neural tissue ---
ABSORPTION_COEFF_PER_CM = 2.0       # approximate tissue absorption at ~500 nm
SCATTER_COEFF_PER_CM = 10.0         # Rayleigh + Mie scattering
BEND_LOSS_PER_CM = 1.0              # bending losses in curved axons
# Total attenuation: 4–40 dB/cm depending on wavelength and geometry

# --- Spectral tuning coefficients (Sefati/Zeng model) ---
SPECTRAL_SHIFT_PER_LAYER_NM = 52.3          # +52.3 nm per myelin wrap
SPECTRAL_SHIFT_PER_UM_DIAMETER_NM = -94.5   # -94.5 nm per μm axon diameter

# --- Detector specifications ---
DETECTOR_SPECS = {
    "PMT": {
        "dark_rate_hz": 30.0,
        "quantum_efficiency": 0.25,
        "timing_jitter_ns": 0.3,
        "description": "Photomultiplier tube (e.g. Hamamatsu H7421-40)",
    },
    "EMCCD": {
        "dark_rate_hz": 0.001,   # cooled EM-CCD, per pixel
        "quantum_efficiency": 0.90,
        "timing_jitter_ns": None,  # frame-based, not single-photon
        "description": "Electron-multiplying CCD (e.g. Andor iXon)",
    },
    "SPAD": {
        "dark_rate_hz": 25.0,
        "quantum_efficiency": 0.50,
        "timing_jitter_ns": 0.05,
        "description": "Single-photon avalanche diode",
    },
    "SNSPD": {
        "dark_rate_hz": 0.01,
        "quantum_efficiency": 0.93,
        "timing_jitter_ns": 0.003,
        "description": "Superconducting nanowire (cryogenic)",
    },
}

# --- Hill equation defaults ---
HILL_COEFFICIENT_DEFAULT = 3.0   # cooperative binding/damage sigmoid
HILL_K_HALF_DEFAULT = 0.5       # half-maximal effect at 50% damage
