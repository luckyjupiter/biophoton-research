"""
Inflammation-driven biophoton dynamics model.

Key insight: Inflammation precedes demyelination by days to weeks, creating
an early detection window. ROS amplification during inflammation could be
the most sensitive biomarker we have.

Based on:
- MS inflammation cascade timing
- Microglial activation kinetics  
- ROS burst from activated immune cells
- Cytokine-driven metabolic shifts
"""

import numpy as np
from scipy.integrate import odeint
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

# Import our models
try:
    from .constants import BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S
    from .emission_balance import ros_emission_spectrum
except ImportError:
    from constants import BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S
    from emission_balance import ros_emission_spectrum

class InflammationCascade:
    """Model the temporal dynamics of neuroinflammation → demyelination."""
    
    def __init__(self):
        # Timescales (days)
        self.t_trigger = 0  # Inflammatory trigger
        self.t_microglia = 1  # Microglial activation
        self.t_cytokine = 3  # Cytokine storm peak
        self.t_demyelin_start = 7  # Visible demyelination begins
        self.t_demyelin_peak = 21  # Peak demyelination
        
        # Amplification factors
        self.microglia_ros_factor = 5
        self.cytokine_ros_factor = 20
        self.demyelin_ros_factor = 50
        
        # Decay rates (1/days)
        self.k_microglia = 0.5
        self.k_cytokine = 0.3
        self.k_resolution = 0.1
    
    def microglia_activation(self, t):
        """Microglial response to inflammatory trigger."""
        if t < self.t_microglia:
            return 0
        
        # Rapid activation, slower resolution
        tau_rise = 0.5  # days
        tau_decay = 5   # days
        
        t_shifted = t - self.t_microglia
        
        # Double exponential for rise and decay
        activation = (1 - np.exp(-t_shifted / tau_rise)) * np.exp(-t_shifted / tau_decay)
        
        return np.clip(activation * 4, 0, 1)  # Scale to peak at ~1
    
    def cytokine_cascade(self, t, microglia):
        """Cytokine release driven by activated microglia."""
        # Delayed and amplified response
        if t < self.t_cytokine:
            return 0
        
        # Integrates microglial activity
        drive = microglia * 2
        tau = 2  # days
        
        cytokines = drive * (1 - np.exp(-(t - self.t_cytokine) / tau))
        
        return np.clip(cytokines, 0, 1)
    
    def demyelination_damage(self, t, cytokines):
        """Demyelination as downstream effect of inflammation."""
        if t < self.t_demyelin_start:
            return 0
        
        # Sigmoid progression
        t_rel = t - self.t_demyelin_start
        t_half = self.t_demyelin_peak - self.t_demyelin_start
        
        damage = cytokines * (1 / (1 + np.exp(-2 * (t_rel - t_half) / t_half)))
        
        return np.clip(damage, 0, 1)
    
    def ros_amplification(self, t):
        """Total ROS amplification factor over baseline."""
        microglia = self.microglia_activation(t)
        cytokines = self.cytokine_cascade(t, microglia)
        demyelin = self.demyelination_damage(t, cytokines)
        
        # Each process contributes
        amp = 1 + \
              microglia * (self.microglia_ros_factor - 1) + \
              cytokines * (self.cytokine_ros_factor - 1) + \
              demyelin * (self.demyelin_ros_factor - 1)
        
        return amp
    
    def biophoton_timecourse(self, t_days):
        """
        Calculate biophoton emission over disease course.
        
        Returns:
            times, total_emission, components (dict)
        """
        times = np.linspace(0, t_days, int(t_days * 24))  # Hourly resolution
        
        # Calculate components
        microglia = np.array([self.microglia_activation(t) for t in times])
        cytokines = np.array([self.cytokine_cascade(t, self.microglia_activation(t)) 
                             for t in times])
        demyelin = np.array([self.demyelination_damage(t, 
                           self.cytokine_cascade(t, self.microglia_activation(t)))
                           for t in times])
        
        # ROS amplification
        ros_amp = np.array([self.ros_amplification(t) for t in times])
        
        # Total emission
        baseline = BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S
        total_emission = baseline * ros_amp
        
        components = {
            'microglia': microglia,
            'cytokines': cytokines,
            'demyelination': demyelin,
            'ros_amplification': ros_amp
        }
        
        return times, total_emission, components
    
    def detection_windows(self, threshold_factor=2):
        """
        Find optimal detection windows before visible damage.
        
        Args:
            threshold_factor: Emission increase to trigger detection
            
        Returns:
            dict with window timings
        """
        times, emission, components = self.biophoton_timecourse(30)
        
        # Find when emission exceeds threshold
        baseline = BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S
        above_threshold = emission > baseline * threshold_factor
        
        if not any(above_threshold):
            return None
        
        # First detection
        first_detect_idx = np.where(above_threshold)[0][0]
        first_detect_time = times[first_detect_idx]
        
        # Peak inflammation (before demyelination)
        pre_demyelin_mask = times < self.t_demyelin_start
        peak_inflam_idx = np.argmax(emission[pre_demyelin_mask])
        peak_inflam_time = times[peak_inflam_idx]
        peak_inflam_emission = emission[peak_inflam_idx]
        
        # MRI visibility estimate (significant demyelination)
        demyelin_threshold = 0.3  # 30% myelin loss
        mri_visible_idx = np.where(components['demyelination'] > demyelin_threshold)[0]
        mri_visible_time = times[mri_visible_idx[0]] if len(mri_visible_idx) > 0 else None
        
        windows = {
            'first_detection_days': first_detect_time,
            'peak_inflammation_days': peak_inflam_time,
            'peak_inflammation_factor': peak_inflam_emission / baseline,
            'mri_visible_days': mri_visible_time,
            'early_warning_window_days': mri_visible_time - first_detect_time if mri_visible_time else None
        }
        
        return windows

def inflammatory_spectral_signature():
    """
    Model how inflammation changes the spectral signature.
    
    Different inflammatory mediators have distinct ROS signatures.
    """
    wavelengths = np.linspace(300, 900, 601)
    
    # Baseline healthy
    healthy_spectrum = ros_emission_spectrum(wavelengths, 'healthy')
    
    # Microglial activation - more UV/blue from NADPH oxidase
    microglia_spectrum = healthy_spectrum.copy()
    microglia_spectrum += 5 * np.exp(-0.5 * ((wavelengths - 420) / 60)**2)
    
    # Cytokine storm - broad spectrum ROS
    cytokine_spectrum = healthy_spectrum * 20  # Massive amplification
    
    # Demyelination - lipid peroxidation dominates
    demyelin_spectrum = healthy_spectrum.copy()
    demyelin_spectrum += 30 * np.exp(-0.5 * ((wavelengths - 480) / 80)**2)  # Lipid perox
    demyelin_spectrum += 10 * np.exp(-0.5 * ((wavelengths - 635) / 40)**2)  # Singlet O2
    
    signatures = {
        'healthy': healthy_spectrum,
        'microglia': microglia_spectrum,
        'cytokine': cytokine_spectrum,
        'demyelination': demyelin_spectrum
    }
    
    return wavelengths, signatures

def clinical_detection_analysis():
    """Analyze clinical feasibility of inflammation detection."""
    cascade = InflammationCascade()
    windows = cascade.detection_windows(threshold_factor=2)
    
    print("=== Clinical Detection Analysis ===\n")
    
    print("Detection Timeline:")
    print(f"  First 2× increase: Day {windows['first_detection_days']:.1f}")
    print(f"  Peak inflammation: Day {windows['peak_inflammation_days']:.1f} "
          f"({windows['peak_inflammation_factor']:.1f}× baseline)")
    if windows['mri_visible_days']:
        print(f"  MRI visible damage: Day {windows['mri_visible_days']:.1f}")
        print(f"  Early warning window: {windows['early_warning_window_days']:.1f} days")
    else:
        print("  MRI visible damage: Not reached in simulation")
    
    # Sensitivity analysis
    print("\n\nSensitivity Analysis:")
    for threshold in [1.5, 2, 3, 5, 10]:
        windows = cascade.detection_windows(threshold)
        if windows and windows['early_warning_window_days']:
            print(f"  {threshold}× threshold: {windows['early_warning_window_days']:.1f} day warning")
        elif windows:
            print(f"  {threshold}× threshold: Detected but no MRI visibility in simulation")
    
    # Spectral signatures
    wavelengths, signatures = inflammatory_spectral_signature()
    
    print("\n\nSpectral Fingerprints:")
    for stage, spectrum in signatures.items():
        peak_idx = np.argmax(spectrum)
        peak_wl = wavelengths[peak_idx]
        print(f"  {stage}: Peak at {peak_wl:.0f}nm")

def plot_inflammation_dynamics():
    """Visualize the inflammation → demyelination cascade."""
    cascade = InflammationCascade()
    times, emission, components = cascade.biophoton_timecourse(30)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    
    # Top: Components
    ax1.plot(times, components['microglia'], 'g-', linewidth=2, label='Microglia')
    ax1.plot(times, components['cytokines'], 'orange', linewidth=2, label='Cytokines')
    ax1.plot(times, components['demyelination'], 'r-', linewidth=2, label='Demyelination')
    
    ax1.axvline(cascade.t_demyelin_start, color='k', linestyle='--', alpha=0.5)
    ax1.text(cascade.t_demyelin_start + 0.5, 0.8, 'MRI visible', rotation=90)
    
    ax1.set_ylabel('Activation Level')
    ax1.set_title('Neuroinflammation Cascade Components')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Middle: ROS amplification
    ax2.plot(times, components['ros_amplification'], 'purple', linewidth=3)
    ax2.axhline(2, color='green', linestyle='--', label='2× detection threshold')
    ax2.axhline(10, color='orange', linestyle='--', label='10× clinical threshold')
    
    ax2.set_ylabel('ROS Amplification Factor')
    ax2.set_title('Reactive Oxygen Species Production')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Bottom: Biophoton emission
    ax3.plot(times, emission, 'b-', linewidth=3)
    ax3.fill_between(times, 0, emission, alpha=0.3)
    
    # Mark key timepoints
    windows = cascade.detection_windows()
    ax3.axvline(windows['first_detection_days'], color='green', linewidth=2, 
                label=f"First detection (Day {windows['first_detection_days']:.1f})")
    ax3.axvline(windows['peak_inflammation_days'], color='orange', linewidth=2,
                label=f"Peak inflammation (Day {windows['peak_inflammation_days']:.1f})")
    
    if windows['mri_visible_days']:
        ax3.axvline(windows['mri_visible_days'], color='red', linewidth=2,
                    label=f"MRI visible (Day {windows['mri_visible_days']:.1f})")
        # Add early warning window
        ax3.axvspan(windows['first_detection_days'], windows['mri_visible_days'],
                    alpha=0.2, color='yellow', label='Early warning window')
    else:
        # Just show inflammation window
        ax3.axvspan(windows['first_detection_days'], windows['peak_inflammation_days'],
                    alpha=0.2, color='orange', label='Inflammation window')
    
    ax3.set_xlabel('Time (days)')
    ax3.set_ylabel('Biophoton Emission (photons/cm²/s)')
    ax3.set_title('Total Biophoton Emission During MS Flare')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.suptitle('Inflammation-Driven Biophoton Dynamics: Early MS Detection Window',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('inflammation_dynamics.png', dpi=300, bbox_inches='tight')
    print("\nSaved inflammation_dynamics.png")

if __name__ == "__main__":
    clinical_detection_analysis()
    plot_inflammation_dynamics()
    
    # Extra analysis: repeated flares
    print("\n\n=== Repeated Flare Detection ===")
    print("MS typically has multiple inflammatory episodes...")
    print("Each leaves a spectral 'scar' even after clinical recovery")
    print("Cumulative optical damage could track disease progression better than MRI")