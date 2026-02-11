"""
Optical waveguide propagation through myelinated axon segments.

Implements:
- Transfer matrix method for multilayer dielectric transmission
- ARROW (anti-resonant reflecting optical waveguide) formula
- Sefati/Zeng spectral tuning model
- Multi-node propagation with Node of Ranvier coupling losses
"""

from __future__ import annotations

import numpy as np

from . import constants as C
from .axon import AxonGeometry


def _phase_thickness(d_m: float, n: float, wavelength_m: float, theta: float = 0.0) -> float:
    """Phase accumulated traversing a layer: δ = 2π·n·d·cos(θ)/λ."""
    return 2 * np.pi * n * d_m * np.cos(theta) / wavelength_m


def _layer_matrix(delta: float | np.ndarray, eta: float) -> np.ndarray:
    """2×2 transfer matrix for a single dielectric layer (TE polarization).

    M = [[cos δ, -i sin δ / η],
         [-i η sin δ, cos δ]]

    Parameters
    ----------
    delta : phase thickness of the layer
    eta : n·cos(θ) for TE, or n/cos(θ) for TM
    """
    cos_d = np.cos(delta)
    sin_d = np.sin(delta)
    return np.array([
        [cos_d, -1j * sin_d / eta],
        [-1j * eta * sin_d, cos_d],
    ])


def transfer_matrix_transmission(
    axon: AxonGeometry,
    wavelength_nm: float | np.ndarray,
    n_wraps_override: int | None = None,
) -> np.ndarray:
    """Compute spectral transmission T(λ) through the myelin sheath using
    the transfer matrix method.

    Each myelin wrap is modeled as a single dielectric layer (n=1.44, d=10 nm).
    The full sheath is n_wraps such layers sandwiched between axon (n=1.38)
    and ECF (n=1.34).

    Returns T(λ) as a float or array matching the input wavelength shape.
    """
    wavelength_m = np.atleast_1d(wavelength_nm * 1e-9).astype(np.float64)
    n_wraps = n_wraps_override if n_wraps_override is not None else axon.n_wraps

    # Build system matrix as product of individual layer matrices
    # For normal incidence θ=0, η = n for TE
    eta_myelin = C.N_MYELIN
    eta_axon = C.N_AXON
    eta_ecf = C.N_ECF

    d_layer = C.LIPID_BILAYER_THICKNESS_M

    T = np.zeros_like(wavelength_m)
    for i, lam in enumerate(wavelength_m):
        delta = _phase_thickness(d_layer, C.N_MYELIN, lam)
        M_layer = _layer_matrix(delta, eta_myelin)

        # Total matrix = M_layer^n_wraps (repeated identical layers)
        M_total = np.linalg.matrix_power(M_layer, n_wraps)

        # Transmission coefficient: t = 2·η_in / (M11·η_in + M12·η_in·η_out + M21 + M22·η_out)
        # Simplified for normal incidence with η = n:
        m11, m12 = M_total[0, 0], M_total[0, 1]
        m21, m22 = M_total[1, 0], M_total[1, 1]

        t = 2 * eta_axon / (m11 * eta_axon + m12 * eta_axon * eta_ecf + m21 + m22 * eta_ecf)
        T[i] = (eta_ecf / eta_axon) * np.abs(t) ** 2

    return T.item() if T.size == 1 else T


def arrow_wavelengths(axon: AxonGeometry, m_max: int = 5) -> np.ndarray:
    """Anti-resonant wavelengths where guided modes are most strongly confined.

    λ_AR(m) = (2d / (2m-1)) · √(n_clad² - n_core²)

    These are the wavelengths where the myelin sheath acts as a high-reflectivity
    Fabry-Pérot, maximizing waveguide confinement.
    """
    d_total = axon.myelin_thickness_um * 1e3  # nm
    na = np.sqrt(C.N_MYELIN**2 - C.N_AXON**2)
    m_vals = np.arange(1, m_max + 1)
    return 2 * d_total * na / (2 * m_vals - 1)


def sefati_zeng_peak(axon: AxonGeometry) -> float:
    """Predicted peak guided wavelength from the Sefati/Zeng empirical model.

    λ_peak ≈ λ_base + 52.3·n_wraps - 94.5·d_axon(μm)

    Returns wavelength in nm. λ_base chosen so typical CNS axon peaks ~400-500 nm.
    """
    lambda_base = 300.0  # nm, baseline offset
    return (
        lambda_base
        + C.SPECTRAL_SHIFT_PER_LAYER_NM * axon.n_wraps
        + C.SPECTRAL_SHIFT_PER_UM_DIAMETER_NM * axon.axon_diameter_um
    )


def attenuation_db_per_cm(wavelength_nm: float | np.ndarray) -> np.ndarray:
    """Total attenuation in the myelin waveguide (dB/cm).

    Combines absorption (∝ 1/λ), scattering (∝ 1/λ⁴ Rayleigh), and bend loss.
    """
    lam = np.atleast_1d(wavelength_nm).astype(np.float64)
    ref_lam = 500.0  # reference wavelength

    alpha_abs = C.ABSORPTION_COEFF_PER_CM * (ref_lam / lam)
    alpha_scat = C.SCATTER_COEFF_PER_CM * (ref_lam / lam) ** 4
    alpha_bend = C.BEND_LOSS_PER_CM * np.ones_like(lam)

    # Convert from 1/cm (Neper) to dB/cm: dB = 4.343 × Neper
    total_neper = alpha_abs + alpha_scat + alpha_bend
    return 4.343 * total_neper


def propagate_multi_node(
    axon: AxonGeometry,
    wavelength_nm: np.ndarray,
    n_nodes: int = 20,
    node_coupling_loss_db: float = 1.0,
) -> np.ndarray:
    """Propagate light through a chain of myelinated segments with Nodes of Ranvier.

    At each Node of Ranvier, light exits the waveguide into a ~1 μm gap
    and must re-couple into the next internode segment. This adds coupling loss.

    Returns transmission T(λ) for the full chain.
    """
    internode_um = axon.internode_length_um()
    internode_cm = internode_um * 1e-4

    lam = np.atleast_1d(wavelength_nm).astype(np.float64)

    # Single internode transmission: T_segment = T_sheath × 10^(-α·L/10)
    t_sheath = transfer_matrix_transmission(axon, lam)
    atten = attenuation_db_per_cm(lam)
    t_segment = t_sheath * 10 ** (-atten * internode_cm / 10)

    # Node coupling loss
    coupling = 10 ** (-node_coupling_loss_db / 10)

    # Chain: n_nodes internodes, (n_nodes - 1) gaps
    t_total = t_segment ** n_nodes * coupling ** (n_nodes - 1)
    return t_total
