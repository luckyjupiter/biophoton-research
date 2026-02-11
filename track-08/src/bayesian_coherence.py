"""
Bayesian Updating Framework for Biophoton Coherence Estimation

Implements the same Bayesian updating (BU) algorithm used in QTrainerAI,
adapted for biophoton coherence state classification. The core insight:
QTrainerAI uses BU to estimate whether a QRNG stream carries intentional
bias; here we use BU to estimate whether a biophoton stream carries
coherence signatures.

Framework:
    - Prior: P(high-coherence state) -- starts at INITIAL_PRIOR = 0.51
    - Likelihood: success rate SR = 0.515 (probability of observation
      given high-coherence)
    - Observation: +1 (consistent with coherence) or 0 (not)
    - Posterior: updated via Bayes' theorem

The Combined BU aggregates evidence from multiple independent observables
(analogous to QTrainerAI's 17 methods), where each observable provides
an independent stream of coherence/incoherence observations.

References:
    Kruger, Feeney, Duarte (2023) - M-Phi framework
    QTrainerAI BU implementation - Scott's directives Jan-Feb 2026
"""

import numpy as np
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass, field

from .constants import (
    INITIAL_PRIOR,
    LIKELIHOOD_SR,
    BU_OBS_HIT,
    BU_OBS_MISS,
    N_METHODS,
    QTRAINER_METHODS,
    LAMBDA_CRITICAL,
    AS_CDF_C1,
    AS_CDF_C7,
    AS_CDF_C8,
    AS_CDF_C9,
    AS_CDF_C10,
    AS_CDF_C11,
    AS_CDF_C12,
)


def scott_cdf_z_score(z: float) -> float:
    """Standard normal CDF using Abramowitz-Stegun approximation.

    This is the same CDF function used in QTrainerAI for subtrial-level
    z-to-p conversion. Coefficients match the Rust implementation in
    stats/cdf.rs.

    Parameters
    ----------
    z : float
        Standard normal z-score.

    Returns
    -------
    float
        Cumulative probability P(Z <= z).
    """
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0

    L = abs(z)
    k = 1.0 / (1.0 + AS_CDF_C7 * L)
    k2 = k * k
    k3 = k2 * k
    k4 = k3 * k
    k5 = k4 * k

    w = (
        AS_CDF_C8 * k
        + AS_CDF_C9 * k2
        + AS_CDF_C10 * k3
        + AS_CDF_C11 * k4
        + AS_CDF_C12 * k5
    )
    w = 1.0 - w * np.exp(-L * L / 2.0) / AS_CDF_C1

    if z < 0.0:
        return 1.0 - w
    return w


def bayesian_update_single(
    prior: float,
    observation: int,
    sr: float = LIKELIHOOD_SR,
) -> float:
    """Single Bayesian update step.

    Implements the exact BU formula from QTrainerAI:
        obs=1: posterior = (SR * prior) / (SR * prior + (1-SR) * (1-prior))
        obs=0: posterior = ((1-SR) * prior) / ((1-SR) * prior + SR * (1-prior))

    Parameters
    ----------
    prior : float
        Current prior probability P(high-coherence).
    observation : int
        1 for coherence-consistent observation, 0 for not.
    sr : float
        Success rate (likelihood parameter). Default 0.515.

    Returns
    -------
    float
        Updated posterior probability.
    """
    if observation == BU_OBS_HIT:
        numerator = sr * prior
        denominator = sr * prior + (1.0 - sr) * (1.0 - prior)
    else:
        numerator = (1.0 - sr) * prior
        denominator = (1.0 - sr) * prior + sr * (1.0 - prior)

    if denominator == 0.0:
        return prior
    return numerator / denominator


def bayesian_update_sequence(
    observations: np.ndarray,
    prior: float = INITIAL_PRIOR,
    sr: float = LIKELIHOOD_SR,
) -> Tuple[np.ndarray, float]:
    """Apply BU over a sequence of observations.

    Parameters
    ----------
    observations : np.ndarray
        Array of 0/1 observations.
    prior : float
        Initial prior. Default 0.51.
    sr : float
        Success rate. Default 0.515.

    Returns
    -------
    posteriors : np.ndarray
        Posterior after each observation (same length as observations).
    final_posterior : float
        Final posterior value.
    """
    n = len(observations)
    posteriors = np.empty(n, dtype=np.float64)
    current = prior

    for i in range(n):
        current = bayesian_update_single(current, int(observations[i]), sr)
        posteriors[i] = current

    return posteriors, current


@dataclass
class MethodBUState:
    """State of a single method's Bayesian updating process."""

    name: str
    prior: float = INITIAL_PRIOR
    posterior: float = INITIAL_PRIOR
    n_observations: int = 0
    n_hits: int = 0
    hit_rate: float = 0.0
    posteriors_history: List[float] = field(default_factory=list)

    def update(self, observation: int, sr: float = LIKELIHOOD_SR) -> float:
        """Update this method's BU state with a new observation.

        Parameters
        ----------
        observation : int
            1 for hit, 0 for miss.
        sr : float
            Success rate parameter.

        Returns
        -------
        float
            New posterior.
        """
        self.prior = self.posterior
        self.posterior = bayesian_update_single(self.prior, observation, sr)
        self.n_observations += 1
        if observation == BU_OBS_HIT:
            self.n_hits += 1
        self.hit_rate = self.n_hits / self.n_observations
        self.posteriors_history.append(self.posterior)
        return self.posterior


@dataclass
class CombinedBUState:
    """Combined Bayesian Updating across multiple methods.

    In QTrainerAI, 17 methods each provide independent observations that
    are combined into a single coherence estimate. The Combined BU uses
    method outcomes (not raw observations) -- "state is observation,
    Posterior becomes Prior" (Scott, Jan 28 2026).

    In the biophoton context, each method corresponds to a different
    observable computed from the photon stream (e.g., Mandel Q, Fano
    factor, autocorrelation, KS statistic, etc.).
    """

    methods: Dict[str, MethodBUState] = field(default_factory=dict)
    combined_prior: float = INITIAL_PRIOR
    combined_posterior: float = INITIAL_PRIOR
    combined_history: List[float] = field(default_factory=list)
    trial_count: int = 0

    def __post_init__(self):
        if not self.methods:
            for name in QTRAINER_METHODS:
                self.methods[name] = MethodBUState(name=name)

    def update_method(
        self,
        method_name: str,
        observation: int,
        sr: float = LIKELIHOOD_SR,
    ) -> float:
        """Update a single method with an observation.

        Parameters
        ----------
        method_name : str
            Which method (must be in QTRAINER_METHODS).
        observation : int
            1 for hit, 0 for miss.
        sr : float
            Success rate.

        Returns
        -------
        float
            Method's new posterior.
        """
        if method_name not in self.methods:
            raise ValueError(
                f"Unknown method '{method_name}'. "
                f"Valid: {list(self.methods.keys())}"
            )
        return self.methods[method_name].update(observation, sr)

    def compute_combined_posterior(self, sr: float = LIKELIHOOD_SR) -> float:
        """Compute combined BU from all method posteriors.

        The combined BU treats each method's outcome as an observation
        in a higher-level Bayesian update. A method's outcome is a "hit"
        if its posterior > 0.5 (evidence for coherence), "miss" otherwise.

        This follows Scott's directive: "state is observation, Posterior
        becomes Prior" -- we use method outcomes, NOT raw observation pooling.

        Parameters
        ----------
        sr : float
            Success rate for the combined update.

        Returns
        -------
        float
            Combined posterior.
        """
        self.combined_prior = self.combined_posterior

        for method in self.methods.values():
            if method.n_observations > 0:
                method_outcome = (
                    BU_OBS_HIT if method.posterior > 0.5 else BU_OBS_MISS
                )
                self.combined_posterior = bayesian_update_single(
                    self.combined_posterior, method_outcome, sr
                )

        self.combined_history.append(self.combined_posterior)
        self.trial_count += 1
        return self.combined_posterior

    def coherence_state(self) -> str:
        """Classify current coherence state based on combined posterior.

        Returns
        -------
        str
            "high_coherence", "indeterminate", or "low_coherence".
        """
        if self.combined_posterior > 0.6:
            return "high_coherence"
        elif self.combined_posterior < 0.4:
            return "low_coherence"
        else:
            return "indeterminate"

    def z_score(self) -> float:
        """Convert combined posterior to a z-score.

        Returns
        -------
        float
            z-score corresponding to the combined posterior.
        """
        p = np.clip(self.combined_posterior, 1e-10, 1.0 - 1e-10)
        return _inverse_normal_cdf(p)

    def summary(self) -> Dict:
        """Return summary statistics of the combined BU state."""
        active_methods = {
            name: m for name, m in self.methods.items() if m.n_observations > 0
        }
        return {
            "combined_posterior": self.combined_posterior,
            "combined_z_score": self.z_score(),
            "coherence_state": self.coherence_state(),
            "trial_count": self.trial_count,
            "active_methods": len(active_methods),
            "method_posteriors": {
                name: m.posterior for name, m in active_methods.items()
            },
            "method_hit_rates": {
                name: m.hit_rate for name, m in active_methods.items()
            },
        }


def _inverse_normal_cdf(p: float) -> float:
    """Approximate inverse of standard normal CDF (probit function).

    Uses the rational approximation from Abramowitz and Stegun (26.2.23).

    Parameters
    ----------
    p : float
        Probability in (0, 1).

    Returns
    -------
    float
        z-score such that Phi(z) approximately equals p.
    """
    if p <= 0.0:
        return -8.0
    if p >= 1.0:
        return 8.0

    if p < 0.5:
        sign = -1.0
        p_work = p
    else:
        sign = 1.0
        p_work = 1.0 - p

    t = np.sqrt(-2.0 * np.log(p_work))

    c0 = 2.515517
    c1 = 0.802853
    c2 = 0.010328
    d1 = 1.432788
    d2 = 0.189269
    d3 = 0.001308

    z = t - (c0 + c1 * t + c2 * t * t) / (
        1.0 + d1 * t + d2 * t * t + d3 * t * t * t
    )

    return sign * z


class BiophotonCoherenceEstimator:
    """Bayesian coherence estimator for biophoton photon-count streams.

    Translates raw photon count data into coherence observations suitable
    for Bayesian updating. The key mapping:

    Photon counts --> statistical tests --> hit/miss observations --> BU

    Each statistical test produces an observation:
        - Hit (+1): statistic consistent with coherent/non-thermal emission
        - Miss (0): statistic consistent with thermal/random emission

    The statistical tests mirror the QTrainerAI 17-method suite, adapted
    for photon counting data rather than binary QRNG streams.
    """

    def __init__(
        self,
        prior: float = INITIAL_PRIOR,
        sr: float = LIKELIHOOD_SR,
        window_size: int = 100,
    ):
        """Initialize the biophoton coherence estimator.

        Parameters
        ----------
        prior : float
            Initial prior for P(coherent).
        sr : float
            Success rate parameter for BU.
        window_size : int
            Number of photon counts per analysis window.
        """
        self.sr = sr
        self.window_size = window_size
        self.bu_state = CombinedBUState()
        self.bu_state.combined_prior = prior
        self.bu_state.combined_posterior = prior
        self._count_buffer: List[int] = []

    def ingest_counts(self, counts: np.ndarray) -> Optional[Dict]:
        """Ingest a batch of photon counts.

        Counts are buffered until window_size is reached, then analyzed.

        Parameters
        ----------
        counts : np.ndarray
            Array of integer photon counts (one per time bin).

        Returns
        -------
        dict or None
            Analysis results if a complete window was processed, else None.
        """
        self._count_buffer.extend(counts.tolist())

        if len(self._count_buffer) >= self.window_size:
            window = np.array(self._count_buffer[: self.window_size])
            self._count_buffer = self._count_buffer[self.window_size :]
            return self._analyze_window(window)

        return None

    def _analyze_window(self, counts: np.ndarray) -> Dict:
        """Analyze a complete window of photon counts.

        Applies multiple statistical tests and feeds results into the
        combined BU framework.

        Parameters
        ----------
        counts : np.ndarray
            Array of photon counts (length = window_size).

        Returns
        -------
        dict
            Analysis results including per-method observations and
            combined posterior.
        """
        observations = {}

        # 1. Mandel Q test (mv analogue) -- sub-Poissonian = coherence hit
        mean_n = np.mean(counts)
        var_n = np.var(counts, ddof=1) if len(counts) > 1 else mean_n
        if mean_n > 0:
            Q = (var_n - mean_n) / mean_n
        else:
            Q = 0.0
        obs_mv = BU_OBS_HIT if Q < 0 else BU_OBS_MISS
        observations["mv"] = obs_mv
        self.bu_state.update_method("mv", obs_mv, self.sr)

        # 2. RWBA analogue -- cumulative sum deviation from expected
        expected = mean_n
        cumsum = np.cumsum(counts - expected)
        max_dev = np.max(np.abs(cumsum))
        threshold = 2.0 * np.sqrt(mean_n * len(counts))
        obs_rwba = BU_OBS_HIT if max_dev > threshold else BU_OBS_MISS
        observations["rwba"] = obs_rwba
        self.bu_state.update_method("rwba", obs_rwba, self.sr)

        # 3-4. Autocorrelation lag-1 and lag-2
        for lag, method in [(1, "ac1"), (2, "ac2")]:
            if len(counts) > lag:
                ac = _autocorrelation(counts, lag)
                obs = BU_OBS_HIT if ac > 2.0 / np.sqrt(len(counts)) else BU_OBS_MISS
            else:
                obs = BU_OBS_MISS
            observations[method] = obs
            self.bu_state.update_method(method, obs, self.sr)

        # 5-9. Running averages at different windows (ra1-ra5)
        for i, (w, method) in enumerate(
            [(3, "ra1"), (5, "ra2"), (10, "ra3"), (20, "ra4"), (50, "ra5")]
        ):
            if len(counts) >= w:
                running_avg = np.convolve(
                    counts, np.ones(w) / w, mode="valid"
                )
                diffs = np.diff(running_avg)
                frac_positive = np.mean(diffs > 0) if len(diffs) > 0 else 0.5
                obs = BU_OBS_HIT if frac_positive > 0.55 else BU_OBS_MISS
            else:
                obs = BU_OBS_MISS
            observations[method] = obs
            self.bu_state.update_method(method, obs, self.sr)

        # 10-12. Cumulative advantage at windows 7, 15, 23
        for w, method in [(7, "ca7"), (15, "ca15"), (23, "ca23")]:
            if len(counts) >= w:
                windows = [
                    counts[j : j + w] for j in range(0, len(counts) - w + 1, w)
                ]
                if len(windows) >= 2:
                    means = [np.mean(win) for win in windows]
                    trend = np.polyfit(range(len(means)), means, 1)[0]
                    obs = BU_OBS_HIT if trend > 0 else BU_OBS_MISS
                else:
                    obs = BU_OBS_MISS
            else:
                obs = BU_OBS_MISS
            observations[method] = obs
            self.bu_state.update_method(method, obs, self.sr)

        # 13. LZT analogue -- Lempel-Ziv complexity
        binary = (counts > np.median(counts)).astype(int)
        lz_complexity = _lempel_ziv_complexity(binary)
        expected_lz = len(counts) / np.log2(len(counts)) if len(counts) > 1 else 1
        obs_lzt = BU_OBS_HIT if lz_complexity < 0.9 * expected_lz else BU_OBS_MISS
        observations["lzt"] = obs_lzt
        self.bu_state.update_method("lzt", obs_lzt, self.sr)

        # 14. KS test -- compare distribution to Poisson
        from scipy import stats as sp_stats

        if mean_n > 0:
            ks_stat, ks_p = sp_stats.kstest(
                counts, lambda x: sp_stats.poisson.cdf(x, mean_n)
            )
            obs_ks = BU_OBS_HIT if ks_p < 0.05 else BU_OBS_MISS
        else:
            obs_ks = BU_OBS_MISS
            ks_stat, ks_p = 0.0, 1.0
        observations["ks"] = obs_ks
        self.bu_state.update_method("ks", obs_ks, self.sr)

        # 15-17. Higher-order methods (m2, m3, m4)
        # m2: Fano factor test
        fano = var_n / mean_n if mean_n > 0 else 1.0
        obs_m2 = BU_OBS_HIT if fano < 0.95 else BU_OBS_MISS
        observations["m2"] = obs_m2
        self.bu_state.update_method("m2", obs_m2, self.sr)

        # m3: Second-order coherence g^(2)(0) estimate
        if mean_n > 0 and len(counts) > 1:
            mean_n_sq = np.mean(counts * (counts - 1))
            g2 = mean_n_sq / (mean_n ** 2) if mean_n > 0 else 2.0
            obs_m3 = BU_OBS_HIT if g2 < 1.0 else BU_OBS_MISS
        else:
            obs_m3 = BU_OBS_MISS
            g2 = 2.0
        observations["m3"] = obs_m3
        self.bu_state.update_method("m3", obs_m3, self.sr)

        # m4: Entropy test
        if mean_n > 0:
            hist, _ = np.histogram(counts, bins="auto", density=True)
            hist = hist[hist > 0]
            bin_width = (np.max(counts) - np.min(counts)) / len(hist) if len(hist) > 0 else 1.0
            entropy = -np.sum(hist * np.log2(hist)) * bin_width
            poisson_entropy = 0.5 * np.log2(2.0 * np.pi * np.e * mean_n)
            obs_m4 = BU_OBS_HIT if entropy < poisson_entropy else BU_OBS_MISS
        else:
            obs_m4 = BU_OBS_MISS
        observations["m4"] = obs_m4
        self.bu_state.update_method("m4", obs_m4, self.sr)

        # Compute combined posterior
        combined = self.bu_state.compute_combined_posterior(self.sr)

        return {
            "window_observations": observations,
            "mandel_Q": Q,
            "fano_factor": fano,
            "g2_estimate": g2,
            "ks_statistic": ks_stat,
            "ks_pvalue": ks_p,
            "lz_complexity": lz_complexity,
            "combined_posterior": combined,
            "coherence_state": self.bu_state.coherence_state(),
            "summary": self.bu_state.summary(),
        }


def _autocorrelation(x: np.ndarray, lag: int) -> float:
    """Compute normalized autocorrelation at given lag."""
    n = len(x)
    if n <= lag:
        return 0.0
    mean = np.mean(x)
    var = np.var(x)
    if var == 0:
        return 0.0
    return np.mean((x[: n - lag] - mean) * (x[lag:] - mean)) / var


def _lempel_ziv_complexity(sequence: np.ndarray) -> int:
    """Compute Lempel-Ziv complexity of a binary sequence."""
    s = "".join(str(int(b)) for b in sequence)
    n = len(s)
    if n == 0:
        return 0

    complexity = 1
    i = 0
    prefix_len = 1

    while i + prefix_len <= n:
        substring = s[i + 1 : i + prefix_len + 1]
        if substring in s[: i + prefix_len]:
            prefix_len += 1
            if i + prefix_len > n:
                break
        else:
            complexity += 1
            i = i + prefix_len
            prefix_len = 1

    return complexity


def simulate_coherent_stream(
    n_counts: int,
    mean_rate: float = 50.0,
    coherence_fraction: float = 0.3,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Simulate a photon count stream with partial coherence.

    Generates a mixture of Poisson (thermal) and sub-Poissonian (coherent)
    components, controlled by the coherence_fraction parameter.

    Parameters
    ----------
    n_counts : int
        Number of time bins.
    mean_rate : float
        Mean photon count per bin.
    coherence_fraction : float
        Fraction of signal from coherent source (0 = thermal, 1 = coherent).
    rng : np.random.Generator, optional
        Random number generator.

    Returns
    -------
    np.ndarray
        Simulated photon counts per time bin.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    thermal_rate = mean_rate * (1.0 - coherence_fraction)
    coherent_rate = mean_rate * coherence_fraction

    thermal_counts = rng.poisson(thermal_rate, size=n_counts)

    n_trials = max(int(coherent_rate * 10), 1)
    p_trial = min(coherent_rate / n_trials, 1.0)
    coherent_counts = rng.binomial(n_trials, p_trial, size=n_counts)

    return thermal_counts + coherent_counts


if __name__ == "__main__":
    print("=== Bayesian Coherence Estimation Demo ===\n")

    rng = np.random.default_rng(42)

    print("--- Thermal Stream (coherence_fraction=0.0) ---")
    thermal = simulate_coherent_stream(
        500, mean_rate=50.0, coherence_fraction=0.0, rng=rng
    )
    estimator_thermal = BiophotonCoherenceEstimator(window_size=100)
    for i in range(0, 500, 100):
        result = estimator_thermal.ingest_counts(thermal[i : i + 100])
        if result is not None:
            print(
                f"  Window {i // 100 + 1}: posterior={result['combined_posterior']:.4f}, "
                f"Q={result['mandel_Q']:.3f}, "
                f"state={result['coherence_state']}"
            )

    print("\n--- Partially Coherent Stream (coherence_fraction=0.5) ---")
    rng2 = np.random.default_rng(123)
    coherent = simulate_coherent_stream(
        500, mean_rate=50.0, coherence_fraction=0.5, rng=rng2
    )
    estimator_coherent = BiophotonCoherenceEstimator(window_size=100)
    for i in range(0, 500, 100):
        result = estimator_coherent.ingest_counts(coherent[i : i + 100])
        if result is not None:
            print(
                f"  Window {i // 100 + 1}: posterior={result['combined_posterior']:.4f}, "
                f"Q={result['mandel_Q']:.3f}, "
                f"state={result['coherence_state']}"
            )

    print("\n=== Summary ===")
    print(f"Thermal final posterior:  {estimator_thermal.bu_state.combined_posterior:.4f}")
    print(f"Coherent final posterior: {estimator_coherent.bu_state.combined_posterior:.4f}")
