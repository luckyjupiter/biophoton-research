"""
Track 08: MMI-Biophoton Coherence Bridge

Connects biophoton physics (Tracks 1-7) to mind-matter interaction (MMI)
research through the unified M-Phi coherence framework (Kruger, Feeney,
Duarte 2023).

Modules:
    constants          - Physical, statistical, and framework constants
    bayesian_coherence - Bayesian updating for biophoton coherence estimation
    phi_field_coupling - Phi-field coupling model and steady-state responsivity
    cross_prediction   - Correlation models: biophoton emission vs MMI hit rates
    qtrainer_bridge    - 17 QTrainerAI methods mapped to biophoton analysis
"""

from .constants import (
    INITIAL_PRIOR,
    LIKELIHOOD_SR,
    G_PHI_PSI_DEFAULT,
    KAPPA_DEFAULT,
    QTRAINER_METHODS,
)

__version__ = "0.1.0"
__all__ = [
    "constants",
    "bayesian_coherence",
    "phi_field_coupling",
    "cross_prediction",
    "qtrainer_bridge",
]
