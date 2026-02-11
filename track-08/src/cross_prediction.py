"""
Cross-Prediction Model: Biophoton Emission vs MMI Hit Rates

Models the expected correlation between biophoton emission measures and
MMI/QFT device success rates (Responsivity), under the hypothesis that
both phenomena couple to the same Phi field.

Core predictions:
    1. Biophoton-Responsivity correlation (rho ~ 0.2-0.4)
    2. Spectral shift during high-coherence states
    3. EEG-Biophoton-MMI triple correlation
    4. Demyelination reduces MMI capability
    5. Remyelination restores MMI capability
    6. Waveguide-informed CCF design improves Responsivity

The model uses:
    - Shared Phi field as latent variable
    - Biophoton emission rate as noisy proxy for Lambda
    - Hit rate as noisy proxy for Responsivity (also Lambda-dependent)
    - Noise models for each measurement channel

References:
    M-Phi framework: Kruger, Feeney, Duarte (2023)
    Biophoton spectral data: Wang et al. (2016) PNAS
    Brain UPE: Casey et al. (2025) iScience
    EEG-biophoton correlation: Dotta et al. (2012)
"""

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass

from .constants import (
    BIOPHOTON_RATE_NEURAL,
    BIOPHOTON_WAVELENGTH_PEAK_NM,
    DETECTOR_DARK_RATE_PMT_HZ,
    DETECTOR_QE_PMT,
    RESPONSIVITY_BASELINE,
    RESPONSIVITY_TYPICAL,
    LAMBDA_CRITICAL,
    LAMBDA_SS_HEALTHY,
    DEFAULT_N_TRIALS,
    RNG_SEED,
)
from .phi_field_coupling import (
    PhiFieldParameters,
    responsivity_from_coherence,
    demyelination_impact,
)


@dataclass
class CrossPredictionParams:
    """Parameters for cross-prediction modeling."""

    # Biophoton measurement noise
    biophoton_noise_sigma: float = 15.0  # photons/s/cm^2 (dark counts + shot noise)
    biophoton_sensitivity: float = 1.0    # scaling from Lambda to photon rate

    # MMI measurement noise
    mmi_noise_sigma: float = 0.02  # noise in observed success rate per trial block
    mmi_n_trials_per_block: int = 100  # trials per measurement block

    # Shared Phi field
    phi_mean: float = 1.0
    phi_std: float = 0.2  # fluctuations in ambient Phi

    # Correlation structure
    biophoton_lambda_sensitivity: float = 50.0  # photons/s/cm^2 per unit Lambda
    mmi_lambda_sensitivity: float = 0.02  # SR excess per unit Lambda above baseline


def simulate_shared_phi_field(
    n_timepoints: int = 1000,
    dt: float = 1.0,
    phi_mean: float = 1.0,
    phi_std: float = 0.2,
    correlation_time: float = 30.0,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Simulate a shared Phi field as an Ornstein-Uhlenbeck process.

    Phi(t+dt) = Phi(t) + theta*(mu - Phi(t))*dt + sigma*sqrt(dt)*dW

    where theta = 1/correlation_time, mu = phi_mean, and sigma is chosen
    so that the stationary distribution has std = phi_std.

    Parameters
    ----------
    n_timepoints : int
        Number of time steps.
    dt : float
        Time step (seconds).
    phi_mean : float
        Mean of the Phi field.
    phi_std : float
        Standard deviation of Phi fluctuations.
    correlation_time : float
        Autocorrelation time of the OU process (seconds).
    rng : np.random.Generator, optional
        Random number generator.

    Returns
    -------
    np.ndarray
        Phi(t) time series.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    theta = 1.0 / correlation_time
    # Stationary variance of OU: sigma^2 / (2*theta) = phi_std^2
    sigma_ou = phi_std * np.sqrt(2.0 * theta)

    phi = np.zeros(n_timepoints)
    phi[0] = rng.normal(phi_mean, phi_std)

    for i in range(1, n_timepoints):
        dphi = theta * (phi_mean - phi[i - 1]) * dt + sigma_ou * np.sqrt(dt) * rng.standard_normal()
        phi[i] = phi[i - 1] + dphi

    return phi


def biophoton_observable(
    phi_field: np.ndarray,
    params: CrossPredictionParams,
    coupling_params: Optional[PhiFieldParameters] = None,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Generate observable biophoton rate from the shared Phi field.

    Maps Phi -> Lambda (via coherence equation steady-state) ->
    biophoton rate (linear mapping + Poisson noise).

    Parameters
    ----------
    phi_field : np.ndarray
        Shared Phi field time series.
    params : CrossPredictionParams
        Cross-prediction parameters.
    coupling_params : PhiFieldParameters, optional
        Coupling parameters for Lambda computation.
    rng : np.random.Generator, optional
        Random number generator.

    Returns
    -------
    np.ndarray
        Observed biophoton rate (photons/s/cm^2).
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED + 1)
    if coupling_params is None:
        coupling_params = PhiFieldParameters()

    # Lambda_ss = (g/kappa) * |Psi|^2 * Phi(t)
    lambda_values = (
        coupling_params.g_phi_psi
        / coupling_params.kappa
        * coupling_params.psi_squared
        * phi_field
    )

    # True biophoton rate = baseline + sensitivity * Lambda
    true_rate = BIOPHOTON_RATE_NEURAL + params.biophoton_lambda_sensitivity * lambda_values

    # Add measurement noise (Poisson + dark counts)
    # For each time point, observed = Poisson(true_rate * QE) + dark_counts
    observed = np.zeros_like(true_rate)
    for i, rate in enumerate(true_rate):
        detected = rng.poisson(max(rate * DETECTOR_QE_PMT, 0.0))
        dark = rng.poisson(DETECTOR_DARK_RATE_PMT_HZ)
        observed[i] = detected + dark

    return observed


def mmi_observable(
    phi_field: np.ndarray,
    params: CrossPredictionParams,
    coupling_params: Optional[PhiFieldParameters] = None,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Generate observable MMI hit rate from the shared Phi field.

    Maps Phi -> Lambda -> Responsivity (via sigmoid) + binomial noise.

    Parameters
    ----------
    phi_field : np.ndarray
        Shared Phi field time series.
    params : CrossPredictionParams
        Cross-prediction parameters.
    coupling_params : PhiFieldParameters, optional
        Coupling parameters.
    rng : np.random.Generator, optional
        Random number generator.

    Returns
    -------
    np.ndarray
        Observed success rate per time block.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED + 2)
    if coupling_params is None:
        coupling_params = PhiFieldParameters()

    lambda_values = (
        coupling_params.g_phi_psi
        / coupling_params.kappa
        * coupling_params.psi_squared
        * phi_field
    )

    observed_sr = np.zeros_like(lambda_values)
    for i, lam in enumerate(lambda_values):
        true_sr = responsivity_from_coherence(lam)
        # Binomial sampling: n_trials attempts at probability true_sr
        hits = rng.binomial(params.mmi_n_trials_per_block, true_sr)
        observed_sr[i] = hits / params.mmi_n_trials_per_block

    return observed_sr


def predict_correlation(
    n_timepoints: int = 500,
    params: Optional[CrossPredictionParams] = None,
    coupling_params: Optional[PhiFieldParameters] = None,
    rng: Optional[np.random.Generator] = None,
) -> Dict:
    """Predict the biophoton-MMI correlation from the shared Phi field model.

    Generates synthetic data from the shared-field model and computes
    the Pearson correlation between biophoton rate and MMI success rate.

    Parameters
    ----------
    n_timepoints : int
        Number of measurement blocks.
    params : CrossPredictionParams, optional
        Model parameters.
    coupling_params : PhiFieldParameters, optional
        Phi-field coupling parameters.
    rng : np.random.Generator, optional
        Random number generator.

    Returns
    -------
    dict
        Keys: "phi_field", "biophoton_rate", "mmi_sr",
        "pearson_r", "pearson_p", "spearman_r", "spearman_p",
        "predicted_correlation_range".
    """
    if params is None:
        params = CrossPredictionParams()
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)
    if coupling_params is None:
        coupling_params = PhiFieldParameters()

    phi = simulate_shared_phi_field(n_timepoints, rng=rng, phi_mean=params.phi_mean, phi_std=params.phi_std)
    bio = biophoton_observable(phi, params, coupling_params, np.random.default_rng(rng.integers(2**31)))
    mmi = mmi_observable(phi, params, coupling_params, np.random.default_rng(rng.integers(2**31)))

    r_pearson, p_pearson = stats.pearsonr(bio, mmi)
    r_spearman, p_spearman = stats.spearmanr(bio, mmi)

    return {
        "phi_field": phi,
        "biophoton_rate": bio,
        "mmi_sr": mmi,
        "pearson_r": r_pearson,
        "pearson_p": p_pearson,
        "spearman_r": r_spearman,
        "spearman_p": p_spearman,
        "n_timepoints": n_timepoints,
    }


def monte_carlo_correlation_distribution(
    n_simulations: int = 1000,
    n_timepoints: int = 200,
    params: Optional[CrossPredictionParams] = None,
    coupling_params: Optional[PhiFieldParameters] = None,
) -> Dict:
    """Monte Carlo estimate of the correlation distribution.

    Runs many simulations to estimate the distribution of observable
    correlations between biophoton rate and MMI success rate.

    Parameters
    ----------
    n_simulations : int
        Number of Monte Carlo simulations.
    n_timepoints : int
        Timepoints per simulation.
    params : CrossPredictionParams, optional
        Model parameters.
    coupling_params : PhiFieldParameters, optional
        Coupling parameters.

    Returns
    -------
    dict
        Keys: "correlations" (array), "mean_r", "std_r",
        "ci_95" (tuple), "fraction_significant".
    """
    if params is None:
        params = CrossPredictionParams()
    if coupling_params is None:
        coupling_params = PhiFieldParameters()

    correlations = np.zeros(n_simulations)

    for i in range(n_simulations):
        rng = np.random.default_rng(RNG_SEED + i * 100)
        result = predict_correlation(n_timepoints, params, coupling_params, rng)
        correlations[i] = result["pearson_r"]

    mean_r = np.mean(correlations)
    std_r = np.std(correlations)
    ci_lo, ci_hi = np.percentile(correlations, [2.5, 97.5])

    # Fraction of simulations with significant correlation (p < 0.05)
    significant = 0
    for i in range(n_simulations):
        rng = np.random.default_rng(RNG_SEED + i * 100)
        result = predict_correlation(n_timepoints, params, coupling_params, rng)
        if result["pearson_p"] < 0.05:
            significant += 1

    return {
        "correlations": correlations,
        "mean_r": mean_r,
        "std_r": std_r,
        "ci_95": (ci_lo, ci_hi),
        "fraction_significant": significant / n_simulations,
        "n_simulations": n_simulations,
    }


def demyelination_mmi_prediction(
    damage_fractions: np.ndarray = np.linspace(0.0, 1.0, 50),
    params_healthy: Optional[PhiFieldParameters] = None,
) -> Dict:
    """Predict how demyelination affects MMI performance.

    For each damage fraction, computes the steady-state coherence and
    maps it to expected Responsivity.

    Parameters
    ----------
    damage_fractions : np.ndarray
        Array of damage fractions to evaluate.
    params_healthy : PhiFieldParameters, optional
        Healthy tissue parameters.

    Returns
    -------
    dict
        Keys: "damage_fractions", "lambda_ss", "responsivity",
        "critical_damage" (where Lambda drops below threshold).
    """
    if params_healthy is None:
        params_healthy = PhiFieldParameters()

    lambda_values = np.zeros_like(damage_fractions)
    sr_values = np.zeros_like(damage_fractions)

    for i, d in enumerate(damage_fractions):
        result = demyelination_impact(d, params_healthy)
        lambda_values[i] = result["lambda_ss_damaged"]
        sr_values[i] = responsivity_from_coherence(lambda_values[i])

    # Find critical damage fraction
    critical_idx = np.argmax(lambda_values < LAMBDA_CRITICAL)
    if lambda_values[critical_idx] >= LAMBDA_CRITICAL and critical_idx == 0:
        critical_damage = float("nan")
    else:
        critical_damage = damage_fractions[critical_idx]

    return {
        "damage_fractions": damage_fractions,
        "lambda_ss": lambda_values,
        "responsivity": sr_values,
        "critical_damage": critical_damage,
        "lambda_healthy": params_healthy.lambda_ss,
        "sr_healthy": responsivity_from_coherence(params_healthy.lambda_ss),
    }


def spectral_shift_prediction(
    lambda_values: np.ndarray,
    base_wavelength_nm: float = BIOPHOTON_WAVELENGTH_PEAK_NM,
    shift_coefficient: float = -20.0,
) -> np.ndarray:
    """Predict biophoton spectral peak shift as function of coherence.

    Higher coherence -> redshift (Wang et al. 2016 PNAS).

    Lambda_peak(Lambda) = base + shift_coefficient * (Lambda / Lambda_ref - 1)

    Parameters
    ----------
    lambda_values : np.ndarray
        Coherence values.
    base_wavelength_nm : float
        Baseline peak wavelength.
    shift_coefficient : float
        nm shift per unit coherence deviation (negative = redshift for
        increased coherence).

    Returns
    -------
    np.ndarray
        Predicted peak wavelengths (nm).
    """
    ref = LAMBDA_SS_HEALTHY
    shift = shift_coefficient * (lambda_values / ref - 1.0)
    return base_wavelength_nm - shift  # redshift = increase in wavelength


def triple_correlation_model(
    n_timepoints: int = 500,
    eeg_plv_noise: float = 0.1,
    rng: Optional[np.random.Generator] = None,
) -> Dict:
    """Simulate the EEG-Biophoton-MMI triple correlation.

    Prediction 3 from Track 08: corr[C_gamma(t), PLV(t), SR(t)] >> 0

    All three observables (biophoton coherence, EEG phase-locking value,
    and MMI success rate) share a common latent variable (Phi field).

    Parameters
    ----------
    n_timepoints : int
        Number of measurement time points.
    eeg_plv_noise : float
        Noise level in EEG phase-locking value measurement.
    rng : np.random.Generator, optional
        Random number generator.

    Returns
    -------
    dict
        Keys: "phi_field", "biophoton_coherence", "eeg_plv",
        "mmi_sr", "correlation_matrix", "partial_correlations".
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    params = CrossPredictionParams()
    coupling = PhiFieldParameters()

    phi = simulate_shared_phi_field(n_timepoints, rng=rng)

    # Biophoton coherence (Lambda proxy)
    lambda_values = (coupling.g_phi_psi / coupling.kappa) * coupling.psi_squared * phi
    bio_coherence = lambda_values + rng.normal(0, 0.1 * np.std(lambda_values), n_timepoints)

    # EEG PLV -- linearly related to Lambda with noise
    eeg_plv_true = 0.3 + 0.2 * (lambda_values / LAMBDA_SS_HEALTHY)
    eeg_plv = np.clip(
        eeg_plv_true + rng.normal(0, eeg_plv_noise, n_timepoints),
        0.0, 1.0
    )

    # MMI success rate
    mmi_sr = mmi_observable(phi, params, coupling, np.random.default_rng(rng.integers(2**31)))

    # Correlation matrix
    data = np.column_stack([bio_coherence, eeg_plv, mmi_sr])
    corr_matrix = np.corrcoef(data.T)

    # Partial correlations (controlling for Phi)
    # r_AB.C = (r_AB - r_AC * r_BC) / sqrt((1 - r_AC^2)(1 - r_BC^2))
    r_bio_eeg = corr_matrix[0, 1]
    r_bio_mmi = corr_matrix[0, 2]
    r_eeg_mmi = corr_matrix[1, 2]

    def partial_corr(r_xy, r_xz, r_yz):
        num = r_xy - r_xz * r_yz
        den = np.sqrt((1 - r_xz**2) * (1 - r_yz**2))
        return num / den if den > 0 else 0.0

    partial_bio_eeg = partial_corr(r_bio_eeg, r_bio_mmi, r_eeg_mmi)
    partial_bio_mmi = partial_corr(r_bio_mmi, r_bio_eeg, r_eeg_mmi)
    partial_eeg_mmi = partial_corr(r_eeg_mmi, r_bio_eeg, r_bio_mmi)

    return {
        "phi_field": phi,
        "biophoton_coherence": bio_coherence,
        "eeg_plv": eeg_plv,
        "mmi_sr": mmi_sr,
        "correlation_matrix": corr_matrix,
        "labels": ["Biophoton Coherence", "EEG PLV", "MMI Success Rate"],
        "partial_correlations": {
            "bio_eeg|mmi": partial_bio_eeg,
            "bio_mmi|eeg": partial_bio_mmi,
            "eeg_mmi|bio": partial_eeg_mmi,
        },
    }


def required_sample_size(
    target_r: float = 0.25,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Compute required sample size to detect a given correlation.

    Uses the Fisher z-transform approach:
        n = ((z_alpha + z_beta) / arctanh(r))^2 + 3

    Parameters
    ----------
    target_r : float
        Expected Pearson correlation to detect.
    alpha : float
        Significance level.
    power : float
        Statistical power.

    Returns
    -------
    int
        Required sample size.
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    fisher_z = np.arctanh(target_r)
    n = ((z_alpha + z_beta) / fisher_z) ** 2 + 3
    return int(np.ceil(n))


# --- Standalone execution ---
if __name__ == "__main__":
    print("=== Cross-Prediction Model Demo ===\n")

    # 1. Single-run correlation prediction
    print("--- Single Simulation ---")
    result = predict_correlation(n_timepoints=500)
    print(f"  Pearson r  = {result['pearson_r']:.4f} (p = {result['pearson_p']:.4e})")
    print(f"  Spearman r = {result['spearman_r']:.4f} (p = {result['spearman_p']:.4e})")

    # 2. Demyelination prediction
    print("\n--- Demyelination -> MMI Prediction ---")
    demyel = demyelination_mmi_prediction()
    print(f"  Healthy Lambda_ss = {demyel['lambda_healthy']:.4f}")
    print(f"  Healthy SR        = {demyel['sr_healthy']:.4f}")
    print(f"  Critical damage   = {demyel['critical_damage']:.2%}")

    # 3. Required sample size
    for r in [0.15, 0.20, 0.25, 0.30]:
        n = required_sample_size(target_r=r)
        print(f"  To detect r={r:.2f}: need n={n} blocks")

    # 4. Triple correlation
    print("\n--- Triple Correlation (EEG-Bio-MMI) ---")
    triple = triple_correlation_model()
    print("  Correlation matrix:")
    for i, label in enumerate(triple["labels"]):
        row = "    " + label.ljust(25) + " ".join(
            f"{triple['correlation_matrix'][i, j]:+.3f}" for j in range(3)
        )
        print(row)
    print("  Partial correlations:")
    for key, val in triple["partial_correlations"].items():
        print(f"    {key}: {val:+.3f}")

    # 5. Spectral shift
    print("\n--- Spectral Shift Prediction ---")
    lam_vals = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    wavelengths = spectral_shift_prediction(lam_vals)
    for l, w in zip(lam_vals, wavelengths):
        print(f"  Lambda={l:.1f}: peak={w:.1f} nm")
