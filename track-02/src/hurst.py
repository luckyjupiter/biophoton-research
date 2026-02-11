#!/usr/bin/env python3
"""Multiple Hurst exponent estimators with bias characterization.

Implements:
- Rescaled Range (R/S) analysis
- DFA-based Hurst estimation
- Wavelet-based estimation (discrete wavelet transform variance)
- Periodogram-based estimation (spectral slope)
- Detrended Moving Average (DMA)

Includes tools for quantifying small-sample bias at the short series
lengths (N=256..2048) typical of biophoton experiments.

References
----------
- Hurst HE, Trans. Am. Soc. Civ. Eng. 116: 770-808 (1951)
- Peng CK et al., Physical Review E 49(2): 1685 (1994)
- Abry P, Veitch D, IEEE Trans. Info. Theory 44(1): 2-15 (1998)
"""

import numpy as np
from scipy import signal as sig
from typing import Optional, Tuple, List


def hurst_rs(x: np.ndarray, min_window: int = 16,
             max_window: Optional[int] = None,
             n_windows: int = 20) -> Tuple[float, np.ndarray, np.ndarray]:
    """Rescaled range (R/S) analysis for Hurst exponent estimation.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    min_window : int
        Minimum subseries length.
    max_window : int, optional
        Maximum subseries length. Defaults to N//2.
    n_windows : int
        Number of window sizes to use.

    Returns
    -------
    H : float
        Estimated Hurst exponent.
    window_sizes : np.ndarray
        Window sizes used.
    rs_values : np.ndarray
        Mean R/S values at each window size.
    """
    N = len(x)
    if max_window is None:
        max_window = N // 2

    window_sizes = np.unique(np.logspace(
        np.log10(min_window), np.log10(max_window), n_windows
    ).astype(int))

    rs_values = np.zeros(len(window_sizes))

    for i, w in enumerate(window_sizes):
        n_blocks = N // w
        if n_blocks < 1:
            rs_values[i] = np.nan
            continue

        rs_list = []
        for b in range(n_blocks):
            block = x[b * w:(b + 1) * w]
            mean_block = np.mean(block)
            std_block = np.std(block, ddof=1)
            if std_block < 1e-12:
                continue

            # Cumulative deviations from mean
            cum_dev = np.cumsum(block - mean_block)
            R = np.max(cum_dev) - np.min(cum_dev)
            rs_list.append(R / std_block)

        if len(rs_list) > 0:
            rs_values[i] = np.mean(rs_list)
        else:
            rs_values[i] = np.nan

    # Log-log regression
    valid = ~np.isnan(rs_values) & (rs_values > 0)
    if np.sum(valid) < 2:
        return 0.5, window_sizes, rs_values

    log_w = np.log(window_sizes[valid])
    log_rs = np.log(rs_values[valid])
    coeffs = np.polyfit(log_w, log_rs, 1)
    H = coeffs[0]

    return H, window_sizes[valid], rs_values[valid]


def hurst_dfa(x: np.ndarray, order: int = 1, **kwargs) -> float:
    """Hurst exponent via DFA.

    For stationary processes (alpha < 1), H = alpha.
    For nonstationary (alpha > 1), H = alpha - 1.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    order : int
        DFA detrending order.
    **kwargs
        Additional arguments passed to dfa().

    Returns
    -------
    float
        Estimated Hurst exponent.
    """
    # Import here to avoid circular dependency
    from dfa import dfa as _dfa
    _, _, alpha, _ = _dfa(x, order=order, **kwargs)
    if alpha > 1.0:
        return alpha - 1.0
    return alpha


def hurst_wavelet(x: np.ndarray, n_levels: Optional[int] = None) -> Tuple[float, np.ndarray, np.ndarray]:
    """Hurst exponent via discrete wavelet transform variance.

    Uses the Haar wavelet for simplicity. The wavelet variance at scale j
    scales as 2^{j(2H+1)} for fGn with Hurst exponent H.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    n_levels : int, optional
        Number of decomposition levels. Defaults to floor(log2(N)) - 2.

    Returns
    -------
    H : float
        Estimated Hurst exponent.
    scales : np.ndarray
        Wavelet scales (2^j).
    variances : np.ndarray
        Wavelet variance at each scale.
    """
    N = len(x)
    if n_levels is None:
        n_levels = max(int(np.floor(np.log2(N))) - 2, 2)

    # Haar wavelet decomposition via successive averaging
    variances = []
    scales = []

    current = x.copy().astype(float)
    for j in range(1, n_levels + 1):
        n_cur = len(current)
        if n_cur < 4:
            break
        n_pairs = n_cur // 2

        # Detail coefficients (differences)
        details = (current[1::2] - current[::2])[:n_pairs] / np.sqrt(2)
        # Approximation coefficients (averages)
        approx = (current[1::2] + current[::2])[:n_pairs] / np.sqrt(2)

        var_j = np.var(details)
        if var_j > 0:
            variances.append(var_j)
            scales.append(2 ** j)

        current = approx

    if len(scales) < 2:
        return 0.5, np.array([]), np.array([])

    scales = np.array(scales)
    variances = np.array(variances)

    # The wavelet variance of fGn scales as sigma^2 * 2^{j(2H-1)}
    # so log2(var_j) = const + (2H-1)*j
    log_scales = np.log2(scales)
    log_var = np.log2(variances)

    coeffs = np.polyfit(log_scales, log_var, 1)
    # slope = 2H - 1 for fGn
    H = (coeffs[0] + 1) / 2.0

    return H, scales, variances


def hurst_periodogram(x: np.ndarray, freq_range: Optional[Tuple[float, float]] = None) -> Tuple[float, np.ndarray, np.ndarray]:
    """Hurst exponent from power spectral density slope.

    For fGn with Hurst H, the PSD follows S(f) ~ f^{-(2H-1)}.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    freq_range : tuple of (f_low, f_high), optional
        Frequency range for fitting. Defaults to (1/(N/4), 0.4).

    Returns
    -------
    H : float
        Estimated Hurst exponent.
    freqs : np.ndarray
        Frequencies from Welch periodogram.
    psd : np.ndarray
        Power spectral density estimate.
    """
    N = len(x)

    # Welch periodogram
    nperseg = min(N // 4, 256)
    freqs, psd = sig.welch(x, nperseg=nperseg, noverlap=nperseg // 2)

    # Remove zero frequency
    mask = freqs > 0
    freqs = freqs[mask]
    psd = psd[mask]

    if freq_range is None:
        f_low = 4.0 / N  # exclude very low freqs
        f_high = 0.4
    else:
        f_low, f_high = freq_range

    fit_mask = (freqs >= f_low) & (freqs <= f_high)
    if np.sum(fit_mask) < 3:
        return 0.5, freqs, psd

    log_f = np.log(freqs[fit_mask])
    log_psd = np.log(psd[fit_mask])

    coeffs = np.polyfit(log_f, log_psd, 1)
    beta = -coeffs[0]  # spectral exponent: S(f) ~ f^{-beta}

    # beta = 2H - 1 for stationary fGn
    H = (beta + 1) / 2.0

    return H, freqs, psd


def hurst_dma(x: np.ndarray, min_scale: int = 4,
              max_scale: Optional[int] = None,
              n_scales: int = 30) -> Tuple[float, np.ndarray, np.ndarray]:
    """Hurst exponent via Detrended Moving Average analysis.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    min_scale : int
        Minimum moving average window.
    max_scale : int, optional
        Maximum moving average window. Defaults to N//4.
    n_scales : int
        Number of scales.

    Returns
    -------
    H : float
        Estimated Hurst exponent.
    scales : np.ndarray
        Window sizes.
    fluct : np.ndarray
        DMA fluctuation at each scale.
    """
    N = len(x)
    if max_scale is None:
        max_scale = N // 4

    profile = np.cumsum(x - np.mean(x))

    scales = np.unique(np.logspace(
        np.log10(min_scale), np.log10(max_scale), n_scales
    ).astype(int))

    fluct = np.zeros(len(scales))

    for i, s in enumerate(scales):
        if s >= N:
            fluct[i] = np.nan
            continue
        # Backward moving average
        ma = np.convolve(profile, np.ones(s) / s, mode='valid')
        # Align: moving average at index k uses profile[k-s+1:k+1]
        residual = profile[s - 1:] - ma
        fluct[i] = np.sqrt(np.mean(residual ** 2))

    valid = ~np.isnan(fluct) & (fluct > 0)
    if np.sum(valid) < 2:
        return 0.5, scales, fluct

    log_s = np.log(scales[valid])
    log_f = np.log(fluct[valid])
    coeffs = np.polyfit(log_s, log_f, 1)
    H = coeffs[0]

    if H > 1.0:
        H = H - 1.0

    return H, scales[valid], fluct[valid]


def compare_hurst_estimators(x: np.ndarray, true_H: Optional[float] = None) -> dict:
    """Compare all Hurst exponent estimators on the same data.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    true_H : float, optional
        Known true Hurst exponent for bias calculation.

    Returns
    -------
    dict
        Results from each method including estimated H and bias.
    """
    results = {}

    # R/S
    H_rs, _, _ = hurst_rs(x)
    results['R/S'] = {'H': H_rs}

    # DFA
    H_dfa = hurst_dfa(x)
    results['DFA'] = {'H': H_dfa}

    # Wavelet
    H_wav, _, _ = hurst_wavelet(x)
    results['Wavelet'] = {'H': H_wav}

    # Periodogram
    H_per, _, _ = hurst_periodogram(x)
    results['Periodogram'] = {'H': H_per}

    # DMA
    H_dma, _, _ = hurst_dma(x)
    results['DMA'] = {'H': H_dma}

    # Add bias if true H is known
    if true_H is not None:
        for method in results:
            results[method]['bias'] = results[method]['H'] - true_H
            results[method]['true_H'] = true_H

    return results


def bias_characterization(H_values: List[float] = None,
                          N_values: List[int] = None,
                          n_realizations: int = 100,
                          seed: int = 42) -> dict:
    """Characterize estimator bias as a function of H and series length N.

    This is the key analysis for biophoton work: how reliable are the
    estimators at the short series lengths (N=256..2048) typical of
    biophoton experiments?

    Parameters
    ----------
    H_values : list of float
        Hurst exponents to test. Defaults to [0.3, 0.5, 0.7, 0.9].
    N_values : list of int
        Series lengths to test. Defaults to [128, 256, 512, 1024, 2048, 4096].
    n_realizations : int
        Number of Monte Carlo realizations per (H, N) pair.
    seed : int
        Base random seed.

    Returns
    -------
    dict with keys:
        'H_values', 'N_values': parameter grids
        'methods': list of method names
        'mean_H': shape (n_methods, n_H, n_N) mean estimated H
        'std_H': shape (n_methods, n_H, n_N) std of estimated H
        'bias': shape (n_methods, n_H, n_N) mean bias (estimated - true)
        'rmse': shape (n_methods, n_H, n_N) root mean squared error
    """
    import sys
    sys.path.insert(0, '/home/yesh/biophoton-research/worktrees/track-02/src')
    from synthetic_data import fgn_davies_harte

    if H_values is None:
        H_values = [0.3, 0.5, 0.7, 0.9]
    if N_values is None:
        N_values = [128, 256, 512, 1024, 2048, 4096]

    methods = ['R/S', 'DFA', 'Wavelet', 'Periodogram', 'DMA']
    n_methods = len(methods)
    n_H = len(H_values)
    n_N = len(N_values)

    all_H = np.zeros((n_methods, n_H, n_N, n_realizations))

    for h_idx, H_true in enumerate(H_values):
        for n_idx, N in enumerate(N_values):
            for r in range(n_realizations):
                x = fgn_davies_harte(N, H_true, seed=seed + h_idx * 10000 + n_idx * 1000 + r)
                results = compare_hurst_estimators(x, true_H=H_true)
                for m_idx, method in enumerate(methods):
                    all_H[m_idx, h_idx, n_idx, r] = results[method]['H']

    mean_H = np.mean(all_H, axis=3)
    std_H = np.std(all_H, axis=3)

    # Bias and RMSE
    true_grid = np.array(H_values)[np.newaxis, :, np.newaxis]
    bias = mean_H - true_grid
    rmse = np.sqrt(np.mean((all_H - true_grid[:, :, :, np.newaxis]) ** 2, axis=3))

    return {
        'H_values': H_values,
        'N_values': N_values,
        'methods': methods,
        'mean_H': mean_H,
        'std_H': std_H,
        'bias': bias,
        'rmse': rmse,
    }


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/yesh/biophoton-research/worktrees/track-02/src')
    from synthetic_data import fgn_davies_harte

    print("=== Comparing Hurst estimators on fGn signals ===")
    for H_true in [0.3, 0.5, 0.7, 0.9]:
        x = fgn_davies_harte(4096, H_true, seed=42)
        results = compare_hurst_estimators(x, true_H=H_true)
        print(f"\nH_true = {H_true:.1f}:")
        for method, res in results.items():
            print(f"  {method:15s}: H={res['H']:.4f}, bias={res['bias']:+.4f}")
