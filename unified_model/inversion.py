"""Parameter inversion for demyelination state from spectra or counts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np

from models.axon import AxonGeometry
from models.demyelination import DemyelinationState
from models import emission as m_emission


@dataclass
class InversionResult:
    alpha: float
    gamma: float
    rho: float
    loss: float


def _spectrum_loss(target: np.ndarray, pred: np.ndarray) -> float:
    if target.size == 0 or pred.size == 0:
        return float("inf")
    t = target / (np.max(target) + 1e-12)
    p = pred / (np.max(pred) + 1e-12)
    return float(np.mean((t - p) ** 2))


def invert_spectrum(
    wavelengths_nm: np.ndarray,
    target_spectrum: np.ndarray,
    axon: AxonGeometry,
    grid: Iterable[float] = (0.0, 0.25, 0.5, 0.75, 1.0),
    wavelength_stride: int = 6,
) -> InversionResult:
    """Grid-search inversion for alpha/gamma/rho from a target spectrum."""
    best = InversionResult(0.0, 0.0, 0.0, float("inf"))
    if wavelength_stride > 1:
        wl = wavelengths_nm[::wavelength_stride]
        tgt = target_spectrum[::wavelength_stride]
    else:
        wl = wavelengths_nm
        tgt = target_spectrum
    for a in grid:
        for g in grid:
            for r in grid:
                state = DemyelinationState(alpha=a, gamma=g, rho=r)
                pred = m_emission.waveguide_filtered_emission(axon, state, wl)
                loss = _spectrum_loss(tgt, pred)
                if loss < best.loss:
                    best = InversionResult(a, g, r, loss)
    return best


def invert_spectrum_random(
    wavelengths_nm: np.ndarray,
    target_spectrum: np.ndarray,
    axon: AxonGeometry,
    n_samples: int = 200,
    refine_steps: int = 6,
    step_size: float = 0.1,
    wavelength_stride: int = 6,
    seed: int = 7,
) -> InversionResult:
    """Random + local refinement inversion on continuous parameters."""
    rng = np.random.default_rng(seed)
    if wavelength_stride > 1:
        wl = wavelengths_nm[::wavelength_stride]
        tgt = target_spectrum[::wavelength_stride]
    else:
        wl = wavelengths_nm
        tgt = target_spectrum

    def eval_state(a: float, g: float, r: float) -> float:
        state = DemyelinationState(alpha=a, gamma=g, rho=r)
        pred = m_emission.waveguide_filtered_emission(axon, state, wl)
        return _spectrum_loss(tgt, pred)

    best = InversionResult(0.0, 0.0, 0.0, float("inf"))
    for _ in range(n_samples):
        a, g, r = rng.random(3)
        loss = eval_state(a, g, r)
        if loss < best.loss:
            best = InversionResult(a, g, r, loss)

    # Coordinate refinement.
    a, g, r = best.alpha, best.gamma, best.rho
    for _ in range(refine_steps):
        improved = False
        for da, dg, dr in [
            (step_size, 0, 0),
            (-step_size, 0, 0),
            (0, step_size, 0),
            (0, -step_size, 0),
            (0, 0, step_size),
            (0, 0, -step_size),
        ]:
            aa = min(1.0, max(0.0, a + da))
            gg = min(1.0, max(0.0, g + dg))
            rr = min(1.0, max(0.0, r + dr))
            loss = eval_state(aa, gg, rr)
            if loss < best.loss:
                best = InversionResult(aa, gg, rr, loss)
                a, g, r = aa, gg, rr
                improved = True
        if not improved:
            step_size *= 0.5
    return best


def synthetic_target(
    wavelengths_nm: np.ndarray,
    axon: AxonGeometry,
    alpha: float,
    gamma: float,
    rho: float,
) -> np.ndarray:
    state = DemyelinationState(alpha=alpha, gamma=gamma, rho=rho)
    return m_emission.waveguide_filtered_emission(axon, state, wavelengths_nm)
