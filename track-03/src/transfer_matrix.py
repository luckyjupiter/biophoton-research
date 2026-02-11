"""
Transfer matrix model for multilayer cylindrical waveguide (planar approx).

Implements the Zeng et al. (2022) approach: each myelin lamella is resolved
as a distinct dielectric layer. Computes transmission through the full
myelin stack as a function of wavelength.

References:
    Zeng et al. (2022) Applied Optics 61(14), 4013-4021
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (AxonGeometry, N_MYELIN, N_AXOPLASM, N_ECF,
                       N_LIPID_BILAYER, N_CYTOPLASM_INTRA, MYELIN_PERIOD_NM)


def transfer_matrix_layer(wavelength_nm, d_nm, n_layer, theta_deg=0, polarization="TE"):
    """2x2 transfer matrix for a single planar dielectric layer.

    Args:
        wavelength_nm: Free-space wavelength in nm.
        d_nm: Layer thickness in nm.
        n_layer: Layer refractive index.
        theta_deg: Angle of incidence (degrees).
        polarization: 'TE' or 'TM'.

    Returns:
        2x2 complex transfer matrix.
    """
    theta = np.radians(theta_deg)
    sin_t = np.sin(theta)
    # Snell's law in layer (assuming incident from vacuum equivalent)
    sin_tl = sin_t / n_layer  # simplified
    if abs(sin_tl) > 1:
        cos_tl = 1j * np.sqrt(sin_tl**2 - 1)
    else:
        cos_tl = np.sqrt(1 - sin_tl**2)
    k_z = (2 * np.pi / wavelength_nm) * n_layer * d_nm * cos_tl
    if polarization == "TE":
        eta = n_layer * cos_tl
    else:
        eta = cos_tl / n_layer
    M = np.array([
        [np.cos(k_z), -1j * np.sin(k_z) / eta],
        [-1j * eta * np.sin(k_z), np.cos(k_z)]
    ], dtype=complex)
    return M


def build_myelin_stack(n_lamellae, d_period_nm=MYELIN_PERIOD_NM,
                       lipid_fraction=0.41):
    """Build the layer structure for a myelin stack.

    Returns list of (thickness_nm, refractive_index) tuples.
    """
    d_lipid = d_period_nm * lipid_fraction
    d_aqueous = d_period_nm * (1 - lipid_fraction)
    layers = []
    for _ in range(n_lamellae):
        layers.append((d_lipid, N_LIPID_BILAYER))
        layers.append((d_aqueous, N_CYTOPLASM_INTRA))
    return layers


def compute_transmission_spectrum(layers, wavelength_range_nm=(300, 800),
                                   n_wavelengths=500, n_incident=N_AXOPLASM,
                                   n_exit=N_ECF, theta_deg=0, polarization="TE"):
    """Compute transmission spectrum through a multilayer stack.

    Args:
        layers: List of (thickness_nm, refractive_index) tuples.
        wavelength_range_nm: (min, max) wavelength range.
        n_wavelengths: Number of wavelength points.
        n_incident: Incident medium refractive index.
        n_exit: Exit medium refractive index.
        theta_deg: Angle of incidence.
        polarization: 'TE' or 'TM'.

    Returns:
        dict with 'wavelengths', 'transmission', 'reflectance', 'phase'.
    """
    wavelengths = np.linspace(wavelength_range_nm[0], wavelength_range_nm[1],
                              n_wavelengths)
    T_arr = np.zeros(len(wavelengths))
    R_arr = np.zeros(len(wavelengths))
    phase_arr = np.zeros(len(wavelengths))

    theta = np.radians(theta_deg)
    for idx, wl in enumerate(wavelengths):
        M_total = np.eye(2, dtype=complex)
        for (d_nm, n_layer) in layers:
            M_layer = transfer_matrix_layer(wl, d_nm, n_layer, theta_deg, polarization)
            M_total = M_total @ M_layer
        # Compute reflection and transmission
        if polarization == "TE":
            eta_in = n_incident * np.cos(theta)
            eta_out = n_exit * np.cos(theta)
        else:
            eta_in = np.cos(theta) / n_incident
            eta_out = np.cos(theta) / n_exit
        A = M_total[0,0]; B = M_total[0,1]; C = M_total[1,0]; D = M_total[1,1]
        r = (A*eta_out + B*eta_in*eta_out - C - D*eta_in) /             (A*eta_out + B*eta_in*eta_out + C + D*eta_in)
        t = 2*eta_in / (A*eta_out + B*eta_in*eta_out + C + D*eta_in)
        R_arr[idx] = abs(r)**2
        T_arr[idx] = abs(t)**2 * (eta_out / eta_in).real
        phase_arr[idx] = np.angle(t)

    return {
        'wavelengths': wavelengths,
        'transmission': T_arr,
        'reflectance': R_arr,
        'phase': phase_arr,
    }


def spectral_tuning_analysis(axon_diameters_um=None, lamellae_counts=None):
    """Reproduce Zeng et al. (2022) spectral tuning results.

    Computes how operating wavelength shifts with:
    - Additional myelin layers (+52.3 nm/layer predicted)
    - Axon diameter changes (-94.5 nm/um predicted)

    Returns:
        dict with 'diameters', 'lamellae', 'peak_wavelengths_diameter',
              'peak_wavelengths_lamellae'.
    """
    if axon_diameters_um is None:
        axon_diameters_um = np.linspace(0.3, 2.0, 10)
    if lamellae_counts is None:
        lamellae_counts = np.arange(5, 30)

    # Vary lamellae count (fixed diameter)
    peak_lam_lamellae = []
    for n_lam in lamellae_counts:
        layers = build_myelin_stack(n_lam)
        spec = compute_transmission_spectrum(layers, wavelength_range_nm=(300, 800),
                                              n_wavelengths=300)
        # Find peak transmission wavelength
        peak_idx = np.argmax(spec['transmission'])
        peak_lam_lamellae.append(spec['wavelengths'][peak_idx])

    # Vary diameter (fixed lamellae)
    peak_lam_diameter = []
    n_lam_fixed = 15
    for d_um in axon_diameters_um:
        axon = AxonGeometry(r_axon_um=d_um/2, g_ratio=0.7, n_lamellae=n_lam_fixed)
        layers = build_myelin_stack(n_lam_fixed)
        spec = compute_transmission_spectrum(layers, wavelength_range_nm=(300, 800),
                                              n_wavelengths=300)
        peak_idx = np.argmax(spec['transmission'])
        peak_lam_diameter.append(spec['wavelengths'][peak_idx])

    return {
        'lamellae_counts': np.array(lamellae_counts),
        'axon_diameters_um': np.array(axon_diameters_um),
        'peak_wavelengths_lamellae': np.array(peak_lam_lamellae),
        'peak_wavelengths_diameter': np.array(peak_lam_diameter),
    }


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("Track 03: Transfer Matrix Model")
    print("=" * 50)

    # Standard axon
    axon = AxonGeometry(r_axon_um=0.5, g_ratio=0.7)
    print(axon.summary())
    print()

    # Build myelin stack and compute transmission
    layers = build_myelin_stack(axon.n_lamellae)
    print(f"Myelin stack: {len(layers)} sublayers ({axon.n_lamellae} periods)")

    spec = compute_transmission_spectrum(layers, wavelength_range_nm=(300, 800),
                                          n_wavelengths=500)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.plot(spec['wavelengths'], spec['transmission'], 'b-', lw=1.2)
    ax1.set_ylabel('Transmission')
    ax1.set_title(f'Transfer Matrix: Myelin Stack ({axon.n_lamellae} lamellae)')
    ax1.grid(True, alpha=0.3)

    ax2.plot(spec['wavelengths'], spec['reflectance'], 'r-', lw=1.2)
    ax2.set_xlabel('Wavelength [nm]')
    ax2.set_ylabel('Reflectance')
    ax2.grid(True, alpha=0.3)

    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                      "transfer_matrix_spectrum.png")
    plt.tight_layout()
    plt.savefig(fp, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp)

    # Spectral tuning analysis
    print("Computing spectral tuning...")
    tuning = spectral_tuning_analysis()

    fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5))
    ax3.plot(tuning['lamellae_counts'], tuning['peak_wavelengths_lamellae'], 'bo-', ms=4)
    ax3.set_xlabel('Number of lamellae')
    ax3.set_ylabel('Peak wavelength [nm]')
    ax3.set_title('Spectral shift vs lamellae count')
    ax3.grid(True, alpha=0.3)
    # Fit slope
    if len(tuning['lamellae_counts']) > 2:
        p = np.polyfit(tuning['lamellae_counts'], tuning['peak_wavelengths_lamellae'], 1)
        ax3.plot(tuning['lamellae_counts'], np.polyval(p, tuning['lamellae_counts']),
                 'r--', label=f'slope={p[0]:.1f} nm/layer')
        ax3.legend()
        print(f"  Spectral shift per lamella: {p[0]:.1f} nm/layer (Zeng: +52.3)")

    ax4.plot(tuning['axon_diameters_um'], tuning['peak_wavelengths_diameter'], 'ro-', ms=4)
    ax4.set_xlabel('Axon diameter [um]')
    ax4.set_ylabel('Peak wavelength [nm]')
    ax4.set_title('Spectral shift vs axon diameter')
    ax4.grid(True, alpha=0.3)

    fp2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "spectral_tuning.png")
    plt.tight_layout()
    plt.savefig(fp2, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp2)
    print("Done.")
