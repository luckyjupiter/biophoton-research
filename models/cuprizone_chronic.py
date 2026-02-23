"""
Chronic cuprizone model implementation.

Extends the acute 6-week model to 13-week chronic protocol with impaired recovery.
Key differences:
- More severe peak demyelination (g~0.97-0.98)
- Slower recovery kinetics 
- Incomplete remyelination (plateaus at g~0.86-0.88)
- Regional heterogeneity more pronounced

Based on:
- Lindner et al. 2008 (acute timeline)
- Sachs et al. 2014 (regional differences)
- Steelman et al. 2012 (chronic protocol)
"""

import numpy as np
from scipy.interpolate import interp1d

# Acute timeline from Lindner 2008
ACUTE_TIMELINE = {
    0: 0.802,   # Baseline
    2: 0.830,   # Early demyelination
    3: 0.875,   # Progressive
    4: 0.926,   # Accelerating
    5: 0.952,   # Near peak
    6: 0.964,   # Peak demyelination
    7: 0.920,   # Early recovery
    8: 0.878,   # Active remyelination
    10: 0.849,  # Late recovery
    12: 0.841,  # Near plateau
    13: 0.839   # Stable remyelinated
}

# Chronic timeline (extrapolated from literature)
CHRONIC_TIMELINE = {
    0: 0.802,   # Baseline
    2: 0.835,   # Slower start
    3: 0.885,   # Still progressing
    4: 0.935,   # More severe
    5: 0.965,   # Approaching peak
    6: 0.975,   # Peak more severe
    7: 0.968,   # Minimal recovery
    8: 0.955,   # Very slow improvement
    10: 0.920,  # Still highly demyelinated
    12: 0.895,  # Plateauing high
    13: 0.885,  # Chronic damage
    16: 0.875,  # Extended timepoint
    20: 0.870   # Long-term plateau
}

def cuprizone_gratio(week, protocol='acute', region='corpus_callosum'):
    """
    Get g-ratio at specified week for given protocol and region.
    
    Args:
        week: Time in weeks (can be fractional)
        protocol: 'acute' or 'chronic'
        region: 'corpus_callosum', 'splenium', 'dhc', or 'genu'
    
    Returns:
        g-ratio value
    """
    # Select timeline
    if protocol == 'acute':
        timeline = ACUTE_TIMELINE
    else:
        timeline = CHRONIC_TIMELINE
    
    # Create interpolator
    weeks = sorted(timeline.keys())
    gratios = [timeline[w] for w in weeks]
    
    # Handle out of range
    if week < 0:
        week = 0
    if week > max(weeks):
        return timeline[max(weeks)]
    
    # Interpolate
    f = interp1d(weeks, gratios, kind='cubic')
    base_gratio = float(f(week))
    
    # Apply regional modifiers
    regional_factors = {
        'corpus_callosum': 1.00,  # Reference region
        'splenium': 0.98,         # Slightly less affected
        'dhc': 1.02,              # Most affected
        'genu': 1.00              # Similar to CC
    }
    
    # During demyelination, amplify differences
    if week >= 3 and week <= 8:
        severity = (week - 3) / 5  # 0 to 1 over demyelination phase
        factor = 1 + (regional_factors[region] - 1) * (1 + severity)
    else:
        factor = regional_factors[region]
    
    return base_gratio * factor

def recovery_trajectory(protocol='acute'):
    """
    Get full recovery trajectory with key phases marked.
    
    Returns:
        weeks, g_ratios, phases (dict of phase boundaries)
    """
    weeks = np.linspace(0, 13 if protocol == 'acute' else 20, 200)
    g_ratios = [cuprizone_gratio(w, protocol) for w in weeks]
    
    phases = {
        'baseline': (0, 2),
        'demyelination': (2, 6),
        'early_recovery': (6, 8),
        'late_recovery': (8, 13),
    }
    
    if protocol == 'chronic':
        phases['chronic_plateau'] = (13, 20)
    
    return weeks, g_ratios, phases

def compare_protocols():
    """Generate comparison data between acute and chronic."""
    weeks = np.linspace(0, 20, 201)
    
    acute_g = []
    chronic_g = []
    
    for w in weeks:
        if w <= 13:
            acute_g.append(cuprizone_gratio(w, 'acute'))
        else:
            acute_g.append(cuprizone_gratio(13, 'acute'))  # Plateau
        
        chronic_g.append(cuprizone_gratio(w, 'chronic'))
    
    return weeks, acute_g, chronic_g

def spectral_impact_chronic(week, protocol='chronic', baseline_centroid=648):
    """
    Calculate predicted spectral shift for chronic cuprizone.
    
    Returns:
        dict with g_ratio, predicted_centroid, shift_nm
    """
    # Import here to avoid circular dependency
    try:
        from .waveguide_physics import calculate_spectral_shift
    except ImportError:
        from waveguide_physics import calculate_spectral_shift
    
    g_ratio = cuprizone_gratio(week, protocol)
    predicted = calculate_spectral_shift(g_ratio, baseline_g=0.78, 
                                       baseline_centroid=baseline_centroid)
    
    return {
        'week': week,
        'protocol': protocol,
        'g_ratio': g_ratio,
        'predicted_centroid_nm': predicted,
        'shift_nm': predicted - baseline_centroid,
        'severity': 'severe' if g_ratio > 0.95 else 'moderate' if g_ratio > 0.88 else 'mild'
    }

def regional_heterogeneity_map(week, protocol='acute'):
    """
    Get g-ratios for all regions at specified timepoint.
    
    Returns:
        dict mapping region names to g-ratios
    """
    regions = ['corpus_callosum', 'splenium', 'dhc', 'genu']
    
    return {
        region: cuprizone_gratio(week, protocol, region) 
        for region in regions
    }

def remyelination_quality_factor(week, protocol='acute'):
    """
    Calculate quality of remyelinated myelin (0-1 scale).
    
    Remyelinated myelin is:
    - Thinner (higher g-ratio)
    - More irregular
    - Has different optical properties
    
    Returns:
        quality_factor (1 = perfect, <1 = impaired)
    """
    if week < 6:
        return 1.0  # No remyelination yet
    
    # Time since peak demyelination
    recovery_time = week - 6
    
    if protocol == 'acute':
        # Approaches 0.85 quality asymptotically
        quality = 0.85 * (1 - np.exp(-recovery_time / 3))
    else:
        # Chronic: much worse quality, plateaus at 0.65
        quality = 0.65 * (1 - np.exp(-recovery_time / 5))
    
    return quality

def print_validation():
    """Print validation against known data."""
    print("=== Chronic Cuprizone Model Validation ===\n")
    
    print("Acute vs Chronic at key timepoints:")
    print("Week | Acute g | Chronic g | Difference")
    print("-" * 45)
    
    for week in [0, 3, 6, 8, 10, 13]:
        acute = cuprizone_gratio(week, 'acute')
        chronic = cuprizone_gratio(week, 'chronic')
        diff = chronic - acute
        print(f"{week:4} | {acute:7.3f} | {chronic:9.3f} | {diff:+10.3f}")
    
    print("\n\nSpectral predictions (chronic):")
    print("Week | g-ratio | Centroid | Shift")
    print("-" * 40)
    
    for week in [0, 6, 13, 20]:
        result = spectral_impact_chronic(week)
        print(f"{week:4} | {result['g_ratio']:7.3f} | {result['predicted_centroid_nm']:8.0f} | "
              f"{result['shift_nm']:+5.0f}")
    
    print("\n\nRegional differences at peak (week 6):")
    regions = regional_heterogeneity_map(6, 'chronic')
    for region, g in regions.items():
        print(f"  {region:20}: {g:.3f}")
    
    print("\n\nRemyelination quality:")
    print("Week | Acute | Chronic")
    print("-" * 25)
    for week in [8, 10, 13, 16, 20]:
        acute_q = remyelination_quality_factor(week, 'acute')
        chronic_q = remyelination_quality_factor(week, 'chronic')
        print(f"{week:4} | {acute_q:5.2f} | {chronic_q:7.2f}")

if __name__ == "__main__":
    print_validation()