"""Network graph for electrical and photonic connectivity."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .config import NetworkParams, DemyelinationParams
from .waveguide import WaveguideModel


@dataclass
class PhotonicNetwork:
    n: int
    electrical: np.ndarray  # shape (n, n)
    photonic: np.ndarray  # shape (n, n)
    lengths_um: np.ndarray  # shape (n, n)

    @classmethod
    def random(cls, params: NetworkParams, rng: np.random.Generator) -> "PhotonicNetwork":
        n = params.n_neurons
        electrical = (rng.random((n, n)) < params.electrical_conn_prob).astype(float)
        np.fill_diagonal(electrical, 0.0)

        photonic = (rng.random((n, n)) < params.photonic_conn_prob).astype(float)
        photonic = np.triu(photonic, 1)
        photonic = photonic + photonic.T
        np.fill_diagonal(photonic, 0.0)

        # Random lengths between 100 and 2000 um for photonic links.
        lengths = rng.uniform(100.0, 2000.0, size=(n, n))
        lengths = (lengths + lengths.T) / 2.0
        np.fill_diagonal(lengths, 0.0)

        return cls(n=n, electrical=electrical, photonic=photonic, lengths_um=lengths)

    def photonic_weights(self, waveguide: WaveguideModel, demyelination: DemyelinationParams) -> np.ndarray:
        base = self.photonic.copy()
        if base.sum() == 0:
            return base
        coupling = waveguide.coupling_efficiency(demyelination)
        weights = np.zeros_like(base)
        for i in range(self.n):
            for j in range(self.n):
                if base[i, j] > 0:
                    path = waveguide.path_transmission(self.lengths_um[i, j], demyelination)
                    weights[i, j] = coupling * path * base[i, j]
        # Normalize rows to avoid exploding counts.
        row_sums = weights.sum(axis=1)
        for i in range(self.n):
            if row_sums[i] > 0:
                weights[i] /= row_sums[i]
        return weights
