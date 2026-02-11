"""Configuration structures for the unified simulation."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from models import constants as MC


@dataclass(frozen=True)
class AxonParams:
    n_myelin: float = 1.44
    n_axon: float = 1.38
    n_ecf: float = 1.34
    g_ratio: float = 0.7
    diameter_um: float = 1.0
    bilayer_thickness_nm: float = 10.0
    internode_length_um: float = 200.0


@dataclass(frozen=True)
class DemyelinationParams:
    thickness_loss: float = 0.0  # 0..1
    continuity_loss: float = 0.0  # gap probability
    irregularity: float = 0.0  # variance in layer thickness


@dataclass(frozen=True)
class MolecularParams:
    baseline_rate_hz: float = 50.0  # photons/s per neuron
    ros_burst_gain: float = 2.5
    metabolic_tau_ms: float = 200.0
    emission_tau_ms: float = 50.0
    spectrum_min_nm: float = 300.0
    spectrum_max_nm: float = 900.0


@dataclass(frozen=True)
class NetworkParams:
    n_neurons: int = 64
    electrical_conn_prob: float = 0.08
    photonic_conn_prob: float = 0.12
    base_photonic_weight: float = 0.15


@dataclass(frozen=True)
class SimulationConfig:
    dt_ms: float = 1.0
    duration_ms: int = 2000
    seed: int = 7
    axon: AxonParams = AxonParams()
    demyelination: DemyelinationParams = DemyelinationParams()
    molecular: MolecularParams = MolecularParams()
    network: NetworkParams = NetworkParams()
    wavelengths_nm: np.ndarray = field(default_factory=lambda: MC.DEFAULT_LAMBDA_RANGE_NM.copy())
    detector_name: str = "PMT"
    exposure_s: float = 10.0
    detector_area_cm2: float = 1.0
    n_measurements: int = 10
    use_full_stack: bool = True
