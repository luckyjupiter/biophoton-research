# Track 06: Demyelination & Pathology -- Progress Log

## 2026-02-11: Initial Build

### Completed

**Source code** (`src/`):

1. **constants.py** -- Physical constants and parameters for all models:
   - Refractive indices (myelin 1.44, axoplasm 1.38, ECF 1.34)
   - Myelin geometry (bilayer thickness, g-ratio, internode length)
   - Waveguide optics (52.3 nm/layer shift, junction loss, propagation loss)
   - M-Phi framework parameters (g_PhiPsi, kappa, Psi)
   - Oxidative stress emission wavelengths (singlet O2, triplet carbonyls)
   - Disease-specific timescales (EAE, cuprizone, Wallerian, LPC)
   - MS subtype parameters (RRMS relapse rate, SPMS/PPMS annual loss)
   - Kappa subcomponents (thermal, structural, ROS, inflammatory)
   - Dose-response Hill equation parameters
   - Detector specifications (dark count, QE, integration time)

2. **demyelination_progression.py** -- Core demyelination model:
   - Sigmoid trajectories for thickness (alpha), continuity (gamma), regularity (rho)
   - Effective refractive index under pathology
   - Operating wavelength shift (blueshift with layer loss)
   - Propagation loss (dB/mm) from intrinsic + junction scattering
   - Coherence field ODE: dLambda/dt = g|Psi|^2*Phi - kappa*Lambda
   - ODE solver with time-dependent kappa(t)
   - Hill dose-response for emission vs demyelination fraction
   - 2x3 panel progression figure + coherence degradation figure

3. **ms_subtypes.py** -- MS subtype modeling:
   - RRMS: Poisson-distributed relapses with partial recovery (sawtooth)
   - SPMS: Exponential decay from reduced baseline + chronic inflammation
   - PPMS: Steady exponential decline from onset
   - Biophoton signature computation for all subtypes
   - 3x3 panel comparison figure + overlay figure

4. **kappa_decomposition.py** -- Decoherence rate decomposition:
   - kappa_thermal: Arrhenius-like temperature dependence
   - kappa_structural: 1/m^2 scaling with myelin integrity
   - kappa_ROS: Linear scaling with reactive oxygen species
   - kappa_inflammatory: Hill-like activation with threshold
   - Five disease scenarios (healthy, mild, moderate, severe, acute relapse)
   - Stacked bar chart + sensitivity analysis figures

5. **biomarker_predictions.py** -- Diagnostic biomarker analysis:
   - Simulated healthy/diseased measurement distributions
   - ROC curve computation for 5 biomarkers (photon count, spectral shift,
     SO2/carbonyl ratio, g^(2)(0), combined score)
   - Multi-stage analysis (preclinical through active relapse)
   - AUC heatmap and sensitivity curves vs severity
   - Testable predictions report generation

6. **experimental_protocol.py** -- Experimental design tools:
   - Power analysis (sample size for given effect size and power)
   - Shot-noise-limited SNR calculation
   - Integration time requirements
   - EAE timeline predictions (5 time points)
   - Cuprizone timeline predictions (7 time points)
   - Formatted protocol document generation

7. **generate_all_figures.py** -- Master script to run everything

**Figures** (9 total):
- demyelination_progression.png: 2x3 panel (alpha/gamma/rho, n_eff, wavelength, loss, transmission, dose-response)
- coherence_field_degradation.png: Lambda(t) and kappa(t) under progressive demyelination
- ms_subtype_comparison.png: 3x3 panel (RRMS, SPMS, PPMS x myelin/wavelength/coherence)
- ms_subtype_overlay.png: 2x2 overlay comparing all three subtypes
- kappa_decomposition.png: Stacked bars + coherence for 5 disease scenarios
- kappa_sensitivity.png: 2x2 sensitivity of each kappa component
- biomarker_roc_curves.png: ROC curves for 5 biomarkers at 5 disease stages + AUC heatmap
- biomarker_sensitivity.png: AUC and Cohen's d vs severity for all biomarkers
- power_analysis.png: Power curves + integration time requirements

**Results** (2 documents):
- testable_predictions.txt: Quantitative predictions with AUC and effect sizes
- experimental_protocol.txt: Three-experiment protocol (EAE, cuprizone, LPC)

### Key Quantitative Results

**Kappa decomposition across disease states:**

| Scenario | kappa_total | Lambda_ss |
|----------|-------------|-----------|
| Healthy | 0.0400 | 0.025000 |
| Mild (early MS) | 0.2081 | 0.004805 |
| Moderate (active MS) | 0.4986 | 0.002006 |
| Severe (late MS) | 0.4113 | 0.002431 |
| Acute relapse | 0.6613 | 0.001512 |

**Coherence degradation:** Lambda drops from 1.0 to ~0.02 over 20 weeks
of progressive demyelination (kappa increasing as 1/alpha^2).

**Most sensitive biomarker:** Combined multi-parameter score (AUC > 0.8
at moderate disease), followed by photon count (emission intensity).

**Least sensitive biomarker:** g^(2)(0) photon correlations -- requires
severe demyelination for reliable detection.

### Dependencies
- Track 03 (waveguide physics): Refractive indices, mode structure, 52.3 nm/layer rule
- Track 04 (quantum optics): g^(2)(0) predictions, entangled pair production
- Track 05 (signal-to-noise): Detector specifications, integration times
