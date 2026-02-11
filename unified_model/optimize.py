"""Experiment design optimization for detector and schedule selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np

from models.axon import AxonGeometry
from models.demyelination import DemyelinationState, cuprizone_timeline
from models import emission as m_emission
from models import detection as m_detection
from models import constants as MC


@dataclass
class DesignResult:
    detector: str
    exposure_s: float
    area_cm2: float
    score: float


def _cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    va = np.var(a, ddof=1) if a.size > 1 else 0.0
    vb = np.var(b, ddof=1) if b.size > 1 else 0.0
    pooled = np.sqrt((va + vb) / 2.0) if (va + vb) > 0 else 1.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def evaluate_design(
    detector_name: str,
    exposure_s: float,
    area_cm2: float,
    weeks: Iterable[float],
    axon: AxonGeometry,
    wavelengths_nm: np.ndarray,
    n_measurements: int = 20,
    seed: int = 7,
) -> float:
    rng = np.random.default_rng(seed)
    detector = m_detection.Detector.from_name(detector_name)

    # Healthy baseline (week 0)
    healthy_state = DemyelinationState(alpha=0.0, gamma=0.0, rho=0.0)
    healthy_spec = m_emission.waveguide_filtered_emission(axon, healthy_state, wavelengths_nm)
    healthy_rate = float(np.trapezoid(healthy_spec, wavelengths_nm)) * area_cm2
    healthy_counts = m_detection.simulate_counts(
        healthy_rate,
        detector,
        exposure_s,
        n_measurements=n_measurements,
        rng=rng,
    )

    scores = []
    for week in weeks:
        state = cuprizone_timeline(week)
        diseased_spec = m_emission.waveguide_filtered_emission(axon, state, wavelengths_nm)
        diseased_rate = float(np.trapezoid(diseased_spec, wavelengths_nm)) * area_cm2
        diseased_counts = m_detection.simulate_counts(
            diseased_rate,
            detector,
            exposure_s,
            n_measurements=n_measurements,
            rng=rng,
        )
        scores.append(abs(_cohen_d(diseased_counts, healthy_counts)))

    return float(np.mean(scores)) if scores else 0.0


def optimize_design(
    detectors: Iterable[str] = ("PMT", "EMCCD", "SPAD", "SNSPD"),
    exposures_s: Iterable[float] = (1.0, 5.0, 10.0, 30.0),
    area_cm2: float = 1.0,
    weeks: Iterable[float] = (1, 3, 5, 7, 10),
    n_measurements: int = 20,
) -> DesignResult:
    axon = AxonGeometry.typical_cns()
    lam = MC.DEFAULT_LAMBDA_RANGE_NM

    best = DesignResult(detector="PMT", exposure_s=1.0, area_cm2=area_cm2, score=-1.0)
    for det in detectors:
        for exp in exposures_s:
            score = evaluate_design(
                detector_name=det,
                exposure_s=exp,
                area_cm2=area_cm2,
                weeks=weeks,
                axon=axon,
                wavelengths_nm=lam,
                n_measurements=n_measurements,
            )
            if score > best.score:
                best = DesignResult(detector=det, exposure_s=exp, area_cm2=area_cm2, score=score)
    return best
