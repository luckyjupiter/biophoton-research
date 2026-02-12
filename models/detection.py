"""
Detector simulation and statistical analysis for biophoton measurements.

Implements:
- Detector models (PMT, EM-CCD, SPAD, SNSPD) with realistic noise
- Poisson-sampled photon counting
- Li-Ma significance for on/off counting experiments
- Feldman-Cousins confidence intervals for low-count regime
- ROC curves and Bayesian classification
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats as sp_stats

from . import constants as C


@dataclass
class Detector:
    """Base detector model with dark rate, quantum efficiency, and timing jitter."""

    name: str
    dark_rate_hz: float
    quantum_efficiency: float
    timing_jitter_ns: float | None

    @classmethod
    def from_name(cls, name: str) -> Detector:
        """Create a detector from the constants table."""
        specs = C.DETECTOR_SPECS[name.upper()]
        return cls(
            name=name.upper(),
            dark_rate_hz=specs["dark_rate_hz"],
            quantum_efficiency=specs["quantum_efficiency"],
            timing_jitter_ns=specs["timing_jitter_ns"],
        )

    @classmethod
    def PMT(cls) -> Detector:
        return cls.from_name("PMT")

    @classmethod
    def EMCCD(cls) -> Detector:
        return cls.from_name("EMCCD")

    @classmethod
    def SPAD(cls) -> Detector:
        return cls.from_name("SPAD")

    @classmethod
    def SNSPD(cls) -> Detector:
        return cls.from_name("SNSPD")


def simulate_counts(
    signal_rate_hz: float,
    detector: Detector,
    exposure_s: float,
    n_measurements: int = 1,
    rng: np.random.Generator | None = None,
    animal_cv: float = 0.0,
    afterpulse_prob: float = 0.0,
    gain_drift_frac: float = 0.0,
) -> np.ndarray:
    """Simulate detected photon counts including QE, dark noise, and optional extras.

    Parameters
    ----------
    animal_cv : float
        Biological variability (coefficient of variation). When > 0, each
        measurement's signal rate is multiplied by lognormal(1, animal_cv).
    afterpulse_prob : float
        Probability that each detected photon triggers an afterpulse (0-1).
    gain_drift_frac : float
        Fractional gain drift per measurement (simulates detector instability).

    Returns an array of integer counts, one per measurement.
    """
    if rng is None:
        rng = np.random.default_rng()

    detected_rate = signal_rate_hz * detector.quantum_efficiency

    # Per-animal biological variability
    if animal_cv > 0:
        bio_multipliers = rng.lognormal(0, animal_cv, size=n_measurements)
        rates = detected_rate * bio_multipliers + detector.dark_rate_hz
    else:
        rates = np.full(n_measurements, detected_rate + detector.dark_rate_hz)

    # Gain drift: each measurement has slightly different effective gain
    if gain_drift_frac > 0:
        drift = 1.0 + rng.normal(0, gain_drift_frac, size=n_measurements)
        rates = rates * np.maximum(drift, 0.01)

    expected_counts = rates * exposure_s
    counts = rng.poisson(np.maximum(expected_counts, 0))

    # Afterpulsing: each real count has a probability of generating an extra
    if afterpulse_prob > 0:
        afterpulses = rng.binomial(counts, afterpulse_prob)
        counts = counts + afterpulses

    return counts


def li_ma_significance(n_on: float, n_off: float, alpha_ratio: float = 1.0) -> float:
    """Li-Ma significance for on-source / off-source counting experiment.

    S = √2 · { N_on · ln[(1+α)/α · N_on/(N_on+N_off)]
              + N_off · ln[(1+α) · N_off/(N_on+N_off)] }^(1/2)

    Parameters
    ----------
    n_on : float
        Counts in the "on" (signal + background) region.
    n_off : float
        Counts in the "off" (background only) region.
    alpha_ratio : float
        Ratio of on-exposure to off-exposure (typically 1.0 for equal exposures).

    Returns
    -------
    float
        Significance in standard deviations (σ). Positive = excess in on region.
    """
    if n_on <= 0 or n_off <= 0:
        return 0.0

    a = alpha_ratio
    total = n_on + n_off

    term1 = n_on * np.log((1 + a) / a * n_on / total)
    term2 = n_off * np.log((1 + a) * n_off / total)

    arg = 2 * (term1 + term2)
    if arg < 0:
        return 0.0
    return float(np.sqrt(arg))


def compare_groups(
    treated_counts: np.ndarray,
    control_counts: np.ndarray,
    test: str = "mann_whitney",
) -> dict:
    """Proper between-subjects statistical test for comparing two groups.

    Replaces Li-Ma (designed for on/off photon counting, not biological replicates)
    with tests appropriate for between-subjects designs with animal-level variability.

    Parameters
    ----------
    treated_counts : array
        Per-animal counts for treated group (N_treated,).
    control_counts : array
        Per-animal counts for control group (N_control,).
    test : str
        "mann_whitney" (default, nonparametric), "welch_t" (parametric),
        or "permutation" (exact).

    Returns
    -------
    dict with: statistic, p_value, effect_size (Cohen's d), effect_size_ci.
    """
    treated = np.asarray(treated_counts, dtype=float)
    control = np.asarray(control_counts, dtype=float)

    # Cohen's d effect size
    n_t, n_c = len(treated), len(control)
    m_t, m_c = np.mean(treated), np.mean(control)
    s_t, s_c = np.std(treated, ddof=1), np.std(control, ddof=1)
    # Pooled standard deviation
    s_pooled = np.sqrt(((n_t - 1) * s_t**2 + (n_c - 1) * s_c**2) / (n_t + n_c - 2)) if (n_t + n_c > 2) else 1.0
    cohens_d = (m_t - m_c) / s_pooled if s_pooled > 0 else 0.0

    # Approximate CI for Cohen's d (Hedges & Olkin)
    se_d = np.sqrt((n_t + n_c) / (n_t * n_c) + cohens_d**2 / (2 * (n_t + n_c)))
    d_ci = (cohens_d - 1.96 * se_d, cohens_d + 1.96 * se_d)

    if test == "mann_whitney":
        stat, p_value = sp_stats.mannwhitneyu(treated, control, alternative="two-sided")
    elif test == "welch_t":
        stat, p_value = sp_stats.ttest_ind(treated, control, equal_var=False)
        p_value = float(p_value)
    elif test == "permutation":
        combined = np.concatenate([treated, control])
        observed_diff = m_t - m_c
        rng = np.random.default_rng(42)
        n_perm = 9999
        count_extreme = 0
        for _ in range(n_perm):
            rng.shuffle(combined)
            perm_diff = np.mean(combined[:n_t]) - np.mean(combined[n_t:])
            if abs(perm_diff) >= abs(observed_diff):
                count_extreme += 1
        p_value = (count_extreme + 1) / (n_perm + 1)
        stat = observed_diff
    else:
        raise ValueError(f"Unknown test: {test}")

    return {
        "statistic": float(stat),
        "p_value": float(p_value),
        "effect_size": float(cohens_d),
        "effect_size_ci": (float(d_ci[0]), float(d_ci[1])),
        "test": test,
    }


def feldman_cousins_interval(
    n_observed: int,
    background: float,
    confidence: float = 0.90,
) -> tuple[float, float]:
    """Feldman-Cousins confidence interval for Poisson signal with known background.

    Uses the unified approach that correctly handles the transition between
    upper limits (low counts) and two-sided intervals (high counts).

    Simplified implementation using scipy for the Poisson CDF.
    """
    # Grid search over possible signal values
    mu_max = max(n_observed * 3, 30)
    mu_grid = np.linspace(0, mu_max, 1000)

    # For each mu, compute the probability of observing n_observed or fewer
    # using the ordering principle
    lower = 0.0
    upper = mu_max

    alpha = 1 - confidence
    for mu in mu_grid:
        total_mu = mu + background
        # Acceptance: P(n ≤ n_observed | mu + bg) - check if n_observed is in acceptance region
        p_value = 1 - sp_stats.poisson.cdf(n_observed - 1, total_mu) if n_observed > 0 else sp_stats.poisson.pmf(0, total_mu)

        if p_value > alpha / 2:
            if mu < upper:
                lower = mu
                break

    for mu in reversed(mu_grid):
        total_mu = mu + background
        p_value = sp_stats.poisson.cdf(n_observed, total_mu)
        if p_value > alpha / 2:
            upper = mu
            break

    return (max(0.0, lower), upper)


def compute_roc(
    healthy_features: list[dict[str, float]],
    disease_features: list[dict[str, float]],
    feature_key: str = "total_intensity",
    cross_validate: bool = False,
) -> dict[str, np.ndarray | float]:
    """Compute ROC curve for healthy vs. demyelinated classification.

    Uses a simple threshold classifier on a single feature.

    Parameters
    ----------
    cross_validate : bool
        When True, also compute leave-one-out cross-validated AUC where each
        sample is classified using stats from the remaining samples. This
        prevents overfitting and gives a more honest AUC estimate.

    Returns dict with keys: fpr, tpr, thresholds, auc, and optionally cv_auc.
    """
    h_vals = np.array([f[feature_key] for f in healthy_features])
    d_vals = np.array([f[feature_key] for f in disease_features])

    # Try both directions: disease > healthy AND disease < healthy
    # Pick whichever gives AUC > 0.5 (i.e. better than random)
    best_auc = 0.0
    best_result = None

    for sign in [1, -1]:
        hv = sign * h_vals
        dv = sign * d_vals

        all_vals = np.concatenate([hv, dv])
        thresholds = np.sort(np.unique(all_vals))
        thresholds = np.concatenate([[thresholds[0] - 1], thresholds, [thresholds[-1] + 1]])

        tpr = np.zeros(len(thresholds))
        fpr = np.zeros(len(thresholds))

        for i, thresh in enumerate(thresholds):
            # Positive = above threshold = classified as diseased
            tpr[i] = np.mean(dv >= thresh)
            fpr[i] = np.mean(hv >= thresh)

        # Sort by FPR for proper ROC curve
        order = np.argsort(fpr)
        fpr_sorted = fpr[order]
        tpr_sorted = tpr[order]

        auc = float(np.trapezoid(tpr_sorted, fpr_sorted))
        if auc > best_auc:
            best_auc = auc
            best_result = {
                "fpr": fpr_sorted,
                "tpr": tpr_sorted,
                "thresholds": thresholds[order] * sign,
                "auc": auc,
            }

    # LOO cross-validated AUC
    if cross_validate and best_result is not None:
        h_vals = np.array([f[feature_key] for f in healthy_features])
        d_vals = np.array([f[feature_key] for f in disease_features])
        all_vals = np.concatenate([h_vals, d_vals])
        labels = np.concatenate([np.zeros(len(h_vals)), np.ones(len(d_vals))])
        n_total = len(all_vals)

        loo_scores = np.zeros(n_total)
        for i in range(n_total):
            # Leave one out
            train_vals = np.delete(all_vals, i)
            train_labels = np.delete(labels, i)
            # Simple classifier: compare to mean of each class in training set
            h_mean = np.mean(train_vals[train_labels == 0])
            d_mean = np.mean(train_vals[train_labels == 1])
            midpoint = (h_mean + d_mean) / 2
            # Score: distance from midpoint, signed by which class is higher
            if d_mean > h_mean:
                loo_scores[i] = all_vals[i] - midpoint
            else:
                loo_scores[i] = midpoint - all_vals[i]

        # Compute AUC from LOO scores
        h_scores = loo_scores[labels == 0]
        d_scores = loo_scores[labels == 1]
        # Mann-Whitney U statistic as AUC estimator
        n_h, n_d = len(h_scores), len(d_scores)
        if n_h > 0 and n_d > 0:
            u_count = sum(1 for hs in h_scores for ds in d_scores if ds > hs)
            u_count += 0.5 * sum(1 for hs in h_scores for ds in d_scores if ds == hs)
            cv_auc = u_count / (n_h * n_d)
        else:
            cv_auc = 0.5
        best_result["cv_auc"] = float(cv_auc)

    return best_result


def simulate_measurement(
    signal_rate: float,
    detector: Detector,
    exposure_s: float,
    animal_cv: float = 0.35,
    autofluorescence_rate: float = 0.0,
    extraction_artifact: float = 0.0,
    temperature_cv: float = 0.0,
    rng: np.random.Generator | None = None,
) -> dict:
    """Realistic single-animal measurement with all noise sources.

    Parameters
    ----------
    signal_rate : float
        True biophoton signal rate (photons/s).
    detector : Detector
        Detector model.
    exposure_s : float
        Integration time in seconds.
    animal_cv : float
        Animal-to-animal biological variability (coefficient of variation).
    autofluorescence_rate : float
        Background rate from tissue autofluorescence (photons/s).
    extraction_artifact : float
        Additional ROS signal from tissue preparation (photons/s).
    temperature_cv : float
        Fractional temperature variation affecting dark rate.

    Returns
    -------
    dict with: counts, true_signal, noise_breakdown, snr.
    """
    if rng is None:
        rng = np.random.default_rng()

    # Biological variability
    bio_mult = rng.lognormal(0, animal_cv) if animal_cv > 0 else 1.0
    effective_signal = signal_rate * bio_mult

    # Confound sources
    confound_rate = autofluorescence_rate + extraction_artifact

    # Temperature-dependent dark rate
    dark = detector.dark_rate_hz
    if temperature_cv > 0:
        dark *= rng.lognormal(0, temperature_cv)

    # Total detected rate
    total_rate = (effective_signal + confound_rate) * detector.quantum_efficiency + dark
    expected_counts = max(total_rate * exposure_s, 0)
    counts = int(rng.poisson(expected_counts))

    # Noise breakdown
    signal_counts = effective_signal * detector.quantum_efficiency * exposure_s
    dark_counts = dark * exposure_s
    confound_counts = confound_rate * detector.quantum_efficiency * exposure_s
    snr = signal_counts / np.sqrt(signal_counts + dark_counts + confound_counts) if (signal_counts + dark_counts + confound_counts) > 0 else 0.0

    return {
        "counts": counts,
        "true_signal_rate": effective_signal,
        "bio_multiplier": bio_mult,
        "noise_breakdown": {
            "signal": signal_counts,
            "dark": dark_counts,
            "confound": confound_counts,
            "shot_noise_sigma": np.sqrt(expected_counts),
        },
        "snr": float(snr),
    }


def bayesian_classifier(
    features: dict[str, float],
    healthy_prior: float = 0.5,
    healthy_stats: dict[str, tuple[float, float]] | None = None,
    disease_stats: dict[str, tuple[float, float]] | None = None,
) -> dict[str, float]:
    """Bayesian 6-feature classifier: compute posterior odds of demyelination.

    Assumes Gaussian feature distributions with known mean/std for each class.
    Uses all 6 features from compute_feature_vector().

    Parameters
    ----------
    features : dict
        The 6-feature measurement vector.
    healthy_prior : float
        Prior probability of healthy (default 0.5 = no prior preference).
    healthy_stats, disease_stats : dict
        Mapping feature_name → (mean, std) for each class. If None, uses defaults.

    Returns
    -------
    dict with keys: p_healthy, p_disease, log_odds, classification
    """
    if healthy_stats is None:
        healthy_stats = {
            "total_intensity": (500.0, 100.0),
            "peak_wavelength": (480.0, 30.0),
            "spectral_width": (120.0, 20.0),
            "temporal_variance": (500.0, 150.0),
            "coherence_degree": (0.8, 0.1),
            "polarization_ratio": (0.6, 0.1),
        }
    if disease_stats is None:
        disease_stats = {
            "total_intensity": (2000.0, 500.0),
            "peak_wavelength": (450.0, 40.0),
            "spectral_width": (180.0, 40.0),
            "temporal_variance": (3000.0, 1000.0),
            "coherence_degree": (0.3, 0.15),
            "polarization_ratio": (0.2, 0.15),
        }

    log_likelihood_healthy = 0.0
    log_likelihood_disease = 0.0

    for key, value in features.items():
        if key in healthy_stats and key in disease_stats:
            h_mean, h_std = healthy_stats[key]
            d_mean, d_std = disease_stats[key]
            log_likelihood_healthy += sp_stats.norm.logpdf(value, h_mean, h_std)
            log_likelihood_disease += sp_stats.norm.logpdf(value, d_mean, d_std)

    # Log posterior odds
    log_prior_odds = np.log(healthy_prior / (1 - healthy_prior))
    log_odds = log_prior_odds + log_likelihood_healthy - log_likelihood_disease

    # Convert to probabilities
    p_healthy = 1 / (1 + np.exp(-log_odds))
    p_disease = 1 - p_healthy

    return {
        "p_healthy": float(p_healthy),
        "p_disease": float(p_disease),
        "log_odds": float(log_odds),
        "classification": "healthy" if p_healthy > 0.5 else "demyelinated",
    }
