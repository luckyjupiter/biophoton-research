"""
Cuprizone experiment with relay model predictions.

Extends the standard cuprizone simulator with predictions from
the Zangari nanoantenna relay model. Demyelination now affects
TWO measurable quantities:

1. External leakage signal (INCREASES with damage) — original model
2. Internal guided relay signal (DECREASES with damage) — new prediction

This dual-signature is unique to the relay model and experimentally testable.

References:
    Zangari et al., Sci Rep 8:539 (2018)
    Zangari et al., Sci Rep 11:3022 (2021)
    Kumar et al., Sci Rep 6:36508 (2016)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

from . import constants as C
from .axon import AxonGeometry
from .demyelination import cuprizone_timeline, DemyelinationState
from .emission import waveguide_filtered_emission
from .node_emission import NodeEmission, propagate_with_relay
from .detection import Detector


@dataclass
class RelayTimePoint:
    """Results at one timepoint with both external and relay signals."""
    week: float
    state: DemyelinationState
    
    # External signal (what detector sees from OUTSIDE the nerve)
    external_signal: float          # photons/s/cm² (leakage + scatter)
    external_counts: np.ndarray     # per-mouse detected counts
    control_counts: np.ndarray      # healthy controls
    
    # Internal relay signal (what propagates ALONG the axon)
    relay_signal_at_node_10: float  # photons/s/nm at node 10
    relay_steady_state: float       # analytical steady state
    relay_transmission: float       # per-internode transmission
    
    # Derived
    external_enhancement: float     # fold increase vs healthy
    relay_reduction: float          # fraction of healthy relay signal
    p_value: float = 1.0
    effect_size: float = 0.0


def run_cuprizone_relay(
    axon: AxonGeometry = None,
    n_mice: int = 10,
    weeks: int = 12,
    detector: Detector = None,
    exposure_s: float = 300.0,
    collection_area_cm2: float = 0.01,
    animal_cv: float = 0.35,
    n_relay_nodes: int = 10,
    ap_rate_hz: float = 10.0,
    seed: int = 42,
) -> list[RelayTimePoint]:
    """Run cuprizone experiment with relay model predictions.
    
    For each timepoint (week), computes:
    1. External biophoton signal (existing model — leakage increases with damage)
    2. Internal relay signal (new — guided signal decreases with damage)
    
    Demyelination degrades the waveguide:
    - Fewer myelin wraps → lower transmission per internode
    - More gaps → more leakage at nodes
    - Nanoantenna emission unchanged (node channels unaffected by myelin loss)
    - Net effect on relay: lower T → lower steady state
    """
    if axon is None:
        axon = AxonGeometry(1.0, 0.75)
    if detector is None:
        detector = Detector.PMT()
    
    rng = np.random.default_rng(seed)
    wavelengths = C.DEFAULT_LAMBDA_RANGE_NM
    lam_relay = np.array([500.0])  # representative wavelength for relay
    
    # Per-animal variability
    treated_mult = rng.lognormal(0, animal_cv, size=n_mice)
    control_mult = rng.lognormal(0, animal_cv, size=n_mice)
    
    # Healthy baselines
    healthy = DemyelinationState(0, 0, 0)
    healthy_external = waveguide_filtered_emission(axon, healthy, wavelengths)
    healthy_rate = float(np.trapezoid(healthy_external, wavelengths)) * collection_area_cm2
    
    healthy_relay = propagate_with_relay(axon, lam_relay, n_nodes=n_relay_nodes, ap_rate_hz=ap_rate_hz)
    healthy_relay_at_10 = float(healthy_relay['total_signal'][n_relay_nodes, 0])
    healthy_relay_ss = float(healthy_relay['steady_state'][0])
    
    timepoints = []
    measurement_weeks = np.arange(0, weeks + 0.01, 1.0)
    
    for week in measurement_weeks:
        state = cuprizone_timeline(float(week))
        
        # === External signal (leakage — increases with damage) ===
        spectrum = waveguide_filtered_emission(axon, state, wavelengths)
        signal_rate = float(np.trapezoid(spectrum, wavelengths)) * collection_area_cm2
        
        treated_counts = np.array([
            rng.poisson(max(1e-10,
                signal_rate * m * detector.quantum_efficiency
                + detector.dark_rate_hz) * exposure_s)
            for m in treated_mult
        ])
        control_counts = np.array([
            rng.poisson(max(1e-10,
                healthy_rate * m * detector.quantum_efficiency
                + detector.dark_rate_hz) * exposure_s)
            for m in control_mult
        ])
        
        # Stats
        from .detection import compare_groups
        grp = compare_groups(treated_counts.astype(float), control_counts.astype(float))
        
        # === Internal relay signal (decreases with damage) ===
        # Demyelination reduces myelin wraps → changes waveguide transmission
        # Create a damaged axon with effective reduced wraps
        effective_wraps = state.effective_wraps(axon.n_wraps)
        effective_g = axon.g_ratio  # g-ratio changes are more complex; keep constant
        
        # Recalculate with damaged myelin thickness
        # More gap fraction = more coupling loss at nodes
        base_coupling_loss_db = 1.0
        damage_coupling_penalty_db = state.gamma * 3.0  # gaps increase node loss
        total_coupling_loss_db = base_coupling_loss_db + damage_coupling_penalty_db
        
        # Build damaged axon for relay (fewer wraps = worse waveguide)
        if effective_wraps > 0:
            # Approximate: thinner myelin = higher g-ratio
            damaged_myelin_um = effective_wraps * C.LIPID_BILAYER_THICKNESS_NM * 1e-3
            damaged_diameter = axon.axon_diameter_um + 2 * damaged_myelin_um
            damaged_g = axon.axon_diameter_um / damaged_diameter if damaged_diameter > 0 else 0.99
            damaged_axon = AxonGeometry(damaged_diameter, min(damaged_g, 0.99))
        else:
            damaged_axon = axon  # fallback
        
        relay = propagate_with_relay(
            damaged_axon, lam_relay, 
            n_nodes=n_relay_nodes,
            node_coupling_loss_db=total_coupling_loss_db,
            ap_rate_hz=ap_rate_hz,
        )
        relay_at_10 = float(relay['total_signal'][n_relay_nodes, 0])
        relay_ss = float(relay['steady_state'][0])
        relay_t = float(relay['transmission_per_internode'][0])
        
        tp = RelayTimePoint(
            week=float(week),
            state=state,
            external_signal=signal_rate,
            external_counts=treated_counts,
            control_counts=control_counts,
            relay_signal_at_node_10=relay_at_10,
            relay_steady_state=relay_ss,
            relay_transmission=relay_t,
            external_enhancement=signal_rate / max(healthy_rate, 1e-30),
            relay_reduction=relay_at_10 / max(healthy_relay_at_10, 1e-30),
            p_value=grp['p_value'],
            effect_size=grp['effect_size'],
        )
        timepoints.append(tp)
    
    return timepoints
