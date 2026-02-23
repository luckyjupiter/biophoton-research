"""
Physics-based waveguide mode solver for myelinated axons.

Key physics:
- Myelin forms a leaky waveguide (n_myelin > n_cytoplasm > n_extracellular)
- Light propagates in the high-index myelin layer
- Wavelength-dependent confinement creates spectral filtering
- Thicker myelin (lower g-ratio) → better IR confinement → redder spectrum
- Thinner myelin (higher g-ratio) → more leakage → bluer spectrum

References:
- Kumar et al. 2016: Myelinated axon as optical waveguide
- Zeng et al. 2022: EM modeling of neural waveguides
- Reed et al. 2023: Myelin as spectral filter in AD
"""

import numpy as np
from scipy.special import exp1  # Exponential integral

# Physical constants
WAVELENGTH_RANGE = (300, 1200)  # nm
N_CYTOPLASM = 1.359      # Axon core refractive index (Kumar 2016)
N_MYELIN = 1.439         # Myelin sheath index (Kumar 2016)
N_EXTRACELLULAR = 1.335  # External medium (Tang 2016)

# Axon parameters (mouse optic nerve)
AXON_RADIUS_DEFAULT = 0.4e-6  # 400 nm typical for CNS

def penetration_depth(wavelength_nm, n1=N_MYELIN, n2=N_EXTRACELLULAR):
    """
    Calculate evanescent field penetration depth at interface.
    For wavelengths where myelin guides, this sets the confinement scale.
    """
    wavelength_m = wavelength_nm * 1e-9
    
    # Critical angle for total internal reflection
    if n1 <= n2:
        return np.inf  # No TIR possible
    
    sin_critical = n2 / n1
    
    # Typical incident angle (45° from myelin axis)
    theta_i = np.pi / 4
    sin_theta = np.sin(theta_i)
    
    if sin_theta < sin_critical:
        # Below critical angle, no confinement
        return np.inf
    
    # Penetration depth for evanescent wave
    k0 = 2 * np.pi / wavelength_m
    kz = k0 * n1 * np.sqrt(sin_theta**2 - sin_critical**2)
    
    return 1 / kz * 1e9  # Convert to nm

def myelin_confinement(wavelength_nm, myelin_thickness_nm):
    """
    Calculate fraction of optical power confined within myelin sheath.
    Based on overlap of guided mode with myelin region.
    """
    # Penetration depths into both boundaries
    d_ext = penetration_depth(wavelength_nm, N_MYELIN, N_EXTRACELLULAR)
    d_cyt = penetration_depth(wavelength_nm, N_MYELIN, N_CYTOPLASM)
    
    # Characteristic mode size
    mode_size = np.minimum(d_ext, d_cyt)
    
    if mode_size == np.inf:
        return 0.0  # No confinement
    
    # Fraction confined scales with thickness/mode_size ratio
    ratio = myelin_thickness_nm / mode_size
    
    # Use error function profile for mode confinement
    # Approximation: 1 - exp(-2*ratio) gives fraction in guiding layer
    confinement = 1 - np.exp(-2 * ratio)
    
    return confinement

def spectral_filter_function(wavelength_nm, g_ratio, axon_radius_nm=400):
    """
    Calculate wavelength-dependent transmission through myelin.
    
    Key effects:
    1. Wavelength-dependent confinement (λ↑ → confinement↓)
    2. Myelin thickness effect (g↓ → thickness↑ → IR guided better)
    3. Scattering losses (λ↓ → loss↑)
    
    Returns: transmission coefficient (0-1)
    """
    wavelength_nm = np.atleast_1d(wavelength_nm)
    
    # Calculate myelin thickness
    outer_radius_nm = axon_radius_nm / g_ratio
    myelin_thickness_nm = outer_radius_nm - axon_radius_nm
    
    # Base confinement from waveguiding
    confinement = myelin_confinement(wavelength_nm, myelin_thickness_nm)
    
    # Scattering loss (Rayleigh-like, stronger at short wavelengths)
    scattering_loss = np.exp(-300 / wavelength_nm)  # Empirical scaling
    
    # Absorption edge effects (myelin more transparent in red/IR)
    absorption = 1 / (1 + np.exp((wavelength_nm - 950) / 100))
    
    # Total transmission
    transmission = confinement * scattering_loss * absorption
    
    return transmission

def calculate_spectral_centroid(wavelength_nm, spectrum, transmission):
    """Calculate intensity-weighted centroid of filtered spectrum."""
    filtered = spectrum * transmission
    if np.sum(filtered) > 0:
        return np.sum(wavelength_nm * filtered) / np.sum(filtered)
    else:
        return np.mean(wavelength_nm)

def predict_spectral_shift(g_ratio, baseline_g=0.78, baseline_centroid=648):
    """
    Predict spectral centroid for given g-ratio.
    
    Args:
        g_ratio: myelin g-ratio (inner/outer radius)
        baseline_g: reference g-ratio with known centroid
        baseline_centroid: known centroid at baseline (nm)
    
    Returns:
        predicted centroid (nm)
    """
    # Generate wavelength array
    wavelengths = np.linspace(350, 1000, 651)
    
    # Source spectrum (broad Gaussian centered at 700nm)
    # This represents the intrinsic biophoton emission
    source_spectrum = np.exp(-0.5 * ((wavelengths - 700) / 200)**2)
    
    # Calculate transmission for baseline
    trans_baseline = spectral_filter_function(wavelengths, baseline_g)
    centroid_baseline_raw = calculate_spectral_centroid(wavelengths, source_spectrum, trans_baseline)
    
    # Calculate transmission for target g-ratio
    trans_target = spectral_filter_function(wavelengths, g_ratio)
    centroid_target_raw = calculate_spectral_centroid(wavelengths, source_spectrum, trans_target)
    
    # Apply calibration offset to match known baseline
    offset = baseline_centroid - centroid_baseline_raw
    centroid_target = centroid_target_raw + offset
    
    return centroid_target

def validate_model():
    """Validate against known data points."""
    print("=== Myelin Waveguide Model Validation ===\n")
    
    # Test penetration depths
    print("Penetration depths at 600nm:")
    d_ext = penetration_depth(600)
    print(f"  Into extracellular: {d_ext:.1f} nm")
    d_cyt = penetration_depth(600, N_MYELIN, N_CYTOPLASM)  
    print(f"  Into cytoplasm: {d_cyt:.1f} nm")
    
    # Test spectral predictions
    print("\n\nSpectral centroid predictions:")
    print("g-ratio | Centroid (nm) | Shift from baseline | Note")
    print("-" * 70)
    
    # Known reference point
    baseline_g = 0.78
    baseline_centroid = 648  # Dai et al. WT mice
    
    test_gratios = [
        (0.70, "Healthy young adult"),
        (0.78, "Standard WT mouse (Dai)"),
        (0.85, "Mild demyelination"), 
        (0.90, "Moderate demyelination"),
        (0.96, "Severe cuprizone peak"),
        (0.99, "Near-complete loss")
    ]
    
    for g, note in test_gratios:
        centroid = predict_spectral_shift(g, baseline_g, baseline_centroid)
        shift = centroid - baseline_centroid
        print(f"{g:.2f}    | {centroid:13.1f} | {shift:+6.1f} nm      | {note}")
    
    # Compare to Dai's measured AD shift
    print("\n\nComparison to Dai et al. 2020 AD data:")
    dai_wt = 648
    dai_ad = 582
    dai_shift = dai_ad - dai_wt
    print(f"  Measured: {dai_wt}nm → {dai_ad}nm (shift: {dai_shift}nm)")
    
    # Our prediction for AD-like demyelination (estimate g~0.90)
    ad_g_estimate = 0.90
    our_prediction = predict_spectral_shift(ad_g_estimate, baseline_g, baseline_centroid)
    our_shift = our_prediction - baseline_centroid
    print(f"  Model prediction at g={ad_g_estimate}: {baseline_centroid}nm → {our_prediction:.0f}nm (shift: {our_shift:.0f}nm)")
    print(f"  Error: {abs(our_shift - dai_shift):.0f}nm")

def plot_filter_functions():
    """Generate visualization data for filter functions."""
    wavelengths = np.linspace(350, 1000, 651)
    
    print("\n\n=== Filter Function Data (for plotting) ===")
    
    # Different g-ratios
    gratios = [0.70, 0.78, 0.85, 0.90, 0.96]
    
    for g in gratios:
        trans = spectral_filter_function(wavelengths, g)
        # Print sample points for external plotting
        print(f"\ng-ratio {g}:")
        for i in range(0, len(wavelengths), 50):
            print(f"  {wavelengths[i]:.0f}nm: {trans[i]:.3f}")

if __name__ == "__main__":
    validate_model()
    plot_filter_functions()