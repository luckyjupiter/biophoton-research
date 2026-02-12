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
from .detection import Detector, simulate_counts, li_ma_significance, compare_groups


@dataclass
class TimePoint:
    """Results at a single measurement timepoint."""

    week: float
    state: DemyelinationState
    mean_signal_rate: float          # photons/s at detector
    detected_counts: np.ndarray      # array of counts (one per mouse)
    background_counts: np.ndarray    # from control mice
    li_ma_sigma: float               # significance of signal vs. background (legacy)
    features: dict[str, float]       # 6-feature vector (average across mice)
    p_value: float = 1.0             # between-subjects test p-value
    effect_size: float = 0.0         # Cohen's d
    effect_size_ci: tuple[float, float] = (0.0, 0.0)  # 95% CI for Cohen's d


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
    animal_cv: float = 0.35     # biological variability (coefficient of variation)

    # Results
    timepoints: list[TimePoint] = field(default_factory=list, init=False)

    def run(self, seed: int = 42) -> list[TimePoint]:
        """Execute the full experiment simulation with per-animal variability."""
        rng = np.random.default_rng(seed)
        wavelengths = C.DEFAULT_LAMBDA_RANGE_NM

        self.timepoints = []
        measurement_weeks = np.arange(0, self.weeks + 0.01, self.measurement_interval_weeks)

        # Per-animal baseline multipliers (persist across timepoints)
        treated_multipliers = rng.lognormal(0, self.animal_cv, size=self.n_mice) if self.animal_cv > 0 else np.ones(self.n_mice)
        control_multipliers = rng.lognormal(0, self.animal_cv, size=self.n_mice) if self.animal_cv > 0 else np.ones(self.n_mice)

        # Healthy baseline (control mice never change)
        healthy_state = DemyelinationState(0, 0, 0)
        healthy_spectrum = waveguide_filtered_emission(self.axon, healthy_state, wavelengths)
        healthy_rate = float(np.trapezoid(healthy_spectrum, wavelengths)) * self.collection_area_cm2

        for week in measurement_weeks:
            state = cuprizone_timeline(week)

            # Signal from treated mice
            spectrum = waveguide_filtered_emission(self.axon, state, wavelengths)
            signal_rate = float(np.trapezoid(spectrum, wavelengths)) * self.collection_area_cm2

            # Per-animal counts with biological variability
            treated_counts = np.array([
                rng.poisson(max(1e-10,
                    signal_rate * m * self.detector.quantum_efficiency
                    + self.detector.dark_rate_hz) * self.exposure_s)
                for m in treated_multipliers
            ])
            control_counts = np.array([
                rng.poisson(max(1e-10,
                    healthy_rate * m * self.detector.quantum_efficiency
                    + self.detector.dark_rate_hz) * self.exposure_s)
                for m in control_multipliers
            ])

            # Li-Ma significance (legacy, kept for backward compat)
            n_on = float(np.sum(treated_counts))
            n_off = float(np.sum(control_counts))
            sigma = li_ma_significance(n_on, n_off)

            # Proper between-subjects test
            grp_result = compare_groups(
                treated_counts.astype(float), control_counts.astype(float)
            )

            # Feature vector (average across treated mice)
            features = compute_feature_vector(self.axon, state, wavelengths, rng,
                                              animal_cv=self.animal_cv)

            tp = TimePoint(
                week=float(week),
                state=state,
                mean_signal_rate=signal_rate,
                detected_counts=treated_counts,
                background_counts=control_counts,
                li_ma_sigma=sigma,
                features=features,
                p_value=grp_result["p_value"],
                effect_size=grp_result["effect_size"],
                effect_size_ci=grp_result["effect_size_ci"],
            )
            self.timepoints.append(tp)

        return self.timepoints

    def first_significant_week(self, threshold_sigma: float = 3.0,
                               p_threshold: float | None = None) -> float | None:
        """Find the first week where significance exceeds threshold.

        If p_threshold is given, uses the between-subjects p_value.
        Otherwise falls back to Li-Ma sigma (legacy).
        """
        for tp in self.timepoints:
            if p_threshold is not None:
                if tp.p_value <= p_threshold:
                    return tp.week
            else:
                if tp.li_ma_sigma >= threshold_sigma:
                    return tp.week
        return None

    def run_with_uncertainty(self, n_mc: int = 1000, seed: int = 42) -> dict:
        """Run experiment n_mc times with parameter uncertainty.

        Each MC iteration draws new Hill parameters, baseline emission,
        coupling efficiency, and per-animal multipliers. Returns credible
        intervals for key outcomes.
        """
        from .uncertainty import UncertaintyEngine, build_default_parameter_set

        engine = UncertaintyEngine(n_samples=n_mc, seed=seed)
        engine.load_defaults()
        rng = np.random.default_rng(seed)
        wavelengths = C.DEFAULT_LAMBDA_RANGE_NM
        measurement_weeks = np.arange(0, self.weeks + 0.01, self.measurement_interval_weeks)

        healthy_state = DemyelinationState(0, 0, 0)

        first_sig_weeks = []
        peak_effect_sizes = []
        effect_sizes_by_week = {float(w): [] for w in measurement_weeks}
        p_values_by_week = {float(w): [] for w in measurement_weeks}

        for mc_i in range(n_mc):
            # Draw parameters
            params = {}
            for name, pd in engine.parameters.items():
                params[name] = float(pd.sample(rng, 1)[0])

            baseline = params.get("baseline_emission", C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S)
            hill_n = params.get("hill_n", C.HILL_N_EMISSION)
            hill_k = params.get("hill_k", C.HILL_K_HALF_DEFAULT)
            hill_smax = params.get("hill_smax", C.HILL_SMAX_NOMINAL)
            coupling = params.get("coupling_efficiency", C.COUPLING_EFFICIENCY_NOMINAL)
            animal_cv = params.get("animal_cv", C.ANIMAL_CV_NOMINAL)

            # Per-animal multipliers for this MC run
            treated_mult = rng.lognormal(0, animal_cv, size=self.n_mice) if animal_cv > 0 else np.ones(self.n_mice)
            control_mult = rng.lognormal(0, animal_cv, size=self.n_mice) if animal_cv > 0 else np.ones(self.n_mice)

            # Healthy rate (use waveguide_filtered_emission for full pipeline)
            # Scale by MC-sampled baseline and coupling relative to nominals
            scale = (baseline / C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S) * (coupling / C.COUPLING_EFFICIENCY_NOMINAL)
            h_spectrum = waveguide_filtered_emission(self.axon, healthy_state, wavelengths)
            h_rate = float(np.trapezoid(h_spectrum, wavelengths)) * self.collection_area_cm2 * scale

            first_sig = None
            max_es = 0.0

            for week in measurement_weeks:
                state = cuprizone_timeline(float(week))
                # Use full waveguide pipeline with MC-varied Hill parameters
                d_spectrum = waveguide_filtered_emission(
                    self.axon, state, wavelengths,
                    hill_n=hill_n, hill_k=hill_k, hill_smax=hill_smax)
                d_rate = float(np.trapezoid(d_spectrum, wavelengths)) * self.collection_area_cm2 * scale

                # Per-animal counts
                d_counts = np.array([
                    rng.poisson(max(1e-10, d_rate * m * self.detector.quantum_efficiency
                                    + self.detector.dark_rate_hz) * self.exposure_s)
                    for m in treated_mult
                ], dtype=float)
                h_counts = np.array([
                    rng.poisson(max(1e-10, h_rate * m * self.detector.quantum_efficiency
                                    + self.detector.dark_rate_hz) * self.exposure_s)
                    for m in control_mult
                ], dtype=float)

                result = compare_groups(d_counts, h_counts)
                es = result["effect_size"]
                pv = result["p_value"]

                effect_sizes_by_week[float(week)].append(es)
                p_values_by_week[float(week)].append(pv)

                if es > max_es:
                    max_es = es
                if first_sig is None and pv < 0.05:
                    first_sig = float(week)

            first_sig_weeks.append(first_sig if first_sig is not None else float("inf"))
            peak_effect_sizes.append(max_es)

        # Aggregate results
        first_sig_arr = np.array(first_sig_weeks)
        finite_mask = np.isfinite(first_sig_arr)
        peak_es_arr = np.array(peak_effect_sizes)

        result = {
            "first_significant_week_median": float(np.median(first_sig_arr[finite_mask])) if finite_mask.any() else float("inf"),
            "first_significant_week_ci": (
                float(np.percentile(first_sig_arr[finite_mask], 5)),
                float(np.percentile(first_sig_arr[finite_mask], 95))
            ) if finite_mask.any() else (float("inf"), float("inf")),
            "fraction_never_significant": float(1 - finite_mask.mean()),
            "peak_effect_size_median": float(np.median(peak_es_arr)),
            "peak_effect_size_ci": (
                float(np.percentile(peak_es_arr, 5)),
                float(np.percentile(peak_es_arr, 95)),
            ),
            "effect_sizes_by_week": {},
            "p_values_by_week": {},
        }

        for week in measurement_weeks:
            w = float(week)
            es_arr = np.array(effect_sizes_by_week[w])
            pv_arr = np.array(p_values_by_week[w])
            result["effect_sizes_by_week"][w] = {
                "median": float(np.median(es_arr)),
                "ci_90": (float(np.percentile(es_arr, 5)), float(np.percentile(es_arr, 95))),
            }
            result["p_values_by_week"][w] = {
                "median": float(np.median(pv_arr)),
                "fraction_significant": float(np.mean(pv_arr < 0.05)),
            }

        return result

    def summary(self) -> str:
        """Human-readable summary of experiment results."""
        if not self.timepoints:
            return "Experiment not yet run. Call .run() first."

        lines = [
            f"Cuprizone Experiment: {self.n_mice} mice, {self.weeks} weeks (CV={self.animal_cv:.0%})",
            f"Detector: {self.detector.name} (QE={self.detector.quantum_efficiency:.0%})",
            f"Axon: {self.axon}",
            f"Exposure: {self.exposure_s:.0f}s per measurement",
            "",
            f"{'Week':>5} {'α':>5} {'γ':>5} {'ρ':>5} {'Rate':>10} {'Mean Cts':>10} {'p-value':>10} {'Cohen d':>8}",
            "-" * 70,
        ]

        for tp in self.timepoints:
            mean_cts = np.mean(tp.detected_counts)
            lines.append(
                f"{tp.week:5.1f} {tp.state.alpha:5.2f} {tp.state.gamma:5.2f} "
                f"{tp.state.rho:5.2f} {tp.mean_signal_rate:10.1f} {mean_cts:10.1f} "
                f"{tp.p_value:10.4f} {tp.effect_size:8.2f}"
            )

        first = self.first_significant_week(p_threshold=0.05)
        if first is not None:
            lines.append(f"\nFirst significant detection (p<0.05) at week {first:.1f}")
        else:
            lines.append("\nNever reached significance (p<0.05)")

        return "\n".join(lines)
