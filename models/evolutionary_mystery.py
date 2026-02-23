"""
The evolutionary mystery of infrared brain photons.

Why did evolution push human brain biophotons into the near-infrared (865nm)
where our eyes can't see them? This explores possible adaptive advantages.

Hypotheses:
1. Accidental byproduct of myelination for speed
2. Infrared penetrates tissue better (communication?)
3. Avoids interference with vision
4. Thermal management
5. Something we haven't thought of yet...
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson

# Import our data
try:
    from .literature_data import WANG_2016_SPECIES
    from .detection import detector_efficiency_curve
    from .constants import N_MYELIN
except ImportError:
    from literature_data import WANG_2016_SPECIES
    from detection import detector_efficiency_curve
    
# Physical constants
TISSUE_ABSORPTION_COEFFICIENTS = {
    # μa (1/cm) at different wavelengths
    400: 0.5,   # High absorption (hemoglobin, melanin)
    500: 0.3,   # Moderate
    600: 0.2,   # Lower
    700: 0.15,  # Optical window begins
    800: 0.12,  # Good penetration
    865: 0.10,  # Human brain peak - excellent penetration!
    900: 0.11,  # Water absorption starts
    1000: 0.15, # Water absorption increases
    1200: 0.25  # Strong water absorption
}

TISSUE_SCATTERING_COEFFICIENTS = {
    # μs' (1/cm) reduced scattering
    400: 20,    # Very high scattering
    500: 15,    # High
    600: 12,    # Moderate
    700: 10,    # Lower
    800: 8,     # Low scattering
    865: 7.5,   # Human brain peak
    900: 7,     # Minimal scattering
    1000: 6.5,  # Low
    1200: 6     # Low
}

def tissue_penetration_depth(wavelength_nm):
    """
    Calculate 1/e penetration depth in brain tissue.
    
    Uses diffusion approximation: δ = 1/√(3μa(μa + μs'))
    """
    # Interpolate coefficients
    wavelengths = sorted(TISSUE_ABSORPTION_COEFFICIENTS.keys())
    absorptions = [TISSUE_ABSORPTION_COEFFICIENTS[w] for w in wavelengths]
    scatterings = [TISSUE_SCATTERING_COEFFICIENTS[w] for w in wavelengths]
    
    μa = np.interp(wavelength_nm, wavelengths, absorptions)
    μs_prime = np.interp(wavelength_nm, wavelengths, scatterings)
    
    # Diffusion approximation
    μt_prime = μa + μs_prime
    δ = 1 / np.sqrt(3 * μa * μt_prime)  # cm
    
    return δ * 10  # Convert to mm

def analyze_species_evolution():
    """Analyze the evolutionary progression of biophoton wavelengths."""
    
    print("=== Evolutionary Analysis of Brain Biophoton Redshift ===\n")
    
    # Get species data
    species_order = ['bullfrog', 'mouse', 'pig', 'monkey', 'human']
    
    # Calculate various metrics for each species
    results = []
    
    for species in species_order:
        peak_nm = WANG_2016_SPECIES[species]['peak_nm']
        
        # Tissue penetration
        penetration_mm = tissue_penetration_depth(peak_nm)
        
        # Visual system sensitivity (rough approximation)
        # Most vertebrates peak sensitivity ~500-550nm
        visual_overlap = np.exp(-0.5 * ((peak_nm - 525) / 100)**2)
        
        # Brain size correlation (very rough)
        brain_sizes = {
            'bullfrog': 0.1,    # grams
            'mouse': 0.4,
            'pig': 180,
            'monkey': 100,
            'human': 1400
        }
        brain_mass = brain_sizes[species]
        
        # Myelin content estimate
        myelin_fractions = {
            'bullfrog': 0.05,   # Minimal white matter
            'mouse': 0.10,
            'pig': 0.35,
            'monkey': 0.40,
            'human': 0.45       # Highest white matter fraction
        }
        myelin = myelin_fractions[species]
        
        results.append({
            'species': species.capitalize(),
            'peak_nm': peak_nm,
            'penetration_mm': penetration_mm,
            'visual_overlap': visual_overlap,
            'brain_mass_g': brain_mass,
            'myelin_fraction': myelin
        })
    
    # Print analysis
    print("Species | Peak | Penetration | Visual Overlap | Brain Mass | Myelin %")
    print("-" * 75)
    
    for r in results:
        print(f"{r['species']:8} | {r['peak_nm']:3d}nm | {r['penetration_mm']:6.1f}mm | "
              f"{r['visual_overlap']:13.1%} | {r['brain_mass_g']:8.1f}g | {r['myelin_fraction']:7.0%}")
    
    # Correlation analysis
    peaks = [r['peak_nm'] for r in results]
    penetrations = [r['penetration_mm'] for r in results]
    brain_masses = [r['brain_mass_g'] for r in results]
    myelin_fractions = [r['myelin_fraction'] for r in results]
    
    # Log transform brain mass for correlation
    log_brain_masses = np.log10(brain_masses)
    
    # Correlations
    from scipy.stats import pearsonr
    
    r_brain, p_brain = pearsonr(peaks, log_brain_masses)
    r_myelin, p_myelin = pearsonr(peaks, myelin_fractions)
    r_penetration, p_penetration = pearsonr(peaks, penetrations)
    
    print(f"\n\nCorrelations with peak wavelength:")
    print(f"  Brain mass (log): r={r_brain:.3f}, p={p_brain:.3f}")
    print(f"  Myelin fraction:  r={r_myelin:.3f}, p={p_myelin:.3f}")
    print(f"  Tissue penetration: r={r_penetration:.3f}, p={p_penetration:.3f}")
    
    return results

def explore_adaptive_advantages():
    """Explore potential adaptive advantages of IR brain photons."""
    
    print("\n\n=== Potential Adaptive Advantages of 865nm Peak ===\n")
    
    # 1. Tissue penetration advantage
    wavelengths = np.linspace(400, 1000, 601)
    penetrations = [tissue_penetration_depth(w) for w in wavelengths]
    
    human_penetration = tissue_penetration_depth(865)
    bullfrog_penetration = tissue_penetration_depth(600)
    
    print(f"1. TISSUE PENETRATION:")
    print(f"   Human (865nm): {human_penetration:.1f}mm")
    print(f"   Bullfrog (600nm): {bullfrog_penetration:.1f}mm")
    print(f"   Advantage: {human_penetration/bullfrog_penetration:.1f}× deeper penetration")
    
    # 2. Visual interference
    print(f"\n2. VISUAL SYSTEM INTERFERENCE:")
    
    # Rod spectral sensitivity (peak ~498nm)
    rod_sensitivity = np.exp(-0.5 * ((wavelengths - 498) / 50)**2)
    
    # Cone sensitivities (S: 420nm, M: 534nm, L: 564nm)
    s_cone = np.exp(-0.5 * ((wavelengths - 420) / 30)**2)
    m_cone = np.exp(-0.5 * ((wavelengths - 534) / 40)**2)
    l_cone = np.exp(-0.5 * ((wavelengths - 564) / 40)**2)
    
    total_visual = rod_sensitivity + s_cone + m_cone + l_cone
    
    human_visual = np.interp(865, wavelengths, total_visual)
    bullfrog_visual = np.interp(600, wavelengths, total_visual)
    
    print(f"   Human (865nm): {human_visual:.1e} (essentially zero)")
    print(f"   Bullfrog (600nm): {bullfrog_visual:.3f}")
    print(f"   Advantage: No interference with vision")
    
    # 3. Thermal considerations
    print(f"\n3. THERMAL MANAGEMENT:")
    
    # Planck's law peak
    T_brain = 310  # K (37°C)
    peak_thermal = 2898 / T_brain * 1000  # Wien's law, nm
    
    print(f"   Brain thermal peak: {peak_thermal:.0f}nm")
    print(f"   Human biophoton: 865nm")
    print(f"   Overlap with thermal: Minimal (good for signal/noise)")
    
    # 4. Communication hypothesis
    print(f"\n4. OPTICAL COMMUNICATION HYPOTHESIS:")
    
    # Calculate communication range
    # Simple exponential decay model
    source_intensity = 1  # arbitrary units
    noise_floor = 0.01
    
    comm_range_865 = -np.log(noise_floor) / (1/tissue_penetration_depth(865))
    comm_range_600 = -np.log(noise_floor) / (1/tissue_penetration_depth(600))
    
    print(f"   Theoretical communication range:")
    print(f"   - At 865nm: {comm_range_865:.1f}mm")
    print(f"   - At 600nm: {comm_range_600:.1f}mm")
    print(f"   Advantage: {comm_range_865/comm_range_600:.1f}× longer range")
    
    return wavelengths, penetrations, total_visual

def plot_evolutionary_advantage():
    """Visualize the evolutionary optimization."""
    
    wavelengths, penetrations, visual_sensitivity = explore_adaptive_advantages()
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    
    # Top: Tissue penetration vs wavelength
    ax1.plot(wavelengths, penetrations, 'b-', linewidth=2)
    
    # Mark species
    for species in ['bullfrog', 'mouse', 'pig', 'monkey', 'human']:
        peak = WANG_2016_SPECIES[species]['peak_nm']
        pen = tissue_penetration_depth(peak)
        color = {'bullfrog': 'green', 'mouse': 'orange', 'pig': 'pink', 
                'monkey': 'brown', 'human': 'purple'}[species]
        ax1.plot(peak, pen, 'o', color=color, markersize=10, label=species.capitalize())
    
    ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Penetration Depth (mm)')
    ax1.set_title('Tissue Penetration Advantage of IR Shift')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Middle: Visual sensitivity
    ax2.plot(wavelengths, visual_sensitivity, 'g-', linewidth=2, label='Human visual sensitivity')
    ax2.fill_between(wavelengths, 0, visual_sensitivity, alpha=0.3, color='yellow')
    
    # Mark species peaks
    for species in ['bullfrog', 'mouse', 'human']:
        peak = WANG_2016_SPECIES[species]['peak_nm']
        ax2.axvline(peak, color={'bullfrog': 'green', 'mouse': 'orange', 'human': 'purple'}[species],
                   linestyle='--', label=f'{species.capitalize()} peak')
    
    ax2.set_xlabel('Wavelength (nm)')
    ax2.set_ylabel('Visual System Sensitivity')
    ax2.set_title('Avoiding Visual Interference')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Bottom: Combined optimization landscape
    # Create a fitness function combining penetration and avoiding visual interference
    penetration_norm = np.array(penetrations) / max(penetrations)
    visual_avoidance = 1 - visual_sensitivity / max(visual_sensitivity)
    
    fitness = penetration_norm * visual_avoidance
    
    ax3.plot(wavelengths, fitness, 'purple', linewidth=3, label='Evolutionary fitness')
    ax3.fill_between(wavelengths, 0, fitness, alpha=0.3, color='purple')
    
    # Mark human peak
    human_peak = 865
    human_fitness = np.interp(human_peak, wavelengths, fitness)
    ax3.plot(human_peak, human_fitness, 'r*', markersize=20, label='Human brain')
    
    # Find optimal wavelength
    optimal_idx = np.argmax(fitness)
    optimal_wavelength = wavelengths[optimal_idx]
    ax3.axvline(optimal_wavelength, color='red', linestyle=':', 
                label=f'Optimal: {optimal_wavelength:.0f}nm')
    
    ax3.set_xlabel('Wavelength (nm)')
    ax3.set_ylabel('Evolutionary Fitness Score')
    ax3.set_title('Optimization Landscape: Penetration × Visual Avoidance')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.suptitle('The Evolutionary Drive Toward Infrared Brain Photons', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('evolutionary_optimization.png', dpi=300, bbox_inches='tight')
    print("\n\nSaved evolutionary_optimization.png")

def speculative_functions():
    """Explore more speculative functions of IR brain photons."""
    
    print("\n\n=== Speculative Functions of IR Brain Photons ===\n")
    
    print("1. QUANTUM BRAIN HYPOTHESIS (Penrose-Hameroff):")
    print("   - IR photons less likely to cause decoherence")
    print("   - Could maintain quantum states slightly longer")
    print("   - Still probably too warm, but interesting...")
    
    print("\n2. OPTOGENETIC-LIKE SIGNALING:")
    print("   - Some proteins sensitive to IR (cryptochromes?)")
    print("   - Could modulate cellular activity")
    print("   - Natural optogenetics before we invented it?")
    
    print("\n3. WASTE HEAT MANAGEMENT:")
    print("   - Brain uses 20% of body's energy")
    print("   - IR emission could help thermal regulation")
    print("   - Photons as information + cooling?")
    
    print("\n4. INTER-BRAIN COMMUNICATION:")
    print("   - Mother-infant bonding")
    print("   - Close-contact emotional transmission")
    print("   - Would explain 'sensing' others' moods")
    
    print("\n5. EVOLUTIONARY SPANDREL:")
    print("   - Just a byproduct of myelination for speed")
    print("   - No adaptive function needed")
    print("   - Occam's razor says this is most likely...")
    
    print("\n\nFuture experiments to test these:")
    print("- Block IR transmission between bonded pairs")
    print("- Look for IR-sensitive proteins in neurons")
    print("- Measure IR emission during different cognitive states")
    print("- Check if IR correlates with EEG/fMRI signals")

if __name__ == "__main__":
    results = analyze_species_evolution()
    wavelengths, penetrations, visual = explore_adaptive_advantages()
    plot_evolutionary_advantage()
    speculative_functions()
    
    print("\n\n=== The Big Picture ===")
    print("Evolution pushed our brain's photons beyond our vision.")
    print("Whether this is adaptive or accidental remains a mystery.")
    print("But it creates a unique technical challenge for detection!")
    print("\nIrony: We evolved to emit light we cannot see.")