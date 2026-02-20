"""
Two-mechanism spectral shift model: metabolic + waveguide.

Based on Dai 2020 synaptosome data showing myelin-independent blueshift.

Key insight: Spectral centroid shifts have TWO independent components:
1. Metabolic/oxidative stress (~35nm, myelin-independent, drug-reversible)
2. Waveguide geometry (~31nm, myelin-dependent, structural)

Evidence:
- Dai 2023: Blueshift occurs in myelin-FREE synaptosomes
- Partially reversed by ifenprodil (NMDA blocker): 582→617nm (~35nm)
- This metabolic component is independent of g-ratio

This explains why:
- Remyelinated tissue (g=0.825) doesn't follow demyelination curve
- Single waveguide model can't fit all reference points simultaneously
- AD/VaD have different spectral signatures despite similar demyelination
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

# Add models directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class TwoMechanismState:
    """Combined metabolic + waveguide spectral state."""
    
    g_ratio: float
    metabolic_stress: float  # 0-1, unitless stress factor
    week: float
    region: Literal["splenium", "DHC", "genu"] = "splenium"
    
    @property
    def waveguide_centroid(self) -> float:
        """Pure waveguide contribution (nm)."""
        return waveguide_spectral_shift(self.g_ratio)
    
    @property
    def metabolic_centroid(self) -> float:
        """Pure metabolic contribution (nm)."""
        return metabolic_spectral_shift(self.metabolic_stress)
    
    @property
    def combined_centroid(self) -> float:
        """Combined spectral centroid (nm)."""
        # Both mechanisms shift spectrum blue (subtract from baseline)
        # They act independently and additively
        baseline = 794.0  # healthy baseline (nm)
        waveguide_shift = baseline - self.waveguide_centroid
        metabolic_shift = baseline - self.metabolic_centroid
        
        # Combined shift is sum of individual shifts
        total_shift = waveguide_shift + metabolic_shift
        return baseline - total_shift


def waveguide_spectral_shift(g_ratio: float) -> float:
    """
    Pure waveguide geometry effect on spectral centroid.
    
    Reference points (from Telegram pack, waveguide component only):
    - g=0.802 (healthy): 794nm baseline
    - g=0.825 (remyelinated, low stress): ~785nm (9nm shift)
    - g=0.926 (week 4): ~765nm (29nm shift)
    - g=0.964 (peak demyelination): ~763nm (31nm shift)
    
    Waveguide shift saturates at high g-ratio (all modes cut off).
    """
    g_healthy = 0.802
    centroid_healthy = 794.0
    
    if g_ratio <= g_healthy:
        return centroid_healthy
    
    # Piecewise linear model for waveguide effect
    # Shift increases rapidly 0.80→0.88, then saturates
    if g_ratio <= 0.88:
        # Linear region: 0→20nm shift over g=0.802→0.88
        max_shift_linear = 20.0
        g_range = 0.88 - g_healthy
        shift = max_shift_linear * (g_ratio - g_healthy) / g_range
    else:
        # Saturation region: approaches ~31nm asymptotically
        max_shift_saturated = 31.0
        # Exponential approach to saturation
        excess = g_ratio - 0.88
        remaining = max_shift_saturated - 20.0
        shift = 20.0 + remaining * (1 - np.exp(-excess / 0.05))
    
    return centroid_healthy - shift


def metabolic_spectral_shift(stress_factor: float) -> float:
    """
    Pure metabolic/oxidative stress effect on spectral centroid.
    
    Reference points (from Dai 2023 ifenprodil reversal):
    - stress=0 (healthy): 794nm baseline
    - stress=1 (peak AD): 582nm → ifenprodil → 617nm
      - Total shift: 212nm (794→582)
      - Reversible (metabolic) component: ~35nm (582→617)
      - Irreversible (structural) component: ~177nm (617→794, includes waveguide)
    
    For cuprizone:
    - Week 0: stress ≈ 0.0
    - Week 4-6: stress ≈ 0.6-0.8 (acute demyelination → oxidative stress)
    - Week 13: stress ≈ 0.1-0.2 (recovery, but some residual inflammation)
    
    Metabolic shift is roughly linear with stress up to saturation (~35nm max).
    """
    baseline = 794.0
    max_metabolic_shift = 35.0  # from ifenprodil reversal
    
    # Linear relationship: stress → blueshift
    shift = max_metabolic_shift * np.clip(stress_factor, 0.0, 1.0)
    
    return baseline - shift


def cuprizone_metabolic_stress(week: float) -> float:
    """
    Metabolic stress timeline for cuprizone model.
    
    Based on:
    - Oxidative stress markers peak around week 4-6
    - Inflammation continues during early remyelination
    - Slowly resolves but never fully returns to baseline
    
    Timeline:
    - Week 0: 0.0 (healthy)
    - Week 4: 0.6 (rising oxidative stress)
    - Week 6: 0.8 (peak demyelination + inflammation)
    - Week 8: 0.5 (recovery starting, still inflamed)
    - Week 13+: 0.1-0.2 (residual low-grade inflammation)
    """
    week = max(0.0, float(week))
    
    if week <= 6.0:
        # Demyelination phase: stress rises
        # Sigmoid curve
        k = 1.5
        midpoint = 3.5
        peak_stress = 0.8
        stress = peak_stress / (1 + np.exp(-k * (week - midpoint)))
    
    else:
        # Recovery phase: stress decays but not to zero
        peak_stress = 0.8
        residual_stress = 0.15
        tau = 4.0  # weeks, decay timescale
        
        recovery_time = week - 6.0
        stress = residual_stress + (peak_stress - residual_stress) * np.exp(-recovery_time / tau)
    
    return float(np.clip(stress, 0.0, 1.0))


def cuprizone_two_mechanism(
    week: float,
    region: Literal["splenium", "DHC", "genu"] = "splenium",
) -> TwoMechanismState:
    """
    Full two-mechanism cuprizone timeline.
    
    Combines:
    - G-ratio evolution (structural, from cuprizone_v2.py)
    - Metabolic stress timeline (oxidative, independent)
    
    Returns TwoMechanismState with both components.
    """
    from cuprizone_v2 import cuprizone_gratio
    
    g_ratio = cuprizone_gratio(week, region=region)
    stress = cuprizone_metabolic_stress(week)
    
    return TwoMechanismState(
        g_ratio=g_ratio,
        metabolic_stress=stress,
        week=week,
        region=region,
    )


def generate_two_mechanism_timeline(
    weeks: int = 13,
    region: Literal["splenium", "DHC", "genu"] = "splenium",
) -> dict[str, np.ndarray]:
    """
    Generate complete two-mechanism timeline.
    
    Returns dict with:
    - weeks: array of timepoints
    - g_ratio: g-ratio at each timepoint
    - metabolic_stress: stress factor (0-1)
    - centroid_waveguide: waveguide component only (nm)
    - centroid_metabolic: metabolic component only (nm)
    - centroid_combined: total predicted centroid (nm)
    """
    timepoints = np.linspace(0, weeks, weeks * 4 + 1)
    
    states = [cuprizone_two_mechanism(w, region=region) for w in timepoints]
    
    g_ratios = np.array([s.g_ratio for s in states])
    stresses = np.array([s.metabolic_stress for s in states])
    centroid_wg = np.array([s.waveguide_centroid for s in states])
    centroid_met = np.array([s.metabolic_centroid for s in states])
    centroid_combined = np.array([s.combined_centroid for s in states])
    
    return {
        "weeks": timepoints,
        "g_ratio": g_ratios,
        "metabolic_stress": stresses,
        "centroid_waveguide_nm": centroid_wg,
        "centroid_metabolic_nm": centroid_met,
        "centroid_combined_nm": centroid_combined,
    }


def multi_region_two_mechanism(weeks: int = 13) -> dict[str, dict[str, np.ndarray]]:
    """Generate two-mechanism timeline for all three regions."""
    return {
        "splenium": generate_two_mechanism_timeline(weeks, "splenium"),
        "DHC": generate_two_mechanism_timeline(weeks, "DHC"),
        "genu": generate_two_mechanism_timeline(weeks, "genu"),
    }


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Generate multi-region timeline
    data = multi_region_two_mechanism(weeks=13)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # G-ratio over time
    ax = axes[0, 0]
    for region, timeline in data.items():
        ax.plot(timeline["weeks"], timeline["g_ratio"], label=region, linewidth=2)
    ax.axhline(0.802, color='green', linestyle='--', alpha=0.5, label='Healthy')
    ax.axvline(6, color='red', linestyle='--', alpha=0.3, label='Cuprizone withdrawn')
    ax.set_xlabel("Week")
    ax.set_ylabel("G-ratio")
    ax.set_title("G-Ratio (Structural)")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Metabolic stress
    ax = axes[0, 1]
    for region, timeline in data.items():
        ax.plot(timeline["weeks"], timeline["metabolic_stress"], label=region, linewidth=2)
    ax.axvline(6, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel("Week")
    ax.set_ylabel("Metabolic Stress (0-1)")
    ax.set_title("Oxidative Stress (Independent)")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Combined centroid
    ax = axes[0, 2]
    for region, timeline in data.items():
        ax.plot(timeline["weeks"], timeline["centroid_combined_nm"], label=region, linewidth=2)
    ax.axhline(794, color='green', linestyle='--', alpha=0.5, label='Healthy')
    ax.axhline(768, color='orange', linestyle='--', alpha=0.5, label='Target remyelinated')
    ax.axhline(581, color='red', linestyle='--', alpha=0.5, label='Target peak')
    ax.axvline(6, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel("Week")
    ax.set_ylabel("Spectral Centroid (nm)")
    ax.set_title("Combined Prediction")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Component breakdown (splenium only)
    ax = axes[1, 0]
    splen = data["splenium"]
    ax.plot(splen["weeks"], splen["centroid_waveguide_nm"], 
            label="Waveguide only", linewidth=2, linestyle='--')
    ax.plot(splen["weeks"], splen["centroid_metabolic_nm"], 
            label="Metabolic only", linewidth=2, linestyle='--')
    ax.plot(splen["weeks"], splen["centroid_combined_nm"], 
            label="Combined", linewidth=2, color='black')
    ax.axhline(794, color='green', linestyle='--', alpha=0.3)
    ax.axvline(6, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel("Week")
    ax.set_ylabel("Spectral Centroid (nm)")
    ax.set_title("Mechanism Decomposition (Splenium)")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Shift magnitude comparison
    ax = axes[1, 1]
    for region, timeline in data.items():
        shift = 794 - timeline["centroid_combined_nm"]
        ax.plot(timeline["weeks"], shift, label=region, linewidth=2)
    ax.axhline(0, color='green', linestyle='--', alpha=0.5, label='No shift')
    ax.axhline(213, color='red', linestyle='--', alpha=0.5, label='Target peak (581nm)')
    ax.axhline(26, color='orange', linestyle='--', alpha=0.5, label='Target remyelin (768nm)')
    ax.axvline(6, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel("Week")
    ax.set_ylabel("Blue Shift from Healthy (nm)")
    ax.set_title("Total Spectral Shift")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Reference point comparison
    ax = axes[1, 2]
    splen = data["splenium"]
    
    # Reference points from literature
    ref_weeks = np.array([0, 6, 13])
    ref_centroids = np.array([794, 581, 768])
    
    # Our predictions
    pred_idx = [0, 24, 52]  # week 0, 6, 13 indices
    pred_centroids = splen["centroid_combined_nm"][pred_idx]
    
    ax.scatter(ref_weeks, ref_centroids, s=100, marker='o', 
              label='Target (literature)', color='red', zorder=10)
    ax.scatter(ref_weeks, pred_centroids, s=100, marker='x', 
              label='Predicted (two-mechanism)', color='blue', zorder=10)
    ax.plot(splen["weeks"], splen["centroid_combined_nm"], 
           alpha=0.5, linewidth=2, color='blue')
    
    # Connect with error bars
    for w, ref, pred in zip(ref_weeks, ref_centroids, pred_centroids):
        ax.plot([w, w], [ref, pred], 'k--', alpha=0.3, linewidth=1)
        error = abs(ref - pred)
        ax.text(w + 0.3, (ref + pred) / 2, f'Δ={error:.0f}nm', 
               fontsize=8, ha='left')
    
    ax.set_xlabel("Week")
    ax.set_ylabel("Spectral Centroid (nm)")
    ax.set_title("Prediction vs Target (Splenium)")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlim(-0.5, 13.5)
    
    plt.tight_layout()
    plt.savefig("/tmp/two_mechanism_timeline.png", dpi=150)
    print("Saved visualization to /tmp/two_mechanism_timeline.png")
    
    # Print key predictions vs targets
    print("\n=== KEY PREDICTIONS (Splenium) ===")
    print(f"Healthy (week 0):")
    print(f"  Target: 794nm")
    print(f"  Predicted: {pred_centroids[0]:.1f}nm")
    print(f"  Error: {abs(794 - pred_centroids[0]):.1f}nm\n")
    
    print(f"Peak demyelination (week 6):")
    print(f"  Target: 581nm")
    print(f"  Predicted: {pred_centroids[1]:.1f}nm")
    print(f"  Error: {abs(581 - pred_centroids[1]):.1f}nm\n")
    
    print(f"Stable remyelinated (week 13):")
    print(f"  Target: 768nm")
    print(f"  Predicted: {pred_centroids[2]:.1f}nm")
    print(f"  Error: {abs(768 - pred_centroids[2]):.1f}nm\n")
    
    # Mechanism breakdown at key timepoints
    print("=== MECHANISM BREAKDOWN ===")
    for i, (w, label) in enumerate([(0, "Week 0"), (6, "Week 6"), (13, "Week 13")]):
        idx = pred_idx[i]
        wg = splen["centroid_waveguide_nm"][idx]
        met = splen["centroid_metabolic_nm"][idx]
        comb = splen["centroid_combined_nm"][idx]
        wg_shift = 794 - wg
        met_shift = 794 - met
        total_shift = 794 - comb
        
        print(f"{label}:")
        print(f"  Waveguide: {wg:.1f}nm (shift: {wg_shift:.1f}nm)")
        print(f"  Metabolic: {met:.1f}nm (shift: {met_shift:.1f}nm)")
        print(f"  Combined: {comb:.1f}nm (total shift: {total_shift:.1f}nm)")
        print(f"  g-ratio: {splen['g_ratio'][idx]:.3f}, stress: {splen['metabolic_stress'][idx]:.2f}\n")
