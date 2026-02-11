"""
Attenuation modeling for biophoton propagation in myelinated axons.

Models multiple loss mechanisms: material absorption, Rayleigh scattering,
bending losses, Node of Ranvier scattering, and radiation leakage.

References:
    Kumar et al. (2016) Scientific Reports 6, 36508
    Frede et al. (2023) IEEE JSTQE / bioRxiv 2023.03.30.534951
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (AxonGeometry, N_MYELIN, N_AXOPLASM, N_ECF, C_VACUUM)


def absorption_coefficient(wavelength_nm, medium="myelin"):
    """Material absorption coefficient in cm^-1.

    Approximate values based on biological tissue optical properties.
    Dominant contributors: water (>900nm), proteins (<300nm), lipids (weak 400-800nm).

    Args:
        wavelength_nm: Wavelength(s) in nm.
        medium: 'myelin', 'axoplasm', or 'ecf'.

    Returns:
        Absorption coefficient in cm^-1.
    """
    lam = np.asarray(wavelength_nm, dtype=float)
    if medium == "myelin":
        # Lipid absorption: relatively flat in visible, rises in UV
        alpha = 0.5 + 50.0 * np.exp(-(lam - 280)**2 / (40**2))  # UV peak
        alpha += 0.1 * (lam / 500)**(-0.5)  # Weak visible
        # Water absorption bands
        alpha += 2.0 * np.exp(-(lam - 970)**2 / (30**2))
    elif medium == "axoplasm":
        # Higher scatterer content (organelles, filaments)
        alpha = 1.0 + 100.0 * np.exp(-(lam - 280)**2 / (40**2))
        alpha += 0.3 * (lam / 500)**(-0.5)
        alpha += 5.0 * np.exp(-(lam - 970)**2 / (30**2))
    else:  # ecf
        # Mostly water
        alpha = 0.3 + 20.0 * np.exp(-(lam - 280)**2 / (40**2))
        alpha += 5.0 * np.exp(-(lam - 970)**2 / (30**2))
    return alpha


def rayleigh_scattering(wavelength_nm, medium="myelin"):
    """Rayleigh scattering coefficient in cm^-1.

    Scales as lambda^-4. Dominant at short wavelengths.

    Args:
        wavelength_nm: Wavelength(s) in nm.
        medium: 'myelin' or 'axoplasm'.

    Returns:
        Scattering coefficient in cm^-1.
    """
    lam = np.asarray(wavelength_nm, dtype=float)
    if medium == "myelin":
        # Lower scattering due to ordered lipid structure
        alpha_500 = 2.0  # cm^-1 at 500nm
    else:
        # Higher scattering in cytoplasm (organelles, filaments)
        alpha_500 = 10.0
    return alpha_500 * (500.0 / lam)**4


def bending_loss(wavelength_nm, bend_radius_um, n_core=N_MYELIN, n_clad=N_AXOPLASM,
                 a_um=0.714):
    """Bending loss coefficient in cm^-1.

    Uses the exponential model: alpha_bend ~ C * exp(-R/Rc).

    Args:
        wavelength_nm: Wavelength in nm.
        bend_radius_um: Bend radius in micrometers.
        n_core: Core refractive index.
        n_clad: Cladding refractive index.
        a_um: Waveguide radius in um.

    Returns:
        Bending loss in cm^-1.
    """
    lam = np.asarray(wavelength_nm, dtype=float)
    Delta = (n_core**2 - n_clad**2) / (2 * n_core**2)
    # Critical radius
    Rc_um = (lam * 1e-3) / (4 * np.pi) * (1 / Delta)**1.5  # um
    R = np.asarray(bend_radius_um, dtype=float)
    # Loss coefficient
    alpha_bend = 0.1 * np.exp(-R / Rc_um)  # cm^-1, prefactor is approximate
    return alpha_bend


def node_of_ranvier_loss(wavelength_nm, node_length_um=1.0, n_modes=1):
    """Per-node transmission loss at a Node of Ranvier.

    Based on Kumar et al. (2016): T_node ~ 0.46 to 0.96 depending on
    wavelength and geometry. We use a simple model where transmission
    depends on the ratio of node length to wavelength.

    Args:
        wavelength_nm: Wavelength(s) in nm.
        node_length_um: Node length in micrometers.
        n_modes: Number of guided modes (more modes = more scattering).

    Returns:
        dict with 'T_node' (per-node power transmission) and
             'alpha_node_per_cm' (equivalent distributed loss).
    """
    lam = np.asarray(wavelength_nm, dtype=float)
    node_length_nm = node_length_um * 1000
    # Simple model: T decreases with node_length/lambda ratio
    # Calibrated to match Kumar et al. range
    ratio = node_length_nm / lam
    T_node = 0.95 * np.exp(-0.15 * ratio) * (1.0 / (1 + 0.02 * (n_modes - 1)))
    T_node = np.clip(T_node, 0.3, 0.98)
    # Equivalent distributed loss (per cm, assuming 1mm internode)
    alpha_node = -np.log(T_node) / 0.1  # 0.1 cm = 1 mm internode
    return {'T_node': T_node, 'alpha_node_per_cm': alpha_node}


def total_attenuation(axon, wavelength_nm, bend_radius_um=50.0):
    """Compute total attenuation budget for a myelinated axon.

    Returns all loss components and total in cm^-1.
    """
    lam = np.asarray(wavelength_nm, dtype=float)
    alpha_abs_myelin = absorption_coefficient(lam, "myelin")
    alpha_abs_axon = absorption_coefficient(lam, "axoplasm")
    alpha_scat_myelin = rayleigh_scattering(lam, "myelin")
    alpha_scat_axon = rayleigh_scattering(lam, "axoplasm")
    alpha_bend = bending_loss(lam, bend_radius_um, a_um=axon.r_outer_um)
    node_loss = node_of_ranvier_loss(lam, axon.node_length_um)
    # Weighted average based on confinement (assume 60% in myelin, 30% axon, 10% ECF)
    Gm, Ga = 0.6, 0.3
    alpha_material = Gm * alpha_abs_myelin + Ga * alpha_abs_axon
    alpha_scatter = Gm * alpha_scat_myelin + Ga * alpha_scat_axon
    alpha_total = alpha_material + alpha_scatter + alpha_bend + node_loss['alpha_node_per_cm']

    return {
        'wavelengths': lam,
        'alpha_absorption': alpha_material,
        'alpha_scattering': alpha_scatter,
        'alpha_bending': alpha_bend,
        'alpha_node': node_loss['alpha_node_per_cm'],
        'T_node': node_loss['T_node'],
        'alpha_total': alpha_total,
        'loss_dB_per_cm': 10 * np.log10(np.e) * alpha_total,
    }


def propagation_distance(axon, wavelength_nm, threshold_dB=-20):
    """Compute maximum propagation distance for given loss threshold.

    Args:
        axon: AxonGeometry.
        wavelength_nm: Wavelength(s).
        threshold_dB: Minimum acceptable transmission in dB.

    Returns:
        Maximum propagation distance in cm.
    """
    att = total_attenuation(axon, wavelength_nm)
    # L_max = |threshold_dB| / loss_dB_per_cm
    L_max = abs(threshold_dB) / np.maximum(att['loss_dB_per_cm'], 0.01)
    return L_max


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("Track 03: Attenuation Modeling")
    print("=" * 50)

    axon = AxonGeometry(r_axon_um=0.5, g_ratio=0.7)
    print(axon.summary())

    wavelengths = np.linspace(350, 700, 200)
    att = total_attenuation(axon, wavelengths)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    ax1.semilogy(wavelengths, att['alpha_absorption'], 'b-', lw=1.5, label='Absorption')
    ax1.semilogy(wavelengths, att['alpha_scattering'], 'r-', lw=1.5, label='Rayleigh')
    ax1.semilogy(wavelengths, att['alpha_bending'], 'g-', lw=1.5, label='Bending')
    ax1.semilogy(wavelengths, att['alpha_node'], 'm-', lw=1.5, label='Node of Ranvier')
    ax1.semilogy(wavelengths, att['alpha_total'], 'k-', lw=2, label='Total')
    ax1.set_ylabel('Attenuation [cm^-1]')
    ax1.set_title('Loss Mechanisms in Myelinated Axon Waveguide')
    ax1.legend(); ax1.grid(True, alpha=0.3)

    ax2.plot(wavelengths, att['loss_dB_per_cm'], 'k-', lw=2)
    ax2.set_ylabel('Loss [dB/cm]')
    ax2.grid(True, alpha=0.3)

    ax3.plot(wavelengths, att['T_node'], 'b-', lw=1.5)
    ax3.set_xlabel('Wavelength [nm]')
    ax3.set_ylabel('Node Transmission')
    ax3.set_title('Per-Node Transmission (Node of Ranvier)')
    ax3.grid(True, alpha=0.3)

    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                      "attenuation_budget.png")
    plt.tight_layout()
    plt.savefig(fp, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp)

    # Propagation distance
    L_max = propagation_distance(axon, wavelengths, threshold_dB=-20)
    fig2, ax4 = plt.subplots(figsize=(10, 5))
    ax4.plot(wavelengths, L_max * 10, 'b-', lw=1.5)  # Convert to mm
    ax4.set_xlabel('Wavelength [nm]')
    ax4.set_ylabel('Max propagation distance [mm]')
    ax4.set_title('Propagation distance at -20 dB threshold')
    ax4.grid(True, alpha=0.3)
    fp2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "propagation_distance.png")
    plt.savefig(fp2, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp2)

    # Summary table
    key_wavelengths = [400, 450, 500, 550, 600, 650, 700]
    print()
    print(f"{'lambda':>8} {'alpha_tot':>10} {'dB/cm':>8} {'T_node':>8} {'L_max(mm)':>10}")
    for wl in key_wavelengths:
        a = total_attenuation(axon, wl)
        L = propagation_distance(axon, wl, threshold_dB=-20)
        print(f"{wl:>8} {float(a['alpha_total']):>10.2f} {float(a['loss_dB_per_cm']):>8.1f} "
              f"{float(a['T_node']):>8.3f} {float(L)*10:>10.2f}")
    print("Done.")
