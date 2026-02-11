#!/usr/bin/env python3
"""Synthetic biophoton-like data generation with known correlation structures.

Generates:
- Fractional Gaussian noise (fGn) with specified Hurst exponent
- ARFIMA processes with long memory
- Poisson processes (homogeneous and inhomogeneous)
- Modulated Poisson processes (simulating metabolic bursting)
- Binomial multifractal cascades (for testing MFDFA)

All generators produce integer-valued photon count series when appropriate.
"""

import numpy as np
from typing import Optional, Tuple


def fgn_davies_harte(n: int, H: float, sigma: float = 1.0,
                     seed: Optional[int] = None) -> np.ndarray:
    """Generate fractional Gaussian noise via the Davies-Harte (circulant) method.

    Uses circulant embedding of the autocovariance matrix with proper
    Hermitian-symmetric frequency-domain generation for exact fGn.

    Parameters
    ----------
    n : int
        Length of the output series.
    H : float
        Hurst exponent in (0, 1). H=0.5 gives white noise.
    sigma : float
        Standard deviation of the output.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        Fractional Gaussian noise of length n.
    """
    rng = np.random.default_rng(seed)

    # Autocovariance of fGn at lag k:
    # gamma(k) = (sigma^2 / 2) * (|k-1|^{2H} - 2|k|^{2H} + |k+1|^{2H})
    m = 2 * n  # embed in circulant of size 2n
    k = np.arange(0, n + 1, dtype=float)
    gamma = 0.5 * sigma**2 * (
        np.abs(k - 1)**(2*H) - 2 * np.abs(k)**(2*H) + np.abs(k + 1)**(2*H)
    )
    gamma[0] = sigma**2

    # Build the first row of the circulant matrix (symmetric embedding)
    row = np.zeros(m)
    row[:n + 1] = gamma
    row[n + 1:] = gamma[n - 1:0:-1]

    # Eigenvalues of the circulant matrix via FFT
    eigenvalues = np.fft.fft(row).real

    # Check non-negativity (Davies-Harte condition)
    if np.any(eigenvalues < -1e-10):
        return _fgn_cholesky(n, H, sigma, rng)
    eigenvalues = np.maximum(eigenvalues, 0)

    # Generate frequency-domain coefficients with Hermitian symmetry
    w = np.zeros(m, dtype=complex)
    w[0] = np.sqrt(eigenvalues[0]) * rng.standard_normal()
    for j in range(1, m // 2):
        re = rng.standard_normal()
        im = rng.standard_normal()
        w[j] = np.sqrt(eigenvalues[j] / 2) * (re + 1j * im)
        w[m - j] = np.sqrt(eigenvalues[j] / 2) * (re - 1j * im)
    w[m // 2] = np.sqrt(eigenvalues[m // 2]) * rng.standard_normal()

    # IFFT with proper scaling: numpy ifft includes 1/m factor,
    # multiply by sqrt(m) to get correct variance.
    y = np.fft.ifft(w).real * np.sqrt(m)

    return y[:n]


def _fgn_cholesky(n: int, H: float, sigma: float,
                  rng: np.random.Generator) -> np.ndarray:
    """Fallback fGn generation via Cholesky decomposition.

    Slower (O(n^2) memory, O(n^3) time) but always works.
    Only suitable for n < ~5000.
    """
    gamma = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            lag = abs(i - j)
            if lag == 0:
                gamma[i, j] = sigma**2
            else:
                gamma[i, j] = 0.5 * sigma**2 * (
                    abs(lag - 1)**(2*H) - 2 * abs(lag)**(2*H) + abs(lag + 1)**(2*H)
                )

    L = np.linalg.cholesky(gamma)
    z = rng.standard_normal(n)
    return L @ z


def fbm_from_fgn(n: int, H: float, sigma: float = 1.0,
                 seed: Optional[int] = None) -> np.ndarray:
    """Generate fractional Brownian motion by cumulative summation of fGn.

    Parameters
    ----------
    n : int
        Length of the output fBm.
    H : float
        Hurst exponent.
    sigma : float
        Increment standard deviation.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        Fractional Brownian motion of length n.
    """
    increments = fgn_davies_harte(n, H, sigma, seed)
    return np.cumsum(increments)


def arfima(n: int, d: float, phi: Optional[list] = None,
           theta: Optional[list] = None, sigma: float = 1.0,
           seed: Optional[int] = None) -> np.ndarray:
    """Generate an ARFIMA(p, d, q) process.

    The fractional differencing parameter d relates to H by H = d + 0.5.

    Parameters
    ----------
    n : int
        Length of output.
    d : float
        Fractional differencing parameter, -0.5 < d < 0.5.
    phi : list, optional
        AR coefficients [phi_1, ..., phi_p].
    theta : list, optional
        MA coefficients [theta_1, ..., theta_q].
    sigma : float
        Innovation standard deviation.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        ARFIMA process realization.
    """
    rng = np.random.default_rng(seed)

    if phi is None:
        phi = []
    if theta is None:
        theta = []

    # Fractional differencing filter via recursion: pi_0=1, pi_j = pi_{j-1}*(j-1+d)/j
    n_filter = min(n, 1000)
    pi_coeffs = np.zeros(n_filter)
    pi_coeffs[0] = 1.0
    for j in range(1, n_filter):
        pi_coeffs[j] = pi_coeffs[j - 1] * (j - 1 + d) / j

    burn_in = 500
    total = n + burn_in
    eps = rng.normal(0, sigma, total)

    # Apply fractional filter
    x = np.zeros(total)
    for t in range(total):
        frac_sum = 0.0
        for j in range(min(t + 1, n_filter)):
            frac_sum += pi_coeffs[j] * eps[t - j]
        x[t] = frac_sum

    # Apply AR part
    p = len(phi)
    if p > 0:
        y = np.copy(x)
        for t in range(p, total):
            ar_sum = sum(phi[kk] * y[t - kk - 1] for kk in range(p))
            y[t] = x[t] + ar_sum
        x = y

    # Apply MA part
    q = len(theta)
    if q > 0:
        y = np.copy(x)
        for t in range(q, total):
            ma_sum = sum(theta[kk] * eps[t - kk - 1] for kk in range(q))
            y[t] = x[t] + ma_sum
        x = y

    return x[burn_in:]


def poisson_homogeneous(n: int, rate: float = 10.0,
                        seed: Optional[int] = None) -> np.ndarray:
    """Generate a homogeneous Poisson count time series.

    Parameters
    ----------
    n : int
        Number of time bins.
    rate : float
        Mean counts per bin.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        Integer-valued count series.
    """
    rng = np.random.default_rng(seed)
    return rng.poisson(rate, n)


def poisson_modulated(n: int, base_rate: float = 10.0,
                      modulation_depth: float = 0.5,
                      modulation_period: int = 100,
                      seed: Optional[int] = None) -> np.ndarray:
    """Generate a sinusoidally modulated Poisson process.

    Simulates periodic metabolic modulation of biophoton emission rate.

    Parameters
    ----------
    n : int
        Number of time bins.
    base_rate : float
        Mean count rate.
    modulation_depth : float
        Fractional modulation depth (0 to 1).
    modulation_period : int
        Period of modulation in bins.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        Integer-valued count series.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    rate = base_rate * (1.0 + modulation_depth * np.sin(2 * np.pi * t / modulation_period))
    rate = np.maximum(rate, 0.01)
    return rng.poisson(rate)


def binomial_multifractal_cascade(n_levels: int, a: float = 0.6,
                                  base_rate: float = 10.0,
                                  seed: Optional[int] = None) -> np.ndarray:
    """Generate a binomial multifractal cascade for MFDFA testing.

    The cascade produces a measure with known multifractal properties.
    Theoretical h(q) = 1 - log2(a^q + (1-a)^q) / q for the increments.

    Parameters
    ----------
    n_levels : int
        Number of cascade levels. Output length = 2^n_levels.
    a : float
        Cascade parameter, 0 < a < 1. a=0.5 gives monofractal.
    base_rate : float
        Mean intensity for normalizing output.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        The cascade measure (continuous) of length 2^n_levels.
    """
    rng = np.random.default_rng(seed)

    n = 2 ** n_levels
    measure = np.ones(n)

    for level in range(n_levels):
        segment_size = n // (2 ** (level + 1))
        for i in range(2 ** level):
            start = i * 2 * segment_size
            if rng.random() < 0.5:
                left_weight, right_weight = a, 1.0 - a
            else:
                left_weight, right_weight = 1.0 - a, a
            measure[start:start + segment_size] *= left_weight * 2
            measure[start + segment_size:start + 2 * segment_size] *= right_weight * 2

    measure = measure * base_rate / np.mean(measure)
    return measure


def correlated_poisson(n: int, H: float, rate: float = 10.0,
                       seed: Optional[int] = None) -> np.ndarray:
    """Generate a Poisson process whose rate is modulated by fGn.

    Produces integer-valued photon counts with long-range correlations,
    realistic for biophoton data analysis validation.

    Parameters
    ----------
    n : int
        Number of time bins.
    H : float
        Hurst exponent of the rate modulation (0 < H < 1).
    rate : float
        Mean count rate per bin.
    seed : int, optional
        Random seed.

    Returns
    -------
    np.ndarray
        Integer-valued photon count series with correlations governed by H.
    """
    rng = np.random.default_rng(seed)

    # Generate correlated rate modulation
    noise = fgn_davies_harte(n, H, sigma=1.0, seed=seed)

    # Transform to positive rate via log-normal mapping
    sigma_noise = 0.3  # ~30% coefficient of variation
    noise_std = np.std(noise)
    if noise_std > 0:
        noise = noise / noise_std
    log_rate = np.log(rate) + sigma_noise * noise
    rates = np.exp(log_rate)

    counts = rng.poisson(rates)
    return counts


def generate_test_suite(n: int = 4096, seed: int = 42) -> dict:
    """Generate a full suite of test signals for method validation.

    Parameters
    ----------
    n : int
        Length of each signal.
    seed : int
        Base random seed.

    Returns
    -------
    dict
        Dictionary mapping signal names to (data, expected_H) tuples.
    """
    signals = {}

    # White noise (H = 0.5)
    signals['fgn_H0.5'] = (fgn_davies_harte(n, 0.5, seed=seed), 0.5)

    # Anti-correlated fGn (H = 0.3) -- like Dlask et al. findings
    signals['fgn_H0.3'] = (fgn_davies_harte(n, 0.3, seed=seed + 1), 0.3)

    # Mildly persistent fGn (H = 0.7)
    signals['fgn_H0.7'] = (fgn_davies_harte(n, 0.7, seed=seed + 2), 0.7)

    # Strongly persistent fGn (H = 0.9)
    signals['fgn_H0.9'] = (fgn_davies_harte(n, 0.9, seed=seed + 3), 0.9)

    # Poisson (should show H ~ 0.5)
    signals['poisson'] = (poisson_homogeneous(n, rate=10.0, seed=seed + 4), 0.5)

    # Correlated Poisson (H = 0.7)
    signals['corr_poisson_H0.7'] = (
        correlated_poisson(n, H=0.7, rate=10.0, seed=seed + 5), 0.7
    )

    # Correlated Poisson (H = 0.3) -- anti-persistent biophoton model
    signals['corr_poisson_H0.3'] = (
        correlated_poisson(n, H=0.3, rate=10.0, seed=seed + 6), 0.3
    )

    # ARFIMA with d = 0.2 (H = 0.7)
    signals['arfima_d0.2'] = (arfima(n, d=0.2, seed=seed + 7), 0.7)

    # ARFIMA with d = -0.2 (H = 0.3)
    signals['arfima_d-0.2'] = (arfima(n, d=-0.2, seed=seed + 8), 0.3)

    return signals


if __name__ == '__main__':
    signals = generate_test_suite(n=2048, seed=42)
    for name, (data, expected_H) in signals.items():
        print(f"{name:25s}: len={len(data)}, mean={np.mean(data):.4f}, "
              f"std={np.std(data):.4f}, expected H={expected_H:.1f}")
