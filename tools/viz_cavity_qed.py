#!/usr/bin/env python3
"""
Visualization of Liu et al. cavity QED model.
Shows why quantum effects are negligible in biophoton measurements.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))

from cavity_qed import (
    cavity_coupling_g, cooperativity, entanglement_degradation,
    photon_generation_rate, liu_model_critique
)

def plot_cavity_qed_analysis(save_path="cavity_qed_analysis.png"):
    """Create 4-panel figure explaining cavity QED irrelevance."""
    
    fig = plt.figure(figsize=(14, 10))
    
    # Panel 1: Cavity schematic
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # Draw myelin layers
    for i in range(5):
        y = 2 + i * 1.2
        rect = FancyBboxPatch((1, y), 8, 0.8, boxstyle="round,pad=0.1",
                              facecolor='lightblue', edgecolor='darkblue', linewidth=2)
        ax1.add_patch(rect)
        if i == 2:
            ax1.text(5, y+0.4, 'Myelin layer', ha='center', va='center', fontsize=10)
    
    # Add cavity mode
    x = np.linspace(1.5, 8.5, 100)
    y_mode = 5 + 2*np.sin(2*np.pi*x/7)
    ax1.plot(x, y_mode, 'r--', linewidth=2, label='Cavity mode')
    
    # Add C-H bonds
    for x_pos in [3, 5, 7]:
        ax1.plot([x_pos, x_pos], [4.5, 5.5], 'k-', linewidth=3)
        ax1.text(x_pos, 4.2, 'C-H', ha='center', fontsize=8)
    
    ax1.set_title('A) Myelin "Cavity" (Liu et al. concept)')
    ax1.axis('off')
    ax1.legend(loc='upper right')
    
    # Panel 2: Coupling strength comparison
    ax2 = plt.subplot(2, 2, 2)
    
    critique = liu_model_critique()
    
    # Energy scales
    energies = {
        'Thermal (kT)': 0.0267,  # eV at 310K
        'Liu coupling (g)': critique['cavity_coupling_eV'],
        'Molecular vibration': 0.4,  # C-H stretch
        'Visible photon': 2.0,  # ~600 nm
    }
    
    colors = ['red', 'blue', 'green', 'purple']
    y_pos = np.arange(len(energies))
    values = list(energies.values())
    
    bars = ax2.barh(y_pos, values, color=colors)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(list(energies.keys()))
    ax2.set_xlabel('Energy (eV)')
    ax2.set_xscale('log')
    ax2.set_xlim(1e-10, 10)
    ax2.set_title('B) Energy Scale Comparison')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add text labels
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax2.text(value * 1.5, bar.get_y() + bar.get_height()/2,
                f'{value:.1e} eV', va='center', fontsize=9)
    
    # Mark weak coupling
    ax2.axvline(energies['Thermal (kT)'], color='red', linestyle='--', alpha=0.5)
    ax2.text(0.05, 0.5, 'g << kT\n(no quantum effects)', transform=ax2.transAxes,
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # Panel 3: Entanglement decay
    ax3 = plt.subplot(2, 2, 3)
    
    times_ps = np.logspace(-3, 3, 1000)  # 0.001 ps to 1000 ps
    S_remaining = [entanglement_degradation(1.0, t/1000, 0.001) for t in times_ps]
    
    ax3.semilogx(times_ps, S_remaining, 'b-', linewidth=3)
    ax3.axhline(0.01, color='red', linestyle='--', label='Classical threshold')
    ax3.axvline(1.0, color='green', linestyle=':', label='Measurement limit (~1 ps)')
    
    ax3.fill_between(times_ps, 0, S_remaining, where=(times_ps < 1), 
                     alpha=0.3, color='blue', label='Quantum regime')
    ax3.fill_between(times_ps, 0, 1, where=(times_ps > 1), 
                     alpha=0.3, color='red', label='Classical only')
    
    ax3.set_xlabel('Time (ps)')
    ax3.set_ylabel('Entanglement (bits)')
    ax3.set_title('C) Quantum Decoherence in Biology')
    ax3.set_ylim(0, 1.1)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Panel 4: Emission comparison pie chart
    ax4 = plt.subplot(2, 2, 4)
    
    # Get emission rates
    pair_rate, thermal_singles = photon_generation_rate()
    
    # For visible light (our actual measurements)
    visible_emissions = {
        'ROS (chemical)': 100,  # photons/s/cm² typical
        'Nanoantenna (electrical)': 1,  # Zangari estimate
        'Thermal (blackbody)': 0.001,  # negligible at 310K for visible
        'Liu QED (pairs)': pair_rate * 1e15  # Scale up to make visible
    }
    
    # Remove near-zero values for pie chart
    filtered_emissions = {k: v for k, v in visible_emissions.items() if v > 0.01}
    
    labels = list(filtered_emissions.keys())
    sizes = list(filtered_emissions.values())
    colors = ['lightcoral', 'lightskyblue', 'lightgreen', 'plum']
    
    # Explode the tiny quantum slice
    explode = [0.1 if 'QED' in label else 0 for label in labels]
    
    wedges, texts, autotexts = ax4.pie(sizes, labels=labels, colors=colors, 
                                        autopct='%1.1f%%', startangle=90,
                                        explode=explode)
    
    ax4.set_title('D) Visible Biophoton Sources')
    
    # Add note about quantum contribution
    ax4.text(0.5, -1.3, 'Note: Liu QED contribution enlarged 10¹⁵× to be visible',
             ha='center', transform=ax4.transAxes, fontsize=10, style='italic')
    
    # Overall title and summary
    fig.suptitle('Why Quantum Effects Don\'t Matter for Biophotons', fontsize=16, fontweight='bold')
    
    # Add summary text box
    summary_text = """Key Points:
• Coupling g = 0.1 µeV << thermal energy kT = 27 meV
• Entanglement destroyed in < 1 ps (unmeasurable)
• Classical sources dominate by >10¹⁵×
• Standard detection appropriate"""
    
    fig.text(0.5, 0.02, summary_text, ha='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, bottom=0.15)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved cavity QED analysis to {save_path}")

def plot_emission_spectrum_comparison(save_path="emission_spectrum_comparison.png"):
    """Compare different emission mechanisms across wavelengths."""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    wavelengths = np.linspace(200, 1200, 1000)
    
    # ROS emission (broad visible peak)
    ros_spectrum = np.exp(-0.5 * ((wavelengths - 550) / 150)**2)
    
    # Nanoantenna emission (IR peaked)
    antenna_spectrum = np.exp(-0.5 * ((wavelengths - 850) / 200)**2)
    
    # Thermal emission at 310K (Planck's law, normalized)
    h = 6.626e-34
    c = 3e8
    k = 1.381e-23
    T = 310
    wavelength_m = wavelengths * 1e-9
    thermal_spectrum = 2*h*c**2 / (wavelength_m**5 * (np.exp(h*c/(wavelength_m*k*T)) - 1))
    thermal_spectrum = thermal_spectrum / np.max(thermal_spectrum) * 0.1  # Scale for visibility
    
    # Liu QED (would be at 3300 nm, off scale)
    qed_wavelength = 3300
    ax.axvline(qed_wavelength, color='purple', linestyle='--', alpha=0.7, label='Liu QED (3.3 µm)')
    
    # Plot spectra
    ax.plot(wavelengths, ros_spectrum, 'r-', linewidth=3, label='ROS (chemical)')
    ax.plot(wavelengths, antenna_spectrum, 'b-', linewidth=3, label='Nanoantenna (Zangari)')
    ax.plot(wavelengths, thermal_spectrum, 'k:', linewidth=2, label='Thermal (310K)')
    
    # Add detector ranges
    ax.axvspan(200, 850, alpha=0.1, color='blue', label='Si detector')
    ax.axvspan(850, 1200, alpha=0.1, color='red', label='InGaAs needed')
    
    # Mark key wavelengths
    ax.axvline(648, color='green', linestyle=':', alpha=0.7, label='Mouse WT')
    ax.axvline(865, color='purple', linestyle=':', alpha=0.7, label='Human brain')
    
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Normalized Emission')
    ax.set_title('Biophoton Emission Mechanisms vs Wavelength')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(200, 1200)
    ax.set_ylim(0, 1.2)
    
    # Add text annotations
    ax.text(550, 1.05, 'Visible\nrange', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax.text(1000, 0.5, 'IR range', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='orange', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved emission spectrum comparison to {save_path}")

if __name__ == "__main__":
    plot_cavity_qed_analysis()
    plot_emission_spectrum_comparison()