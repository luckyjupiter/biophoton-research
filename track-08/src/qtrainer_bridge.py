"""
QTrainerAI Bridge: 17 Methods Mapped to Biophoton Analysis

Maps each of the 17 QTrainerAI statistical methods to its biophoton
analysis counterpart. For each method, defines:
    1. What it computes on QRNG binary streams (MMI context)
    2. What it computes on photon count streams (biophoton context)
    3. The mathematical relationship between the two
    4. Implementation for biophoton data

The 17 methods (Scott directives, all calibrations = 1.0, no exclusions):
    mv, rwba, ac1, ac2, ra1-ra5, ca7, ca15, ca23, lzt, ks, m2, m3, m4

References:
    QTrainerAI codebase: quantum-dev:/home/quantum-dev/QTrainerAI/
    Scott's email directives (Jan-Feb 2026)
"""

import numpy as np
from scipy import stats as sp_stats
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .constants import (
    QTRAINER_METHODS,
    N_METHODS,
    METHOD_CALIBRATIONS,
    BU_OBS_HIT,
    BU_OBS_MISS,
    LIKELIHOOD_SR,
    INITIAL_PRIOR,
)


@dataclass
class MethodMapping:
    """Describes how a QTrainerAI method maps to biophoton analysis."""
    name: str
    qtrainer_description: str
    biophoton_description: str
    input_type_qrng: str
    input_type_biophoton: str
    relevant_tracks: List[str]
    transfer_quality: str  # "direct", "adapted", "analogous"


METHOD_MAPPINGS: Dict[str, MethodMapping] = {
    "mv": MethodMapping(
        name="mv",
        qtrainer_description="Majority Vote: counts hits in subtrial block",
        biophoton_description="Mandel Q parameter: (Var-Mean)/Mean; Q<0 = sub-Poissonian",
        input_type_qrng="binary block",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 01"],
        transfer_quality="adapted",
    ),
    "rwba": MethodMapping(
        name="rwba",
        qtrainer_description="Random Walk Bias Amplification: cumsum boundary crossing",
        biophoton_description="Cumulative photon deviation from expected rate",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ac1": MethodMapping(
        name="ac1",
        qtrainer_description="Autocorrelation lag-1: short-range temporal dependence",
        biophoton_description="Photon autocorrelation g^(1)(tau=1 bin)",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ac2": MethodMapping(
        name="ac2",
        qtrainer_description="Autocorrelation lag-2: next-nearest dependence",
        biophoton_description="Photon autocorrelation g^(1)(tau=2 bins)",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ra1": MethodMapping(
        name="ra1",
        qtrainer_description="Running Average window 1 (small): rapid bias onset",
        biophoton_description="3-bin moving average of count rate",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ra2": MethodMapping(
        name="ra2",
        qtrainer_description="Running Average window 2: medium-short",
        biophoton_description="5-bin moving average of count rate",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ra3": MethodMapping(
        name="ra3",
        qtrainer_description="Running Average window 3: medium",
        biophoton_description="10-bin moving average of count rate",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ra4": MethodMapping(
        name="ra4",
        qtrainer_description="Running Average window 4: medium-long",
        biophoton_description="20-bin moving average of count rate",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ra5": MethodMapping(
        name="ra5",
        qtrainer_description="Running Average window 5: long window",
        biophoton_description="50-bin moving average for slow drift detection",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ca7": MethodMapping(
        name="ca7",
        qtrainer_description="Cumulative Advantage w=7: persistent directional bias",
        biophoton_description="7-bin sliding window trend: short-scale emission buildup",
        input_type_qrng="binary blocks",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ca15": MethodMapping(
        name="ca15",
        qtrainer_description="Cumulative Advantage w=15",
        biophoton_description="15-bin sliding window trend: medium emission buildup",
        input_type_qrng="binary blocks",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "ca23": MethodMapping(
        name="ca23",
        qtrainer_description="Cumulative Advantage w=23",
        biophoton_description="23-bin sliding window trend: long emission buildup",
        input_type_qrng="binary blocks",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 02"],
        transfer_quality="direct",
    ),
    "lzt": MethodMapping(
        name="lzt",
        qtrainer_description="Lempel-Ziv complexity: algorithmic complexity of output",
        biophoton_description="LZ complexity of binarized photon stream; low = structured",
        input_type_qrng="binary stream",
        input_type_biophoton="binarized counts",
        relevant_tracks=["Track 02", "Track 05"],
        transfer_quality="adapted",
    ),
    "ks": MethodMapping(
        name="ks",
        qtrainer_description="Kolmogorov-Smirnov: distribution test, D_max statistic",
        biophoton_description="KS test of counts vs Poisson(mean); rejection = non-thermal",
        input_type_qrng="binary stream",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 01", "Track 05"],
        transfer_quality="direct",
    ),
    "m2": MethodMapping(
        name="m2",
        qtrainer_description="Method 2: secondary bias detection",
        biophoton_description="Fano factor F = Var/Mean; F<1 = sub-Poissonian",
        input_type_qrng="binary blocks",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 01"],
        transfer_quality="adapted",
    ),
    "m3": MethodMapping(
        name="m3",
        qtrainer_description="Method 3: tertiary bias detection",
        biophoton_description="g^(2)(0) estimate: bunching/antibunching measure",
        input_type_qrng="binary blocks",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 01", "Track 04"],
        transfer_quality="analogous",
    ),
    "m4": MethodMapping(
        name="m4",
        qtrainer_description="Method 4: quaternary bias detection",
        biophoton_description="Shannon entropy of count distribution vs Poisson entropy",
        input_type_qrng="binary blocks",
        input_type_biophoton="photon counts",
        relevant_tracks=["Track 01", "Track 05"],
        transfer_quality="adapted",
    ),
}


def apply_all_methods(
    counts: np.ndarray,
    expected_rate: Optional[float] = None,
) -> Dict[str, Dict]:
    """Apply all 17 biophoton-adapted methods to a photon count stream.

    Parameters
    ----------
    counts : np.ndarray
        Array of photon counts per time bin.
    expected_rate : float, optional
        Expected mean count rate. If None, estimated from data.

    Returns
    -------
    dict
        Method name -> {"observation": 0/1, "statistic": float, "description": str}.
    """
    if expected_rate is None:
        expected_rate = np.mean(counts)

    mean_n = np.mean(counts)
    var_n = np.var(counts, ddof=1) if len(counts) > 1 else mean_n
    results = {}

    # mv: Mandel Q
    Q = (var_n - mean_n) / mean_n if mean_n > 0 else 0.0
    results["mv"] = {
        "observation": BU_OBS_HIT if Q < 0 else BU_OBS_MISS,
        "statistic": Q,
        "description": f"Mandel Q = {Q:.4f}",
    }

    # rwba: Cumulative deviation
    cumsum = np.cumsum(counts - expected_rate)
    max_dev = np.max(np.abs(cumsum))
    threshold = 2.0 * np.sqrt(expected_rate * len(counts))
    ratio = max_dev / threshold if threshold > 0 else 0.0
    results["rwba"] = {
        "observation": BU_OBS_HIT if max_dev > threshold else BU_OBS_MISS,
        "statistic": ratio,
        "description": f"Deviation ratio = {ratio:.4f}",
    }

    # ac1, ac2
    for lag, method in [(1, "ac1"), (2, "ac2")]:
        ac = _autocorr(counts, lag) if len(counts) > lag else 0.0
        sig = 2.0 / np.sqrt(len(counts))
        results[method] = {
            "observation": BU_OBS_HIT if ac > sig else BU_OBS_MISS,
            "statistic": ac,
            "description": f"AC(lag={lag}) = {ac:.4f}",
        }

    # ra1-ra5
    for w, method in [(3, "ra1"), (5, "ra2"), (10, "ra3"), (20, "ra4"), (50, "ra5")]:
        if len(counts) >= w:
            running = np.convolve(counts, np.ones(w) / w, mode="valid")
            diffs = np.diff(running)
            frac = np.mean(diffs > 0) if len(diffs) > 0 else 0.5
        else:
            frac = 0.5
        results[method] = {
            "observation": BU_OBS_HIT if frac > 0.55 else BU_OBS_MISS,
            "statistic": frac,
            "description": f"Trend frac (w={w}) = {frac:.4f}",
        }

    # ca7, ca15, ca23
    for w, method in [(7, "ca7"), (15, "ca15"), (23, "ca23")]:
        if len(counts) >= 2 * w:
            blocks = [counts[j:j+w] for j in range(0, len(counts) - w + 1, w)]
            if len(blocks) >= 2:
                means = [np.mean(b) for b in blocks]
                slope = np.polyfit(range(len(means)), means, 1)[0]
            else:
                slope = 0.0
        else:
            slope = 0.0
        results[method] = {
            "observation": BU_OBS_HIT if slope > 0 else BU_OBS_MISS,
            "statistic": slope,
            "description": f"Block slope (w={w}) = {slope:.4f}",
        }

    # lzt: Lempel-Ziv
    binary = (counts > np.median(counts)).astype(int)
    lz = _lz_complexity(binary)
    lz_exp = len(counts) / np.log2(max(len(counts), 2))
    lz_ratio = lz / lz_exp if lz_exp > 0 else 1.0
    results["lzt"] = {
        "observation": BU_OBS_HIT if lz_ratio < 0.9 else BU_OBS_MISS,
        "statistic": lz_ratio,
        "description": f"LZ ratio = {lz_ratio:.4f}",
    }

    # ks: Kolmogorov-Smirnov
    if mean_n > 0:
        ks_stat, ks_p = sp_stats.kstest(
            counts, lambda x: sp_stats.poisson.cdf(x, mean_n)
        )
    else:
        ks_stat, ks_p = 0.0, 1.0
    results["ks"] = {
        "observation": BU_OBS_HIT if ks_p < 0.05 else BU_OBS_MISS,
        "statistic": ks_stat,
        "description": f"KS D={ks_stat:.4f}, p={ks_p:.4e}",
    }

    # m2: Fano factor
    fano = var_n / mean_n if mean_n > 0 else 1.0
    results["m2"] = {
        "observation": BU_OBS_HIT if fano < 0.95 else BU_OBS_MISS,
        "statistic": fano,
        "description": f"Fano F = {fano:.4f}",
    }

    # m3: g^(2)(0)
    if mean_n > 0 and len(counts) > 1:
        factorial_moment = np.mean(counts * (counts - 1))
        g2 = factorial_moment / (mean_n ** 2)
    else:
        g2 = 2.0
    results["m3"] = {
        "observation": BU_OBS_HIT if g2 < 1.0 else BU_OBS_MISS,
        "statistic": g2,
        "description": f"g^(2)(0) = {g2:.4f}",
    }

    # m4: Entropy
    if mean_n > 0 and len(counts) > 1:
        vals, freqs = np.unique(counts, return_counts=True)
        probs = freqs / freqs.sum()
        entropy = -np.sum(probs * np.log2(probs))
        poisson_ent = 0.5 * np.log2(2.0 * np.pi * np.e * mean_n)
    else:
        entropy, poisson_ent = 0.0, 0.0
    results["m4"] = {
        "observation": BU_OBS_HIT if entropy < poisson_ent else BU_OBS_MISS,
        "statistic": entropy,
        "description": f"H = {entropy:.4f} (Poisson ~ {poisson_ent:.4f})",
    }

    return results


def method_summary_table(results: Dict[str, Dict]) -> str:
    """Format method results as a text table."""
    lines = [f"{'Method':<8} {'Obs':>3} {'Statistic':>12} {'Description'}"]
    lines.append("-" * 70)
    for name in QTRAINER_METHODS:
        if name in results:
            r = results[name]
            obs = "HIT" if r["observation"] == BU_OBS_HIT else "   "
            lines.append(f"{name:<8} {obs:>3} {r['statistic']:>12.4f}  {r['description']}")
    n_hits = sum(1 for r in results.values() if r["observation"] == BU_OBS_HIT)
    lines.append("-" * 70)
    lines.append(f"Total hits: {n_hits}/{N_METHODS}")
    return "\n".join(lines)


def compute_combined_bu_from_methods(
    results: Dict[str, Dict],
    prior: float = INITIAL_PRIOR,
    sr: float = LIKELIHOOD_SR,
) -> Tuple[float, List[float]]:
    """Compute combined BU posterior from method results."""
    from .bayesian_coherence import bayesian_update_single
    current = prior
    history = []
    for name in QTRAINER_METHODS:
        if name in results:
            obs = results[name]["observation"]
            current = bayesian_update_single(current, obs, sr)
            history.append(current)
    return current, history


def _autocorr(x: np.ndarray, lag: int) -> float:
    n = len(x)
    if n <= lag:
        return 0.0
    m = np.mean(x)
    v = np.var(x)
    if v == 0:
        return 0.0
    return np.mean((x[:n-lag] - m) * (x[lag:] - m)) / v


def _lz_complexity(seq: np.ndarray) -> int:
    s = "".join(str(int(b)) for b in seq)
    n = len(s)
    if n == 0:
        return 0
    c, i, plen = 1, 0, 1
    while i + plen <= n:
        sub = s[i+1:i+plen+1]
        if sub in s[:i+plen]:
            plen += 1
            if i + plen > n:
                break
        else:
            c += 1
            i = i + plen
            plen = 1
    return c


if __name__ == "__main__":
    print("=== QTrainerAI Bridge: 17-Method Biophoton Analysis ===\n")
    rng = np.random.default_rng(42)

    print("--- Thermal (Poisson, mean=50) ---")
    thermal = rng.poisson(50, size=200)
    res_t = apply_all_methods(thermal)
    print(method_summary_table(res_t))
    post_t, _ = compute_combined_bu_from_methods(res_t)
    print(f"\nCombined BU posterior: {post_t:.4f}\n")

    print("--- Sub-Poissonian (binomial, mean~50, F~0.9) ---")
    coherent = rng.binomial(500, 0.1, size=200)
    res_c = apply_all_methods(coherent)
    print(method_summary_table(res_c))
    post_c, _ = compute_combined_bu_from_methods(res_c)
    print(f"\nCombined BU posterior: {post_c:.4f}\n")

    print("=== Method Mapping Catalog ===\n")
    for name in QTRAINER_METHODS:
        m = METHOD_MAPPINGS[name]
        print(f"[{name}] Transfer: {m.transfer_quality}")
        print(f"  QRNG:      {m.qtrainer_description}")
        print(f"  Biophoton: {m.biophoton_description}")
        print(f"  Tracks:    {', '.join(m.relevant_tracks)}")
        print()
