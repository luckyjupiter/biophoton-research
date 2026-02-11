"""
Experimental protocol tools.

Computes sample size requirements, statistical power, expected effect sizes,
and measurement integration times for proposed biophoton-demyelination experiments.

Usage:
    python src/experimental_protocol.py
"""

import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from constants import (
    BASAL_EMISSION_RATE, INFLAMMATORY_EMISSION_FACTOR_HIGH,
    MEASUREMENT_INTEGRATION_TIME_S, DETECTOR_DARK_COUNT_RATE, DETECTOR_QE,
    EAE_ONSET_DAY, EAE_PEAK_DAY, EAE_CHRONIC_DAY,
)


def required_sample_size(effect_size, alpha=0.05, power=0.80, two_sided=True):
    """Sample size per group for two-sample t-test."""
    if abs(effect_size) < 1e-10:
        return 99999
    z_alpha = stats.norm.ppf(1 - alpha / (2 if two_sided else 1))
    z_beta = stats.norm.ppf(power)
    n = ((z_alpha + z_beta) / effect_size) ** 2
    return int(np.ceil(n)) + 1


def statistical_power(n_per_group, effect_size, alpha=0.05, two_sided=True):
    """Compute power for given sample size and effect size."""
    z_alpha = stats.norm.ppf(1 - alpha / (2 if two_sided else 1))
    z_crit = effect_size * np.sqrt(n_per_group) - z_alpha
    return float(stats.norm.cdf(z_crit))


def signal_to_noise(emission_rate, integration_time_s,
                    dark_rate=DETECTOR_DARK_COUNT_RATE, qe=DETECTOR_QE):
    """Photon counting SNR. SNR = S / sqrt(S + B)."""
    S = emission_rate * qe * integration_time_s
    B = dark_rate * integration_time_s
    if S + B <= 0:
        return 0.0
    return S / np.sqrt(S + B)


def required_integration_time(emission_rate, target_snr=5.0,
                              dark_rate=DETECTOR_DARK_COUNT_RATE, qe=DETECTOR_QE):
    """Integration time needed to achieve target SNR."""
    S = emission_rate * qe
    B = dark_rate
    if S <= 0:
        return float('inf')
    return target_snr**2 * (S + B) / S**2


def eae_timeline_predictions():
    """Predicted biophoton measurements at EAE model time points."""
    timepoints = {
        "Baseline (day 0)": {"day": 0, "myelin_loss": 0.0, "inflammation": 0.0},
        "Pre-symptomatic (day 7)": {"day": 7, "myelin_loss": 0.02, "inflammation": 0.1},
        "Onset (day 10-12)": {"day": EAE_ONSET_DAY, "myelin_loss": 0.10, "inflammation": 0.5},
        "Peak (day 14-18)": {"day": EAE_PEAK_DAY, "myelin_loss": 0.35, "inflammation": 0.9},
        "Chronic (day 28+)": {"day": EAE_CHRONIC_DAY, "myelin_loss": 0.25, "inflammation": 0.15},
    }
    for name, tp in timepoints.items():
        base = BASAL_EMISSION_RATE * (1.0 + 5.0 * tp["myelin_loss"])
        inflam = BASAL_EMISSION_RATE * INFLAMMATORY_EMISSION_FACTOR_HIGH * tp["inflammation"]
        tp["predicted_emission"] = base + inflam
        tp["emission_fold_change"] = tp["predicted_emission"] / BASAL_EMISSION_RATE
        tp["snr_1hr"] = signal_to_noise(tp["predicted_emission"], MEASUREMENT_INTEGRATION_TIME_S)
        tp["time_for_snr5"] = required_integration_time(tp["predicted_emission"])
    return timepoints


def cuprizone_timeline_predictions():
    """Predicted biophoton measurements at cuprizone model time points."""
    timepoints = {
        "Week 0 (baseline)": {"week": 0, "myelin_loss": 0.0, "inflammation": 0.0},
        "Week 1-2 (OL stress)": {"week": 1.5, "myelin_loss": 0.05, "inflammation": 0.15},
        "Week 3 (microglial)": {"week": 3, "myelin_loss": 0.20, "inflammation": 0.35},
        "Week 4-5 (active)": {"week": 4.5, "myelin_loss": 0.55, "inflammation": 0.50},
        "Week 6 (peak loss)": {"week": 6, "myelin_loss": 0.85, "inflammation": 0.30},
        "Week 8 (early remyel)": {"week": 8, "myelin_loss": 0.60, "inflammation": 0.10},
        "Week 12 (remyelinated)": {"week": 12, "myelin_loss": 0.25, "inflammation": 0.05},
    }
    for name, tp in timepoints.items():
        base = BASAL_EMISSION_RATE * (1.0 + 5.0 * tp["myelin_loss"])
        inflam = BASAL_EMISSION_RATE * INFLAMMATORY_EMISSION_FACTOR_HIGH * tp["inflammation"]
        tp["predicted_emission"] = base + inflam
        tp["emission_fold_change"] = tp["predicted_emission"] / BASAL_EMISSION_RATE
        tp["snr_1hr"] = signal_to_noise(tp["predicted_emission"], MEASUREMENT_INTEGRATION_TIME_S)
    return timepoints


def power_analysis_table():
    """Generate sample size requirements for different scenarios."""
    lines = []
    lines.append("=" * 75)
    lines.append("SAMPLE SIZE REQUIREMENTS (alpha=0.05, power=0.80, two-sided)")
    lines.append("=" * 75)
    fmt = "{:<35} {:>10} {:>10} {:>10}"
    lines.append(fmt.format("Scenario", "Effect (d)", "N/group", "N total"))
    lines.append("-" * 75)
    scenarios = [
        ("Preclinical (emission intensity)", 0.3),
        ("Preclinical (spectral shift)", 0.2),
        ("Early clinical (emission)", 0.8),
        ("Early clinical (spectral)", 0.6),
        ("Moderate (emission)", 1.5),
        ("Moderate (spectral shift)", 1.2),
        ("Severe (emission)", 2.5),
        ("Active inflammation (emission)", 3.0),
        ("g2(0) decrease (moderate)", 0.5),
        ("Combined score (moderate)", 1.0),
        ("Remyelination reversal", 0.7),
    ]
    for name, d in scenarios:
        n = required_sample_size(d)
        lines.append(fmt.format(name, f"{d:.1f}", str(n), str(2*n)))
    lines.append("-" * 75)
    return "\n".join(lines)


def plot_power_curves(save_path="../figures/power_analysis.png"):
    """Plot power curves for key experimental scenarios."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    n_range = np.arange(3, 60)
    effect_sizes = [0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(effect_sizes)))
    for d, color in zip(effect_sizes, colors):
        powers = [statistical_power(n, d) for n in n_range]
        ax1.plot(n_range, powers, color=color, linewidth=2, label="d = {:.1f}".format(d))
    ax1.axhline(y=0.80, color="red", linestyle="--", alpha=0.4, label="Power = 0.80")
    ax1.set_xlabel("Sample Size per Group")
    ax1.set_ylabel("Statistical Power")
    ax1.set_title("Power Curves for Two-Sample t-Test")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    rates = np.logspace(-1, 3, 100)
    for target, color in zip([3, 5, 10], ["tab:blue", "tab:orange", "tab:red"]):
        times = [required_integration_time(r, target_snr=target) for r in rates]
        ax2.loglog(rates, times, color=color, linewidth=2, label="SNR = {}".format(target))
    ax2.axvline(x=BASAL_EMISSION_RATE, color="green", linestyle="--", alpha=0.5,
                label="Basal = {} ph/s".format(BASAL_EMISSION_RATE))
    ax2.axhline(y=3600, color="gray", linestyle=":", alpha=0.3, label="1 hour")
    ax2.set_xlabel("Emission Rate (photons/s)")
    ax2.set_ylabel("Required Integration Time (s)")
    ax2.set_title("Integration Time for Target SNR")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    fig.suptitle("Experimental Design: Power and Integration Analysis",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: " + save_path)


def generate_protocol_document():
    """Generate a formatted experimental protocol document."""
    eae = eae_timeline_predictions()
    cup = cuprizone_timeline_predictions()
    power_tbl = power_analysis_table()
    doc = []
    doc.append("=" * 70)
    doc.append("EXPERIMENTAL PROTOCOL: Biophoton Detection in Demyelinating Disease")
    doc.append("Track 06 -- Demyelination & Pathology")
    doc.append("=" * 70)
    doc.append("")
    doc.append("OBJECTIVE: Test that demyelination alters biophoton emission")
    doc.append("from neural tissue using established animal models.")
    doc.append("")
    doc.append("HYPOTHESIS: Demyelinated nerve emits biophotons with (a) spectral")
    doc.append("blueshift, (b) increased intensity during inflammation, (c) reduced")
    doc.append("photon-photon correlations vs healthy myelinated tissue.")
    doc.append("")
    doc.append("EXPERIMENT 1: EAE Mouse Model (Optic Nerve, Ex Vivo)")
    doc.append("-" * 55)
    doc.append("MOG35-55-induced EAE in C57BL/6, n=8/timepoint x 3 groups x 5 = 120")
    doc.append("")
    fmt = "  {:<28} {:>10} {:>6} {:>8} {:>10}"
    doc.append(fmt.format("Time point", "Emission", "Fold", "SNR(1h)", "t(SNR=5)"))
    doc.append("  " + "-" * 68)
    for name, tp in eae.items():
        doc.append(fmt.format(name,
            "{:.1f}".format(tp["predicted_emission"]),
            "{:.1f}x".format(tp["emission_fold_change"]),
            "{:.1f}".format(tp["snr_1hr"]),
            "{:.0f}s".format(tp["time_for_snr5"])))
    doc.append("")
    doc.append("EXPERIMENT 2: Cuprizone (Corpus Callosum, Longitudinal)")
    doc.append("-" * 55)
    doc.append("0.2% cuprizone 6 weeks then normal chow, n=12/group x 2 = 24")
    doc.append("")
    fmt2 = "  {:<30} {:>10} {:>12} {:>8}"
    doc.append(fmt2.format("Time point", "Emission", "Fold", "SNR(1h)"))
    doc.append("  " + "-" * 64)
    for name, tp in cup.items():
        doc.append(fmt2.format(name,
            "{:.1f}".format(tp["predicted_emission"]),
            "{:.1f}x".format(tp["emission_fold_change"]),
            "{:.1f}".format(tp["snr_1hr"])))
    doc.append("")
    doc.append("EXPERIMENT 3: LPC Focal Lesion (Sciatic Nerve, In Vivo)")
    doc.append("-" * 55)
    doc.append("LPC injection, n=10, left sciatic LPC, right vehicle, days 3/7/14/21")
    doc.append("")
    doc.append("DETECTION: EM-CCD (Hamamatsu ImagEM X2), PMT (H7421-40), SPADs (HBT)")
    doc.append("CONTROLS: Dark counts, heat-killed, contralateral, TTX, NAC, sham")
    doc.append("STATS: Two-way ANOVA, paired t-test, Bonferroni, Cohen's d")
    doc.append("")
    doc.append(power_tbl)
    return "\n".join(doc)


if __name__ == "__main__":
    import os
    os.makedirs("../figures", exist_ok=True)
    os.makedirs("../results", exist_ok=True)
    plot_power_curves()
    protocol = generate_protocol_document()
    print(protocol)
    with open("../results/experimental_protocol.txt", "w") as f:
        f.write(protocol)
    print("\nSaved: ../results/experimental_protocol.txt")
