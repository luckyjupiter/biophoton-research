"""Experiment scaffolding for demyelination studies."""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

import numpy as np

from .config import DemyelinationParams, SimulationConfig
from .engine import SimulationEngine, SimulationResult
from models import demyelination as m_demy


def cuprizone_timeline(week: float) -> DemyelinationParams:
    """Cuprizone demyelination trajectory (from models.demyelination)."""
    state = m_demy.cuprizone_timeline(week)
    return DemyelinationParams(
        thickness_loss=state.alpha,
        continuity_loss=state.gamma,
        irregularity=state.rho,
    )


def run_condition(config: SimulationConfig, demyelination: DemyelinationParams) -> SimulationResult:
    cfg = replace(config, demyelination=demyelination)
    engine = SimulationEngine(cfg)
    return engine.run()


def demyelination_sweep(config: SimulationConfig, levels: List[float]) -> Dict[float, SimulationResult]:
    results: Dict[float, SimulationResult] = {}
    for level in levels:
        dem = DemyelinationParams(thickness_loss=level, continuity_loss=0.1 + 0.5 * level, irregularity=0.2 + 0.5 * level)
        results[level] = run_condition(config, dem)
    return results


def cuprizone_series(config: SimulationConfig, weeks: List[float]) -> Dict[float, SimulationResult]:
    results: Dict[float, SimulationResult] = {}
    for week in weeks:
        dem = cuprizone_timeline(week)
        results[week] = run_condition(config, dem)
    return results
