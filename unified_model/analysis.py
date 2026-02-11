"""Analysis utilities for simulation outputs."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

import numpy as np

from .engine import SimulationResult


def fano_factor(counts: np.ndarray) -> float:
    mean = np.mean(counts)
    if mean <= 0:
        return 0.0
    return float(np.var(counts) / mean)


def g2_zero(counts: np.ndarray) -> float:
    """Estimate g2(0) from count time series (naive estimator)."""
    mean = np.mean(counts)
    if mean <= 0:
        return 0.0
    return float(np.mean(counts * counts) / (mean * mean))


def summarize(result: SimulationResult) -> Dict[str, float]:
    emitted = result.totals["total_emitted"]
    received = result.totals["total_received"]
    det = result.detected_counts if result.detected_counts.size > 0 else np.array([0.0])
    return {
        "mean_emitted": float(np.mean(emitted)),
        "mean_received": float(np.mean(received)),
        "fano_emitted": fano_factor(emitted),
        "g2_emitted": g2_zero(emitted),
        "fano_received": fano_factor(received),
        "g2_received": g2_zero(received),
        "mean_detected": float(np.mean(det)),
        "fano_detected": fano_factor(det),
    }


def roc_auc(scores_pos: Iterable[float], scores_neg: Iterable[float]) -> float:
    pos = np.asarray(list(scores_pos), dtype=float)
    neg = np.asarray(list(scores_neg), dtype=float)
    if len(pos) == 0 or len(neg) == 0:
        return 0.0
    # Mann-Whitney U for AUC.
    ranks = np.argsort(np.concatenate([pos, neg]))
    combined = np.concatenate([pos, neg])
    order = np.argsort(combined)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(combined)) + 1
    r_pos = np.sum(ranks[: len(pos)])
    u = r_pos - len(pos) * (len(pos) + 1) / 2
    auc = u / (len(pos) * len(neg))
    return float(auc)
