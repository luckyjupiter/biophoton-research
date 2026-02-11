"""Simulation engine linking molecular emission, waveguide transport, and network dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from .config import SimulationConfig
from .molecular import MolecularROSModel
from .waveguide import WaveguideModel
from .network import PhotonicNetwork
from models.axon import AxonGeometry
from models.demyelination import DemyelinationState
from models import emission as m_emission
from models import waveguide as m_waveguide
from models import detection as m_detection


@dataclass
class SimulationResult:
    times_ms: np.ndarray
    spikes: np.ndarray  # shape (T, N)
    metabolic: np.ndarray  # shape (T, N)
    emitted: np.ndarray  # shape (T, N)
    received: np.ndarray  # shape (T, N)
    detected_counts: np.ndarray  # shape (n_measurements,)
    spectrum: np.ndarray  # leaked spectrum shape (len(wavelengths),)
    guided_spectrum: np.ndarray  # guided spectrum shape (len(wavelengths),)
    received_spectrum: np.ndarray  # received spectrum estimate
    features: Dict[str, float]
    totals: Dict[str, np.ndarray]


class SimulationEngine:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.molecular = MolecularROSModel(config.molecular)
        self.waveguide = WaveguideModel(config.axon)
        self.network = PhotonicNetwork.random(config.network, self.rng)
        self.axon_geo = AxonGeometry(
            diameter_um=config.axon.diameter_um,
            g_ratio=config.axon.g_ratio,
        )
        self.detector = m_detection.Detector.from_name(config.detector_name)

    def run(self) -> SimulationResult:
        cfg = self.config
        n = cfg.network.n_neurons
        steps = int(cfg.duration_ms / cfg.dt_ms)
        times = np.arange(0, steps) * cfg.dt_ms

        spikes = np.zeros((steps, n), dtype=float)
        metabolic = np.zeros((steps, n), dtype=float)
        emitted = np.zeros((steps, n), dtype=float)
        received = np.zeros((steps, n), dtype=float)

        weights = self.network.photonic_weights(self.waveguide, cfg.demyelination)

        # Baseline spiking rate (Hz) and photonic coupling.
        base_spike_hz = 5.0
        photonic_gain = 0.15

        m = np.zeros(n, dtype=float)
        phot_in = np.zeros(n, dtype=float)

        # Spectrally resolved propagation: compute guided vs leaked fractions.
        dem_state = DemyelinationState(
            alpha=cfg.demyelination.thickness_loss,
            gamma=cfg.demyelination.continuity_loss,
            rho=cfg.demyelination.irregularity,
        )
        lam = cfg.wavelengths_nm
        source_spec = m_emission.disease_emission(dem_state, lam)
        effective_wraps = dem_state.effective_wraps(self.axon_geo.n_wraps)
        if effective_wraps > 0:
            t_guided = m_waveguide.transfer_matrix_transmission(
                self.axon_geo,
                lam,
                n_wraps_override=effective_wraps,
            )
        else:
            t_guided = np.zeros_like(lam)
        atten = m_waveguide.attenuation_db_per_cm(lam)
        propagation_factor = 10 ** (-atten * 0.1 / 10)  # 0.1 cm default path
        guided_spec = source_spec * t_guided * propagation_factor
        leaked_spec = m_emission.waveguide_filtered_emission(
            self.axon_geo,
            dem_state,
            lam,
        )
        guided_intensity = float(np.trapezoid(guided_spec, lam))
        leaked_intensity = float(np.trapezoid(leaked_spec, lam))
        total_intensity = max(guided_intensity + leaked_intensity, 1e-12)
        guided_fraction = guided_intensity / total_intensity

        # Scale photonic coupling by guided fraction and demyelination continuity.
        photonic_gain *= (0.25 + 0.75 * guided_fraction) * (1.0 - cfg.demyelination.continuity_loss)
        weights = weights * (0.25 + 0.75 * guided_fraction)

        for t in range(steps):
            # Spiking: Poisson with rate influenced by photonic input.
            rate_hz = base_spike_hz * (1.0 + photonic_gain * phot_in)
            spike_prob = np.clip(rate_hz * (cfg.dt_ms / 1000.0), 0.0, 0.9)
            spk = self.rng.random(n) < spike_prob
            spikes[t] = spk.astype(float)

            # Metabolic state low-pass of spiking.
            tau = cfg.molecular.metabolic_tau_ms
            m += (cfg.dt_ms / tau) * (spk.astype(float) - m)
            metabolic[t] = m

            # Emission per neuron.
            rates = np.array([self.molecular.emission_rate_hz(mi) for mi in m])
            emit_counts = self.rng.poisson(rates * (cfg.dt_ms / 1000.0))
            emitted[t] = emit_counts

            # Photonic propagation: Poisson per edge.
            recv = np.zeros(n, dtype=float)
            if weights.sum() > 0:
                for i in range(n):
                    if emit_counts[i] <= 0:
                        continue
                    w = weights[i]
                    if w.sum() <= 0:
                        continue
                    # Expected counts per neighbor.
                    lam = emit_counts[i] * w
                    recv += self.rng.poisson(lam)

            received[t] = recv
            phot_in = recv

        if cfg.use_full_stack:
            spectrum = leaked_spec
            features = m_emission.compute_feature_vector(
                self.axon_geo,
                dem_state,
                cfg.wavelengths_nm,
                rng=self.rng,
            )
            # Integrated signal rate scaled by collection area.
            signal_rate_hz = float(np.trapezoid(spectrum, cfg.wavelengths_nm)) * cfg.detector_area_cm2
            detected_counts = m_detection.simulate_counts(
                signal_rate_hz=signal_rate_hz,
                detector=self.detector,
                exposure_s=cfg.exposure_s,
                n_measurements=cfg.n_measurements,
                rng=self.rng,
            )
        else:
            spectrum = np.zeros_like(cfg.wavelengths_nm, dtype=float)
            features = {}
            detected_counts = np.zeros(cfg.n_measurements, dtype=float)

        totals = {
            "total_emitted": emitted.sum(axis=1),
            "total_received": received.sum(axis=1),
            "mean_metabolic": metabolic.mean(axis=1),
            "total_spikes": spikes.sum(axis=1),
        }
        total_emitted_photons = float(emitted.sum())
        total_received_photons = float(received.sum())
        if guided_intensity > 0 and total_emitted_photons > 0:
            receive_scale = total_received_photons / (total_emitted_photons * guided_fraction + 1e-12)
            received_spectrum = guided_spec * max(receive_scale, 0.0)
        else:
            received_spectrum = np.zeros_like(lam, dtype=float)

        return SimulationResult(
            times_ms=times,
            spikes=spikes,
            metabolic=metabolic,
            emitted=emitted,
            received=received,
            detected_counts=detected_counts,
            spectrum=spectrum,
            guided_spectrum=guided_spec,
            received_spectrum=received_spectrum,
            features=features,
            totals=totals,
        )
