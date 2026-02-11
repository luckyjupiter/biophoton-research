"""
Artifact Catalog and Simulation for Biophoton Research
=======================================================
Simulates every known artifact that can masquerade as biophoton emission
or coherence: delayed luminescence, chemiluminescence, detector artifacts,
cosmic rays, phosphorescence, and cross-talk.

Usage: python src/artifacts.py
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class ArtifactSource:
    name: str
    rate: float
    temporal_signature: str
    spectral_signature: str
    distinguishable: bool
    mitigation: str


ARTIFACT_CATALOG = [
    ArtifactSource(
        "Delayed luminescence", 1000.0,
        "Hyperbolic decay: I(t) ~ t^(-m), m=1-2, seconds to minutes",
        "Broad, peaks 500-700nm, similar to UPE", True,
        "Wait 30+ min after light exposure; monitor decay curve"),
    ArtifactSource(
        "Chemiluminescence (oxidative)", 50.0,
        "Steady-state with slow drift; responds to chemical perturbation",
        "Broad 400-700nm, peaks depend on ROS species", False,
        "Antioxidant controls; dead tissue comparison"),
    ArtifactSource(
        "Afterpulsing (PMT/SPAD)", 2.0,
        "Exponential delay 20-200ns after parent; creates g2 excess",
        "Same as dark counts", True,
        "Characterize AP probability; correct g2; hold-off time"),
    ArtifactSource(
        "Cosmic ray hits", 0.017,
        "Random Poisson; large energy deposit per event",
        "Broadband; may trigger Cherenkov in glass", True,
        "Pulse height discrimination; coincidence veto; underground lab"),
    ArtifactSource(
        "Phosphorescence", 10.0,
        "Exponential decay, tau=ms to hours",
        "Narrow bands, species-specific", True,
        "Time-resolved measurement; spectral filtering"),
    ArtifactSource(
        "Fluorescence from optics", 5.0,
        "Steady under UV excitation; decays when removed",
        "Red-shifted from excitation; glass-dependent", True,
        "Non-fluorescent optics (CaF2, fused silica)"),
    ArtifactSource(
        "Triboluminescence", 100.0,
        "Correlated with mechanical disturbance; burst-like",
        "Broad visible, often blue-white", True,
        "Minimize vibration; settle time after handling"),
    ArtifactSource(
        "SPAD cross-talk", 0.01,
        "Coincident with avalanche in neighbor; sub-ns",
        "NIR 800-1100nm from hot-carrier emission", True,
        "Optical isolation OD>6; spectral filter"),
    ArtifactSource(
        "Dark rate drift (thermal)", 0.3,
        "Slow monotonic or periodic (room temp cycles)",
        "None (electronic)", True,
        "Temp monitoring to 0.01C; interleaved blanks"),
    ArtifactSource(
        "Bioluminescence (enzymatic)", 100.0,
        "Steady state; ATP-dependent",
        "Narrow 550-570nm (luciferase) or specific", True,
        "Metabolic inhibitors; spectral analysis"),
]


def simulate_delayed_luminescence(t_dark_adapt, t_observe, rate_0=1000.0,
                                   decay_exponent=1.5, rng=None):
    """Simulate delayed luminescence with power-law decay."""
    if rng is None:
        rng = np.random.default_rng()
    t0 = 1.0
    m = decay_exponent
    rate_start = rate_0 * (t_dark_adapt / t0)**(-m)
    n_est = int(rate_start * t_observe * 2)
    if n_est <= 0:
        return np.array([])
    u = rng.uniform(size=max(1, n_est))
    if m != 1:
        t_rel = t_dark_adapt * ((1 - u)**(1.0 / (1.0 - m)) - 1)
    else:
        t_rel = t_dark_adapt * (np.exp(-np.log(1 - u + 1e-30)) - 1)
    t_rel = t_rel[(t_rel >= 0) & (t_rel < t_observe)]
    t_rel.sort()
    return t_rel


def simulate_chemiluminescence(rate, duration, drift_frac=0.01, rng=None):
    """Simulate chemiluminescence with slow drift."""
    if rng is None:
        rng = np.random.default_rng()
    n_bins = int(duration)
    rates = rate * (1 + drift_frac * np.arange(n_bins) / n_bins)
    return rng.poisson(rates)


def simulate_afterpulse_g2_contamination(total_rate, p_ap, tau_ap, tau_bins):
    """Compute g(2) excess from afterpulsing at given time lags."""
    tau = np.asarray(tau_bins)
    g2_excess = (p_ap / (total_rate * tau_ap)) * np.exp(-tau / tau_ap)
    return 1.0 + g2_excess


def simulate_cosmic_ray_events(area_cm2, duration, rng=None):
    """Simulate cosmic ray hits on a detector."""
    if rng is None:
        rng = np.random.default_rng()
    rate = 0.017 * area_cm2
    n = rng.poisson(rate * duration)
    if n == 0:
        return np.array([]), np.array([])
    times = rng.uniform(0, duration, size=n)
    times.sort()
    energies = rng.lognormal(mean=np.log(3000), sigma=0.5, size=n)
    return times, energies


def main():
    print("=" * 80)
    print("ARTIFACT CATALOG FOR BIOPHOTON RESEARCH")
    print("=" * 80)
    print()
    print("%-30s  %8s  %15s  %s" % ("Artifact", "Rate/s", "Distinguishable", "Mitigation"))
    print("-" * 120)
    for a in ARTIFACT_CATALOG:
        print("%-30s  %8.3f  %15s  %s" % (
            a.name, a.rate,
            "Yes" if a.distinguishable else "NO",
            a.mitigation[:60]))
    print()
    print("--- Delayed Luminescence Simulation ---")
    for t_dark in [60, 300, 1800, 3600]:
        dl = simulate_delayed_luminescence(t_dark, 600)
        print("  Dark-adapt %5ds: %d events in 600s (%.3f/s)" % (
            t_dark, len(dl), len(dl) / 600))
    print()
    print("--- Afterpulse g(2) Contamination ---")
    taus = np.array([1e-9, 5e-9, 10e-9, 50e-9, 100e-9, 500e-9, 1e-6])
    g2 = simulate_afterpulse_g2_contamination(100, 0.02, 50e-9, taus)
    for i, tau in enumerate(taus):
        print("  tau=%6.1f ns: g2 = %.6f (excess = %.2e)" % (
            tau * 1e9, g2[i], g2[i] - 1))
    print()
    print("--- Cosmic Ray Events ---")
    for area in [1, 5, 10]:
        times, energies = simulate_cosmic_ray_events(area, 3600)
        print("  Area %2d cm2, 1hr: %d events (%.3f/min)" % (
            area, len(times), len(times) / 60))


if __name__ == "__main__":
    main()
