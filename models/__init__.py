"""
Biophoton Demyelination Simulator

Models biophoton emission from healthy vs. demyelinated neural tissue,
simulates what experiments would measure, and provides diagnostic
classification tools.

Key classes:
    AxonGeometry       — myelinated axon as optical waveguide
    WaveguideModel     — light propagation through myelin sheath
    DemyelinationState — three-axis disease parameterization
    EmissionModel      — biophoton generation and filtering
    Detector           — photon detector with realistic noise
"""

from .axon import AxonGeometry
from .demyelination import DemyelinationState
from .detection import Detector
from .emission import (
    compute_feature_vector,
    disease_emission,
    ros_spectrum,
    waveguide_filtered_emission,
)
from .waveguide import (
    arrow_wavelengths,
    propagate_multi_node,
    sefati_zeng_peak,
    transfer_matrix_transmission,
)

__all__ = [
    "AxonGeometry",
    "DemyelinationState",
    "Detector",
    "compute_feature_vector",
    "disease_emission",
    "ros_spectrum",
    "waveguide_filtered_emission",
    "arrow_wavelengths",
    "propagate_multi_node",
    "sefati_zeng_peak",
    "transfer_matrix_transmission",
]
