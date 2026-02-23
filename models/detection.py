"""
Detector response functions for biophoton measurements.

Key insight: Most biophoton studies use Si-based detectors (PMT, EMCCD)
which have poor sensitivity above 850nm. Human brain peak is at 865nm.
This means we're missing ~50% of the signal!
"""

import numpy as np
try:
    from .literature_data import DETECTOR_QE_CURVES, interpolate_detector_qe
except ImportError:
    from literature_data import DETECTOR_QE_CURVES, interpolate_detector_qe

def detector_efficiency_curve(wavelength_nm, detector_type="Si_PMT"):
    """
    Get quantum efficiency curve for specified detector.
    
    Args:
        wavelength_nm: Single wavelength or array
        detector_type: "Si_PMT", "InGaAs", or "EMCCD"
    
    Returns:
        Quantum efficiency (0-1)
    """
    wavelength_nm = np.atleast_1d(wavelength_nm)
    
    # Interpolate from measured curves
    qe = np.array([interpolate_detector_qe(w, detector_type) for w in wavelength_nm])
    
    return qe

def effective_spectrum(source_spectrum, wavelength_nm, detector_type="Si_PMT"):
    """
    Calculate what the detector actually sees.
    
    Args:
        source_spectrum: Intensity at each wavelength
        wavelength_nm: Wavelength array
        detector_type: Detector to use
    
    Returns:
        Detector-weighted spectrum
    """
    qe = detector_efficiency_curve(wavelength_nm, detector_type)
    return source_spectrum * qe

def detection_bias_factor(peak_wavelength_nm, detector_type="Si_PMT"):
    """
    Calculate how much signal we're missing due to detector response.
    
    For a Gaussian spectrum centered at peak_wavelength, what fraction
    of photons does the detector actually see?
    
    Returns:
        Detection fraction (0-1)
    """
    # Generate Gaussian spectrum
    wavelengths = np.linspace(300, 1200, 901)
    sigma = 150  # Typical biophoton spectrum width
    spectrum = np.exp(-0.5 * ((wavelengths - peak_wavelength_nm) / sigma)**2)
    
    # Weight by detector response
    qe = detector_efficiency_curve(wavelengths, detector_type)
    detected = spectrum * qe
    
    # Fraction detected
    total_photons = np.sum(spectrum)
    detected_photons = np.sum(detected)
    
    return detected_photons / total_photons

def recommend_detector(peak_wavelength_nm):
    """
    Recommend optimal detector for given peak wavelength.
    
    Returns:
        (detector_type, detection_fraction, recommendation_text)
    """
    detectors = ["Si_PMT", "EMCCD", "InGaAs"]
    fractions = {}
    
    for det in detectors:
        fractions[det] = detection_bias_factor(peak_wavelength_nm, det)
    
    best_detector = max(fractions, key=fractions.get)
    best_fraction = fractions[best_detector]
    
    if peak_wavelength_nm < 850:
        rec = f"Use {best_detector} for {peak_wavelength_nm}nm peak (captures {best_fraction:.0%})"
    elif peak_wavelength_nm < 1000:
        rec = f"⚠️ Peak at {peak_wavelength_nm}nm is in Si detector gap! "
        rec += f"Use InGaAs (captures {fractions['InGaAs']:.0%}) or lose {1-fractions['Si_PMT']:.0%} with Si"
    else:
        rec = f"Must use InGaAs for {peak_wavelength_nm}nm peak"
    
    return best_detector, best_fraction, rec

def cuprizone_detection_analysis(g_ratio, baseline_peak=648):
    """
    Analyze detection considerations for cuprizone experiment.
    
    Shows how spectral shift affects detectability.
    """
    # Import here to avoid circular dependency
    try:
        from .waveguide_physics import calculate_spectral_shift
    except ImportError:
        from waveguide_physics import calculate_spectral_shift
    
    predicted_peak = calculate_spectral_shift(g_ratio, baseline_g=0.78, 
                                             baseline_centroid=baseline_peak)
    
    # Detection efficiency with standard EMCCD
    baseline_detection = detection_bias_factor(baseline_peak, "EMCCD")
    shifted_detection = detection_bias_factor(predicted_peak, "EMCCD")
    
    # Change in detected photons (not just peak shift)
    detection_change = (shifted_detection / baseline_detection - 1) * 100
    
    results = {
        "g_ratio": g_ratio,
        "baseline_peak_nm": baseline_peak,
        "predicted_peak_nm": predicted_peak,
        "spectral_shift_nm": predicted_peak - baseline_peak,
        "baseline_detection_fraction": baseline_detection,
        "shifted_detection_fraction": shifted_detection,
        "detection_change_percent": detection_change
    }
    
    return results

def validate_detector_models():
    """Run validation tests."""
    print("=== Detector Response Analysis ===\n")
    
    # Test key wavelengths
    test_wavelengths = [400, 500, 600, 700, 800, 865, 900, 1000]
    
    print("Quantum Efficiency Comparison:")
    print("λ (nm) | Si PMT | EMCCD  | InGaAs")
    print("-" * 40)
    
    for w in test_wavelengths:
        si = detector_efficiency_curve(w, "Si_PMT")[0]
        emccd = detector_efficiency_curve(w, "EMCCD")[0]
        ingaas = detector_efficiency_curve(w, "InGaAs")[0]
        print(f"{w:6} | {si:5.1%} | {emccd:5.1%} | {ingaas:5.1%}")
    
    # Human brain peak analysis
    print("\n\nHuman Brain Biophoton Detection:")
    human_peak = 865  # From Wang 2016
    
    for det_type in ["Si_PMT", "EMCCD", "InGaAs"]:
        frac = detection_bias_factor(human_peak, det_type)
        print(f"  {det_type}: captures {frac:.1%} of 865nm peaked spectrum")
    
    print("\n⚠️ Standard detectors miss >50% of human brain biophotons!")
    
    # Cuprizone detection effects
    print("\n\nCuprizone Experiment Detection Effects:")
    print("(Using EMCCD detector)")
    print("\ng-ratio | Peak (nm) | Detected | Change")
    print("-" * 45)
    
    for g in [0.78, 0.85, 0.90, 0.96]:
        results = cuprizone_detection_analysis(g)
        print(f"{g:7.2f} | {results['predicted_peak_nm']:9.0f} | "
              f"{results['shifted_detection_fraction']:7.1%} | "
              f"{results['detection_change_percent']:+6.1f}%")
    
    print("\nNote: Blueshift INCREASES detectability with Si detectors")

if __name__ == "__main__":
    validate_detector_models()
    
    # Generate recommendation table
    print("\n\n=== Detector Recommendations ===")
    for peak in [500, 600, 700, 800, 865, 900, 1000, 1200]:
        det, frac, rec = recommend_detector(peak)
        print(f"\n{peak}nm peak: {rec}")