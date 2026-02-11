"""
Physical and biological constants for myelinated axon waveguide modeling.

All units are SI unless otherwise noted. Wavelengths in meters internally,
but convenience functions accept nanometers.

References:
    Kumar et al. (2016) Scientific Reports 6, 36508
    Babini et al. (2022) Scientific Reports 12, 19429
    Zeng et al. (2022) Applied Optics 61(14), 4013-4021
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


# ============================================================================
# Fundamental physical constants
# ============================================================================
C_VACUUM = 2.998e8          # Speed of light in vacuum [m/s]
MU_0 = 4 * np.pi * 1e-7    # Vacuum permeability [H/m]
EPS_0 = 8.854e-12           # Vacuum permittivity [F/m]
H_PLANCK = 6.626e-34        # Planck constant [J*s]
HBAR = 1.055e-34            # Reduced Planck constant [J*s]


# ============================================================================
# Refractive indices at visible wavelengths (~550 nm reference)
# ============================================================================
N_MYELIN = 1.44             # Myelin sheath (bulk effective index)
N_AXOPLASM = 1.38           # Axoplasm (cytoplasm, neurofilaments, microtubules)
N_ECF = 1.34                # Extracellular fluid
N_PERIAXONAL = 1.34         # Periaxonal space (thin fluid layer)
N_LIPID_BILAYER = 1.48      # Individual lipid bilayer within myelin
N_CYTOPLASM_INTRA = 1.35    # Intra-myelin cytoplasmic layers


# ============================================================================
# Myelin structural parameters
# ============================================================================
MYELIN_PERIOD_NM = 17.0     # Myelin lamella periodicity [nm]
MYELIN_PERIOD = 17e-9       # Myelin lamella periodicity [m]
LIPID_BILAYER_THICKNESS_NM = 3.5    # Single lipid bilayer [nm]
CYTOPLASMIC_LAYER_NM = 2.5          # Cytoplasmic apposition [nm]
EXTRACELLULAR_LAYER_NM = 1.5        # Extracellular apposition [nm]

# Sub-layer thicknesses within one myelin period (~17 nm total)
SUBLAYER_LIPID_NM = 7.0     # Combined lipid thickness per period [nm]
SUBLAYER_AQUEOUS_NM = 10.0  # Combined aqueous thickness per period [nm]


# ============================================================================
# Biological geometry parameters
# ============================================================================
G_RATIO_PNS = 0.6           # Typical PNS g-ratio
G_RATIO_CNS = 0.75          # Typical CNS g-ratio
G_RATIO_OPTIMAL_OPTICAL = 0.7  # Optimal for waveguiding (Babini et al. 2022)

NODE_LENGTH_UM = 1.0        # Typical Node of Ranvier length [um]
NODE_LENGTH = 1e-6           # Node of Ranvier length [m]
INTERNODE_LENGTH_MM = 1.0   # Typical internode length [mm]
INTERNODE_LENGTH = 1e-3      # Internode length [m]


# ============================================================================
# Biophoton wavelength range
# ============================================================================
LAMBDA_MIN_NM = 350.0       # Minimum biophoton wavelength [nm]
LAMBDA_MAX_NM = 700.0       # Maximum biophoton wavelength [nm]
LAMBDA_MIN = 350e-9         # [m]
LAMBDA_MAX = 700e-9         # [m]


# ============================================================================
# Dispersion: Cauchy coefficients for myelin (approximate)
# n(lambda) = A + B/lambda^2 + C/lambda^4
# Fitted to n=1.44 at 550nm with typical biological dispersion
# ============================================================================
CAUCHY_A_MYELIN = 1.4270
CAUCHY_B_MYELIN = 3.96e-15   # [m^2]
CAUCHY_C_MYELIN = 0.0

CAUCHY_A_AXOPLASM = 1.3680
CAUCHY_B_AXOPLASM = 3.63e-15

CAUCHY_A_ECF = 1.3280
CAUCHY_B_ECF = 3.63e-15


def n_cauchy(wavelength_m: float, A: float, B: float, C: float = 0.0) -> np.ndarray:
    """Cauchy dispersion relation: n(lambda) = A + B/lambda^2 + C/lambda^4."""
    lam = np.asarray(wavelength_m, dtype=float)
    return A + B / lam**2 + C / lam**4


def n_myelin(wavelength_nm: float) -> np.ndarray:
    """Refractive index of myelin at given wavelength(s) in nm."""
    lam_m = np.asarray(wavelength_nm, dtype=float) * 1e-9
    return n_cauchy(lam_m, CAUCHY_A_MYELIN, CAUCHY_B_MYELIN)


def n_axoplasm(wavelength_nm: float) -> np.ndarray:
    """Refractive index of axoplasm at given wavelength(s) in nm."""
    lam_m = np.asarray(wavelength_nm, dtype=float) * 1e-9
    return n_cauchy(lam_m, CAUCHY_A_AXOPLASM, CAUCHY_B_AXOPLASM)


def n_ecf(wavelength_nm: float) -> np.ndarray:
    """Refractive index of extracellular fluid at given wavelength(s) in nm."""
    lam_m = np.asarray(wavelength_nm, dtype=float) * 1e-9
    return n_cauchy(lam_m, CAUCHY_A_ECF, CAUCHY_B_ECF)


# ============================================================================
# Axon geometry dataclass
# ============================================================================
@dataclass
class AxonGeometry:
    """Parameterized myelinated axon geometry.

    Attributes:
        r_axon_um: Axon radius in micrometers.
        g_ratio: Ratio r_axon / r_outer.
        n_lamellae: Number of myelin lamellae (computed from geometry if None).
        internode_length_mm: Internode segment length in mm.
        node_length_um: Node of Ranvier length in um.
    """
    r_axon_um: float = 0.5
    g_ratio: float = 0.7
    n_lamellae: Optional[int] = None
    internode_length_mm: float = 1.0
    node_length_um: float = 1.0

    def __post_init__(self):
        if self.n_lamellae is None:
            self.n_lamellae = int(round(self.myelin_thickness_um * 1000 / MYELIN_PERIOD_NM))

    @property
    def r_outer_um(self) -> float:
        """Outer radius of myelin sheath [um]."""
        return self.r_axon_um / self.g_ratio

    @property
    def myelin_thickness_um(self) -> float:
        """Myelin sheath thickness [um]."""
        return self.r_outer_um - self.r_axon_um

    @property
    def r_axon_m(self) -> float:
        return self.r_axon_um * 1e-6

    @property
    def r_outer_m(self) -> float:
        return self.r_outer_um * 1e-6

    @property
    def myelin_thickness_m(self) -> float:
        return self.myelin_thickness_um * 1e-6

    def v_number(self, wavelength_nm: float, n_core: float = N_MYELIN,
                 n_clad: float = N_AXOPLASM) -> np.ndarray:
        """Compute V-number for the waveguide at given wavelength(s).

        By default uses myelin as guiding region (core) and axoplasm as cladding.
        """
        lam_m = np.asarray(wavelength_nm, dtype=float) * 1e-9
        a_m = self.r_outer_m
        NA = np.sqrt(n_core**2 - n_clad**2)
        return (2 * np.pi * a_m / lam_m) * NA

    def num_modes_approx(self, wavelength_nm: float) -> np.ndarray:
        """Approximate number of guided modes (V^2/2 for step-index)."""
        V = self.v_number(wavelength_nm)
        return np.maximum(1, V**2 / 2)

    def summary(self) -> str:
        """Return a summary of the axon geometry."""
        lines = [
            f"Myelinated Axon Geometry",
            f"  Axon radius:        {self.r_axon_um:.3f} um",
            f"  Outer radius:       {self.r_outer_um:.3f} um",
            f"  g-ratio:            {self.g_ratio:.3f}",
            f"  Myelin thickness:   {self.myelin_thickness_um:.3f} um",
            f"  Lamellae count:     {self.n_lamellae}",
            f"  Internode length:   {self.internode_length_mm:.2f} mm",
            f"  Node length:        {self.node_length_um:.2f} um",
        ]
        return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("Track 03: Waveguide Constants and Reference Values")
    print("=" * 60)

    axon = AxonGeometry(r_axon_um=0.5, g_ratio=0.7)
    print(axon.summary())
    print()

    wavelengths = [400, 500, 550, 600, 700]
    print(f"{'lambda (nm)':>12} {'n_myelin':>10} {'n_axoplasm':>12} {'n_ecf':>8} {'V-number':>10} {'N_modes':>8}")
    for lam in wavelengths:
        nm = n_myelin(lam)
        na = n_axoplasm(lam)
        ne = n_ecf(lam)
        V = axon.v_number(lam)
        Nm = axon.num_modes_approx(lam)
        print(f"{lam:>12.0f} {float(nm):>10.4f} {float(na):>12.4f} {float(ne):>8.4f} {float(V):>10.2f} {float(Nm):>8.0f}")

    print()
    NA_inner = np.sqrt(N_MYELIN**2 - N_AXOPLASM**2)
    NA_outer = np.sqrt(N_MYELIN**2 - N_ECF**2)
    print(f"Numerical Aperture (myelin-axoplasm): {NA_inner:.4f}")
    print(f"Numerical Aperture (myelin-ECF):      {NA_outer:.4f}")
