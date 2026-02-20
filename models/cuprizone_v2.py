"""
Improved cuprizone model using literature g-ratio data.

Based on Telegram biophoton research reference pack:
- Lindner et al. 2008: g-ratio measurements at weeks 0, 4, 6
- Sachs et al. 2014: remyelination timeline
- Regional heterogeneity (splenium vs DHC)
- Permanent residual blue shift in remyelinated state
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class GRatioState:
    """G-ratio based demyelination state.
    
    G-ratio = axon_radius / (axon_radius + myelin_thickness)
    
    Healthy: ~0.80
    Demyelinated: ~0.96
    Remyelinated: ~0.83 (never returns to 0.80)
    """
    
    g_ratio: float
    week: float
    region: Literal["splenium", "DHC", "genu"] = "splenium"
    
    @property
    def is_healthy(self) -> bool:
        return self.g_ratio <= 0.805
    
    @property
    def is_demyelinated(self) -> bool:
        return self.g_ratio >= 0.90
    
    @property
    def is_remyelinating(self) -> bool:
        return self.week > 6.0 and 0.80 < self.g_ratio < 0.90
    
    @property
    def myelin_fraction_remaining(self) -> float:
        """Fraction of myelin remaining relative to healthy.
        
        g = r_axon / r_total
        For fixed axon radius: thickness ∝ (1/g - 1)
        """
        g_healthy = 0.802
        if self.g_ratio >= 0.999:
            return 0.0
        thickness_ratio = (1.0 / self.g_ratio - 1.0) / (1.0 / g_healthy - 1.0)
        return np.clip(thickness_ratio, 0.0, 1.0)


def cuprizone_gratio(
    week: float,
    region: Literal["splenium", "DHC", "genu"] = "splenium",
    add_noise: bool = False,
    rng: np.random.Generator | None = None,
) -> float:
    """
    G-ratio timeline for cuprizone model.
    
    Data from Lindner et al. 2008 (EM measurements):
    - Week 0: 0.802 (healthy)
    - Week 4: 0.926
    - Week 6: 0.964 (peak demyelination)
    
    Remyelination (Sachs et al. 2014, Kipp et al. 2024):
    - Week 8 (+2): ~0.91
    - Week 11 (+5): ~0.845
    - Stable: ~0.825 (permanent residual, never returns to 0.802)
    
    Regional differences:
    - Splenium: fast remyelination
    - DHC: slow remyelination
    - Genu: moderate demyelination/remyelination
    """
    week = max(0.0, float(week))
    
    # Demyelination phase (weeks 0-6): sigmoid fit to literature data
    if week <= 6.0:
        # Sigmoid parameters fit to [0.802, 0.926, 0.964] at [0, 4, 6]
        g_peak = 0.964
        g_healthy = 0.802
        k = 2.5  # steepness
        midpoint = 3.8
        
        g_ratio = g_healthy + (g_peak - g_healthy) / (1 + np.exp(-k * (week - midpoint)))
    
    else:
        # Remyelination phase (weeks 6+)
        g_peak = 0.964
        
        # Regional recovery rate differences
        if region == "splenium":
            tau = 4.0  # weeks, fast recovery
            g_stable = 0.825
        elif region == "DHC":
            tau = 7.0  # weeks, slow recovery
            g_stable = 0.840  # worse final outcome
        else:  # genu
            tau = 5.5
            g_stable = 0.830
        
        # Exponential recovery toward stable state (never reaches healthy 0.802)
        recovery_time = week - 6.0
        g_ratio = g_stable + (g_peak - g_stable) * np.exp(-recovery_time / tau)
    
    # Add noise during early remyelination (weeks 6-8)
    if add_noise and 6.0 < week < 8.5:
        if rng is None:
            rng = np.random.default_rng()
        # High variance during early remyelination (Kipp et al. 2024)
        noise_std = 0.08 * (1 - (week - 6.0) / 2.5)  # decreases over time
        g_ratio += rng.normal(0, noise_std)
    
    return float(np.clip(g_ratio, 0.75, 0.99))


def gratio_to_spectral_centroid(
    g_ratio: float,
    model: Literal["simple", "quadratic"] = "quadratic",
) -> float:
    """
    Convert g-ratio to predicted spectral centroid (nm).
    
    From Telegram reference pack predictions:
    g=0.802 → 794nm (healthy)
    g=0.926 → 735nm (week 4)
    g=0.964 → 581nm (max demyelination, week 6)
    g=0.825 → 768nm (stable remyelinated)
    
    Models:
    - simple: piecewise linear
    - quadratic: quadratic fit through reference points
    """
    if model == "simple":
        # Piecewise linear interpolation through reference points
        if g_ratio <= 0.802:
            return 794.0
        elif g_ratio <= 0.825:
            # Interpolate between 0.802→794 and 0.825→768
            slope = (768 - 794) / (0.825 - 0.802)
            return 794 + slope * (g_ratio - 0.802)
        elif g_ratio <= 0.926:
            # Interpolate between 0.825→768 and 0.926→735
            slope = (735 - 768) / (0.926 - 0.825)
            return 768 + slope * (g_ratio - 0.825)
        else:
            # Interpolate between 0.926→735 and 0.964→581
            slope = (581 - 735) / (0.964 - 0.926)
            return 735 + slope * (g_ratio - 0.926)
    
    else:  # quadratic
        # Quadratic fit through 3 main points: (0.802, 794), (0.926, 735), (0.964, 581)
        # λ(g) = a*(g - g0)^2 + b*(g - g0) + c
        # Shift to g0 = 0.802 for numerical stability
        
        g_shifted = g_ratio - 0.802
        
        # Coefficients from exact least-squares fit
        # Perfect fit to reference points, but note:
        # - This predicts ~834nm for remyelinated g=0.825 (reference says ~768nm)
        # - Discrepancy suggests either:
        #   1. Remyelinated myelin has different optical properties (disordered)
        #   2. Reference points aren't on same curve
        #   3. Need more sophisticated waveguide model
        a = -22079.17
        b = 2262.01
        c = 794.0
        
        centroid = a * g_shifted**2 + b * g_shifted + c
    
    return float(np.clip(centroid, 450, 1000))


def generate_recovery_timeline(
    weeks: int = 13,
    region: Literal["splenium", "DHC", "genu"] = "splenium",
) -> dict[str, np.ndarray]:
    """
    Generate complete cuprizone timeline including recovery.
    
    Returns dict with:
    - weeks: array of timepoints
    - g_ratio: g-ratio at each timepoint
    - centroid: spectral centroid (nm)
    - myelin_fraction: fraction of myelin remaining
    """
    timepoints = np.linspace(0, weeks, weeks * 4 + 1)  # 4 measurements per week
    
    g_ratios = np.array([cuprizone_gratio(w, region=region) for w in timepoints])
    centroids = np.array([gratio_to_spectral_centroid(g) for g in g_ratios])
    
    states = [GRatioState(g, w, region) for g, w in zip(g_ratios, timepoints)]
    myelin_fractions = np.array([s.myelin_fraction_remaining for s in states])
    
    return {
        "weeks": timepoints,
        "g_ratio": g_ratios,
        "centroid_nm": centroids,
        "myelin_fraction": myelin_fractions,
    }


def multi_region_timeline(weeks: int = 13) -> dict[str, dict[str, np.ndarray]]:
    """Generate timeline for all three regions."""
    return {
        "splenium": generate_recovery_timeline(weeks, "splenium"),
        "DHC": generate_recovery_timeline(weeks, "DHC"),
        "genu": generate_recovery_timeline(weeks, "genu"),
    }


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Generate multi-region timeline
    data = multi_region_timeline(weeks=13)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # G-ratio over time
    ax = axes[0, 0]
    for region, timeline in data.items():
        ax.plot(timeline["weeks"], timeline["g_ratio"], label=region, linewidth=2)
    ax.axhline(0.802, color='green', linestyle='--', alpha=0.5, label='Healthy')
    ax.axhline(0.825, color='orange', linestyle='--', alpha=0.5, label='Remyelinated')
    ax.axvline(6, color='red', linestyle='--', alpha=0.3, label='Cuprizone withdrawn')
    ax.set_xlabel("Week")
    ax.set_ylabel("G-ratio")
    ax.set_title("G-Ratio Timeline (Cuprizone + Recovery)")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Spectral centroid
    ax = axes[0, 1]
    for region, timeline in data.items():
        ax.plot(timeline["weeks"], timeline["centroid_nm"], label=region, linewidth=2)
    ax.axhline(794, color='green', linestyle='--', alpha=0.5, label='Healthy')
    ax.axhline(768, color='orange', linestyle='--', alpha=0.5, label='Remyelinated')
    ax.axvline(6, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel("Week")
    ax.set_ylabel("Spectral Centroid (nm)")
    ax.set_title("Predicted Spectral Shift")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Myelin fraction remaining
    ax = axes[1, 0]
    for region, timeline in data.items():
        ax.plot(timeline["weeks"], timeline["myelin_fraction"], label=region, linewidth=2)
    ax.axhline(1.0, color='green', linestyle='--', alpha=0.5, label='Healthy')
    ax.axvline(6, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel("Week")
    ax.set_ylabel("Myelin Fraction Remaining")
    ax.set_title("Myelin Thickness Relative to Healthy")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Permanent blue shift
    ax = axes[1, 1]
    for region, timeline in data.items():
        final_centroid = timeline["centroid_nm"][-1]
        permanent_shift = 794 - final_centroid
        weeks = timeline["weeks"]
        shift = 794 - timeline["centroid_nm"]
        ax.plot(weeks, shift, label=f"{region} (Δ={permanent_shift:.0f}nm)", linewidth=2)
    ax.axhline(0, color='green', linestyle='--', alpha=0.5, label='No shift')
    ax.axvline(6, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel("Week")
    ax.set_ylabel("Blue Shift from Healthy (nm)")
    ax.set_title("Permanent Residual Blue Shift After Remyelination")
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("/tmp/cuprizone_v2_timeline.png", dpi=150)
    print("Saved visualization to /tmp/cuprizone_v2_timeline.png")
    
    # Print key values
    print("\nKey Predictions:")
    print(f"Healthy (week 0): g={data['splenium']['g_ratio'][0]:.3f}, λ={data['splenium']['centroid_nm'][0]:.1f}nm")
    print(f"Peak demyelination (week 6): g={data['splenium']['g_ratio'][24]:.3f}, λ={data['splenium']['centroid_nm'][24]:.1f}nm")
    print(f"Stable remyelinated (week 13): g={data['splenium']['g_ratio'][-1]:.3f}, λ={data['splenium']['centroid_nm'][-1]:.1f}nm")
    print(f"Permanent blue shift (splenium): {794 - data['splenium']['centroid_nm'][-1]:.1f}nm")
    print(f"Permanent blue shift (DHC): {794 - data['DHC']['centroid_nm'][-1]:.1f}nm")
