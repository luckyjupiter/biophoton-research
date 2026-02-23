"""
Biophoton Demyelination Simulator — Unified Model Package

This is the single source of truth for all shared physics, biology, and
detection models in the biophoton research program.  Per-track src/ code
should import from here rather than reimplementing core computations.

Modules:
    constants      — All physical, biological, and statistical constants
    axon           — AxonGeometry: myelinated axon as optical waveguide
    waveguide      — Transfer matrix, ARROW, multi-node propagation
    demyelination  — DemyelinationState, Hill equation, disease timelines
    emission       — ROS spectrum, disease emission, waveguide filtering
    detection      — Detector models, Poisson counting, ROC, Bayesian classifier
    coherence      — M-Phi coherence evolution (0D ODE + 1D PDE), kappa models
    network        — Kuramoto synchronization, M-function, network coherence
    cuprizone      — Full cuprizone experiment simulator
    visualization  — Matplotlib plotting functions
    simulate       — CLI entry point
"""

from .axon import AxonGeometry
from .demyelination import DemyelinationState
# from .detection import Detector  # TODO: Update when Detector class is implemented
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
from .coherence import (
    analytical_steady_state,
    analytical_transient,
    coherence_ode,
    solve_coherence_0d,
    solve_coherence_1d,
    solve_coherence_1d_demyelination,
    bifurcation_analysis,
    kappa_from_components,
    kappa_demyelinated,
)
from .network import (
    build_coupling_matrix,
    compute_m_function,
    kuramoto_order_parameter,
    simulate_network_synchronization,
    axon_coherence_from_sync,
)
from .uncertainty import (
    UncertaintyEngine,
    ParameterDistribution,
    build_default_parameter_set,
    propagate_emission_prediction,
    propagate_detection_prediction,
    propagate_roc_prediction,
    tornado_plot_data,
    run_full_cascade_mc,
)
from .detection import compare_groups, simulate_measurement
from .emission import confound_emission
from .node_emission import (
    NodeEmission,
    propagate_with_relay,
    ap_timing,
)

__all__ = [
    # Geometry
    "AxonGeometry",
    # Demyelination
    "DemyelinationState",
    # Detection
    # "Detector",  # TODO: Add when implemented
    # Emission
    "compute_feature_vector",
    "disease_emission",
    "ros_spectrum",
    "waveguide_filtered_emission",
    # Waveguide
    "arrow_wavelengths",
    "propagate_multi_node",
    "sefati_zeng_peak",
    "transfer_matrix_transmission",
    # Coherence
    "analytical_steady_state",
    "analytical_transient",
    "coherence_ode",
    "solve_coherence_0d",
    "solve_coherence_1d",
    "solve_coherence_1d_demyelination",
    "bifurcation_analysis",
    "kappa_from_components",
    "kappa_demyelinated",
    # Network
    "build_coupling_matrix",
    "compute_m_function",
    "kuramoto_order_parameter",
    "simulate_network_synchronization",
    "axon_coherence_from_sync",
    # Uncertainty
    "UncertaintyEngine",
    "ParameterDistribution",
    "build_default_parameter_set",
    "propagate_emission_prediction",
    "propagate_detection_prediction",
    "propagate_roc_prediction",
    "tornado_plot_data",
    "run_full_cascade_mc",
    # New detection functions
    "compare_groups",
    "simulate_measurement",
    # New emission functions
    "confound_emission",
    # Node emission (Zangari relay model)
    "NodeEmission",
    "propagate_with_relay",
    "ap_timing",
]
