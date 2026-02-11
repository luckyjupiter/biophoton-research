#!/usr/bin/env python3
"""Surrogate data generation for hypothesis testing.

Implements:
- Shuffled surrogates (test for any temporal structure)
- Phase-randomized (Fourier) surrogates (test for nonlinearity)
- IAAFT surrogates (test for nonlinearity preserving exact distribution)
- Rate-matched Poisson surrogates (test against inhomogeneous Poisson)

References
----------
- Theiler J et al., Physica D 58: 77-94 (1992)
- Schreiber T, Schmitz A, Physical Review Letters 77(4): 635 (1996)
"""

import numpy as np
from typing import Optional, Tuple


def shuffled_surrogate(x: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
    """Generate a randomly shuffled surrogate.

    Preserves the amplitude distribution but destroys all temporal correlations.
    Tests H0: the data is an i.i.d. process.

    Parameters
    ----------
    x : np.ndarray
        Original time series.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        Shuffled surrogate.
    """
    rng = np.random.default_rng(seed)
    surrogate = x.copy()
    rng.shuffle(surrogate)
    return surrogate


def phase_randomized_surrogate(x: np.ndarray,
                               seed: Optional[int] = None) -> np.ndarray:
    """Generate a Fourier phase-randomized surrogate.

    Preserves the power spectrum (and thus the autocorrelation function)
    but randomizes phases. Tests H0: the data is a linear Gaussian process.

    Parameters
    ----------
    x : np.ndarray
        Original time series.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        Phase-randomized surrogate.
    """
    rng = np.random.default_rng(seed)
    N = len(x)

    # FFT
    X = np.fft.rfft(x)

    # Random phases (preserve symmetry for real output)
    n_freq = len(X)
    random_phases = rng.uniform(0, 2 * np.pi, n_freq)
    # DC component (index 0) and Nyquist (last, if N even) keep their phase
    random_phases[0] = 0
    if N % 2 == 0:
        random_phases[-1] = 0

    # Apply random phases
    X_surr = np.abs(X) * np.exp(1j * (np.angle(X) + random_phases))

    # Inverse FFT
    surrogate = np.fft.irfft(X_surr, n=N)
    return surrogate


def iaaft_surrogate(x: np.ndarray, max_iter: int = 1000,
                    tol: float = 1e-8,
                    seed: Optional[int] = None) -> Tuple[np.ndarray, int]:
    """Generate an IAAFT (Iterative Amplitude Adjusted Fourier Transform) surrogate.

    Preserves BOTH the power spectrum AND the exact amplitude distribution.
    Tests H0: the data is a monotonic nonlinear transformation of a linear
    Gaussian process (i.e., the temporal structure is fully explained by
    the power spectrum and the marginal distribution).

    For integer-valued photon count data, ties in ranking are broken randomly.

    Parameters
    ----------
    x : np.ndarray
        Original time series.
    max_iter : int
        Maximum number of iterations.
    tol : float
        Convergence tolerance on spectral match.
    seed : int, optional
        Random seed.

    Returns
    -------
    surrogate : np.ndarray
        IAAFT surrogate.
    n_iter : int
        Number of iterations to convergence.
    """
    rng = np.random.default_rng(seed)
    N = len(x)

    # Sorted original values and target Fourier amplitudes
    x_sorted = np.sort(x)
    target_amplitudes = np.abs(np.fft.rfft(x))

    # Initialize with random shuffle
    surrogate = x.copy()
    rng.shuffle(surrogate)

    prev_spec_diff = np.inf

    for iteration in range(max_iter):
        # Step A: Match power spectrum
        S = np.fft.rfft(surrogate)
        phases = np.angle(S)
        S_adjusted = target_amplitudes * np.exp(1j * phases)
        surrogate_spectral = np.fft.irfft(S_adjusted, n=N)

        # Step B: Match amplitude distribution via rank ordering
        # For ties (common in photon count data), break randomly
        ranks = _rank_with_random_ties(surrogate_spectral, rng)
        surrogate = x_sorted[ranks]

        # Check convergence: how well does the spectrum match?
        current_amplitudes = np.abs(np.fft.rfft(surrogate))
        spec_diff = np.mean((current_amplitudes - target_amplitudes) ** 2)

        if abs(prev_spec_diff - spec_diff) < tol:
            return surrogate, iteration + 1

        prev_spec_diff = spec_diff

    return surrogate, max_iter


def _rank_with_random_ties(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Compute rank ordering with random tie-breaking.

    Essential for integer-valued (photon count) data where many values
    are identical.

    Parameters
    ----------
    x : np.ndarray
        Values to rank.
    rng : np.random.Generator
        Random number generator for tie-breaking.

    Returns
    -------
    np.ndarray
        Integer ranks (0-indexed).
    """
    N = len(x)
    # Add tiny random noise to break ties
    noise = rng.uniform(-1e-10, 1e-10, N)
    return np.argsort(np.argsort(x + noise))


def rate_matched_poisson_surrogate(x: np.ndarray, window: int = 50,
                                   seed: Optional[int] = None) -> np.ndarray:
    """Generate a Poisson surrogate with locally matched rate.

    Estimates the local emission rate by smoothing the original data,
    then generates Poisson draws with that rate. Tests H0: the data
    is an inhomogeneous Poisson process (i.e., all temporal structure
    comes from rate modulation, not from point-process correlations).

    Parameters
    ----------
    x : np.ndarray
        Original count time series (non-negative integers).
    window : int
        Smoothing window for rate estimation.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        Rate-matched Poisson surrogate.
    """
    rng = np.random.default_rng(seed)

    # Estimate local rate by moving average
    kernel = np.ones(window) / window
    local_rate = np.convolve(x.astype(float), kernel, mode='same')
    local_rate = np.maximum(local_rate, 0.01)  # avoid zero rate

    return rng.poisson(local_rate)


def generate_surrogates(x: np.ndarray, n_surrogates: int = 99,
                        method: str = 'iaaft',
                        seed: int = 42,
                        **kwargs) -> np.ndarray:
    """Generate an ensemble of surrogates.

    Parameters
    ----------
    x : np.ndarray
        Original time series.
    n_surrogates : int
        Number of surrogates to generate.
    method : str
        One of 'shuffle', 'phase', 'iaaft', 'poisson'.
    seed : int
        Base random seed.
    **kwargs
        Additional arguments passed to the surrogate generator.

    Returns
    -------
    np.ndarray, shape (n_surrogates, len(x))
        Array of surrogates.
    """
    surrogates = np.zeros((n_surrogates, len(x)))

    for i in range(n_surrogates):
        s = seed + i
        if method == 'shuffle':
            surrogates[i] = shuffled_surrogate(x, seed=s)
        elif method == 'phase':
            surrogates[i] = phase_randomized_surrogate(x, seed=s)
        elif method == 'iaaft':
            surrogates[i], _ = iaaft_surrogate(x, seed=s, **kwargs)
        elif method == 'poisson':
            surrogates[i] = rate_matched_poisson_surrogate(x, seed=s, **kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")

    return surrogates


def surrogate_test(x: np.ndarray, statistic_func, n_surrogates: int = 99,
                   method: str = 'iaaft', seed: int = 42,
                   **kwargs) -> dict:
    """Perform a surrogate data test.

    Parameters
    ----------
    x : np.ndarray
        Original time series.
    statistic_func : callable
        Function that takes a time series and returns a scalar statistic.
    n_surrogates : int
        Number of surrogates.
    method : str
        Surrogate generation method.
    seed : int
        Random seed.
    **kwargs
        Additional arguments for the surrogate generator.

    Returns
    -------
    dict with keys:
        'statistic_original': test statistic on original data
        'statistic_surrogates': array of surrogate statistics
        'p_value': two-sided p-value
        'rank': rank of original among surrogates
        'significant': bool, True if p < 0.05
    """
    stat_orig = statistic_func(x)

    surrogates = generate_surrogates(x, n_surrogates, method, seed, **kwargs)
    stat_surr = np.array([statistic_func(s) for s in surrogates])

    # Rank of original among surrogates
    rank = np.sum(stat_surr <= stat_orig) + 1
    n_total = n_surrogates + 1

    # Two-sided p-value
    p_value = 2.0 * min(rank, n_total - rank) / n_total

    return {
        'statistic_original': stat_orig,
        'statistic_surrogates': stat_surr,
        'p_value': p_value,
        'rank': rank,
        'significant': p_value < 0.05,
    }


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/yesh/biophoton-research/worktrees/track-02/src')
    from synthetic_data import fgn_davies_harte, poisson_homogeneous, correlated_poisson
    from dfa import dfa

    print("=== IAAFT surrogate test on correlated signal ===")
    x_corr = fgn_davies_harte(1024, 0.7, seed=42)
    _, _, alpha_orig, _ = dfa(x_corr)

    def dfa_alpha(series):
        _, _, a, _ = dfa(series)
        return a

    result = surrogate_test(x_corr, dfa_alpha, n_surrogates=19,
                            method='shuffle', seed=42)
    print(f"  Original DFA alpha: {result['statistic_original']:.4f}")
    print(f"  Surrogate mean:     {np.mean(result['statistic_surrogates']):.4f}")
    print(f"  p-value:            {result['p_value']:.4f}")
    print(f"  Significant:        {result['significant']}")

    print("\n=== IAAFT surrogate test on white noise (should be non-significant) ===")
    x_white = fgn_davies_harte(1024, 0.5, seed=42)
    result_white = surrogate_test(x_white, dfa_alpha, n_surrogates=19,
                                  method='shuffle', seed=42)
    print(f"  Original DFA alpha: {result_white['statistic_original']:.4f}")
    print(f"  Surrogate mean:     {np.mean(result_white['statistic_surrogates']):.4f}")
    print(f"  p-value:            {result_white['p_value']:.4f}")
    print(f"  Significant:        {result_white['significant']}")

    print("\n=== IAAFT convergence on Poisson data ===")
    x_pois = poisson_homogeneous(512, rate=5.0, seed=42)
    surr, n_iter = iaaft_surrogate(x_pois, seed=42)
    print(f"  Converged in {n_iter} iterations")
    print(f"  Original mean={np.mean(x_pois):.2f}, surrogate mean={np.mean(surr):.2f}")
    print(f"  Distribution match: {np.allclose(np.sort(x_pois), np.sort(surr))}")
