"""Waveguide transmission model (simplified ARROW + loss)."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from .config import AxonParams, DemyelinationParams


@dataclass
class WaveguideModel:
    axon: AxonParams

    def _arrow_wavelength_nm(self, demyelination: DemyelinationParams) -> float:
        # Base ARROW anti-resonance wavelength from layer thickness.
        d_nm = self.axon.bilayer_thickness_nm
        n_clad = self.axon.n_myelin
        n_core = self.axon.n_axon
        base = (2 * d_nm) * math.sqrt(max(n_clad ** 2 - n_core ** 2, 0.0))
        # Adjust for thickness loss: each layer lost blueshifts by ~52.3 nm (Track 06).
        layers_lost = 40 * max(0.0, min(1.0, demyelination.thickness_loss))
        return max(250.0, base - 52.3 * layers_lost)

    def transmission(self, wavelengths_nm: Iterable[float], demyelination: DemyelinationParams) -> np.ndarray:
        wl = np.asarray(wavelengths_nm, dtype=float)
        peak = self._arrow_wavelength_nm(demyelination)
        # Narrow passband ~10 nm in healthy tissue; broaden with irregularity.
        sigma = 5.0 + 25.0 * demyelination.irregularity
        band = np.exp(-0.5 * ((wl - peak) / sigma) ** 2)
        # Apply continuity loss as multiplicative attenuation.
        continuity = 1.0 - demyelination.continuity_loss
        return np.clip(band * continuity, 0.0, 1.0)

    def coupling_efficiency(self, demyelination: DemyelinationParams) -> float:
        # Simple coupling loss from demyelination.
        base = 0.18
        return max(0.01, base * (1.0 - 0.7 * demyelination.thickness_loss))

    def path_transmission(self, length_um: float, demyelination: DemyelinationParams) -> float:
        # Exponential loss per cm: 4-40 dB/cm -> alpha ~0.92-9.2 1/cm
        alpha_cm = 0.92 + 8.3 * demyelination.thickness_loss
        length_cm = max(0.0, length_um) * 1e-4
        return math.exp(-alpha_cm * length_cm)
