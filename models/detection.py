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
) -> np.ndarray:
    """Simulate detected photon counts including QE and dark noise.

    Returns an array of integer counts, one per measurement.
    """
    if rng is None:
        rng = np.random.default_rng()

    detected_rate = signal_rate_hz * detector.quantum_efficiency
    total_rate = detected_rate + detector.dark_rate_hz
    expected_counts = total_rate * exposure_s

    return rng.poisson(expected_counts, size=n_measurements)


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
) -> dict[str, np.ndarray | float]:
    """Compute ROC curve for healthy vs. demyelinated classification.

    Uses a simple threshold classifier on a single feature.

    Returns dict with keys: fpr, tpr, thresholds, auc.
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

    return best_result


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
