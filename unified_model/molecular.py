"""Molecular biophoton generation model (ROS-driven)."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from .config import MolecularParams


@dataclass
class MolecularROSModel:
    params: MolecularParams

    def emission_rate_hz(self, metabolic_state: float) -> float:
        """Photon emission rate per neuron given metabolic state [0..1]."""
        m = max(0.0, min(1.0, metabolic_state))
        return self.params.baseline_rate_hz * (1.0 + self.params.ros_burst_gain * m)

    def spectrum(self, wavelengths_nm: Iterable[float]) -> np.ndarray:
        """Return normalized spectral density for given wavelengths."""
        wl = np.asarray(wavelengths_nm, dtype=float)

        def gauss(mu, sigma, weight):
            return weight * np.exp(-0.5 * ((wl - mu) / sigma) ** 2)

        # Components inspired by track 07: carbonyls, singlet O2, pigments.
        s = (
            gauss(430, 40, 0.45) +
            gauss(520, 60, 0.25) +
            gauss(634, 15, 0.10) +
            gauss(703, 18, 0.08) +
            gauss(760, 45, 0.08) +
            gauss(1270, 25, 0.04)
        )
        s = np.where(wl > 0, s, 0.0)
        total = np.trapz(s, wl)
        if total <= 0:
            return np.zeros_like(wl)
        return s / total

    def sample_photons(self, rate_hz: float, dt_ms: float, rng: np.random.Generator) -> int:
        """Poisson sampling of photons in a timestep."""
        lam = max(0.0, rate_hz) * (dt_ms / 1000.0)
        return int(rng.poisson(lam))
