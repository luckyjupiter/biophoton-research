#!/usr/bin/env python3
"""Recurrence Quantification Analysis (RQA) for biophoton point processes.

Implements phase space reconstruction, recurrence plot computation, and
the standard RQA metrics: recurrence rate, determinism, laminarity,
trapping time, entropy of diagonal lines, and average diagonal line length.

Adapted for ultra-low count rate data with integer-valued time series.

References
----------
- Eckmann JP, Kamphorst SO, Ruelle D, Europhys. Lett. 4(9): 973 (1987)
- Marwan N et al., Physics Reports 438(5-6): 237-329 (2007)
- Belksma R, Master's thesis, Utrecht University (2024)
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from typing import Optional, Tuple


def mutual_information(x: np.ndarray, max_lag: int = 50,
                       n_bins: int = 16) -> Tuple[np.ndarray, int]:
    """Estimate time-delayed mutual information to choose embedding delay.

    The optimal delay tau is the first local minimum of the mutual
    information function I(tau).

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    max_lag : int
        Maximum lag to compute.
    n_bins : int
        Number of histogram bins for probability estimation.

    Returns
    -------
    mi : np.ndarray
        Mutual information at each lag 0..max_lag.
    tau : int
        Optimal delay (first local minimum), or max_lag//4 if no minimum found.
    """
    N = len(x)
    mi = np.zeros(max_lag + 1)

    # Bin edges for the marginal distribution
    edges = np.linspace(np.min(x) - 1e-10, np.max(x) + 1e-10, n_bins + 1)

    for lag in range(max_lag + 1):
        if lag >= N:
            mi[lag] = 0
            continue

        x1 = x[:N - lag] if lag > 0 else x
        x2 = x[lag:] if lag > 0 else x

        # Joint histogram
        joint_hist, _, _ = np.histogram2d(x1, x2, bins=[edges, edges])
        joint_hist = joint_hist / np.sum(joint_hist)

        # Marginals
        px = np.sum(joint_hist, axis=1)
        py = np.sum(joint_hist, axis=0)

        # Mutual information
        mi_val = 0.0
        for i in range(n_bins):
            for j in range(n_bins):
                if joint_hist[i, j] > 0 and px[i] > 0 and py[j] > 0:
                    mi_val += joint_hist[i, j] * np.log2(
                        joint_hist[i, j] / (px[i] * py[j])
                    )
        mi[lag] = mi_val

    # Find first local minimum
    tau = max_lag // 4  # default
    for lag in range(1, max_lag - 1):
        if mi[lag] < mi[lag - 1] and mi[lag] <= mi[lag + 1]:
            tau = lag
            break

    return mi, tau


def false_nearest_neighbors(x: np.ndarray, tau: int,
                            max_dim: int = 10,
                            threshold: float = 10.0) -> Tuple[np.ndarray, int]:
    """False nearest neighbors algorithm for embedding dimension selection.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    tau : int
        Embedding delay.
    max_dim : int
        Maximum embedding dimension to test.
    threshold : float
        Distance ratio threshold for declaring a false neighbor.

    Returns
    -------
    fnn_fraction : np.ndarray
        Fraction of false nearest neighbors at each dimension 1..max_dim.
    m : int
        Optimal embedding dimension (where FNN fraction drops below 0.05).
    """
    N = len(x)
    fnn_fraction = np.zeros(max_dim)

    for dim in range(1, max_dim + 1):
        n_embed = N - (dim) * tau
        if n_embed < 10:
            fnn_fraction[dim - 1] = 1.0
            continue

        # Embed in dimension dim
        embedded = np.zeros((n_embed, dim))
        for d in range(dim):
            embedded[:, d] = x[d * tau:d * tau + n_embed]

        n_false = 0
        n_total = 0

        # For efficiency, use a random subsample for large N
        n_check = min(n_embed - 1, 500)
        indices = np.random.choice(n_embed, n_check, replace=False)

        for idx in indices:
            point = embedded[idx]
            # Find nearest neighbor (excluding self)
            dists = np.sqrt(np.sum((embedded - point) ** 2, axis=1))
            dists[idx] = np.inf
            nn_idx = np.argmin(dists)
            d_m = dists[nn_idx]

            if d_m < 1e-12:
                continue

            n_total += 1

            # Check if the neighbor is false by extending to dim+1
            if dim * tau + idx < N and dim * tau + nn_idx < N:
                extra_dist = abs(x[dim * tau + idx] - x[dim * tau + nn_idx])
                ratio = extra_dist / d_m
                if ratio > threshold:
                    n_false += 1

        fnn_fraction[dim - 1] = n_false / max(n_total, 1)

    # Find optimal dimension
    m = max_dim
    for dim in range(1, max_dim + 1):
        if fnn_fraction[dim - 1] < 0.05:
            m = dim
            break

    return fnn_fraction, m


def embed_time_series(x: np.ndarray, m: int, tau: int) -> np.ndarray:
    """Construct delay embedding vectors.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    m : int
        Embedding dimension.
    tau : int
        Embedding delay.

    Returns
    -------
    np.ndarray, shape (N - (m-1)*tau, m)
        Delay embedding matrix.
    """
    N = len(x)
    n_vectors = N - (m - 1) * tau
    embedded = np.zeros((n_vectors, m))
    for d in range(m):
        embedded[:, d] = x[d * tau:d * tau + n_vectors]
    return embedded


def recurrence_matrix(embedded: np.ndarray, epsilon: float,
                      metric: str = 'chebyshev') -> np.ndarray:
    """Compute the recurrence matrix.

    Parameters
    ----------
    embedded : np.ndarray, shape (N, m)
        Delay-embedded vectors.
    epsilon : float
        Recurrence threshold distance.
    metric : str
        Distance metric ('euclidean' or 'chebyshev').
        Chebyshev is recommended for discrete photon count data.

    Returns
    -------
    np.ndarray, shape (N, N)
        Binary recurrence matrix.
    """
    if metric == 'chebyshev':
        dists = squareform(pdist(embedded, metric='chebyshev'))
    else:
        dists = squareform(pdist(embedded, metric='euclidean'))

    R = (dists <= epsilon).astype(int)
    # Remove the main diagonal (self-recurrence)
    np.fill_diagonal(R, 0)
    return R


def rqa_metrics(R: np.ndarray, l_min: int = 2,
                v_min: int = 2) -> dict:
    """Compute recurrence quantification analysis metrics.

    Parameters
    ----------
    R : np.ndarray
        Binary recurrence matrix.
    l_min : int
        Minimum diagonal line length.
    v_min : int
        Minimum vertical line length.

    Returns
    -------
    dict with keys:
        'RR': Recurrence rate
        'DET': Determinism
        'L': Average diagonal line length
        'L_max': Maximum diagonal line length
        'ENTR': Entropy of diagonal line length distribution
        'LAM': Laminarity
        'TT': Trapping time
        'V_max': Maximum vertical line length
    """
    N = R.shape[0]
    total_recurrence = np.sum(R)

    # Recurrence rate
    RR = total_recurrence / (N * (N - 1)) if N > 1 else 0

    # Diagonal line lengths
    diag_lengths = _extract_diagonal_lines(R)

    # Filter by minimum length
    diag_long = diag_lengths[diag_lengths >= l_min]

    # Determinism
    if total_recurrence > 0:
        DET = np.sum(diag_long) / total_recurrence
    else:
        DET = 0

    # Average diagonal line length
    if len(diag_long) > 0:
        L = np.mean(diag_long)
        L_max = np.max(diag_long)
    else:
        L = 0
        L_max = 0

    # Entropy of diagonal line distribution
    if len(diag_long) > 0:
        # Histogram of line lengths
        unique_lengths, counts = np.unique(diag_long, return_counts=True)
        probs = counts / np.sum(counts)
        ENTR = -np.sum(probs * np.log(probs + 1e-12))
    else:
        ENTR = 0

    # Vertical line lengths
    vert_lengths = _extract_vertical_lines(R)
    vert_long = vert_lengths[vert_lengths >= v_min]

    # Laminarity
    if total_recurrence > 0:
        LAM = np.sum(vert_long) / total_recurrence
    else:
        LAM = 0

    # Trapping time
    if len(vert_long) > 0:
        TT = np.mean(vert_long)
        V_max = np.max(vert_long)
    else:
        TT = 0
        V_max = 0

    return {
        'RR': RR,
        'DET': DET,
        'L': L,
        'L_max': int(L_max),
        'ENTR': ENTR,
        'LAM': LAM,
        'TT': TT,
        'V_max': int(V_max),
    }


def _extract_diagonal_lines(R: np.ndarray) -> np.ndarray:
    """Extract lengths of all diagonal lines in the recurrence matrix.

    Scans all diagonals (above the main diagonal) for consecutive runs of 1s.
    """
    N = R.shape[0]
    lengths = []

    for k in range(1, N):
        diag = np.diag(R, k)
        current_length = 0
        for val in diag:
            if val == 1:
                current_length += 1
            else:
                if current_length > 0:
                    lengths.append(current_length)
                current_length = 0
        if current_length > 0:
            lengths.append(current_length)

    return np.array(lengths) if lengths else np.array([0])


def _extract_vertical_lines(R: np.ndarray) -> np.ndarray:
    """Extract lengths of all vertical lines in the recurrence matrix."""
    N = R.shape[0]
    lengths = []

    for j in range(N):
        col = R[:, j]
        current_length = 0
        for val in col:
            if val == 1:
                current_length += 1
            else:
                if current_length > 0:
                    lengths.append(current_length)
                current_length = 0
        if current_length > 0:
            lengths.append(current_length)

    return np.array(lengths) if lengths else np.array([0])


def _select_epsilon(embedded: np.ndarray, target_rr: float = 0.03,
                    metric: str = 'chebyshev') -> float:
    """Select epsilon to achieve a target recurrence rate.

    Uses the distribution of pairwise distances from a subsample to estimate
    the quantile corresponding to the desired recurrence rate.

    Parameters
    ----------
    embedded : np.ndarray
        Delay-embedded vectors.
    target_rr : float
        Target recurrence rate (default 3%).
    metric : str
        Distance metric.

    Returns
    -------
    float
        Estimated epsilon.
    """
    n = min(len(embedded), 300)
    idx = np.random.choice(len(embedded), n, replace=False)
    sample_dists = pdist(embedded[idx], metric=metric)
    epsilon = np.quantile(sample_dists, target_rr)
    return max(epsilon, 1e-10)


def full_rqa_analysis(x: np.ndarray, epsilon: Optional[float] = None,
                      target_rr: float = 0.03,
                      metric: str = 'chebyshev',
                      max_dim: int = 10) -> dict:
    """Complete RQA analysis with automatic parameter selection.

    Determines embedding parameters (tau, m) automatically, selects epsilon
    to target a recurrence rate of ~3%, and computes all RQA metrics.

    Parameters
    ----------
    x : np.ndarray
        Input time series.
    epsilon : float, optional
        Recurrence threshold. If None, selected to achieve target_rr.
    target_rr : float
        Target recurrence rate for automatic epsilon selection.
    metric : str
        Distance metric ('chebyshev' recommended for discrete data).
    max_dim : int
        Maximum embedding dimension to test.

    Returns
    -------
    dict with all RQA metrics plus embedding parameters.
    """
    # Determine embedding parameters
    mi, tau = mutual_information(x, max_lag=min(50, len(x) // 5))
    fnn, m = false_nearest_neighbors(x, tau, max_dim=max_dim)

    # Ensure reasonable values
    tau = max(tau, 1)
    m = max(m, 2)

    # Embed
    embedded = embed_time_series(x, m, tau)

    # Set epsilon to achieve target recurrence rate
    if epsilon is None:
        epsilon = _select_epsilon(embedded, target_rr=target_rr, metric=metric)

    # Compute recurrence matrix
    R = recurrence_matrix(embedded, epsilon, metric=metric)

    # Compute metrics
    metrics = rqa_metrics(R)
    metrics['tau'] = tau
    metrics['m'] = m
    metrics['epsilon'] = epsilon
    metrics['N_embedded'] = len(embedded)

    return metrics


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/yesh/biophoton-research/worktrees/track-02/src')
    from synthetic_data import (fgn_davies_harte, poisson_homogeneous,
                                 correlated_poisson, poisson_modulated)

    print("=== RQA on correlated fGn (H=0.7) ===")
    x_corr = fgn_davies_harte(1024, 0.7, seed=42)
    result = full_rqa_analysis(x_corr)
    for k, v in result.items():
        print(f"  {k:15s}: {v}")

    print("\n=== RQA on white noise (H=0.5) ===")
    x_white = fgn_davies_harte(1024, 0.5, seed=42)
    result_white = full_rqa_analysis(x_white)
    for k, v in result_white.items():
        print(f"  {k:15s}: {v}")

    print("\n=== RQA on Poisson process ===")
    x_pois = poisson_homogeneous(1024, rate=10.0, seed=42)
    result_pois = full_rqa_analysis(x_pois)
    for k, v in result_pois.items():
        print(f"  {k:15s}: {v}")

    print("\n=== RQA on modulated Poisson (periodic structure) ===")
    x_mod = poisson_modulated(1024, base_rate=10.0, modulation_depth=0.8,
                               modulation_period=50, seed=42)
    result_mod = full_rqa_analysis(x_mod)
    for k, v in result_mod.items():
        print(f"  {k:15s}: {v}")
