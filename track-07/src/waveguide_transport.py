"""Scale 2: Waveguide transport through myelinated axons.

Transfer matrix method for multilayer cylindrical waveguide,
attenuation modeling, and multi-segment propagation.
"""

import numpy as np
from .constants import (
    N_AXOPLASM, N_MYELIN_LIPID, N_MYELIN_WATER, ALPHA_MYELIN,
    AXON_RADIUS, N_LAMELLAE,
    INTERNODE_LENGTH, NODE_TRANSMISSION, LAMBDA_PEAK,
)


def transfer_matrix_layer(n1: float, n2: float, wavelength: float,
                          thickness: float, angle: float = 0.0) -> np.ndarray:
    """Transfer matrix for a single dielectric layer (planar approximation).

    For guided modes in cylindrical geometry, this is the local planar
    approximation valid when radius >> wavelength (marginal for myelin).

    Args:
        n1: Refractive index of incoming medium
        n2: Refractive index of layer
        wavelength: Free-space wavelength (m)
        thickness: Layer thickness (m)
        angle: Angle of incidence (rad)
    """
    k0 = 2 * np.pi / wavelength
    cos_t = np.sqrt(1 - (n1 / n2 * np.sin(angle))**2 + 0j)
    delta = k0 * n2 * cos_t * thickness

    # Interface matrix (TE polarization)
    r = (n1 * np.cos(angle) - n2 * cos_t) / (n1 * np.cos(angle) + n2 * cos_t)
    t_coeff = 2 * n1 * np.cos(angle) / (n1 * np.cos(angle) + n2 * cos_t)

    # Propagation matrix
    P = np.array([
        [np.exp(-1j * delta), 0],
        [0, np.exp(1j * delta)]
    ])

    # Interface matrix
    I_mat = (1 / t_coeff) * np.array([
        [1, r],
        [r, 1]
    ])

    return I_mat @ P


def myelin_transmission(wavelength: float = LAMBDA_PEAK,
                        n_lamellae: int = N_LAMELLAE,
                        angle: float = 0.05) -> dict:
    """Compute transmission through the myelin sheath multilayer.

    Models alternating lipid bilayer and water layers.

    Returns dict with transmission coefficient and phase.
    """
    lipid_thickness = 4e-9    # nm lipid bilayer
    water_thickness = 3e-9    # nm water layer between lamellae

    M_total = np.eye(2, dtype=complex)

    for _ in range(n_lamellae):
        # Water -> lipid interface + propagation
        M_lipid = transfer_matrix_layer(
            N_MYELIN_WATER, N_MYELIN_LIPID, wavelength, lipid_thickness, angle)
        # Lipid -> water interface + propagation
        M_water = transfer_matrix_layer(
            N_MYELIN_LIPID, N_MYELIN_WATER, wavelength, water_thickness, angle)
        M_total = M_total @ M_lipid @ M_water

    # Transmission = |1/M[0,0]|^2
    t_complex = 1.0 / M_total[0, 0]
    T = np.abs(t_complex)**2

    return {
        "transmission": float(np.real(T)),
        "phase": float(np.angle(t_complex)),
        "matrix": M_total,
    }


def guided_mode_condition(wavelength: float, core_radius: float = AXON_RADIUS,
                          n_core: float = N_AXOPLASM,
                          n_clad: float = N_MYELIN_LIPID) -> dict:
    """Check guided mode support using V-number analysis.

    V = (2*pi*a/lambda) * sqrt(n_core^2 - n_clad^2)
    Single mode if V < 2.405 (first zero of J0).
    """
    NA = np.sqrt(abs(n_core**2 - n_clad**2))
    V = (2 * np.pi * core_radius / wavelength) * NA

    # For step-index fiber, approximate number of modes
    if V < 2.405:
        n_modes = 1
    else:
        n_modes = int(V**2 / 2)

    return {
        "V_number": V,
        "NA": NA,
        "n_modes": n_modes,
        "single_mode": V < 2.405,
        "cutoff_wavelength": 2 * np.pi * core_radius * NA / 2.405,
    }


def propagation_loss(length: float, alpha: float = ALPHA_MYELIN) -> float:
    """Beer-Lambert attenuation through lossy waveguide.

    Returns fraction of power remaining after propagation.
    """
    return np.exp(-alpha * length)


def multi_segment_transport(n_internodes: int = 10,
                            internode_length: float = INTERNODE_LENGTH,
                            node_transmission: float = NODE_TRANSMISSION,
                            alpha: float = ALPHA_MYELIN) -> dict:
    """Simulate photon transport through multiple myelinated segments.

    Each internode has exponential attenuation; each node of Ranvier
    has a fixed transmission probability.

    Returns dict with cumulative transmission at each node.
    """
    cumulative = np.ones(n_internodes + 1)

    for i in range(n_internodes):
        # Attenuation through internode
        segment_loss = propagation_loss(internode_length, alpha)
        # Node transmission
        node_t = node_transmission if i < n_internodes - 1 else 1.0
        cumulative[i + 1] = cumulative[i] * segment_loss * node_t

    distances = np.arange(n_internodes + 1) * internode_length

    return {
        "distances": distances,
        "transmission": cumulative,
        "total_length": distances[-1],
        "total_transmission": cumulative[-1],
    }


def wavelength_sweep(wavelengths: np.ndarray | None = None,
                     n_lamellae: int = N_LAMELLAE) -> dict:
    """Compute myelin transmission spectrum across biophoton wavelength range."""
    if wavelengths is None:
        wavelengths = np.linspace(350e-9, 700e-9, 200)

    transmissions = []
    for wl in wavelengths:
        result = myelin_transmission(wavelength=wl, n_lamellae=n_lamellae)
        transmissions.append(result["transmission"])

    return {
        "wavelengths": wavelengths,
        "transmissions": np.array(transmissions),
    }
