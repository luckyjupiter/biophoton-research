"""
Spatial distribution model for cuprizone demyelination.

Models the rostro-caudal gradient and patchy nature of demyelination.
Key features:
- Continuous gradient instead of discrete regions
- Stochastic patchiness overlaid on gradient
- Time-dependent spreading of lesions
- Correlation with local inflammation markers

Based on:
- Steelman et al. 2012: rostro-caudal gradient
- Matsushima & Morell 2001: patchy demyelination patterns  
- Praet et al. 2014: spatiotemporal progression
"""

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.stats import beta as beta_dist

def rostrocaudal_severity(position, week, base_severity=1.0):
    """
    Calculate demyelination severity along rostro-caudal axis.
    
    Args:
        position: 0 (rostral/genu) to 1 (caudal/splenium)
        week: Time point in cuprizone protocol
        base_severity: Scaling factor
    
    Returns:
        Local severity multiplier (0-1)
    """
    if week < 2:
        return 0.0  # No demyelination yet
    
    # Severity peaks in mid-corpus callosum
    # Beta distribution gives flexibility in shape
    if week <= 6:  # Demyelination phase
        # Shape evolves over time
        alpha = 2.0 + (week - 2) * 0.5  # Gets more peaked
        beta = 2.0 + (week - 2) * 0.3   # Slight caudal shift
        
        severity = beta_dist.pdf(position, alpha, beta)
        # Normalize to 0-1 range
        severity = severity / beta_dist.pdf(0.5, alpha, beta)
        
    else:  # Recovery phase
        # Recovery starts caudally (splenium recovers first)
        recovery_gradient = 1 - position  # Stronger recovery caudally
        recovery_factor = min(1.0, (week - 6) / 6)  # 0 to 1 over 6 weeks
        
        # Peak severity from week 6
        peak_alpha = 4.0
        peak_beta = 3.5
        peak_severity = beta_dist.pdf(position, peak_alpha, peak_beta)
        peak_severity = peak_severity / beta_dist.pdf(0.5, peak_alpha, peak_beta)
        
        # Apply recovery
        severity = peak_severity * (1 - recovery_factor * recovery_gradient * 0.7)
    
    return severity * base_severity

def add_stochastic_patches(severity_profile, n_patches=5, patch_size=0.05, seed=None):
    """
    Add random patches of more severe demyelination.
    
    Models the patchy, irregular nature of cuprizone lesions.
    
    Args:
        severity_profile: 1D array of severity values
        n_patches: Number of random patches
        patch_size: Size of patches (fraction of total length)
        seed: Random seed for reproducibility
    
    Returns:
        Modified severity profile with patches
    """
    if seed is not None:
        np.random.seed(seed)
    
    profile = severity_profile.copy()
    positions = np.linspace(0, 1, len(profile))
    
    for _ in range(n_patches):
        # Random patch center
        center = np.random.uniform(0.1, 0.9)
        
        # Random severity boost (20-50% more severe)
        boost = np.random.uniform(0.2, 0.5)
        
        # Gaussian patch
        patch = np.exp(-0.5 * ((positions - center) / patch_size)**2)
        profile = profile * (1 + boost * patch)
    
    # Smooth slightly to avoid sharp edges
    profile = gaussian_filter1d(profile, sigma=len(profile) * 0.02)
    
    # Ensure we don't exceed 1.0
    return np.clip(profile, 0, 1)

def inflammatory_hotspots(position_array, week, n_hotspots=3):
    """
    Model inflammatory hotspots that drive local demyelination.
    
    Inflammation precedes and drives demyelination.
    
    Returns:
        Inflammation intensity profile (0-1)
    """
    if week < 1:
        return np.zeros_like(position_array)
    
    inflammation = np.zeros_like(position_array)
    
    # Hotspot locations (somewhat stable over time)
    np.random.seed(42)  # Fixed for consistency
    hotspot_centers = np.random.uniform(0.2, 0.8, n_hotspots)
    
    for i, center in enumerate(hotspot_centers):
        # Inflammation peaks earlier than demyelination
        peak_week = 3 + i * 0.5  # Staggered peaks
        
        # Temporal profile
        if week < peak_week:
            intensity = (week - 1) / (peak_week - 1)
        else:
            # Decay after peak
            decay_rate = 0.3
            intensity = np.exp(-decay_rate * (week - peak_week))
        
        # Spatial profile (Gaussian)
        width = 0.08 + 0.02 * i  # Variable widths
        spatial = np.exp(-0.5 * ((position_array - center) / width)**2)
        
        inflammation += intensity * spatial
    
    return np.clip(inflammation, 0, 1)

def gratio_from_severity(baseline_g, severity, max_g=0.98):
    """
    Convert severity (0-1) to g-ratio.
    
    Args:
        baseline_g: Healthy g-ratio (~0.78)
        severity: Demyelination severity (0=healthy, 1=complete)
        max_g: Maximum g-ratio (thin myelin remnants)
    
    Returns:
        g-ratio value
    """
    # Nonlinear mapping - most myelin loss happens at high severity
    # This matches histology where you need >70% myelin loss to see major g-ratio change
    severity_adjusted = severity**1.5
    
    return baseline_g + (max_g - baseline_g) * severity_adjusted

def spatial_gratio_distribution(week, n_points=100, protocol='acute'):
    """
    Get g-ratio distribution along rostro-caudal axis.
    
    Returns:
        positions (0-1), g_ratios, severity_profile, inflammation_profile
    """
    positions = np.linspace(0, 1, n_points)
    
    # Base severity from gradient
    severity = np.array([rostrocaudal_severity(p, week) for p in positions])
    
    # Add inflammation
    inflammation = inflammatory_hotspots(positions, week)
    
    # Inflammation drives severity with some lag
    if week > 2:
        inflammation_effect = gaussian_filter1d(inflammation, sigma=n_points * 0.05)
        severity = np.clip(severity + 0.3 * inflammation_effect, 0, 1)
    
    # Add stochastic patches
    if week >= 3:
        severity = add_stochastic_patches(severity, n_patches=int(week/2))
    
    # Chronic protocol is more severe
    if protocol == 'chronic':
        severity = np.clip(severity * 1.15, 0, 1)
    
    # Convert to g-ratios
    baseline_g = 0.78
    g_ratios = [gratio_from_severity(baseline_g, s) for s in severity]
    
    return positions, np.array(g_ratios), severity, inflammation

def lesion_burden(week, protocol='acute'):
    """
    Calculate total lesion burden (fraction of CC affected).
    
    Returns:
        burden (0-1), mean_severity, max_severity
    """
    _, g_ratios, severity, _ = spatial_gratio_distribution(week, n_points=200, protocol=protocol)
    
    # Lesion defined as g > 0.85
    lesion_threshold = 0.85
    burden = np.mean(g_ratios > lesion_threshold)
    
    mean_severity = np.mean(severity)
    max_severity = np.max(severity)
    
    return burden, mean_severity, max_severity

def spectral_map(week, baseline_centroid=648, protocol='acute'):
    """
    Calculate predicted spectral centroids along rostro-caudal axis.
    
    Returns:
        positions, centroids, shifts
    """
    try:
        from .waveguide_physics import calculate_spectral_shift
    except ImportError:
        from waveguide_physics import calculate_spectral_shift
    
    positions, g_ratios, _, _ = spatial_gratio_distribution(week, protocol=protocol)
    
    centroids = []
    for g in g_ratios:
        centroid = calculate_spectral_shift(g, baseline_g=0.78, 
                                          baseline_centroid=baseline_centroid)
        centroids.append(centroid)
    
    centroids = np.array(centroids)
    shifts = centroids - baseline_centroid
    
    return positions, centroids, shifts

def print_spatial_analysis():
    """Print spatial distribution analysis."""
    print("=== Spatial Distribution Model ===\n")
    
    # Lesion burden over time
    print("Lesion burden progression:")
    print("Week | Acute | Chronic")
    print("-" * 25)
    
    for week in [0, 2, 3, 4, 5, 6, 8, 10, 13]:
        burden_acute, _, _ = lesion_burden(week, 'acute')
        burden_chronic, _, _ = lesion_burden(week, 'chronic')
        print(f"{week:4} | {burden_acute:5.1%} | {burden_chronic:7.1%}")
    
    # Regional analysis at peak
    print("\n\nRegional analysis at peak (week 6):")
    positions, g_ratios, severity, inflammation = spatial_gratio_distribution(6)
    
    # Sample at key positions
    regions = {
        'Rostral (0.1)': 0.1,
        'Mid-rostral (0.3)': 0.3,
        'Central (0.5)': 0.5,
        'Mid-caudal (0.7)': 0.7,
        'Caudal (0.9)': 0.9
    }
    
    print("\nPosition | g-ratio | Severity | Inflammation")
    print("-" * 50)
    for name, pos in regions.items():
        idx = int(pos * (len(positions) - 1))
        print(f"{name:16} | {g_ratios[idx]:7.3f} | {severity[idx]:8.1%} | {inflammation[idx]:12.1%}")
    
    # Spectral variation
    print("\n\nSpectral variation at week 6:")
    positions, centroids, shifts = spectral_map(6)
    
    print(f"Mean centroid: {np.mean(centroids):.0f} nm")
    print(f"Range: {np.min(centroids):.0f} - {np.max(centroids):.0f} nm")
    print(f"Standard deviation: {np.std(centroids):.1f} nm")
    
    # Worst affected region
    worst_idx = np.argmin(centroids)
    print(f"\nMost affected position: {positions[worst_idx]:.2f}")
    print(f"  G-ratio: {g_ratios[worst_idx]:.3f}")
    print(f"  Centroid: {centroids[worst_idx]:.0f} nm (shift: {shifts[worst_idx]:+.0f} nm)")

if __name__ == "__main__":
    print_spatial_analysis()