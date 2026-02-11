"""
Axon geometry model: diameter, g-ratio, myelin wraps, guided modes.

The axon + myelin sheath forms a cylindrical optical waveguide.
The V-number determines how many electromagnetic modes can propagate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import constants as C


@dataclass
class AxonGeometry:
    """Myelinated axon modeled as a step-index cylindrical waveguide.

    Parameters
    ----------
    diameter_um : float
        Outer diameter of the myelinated fiber (μm).
    g_ratio : float
        Ratio of inner (axon) to outer (fiber) diameter. Typical 0.6–0.8.
    """

    diameter_um: float
    g_ratio: float

    # Derived quantities (set in __post_init__)
    axon_diameter_um: float = field(init=False)
    myelin_thickness_um: float = field(init=False)
    n_wraps: int = field(init=False)

    def __post_init__(self):
        self.axon_diameter_um = self.diameter_um * self.g_ratio
        self.myelin_thickness_um = (self.diameter_um - self.axon_diameter_um) / 2
        self.n_wraps = max(1, round(
            self.myelin_thickness_um * 1e3 / C.LIPID_BILAYER_THICKNESS_NM
        ))

    # --- Factory methods ---

    @classmethod
    def typical_cns(cls) -> AxonGeometry:
        """Central nervous system axon (e.g. corpus callosum). ~1 μm, g=0.7."""
        return cls(diameter_um=1.0, g_ratio=0.7)

    @classmethod
    def typical_pns(cls) -> AxonGeometry:
        """Peripheral nervous system axon (e.g. sciatic nerve). ~10 μm, g=0.6."""
        return cls(diameter_um=10.0, g_ratio=0.6)

    @classmethod
    def optic_nerve(cls) -> AxonGeometry:
        """Optic nerve fiber. Small diameter ~0.7 μm, g=0.75."""
        return cls(diameter_um=0.7, g_ratio=0.75)

    # --- Waveguide optics ---

    def v_number(self, wavelength_nm: float) -> float:
        """Compute the V-number (normalized frequency) for a given wavelength.

        V = (π · d / λ) · √(n_clad² - n_core²)

        For the myelin waveguide: cladding = myelin (n=1.44), core = axon (n=1.38).
        A higher V-number means more guided modes.
        """
        d_nm = self.axon_diameter_um * 1e3  # μm → nm
        na = math.sqrt(C.N_MYELIN**2 - C.N_AXON**2)
        return math.pi * d_nm / wavelength_nm * na

    def num_modes(self, wavelength_nm: float = 500.0) -> int:
        """Approximate number of guided modes at the given wavelength.

        For a step-index fiber: M ≈ V²/2 (for V >> 1), minimum 1 if V > 2.405.
        """
        v = self.v_number(wavelength_nm)
        if v < 2.405:
            return 1 if v > 0 else 0
        return max(1, int(v**2 / 2))

    def cutoff_wavelength_nm(self) -> float:
        """Longest wavelength that supports at least the fundamental mode (V=2.405)."""
        d_nm = self.axon_diameter_um * 1e3
        na = math.sqrt(C.N_MYELIN**2 - C.N_AXON**2)
        return math.pi * d_nm * na / 2.405

    def internode_length_um(self) -> float:
        """Typical internode (myelinated segment) length ≈ 100× outer diameter."""
        return self.diameter_um * 100

    def __repr__(self) -> str:
        return (
            f"AxonGeometry(d={self.diameter_um}μm, g={self.g_ratio}, "
            f"wraps={self.n_wraps}, modes@500nm={self.num_modes(500)})"
        )
