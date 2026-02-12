"""
Biophoton emission model: ROS spectrum, disease-enhanced emission,
and waveguide-filtered output.

Combines the intrinsic emission spectrum from reactive oxygen species
with the waveguide transmission properties of the myelin sheath to
predict what a detector would actually see.
"""

from __future__ import annotations

import numpy as np

from . import constants as C
from .axon import AxonGeometry
from .demyelination import DemyelinationState, hill_response
from .waveguide import (
    sefati_zeng_peak,
    transfer_matrix_transmission,
    attenuation_db_per_cm,
)


def ros_spectrum(wavelength_nm: np.ndarray) -> np.ndarray:
    """Baseline ROS emission spectrum from healthy neural tissue.

    Modeled as a sum of Gaussians corresponding to known ROS emission lines:
    singlet oxygen, excited carbonyls, lipid peroxidation products.

    Returns spectral radiance in arbitrary units (normalized so peak ≈ 1).
    """
    lam = np.atleast_1d(wavelength_nm).astype(np.float64)
    spectrum = np.zeros_like(lam)

    for center, fwhm, amplitude, _species in C.ROS_COMPONENTS:
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        spectrum += amplitude * np.exp(-0.5 * ((lam - center) / sigma) ** 2)

    # Normalize peak to 1
    peak = spectrum.max()
    if peak > 0:
        spectrum /= peak

    return spectrum


def disease_emission(
    state: DemyelinationState,
    wavelength_nm: np.ndarray,
    hill_n: float | None = None,
    hill_k: float | None = None,
    hill_smax: float | None = None,
) -> np.ndarray:
    """Emission spectrum from demyelinated tissue.

    Demyelination causes:
    1. Increased ROS production (oxidative stress from immune attack + exposed axon)
    2. Spectral shift: more lipid peroxidation products (blue-shifted carbonyl)
    3. Broader spectrum from heterogeneous damage

    The Hill equation modulates the overall intensity enhancement.

    Parameters
    ----------
    hill_n : float or None
        Hill coefficient (steepness). Defaults to 2.5.
    hill_k : float or None
        Half-maximal damage level. Defaults to 0.35.
    hill_smax : float or None
        Maximum enhancement factor. Defaults to 8.0.
    """
    lam = np.atleast_1d(wavelength_nm).astype(np.float64)
    base = ros_spectrum(lam)

    _n = hill_n if hill_n is not None else 2.5
    _k = hill_k if hill_k is not None else 0.35
    _smax = hill_smax if hill_smax is not None else 8.0

    # Intensity enhancement via Hill equation
    enhancement = hill_response(
        state.severity,
        s_base=1.0,
        s_max=_smax,
        n=_n,
        k=_k,
    )

    # Spectral broadening from heterogeneous damage (rho component)
    if state.rho > 0:
        # Convolve with broader kernel → effectively add a smeared component
        broadening_sigma = state.rho * 30  # nm of additional broadening
        broad_component = np.zeros_like(lam)
        for center, fwhm, amplitude, _ in C.ROS_COMPONENTS:
            sigma = (fwhm + broadening_sigma * 2) / (2 * np.sqrt(2 * np.log(2)))
            broad_component += amplitude * np.exp(-0.5 * ((lam - center) / sigma) ** 2)
        peak = broad_component.max()
        if peak > 0:
            broad_component /= peak
        base = (1 - state.rho * 0.5) * base + state.rho * 0.5 * broad_component

    # Extra blue-shifted component from acute lipid peroxidation
    if state.alpha > 0.3:
        perox_center = 420  # nm, excited carbonyl peak
        perox_sigma = 40
        perox_amplitude = (state.alpha - 0.3) / 0.7  # ramps 0→1 as alpha: 0.3→1.0
        base += 0.3 * perox_amplitude * np.exp(-0.5 * ((lam - perox_center) / perox_sigma) ** 2)

    return base * enhancement


def confound_emission(
    state: DemyelinationState,
    wavelength_nm: np.ndarray,
    gliosis_factor: float = 0.0,
    immune_infiltration: float = 0.0,
    autofluorescence_alpha: float = 0.0,
) -> np.ndarray:
    """Emission from non-myelin-specific sources that could confound measurement.

    Parameters
    ----------
    gliosis_factor : float
        0-1, fraction of signal from reactive glia (astrocyte/microglia ROS).
    immune_infiltration : float
        0-1, immune cell density (macrophage/T-cell respiratory burst).
    autofluorescence_alpha : float
        Lipofuscin accumulation rate (age-dependent autofluorescence).

    Returns spectrum array same shape as wavelength_nm.
    """
    lam = np.atleast_1d(wavelength_nm).astype(np.float64)
    confound = np.zeros_like(lam)

    # Gliosis: reactive astrocytes produce ROS with slightly different spectrum
    # Shifted toward blue (more superoxide, less lipid peroxidation)
    if gliosis_factor > 0:
        glia_center = 420.0  # nm
        glia_sigma = 60.0
        confound += gliosis_factor * 0.5 * np.exp(-0.5 * ((lam - glia_center) / glia_sigma) ** 2)

    # Immune infiltration: macrophage respiratory burst (broad, peaks ~500 nm)
    if immune_infiltration > 0:
        immune_center = 500.0
        immune_sigma = 80.0
        confound += immune_infiltration * 0.8 * np.exp(-0.5 * ((lam - immune_center) / immune_sigma) ** 2)

    # Autofluorescence: lipofuscin has broad emission peaking ~600 nm
    if autofluorescence_alpha > 0:
        lipo_center = 600.0
        lipo_sigma = 100.0
        confound += autofluorescence_alpha * 0.3 * np.exp(-0.5 * ((lam - lipo_center) / lipo_sigma) ** 2)

    return confound


def waveguide_filtered_emission(
    axon: AxonGeometry,
    state: DemyelinationState,
    wavelength_nm: np.ndarray,
    propagation_length_cm: float = 0.1,
    hill_n: float | None = None,
    hill_k: float | None = None,
    hill_smax: float | None = None,
) -> np.ndarray:
    """What actually escapes the tissue: emission × waveguide filtering × leakage.

    For healthy myelin: most light is guided along the axon; only evanescent
    leakage and scattering escape transversely → low external signal.

    For damaged myelin: waveguide is disrupted, more light leaks out
    transversely → higher external signal at the detector.

    This is the key insight: demyelination is detectable because it
    *increases* the externally measurable biophoton signal.
    """
    lam = np.atleast_1d(wavelength_nm).astype(np.float64)

    # Source emission
    source = disease_emission(state, lam, hill_n=hill_n, hill_k=hill_k, hill_smax=hill_smax)

    # Waveguide transmission with damaged myelin
    effective_wraps = state.effective_wraps(axon.n_wraps)
    if effective_wraps > 0:
        T_guided = transfer_matrix_transmission(axon, lam, n_wraps_override=effective_wraps)
    else:
        # No myelin → no waveguiding → all light escapes
        T_guided = np.zeros_like(lam)

    # Attenuation along propagation path
    atten = attenuation_db_per_cm(lam)
    propagation_factor = 10 ** (-atten * propagation_length_cm / 10)

    # What's guided stays inside; what leaks is what we detect externally.
    # Leakage fraction: 1 - T_guided for transverse escape
    # Plus scattering losses from propagation
    guided_and_lost = T_guided * (1 - propagation_factor)  # scattered from guided modes
    direct_leakage = (1 - T_guided)  # immediately escapes sheath

    # Gap contributions: at gaps in myelin, all light escapes
    gap_fraction = state.effective_gap_fraction()
    total_leakage = (1 - gap_fraction) * (direct_leakage + guided_and_lost * 0.3) + gap_fraction

    # Scale by baseline emission rate
    external_signal = source * total_leakage * C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S

    return external_signal


def compute_feature_vector(
    axon: AxonGeometry,
    state: DemyelinationState,
    wavelength_nm: np.ndarray,
    rng: np.random.Generator | None = None,
    animal_cv: float = 0.0,
) -> dict[str, float]:
    """Compute the 6-feature diagnostic vector for a single measurement.

    Features:
    1. total_intensity: integrated photon count across spectrum
    2. peak_wavelength: wavelength of maximum emission (nm)
    3. spectral_width: FWHM of emission peak (nm)
    4. temporal_variance: shot noise + biological fluctuation
    5. coherence_degree: fraction of coherent (guided) vs. scattered light
    6. polarization_ratio: linear polarization degree (guided modes are polarized)

    Parameters
    ----------
    animal_cv : float
        Coefficient of variation for biological variability across animals.
        When > 0, multiplies total_intensity by a lognormal factor.
    """
    if rng is None:
        rng = np.random.default_rng()

    lam = np.atleast_1d(wavelength_nm).astype(np.float64)
    spectrum = waveguide_filtered_emission(axon, state, lam)

    # 1. Total intensity (with Poisson measurement noise + biological variability)
    true_intensity = float(np.trapezoid(spectrum, lam))
    if animal_cv > 0:
        true_intensity *= rng.lognormal(0, animal_cv)
    total_intensity = float(rng.poisson(max(1, true_intensity)))

    # 2. Peak wavelength (with spectral resolution jitter ~5 nm)
    peak_idx = np.argmax(spectrum)
    peak_wavelength = float(lam[peak_idx]) + rng.normal(0, 5.0)

    # 3. Spectral width (FWHM, with measurement uncertainty)
    half_max = spectrum[peak_idx] / 2
    above_half = lam[spectrum >= half_max]
    raw_width = float(above_half[-1] - above_half[0]) if len(above_half) > 1 else 50.0
    spectral_width = max(10.0, raw_width + rng.normal(0, raw_width * 0.05))

    # 4. Temporal variance: Poisson noise + biological fluctuation
    poisson_var = true_intensity  # Var[Poisson] = mean
    bio_var = (state.rho * true_intensity * 0.1) ** 2
    temporal_variance = max(1.0, (poisson_var + bio_var) * rng.lognormal(0, 0.1))

    # 5. Coherence degree: healthy myelin guides coherent modes; damage reduces coherence
    effective_wraps = state.effective_wraps(axon.n_wraps, rng)
    coherence_degree = float(np.clip(
        effective_wraps / max(axon.n_wraps, 1) + rng.normal(0, 0.05), 0, 1
    ))

    # 6. Polarization ratio: guided modes are linearly polarized
    # Disrupted waveguide → depolarization
    polarization_ratio = coherence_degree * 0.8 + rng.normal(0, 0.03)
    polarization_ratio = float(np.clip(polarization_ratio, 0, 1))

    return {
        "total_intensity": total_intensity,
        "peak_wavelength": peak_wavelength,
        "spectral_width": spectral_width,
        "temporal_variance": temporal_variance,
        "coherence_degree": coherence_degree,
        "polarization_ratio": polarization_ratio,
    }
