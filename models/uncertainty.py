"""
Monte Carlo uncertainty propagation engine for biophoton predictions.

Propagates parameter uncertainty through the entire cascade:
emission -> waveguide -> detection -> classification.

Provides credible intervals, sensitivity indices, and tornado plot data
for honest reporting of prediction uncertainty.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy import stats as sp_stats

from . import constants as C
from .axon import AxonGeometry
from .demyelination import DemyelinationState, cuprizone_timeline
from .emission import disease_emission, waveguide_filtered_emission, compute_feature_vector
from .detection import Detector, simulate_counts, compare_groups, compute_roc


# ---------------------------------------------------------------------------
# Parameter distribution specification
# ---------------------------------------------------------------------------

@dataclass
class ParameterDistribution:
    """A parameter with uncertainty."""

    name: str
    nominal: float
    distribution: str  # "lognormal", "uniform", "normal", "beta"
    params: dict = field(default_factory=dict)

    def sample(self, rng: np.random.Generator, n: int = 1) -> np.ndarray:
        """Draw n samples from this parameter's distribution."""
        d = self.distribution
        p = self.params
        if d == "lognormal":
            mu = p.get("mu", np.log(self.nominal))
            sigma = p.get("sigma", 0.5)
            return rng.lognormal(mu, sigma, size=n)
        elif d == "uniform":
            low = p.get("low", self.nominal * 0.5)
            high = p.get("high", self.nominal * 1.5)
            return rng.uniform(low, high, size=n)
        elif d == "normal":
            mean = p.get("mean", self.nominal)
            std = p.get("std", self.nominal * 0.1)
            return rng.normal(mean, std, size=n)
        elif d == "beta":
            a = p.get("alpha", 2.0)
            b = p.get("beta", 2.0)
            return rng.beta(a, b, size=n)
        else:
            raise ValueError(f"Unknown distribution: {d}")


# ---------------------------------------------------------------------------
# Default parameter set
# ---------------------------------------------------------------------------

def build_default_parameter_set() -> list[ParameterDistribution]:
    """The 8 key uncertain parameters for Monte Carlo propagation."""
    return [
        ParameterDistribution(
            name="baseline_emission",
            nominal=C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S,
            distribution="lognormal",
            params={"mu": C.BASELINE_EMISSION_LOG_MU,
                    "sigma": C.BASELINE_EMISSION_LOG_SIGMA},
        ),
        ParameterDistribution(
            name="hill_n",
            nominal=C.HILL_N_EMISSION,
            distribution="uniform",
            params={"low": C.HILL_N_EMISSION_RANGE[0],
                    "high": C.HILL_N_EMISSION_RANGE[1]},
        ),
        ParameterDistribution(
            name="hill_k",
            nominal=C.HILL_K_HALF_DEFAULT,
            distribution="uniform",
            params={"low": C.HILL_K_HALF_RANGE[0],
                    "high": C.HILL_K_HALF_RANGE[1]},
        ),
        ParameterDistribution(
            name="hill_smax",
            nominal=C.HILL_SMAX_NOMINAL,
            distribution="lognormal",
            params={"mu": C.HILL_SMAX_LOG_MU,
                    "sigma": C.HILL_SMAX_LOG_SIGMA},
        ),
        ParameterDistribution(
            name="node_transmission",
            nominal=C.NODE_TRANSMISSION_NOMINAL,
            distribution="beta",
            params={"alpha": C.NODE_TRANSMISSION_ALPHA,
                    "beta": C.NODE_TRANSMISSION_BETA},
        ),
        ParameterDistribution(
            name="spectral_shift_per_layer",
            nominal=C.SPECTRAL_SHIFT_PER_LAYER_NM,
            distribution="normal",
            params={"mean": C.SPECTRAL_SHIFT_PER_LAYER_NM,
                    "std": C.SPECTRAL_SHIFT_PER_LAYER_SIGMA},
        ),
        ParameterDistribution(
            name="coupling_efficiency",
            nominal=C.COUPLING_EFFICIENCY_NOMINAL,
            distribution="lognormal",
            params={"mu": C.COUPLING_EFFICIENCY_LOG_MU,
                    "sigma": C.COUPLING_EFFICIENCY_LOG_SIGMA},
        ),
        ParameterDistribution(
            name="animal_cv",
            nominal=C.ANIMAL_CV_NOMINAL,
            distribution="uniform",
            params={"low": C.ANIMAL_CV_RANGE[0],
                    "high": C.ANIMAL_CV_RANGE[1]},
        ),
    ]


# ---------------------------------------------------------------------------
# Uncertainty engine
# ---------------------------------------------------------------------------

class UncertaintyEngine:
    """Monte Carlo propagation of parameter uncertainties."""

    def __init__(self, n_samples: int = 10000, seed: int = 42):
        self.n_samples = n_samples
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.parameters: dict[str, ParameterDistribution] = {}
        self._samples: dict[str, np.ndarray] | None = None

    def define_parameter(self, name: str, nominal: float,
                         distribution: str, **params) -> None:
        """Register a parameter with its uncertainty distribution."""
        self.parameters[name] = ParameterDistribution(
            name=name, nominal=nominal, distribution=distribution, params=params,
        )
        self._samples = None  # invalidate cache

    def load_defaults(self) -> None:
        """Load the 8 default uncertain parameters."""
        for pd in build_default_parameter_set():
            self.parameters[pd.name] = pd
        self._samples = None

    def sample_parameters(self) -> list[dict[str, float]]:
        """Draw n_samples sets of parameters from their distributions.

        Returns list of dicts, one per MC sample.
        """
        if self._samples is None:
            self._samples = {}
            for name, pd in self.parameters.items():
                self._samples[name] = pd.sample(self.rng, self.n_samples)

        return [
            {name: float(arr[i]) for name, arr in self._samples.items()}
            for i in range(self.n_samples)
        ]

    def propagate(self, model_fn: Callable[[dict[str, float]], dict[str, float]],
                  param_names: list[str] | None = None) -> dict[str, np.ndarray]:
        """Run model_fn with each parameter sample, collect outputs.

        Parameters
        ----------
        model_fn : callable
            Takes a dict of parameter values, returns dict of output values.
        param_names : list[str] or None
            Which parameters to vary. None = all registered parameters.

        Returns
        -------
        dict mapping output_name -> array of n_samples values.
        """
        samples = self.sample_parameters()
        if param_names is not None:
            # Only include requested parameters, use nominals for the rest
            nominals = {n: pd.nominal for n, pd in self.parameters.items()}
            filtered = []
            for s in samples:
                merged = dict(nominals)
                for k in param_names:
                    if k in s:
                        merged[k] = s[k]
                filtered.append(merged)
            samples = filtered

        results: dict[str, list] = {}
        for s in samples:
            out = model_fn(s)
            for key, val in out.items():
                results.setdefault(key, []).append(val)

        return {k: np.array(v) for k, v in results.items()}

    def credible_interval(self, values: np.ndarray,
                          level: float = 0.90) -> tuple[float, float]:
        """Central credible interval from samples."""
        alpha = (1 - level) / 2
        lo = float(np.percentile(values, 100 * alpha))
        hi = float(np.percentile(values, 100 * (1 - alpha)))
        return (lo, hi)

    def sensitivity_indices(self) -> dict[str, float]:
        """First-order sensitivity indices via rank correlation with outputs.

        Must be called after propagate(). Uses Spearman correlation squared
        as a Sobol-like proxy for first-order sensitivity.
        """
        if self._samples is None:
            raise RuntimeError("Call sample_parameters() or propagate() first")
        return {}  # placeholder — filled by propagate_* functions below

    def __repr__(self) -> str:
        return (f"UncertaintyEngine(n_samples={self.n_samples}, "
                f"params={list(self.parameters.keys())})")


# ---------------------------------------------------------------------------
# Convenience propagation functions
# ---------------------------------------------------------------------------

def propagate_emission_prediction(
    state: DemyelinationState,
    n_samples: int = 10000,
    seed: int = 42,
    axon: AxonGeometry | None = None,
) -> dict:
    """Emission rate with credible intervals.

    Returns dict with keys: median, ci_90, ci_50, samples, sensitivity.
    """
    if axon is None:
        axon = AxonGeometry.typical_cns()

    engine = UncertaintyEngine(n_samples=n_samples, seed=seed)
    engine.load_defaults()
    wavelengths = C.DEFAULT_LAMBDA_RANGE_NM

    def model_fn(params: dict[str, float]) -> dict[str, float]:
        # Apply parameter perturbations
        baseline = params.get("baseline_emission", C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S)
        hill_n = params.get("hill_n", C.HILL_N_EMISSION)
        hill_k = params.get("hill_k", C.HILL_K_HALF_DEFAULT)
        hill_smax = params.get("hill_smax", C.HILL_SMAX_NOMINAL)
        coupling = params.get("coupling_efficiency", C.COUPLING_EFFICIENCY_NOMINAL)

        spectrum = disease_emission(state, wavelengths,
                                    hill_n=hill_n, hill_k=hill_k, hill_smax=hill_smax)
        total_rate = float(np.trapezoid(spectrum, wavelengths)) * baseline / 100.0 * coupling / 1e-3
        return {"emission_rate": total_rate}

    results = engine.propagate(model_fn)
    samples = results["emission_rate"]

    # Sensitivity: rank correlation of each input with output
    param_samples = engine._samples
    sensitivity = {}
    for name, arr in param_samples.items():
        rho, _ = sp_stats.spearmanr(arr, samples)
        sensitivity[name] = float(rho ** 2)

    return {
        "median": float(np.median(samples)),
        "mean": float(np.mean(samples)),
        "ci_90": engine.credible_interval(samples, 0.90),
        "ci_50": engine.credible_interval(samples, 0.50),
        "samples": samples,
        "sensitivity": sensitivity,
    }


def propagate_detection_prediction(
    state: DemyelinationState,
    detector: Detector | None = None,
    n_samples: int = 5000,
    seed: int = 42,
    exposure_s: float = 300.0,
    n_mice: int = 10,
) -> dict:
    """Detection significance with credible intervals.

    Returns dict with median/CI for: snr, p_value, effect_size.
    """
    if detector is None:
        detector = Detector.PMT()

    engine = UncertaintyEngine(n_samples=n_samples, seed=seed)
    engine.load_defaults()
    axon = AxonGeometry.typical_cns()
    wavelengths = C.DEFAULT_LAMBDA_RANGE_NM
    healthy = DemyelinationState(0, 0, 0)

    def model_fn(params: dict[str, float]) -> dict[str, float]:
        baseline = params.get("baseline_emission", C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S)
        hill_n = params.get("hill_n", C.HILL_N_EMISSION)
        hill_k = params.get("hill_k", C.HILL_K_HALF_DEFAULT)
        hill_smax = params.get("hill_smax", C.HILL_SMAX_NOMINAL)
        coupling = params.get("coupling_efficiency", C.COUPLING_EFFICIENCY_NOMINAL)
        animal_cv = params.get("animal_cv", C.ANIMAL_CV_NOMINAL)

        rng = np.random.default_rng()

        # Diseased emission rate
        d_spectrum = disease_emission(state, wavelengths,
                                      hill_n=hill_n, hill_k=hill_k, hill_smax=hill_smax)
        d_rate = float(np.trapezoid(d_spectrum, wavelengths)) * baseline / 100.0 * coupling / 1e-3

        # Healthy emission rate
        h_spectrum = disease_emission(healthy, wavelengths)
        h_rate = float(np.trapezoid(h_spectrum, wavelengths)) * baseline / 100.0 * coupling / 1e-3

        # Per-animal variability
        d_rates = d_rate * rng.lognormal(0, animal_cv, size=n_mice)
        h_rates = h_rate * rng.lognormal(0, animal_cv, size=n_mice)

        # Simulate counts
        d_counts = np.array([rng.poisson(max(1e-10, r * detector.quantum_efficiency + detector.dark_rate_hz) * exposure_s)
                             for r in d_rates])
        h_counts = np.array([rng.poisson(max(1e-10, r * detector.quantum_efficiency + detector.dark_rate_hz) * exposure_s)
                             for r in h_rates])

        # Between-subjects test
        result = compare_groups(d_counts.astype(float), h_counts.astype(float))
        snr = d_rate / max(h_rate, 1e-30)

        return {
            "snr": snr,
            "p_value": result["p_value"],
            "effect_size": result["effect_size"],
        }

    results = engine.propagate(model_fn)

    out = {}
    for key in ["snr", "p_value", "effect_size"]:
        arr = results[key]
        out[f"{key}_median"] = float(np.median(arr))
        out[f"{key}_ci_90"] = engine.credible_interval(arr, 0.90)
        out[f"{key}_samples"] = arr

    return out


def propagate_roc_prediction(
    n_healthy: int = 10,
    n_disease: int = 10,
    state: DemyelinationState | None = None,
    n_samples: int = 1000,
    seed: int = 42,
) -> dict:
    """AUC with credible intervals from Monte Carlo.

    Returns dict with median AUC, CI, and sample array.
    """
    if state is None:
        state = DemyelinationState(alpha=0.6, gamma=0.3, rho=0.2)

    engine = UncertaintyEngine(n_samples=n_samples, seed=seed)
    engine.load_defaults()
    axon = AxonGeometry.typical_cns()
    wavelengths = C.DEFAULT_LAMBDA_RANGE_NM
    healthy = DemyelinationState(0, 0, 0)

    auc_samples = []
    rng = np.random.default_rng(seed)

    for i in range(n_samples):
        params = {}
        for name, pd in engine.parameters.items():
            params[name] = float(pd.sample(rng, 1)[0])

        animal_cv = params.get("animal_cv", C.ANIMAL_CV_NOMINAL)

        # Generate feature vectors with biological variability
        healthy_features = []
        disease_features = []
        for _ in range(n_healthy):
            bio_mult = rng.lognormal(0, animal_cv)
            fv = compute_feature_vector(axon, healthy, wavelengths, rng)
            fv["total_intensity"] *= bio_mult
            healthy_features.append(fv)
        for _ in range(n_disease):
            bio_mult = rng.lognormal(0, animal_cv)
            fv = compute_feature_vector(axon, state, wavelengths, rng)
            fv["total_intensity"] *= bio_mult
            disease_features.append(fv)

        roc = compute_roc(healthy_features, disease_features, feature_key="total_intensity",
                          cross_validate=True)
        auc_val = roc.get("cv_auc", roc["auc"])
        auc_samples.append(auc_val)

    auc_arr = np.array(auc_samples)
    return {
        "auc_median": float(np.median(auc_arr)),
        "auc_mean": float(np.mean(auc_arr)),
        "auc_ci_90": engine.credible_interval(auc_arr, 0.90),
        "auc_ci_50": engine.credible_interval(auc_arr, 0.50),
        "auc_samples": auc_arr,
    }


def tornado_plot_data(
    state: DemyelinationState,
    param_list: list[ParameterDistribution] | None = None,
    output_key: str = "emission_rate",
) -> dict:
    """One-at-a-time sensitivity for tornado chart.

    For each parameter, evaluates the model at the 10th and 90th percentile
    while holding all others at nominal. Returns sorted by impact.

    Returns dict with keys: param_names, low_values, high_values, nominal_value.
    """
    if param_list is None:
        param_list = build_default_parameter_set()

    axon = AxonGeometry.typical_cns()
    wavelengths = C.DEFAULT_LAMBDA_RANGE_NM

    def evaluate(params: dict[str, float]) -> float:
        baseline = params.get("baseline_emission", C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S)
        hill_n = params.get("hill_n", C.HILL_N_EMISSION)
        hill_k = params.get("hill_k", C.HILL_K_HALF_DEFAULT)
        hill_smax = params.get("hill_smax", C.HILL_SMAX_NOMINAL)
        coupling = params.get("coupling_efficiency", C.COUPLING_EFFICIENCY_NOMINAL)

        spectrum = disease_emission(state, wavelengths,
                                    hill_n=hill_n, hill_k=hill_k, hill_smax=hill_smax)
        return float(np.trapezoid(spectrum, wavelengths)) * baseline / 100.0 * coupling / 1e-3

    nominals = {pd.name: pd.nominal for pd in param_list}
    nominal_value = evaluate(nominals)

    param_names = []
    low_values = []
    high_values = []

    rng = np.random.default_rng(42)
    for pd in param_list:
        # Get 10th and 90th percentile of this parameter's distribution
        samples = pd.sample(rng, 10000)
        p10 = float(np.percentile(samples, 10))
        p90 = float(np.percentile(samples, 90))

        params_low = dict(nominals)
        params_low[pd.name] = p10
        params_high = dict(nominals)
        params_high[pd.name] = p90

        val_low = evaluate(params_low)
        val_high = evaluate(params_high)

        param_names.append(pd.name)
        low_values.append(val_low)
        high_values.append(val_high)

    # Sort by total swing (descending)
    swings = [abs(h - l) for l, h in zip(low_values, high_values)]
    order = np.argsort(swings)[::-1]

    return {
        "param_names": [param_names[i] for i in order],
        "low_values": [low_values[i] for i in order],
        "high_values": [high_values[i] for i in order],
        "nominal_value": nominal_value,
    }


def run_full_cascade_mc(
    weeks: int = 12,
    n_samples: int = 1000,
    seed: int = 42,
    n_mice: int = 10,
    detector: Detector | None = None,
) -> dict:
    """Full cuprizone experiment with all uncertainties propagated.

    Returns credible intervals for first_significant_week, peak_effect_size,
    and AUC at each timepoint.
    """
    if detector is None:
        detector = Detector.PMT()

    engine = UncertaintyEngine(n_samples=n_samples, seed=seed)
    engine.load_defaults()
    axon = AxonGeometry.typical_cns()
    wavelengths = C.DEFAULT_LAMBDA_RANGE_NM
    healthy = DemyelinationState(0, 0, 0)
    measurement_weeks = np.arange(0, weeks + 0.01, 1.0)

    first_sig_weeks = []
    peak_effect_sizes = []
    # Per-timepoint collections
    effect_sizes_by_week = {float(w): [] for w in measurement_weeks}
    p_values_by_week = {float(w): [] for w in measurement_weeks}

    rng = np.random.default_rng(seed)

    for mc_i in range(n_samples):
        params = {}
        for name, pd in engine.parameters.items():
            params[name] = float(pd.sample(rng, 1)[0])

        baseline = params.get("baseline_emission", C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S)
        hill_n = params.get("hill_n", C.HILL_N_EMISSION)
        hill_k = params.get("hill_k", C.HILL_K_HALF_DEFAULT)
        hill_smax = params.get("hill_smax", C.HILL_SMAX_NOMINAL)
        coupling = params.get("coupling_efficiency", C.COUPLING_EFFICIENCY_NOMINAL)
        animal_cv = params.get("animal_cv", C.ANIMAL_CV_NOMINAL)

        # Per-animal baseline multipliers (persists across weeks for this MC run)
        treated_multipliers = rng.lognormal(0, animal_cv, size=n_mice)
        control_multipliers = rng.lognormal(0, animal_cv, size=n_mice)

        # Scale factor for MC-varied baseline and coupling
        scale = (baseline / C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S) * (coupling / C.COUPLING_EFFICIENCY_NOMINAL)

        # Healthy rate via full waveguide pipeline
        from .emission import waveguide_filtered_emission
        collection_area = 0.01  # 1 mm² fiber bundle
        h_spectrum = waveguide_filtered_emission(axon, healthy, wavelengths)
        h_rate_base = float(np.trapezoid(h_spectrum, wavelengths)) * collection_area * scale

        first_sig = None
        max_es = 0.0

        for week in measurement_weeks:
            state = cuprizone_timeline(float(week))
            d_spectrum = waveguide_filtered_emission(
                axon, state, wavelengths,
                hill_n=hill_n, hill_k=hill_k, hill_smax=hill_smax)
            d_rate_base = float(np.trapezoid(d_spectrum, wavelengths)) * collection_area * scale

            # Per-animal counts
            d_counts = np.array([
                rng.poisson(max(1e-10, d_rate_base * m * detector.quantum_efficiency
                                + detector.dark_rate_hz) * 300.0)
                for m in treated_multipliers
            ], dtype=float)
            h_counts = np.array([
                rng.poisson(max(1e-10, h_rate_base * m * detector.quantum_efficiency
                                + detector.dark_rate_hz) * 300.0)
                for m in control_multipliers
            ], dtype=float)

            result = compare_groups(d_counts, h_counts)
            es = result["effect_size"]
            pv = result["p_value"]

            effect_sizes_by_week[float(week)].append(es)
            p_values_by_week[float(week)].append(pv)

            if es > max_es:
                max_es = es
            if first_sig is None and pv < 0.001:
                first_sig = float(week)

        first_sig_weeks.append(first_sig if first_sig is not None else float("inf"))
        peak_effect_sizes.append(max_es)

    first_sig_arr = np.array(first_sig_weeks)
    finite_mask = np.isfinite(first_sig_arr)
    peak_es_arr = np.array(peak_effect_sizes)

    result = {
        "first_significant_week_median": float(np.median(first_sig_arr[finite_mask]))
            if finite_mask.any() else float("inf"),
        "first_significant_week_ci": engine.credible_interval(first_sig_arr[finite_mask], 0.90)
            if finite_mask.any() else (float("inf"), float("inf")),
        "fraction_never_significant": float(1 - finite_mask.mean()),
        "peak_effect_size_median": float(np.median(peak_es_arr)),
        "peak_effect_size_ci": engine.credible_interval(peak_es_arr, 0.90),
        "effect_sizes_by_week": {},
        "p_values_by_week": {},
    }

    for week in measurement_weeks:
        w = float(week)
        es_arr = np.array(effect_sizes_by_week[w])
        pv_arr = np.array(p_values_by_week[w])
        result["effect_sizes_by_week"][w] = {
            "median": float(np.median(es_arr)),
            "ci_90": engine.credible_interval(es_arr, 0.90),
        }
        result["p_values_by_week"][w] = {
            "median": float(np.median(pv_arr)),
            "fraction_significant": float(np.mean(pv_arr < 0.05)),
        }

    return result
