"""
Full cuprizone experiment simulator.

Models a standard cuprizone feeding study where mice are fed the copper
chelator for 6–12 weeks, causing predictable demyelination of the corpus
callosum. Simulates the biophoton measurements a detector would record
at each timepoint.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import constants as C
from .axon import AxonGeometry
from .demyelination import cuprizone_timeline, DemyelinationState
from .emission import waveguide_filtered_emission, compute_feature_vector
from .detection import Detector, simulate_counts, li_ma_significance


@dataclass
class TimePoint:
    """Results at a single measurement timepoint."""

    week: float
    state: DemyelinationState
    mean_signal_rate: float          # photons/s at detector
    detected_counts: np.ndarray      # array of counts (one per mouse)
    background_counts: np.ndarray    # from control mice
    li_ma_sigma: float               # significance of signal vs. background
    features: dict[str, float]       # 6-feature vector (average across mice)


@dataclass
class CuprizoneExperiment:
    """Simulate a cuprizone demyelination experiment with biophoton detection.

    Parameters
    ----------
    n_mice : int
        Number of treated mice (same number of controls).
    weeks : int
        Duration of experiment in weeks.
    detector : Detector
        Photon detector used.
    axon : AxonGeometry
        Representative axon type being imaged.
    exposure_s : float
        Integration time per measurement in seconds.
    measurement_interval_weeks : float
        How often measurements are taken (default: weekly).
    """

    n_mice: int = 10
    weeks: int = 12
    detector: Detector = field(default_factory=Detector.PMT)
    axon: AxonGeometry = field(default_factory=AxonGeometry.typical_cns)
    exposure_s: float = 300.0   # 5-minute exposure
    measurement_interval_weeks: float = 1.0
    collection_area_cm2: float = 0.01  # 1 mm² fiber bundle cross-section

    # Results
    timepoints: list[TimePoint] = field(default_factory=list, init=False)

    def run(self, seed: int = 42) -> list[TimePoint]:
        """Execute the full experiment simulation."""
        rng = np.random.default_rng(seed)
        wavelengths = C.DEFAULT_LAMBDA_RANGE_NM

        self.timepoints = []
        measurement_weeks = np.arange(0, self.weeks + 0.01, self.measurement_interval_weeks)

        # Healthy baseline (control mice never change)
        healthy_state = DemyelinationState(0, 0, 0)
        healthy_spectrum = waveguide_filtered_emission(self.axon, healthy_state, wavelengths)
        # Scale from per-cm² to actual collection area
        healthy_rate = float(np.trapezoid(healthy_spectrum, wavelengths)) * self.collection_area_cm2

        for week in measurement_weeks:
            state = cuprizone_timeline(week)

            # Signal from treated mice
            spectrum = waveguide_filtered_emission(self.axon, state, wavelengths)
            signal_rate = float(np.trapezoid(spectrum, wavelengths)) * self.collection_area_cm2

            # Simulate individual mouse measurements
            treated_counts = simulate_counts(
                signal_rate, self.detector, self.exposure_s, self.n_mice, rng
            )
            control_counts = simulate_counts(
                healthy_rate, self.detector, self.exposure_s, self.n_mice, rng
            )

            # Li-Ma significance: treated (on) vs. control (off)
            n_on = float(np.sum(treated_counts))
            n_off = float(np.sum(control_counts))
            sigma = li_ma_significance(n_on, n_off)

            # Feature vector (average across treated mice)
            features = compute_feature_vector(self.axon, state, wavelengths, rng)

            tp = TimePoint(
                week=float(week),
                state=state,
                mean_signal_rate=signal_rate,
                detected_counts=treated_counts,
                background_counts=control_counts,
                li_ma_sigma=sigma,
                features=features,
            )
            self.timepoints.append(tp)

        return self.timepoints

    def first_significant_week(self, threshold_sigma: float = 3.0) -> float | None:
        """Find the first week where Li-Ma significance exceeds threshold."""
        for tp in self.timepoints:
            if tp.li_ma_sigma >= threshold_sigma:
                return tp.week
        return None

    def summary(self) -> str:
        """Human-readable summary of experiment results."""
        if not self.timepoints:
            return "Experiment not yet run. Call .run() first."

        lines = [
            f"Cuprizone Experiment: {self.n_mice} mice, {self.weeks} weeks",
            f"Detector: {self.detector.name} (QE={self.detector.quantum_efficiency:.0%})",
            f"Axon: {self.axon}",
            f"Exposure: {self.exposure_s:.0f}s per measurement",
            "",
            f"{'Week':>5} {'α':>5} {'γ':>5} {'ρ':>5} {'Rate':>10} {'Mean Cts':>10} {'Li-Ma σ':>8}",
            "-" * 55,
        ]

        for tp in self.timepoints:
            mean_cts = np.mean(tp.detected_counts)
            lines.append(
                f"{tp.week:5.1f} {tp.state.alpha:5.2f} {tp.state.gamma:5.2f} "
                f"{tp.state.rho:5.2f} {tp.mean_signal_rate:10.1f} {mean_cts:10.1f} "
                f"{tp.li_ma_sigma:8.1f}"
            )

        first = self.first_significant_week()
        if first is not None:
            lines.append(f"\nFirst 3σ detection at week {first:.1f}")
        else:
            lines.append("\nNever reached 3σ significance")

        return "\n".join(lines)
