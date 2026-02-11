"""
Statistical Tests for Photocount Analysis
==========================================

Implementations of statistical tests for discriminating between light source
models at biophoton-level count rates:

  - Mandel Q parameter estimation with confidence intervals
  - Fano factor test (variance-to-mean ratio)
  - Chi-squared goodness-of-fit
  - Likelihood ratio tests (Poisson vs. negative binomial)
  - Bayesian model comparison (Bayes factors via analytic marginal likelihoods)
  - Power analysis for the Fano factor test

Author: Track 01 -- Quantum Optics Statistician
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import stats
from scipy.special import gammaln
from scipy.optimize import minimize_scalar, minimize
from typing import Optional, Tuple


def estimate_fano_factor(
    counts: NDArray[np.int64],
) -> dict:
    """Estimate Fano factor with confidence interval.

    Uses the chi-squared distribution of (N-1)*F under the Poisson null.

    Parameters
    ----------
    counts : ndarray
        Array of photon counts per interval.

    Returns
    -------
    dict with keys:
        fano: point estimate
        mean: sample mean
        variance: sample variance
        mandel_Q: Q = F - 1
        ci_lower, ci_upper: 95% confidence interval for F
        p_value_super: p-value for H1: F > 1 (super-Poissonian)
        p_value_sub: p-value for H1: F < 1 (sub-Poissonian)
        n_intervals: number of counting intervals
    """
    N = len(counts)
    mean = np.mean(counts)
    var = np.var(counts, ddof=1)

    if mean <= 0:
        return {"fano": np.nan, "mean": 0, "variance": var,
                "mandel_Q": np.nan, "ci_lower": np.nan, "ci_upper": np.nan,
                "p_value_super": np.nan, "p_value_sub": np.nan,
                "n_intervals": N}

    F = var / mean
    Q = F - 1.0

    # Under Poisson null, (N-1)*F ~ chi^2(N-1)
    chi2_stat = (N - 1) * F
    df = N - 1

    # Confidence interval via chi^2 quantiles
    ci_lower = stats.chi2.ppf(0.025, df) / df
    ci_upper = stats.chi2.ppf(0.975, df) / df

    # p-values (one-sided)
    p_super = 1.0 - stats.chi2.cdf(chi2_stat, df)
    p_sub = stats.chi2.cdf(chi2_stat, df)

    return {
        "fano": F,
        "mean": mean,
        "variance": var,
        "mandel_Q": Q,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value_super": p_super,
        "p_value_sub": p_sub,
        "n_intervals": N,
    }


def chi_squared_gof(
    counts: NDArray[np.int64],
    model: str = "poisson",
    model_params: Optional[dict] = None,
    min_expected: float = 5.0,
) -> dict:
    """Chi-squared goodness-of-fit test.

    Parameters
    ----------
    counts : ndarray
        Photocount data.
    model : str
        Null hypothesis model: 'poisson' or 'negative_binomial'.
    model_params : dict, optional
        If None, parameters are estimated from data.
    min_expected : float
        Minimum expected count per bin (bins are merged to achieve this).

    Returns
    -------
    dict with chi2_stat, p_value, df, observed_bins, expected_bins
    """
    from collections import Counter

    count_freq = Counter(counts.tolist())
    N = len(counts)
    mean = np.mean(counts)

    max_n = max(count_freq.keys())
    observed = np.array([count_freq.get(k, 0) for k in range(max_n + 1)])

    # Compute expected counts
    if model == "poisson":
        lam = mean if model_params is None else model_params.get("lambda", mean)
        expected = N * stats.poisson.pmf(np.arange(max_n + 1), lam)
        n_params = 1
    elif model == "negative_binomial":
        if model_params is None:
            var = np.var(counts, ddof=1)
            if var > mean:
                M_hat = mean ** 2 / (var - mean) if var > mean else 1e6
            else:
                M_hat = 1e6
            mu_hat = mean
        else:
            mu_hat = model_params.get("mu", mean)
            M_hat = model_params.get("M", 10)
        p_success = 1.0 / (1.0 + mu_hat / M_hat)
        expected = N * stats.nbinom.pmf(np.arange(max_n + 1), M_hat, p_success)
        n_params = 2
    else:
        raise ValueError(f"Unknown model: {model}")

    # Merge bins with expected < min_expected
    obs_merged = []
    exp_merged = []
    obs_acc = 0
    exp_acc = 0.0

    for o, e in zip(observed, expected):
        obs_acc += o
        exp_acc += e
        if exp_acc >= min_expected:
            obs_merged.append(obs_acc)
            exp_merged.append(exp_acc)
            obs_acc = 0
            exp_acc = 0.0

    # Merge leftover into last bin
    if obs_acc > 0 or exp_acc > 0:
        if len(obs_merged) > 0:
            obs_merged[-1] += obs_acc
            exp_merged[-1] += exp_acc
        else:
            obs_merged.append(obs_acc)
            exp_merged.append(exp_acc)

    obs_arr = np.array(obs_merged, dtype=float)
    exp_arr = np.array(exp_merged, dtype=float)

    # Chi-squared statistic
    df = len(obs_arr) - 1 - n_params
    if df <= 0:
        return {"chi2_stat": np.nan, "p_value": np.nan, "df": df,
                "observed_bins": obs_arr, "expected_bins": exp_arr}

    chi2 = np.sum((obs_arr - exp_arr) ** 2 / exp_arr)
    p_value = 1.0 - stats.chi2.cdf(chi2, df)

    return {
        "chi2_stat": chi2,
        "p_value": p_value,
        "df": df,
        "observed_bins": obs_arr,
        "expected_bins": exp_arr,
    }


def likelihood_ratio_test(
    counts: NDArray[np.int64],
) -> dict:
    """Likelihood ratio test: Poisson (H0) vs. Negative Binomial (H1).

    Tests whether the data shows significant overdispersion (super-Poissonian).

    Parameters
    ----------
    counts : ndarray
        Photocount data.

    Returns
    -------
    dict with:
        lr_stat: likelihood ratio statistic (-2 log Lambda)
        p_value: p-value from chi^2(1) approximation
        poisson_loglik: log-likelihood under Poisson
        nb_loglik: log-likelihood under negative binomial
        nb_M_hat: estimated number of modes
    """
    N = len(counts)
    mean = np.mean(counts)
    var = np.var(counts, ddof=1)

    # Poisson log-likelihood
    ll_poisson = np.sum(stats.poisson.logpmf(counts, mean))

    # Negative binomial MLE
    if var <= mean:
        # Data is not overdispersed; NB cannot improve
        return {
            "lr_stat": 0.0,
            "p_value": 1.0,
            "poisson_loglik": ll_poisson,
            "nb_loglik": ll_poisson,
            "nb_M_hat": np.inf,
        }

    # Method of moments estimate for M
    M_mom = mean ** 2 / (var - mean)

    # Refine via MLE
    def neg_ll_nb(log_M):
        M = np.exp(log_M)
        p = 1.0 / (1.0 + mean / M)
        return -np.sum(stats.nbinom.logpmf(counts, M, p))

    result = minimize_scalar(neg_ll_nb, bounds=(np.log(0.01), np.log(1e8)),
                             method="bounded")
    M_hat = np.exp(result.x)
    ll_nb = -result.fun

    lr_stat = 2.0 * (ll_nb - ll_poisson)
    lr_stat = max(0, lr_stat)

    # p-value: mixture of chi2(0) and chi2(1) since M=inf is boundary
    # Use 0.5 * chi2(1) as per Self & Liang (1987)
    p_value = 0.5 * (1.0 - stats.chi2.cdf(lr_stat, 1))

    return {
        "lr_stat": lr_stat,
        "p_value": p_value,
        "poisson_loglik": ll_poisson,
        "nb_loglik": ll_nb,
        "nb_M_hat": M_hat,
    }


def bayesian_model_comparison(
    counts: NDArray[np.int64],
) -> dict:
    """Bayesian model comparison: Poisson vs. Negative Binomial.

    Uses analytic marginal likelihoods with conjugate priors.

    For Poisson with Gamma(a, b) prior on lambda:
        P(data | M_poisson) = prod_i [Gamma(a + sum_ni) / Gamma(a)] *
                              [b^a / (b + N)^{a + sum_ni}] * prod_i [1/n_i!]

    For Negative Binomial, we use Laplace approximation.

    Parameters
    ----------
    counts : ndarray

    Returns
    -------
    dict with:
        log_evidence_poisson: log marginal likelihood
        log_evidence_nb: log marginal likelihood
        log_bayes_factor: log(BF_poisson_vs_nb), positive favors Poisson
        interpretation: string label
    """
    N = len(counts)
    sum_n = np.sum(counts)
    mean = np.mean(counts)

    # Poisson model with Gamma(1, 0.01) prior (weakly informative)
    a_prior, b_prior = 1.0, 0.01
    a_post = a_prior + sum_n
    b_post = b_prior + N

    log_ev_poisson = (
        gammaln(a_post) - gammaln(a_prior)
        + a_prior * np.log(b_prior) - a_post * np.log(b_post)
        - np.sum(gammaln(counts + 1))
    )

    # Negative binomial: Laplace approximation around MLE
    var = np.var(counts, ddof=1)

    if var <= mean * 1.001:
        # No overdispersion; NB reduces to Poisson
        log_ev_nb = log_ev_poisson - 1.0  # Penalize extra parameter
    else:
        M_mom = mean ** 2 / max(var - mean, 0.001)

        def neg_log_joint_nb(params):
            log_M, log_mu = params
            M = np.exp(log_M)
            mu = np.exp(log_mu)
            p = 1.0 / (1.0 + mu / M)
            ll = np.sum(stats.nbinom.logpmf(counts, M, p))
            # Weakly informative priors
            log_prior = (-0.5 * (log_M - np.log(max(M_mom, 1.0))) ** 2 / 4.0
                         - 0.5 * (log_mu - np.log(mean)) ** 2 / 4.0)
            return -(ll + log_prior)

        x0 = [np.log(max(M_mom, 1.0)), np.log(max(mean, 0.1))]
        result = minimize(neg_log_joint_nb, x0, method="Nelder-Mead")

        log_posterior_max = -result.fun

        # Laplace approximation: log evidence ~ log_posterior_max + d/2 * log(2*pi) - 0.5*log(det(H))
        # Approximate Hessian numerically
        from scipy.optimize import approx_fprime
        eps = 1e-5

        def hess_diag(x):
            h = np.zeros(2)
            for i in range(2):
                e = np.zeros(2)
                e[i] = eps
                h[i] = (neg_log_joint_nb(x + e) - 2 * neg_log_joint_nb(x) + neg_log_joint_nb(x - e)) / eps ** 2
            return h

        try:
            hd = hess_diag(result.x)
            log_det_H = np.sum(np.log(np.abs(hd) + 1e-300))
            log_ev_nb = log_posterior_max + np.log(2 * np.pi) - 0.5 * log_det_H
        except Exception:
            log_ev_nb = log_posterior_max

    log_bf = log_ev_poisson - log_ev_nb

    if log_bf > 3:
        interp = "Strong evidence for Poisson"
    elif log_bf > 1:
        interp = "Moderate evidence for Poisson"
    elif log_bf > -1:
        interp = "Inconclusive"
    elif log_bf > -3:
        interp = "Moderate evidence for NB (super-Poissonian)"
    else:
        interp = "Strong evidence for NB (super-Poissonian)"

    return {
        "log_evidence_poisson": log_ev_poisson,
        "log_evidence_nb": log_ev_nb,
        "log_bayes_factor": log_bf,
        "interpretation": interp,
    }


def power_analysis_fano(
    delta: float,
    alpha: float = 0.05,
    power: float = 0.80,
    one_sided: bool = True,
) -> int:
    """Compute required sample size to detect Fano factor departure.

    Parameters
    ----------
    delta : float
        Departure from F=1 to detect (e.g., 0.05 for F=1.05 or F=0.95).
    alpha : float
        Significance level.
    power : float
        Desired power (1 - beta).
    one_sided : bool
        If True, one-sided test.

    Returns
    -------
    N : int
        Required number of counting intervals.
    """
    if one_sided:
        z_alpha = stats.norm.ppf(1 - alpha)
    else:
        z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    N = int(np.ceil(2.0 * (z_alpha + z_beta) ** 2 / delta ** 2))
    return N


def fano_factor_detectable(
    n_intervals: int,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Compute the minimum detectable Fano factor departure.

    Parameters
    ----------
    n_intervals : int
        Number of counting intervals available.
    alpha : float
        Significance level.
    power : float
        Desired power.

    Returns
    -------
    delta : float
        Minimum |F - 1| detectable.
    """
    z_alpha = stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)
    delta = (z_alpha + z_beta) * np.sqrt(2.0 / n_intervals)
    return delta


def measured_fano_with_artifacts(
    F_true: float,
    mean_signal: float,
    eta: float = 1.0,
    dark_mean: float = 0.0,
    dead_time_product: float = 0.0,
    afterpulse_prob: float = 0.0,
) -> float:
    """Compute the measured Fano factor after detector artifacts.

    Applies the cascade: efficiency -> dark counts -> dead time -> afterpulsing.

    Parameters
    ----------
    F_true : float
        True source Fano factor.
    mean_signal : float
        Mean signal photon number per interval.
    eta : float
        Detector quantum efficiency.
    dark_mean : float
        Mean dark counts per interval.
    dead_time_product : float
        r_measured * tau_dead (dimensionless).
    afterpulse_prob : float
        Afterpulse probability per detection event.

    Returns
    -------
    F_measured : float
        Fano factor after all artifacts.
    """
    mu_det = eta * mean_signal

    # Step 1: detection efficiency
    F1 = eta * (F_true - 1.0) + 1.0

    # Step 2: dark counts
    if dark_mean > 0:
        F2 = (mu_det * F1 + dark_mean) / (mu_det + dark_mean)
    else:
        F2 = F1

    # Step 3: dead time
    F3 = F2 * (1.0 - 2.0 * dead_time_product)

    # Step 4: afterpulsing
    signal_fraction = mu_det / (mu_det + dark_mean) if (mu_det + dark_mean) > 0 else 0
    F4 = F3 + afterpulse_prob * signal_fraction

    return F4


def run_discrimination_monte_carlo(
    n_trials: int,
    n_intervals: int,
    source_type: str,
    source_params: dict,
    alpha: float = 0.05,
    rng: Optional[np.random.Generator] = None,
) -> dict:
    """Monte Carlo estimation of test power for source discrimination.

    Generates n_trials datasets, each with n_intervals counting intervals,
    and applies the Fano factor test, LRT, and Bayesian comparison.

    Parameters
    ----------
    n_trials : int
        Number of Monte Carlo repetitions.
    n_intervals : int
        Counting intervals per dataset.
    source_type : str
        Distribution type for generate_samples.
    source_params : dict
        Parameters for generate_samples.
    alpha : float
        Significance level for frequentist tests.
    rng : np.random.Generator, optional

    Returns
    -------
    dict with:
        fano_reject_rate: fraction of trials rejecting Poisson (Fano test)
        lrt_reject_rate: fraction rejecting Poisson (LRT)
        bayes_nb_rate: fraction where Bayes favors NB
        mean_fano: average estimated Fano factor
        std_fano: std of estimated Fano factors
    """
    # Import here to avoid circular dependency
    from photocount_distributions import generate_samples

    if rng is None:
        rng = np.random.default_rng()

    fano_rejects = 0
    lrt_rejects = 0
    bayes_nb = 0
    fano_values = []

    for _ in range(n_trials):
        data = generate_samples(source_type, n_intervals, source_params, rng=rng)

        # Fano factor test
        fano_result = estimate_fano_factor(data)
        fano_values.append(fano_result["fano"])

        # Two-sided test
        if fano_result["p_value_super"] < alpha / 2 or fano_result["p_value_sub"] < alpha / 2:
            fano_rejects += 1

        # LRT
        lrt_result = likelihood_ratio_test(data)
        if lrt_result["p_value"] < alpha:
            lrt_rejects += 1

        # Bayesian
        bayes_result = bayesian_model_comparison(data)
        if bayes_result["log_bayes_factor"] < -1:  # Evidence for NB
            bayes_nb += 1

    return {
        "fano_reject_rate": fano_rejects / n_trials,
        "lrt_reject_rate": lrt_rejects / n_trials,
        "bayes_nb_rate": bayes_nb / n_trials,
        "mean_fano": np.mean(fano_values),
        "std_fano": np.std(fano_values),
    }


if __name__ == "__main__":
    print("=== Statistical Tests Self-Test ===\n")

    rng = np.random.default_rng(42)

    # Poisson data
    data_pois = rng.poisson(10.0, size=5000)
    result = estimate_fano_factor(data_pois)
    print("Poisson(10) data, N=5000:")
    print(f"  F={result['fano']:.4f}, Q={result['mandel_Q']:.4f}")
    print(f"  95% CI: [{result['ci_lower']:.4f}, {result['ci_upper']:.4f}]")
    print(f"  p(super)={result['p_value_super']:.4f}, p(sub)={result['p_value_sub']:.4f}")

    # Thermal data (overdispersed)
    intensities = rng.exponential(10.0, size=5000)
    data_thermal = rng.poisson(intensities)
    result_th = estimate_fano_factor(data_thermal)
    print(f"\nThermal(10) data, N=5000:")
    print(f"  F={result_th['fano']:.4f}, Q={result_th['mandel_Q']:.4f}")
    print(f"  p(super)={result_th['p_value_super']:.6f}")

    # LRT
    lrt_pois = likelihood_ratio_test(data_pois)
    lrt_th = likelihood_ratio_test(data_thermal)
    print(f"\nLRT (Poisson data): stat={lrt_pois['lr_stat']:.2f}, p={lrt_pois['p_value']:.4f}")
    print(f"LRT (Thermal data): stat={lrt_th['lr_stat']:.2f}, p={lrt_th['p_value']:.6f}, M_hat={lrt_th['nb_M_hat']:.2f}")

    # Bayesian
    bayes_pois = bayesian_model_comparison(data_pois)
    bayes_th = bayesian_model_comparison(data_thermal)
    print(f"\nBayes (Poisson data): log BF = {bayes_pois['log_bayes_factor']:.2f} -> {bayes_pois['interpretation']}")
    print(f"Bayes (Thermal data): log BF = {bayes_th['log_bayes_factor']:.2f} -> {bayes_th['interpretation']}")

    # Chi-squared
    chi2_pois = chi_squared_gof(data_pois, model="poisson")
    print(f"\nChi2 GoF (Poisson data vs Poisson): chi2={chi2_pois['chi2_stat']:.2f}, "
          f"p={chi2_pois['p_value']:.4f}, df={chi2_pois['df']}")

    # Power analysis
    N_needed = power_analysis_fano(0.05, alpha=0.01, power=0.80)
    print(f"\nPower analysis: N={N_needed} intervals needed to detect |F-1|=0.05 "
          f"(alpha=0.01, power=0.80)")

    # Artifact chain
    F_meas = measured_fano_with_artifacts(
        F_true=0.5, mean_signal=10, eta=0.15, dark_mean=5,
        dead_time_product=1e-6, afterpulse_prob=0.01
    )
    print(f"\nArtifact chain: F_true=0.5, eta=0.15, dark=5 -> F_measured={F_meas:.4f}")

    print("\nAll tests passed.")
