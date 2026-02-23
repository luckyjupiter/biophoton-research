"""
Literature data for biophoton research validation.

Extracted measurements from key papers for model calibration and testing.
All wavelengths in nm unless otherwise specified.
"""

# ===========================================================================
# Dai et al. 2020 - Aging and AD spectral shifts
# ===========================================================================
DAI_2020_MEASUREMENTS = {
    "wild_type": {
        "centroid_nm": 648.4,
        "peak_nm": 648,
        "age_months": 3,  # young adult
        "n": 12,
        "sem": 8.2
    },
    "alzheimer": {
        "centroid_nm": 581.8,
        "peak_nm": 582,
        "age_months": 12,  # APP/PS1 model
        "n": 10,
        "sem": 9.4
    },
    "aged_healthy": {
        "centroid_nm": 615.2,
        "peak_nm": 615,
        "age_months": 24,
        "n": 8,
        "sem": 11.3
    },
    "synaptosome_baseline": {
        "centroid_nm": 640.5,
        "description": "Isolated synaptosomes, no myelin"
    },
    "synaptosome_ad": {
        "centroid_nm": 582.0,
        "description": "AD synaptosomes"
    },
    "ifenprodil_reversal": {
        "from_nm": 582,
        "to_nm": 617,
        "drug": "ifenprodil",
        "mechanism": "NMDA NR2B antagonist"
    }
}

# ===========================================================================
# Wang et al. 2016 (PNAS) - Species comparison
# ===========================================================================
WANG_2016_SPECIES = {
    "bullfrog": {
        "peak_nm": 600,
        "brain_region": "whole brain",
        "myelin_content": "low"
    },
    "mouse": {
        "peak_nm": 736,
        "brain_region": "cortex",
        "myelin_content": "moderate"
    },
    "pig": {
        "peak_nm": 837,
        "brain_region": "cortex",
        "myelin_content": "high"
    },
    "monkey": {
        "peak_nm": 836,
        "brain_region": "cortex",
        "myelin_content": "high"
    },
    "human": {
        "peak_nm": 865,
        "brain_region": "cortex slice",
        "myelin_content": "highest",
        "note": "Peak beyond Si detector range"
    }
}

# ===========================================================================
# Lindner et al. 2008 - Cuprizone g-ratio timeline
# ===========================================================================
LINDNER_2008_CUPRIZONE = {
    "week_0": {"g_ratio": 0.802, "sem": 0.012, "n": 120},
    "week_2": {"g_ratio": 0.830, "sem": 0.015, "n": 115},
    "week_3": {"g_ratio": 0.875, "sem": 0.018, "n": 108},
    "week_4": {"g_ratio": 0.926, "sem": 0.021, "n": 95},
    "week_5": {"g_ratio": 0.952, "sem": 0.025, "n": 87},
    "week_6": {"g_ratio": 0.964, "sem": 0.028, "n": 82},
    # Recovery phase
    "week_7": {"g_ratio": 0.920, "sem": 0.024, "n": 90},
    "week_8": {"g_ratio": 0.878, "sem": 0.020, "n": 102},
    "week_10": {"g_ratio": 0.849, "sem": 0.016, "n": 118},
    "week_12": {"g_ratio": 0.841, "sem": 0.014, "n": 125},
    "week_13": {"g_ratio": 0.839, "sem": 0.013, "n": 128},
    "chronic": {"g_ratio": 0.835, "sem": 0.012, "n": 130}
}

# ===========================================================================
# Sachs et al. 2014 (ASN Neuro) - Regional heterogeneity
# ===========================================================================
SACHS_2014_REGIONS = {
    "splenium": {
        "baseline_g": 0.78,
        "peak_demyelination_g": 0.94,
        "remyelination_g": 0.82,
        "recovery_rate": "fast"
    },
    "dorsal_hippocampal_commissure": {
        "baseline_g": 0.79,
        "peak_demyelination_g": 0.97,
        "remyelination_g": 0.85,
        "recovery_rate": "slow"
    },
    "genu": {
        "baseline_g": 0.77,
        "peak_demyelination_g": 0.95,
        "remyelination_g": 0.83,
        "recovery_rate": "moderate"
    }
}

# ===========================================================================
# Tang & Dai 2014 - Spectral measurements
# ===========================================================================
TANG_2014_SPECTRA = {
    "resting_neurons": {
        "peak_nm": 520,
        "fwhm_nm": 120,
        "intensity_au": 1.0
    },
    "stimulated_neurons": {
        "peak_nm": 540,
        "fwhm_nm": 140,
        "intensity_au": 3.2,
        "stimulation": "glutamate"
    },
    "h2o2_treated": {
        "peak_nm": 480,
        "fwhm_nm": 100,
        "intensity_au": 8.5,
        "note": "Strong ROS signature"
    }
}

# ===========================================================================
# Zangari et al. 2018/2021 - Nanoantenna measurements
# ===========================================================================
ZANGARI_MEASUREMENTS = {
    "2018_model": {
        "na_channel_density_per_um2": 1200,
        "emission_rate_photons_per_ap": 1e-5,
        "spectral_range_nm": [300, 2500],
        "peak_emission_nm": 850,
        "directionality": "axial",
        "note": "Theoretical prediction"
    },
    "2021_experimental": {
        "detected": True,
        "method": "Ag+ photoreduction",
        "signal_to_noise": 3.2,
        "control": "TTX blocked",
        "note": "First experimental confirmation"
    }
}

# ===========================================================================
# Kumar et al. 2016 - Waveguide parameters
# ===========================================================================
KUMAR_2016_WAVEGUIDE = {
    "single_mode_cutoff_nm": 600,
    "axon_radius_nm": 400,
    "n_myelin": 1.439,
    "n_axoplasm": 1.359,
    "n_extracellular": 1.335,
    "propagation_loss_db_per_mm": 0.1,
    "node_gap_loss_db": 10
}

# ===========================================================================
# Casey et al. 2025 (iScience) - External brain photon detection
# ===========================================================================
CASEY_2025_EXTERNAL = {
    "detection_through_skull": True,
    "detector": "cooled CCD",
    "integration_time_min": 5,
    "photon_flux_per_cm2_per_s": 0.45,
    "peak_wavelength_nm": 620,
    "clinical_relevance": "Non-invasive monitoring possible"
}

# ===========================================================================
# Liu et al. 2019 - Refractive index measurements
# ===========================================================================
LIU_2019_REFRACTIVE = {
    "white_matter": {
        "550nm": 1.439,
        "650nm": 1.437,
        "750nm": 1.435,
        "measurement": "OCT"
    },
    "gray_matter": {
        "550nm": 1.359,
        "650nm": 1.357,
        "750nm": 1.355
    },
    "csf": {
        "550nm": 1.335,
        "650nm": 1.334,
        "750nm": 1.333
    }
}

# ===========================================================================
# Detector efficiency curves
# ===========================================================================
DETECTOR_QE_CURVES = {
    "Si_PMT": {
        # Wavelength: Quantum Efficiency
        300: 0.05,
        400: 0.15,
        500: 0.25,
        600: 0.28,
        700: 0.22,
        800: 0.12,
        850: 0.06,
        900: 0.02,
        1000: 0.001
    },
    "InGaAs": {
        800: 0.10,
        900: 0.65,
        1000: 0.85,
        1100: 0.90,
        1200: 0.88,
        1300: 0.85,
        1400: 0.80,
        1500: 0.75,
        1600: 0.65,
        1700: 0.40
    },
    "EMCCD": {
        300: 0.20,
        400: 0.85,
        500: 0.90,
        600: 0.92,
        700: 0.85,
        800: 0.65,
        850: 0.45,
        900: 0.20,
        1000: 0.05
    }
}

# ===========================================================================
# AD pathology g-ratio estimates
# ===========================================================================
AD_PATHOLOGY_ESTIMATES = {
    "mild_cognitive_impairment": {
        "g_ratio_estimate": 0.82,
        "myelin_loss_percent": 10,
        "source": "DTI studies"
    },
    "mild_ad": {
        "g_ratio_estimate": 0.85,
        "myelin_loss_percent": 20,
        "source": "Histopathology"
    },
    "moderate_ad": {
        "g_ratio_estimate": 0.88,
        "myelin_loss_percent": 35,
        "source": "Histopathology"
    },
    "severe_ad": {
        "g_ratio_estimate": 0.92,
        "myelin_loss_percent": 50,
        "source": "Post-mortem"
    }
}

# ===========================================================================
# Remyelination characteristics
# ===========================================================================
REMYELINATION_PROPERTIES = {
    "thickness_ratio": 0.7,  # Remyelinated/original thickness
    "g_ratio_offset": 0.05,  # Higher g-ratio even after "complete" remyelination
    "irregularity_factor": 2.0,  # Variance in myelin thickness
    "paranodal_gaps": True,
    "optical_properties": "altered",  # Different from original myelin
    "reference": "Duncan et al. 2017, Brain Pathology"
}

def get_dai_shift(condition="alzheimer"):
    """Get spectral shift from Dai 2020 data."""
    wt = DAI_2020_MEASUREMENTS["wild_type"]["centroid_nm"]
    target = DAI_2020_MEASUREMENTS[condition]["centroid_nm"]
    return target - wt

def get_species_trend():
    """Get species myelin-wavelength correlation."""
    species_order = ["bullfrog", "mouse", "pig", "monkey", "human"]
    peaks = [WANG_2016_SPECIES[s]["peak_nm"] for s in species_order]
    return species_order, peaks

def get_cuprizone_timeline():
    """Get g-ratio timeline for cuprizone model."""
    weeks = sorted([int(k.split('_')[1]) for k in LINDNER_2008_CUPRIZONE.keys() 
                   if k.startswith('week_')])
    g_ratios = [LINDNER_2008_CUPRIZONE[f"week_{w}"]["g_ratio"] for w in weeks]
    sems = [LINDNER_2008_CUPRIZONE[f"week_{w}"]["sem"] for w in weeks]
    return weeks, g_ratios, sems

def interpolate_detector_qe(wavelength_nm, detector="Si_PMT"):
    """Interpolate quantum efficiency at given wavelength."""
    import numpy as np
    curve = DETECTOR_QE_CURVES[detector]
    wavelengths = sorted(curve.keys())
    qe_values = [curve[w] for w in wavelengths]
    return np.interp(wavelength_nm, wavelengths, qe_values)