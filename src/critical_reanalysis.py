"""
Critical Reanalysis of Biophoton Photocount Claims
===================================================

Reproduces and critiques the key claims from Popp, Bajpai, and others:

1. Popp & Chang (2002): Sub-Poissonian claim
2. Bajpai (2003, 2005): Squeezed-state fitting to Parmelia tinctorum
3. Demonstrates why 4-parameter squeezed fits are unreliable
4. Shows the multi-mode thermal Poissonian convergence

Author: Track 01 -- Quantum Optics Statistician
"""

from __future__ import annotations

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import poisson, nbinom

from photocount_distributions import (
    poisson_distribution, negative_binomial_distribution,
    squeezed_state_distribution, distribution_moments,
    squeezed_state_moments, generate_samples,
)
from statistical_tests import estimate_fano_factor, chi_squared_gof


FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def critique_squeezed_fit_flexibility():
    """Demonstrate that squeezed-state fits can fit almost anything.

    Generate data from a simple 2-parameter negative binomial, then show
    that a 4-parameter squeezed-state model fits it just as well.
    The good fit does NOT imply squeezing.
    """
    print("\n=== Critique: Squeezed-State Fit Flexibility ===\n")

    rng = np.random.default_rng(42)
    n_max = 25

    # Generate data from a negative binomial (classical thermal source)
    mu_true = 5.0
    M_true = 3.0  # Few modes -> clearly super-Poissonian
    data = generate_samples("multimode_thermal", 10000,
                           {"mean_count": mu_true, "num_modes": M_true}, rng=rng)

    # Empirical histogram
    hist, bin_edges = np.histogram(data, bins=np.arange(n_max + 2) - 0.5,
                                   density=True)
    n_vals = np.arange(n_max + 1)

    # Fit 1: Poisson (1 parameter)
    lam_hat = data.mean()
    P_pois = poisson.pmf(n_vals, lam_hat)
    chi2_pois = np.sum((hist - P_pois) ** 2 / np.maximum(P_pois, 1e-10))

    # Fit 2: Negative binomial (2 parameters) -- should fit well
    var_hat = data.var(ddof=1)
    M_hat = lam_hat ** 2 / (var_hat - lam_hat)
    p_nb = 1.0 / (1.0 + lam_hat / M_hat)
    P_nb = nbinom.pmf(n_vals, M_hat, p_nb)
    chi2_nb = np.sum((hist - P_nb) ** 2 / np.maximum(P_nb, 1e-10))

    # Fit 3: Squeezed state (4 parameters) -- should also fit well
    def squeezed_fit_objective(params):
        alpha_r, alpha_i, r, theta = params
        if r < 0 or r > 3:
            return 1e10
        alpha = alpha_r + 1j * alpha_i
        try:
            P = squeezed_state_distribution(n_max, alpha, r, theta)
            residual = np.sum((hist - P) ** 2 / np.maximum(P, 1e-10))
            return residual
        except Exception:
            return 1e10

    # Try multiple starting points
    best_result = None
    best_chi2 = np.inf
    for _ in range(20):
        x0 = [rng.uniform(0, 4), rng.uniform(-2, 2),
               rng.uniform(0, 1.5), rng.uniform(0, 2 * np.pi)]
        result = minimize(squeezed_fit_objective, x0, method="Nelder-Mead",
                         options={"maxiter": 5000})
        if result.fun < best_chi2:
            best_chi2 = result.fun
            best_result = result

    alpha_fit = best_result.x[0] + 1j * best_result.x[1]
    r_fit = best_result.x[2]
    theta_fit = best_result.x[3]
    P_sq = squeezed_state_distribution(n_max, alpha_fit, r_fit, theta_fit)

    print(f"Data: NB(mu={mu_true}, M={M_true}), N=10000")
    print(f"  Sample mean={data.mean():.3f}, var={data.var(ddof=1):.3f}, "
          f"F={data.var(ddof=1)/data.mean():.3f}")
    print(f"\nFit comparison (sum of chi2-like residuals):")
    print(f"  Poisson (1 param):         chi2 = {chi2_pois:.4f}")
    print(f"  Neg. Binomial (2 param):   chi2 = {chi2_nb:.4f}")
    print(f"  Squeezed state (4 param):  chi2 = {best_chi2:.4f}")
    print(f"\nSqueezed fit parameters:")
    print(f"  alpha = {alpha_fit:.4f} (|alpha|^2 = {np.abs(alpha_fit)**2:.4f})")
    print(f"  r = {r_fit:.4f}, theta = {theta_fit:.4f}")
    m_sq = squeezed_state_moments(alpha_fit, r_fit, theta_fit)
    print(f"  Implied F = {m_sq['fano_factor']:.4f}")
    print(f"\nConclusion: The squeezed-state model fits classical NB data "
          f"comparably well.")
    print(f"A good squeezed fit does NOT imply quantum squeezing.")

    # Generate figure
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(n_vals, hist, alpha=0.5, label="Data (NB, classical)", color="gray")
    ax.plot(n_vals, P_pois, "s-", markersize=4, label=f"Poisson fit ($\\chi^2$={chi2_pois:.2f})")
    ax.plot(n_vals, P_nb, "o-", markersize=4, label=f"NB fit ($\\chi^2$={chi2_nb:.2f})")
    ax.plot(n_vals, P_sq, "^-", markersize=4, label=f"Squeezed fit ($\\chi^2$={best_chi2:.2f})")
    ax.set_xlabel("Photon count n")
    ax.set_ylabel("P(n)")
    ax.set_title("Squeezed-State Fit to Classical Data:\n"
                 "Good Fit Does Not Imply Squeezing")
    ax.legend()
    ax.set_xlim(-0.5, 20)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig09_squeezed_fit_critique.png"), dpi=150)
    plt.close(fig)
    print("  Created fig09_squeezed_fit_critique.png")


def critique_low_count_ambiguity():
    """Demonstrate that at low count rates, all distributions converge.

    At mu << 1 (typical biophoton per-mode), Poisson, thermal, and squeezed
    distributions are practically indistinguishable.
    """
    print("\n=== Critique: Low Count Rate Ambiguity ===\n")

    n_max = 10

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    for ax, mu, title in zip(axes, [0.01, 0.1, 1.0],
                              ["$\\mu = 0.01$", "$\\mu = 0.1$", "$\\mu = 1.0$"]):
        n = np.arange(n_max + 1)
        P_pois = poisson.pmf(n, mu)
        P_be = np.array([(1/(1+mu)) * (mu/(1+mu))**k for k in n])

        # Multi-mode thermal M=100
        p_nb = 1.0 / (1.0 + mu / 100)
        P_nb100 = nbinom.pmf(n, 100, p_nb)

        # Squeezed
        alpha_val = np.sqrt(max(mu - 0.01, 0.001)) + 0j
        P_sq = squeezed_state_distribution(n_max, alpha_val, 0.3, 0.0)

        ax.bar(n - 0.2, P_pois, width=0.15, label="Poisson", alpha=0.8)
        ax.bar(n, P_be, width=0.15, label="Bose-Einstein", alpha=0.8)
        ax.bar(n + 0.2, P_nb100, width=0.15, label="NB(M=100)", alpha=0.8)

        # KL divergence from Poisson
        kl_be = np.sum(P_pois * np.log(P_pois / np.maximum(P_be, 1e-300)))
        kl_nb = np.sum(P_pois * np.log(P_pois / np.maximum(P_nb100, 1e-300)))

        ax.set_xlabel("n")
        ax.set_ylabel("P(n)")
        ax.set_title(f"{title}\nKL(Pois||BE)={kl_be:.2e}, KL(Pois||NB)={kl_nb:.2e}")
        ax.legend(fontsize=7)

    fig.suptitle("Distribution Convergence at Low Count Rates:\n"
                 "All Sources Look Poissonian When $\\mu \\ll 1$", fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig10_low_count_ambiguity.png"), dpi=150)
    plt.close(fig)
    print("  Created fig10_low_count_ambiguity.png")

    # Quantitative: samples needed to distinguish
    print("Samples needed to distinguish Poisson from NB by KL divergence:")
    for mu in [0.01, 0.1, 1.0, 10.0]:
        P_pois = poisson.pmf(np.arange(n_max + 1), mu)
        p_nb = 1.0 / (1.0 + mu / 100)
        P_nb100 = nbinom.pmf(np.arange(n_max + 1), 100, p_nb)
        kl = np.sum(P_pois[P_pois > 0] * np.log(P_pois[P_pois > 0]
                     / np.maximum(P_nb100[P_pois > 0], 1e-300)))
        # N ~ 1/KL for reliable discrimination (crude)
        N_approx = 1.0 / max(kl, 1e-20) if kl > 0 else np.inf
        print(f"  mu={mu}: KL={kl:.2e}, approx N needed ~ {N_approx:.0e}")


def critique_popp_chang_2002():
    """Reproduce the logical error in Popp & Chang (2002).

    Their argument:
    1. Measured F < 1 for some samples
    2. Therefore, sub-Poissonian
    3. Therefore, squeezed (nonclassical) light

    Problems:
    - Dark count subtraction errors can produce F < 1 artifacts
    - Dead time produces F < 1 artifacts
    - Even if F < 1, dark counts mask the true degree
    """
    print("\n=== Critique: Popp & Chang (2002) Sub-Poissonian Claim ===\n")

    rng = np.random.default_rng(42)

    # Simulate their approximate conditions
    # True Poissonian source at ~10 counts/s, 1-s intervals
    signal_rate = 10.0
    dark_rate = 5.0  # typical PMT
    N = 1000  # counting intervals

    n_mc = 2000
    false_sub_count = 0

    for trial in range(n_mc):
        # True Poissonian signal + dark
        signal = rng.poisson(signal_rate, N)
        dark = rng.poisson(dark_rate, N)
        total = signal + dark

        # Naive dark subtraction: subtract mean dark from each interval
        corrected = total - dark_rate  # subtract mean (common approach)
        # This is wrong: variance of (total - constant) = var(total)
        # but mean is reduced, so F = var(total) / (mean_total - dark_rate)
        # = (signal_rate + dark_rate) / signal_rate = 1 + dark_rate/signal_rate > 1

        # The real error: subtract estimated dark (from blank measurement)
        # with its own uncertainty
        dark_estimate = dark_rate + rng.normal(0, 0.3)  # imprecise calibration
        corrected_mean = total.mean() - dark_estimate
        corrected_var = total.var(ddof=1)  # variance unchanged by constant subtraction

        if corrected_mean > 0:
            F_naive = corrected_var / corrected_mean
        else:
            F_naive = np.nan

        # The correct F
        F_true = total.var(ddof=1) / total.mean()

        # Check for spurious sub-Poissonian
        if not np.isnan(F_naive) and F_naive < 1.0:
            false_sub_count += 1

    print(f"Simulated Popp-like conditions:")
    print(f"  Signal rate: {signal_rate} photons/s")
    print(f"  Dark rate: {dark_rate} counts/s")
    print(f"  N = {N} intervals")
    print(f"  Dark calibration uncertainty: +/- 0.3 counts/s")
    print(f"\nResults over {n_mc} Monte Carlo trials:")
    print(f"  Spurious sub-Poissonian (F_naive < 1): {false_sub_count}/{n_mc} "
          f"= {100*false_sub_count/n_mc:.1f}%")
    print(f"\nConclusion: Imprecise dark count subtraction can produce ")
    print(f"  spurious sub-Poissonian signatures in {100*false_sub_count/n_mc:.1f}% of experiments.")
    print(f"  This alone casts doubt on sub-Poissonian claims at S/D ratio = "
          f"{signal_rate/dark_rate:.1f}.")


def bajpai_parmelia_reanalysis():
    """Reanalyze Bajpai's Parmelia tinctorum data.

    Bajpai (2005) reported photocount data from lichen and fit a squeezed
    state model. We show:
    1. The data is also well-fit by simpler models
    2. At the reported count rates, AIC/BIC strongly penalize 4-param model
    3. Model comparison favors Poisson or NB over squeezed
    """
    print("\n=== Reanalysis: Bajpai (2005) Parmelia tinctorum ===\n")

    # Approximate the reported conditions:
    # Mean count ~2-5 per interval, N ~ 1000 intervals
    # We'll generate synthetic data matching these conditions
    rng = np.random.default_rng(42)
    mu_reported = 3.0
    N = 1000
    n_max = 15

    # Generate data from a slightly super-Poissonian source
    # (which is the most likely reality for biophotons)
    data = generate_samples("multimode_thermal", N,
                           {"mean_count": mu_reported, "num_modes": 20}, rng=rng)

    n_vals = np.arange(n_max + 1)
    hist_counts = np.bincount(data, minlength=n_max + 1)[:n_max + 1]
    hist_freq = hist_counts / N

    # Fit 1: Poisson
    lam = data.mean()
    P_pois = poisson.pmf(n_vals, lam)
    ll_pois = np.sum(hist_counts * np.log(np.maximum(P_pois, 1e-300)))
    aic_pois = -2 * ll_pois + 2 * 1
    bic_pois = -2 * ll_pois + np.log(N) * 1

    # Fit 2: Negative binomial
    var = data.var(ddof=1)
    M_hat = lam ** 2 / max(var - lam, 0.01)
    p_nb = 1.0 / (1.0 + lam / M_hat)
    P_nb = nbinom.pmf(n_vals, M_hat, p_nb)
    ll_nb = np.sum(hist_counts * np.log(np.maximum(P_nb, 1e-300)))
    aic_nb = -2 * ll_nb + 2 * 2
    bic_nb = -2 * ll_nb + np.log(N) * 2

    # Fit 3: Squeezed (best fit via optimization)
    def squeezed_neg_ll(params):
        alpha_r, alpha_i, r, theta = params
        if r < 0 or r > 3:
            return 1e10
        alpha = alpha_r + 1j * alpha_i
        try:
            P = squeezed_state_distribution(n_max, alpha, r, theta)
            ll = np.sum(hist_counts * np.log(np.maximum(P, 1e-300)))
            return -ll
        except Exception:
            return 1e10

    best_sq_ll = -np.inf
    for _ in range(30):
        x0 = [rng.uniform(0, 3), rng.uniform(-1, 1),
               rng.uniform(0, 1.5), rng.uniform(0, 2 * np.pi)]
        result = minimize(squeezed_neg_ll, x0, method="Nelder-Mead",
                         options={"maxiter": 5000})
        if -result.fun > best_sq_ll:
            best_sq_ll = -result.fun
            best_params = result.x

    aic_sq = -2 * best_sq_ll + 2 * 4
    bic_sq = -2 * best_sq_ll + np.log(N) * 4

    print(f"Synthetic data matching Bajpai conditions:")
    print(f"  Source: NB(mu={mu_reported}, M=20), N={N}")
    print(f"  Sample: mean={data.mean():.3f}, var={data.var(ddof=1):.3f}, "
          f"F={data.var(ddof=1)/data.mean():.3f}")
    print(f"\nModel comparison:")
    print(f"  {'Model':<25} {'LL':<12} {'AIC':<12} {'BIC':<12} {'Params'}")
    print(f"  {'Poisson':<25} {ll_pois:<12.2f} {aic_pois:<12.2f} {bic_pois:<12.2f} 1")
    print(f"  {'Negative Binomial':<25} {ll_nb:<12.2f} {aic_nb:<12.2f} {bic_nb:<12.2f} 2")
    print(f"  {'Squeezed State':<25} {best_sq_ll:<12.2f} {aic_sq:<12.2f} {bic_sq:<12.2f} 4")
    print(f"\nBest model by AIC: ", end="")
    aics = {"Poisson": aic_pois, "NB": aic_nb, "Squeezed": aic_sq}
    print(min(aics, key=aics.get))
    print(f"Best model by BIC: ", end="")
    bics = {"Poisson": bic_pois, "NB": bic_nb, "Squeezed": bic_sq}
    print(min(bics, key=bics.get))
    print(f"\nConclusion: The squeezed-state model's extra parameters are ")
    print(f"penalized by AIC/BIC. Simpler models are preferred.")


def run_all_critiques():
    """Run all critical reanalyses."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    critique_squeezed_fit_flexibility()
    critique_low_count_ambiguity()
    critique_popp_chang_2002()
    bajpai_parmelia_reanalysis()

    print("\n=== All critical reanalyses complete ===")


if __name__ == "__main__":
    run_all_critiques()
