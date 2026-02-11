#!/usr/bin/env python3
"""Detrended Fluctuation Analysis (DFA) and Multifractal DFA (MFDFA).

Implements the algorithms of Peng et al. (1994) and Kantelhardt et al. (2002)
for detecting long-range correlations and multifractal scaling in biophoton
count time series.

References
----------
- Peng CK et al., Physical Review E 49(2): 1685 (1994)
- Kantelhardt JW et al., Physica A 316(1-4): 87-114 (2002)
"""

import numpy as np
from typing import Optional, Tuple, List


def dfa(x: np.ndarray, scales: Optional[np.ndarray] = None,
        order: int = 1, min_scale: int = 16,
        max_scale: Optional[int] = None,
        n_scales: int = 30) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """Detrended Fluctuation Analysis.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    scales : np.ndarray, optional
        Array of window sizes. If None, logarithmically spaced scales
        are generated between min_scale and max_scale.
    order : int
        Polynomial detrending order (1=linear, 2=quadratic, etc.).
    min_scale : int
        Minimum window size.
    max_scale : int, optional
        Maximum window size. Defaults to N//4.
    n_scales : int
        Number of logarithmically spaced scales.

    Returns
    -------
    scales : np.ndarray
        The window sizes used.
    fluct : np.ndarray
        The fluctuation function F(s) at each scale.
    alpha : float
        DFA scaling exponent (slope of log F(s) vs log s).
    r_squared : float
        R^2 of the log-log fit (quality of scaling).
    """
    N = len(x)
    if max_scale is None:
        max_scale = N // 4

    if scales is None:
        scales = np.unique(np.logspace(
            np.log10(min_scale), np.log10(max_scale), n_scales
        ).astype(int))
        scales = scales[scales >= min_scale]

    # Step 1: Integration (cumulative sum of mean-subtracted series)
    profile = np.cumsum(x - np.mean(x))

    fluct = np.zeros(len(scales))

    for idx, s in enumerate(scales):
        # Step 2: Segmentation -- non-overlapping from start and end
        n_seg = N // s
        if n_seg < 1:
            fluct[idx] = np.nan
            continue

        variances = []

        # Forward segments
        for v in range(n_seg):
            segment = profile[v * s:(v + 1) * s]
            # Step 3: Local detrending
            t = np.arange(s)
            coeffs = np.polyfit(t, segment, order)
            trend = np.polyval(coeffs, t)
            # Step 4: Variance
            var = np.mean((segment - trend) ** 2)
            variances.append(var)

        # Backward segments (from end)
        for v in range(n_seg):
            segment = profile[N - (v + 1) * s:N - v * s]
            t = np.arange(s)
            coeffs = np.polyfit(t, segment, order)
            trend = np.polyval(coeffs, t)
            var = np.mean((segment - trend) ** 2)
            variances.append(var)

        # Step 5: Fluctuation function
        fluct[idx] = np.sqrt(np.mean(variances))

    # Remove any NaN values
    valid = ~np.isnan(fluct) & (fluct > 0)
    scales_valid = scales[valid]
    fluct_valid = fluct[valid]

    # Step 6: Log-log regression
    if len(scales_valid) < 2:
        return scales, fluct, np.nan, 0.0

    log_s = np.log(scales_valid)
    log_f = np.log(fluct_valid)
    coeffs = np.polyfit(log_s, log_f, 1)
    alpha = coeffs[0]

    # R-squared
    fit = np.polyval(coeffs, log_s)
    ss_res = np.sum((log_f - fit) ** 2)
    ss_tot = np.sum((log_f - np.mean(log_f)) ** 2)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return scales_valid, fluct_valid, alpha, r_squared


def mfdfa(x: np.ndarray, q_list: Optional[np.ndarray] = None,
          scales: Optional[np.ndarray] = None,
          order: int = 1, min_scale: int = 16,
          max_scale: Optional[int] = None,
          n_scales: int = 30) -> dict:
    """Multifractal Detrended Fluctuation Analysis.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    q_list : np.ndarray, optional
        Array of moment orders q. Defaults to [-5, -4, ..., 4, 5].
    scales : np.ndarray, optional
        Array of window sizes.
    order : int
        Polynomial detrending order.
    min_scale : int
        Minimum window size.
    max_scale : int, optional
        Maximum window size.
    n_scales : int
        Number of scales.

    Returns
    -------
    dict with keys:
        'scales': window sizes
        'q_list': moment orders
        'Fq': F_q(s) array, shape (len(q_list), len(scales))
        'hq': generalized Hurst exponent h(q) for each q
        'tau_q': mass exponent tau(q) = q*h(q) - 1
        'alpha_mf': singularity exponents (Holder exponents)
        'f_alpha': singularity spectrum f(alpha)
        'delta_alpha': multifractal spectrum width
    """
    N = len(x)
    if max_scale is None:
        max_scale = N // 4

    if q_list is None:
        q_list = np.arange(-5, 6, dtype=float)
    q_list = np.array(q_list, dtype=float)

    if scales is None:
        scales = np.unique(np.logspace(
            np.log10(min_scale), np.log10(max_scale), n_scales
        ).astype(int))
        scales = scales[scales >= min_scale]

    # Integration
    profile = np.cumsum(x - np.mean(x))

    # Compute segment variances for all scales
    Fq = np.zeros((len(q_list), len(scales)))

    for s_idx, s in enumerate(scales):
        n_seg = N // s
        if n_seg < 1:
            Fq[:, s_idx] = np.nan
            continue

        seg_var = []

        # Forward segments
        for v in range(n_seg):
            segment = profile[v * s:(v + 1) * s]
            t = np.arange(s)
            coeffs = np.polyfit(t, segment, order)
            trend = np.polyval(coeffs, t)
            var = np.mean((segment - trend) ** 2)
            seg_var.append(var)

        # Backward segments
        for v in range(n_seg):
            segment = profile[N - (v + 1) * s:N - v * s]
            t = np.arange(s)
            coeffs = np.polyfit(t, segment, order)
            trend = np.polyval(coeffs, t)
            var = np.mean((segment - trend) ** 2)
            seg_var.append(var)

        seg_var = np.array(seg_var)
        # Remove zero-variance segments (can happen with constant data)
        seg_var = seg_var[seg_var > 0]
        if len(seg_var) == 0:
            Fq[:, s_idx] = np.nan
            continue

        n_total = len(seg_var)

        for q_idx, q in enumerate(q_list):
            if q == 0:
                # Logarithmic average for q=0
                Fq[q_idx, s_idx] = np.exp(
                    0.5 * np.mean(np.log(seg_var))
                )
            else:
                Fq[q_idx, s_idx] = (
                    np.mean(seg_var ** (q / 2))
                ) ** (1.0 / q)

    # Fit h(q) for each q
    hq = np.zeros(len(q_list))
    for q_idx in range(len(q_list)):
        valid = ~np.isnan(Fq[q_idx, :]) & (Fq[q_idx, :] > 0)
        if np.sum(valid) < 2:
            hq[q_idx] = np.nan
            continue
        log_s = np.log(scales[valid])
        log_fq = np.log(Fq[q_idx, valid])
        coeffs = np.polyfit(log_s, log_fq, 1)
        hq[q_idx] = coeffs[0]

    # Mass exponent tau(q)
    tau_q = q_list * hq - 1.0

    # Singularity spectrum via Legendre transform (numerical differentiation)
    # alpha = d(tau)/d(q), f(alpha) = q*alpha - tau(q)
    alpha_mf = np.gradient(tau_q, q_list)
    f_alpha = q_list * alpha_mf - tau_q

    # Spectrum width
    valid_f = ~np.isnan(alpha_mf)
    if np.any(valid_f):
        delta_alpha = np.max(alpha_mf[valid_f]) - np.min(alpha_mf[valid_f])
    else:
        delta_alpha = 0.0

    # Filter to valid scales
    valid_scales = np.all(~np.isnan(Fq), axis=0) & np.all(Fq > 0, axis=0)

    return {
        'scales': scales[valid_scales] if np.any(valid_scales) else scales,
        'q_list': q_list,
        'Fq': Fq[:, valid_scales] if np.any(valid_scales) else Fq,
        'hq': hq,
        'tau_q': tau_q,
        'alpha_mf': alpha_mf,
        'f_alpha': f_alpha,
        'delta_alpha': delta_alpha,
    }


def dfa_crossover(x: np.ndarray, order: int = 1,
                  min_scale: int = 10,
                  n_scales: int = 50) -> dict:
    """DFA with crossover detection.

    For biophoton data, identifies the scale at which correlations emerge
    above the Poisson noise floor.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    order : int
        Detrending polynomial order.
    min_scale : int
        Minimum window size.
    n_scales : int
        Number of scales.

    Returns
    -------
    dict with keys:
        'scales', 'fluct': DFA results
        'alpha_short': exponent at short scales
        'alpha_long': exponent at long scales
        'crossover_scale': estimated crossover scale
    """
    N = len(x)
    max_scale = N // 4

    scales, fluct, alpha_all, r2 = dfa(
        x, order=order, min_scale=min_scale,
        max_scale=max_scale, n_scales=n_scales
    )

    if len(scales) < 6:
        return {
            'scales': scales, 'fluct': fluct,
            'alpha_short': alpha_all, 'alpha_long': alpha_all,
            'crossover_scale': np.nan,
        }

    log_s = np.log(scales)
    log_f = np.log(fluct)

    # Try all possible crossover points
    best_residual = np.inf
    best_split = len(scales) // 2

    for split in range(3, len(scales) - 3):
        # Fit two lines
        c1 = np.polyfit(log_s[:split], log_f[:split], 1)
        c2 = np.polyfit(log_s[split:], log_f[split:], 1)
        r1 = np.sum((log_f[:split] - np.polyval(c1, log_s[:split])) ** 2)
        r2_val = np.sum((log_f[split:] - np.polyval(c2, log_s[split:])) ** 2)
        total_residual = r1 + r2_val

        if total_residual < best_residual:
            best_residual = total_residual
            best_split = split

    c1 = np.polyfit(log_s[:best_split], log_f[:best_split], 1)
    c2 = np.polyfit(log_s[best_split:], log_f[best_split:], 1)

    return {
        'scales': scales,
        'fluct': fluct,
        'alpha_short': c1[0],
        'alpha_long': c2[0],
        'crossover_scale': scales[best_split],
    }


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/yesh/biophoton-research/worktrees/track-02/src')
    from synthetic_data import fgn_davies_harte, poisson_homogeneous

    # Validate DFA on fGn with known H
    print("=== DFA Validation on fGn ===")
    for H_true in [0.3, 0.5, 0.7, 0.9]:
        x = fgn_davies_harte(4096, H_true, seed=42)
        _, _, alpha, r2 = dfa(x, order=1)
        print(f"  H_true={H_true:.1f} -> DFA alpha={alpha:.4f} (R^2={r2:.4f})")

    print("\n=== DFA on Poisson process ===")
    x_pois = poisson_homogeneous(4096, rate=10.0, seed=42)
    _, _, alpha_pois, r2_pois = dfa(x_pois, order=1)
    print(f"  Poisson -> DFA alpha={alpha_pois:.4f} (R^2={r2_pois:.4f})")

    print("\n=== MFDFA on fGn (should be monofractal) ===")
    x_mono = fgn_davies_harte(4096, 0.7, seed=42)
    result = mfdfa(x_mono, order=1)
    print(f"  h(q=2) = {result['hq'][7]:.4f}")
    print(f"  Delta alpha = {result['delta_alpha']:.4f}")

    print("\n=== MFDFA on binomial cascade (should be multifractal) ===")
    from synthetic_data import binomial_multifractal_cascade
    x_mf = binomial_multifractal_cascade(12, a=0.7, seed=42)
    result_mf = mfdfa(x_mf, order=1)
    print(f"  h(q=2) = {result_mf['hq'][7]:.4f}")
    print(f"  Delta alpha = {result_mf['delta_alpha']:.4f}")
