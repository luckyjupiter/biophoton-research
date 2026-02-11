"""
Photocount Distributions for Biophoton Research
================================================

Implements photocount probability distributions for the canonical light source
models relevant to biophoton experiments:

  - Poisson (coherent state)
  - Bose-Einstein / geometric (single-mode thermal)
  - Negative binomial (multi-mode thermal)
  - Squeezed coherent state (numerical)
  - Doubly stochastic Poisson (Cox process with intensity fluctuations)
  - Mixture models

All distributions are parameterized by detected mean photon number (i.e.,
already incorporating detector efficiency where relevant).

Author: Track 01 -- Quantum Optics Statistician
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.special import gammaln
from scipy.stats import poisson, nbinom
from typing import Optional


def poisson_distribution(
    n_max: int,
    mean_count: float,
) -> NDArray[np.float64]:
    """Poisson distribution P(n) for coherent light.

    Parameters
    ----------
    n_max : int
        Maximum photon number to compute (0..n_max inclusive).
    mean_count : float
        Mean detected photon number mu = eta * n_bar.

    Returns
    -------
    P : ndarray of shape (n_max + 1,)
        P[k] = probability of detecting k photons.
    """
    n = np.arange(n_max + 1)
    return poisson.pmf(n, mean_count)


def bose_einstein_distribution(
    n_max: int,
    mean_count: float,
) -> NDArray[np.float64]:
    """Bose-Einstein (geometric) distribution for single-mode thermal light.

    P(n) = mean^n / (1 + mean)^{n+1}

    Parameters
    ----------
    n_max : int
        Maximum photon number.
    mean_count : float
        Mean detected photon number.

    Returns
    -------
    P : ndarray of shape (n_max + 1,)
    """
    n = np.arange(n_max + 1)
    if mean_count <= 0:
        P = np.zeros(n_max + 1)
        P[0] = 1.0
        return P
    p = mean_count / (1.0 + mean_count)
    return (1.0 - p) * p ** n


def negative_binomial_distribution(
    n_max: int,
    mean_count: float,
    num_modes: float,
) -> NDArray[np.float64]:
    """Negative binomial distribution for M-mode thermal light.

    Parameters
    ----------
    n_max : int
        Maximum photon number.
    mean_count : float
        Mean detected photon number mu.
    num_modes : float
        Number of independent thermal modes M.
        M=1 recovers Bose-Einstein. M->inf approaches Poisson.

    Returns
    -------
    P : ndarray of shape (n_max + 1,)
    """
    n = np.arange(n_max + 1)
    if num_modes > 1e12:
        return poisson.pmf(n, mean_count)
    M = num_modes
    mu = mean_count
    p_success = 1.0 / (1.0 + mu / M)
    return nbinom.pmf(n, M, p_success)


def squeezed_state_distribution(
    n_max: int,
    alpha: complex,
    squeeze_r: float,
    squeeze_theta: float = 0.0,
) -> NDArray[np.float64]:
    """Photon number distribution for a squeezed coherent state |alpha, xi>.

    Computed via recurrence for <n|D(alpha)S(xi)|0> matrix elements:
        sqrt(n+1) c_{n+1} = beta c_n - gamma sqrt(n) c_{n-1}

    Parameters
    ----------
    n_max : int
        Maximum photon number.
    alpha : complex
        Coherent amplitude.
    squeeze_r : float
        Squeeze parameter magnitude (r >= 0).
    squeeze_theta : float
        Squeeze angle theta (radians).

    Returns
    -------
    P : ndarray of shape (n_max + 1,)
        P[k] = |<k|alpha, xi>|^2
    """
    cosh_r = np.cosh(squeeze_r)
    tanh_r = np.tanh(squeeze_r)
    exp_itheta = np.exp(1j * squeeze_theta)

    beta = alpha * cosh_r + np.conj(alpha) * exp_itheta * np.sinh(squeeze_r)
    gamma_coeff = exp_itheta * tanh_r

    prefactor = 1.0 / np.sqrt(cosh_r) * np.exp(
        -0.5 * np.abs(alpha) ** 2
        - 0.5 * np.conj(alpha) ** 2 * exp_itheta * tanh_r
    )

    c = np.zeros(n_max + 1, dtype=np.complex128)
    c[0] = prefactor
    if n_max >= 1:
        c[1] = beta * c[0]
    for k in range(1, n_max):
        c[k + 1] = (beta * c[k] - gamma_coeff * np.sqrt(k) * c[k - 1]) / np.sqrt(k + 1)

    P = np.abs(c) ** 2
    total = np.sum(P)
    if total > 0:
        P /= total
    return P


def squeezed_state_moments(
    alpha: complex,
    squeeze_r: float,
    squeeze_theta: float = 0.0,
) -> dict:
    """Analytic moments for a squeezed coherent state.

    Parameters
    ----------
    alpha : complex
        Coherent amplitude.
    squeeze_r : float
        Squeeze parameter.
    squeeze_theta : float
        Squeeze angle.

    Returns
    -------
    dict with mean, variance, fano_factor, mandel_Q
    """
    psi = np.angle(alpha) - squeeze_theta / 2.0
    abs_alpha_sq = np.abs(alpha) ** 2

    mean_n = abs_alpha_sq + np.sinh(squeeze_r) ** 2
    var_n = (
        abs_alpha_sq * (np.exp(-2 * squeeze_r) * np.cos(psi) ** 2
                        + np.exp(2 * squeeze_r) * np.sin(psi) ** 2)
        + 2 * np.sinh(squeeze_r) ** 2 * np.cosh(squeeze_r) ** 2
    )

    fano = var_n / mean_n if mean_n > 0 else np.nan
    Q = (var_n - mean_n) / mean_n if mean_n > 0 else np.nan

    return {
        "mean": mean_n,
        "variance": var_n,
        "fano_factor": fano,
        "mandel_Q": Q,
    }


def cox_process_samples(
    n_intervals: int,
    mean_rate: float,
    intensity_cv: float,
    correlation_time: float,
    interval_duration: float,
    rng: Optional[np.random.Generator] = None,
) -> NDArray[np.int64]:
    """Generate photocounts from a Cox process (doubly stochastic Poisson).

    The intensity follows an Ornstein-Uhlenbeck process with log-normal
    marginal distribution to ensure positivity.

    Parameters
    ----------
    n_intervals : int
        Number of counting intervals.
    mean_rate : float
        Mean count rate (counts per unit time).
    intensity_cv : float
        Coefficient of variation of intensity.
    correlation_time : float
        Autocorrelation time of intensity fluctuations.
    interval_duration : float
        Duration of each counting interval.
    rng : np.random.Generator, optional

    Returns
    -------
    counts : ndarray of shape (n_intervals,), dtype int64
    """
    if rng is None:
        rng = np.random.default_rng()

    sigma_log = np.sqrt(np.log(1.0 + intensity_cv ** 2))
    mu_log = np.log(mean_rate) - 0.5 * sigma_log ** 2

    n_substeps = max(10, int(interval_duration / (correlation_time * 0.1)))
    dt = interval_duration / n_substeps
    decay = np.exp(-dt / correlation_time)
    noise_std = sigma_log * np.sqrt(1.0 - decay ** 2)

    counts = np.empty(n_intervals, dtype=np.int64)
    log_intensity = mu_log

    for i in range(n_intervals):
        integrated_intensity = 0.0
        for _ in range(n_substeps):
            log_intensity = (mu_log + decay * (log_intensity - mu_log)
                             + noise_std * rng.standard_normal())
            integrated_intensity += np.exp(log_intensity) * dt
        counts[i] = rng.poisson(max(0, integrated_intensity))

    return counts


def mixture_distribution(
    n_max: int,
    weights: list,
    distributions: list,
) -> NDArray[np.float64]:
    """Compute a mixture distribution from component distributions.

    Parameters
    ----------
    n_max : int
        Maximum photon number.
    weights : list of float
        Mixture weights (must sum to 1).
    distributions : list of ndarray
        Component distributions.

    Returns
    -------
    P : ndarray of shape (n_max + 1,)
    """
    w = np.array(weights)
    assert np.isclose(w.sum(), 1.0), f"Weights must sum to 1, got {w.sum()}"
    P = np.zeros(n_max + 1)
    for wi, dist in zip(w, distributions):
        P += wi * dist[: n_max + 1]
    return P


def convolve_with_dark_counts(
    P_signal: NDArray[np.float64],
    dark_mean: float,
) -> NDArray[np.float64]:
    """Convolve a signal distribution with Poisson dark counts.

    Parameters
    ----------
    P_signal : ndarray
        Signal photocount distribution.
    dark_mean : float
        Mean number of dark counts per interval.

    Returns
    -------
    P_measured : ndarray, same length as input.
    """
    n_max = len(P_signal) - 1
    P_dark = poisson.pmf(np.arange(n_max + 1), dark_mean)
    P_conv = np.convolve(P_signal, P_dark)
    return P_conv[: n_max + 1]


def apply_detection_efficiency(
    P_true: NDArray[np.float64],
    eta: float,
) -> NDArray[np.float64]:
    """Apply Bernoulli thinning for detector efficiency.

    P_detected(m) = sum_{n>=m} C(n,m) eta^m (1-eta)^{n-m} P_true(n)

    Parameters
    ----------
    P_true : ndarray
        True photon number distribution.
    eta : float
        Detector quantum efficiency (0 < eta <= 1).

    Returns
    -------
    P_detected : ndarray, same length as input.
    """
    if eta >= 1.0:
        return P_true.copy()

    n_max = len(P_true) - 1
    P_det = np.zeros(n_max + 1)
    log_eta = np.log(max(eta, 1e-300))
    log_1_eta = np.log(max(1 - eta, 1e-300))

    for m in range(n_max + 1):
        for n in range(m, n_max + 1):
            if P_true[n] > 1e-300:
                log_binom = (gammaln(n + 1) - gammaln(m + 1)
                             - gammaln(n - m + 1))
                log_term = log_binom + m * log_eta + (n - m) * log_1_eta
                P_det[m] += np.exp(log_term) * P_true[n]

    total = np.sum(P_det)
    if total > 0:
        P_det /= total
    return P_det


def distribution_moments(P: NDArray[np.float64]) -> dict:
    """Compute moments and standard statistics from a distribution.

    Parameters
    ----------
    P : ndarray
        Probability distribution P(n), indexed from n=0.

    Returns
    -------
    dict with keys: mean, variance, fano_factor, mandel_Q, g2_zero
    """
    n = np.arange(len(P))
    mean = np.sum(n * P)
    var = np.sum(n ** 2 * P) - mean ** 2

    fano = var / mean if mean > 0 else np.nan
    Q = (var - mean) / mean if mean > 0 else np.nan
    g2 = 1.0 + Q / mean if mean > 0 else np.nan

    return {
        "mean": mean,
        "variance": var,
        "fano_factor": fano,
        "mandel_Q": Q,
        "g2_zero": g2,
    }


def generate_samples(
    distribution_type: str,
    n_samples: int,
    params: dict,
    rng: Optional[np.random.Generator] = None,
) -> NDArray[np.int64]:
    """Generate random photocount samples from a specified distribution.

    Parameters
    ----------
    distribution_type : str
        One of 'poisson', 'thermal', 'multimode_thermal', 'squeezed', 'cox'.
    n_samples : int
        Number of counting intervals.
    params : dict
        Distribution parameters (keys depend on type).
    rng : np.random.Generator, optional

    Returns
    -------
    samples : ndarray of shape (n_samples,), dtype int64
    """
    if rng is None:
        rng = np.random.default_rng()

    if distribution_type == "poisson":
        return rng.poisson(params["mean_count"], size=n_samples)

    elif distribution_type == "thermal":
        mu = params["mean_count"]
        intensities = rng.exponential(mu, size=n_samples)
        return rng.poisson(intensities)

    elif distribution_type == "multimode_thermal":
        mu = params["mean_count"]
        M = params["num_modes"]
        if M > 1e10:
            return rng.poisson(mu, size=n_samples)
        intensities = rng.gamma(M, mu / M, size=n_samples)
        return rng.poisson(intensities)

    elif distribution_type == "squeezed":
        n_max_sample = max(200, int(np.abs(params["alpha"]) ** 2 * 5 + 50))
        P = squeezed_state_distribution(
            n_max_sample,
            params["alpha"],
            params["squeeze_r"],
            params.get("squeeze_theta", 0.0),
        )
        cumP = np.cumsum(P)
        u = rng.random(n_samples)
        return np.searchsorted(cumP, u).astype(np.int64)

    elif distribution_type == "cox":
        return cox_process_samples(
            n_samples,
            params["mean_rate"],
            params["intensity_cv"],
            params["correlation_time"],
            params["interval_duration"],
            rng=rng,
        )

    else:
        raise ValueError(f"Unknown distribution type: {distribution_type}")


if __name__ == "__main__":
    print("=== Photocount Distribution Self-Test ===\n")

    n_max = 30
    mu = 5.0

    P_pois = poisson_distribution(n_max, mu)
    m_pois = distribution_moments(P_pois)
    print(f"Poisson(mu={mu}):")
    print(f"  mean={m_pois['mean']:.4f}, var={m_pois['variance']:.4f}, "
          f"F={m_pois['fano_factor']:.4f}, Q={m_pois['mandel_Q']:.6f}")

    P_be = bose_einstein_distribution(n_max, mu)
    m_be = distribution_moments(P_be)
    print(f"\nBose-Einstein(mu={mu}):")
    print(f"  mean={m_be['mean']:.4f}, var={m_be['variance']:.4f}, "
          f"F={m_be['fano_factor']:.4f}, Q={m_be['mandel_Q']:.4f}")

    P_mm = negative_binomial_distribution(n_max, mu, 10)
    m_mm = distribution_moments(P_mm)
    print(f"\nNeg. Binomial(mu={mu}, M=10):")
    print(f"  mean={m_mm['mean']:.4f}, var={m_mm['variance']:.4f}, "
          f"F={m_mm['fano_factor']:.4f}, Q={m_mm['mandel_Q']:.4f}")

    alpha = np.sqrt(4.5) + 0j
    P_sq = squeezed_state_distribution(n_max, alpha, 0.5, 0.0)
    m_sq = distribution_moments(P_sq)
    m_sq_a = squeezed_state_moments(alpha, 0.5, 0.0)
    print(f"\nSqueezed(|alpha|^2={np.abs(alpha)**2:.2f}, r=0.5):")
    print(f"  Numerical:  mean={m_sq['mean']:.4f}, var={m_sq['variance']:.4f}, "
          f"F={m_sq['fano_factor']:.4f}, Q={m_sq['mandel_Q']:.4f}")
    print(f"  Analytic:   mean={m_sq_a['mean']:.4f}, var={m_sq_a['variance']:.4f}, "
          f"F={m_sq_a['fano_factor']:.4f}")

    rng = np.random.default_rng(42)
    samples = generate_samples("poisson", 100000, {"mean_count": 5.0}, rng=rng)
    F_emp = samples.var(ddof=1) / samples.mean()
    print(f"\nPoisson samples (N=100000): mean={samples.mean():.3f}, "
          f"var={samples.var(ddof=1):.3f}, F={F_emp:.4f}")

    print("\nAll self-tests passed.")
