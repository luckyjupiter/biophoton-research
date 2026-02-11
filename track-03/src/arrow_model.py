"""
ARROW (Anti-Resonant Reflecting Optical Waveguide) analysis for myelinated axon.

Models the myelin sheath as a Fabry-Perot cladding layer surrounding a
low-index axoplasm core. Computes transmission spectra identifying
resonant (high-loss) and anti-resonant (low-loss, guided) wavelengths.

References:
    Babini et al. (2022) Scientific Reports 12, 19429
    Litchinitser et al. (2002) Optics Letters 27, 1592
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (AxonGeometry, N_MYELIN, N_AXOPLASM, N_ECF,
                       n_myelin, n_axoplasm, n_ecf, C_VACUUM)


def arrow_wavelengths(d_myelin_um, n_clad=N_MYELIN, n_core=N_AXOPLASM, m_max=5):
    """Compute ARROW anti-resonant and resonant wavelengths.

    Args:
        d_myelin_um: Myelin thickness in micrometers.
        n_clad: Cladding (myelin) refractive index.
        n_core: Core (axoplasm) refractive index.
        m_max: Maximum order to compute.

    Returns:
        dict with 'anti_resonant' and 'resonant' wavelength arrays in nm.
    """
    d = d_myelin_um * 1e-3  # um -> mm... no, keep in um for nm output
    dn = np.sqrt(n_clad**2 - n_core**2)
    ar_wavelengths = []
    r_wavelengths = []
    for m in range(1, m_max + 1):
        lam_ar = (2 * d_myelin_um * 1000 / (2*m - 1)) * dn  # nm
        lam_r = (2 * d_myelin_um * 1000 / (2*m)) * dn  # nm
        if lam_ar > 0:
            ar_wavelengths.append(lam_ar)
        if lam_r > 0:
            r_wavelengths.append(lam_r)
    return {
        'anti_resonant': np.array(ar_wavelengths),
        'resonant': np.array(r_wavelengths),
    }


def fabry_perot_reflectance(wavelength_nm, d_um, n_layer, n_surround, theta_deg=0):
    """Fabry-Perot reflectance of a single dielectric layer.

    Args:
        wavelength_nm: Wavelength(s) in nm.
        d_um: Layer thickness in um.
        n_layer: Layer refractive index.
        n_surround: Surrounding medium index.
        theta_deg: Angle of incidence in degrees.

    Returns:
        Reflectance array.
    """
    lam = np.asarray(wavelength_nm, dtype=float)
    theta = np.radians(theta_deg)
    # Snell's law for angle in layer
    sin_theta_layer = (n_surround / n_layer) * np.sin(theta)
    cos_theta_layer = np.sqrt(1 - sin_theta_layer**2)
    # Phase accumulated in layer
    delta = (2 * np.pi / lam) * n_layer * (d_um * 1000) * cos_theta_layer
    # Fresnel reflection coefficient (TE polarization)
    r = (n_surround * np.cos(theta) - n_layer * cos_theta_layer) /         (n_surround * np.cos(theta) + n_layer * cos_theta_layer)
    R_single = r**2
    # Airy function for Fabry-Perot
    F = 4 * R_single / (1 - R_single)**2
    R_fp = F * np.sin(delta)**2 / (1 + F * np.sin(delta)**2)
    return R_fp


def arrow_transmission_spectrum(axon, wavelength_range_nm=(300, 800),
                                n_wavelengths=500, theta_deg=0):
    """Compute ARROW transmission spectrum for a myelinated axon.

    The myelin sheath acts as a Fabry-Perot cladding. At anti-resonant
    wavelengths, the cladding reflectance is high and light is confined
    in the core. At resonant wavelengths, light leaks through.

    Args:
        axon: AxonGeometry instance.
        wavelength_range_nm: Wavelength range tuple (min, max) in nm.
        n_wavelengths: Number of wavelength points.
        theta_deg: Grazing angle in degrees.

    Returns:
        dict with 'wavelengths', 'reflectance', 'transmission'.
    """
    wavelengths = np.linspace(wavelength_range_nm[0], wavelength_range_nm[1],
                              n_wavelengths)
    d_myelin = axon.myelin_thickness_um
    R = fabry_perot_reflectance(wavelengths, d_myelin, N_MYELIN, N_AXOPLASM,
                                theta_deg)
    T = 1 - R
    # For ARROW, high R means guided (anti-resonant), low R means lossy (resonant)
    return {
        'wavelengths': wavelengths,
        'reflectance': R,
        'transmission': T,
        'confinement_loss_dB_per_cm': -10 * np.log10(np.maximum(R, 1e-10)) * 100,
    }


def multilayer_arrow_reflectance(wavelength_nm, n_lamellae, d_period_nm=17.0,
                                  n_lipid=1.48, n_aqueous=1.35,
                                  n_core=N_AXOPLASM, theta_deg=0):
    """Compute reflectance of multilayer myelin stack using transfer matrix.

    Each myelin period consists of a lipid bilayer (high-n) and an
    aqueous layer (low-n). The stack of N periods creates a 1D photonic
    crystal with stop bands at specific wavelengths.

    Args:
        wavelength_nm: Wavelength(s) in nm.
        n_lamellae: Number of myelin periods.
        d_period_nm: Period thickness in nm.
        n_lipid: Lipid bilayer refractive index.
        n_aqueous: Aqueous layer refractive index.
        n_core: Core (axoplasm) refractive index.
        theta_deg: Angle of incidence.

    Returns:
        Reflectance array.
    """
    lam = np.asarray(wavelength_nm, dtype=float)
    theta0 = np.radians(theta_deg)
    d_lipid = d_period_nm * 0.41  # ~7nm lipid per 17nm period
    d_aqueous = d_period_nm * 0.59  # ~10nm aqueous per period

    reflectance = np.zeros_like(lam)
    for idx in range(len(lam)):
        wl = lam[idx]
        # Transfer matrix for one period
        M = np.eye(2, dtype=complex)
        for (d_nm, n_layer) in [(d_lipid, n_lipid), (d_aqueous, n_aqueous)]:
            sin_theta = (n_core / n_layer) * np.sin(theta0)
            if abs(sin_theta) > 1:
                cos_theta = 1j * np.sqrt(sin_theta**2 - 1)
            else:
                cos_theta = np.sqrt(1 - sin_theta**2)
            delta = (2 * np.pi / wl) * n_layer * d_nm * cos_theta
            eta = n_layer * cos_theta  # TE
            layer_M = np.array([
                [np.cos(delta), -1j * np.sin(delta) / eta],
                [-1j * eta * np.sin(delta), np.cos(delta)]
            ], dtype=complex)
            M = M @ layer_M
        # Stack N periods
        M_total = np.linalg.matrix_power(M, n_lamellae)
        # Reflection coefficient
        eta_in = n_core * np.cos(theta0)
        eta_out = n_core * np.cos(theta0)  # symmetric
        r_num = M_total[0,0]*eta_out + M_total[0,1]*eta_in*eta_out - M_total[1,0] - M_total[1,1]*eta_in
        r_den = M_total[0,0]*eta_out + M_total[0,1]*eta_in*eta_out + M_total[1,0] + M_total[1,1]*eta_in
        r = r_num / r_den if abs(r_den) > 1e-30 else 0
        reflectance[idx] = abs(r)**2

    return reflectance


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("Track 03: ARROW Analysis")
    print("=" * 50)

    axon = AxonGeometry(r_axon_um=0.5, g_ratio=0.7)
    print(axon.summary())
    print()

    # ARROW wavelengths
    aw = arrow_wavelengths(axon.myelin_thickness_um)
    print("Anti-resonant wavelengths (nm):", ["%.1f" % x for x in aw["anti_resonant"]])
    print("Resonant wavelengths (nm):",      ["%.1f" % x for x in aw["resonant"]])

    # Transmission spectrum
    spec = arrow_transmission_spectrum(axon, wavelength_range_nm=(300, 800), n_wavelengths=500)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.plot(spec["wavelengths"], spec["reflectance"], "b-", lw=1.5)
    ax1.set_ylabel("Cladding Reflectance")
    ax1.set_title("ARROW Analysis: Myelin Fabry-Perot Cladding")
    for lam in aw["anti_resonant"]:
        if 300 <= lam <= 800:
            ax1.axvline(lam, color="green", ls="--", alpha=0.5, label="AR" if lam==aw["anti_resonant"][0] else "")
    for lam in aw["resonant"]:
        if 300 <= lam <= 800:
            ax1.axvline(lam, color="red", ls=":", alpha=0.5, label="R" if lam==aw["resonant"][0] else "")
    ax1.legend(); ax1.grid(True, alpha=0.3)

    ax2.plot(spec["wavelengths"], spec["transmission"], "r-", lw=1.5)
    ax2.set_xlabel("Wavelength [nm]")
    ax2.set_ylabel("Cladding Transmission (leakage)")
    ax2.grid(True, alpha=0.3)

    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "arrow_spectrum.png")
    plt.tight_layout()
    plt.savefig(fp, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp)

    # Multilayer reflectance
    print("Computing multilayer myelin reflectance...")
    wls = np.linspace(300, 800, 300)
    R_multi = multilayer_arrow_reflectance(wls, axon.n_lamellae)

    fig2, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(wls, R_multi, "b-", lw=1.5)
    ax3.set_xlabel("Wavelength [nm]")
    ax3.set_ylabel("Multilayer Reflectance")
    ax3.set_title(f"Myelin Stack Reflectance ({axon.n_lamellae} lamellae)")
    ax3.grid(True, alpha=0.3)
    fp2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "multilayer_reflectance.png")
    plt.savefig(fp2, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp2)
    print("Done.")
