"""
Demyelination state modeling for disease progression simulation.

Parameterizes myelin damage with three orthogonal axes:
  alpha (0→1): thickness loss fraction (0 = healthy, 1 = fully stripped)
  gamma (0→1): continuity loss (gap probability at each node)
  rho   (0→1): regularity loss (variance in remaining thickness)

Includes timeline models for common experimental demyelination paradigms.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import constants as C


@dataclass
class DemyelinationState:
    """Three-axis parameterization of myelin damage.

    Parameters
    ----------
    alpha : float
        Thickness loss (0 = full myelin, 1 = completely stripped).
    gamma : float
        Continuity loss / gap probability at nodes (0 = intact, 1 = all gaps).
    rho : float
        Regularity loss / thickness variance (0 = uniform, 1 = maximally irregular).
    """

    alpha: float = 0.0
    gamma: float = 0.0
    rho: float = 0.0

    def __post_init__(self):
        for name, val in [("alpha", self.alpha), ("gamma", self.gamma), ("rho", self.rho)]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {val}")

    @property
    def is_healthy(self) -> bool:
        return self.alpha == 0.0 and self.gamma == 0.0 and self.rho == 0.0

    @property
    def severity(self) -> float:
        """Scalar summary of overall damage (Euclidean norm / √3)."""
        return np.sqrt(self.alpha**2 + self.gamma**2 + self.rho**2) / np.sqrt(3)

    def effective_wraps(self, base_wraps: int, rng: np.random.Generator | None = None) -> int:
        """Number of myelin wraps remaining after damage.

        If rho > 0, adds Gaussian noise to the remaining thickness.
        """
        mean_remaining = base_wraps * (1 - self.alpha)
        if self.rho > 0 and rng is not None:
            sigma = self.rho * base_wraps * 0.3  # 30% of total at max irregularity
            mean_remaining = rng.normal(mean_remaining, sigma)
        return max(0, round(mean_remaining))

    def effective_gap_fraction(self) -> float:
        """Fraction of nodes with complete myelin gaps."""
        return self.gamma

    def __repr__(self) -> str:
        return f"DemyelinationState(α={self.alpha:.2f}, γ={self.gamma:.2f}, ρ={self.rho:.2f})"


# --- Hill equation dose-response ---

def hill_response(
    damage: float,
    s_base: float = 1.0,
    s_max: float = 10.0,
    n: float = C.HILL_COEFFICIENT_DEFAULT,
    k: float = C.HILL_K_HALF_DEFAULT,
) -> float:
    """Hill equation for dose-dependent signal enhancement.

    S(D) = S_base + (S_max - S_base) · D^n / (D^n + K^n)

    Models the sigmoidal increase in biophoton emission as demyelination
    increases oxidative stress.

    Parameters
    ----------
    damage : float
        Damage level (0–1), typically DemyelinationState.severity.
    s_base : float
        Baseline signal (healthy tissue).
    s_max : float
        Maximum signal at full damage.
    n : float
        Hill coefficient (steepness of transition).
    k : float
        Half-maximal damage level.
    """
    if damage <= 0:
        return s_base
    return s_base + (s_max - s_base) * damage**n / (damage**n + k**n)


# --- Experimental timeline models ---

def cuprizone_timeline(week: float) -> DemyelinationState:
    """Cuprizone (bis-cyclohexanone oxaldihydrazone) toxic demyelination model.

    Standard 6-week protocol:
    - Weeks 0–1: minimal change
    - Weeks 2–3: progressive demyelination
    - Weeks 4–5: peak demyelination (corpus callosum nearly bare)
    - Week 6: onset of spontaneous remyelination if cuprizone removed

    Extended (12-week) prevents remyelination and causes chronic damage.
    """
    week = max(0.0, float(week))

    # Alpha: sigmoid reaching ~0.85 at week 5, shifted so ≈0 at week 0
    alpha = 0.9 / (1 + np.exp(-1.5 * (week - 3.5)))
    alpha -= 0.9 / (1 + np.exp(-1.5 * (0 - 3.5)))  # subtract baseline so week 0 = 0

    # Gamma: gap formation lags slightly behind thinning
    gamma = 0.7 / (1 + np.exp(-1.2 * (week - 4.0)))
    gamma -= 0.7 / (1 + np.exp(-1.2 * (0 - 4.0)))

    # Rho: irregularity peaks mid-process then decreases as myelin is uniformly lost
    rho = 0.6 * np.exp(-0.5 * ((week - 3.0) / 1.5) ** 2)
    rho -= 0.6 * np.exp(-0.5 * ((0 - 3.0) / 1.5) ** 2)  # zero at week 0

    return DemyelinationState(
        alpha=float(np.clip(alpha, 0, 1)),
        gamma=float(np.clip(gamma, 0, 1)),
        rho=float(np.clip(rho, 0, 1)),
    )


def eae_timeline(day: float) -> DemyelinationState:
    """Experimental Autoimmune Encephalomyelitis (EAE) model.

    Relapsing-remitting course:
    - Days 0–10: induction phase (immunization + adjuvant)
    - Days 10–15: first attack (acute inflammation + demyelination)
    - Days 15–25: partial remission
    - Days 25–35: relapse (often more severe)
    - Day 35+: chronic phase

    The oscillation models immune-mediated attack/repair cycles.
    """
    day = max(0.0, float(day))

    # Baseline progressive component
    progressive = 0.3 / (1 + np.exp(-0.15 * (day - 20)))

    # Relapsing-remitting oscillation
    attack_1 = 0.5 * np.exp(-0.5 * ((day - 12) / 2.0) ** 2)
    attack_2 = 0.6 * np.exp(-0.5 * ((day - 30) / 3.0) ** 2)
    relapsing = attack_1 + attack_2

    alpha = min(progressive + relapsing * 0.8, 1.0)
    gamma = min(progressive + relapsing * 0.5, 1.0)
    rho = min(relapsing * 0.7, 1.0)

    return DemyelinationState(alpha=alpha, gamma=gamma, rho=rho)


def lysolecithin_timeline(day: float) -> DemyelinationState:
    """Lysolecithin (lysophosphatidylcholine) focal injection model.

    - Day 0: injection into white matter tract
    - Days 1–3: rapid demyelination at injection site
    - Days 3–7: complete focal demyelination, debris clearance
    - Days 7–21: spontaneous remyelination (thin sheaths)
    - Day 28+: remyelination largely complete (thinner myelin)

    Produces the most spatially and temporally defined lesion.
    """
    day = max(0.0, float(day))

    # Rapid onset, then remyelination
    if day < 1:
        alpha = 0.3 * day
    elif day < 5:
        alpha = 0.3 + 0.65 * (day - 1) / 4  # ramps to 0.95
    elif day < 7:
        alpha = 0.95
    else:
        # Remyelination: exponential recovery, but never fully back
        alpha = 0.95 * np.exp(-0.08 * (day - 7)) + 0.15

    gamma = min(alpha * 0.6, 1.0)
    rho = 0.4 * np.exp(-0.5 * ((day - 4) / 2.0) ** 2) if day < 14 else 0.05

    return DemyelinationState(
        alpha=min(max(alpha, 0.0), 1.0),
        gamma=min(max(gamma, 0.0), 1.0),
        rho=min(max(rho, 0.0), 1.0),
    )
