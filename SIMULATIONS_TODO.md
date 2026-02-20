# Simulation Improvements from Telegram Reference Pack

Based on scraped research from https://t.me/biophotonresearch

## What I Just Built

### `models/cuprizone_v2.py` - Improved G-Ratio Model

**Uses literature data instead of abstract alpha:**
- Lindner et al. 2008 EM measurements: g=0.802 (healthy), 0.926 (week 4), 0.964 (week 6)
- Sachs et al. 2014 remyelination timeline
- Regional heterogeneity: splenium (fast recovery), DHC (slow), genu (moderate)
- Permanent residual: remyelinated settles at g=0.825-0.840 (never returns to 0.802)

**Predictions:**
- Healthy (week 0): g=0.802 → 794nm ✓
- Peak demyelination (week 6): g=0.964 → 584nm ✓ (target 581nm)
- Stable remyelinated: g=0.849 → 852nm ✗ (target 768nm)

**What works:**
- Demyelination phase matches reference pack predictions
- Regional differences implemented
- Permanent blue shift concept included

**What's broken:**
- Remyelination spectral prediction is ~84nm too red
- Quadratic fit assumes same optical properties for original vs remyelinated myelin
- Need to model disordered remyelinated myelin separately

## Priority Improvements (From Reference Pack)

### 1. Two-Mechanism Spectral Model ⚠️ CRITICAL

**Problem:** Current model assumes spectral shift = pure waveguide geometry
**Reality:** Two independent mechanisms (Dai 2020 synaptosome data):
- Metabolic shift (~35nm): ROS/oxidative stress changes, myelin-independent
- Waveguide shift (~31nm): geometric mode cutoff, myelin-dependent

**Action:**
```python
def two_mechanism_spectral_shift(g_ratio, metabolic_stress_factor):
    waveguide_shift = waveguide_mode_cutoff(g_ratio)  # from geometry
    metabolic_shift = 35 * metabolic_stress_factor    # from oxidative stress
    return waveguide_shift + metabolic_shift
```

**Evidence:**
- Dai's blueshift occurs in myelin-free synaptosomes
- Partially reversed by ifenprodil (NMDA blocker) → metabolic component
- Our waveguide model alone can't explain this

### 2. Proper Waveguide Mode Solver

**Current:** Empirical quadratic fit to reference points
**Needed:** Actual eigenmode solver for cylindrical dielectric waveguide

**Physics:**
- V-number: V = (2π/λ) × r × √(n_core² - n_clad²)
- n_core = 1.44 (myelin), n_clad = 1.34 (interstitial), n_axon = 1.38
- As r (myelin thickness) decreases → V decreases → higher modes cut off
- Cutoff condition determines minimum λ that can propagate

**References in pack:**
- Kumar et al. 2016: FDTD simulation (Lumerical MODE)
- Zeng et al. 2022: Electromagnetic modeling
- Frede et al. 2023: Multi-node transmission

**Tools:**
- Python: `mpmath.besseljn` for Bessel functions
- Or interface with Lumerical MODE via their Python API
- Or use finite-element solver (FEniCS, COMSOL)

### 3. Nanoantenna vs ROS Emission Balance

**Current problem:** Our model shows nanoantenna dominates ROS by 177×
**Literature balance:** Both sources important, different spatial patterns

**Zangari model (from reference pack):**
- Nanoantenna emission: directional, tiny ~10⁻⁵ photons/AP, coherent
- ROS chemiluminescence: isotropic, dominant, incoherent
- Both modulated by demyelination but differently

**Action:**
- Separate external leakage (ROS-dominated) from internal relay (nanoantenna)
- External increases during demyelination (more oxidative stress)
- Internal relay decreases (waveguide broken)
- Dual signature: up + down simultaneously

### 4. Disordered Remyelinated Myelin Model

**Key insight from reference pack:**
> "Remyelinated myelin has a disorganized and inhomogeneous appearance"

**Optical consequences:**
- Higher scattering loss (thin + irregular layers)
- Modified effective refractive index (not same as original healthy myelin)
- This explains why g=0.825 doesn't follow the demyelination curve

**Action:**
```python
def effective_n_myelin(g_ratio, is_remyelinated, disorder_factor):
    n_base = 1.44  # healthy myelin
    if is_remyelinated:
        # Disordered myelin has lower effective n due to scattering
        n_eff = n_base * (1 - 0.05 * disorder_factor)
    else:
        n_eff = n_base
    return n_eff
```

### 5. Early Remyelination Noise (Week 6-8)

**From Kipp et al. 2024:**
> "Group mean g-ratios do not change as expected during early stages"

**Current model:** Smooth exponential recovery
**Reality:** High variance, non-monotonic during week 6-8

**Action:** Already implemented `add_noise=True` parameter, but need to:
- Add more realistic noise model (bimodal distribution?)
- Model axon diameter changes during early remyelination
- This is important for experimental design (need larger N during this phase)

### 6. Detection Sensitivity Gap

**From reference pack:**
> "Detection gap: all current detectors fall off at ~850nm but human peak is 865nm"

**Impact on our simulations:**
- Detector quantum efficiency in models/detection.py needs spectral response curve
- InGaAs detectors needed for human brain (865nm peak)
- Si PMTs miss the red tail

**Action:**
```python
def detector_efficiency_curve(wavelength_nm, detector_type):
    if detector_type == "Si_PMT":
        # Efficiency drops rapidly >800nm
        return gaussian_response(wavelength_nm, peak=500, fwhm=400, cutoff=850)
    elif detector_type == "InGaAs":
        # Extends to 1100nm
        return gaussian_response(wavelength_nm, peak=900, fwhm=500, cutoff=1100)
```

### 7. Liu et al. 2024 Cavity QED Model

**New paper in reference pack:**
> "Entangled biphoton generation in the myelin sheath" - cavity QED framework

**What they claim:**
- C-H bond vibrations in myelin lipid tails generate entangled photon pairs
- Myelin cavity as quantum environment

**Our response:**
- We already found entanglement vanishingly small (Tegmark decoherence times)
- But worth checking their math for the classical emission rate boost
- Their cavity model might improve our ROS emission spectrum

**Action:** Read Liu et al. 2024 full text, extract emission rate formulas if useful

### 8. Regional Heterogeneity Distribution

**Current:** Three discrete regions (splenium, DHC, genu)
**Needed:** Spatial distribution across full corpus callosum

**From reference pack:**
- Rostro-caudal gradient
- At any timepoint, distribution of g-ratios (not single value)

**Action:**
```python
def spatial_gratio_distribution(week, position_rostral_to_caudal):
    # position: 0 (rostral/genu) → 1 (caudal/splenium)
    # More demyelination toward caudal
    severity_gradient = 0.5 + 0.5 * position
    base_g = cuprizone_gratio(week, region="genu")
    peak_g = cuprizone_gratio(week, region="splenium")
    return base_g + severity_gradient * (peak_g - base_g)
```

### 9. Chronic vs Acute Timeline

**Reference pack provides two scenarios:**
- Acute: 6 weeks cuprizone → recovery
- Chronic: 13 weeks cuprizone → impaired recovery

**Current model:** Only acute
**Needed:** Separate timeline for chronic with:
- More severe peak demyelination
- Slower recovery
- Lower final plateau (~720-740nm vs ~768nm for acute)

## Non-Simulation Improvements

### A. Experimental Validation Data

**From reference pack - papers to get full text:**
1. ✓ Lindner et al. 2008/2009 (Glia) - have g-ratio data
2. ⚠️ Sachs et al. 2014 (ASN Neuro) - need MOG quantification timeline
3. ⚠️ Tang et al. 2016 (PNAS) - need actual spectrum data (not just peak)
4. ⚠️ Liu et al. 2019 (Adv Funct Mater) - refractive index measurements
5. ⚠️ Zeng et al. 2022 (Applied Optics) - EM waveguide model details

**Action:** Download papers, extract numerical data, add to constants.py

### B. Therapeutic Angle

**From reference pack:**
> "Transcranial pulsed focused ultrasound accelerates remyelination"

**Our angle:**
- If ultrasound works, optical modulation at waveguide resonance frequencies might too
- Optical stimulation during weeks 7-10 (active remyelination phase)
- Target the ARROW resonance frequencies of remyelinating tissue

**Simulation needed:**
- Optimal wavelength for thin remyelinating myelin (g~0.88-0.92)
- Pulse timing to match OPC differentiation cycle
- Power levels (LLLT therapeutic window 450-910nm)

### C. Biomarker Application

**Key advantage (from reference pack):**
> "Spectral centroid measures functional waveguide restoration, not just myelin presence"

**Simulation:**
- Distinguish remyelinated (g=0.83, disordered) from healthy (g=0.80, organized)
- MRI can't tell the difference
- Spectral signature can: 768nm vs 794nm

## Implementation Priority

1. **Two-mechanism model** (metabolic + waveguide) — fixes remyelination prediction ⚠️
2. **Proper mode solver** — replaces empirical fit with physics
3. **Disordered remyelinated myelin** — separate optical properties
4. **Detector spectral response** — realistic measurement simulation
5. **Spatial distribution** — g-ratio field instead of single value
6. **Chronic timeline** — add 13-week impaired recovery scenario
7. **Liu cavity QED** — check if useful for emission rates
8. **Experimental data** — add actual spectral measurements to constants

## Files to Create/Modify

- `models/waveguide_modes.py` - proper eigenmode solver
- `models/emission_mechanisms.py` - separate nanoantenna vs ROS
- `models/cuprizone_v2.py` - add two-mechanism model ✓ (created)
- `models/detection.py` - add spectral response curves
- `models/constants.py` - add literature data from reference pack
- `docs/calibration_issues.md` - document the 100nm offset and 3× magnitude problems

## Questions for You

1. Want me to build the proper waveguide mode solver next?
2. Should I prioritize fixing the remyelination calibration (two-mechanism model)?
3. Do you have access to the full text of the papers in the reference pack?
4. Want visualizations comparing different models (simple/quadratic/waveguide/two-mechanism)?
