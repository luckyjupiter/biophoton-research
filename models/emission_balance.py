"""
Balance analysis of nanoantenna vs ROS emission sources.

Key question: What is the relative contribution of each mechanism to the
total biophoton emission, and how does this change with demyelination?

Sources:
1. ROS (reactive oxygen species): Chemical origin, broad spectrum
2. Nanoantenna (nodes of Ranvier): Electrical origin, IR peaked
3. Thermal: Negligible at body temperature for visible light
4. Quantum (Liu): Negligible due to decoherence

This module quantifies the balance and its disease dependence.
"""

import numpy as np
from scipy.integrate import simpson

# Import our models
try:
    from .constants import (
        ROS_COMPONENTS, BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S,
        INFLAMMATORY_EMISSION_FACTOR_HIGH
    )
    from .literature_data import ZANGARI_MEASUREMENTS
    from .waveguide_physics import myelin_transmission_empirical
except ImportError:
    from constants import (
        ROS_COMPONENTS, BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S,
        INFLAMMATORY_EMISSION_FACTOR_HIGH
    )
    from literature_data import ZANGARI_MEASUREMENTS
    from waveguide_physics import myelin_transmission_empirical

def ros_emission_spectrum(wavelength_nm, disease_state='healthy'):
    """
    Calculate ROS emission spectrum.
    
    Based on known ROS spectral components from lipid peroxidation,
    singlet oxygen, and excited carbonyls.
    
    Args:
        wavelength_nm: Wavelength array
        disease_state: 'healthy', 'inflamed', or 'demyelinated'
    
    Returns:
        Emission intensity (photons/s/cm²/nm)
    """
    wavelength_nm = np.atleast_1d(wavelength_nm)
    spectrum = np.zeros_like(wavelength_nm, dtype=float)
    
    # Build spectrum from components
    for center, fwhm, amplitude, species in ROS_COMPONENTS:
        # Gaussian component
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        component = amplitude * np.exp(-0.5 * ((wavelength_nm - center) / sigma)**2)
        spectrum += component
    
    # Normalize to integrate to baseline emission
    norm = simpson(spectrum, wavelength_nm)
    if norm > 0:
        spectrum = spectrum / norm * BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S
    
    # Disease amplification
    if disease_state == 'inflamed':
        spectrum *= 10  # 10× increase with inflammation
    elif disease_state == 'demyelinated':
        spectrum *= 50  # 50× increase with severe demyelination
    
    return spectrum

def nanoantenna_emission_spectrum(wavelength_nm, g_ratio=0.78):
    """
    Calculate nanoantenna emission from nodes of Ranvier.
    
    Based on Zangari et al. 2018/2021 model of Na+ channels as
    phased array antennas.
    
    Args:
        wavelength_nm: Wavelength array  
        g_ratio: Myelin g-ratio (affects node spacing/size)
    
    Returns:
        Emission intensity (photons/s/cm²/nm)
    """
    wavelength_nm = np.atleast_1d(wavelength_nm)
    
    # Zangari parameters
    peak_nm = ZANGARI_MEASUREMENTS['2018_model']['peak_emission_nm']  # 850 nm
    emission_per_ap = ZANGARI_MEASUREMENTS['2018_model']['emission_rate_photons_per_ap']
    
    # Spectral shape: Gaussian centered in near-IR
    sigma = 200  # nm, broad emission
    spectrum = np.exp(-0.5 * ((wavelength_nm - peak_nm) / sigma)**2)
    
    # Node density depends on g-ratio
    # Higher g-ratio = thinner myelin = shorter internodes = more nodes
    node_density_factor = (g_ratio / 0.78)**2  # Quadratic scaling
    
    # Action potential rate
    ap_rate = 100  # Hz, typical for active axons
    
    # Convert to photons/s/cm²/nm
    # Assume 1000 nodes/cm² at baseline
    nodes_per_cm2 = 1000 * node_density_factor
    total_emission = nodes_per_cm2 * ap_rate * emission_per_ap
    
    # Distribute over spectrum
    norm = simpson(spectrum, wavelength_nm)
    if norm > 0:
        spectrum = spectrum / norm * total_emission
    
    return spectrum

def total_observed_spectrum(wavelength_nm, g_ratio=0.78, disease_state='healthy'):
    """
    Calculate total observed biophoton spectrum including waveguide filtering.
    
    This is what a detector would actually see after:
    1. ROS emission (metabolic)
    2. Nanoantenna emission (electrical)
    3. Myelin waveguide filtering (optical)
    
    Args:
        wavelength_nm: Wavelength array
        g_ratio: Myelin g-ratio
        disease_state: Health condition
    
    Returns:
        Observed spectrum (photons/s/cm²/nm)
    """
    # Get emission sources
    ros = ros_emission_spectrum(wavelength_nm, disease_state)
    antenna = nanoantenna_emission_spectrum(wavelength_nm, g_ratio)
    
    # Get waveguide transmission
    transmission = myelin_transmission_empirical(wavelength_nm, g_ratio)
    
    # External detection sees filtered emission
    # Assume 90% of ROS is external (not guided)
    # Assume 50% of nanoantenna is coupled to waveguide
    external_ros = ros * 0.9
    guided_ros = ros * 0.1 * transmission
    
    external_antenna = antenna * 0.5
    guided_antenna = antenna * 0.5 * transmission
    
    # Total observed
    observed = external_ros + guided_ros + external_antenna + guided_antenna
    
    return observed

def calculate_emission_balance(g_ratio=0.78, disease_state='healthy'):
    """
    Calculate relative contributions of ROS vs nanoantenna emission.
    
    Returns:
        dict with balance metrics
    """
    wavelengths = np.linspace(300, 1200, 901)
    
    # Get individual contributions
    ros = ros_emission_spectrum(wavelengths, disease_state)
    antenna = nanoantenna_emission_spectrum(wavelengths, g_ratio)
    total = total_observed_spectrum(wavelengths, g_ratio, disease_state)
    
    # Integrate over visible range (400-700 nm)
    visible_mask = (wavelengths >= 400) & (wavelengths <= 700)
    ros_visible = simpson(ros[visible_mask], wavelengths[visible_mask])
    antenna_visible = simpson(antenna[visible_mask], wavelengths[visible_mask])
    total_visible = simpson(total[visible_mask], wavelengths[visible_mask])
    
    # Integrate over full range
    ros_total = simpson(ros, wavelengths)
    antenna_total = simpson(antenna, wavelengths)
    total_total = simpson(total, wavelengths)
    
    # Calculate centroids
    ros_centroid = np.sum(wavelengths * ros) / np.sum(ros) if np.sum(ros) > 0 else 0
    antenna_centroid = np.sum(wavelengths * antenna) / np.sum(antenna) if np.sum(antenna) > 0 else 0
    total_centroid = np.sum(wavelengths * total) / np.sum(total) if np.sum(total) > 0 else 0
    
    balance = {
        'g_ratio': g_ratio,
        'disease_state': disease_state,
        'ros_fraction_visible': ros_visible / total_visible if total_visible > 0 else 0,
        'antenna_fraction_visible': antenna_visible / total_visible if total_visible > 0 else 0,
        'ros_fraction_total': ros_total / total_total if total_total > 0 else 0,
        'antenna_fraction_total': antenna_total / total_total if total_total > 0 else 0,
        'ros_centroid_nm': ros_centroid,
        'antenna_centroid_nm': antenna_centroid,
        'observed_centroid_nm': total_centroid,
        'total_flux_photons_cm2_s': total_total
    }
    
    return balance

def disease_progression_analysis():
    """
    Analyze how emission balance changes through disease progression.
    
    Returns:
        Timeline of balance changes
    """
    # Define progression stages
    stages = [
        ('Healthy', 0.78, 'healthy'),
        ('Early inflammation', 0.78, 'inflamed'),
        ('Mild demyelination', 0.85, 'inflamed'),
        ('Moderate demyelination', 0.90, 'demyelinated'),
        ('Severe demyelination', 0.96, 'demyelinated'),
        ('Remyelinated', 0.84, 'healthy')  # Incomplete recovery
    ]
    
    results = []
    for stage_name, g_ratio, state in stages:
        balance = calculate_emission_balance(g_ratio, state)
        balance['stage'] = stage_name
        results.append(balance)
    
    return results

def spatial_emission_pattern(week=6):
    """
    Calculate spatial variation in emission balance.
    
    Uses spatial distribution model to show heterogeneity.
    """
    try:
        from .spatial_distribution import spatial_gratio_distribution
    except ImportError:
        from spatial_distribution import spatial_gratio_distribution
    
    positions, g_ratios, severity, inflammation = spatial_gratio_distribution(week)
    
    # Calculate balance at each position
    balances = []
    for i, (pos, g, sev, inf) in enumerate(zip(positions, g_ratios, severity, inflammation)):
        # Determine disease state from severity/inflammation
        if inf > 0.5:
            state = 'inflamed'
        elif sev > 0.7:
            state = 'demyelinated'
        else:
            state = 'healthy'
        
        balance = calculate_emission_balance(g, state)
        balance['position'] = pos
        balance['severity'] = sev
        balance['inflammation'] = inf
        balances.append(balance)
    
    return balances

def print_balance_analysis():
    """Print comprehensive emission balance analysis."""
    print("=== Nanoantenna vs ROS Emission Balance Analysis ===\n")
    
    # Baseline balance
    baseline = calculate_emission_balance()
    print("Baseline (healthy) emission balance:")
    print(f"  ROS contribution (visible): {baseline['ros_fraction_visible']:.1%}")
    print(f"  Nanoantenna (visible): {baseline['antenna_fraction_visible']:.1%}")
    print(f"  ROS centroid: {baseline['ros_centroid_nm']:.0f} nm")
    print(f"  Nanoantenna centroid: {baseline['antenna_centroid_nm']:.0f} nm")
    print(f"  Observed centroid: {baseline['observed_centroid_nm']:.0f} nm")
    
    # Disease progression
    print("\n\nDisease progression:")
    print("Stage | g-ratio | ROS % | Antenna % | Centroid | Total flux")
    print("-" * 70)
    
    for stage in disease_progression_analysis():
        print(f"{stage['stage']:25} | {stage['g_ratio']:7.2f} | "
              f"{stage['ros_fraction_total']:5.1%} | {stage['antenna_fraction_total']:9.1%} | "
              f"{stage['observed_centroid_nm']:8.0f} | {stage['total_flux_photons_cm2_s']:10.1e}")
    
    # Key insights
    print("\n\nKey insights:")
    print("1. ROS dominates in visible range (chemical emission)")
    print("2. Nanoantenna dominates in IR (electrical emission)")
    print("3. Inflammation amplifies ROS dramatically")
    print("4. Demyelination shifts balance and spectrum")
    print("5. Spatial heterogeneity creates mixed emission zones")
    
    # Detection implications
    print("\n\nDetection implications:")
    print("- For visible detection (EMCCD): Primarily measuring ROS")
    print("- For IR detection (InGaAs): Would see more nanoantenna")
    print("- Spectral analysis can separate contributions")
    print("- Spatial mapping reveals emission mechanism zones")

if __name__ == "__main__":
    print_balance_analysis()
    
    # Generate example spectra
    import matplotlib.pyplot as plt
    
    wavelengths = np.linspace(300, 1200, 901)
    
    # Calculate spectra for different conditions
    healthy_spectrum = total_observed_spectrum(wavelengths, 0.78, 'healthy')
    inflamed_spectrum = total_observed_spectrum(wavelengths, 0.85, 'inflamed')
    demyelinated_spectrum = total_observed_spectrum(wavelengths, 0.96, 'demyelinated')
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.semilogy(wavelengths, healthy_spectrum, 'g-', linewidth=2, label='Healthy')
    plt.semilogy(wavelengths, inflamed_spectrum, 'orange', linewidth=2, label='Inflamed')
    plt.semilogy(wavelengths, demyelinated_spectrum, 'r-', linewidth=2, label='Demyelinated')
    
    plt.axvspan(400, 700, alpha=0.1, color='blue', label='Visible range')
    plt.axvspan(700, 1200, alpha=0.1, color='red', label='IR range')
    
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Emission (photons/s/cm²/nm)')
    plt.title('Biophoton Emission: ROS + Nanoantenna Balance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(300, 1200)
    plt.ylim(1e-4, 1e2)
    
    plt.tight_layout()
    plt.savefig('emission_balance_spectra.png', dpi=300)
    print("\nSaved emission balance spectra to emission_balance_spectra.png")