"""Top-level orchestrator: chains Scale 1 -> Scale 2 -> Scale 3.

Given molecular parameters, computes:
1. Photon generation rate (molecular_generation)
2. Transmission through myelin waveguide (waveguide_transport)
3. Network-level coherence (network_coherence + coherence_solver)
"""

import numpy as np
from . import molecular_generation as mol
from . import waveguide_transport as wg
from . import network_coherence as net
from . import coherence_solver as cs
from .constants import (
    G_PHI_PSI, KAPPA_BASE, PSI_SQUARED,
    INTERNODE_LENGTH, NODE_TRANSMISSION, ALPHA_MYELIN,
)


def run_multiscale(
        # Scale 1 params
        ros_params: dict | None = None,
        emitting_volume: float = 1e-12,  # L (1 pL per axon segment)
        # Scale 2 params
        n_internodes: int = 10,
        wavelength: float = 520e-9,
        # Scale 3 params
        n_axons: int = 50,
        coupling_K: float = 0.01,
        topology: str = "nearest_neighbor",
        # Coherence solver params
        g: float = G_PHI_PSI,
        kappa: float = KAPPA_BASE,
        t_coherence: tuple = (0, 10),
) -> dict:
    """Run the full multiscale simulation pipeline.

    Returns a dict with results from each scale and the final
    network coherence measure M.
    """
    results = {}

    # === Scale 1: Molecular photon generation ===
    ss_ros = mol.steady_state_ros(ros_params)
    photon_rate = mol.compute_photon_rate(
        ss_ros["triplet_carbonyl"], emitting_volume
    )
    results["scale1"] = {
        "steady_state_ros": ss_ros,
        "photon_rate_per_axon": photon_rate,
    }

    # === Scale 2: Waveguide transport ===
    # Mode analysis
    mode_info = wg.guided_mode_condition(wavelength)

    # Multi-segment transport
    transport = wg.multi_segment_transport(
        n_internodes=n_internodes,
        internode_length=INTERNODE_LENGTH,
        node_transmission=NODE_TRANSMISSION,
        alpha=ALPHA_MYELIN,
    )

    # Effective photon rate at axon terminal
    delivered_rate = photon_rate * transport["total_transmission"]

    results["scale2"] = {
        "mode_info": mode_info,
        "transport": transport,
        "delivered_photon_rate": delivered_rate,
        "transmission_efficiency": transport["total_transmission"],
    }

    # === Scale 3: Network coherence ===
    # Phase synchronization
    sync = net.simulate_network_synchronization(
        n_axons=n_axons, K=coupling_K, topology=topology,
    )

    # Final order parameter
    r_final = sync["order_parameter"][-1]

    # Network coherence from synchronization
    lambda_network = net.axon_coherence_from_sync(
        r_final, g=g, kappa=kappa
    )

    # M-function (simplified: uniform gamma, theta, delta_gr)
    lambda_per_axon = np.full(n_axons, lambda_network)
    gamma = np.ones(n_axons) * 0.8
    theta = np.ones(n_axons) * 0.9
    delta_gr = np.ones(n_axons) * 0.1

    M = net.compute_m_function(lambda_per_axon, gamma, theta, delta_gr)

    results["scale3"] = {
        "synchronization": {
            "final_order_parameter": r_final,
            "order_parameter_timeseries": sync["order_parameter"],
            "t": sync["t"],
        },
        "lambda_network": lambda_network,
        "M_function": M,
    }

    # === Summary ===
    results["summary"] = {
        "photon_generation_rate": photon_rate,
        "waveguide_transmission": transport["total_transmission"],
        "delivered_photons": delivered_rate,
        "network_sync_r": r_final,
        "coherence_Lambda": lambda_network,
        "neurocoherence_M": M,
    }

    return results


def parameter_sweep(param_name: str, param_values: np.ndarray,
                    base_kwargs: dict | None = None) -> dict:
    """Sweep a single parameter and record key outputs.

    Args:
        param_name: Key in run_multiscale kwargs to sweep
        param_values: Array of values to try
        base_kwargs: Base parameters for run_multiscale
    """
    base = base_kwargs or {}
    sweep_results = {
        "param_name": param_name,
        "param_values": param_values,
        "photon_rate": [],
        "transmission": [],
        "sync_r": [],
        "Lambda": [],
        "M": [],
    }

    for val in param_values:
        kwargs = dict(base)
        kwargs[param_name] = val
        result = run_multiscale(**kwargs)
        s = result["summary"]

        sweep_results["photon_rate"].append(s["photon_generation_rate"])
        sweep_results["transmission"].append(s["waveguide_transmission"])
        sweep_results["sync_r"].append(s["network_sync_r"])
        sweep_results["Lambda"].append(s["coherence_Lambda"])
        sweep_results["M"].append(s["neurocoherence_M"])

    for key in ["photon_rate", "transmission", "sync_r", "Lambda", "M"]:
        sweep_results[key] = np.array(sweep_results[key])

    return sweep_results
