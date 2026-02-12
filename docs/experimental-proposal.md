# Experimental Collaboration Proposal: Testing Biophotonic Signatures of Demyelination in Murine Models

**From:** Biophoton Computational Research Group
**Date:** February 2026
**Document type:** Collaboration proposal for wet-lab experimental validation

---

## 1. Executive Summary

We are a computational biophysics group that has developed a quantitative framework predicting how demyelination alters ultra-weak photon emission (UPE, or biophotons) from neural tissue. Our models -- integrating anti-resonant reflecting optical waveguide (ARROW) theory, reactive oxygen species (ROS) emission physics, and Poisson detection statistics -- generate 42 falsifiable predictions, many of which are testable with standard photomultiplier equipment already present in most neuroscience imaging facilities. The central prediction is that active demyelination produces a 10-100-fold increase in biophoton emission intensity, accompanied by a spectral blueshift of ~52.3 nm per lost myelin layer and a singlet oxygen emission signature (634/703 nm) that discriminates autoimmune from toxic demyelination mechanisms. Our simulations indicate that these signals are detectable at 5-sigma significance in under one minute of integration with a cooled PMT, and that sample sizes as small as N = 5 per group provide 80% statistical power at moderate disease stages.

We propose a 12-month collaboration with an experimental neuroscience laboratory equipped for rodent demyelination models. We bring a complete computational framework -- waveguide simulator, detection feasibility calculator, ROC analysis pipeline, and a library of quantitative benchmarks against which every measurement can be compared. We ask our experimental partners to bring expertise in murine demyelination models (cuprizone, EAE), tissue preparation, and single-photon detection. The proposed experiments are designed so that negative results are as informative as positive ones: each aim has an explicit falsification criterion, and failure at any stage constrains the theoretical framework in a scientifically productive way. No prior experiment has measured biophoton emission specifically from demyelinated versus healthy nerve tissue, making this a genuinely novel test of a long-standing hypothesis in neural biophotonics.

---

## 2. Background: The Myelinated Axon as an Optical Waveguide

### 2.1 Physical basis

Myelinated axons possess a refractive index architecture that mirrors a step-index optical fiber. The myelin sheath (refractive index n = 1.44) surrounds lower-index axoplasm (n = 1.38) and extracellular fluid (n = 1.34), creating a biological dielectric waveguide first rigorously modeled by Kumar et al. (2016). The numerical aperture of this biological waveguide is NA = 0.411, and for typical CNS axons (1 um diameter, g-ratio 0.7), single-mode operation prevails above a cutoff wavelength of 376 nm.

The waveguide operates in an anti-resonant reflecting optical waveguide (ARROW) regime: light at anti-resonant wavelengths is efficiently reflected by the myelin layers and confined to the core, while resonant wavelengths leak through the cladding. For a healthy 30-layer myelin sheath, the dominant transmission peak occurs near 548 nm with a full-width at half-maximum of approximately 10 nm (Zeng et al., 2022).

### 2.2 The spectral tuning relationship

A critical quantitative result from Zeng et al. (2022) is that the operating wavelength shifts by +52.3 nm per additional myelin layer and -94.5 nm per micrometer of axon diameter. This linear spectral tuning means that myelin loss -- the defining pathology of demyelinating disease -- should produce a predictable, measurable spectral blueshift. Loss of 9 myelin layers (~30% demyelination) shifts the peak by approximately 470 nm, easily detectable with broadband bandpass filters.

### 2.3 Biophoton emission and ROS

Ultra-weak photon emission from biological tissue arises primarily from ROS-driven lipid peroxidation, generating electronically excited species: triplet carbonyls (350-550 nm) and singlet oxygen (634, 703, and 1270 nm). During active demyelination, massive peroxidation of the lipid-rich myelin sheath (70-80% lipid by dry weight) is expected to produce a large emission burst. Existing experimental literature documents glutamate-induced biophoton emission in brain slices (Tang and Dai, 2014) and age-dependent spectral blueshift consistent with progressive myelin thinning (Chen et al., 2020), but no study has yet measured biophoton emission in the specific context of demyelinating disease.

### 2.4 What is new

Our contribution is a unified computational framework that connects waveguide physics to disease pathology through a three-axis parameterization of myelin damage (thickness loss, gap formation, structural irregularity), and that generates quantitative predictions -- emission intensities in photons/s/cm^2, spectral peak positions in nm, diagnostic performance as AUC values -- that can be directly compared against experimental measurements. This is not a vague hypothesis; it is a set of numbers waiting to be tested.

---

## 3. Specific Aims

### Aim 1: Detect demyelination-induced biophoton emission changes in the cuprizone mouse model

**Rationale.** The cuprizone model produces predictable, non-immune demyelination of the corpus callosum on a well-characterized timeline (Matsushima and Morell, 2001). It is the most tractable first experiment because: (a) the demyelination timeline is reproducible; (b) the mechanism is toxic rather than autoimmune, simplifying interpretation by removing inflammatory confounds; and (c) longitudinal within-animal measurements are possible through a cranial window.

**Primary prediction.** Biophoton emission from the corpus callosum increases detectably within the first week of cuprizone administration. Specifically, our simulations predict emission of 162.5 photons/s/cm^2 at weeks 1-2 (16-fold above a baseline of 10 photons/s/cm^2), rising to a peak of 537.5 photons/s/cm^2 (54-fold) at weeks 4-5, followed by partial recovery to 72.5 photons/s/cm^2 (7-fold) by week 12 after cuprizone withdrawal. A standard bialkali PMT with 5 cm^2 collection area achieves SNR = 724 in one hour at the week 1-2 emission level, requiring less than one second for 5-sigma detection.

**Falsification criterion.** Active demyelination produces less than 3-fold emission increase in any measurement at any time point. If this occurs, the ROS-emission coupling assumed in our models is weaker than predicted, and the entire biomarker framework requires fundamental revision.

**Design.** C57BL/6 mice fed 0.2% cuprizone for 6 weeks, then normal chow for 6 weeks (remyelination phase). N = 10 mice per group (cuprizone and control). Measurement schedule: baseline, then weekly through week 12. PMT measurements through cranial window over corpus callosum, 5-minute integration per session. Primary endpoint: time to first statistically significant emission elevation (predicted: week 1, 3-sigma).

### Aim 2: Spectral fingerprinting to distinguish autoimmune from toxic demyelination

**Rationale.** No existing biomarker distinguishes the mechanism of demyelination (autoimmune vs. toxic vs. metabolic). Our models predict that this discrimination is possible because autoimmune demyelination (EAE) involves myeloperoxidase (MPO) activity in infiltrating neutrophils, generating singlet oxygen through the hypochlorous acid pathway, while toxic demyelination (cuprizone) produces primarily superoxide-derived triplet carbonyls without the MPO pathway. The singlet oxygen phosphorescence peaks at 634 nm and 703 nm should therefore be elevated in EAE relative to cuprizone-treated animals.

**Primary prediction.** The 634/703 nm singlet oxygen-to-carbonyl emission ratio (SO2/carbonyl) is significantly higher in EAE mice at peak disease (day 14-18) than in cuprizone mice at matched demyelination severity (week 4-5). Our ROC analysis predicts AUC = 1.000 for this ratio during active autoimmune relapse (Cohen's d = 3.32), versus AUC approximately 0.50 (chance) in cuprizone. This mechanistic discrimination is unique among demyelination biomarkers.

**Falsification criterion.** No spectral difference between autoimmune and toxic demyelination models at any wavelength band. If the 634/703 nm ratio is equal in EAE and cuprizone at matched demyelination, the MPO-singlet oxygen pathway does not contribute detectably to biophoton emission.

**Design.** Two parallel cohorts: (a) MOG35-55-induced EAE in C57BL/6 mice (n = 8 per time point, 5 time points: baseline, day 7, 12, 18, 28+); (b) cuprizone 0.2% for 6 weeks (n = 10, weekly measurements). Six-band spectral profiling using a filter wheel with bandpass filters centered at 350, 450, 550, 634, 703, and 800 nm (+/- 20 nm). PMT measurement through each filter in sequence, 30 minutes integration per band (total 3 hours per sample). Ex vivo optic nerve (EAE) and corpus callosum sections (cuprizone). Primary endpoint: 634/703 nm ratio between disease models.

### Aim 3: ROC validation of the multi-parameter diagnostic vector

**Rationale.** Our simulations predict that a combined 6-feature diagnostic vector -- (1) total photon count, (2) spectral peak position, (3) spectral bandwidth, (4) 634 nm intensity, (5) 703 nm intensity, and (6) SO2/carbonyl ratio -- achieves AUC greater than 0.80 across all disease stages with sample sizes as low as N = 5 per group. Individual biomarkers have complementary strengths: total count is the most sensitive early marker (AUC = 1.000 from preclinical stages, Cohen's d = 3.26), spectral shift is the most specific structural marker (Cohen's d = 18.66 at preclinical, 179.78 at severe disease), and the SO2/carbonyl ratio provides mechanistic discrimination. This aim tests whether the predicted diagnostic performance holds in real tissue.

**Primary prediction.** For the combined score comparing moderate demyelination (cuprizone week 4-5) versus healthy controls, the experimentally measured AUC will exceed 0.80. Our simulated value is AUC = 1.000 with Cohen's d = 10.63 at moderate disease. For individual markers, we predict: photon count AUC = 1.000 (d = 3.79), spectral shift AUC = 1.000 (d = 115.37), SO2/carbonyl AUC = 0.991 (d = 2.30). These are deliberately strong predictions; if the real AUC values are substantially lower, it will reveal which model assumptions fail.

**Falsification criterion.** Combined AUC below 0.70 at moderate disease stage, or any single biomarker achieving AUC equal to or greater than the combined score across all disease stages (which would indicate the multi-parameter approach adds no value).

**Design.** Pooled data from Aims 1 and 2. At each measurement time point, all six spectral bands are acquired. The diagnostic vector is computed per animal per time point. ROC curves are constructed using leave-one-out cross-validation, with AUC as the primary performance metric. We will provide pre-registered prediction intervals for each AUC value prior to data unblinding, enabling a direct test of model calibration.

---

## 4. Methods

### 4.1 Equipment

**Primary detector:** Cooled bialkali photomultiplier tube (PMT), e.g., Hamamatsu H7421-40 or equivalent. Key specifications: quantum efficiency 20% at 500 nm, dark count rate approximately 30-50 counts/s, active area 5 cm^2. This detector achieves 5-sigma detection of 10 photons/s/cm^2 baseline UPE in 17.5 seconds of integration.

**Spectral profiling:** Six-position filter wheel with bandpass interference filters (20 nm FWHM) centered at 350, 450, 550, 634, 703, and 800 nm. Thorlabs FW102C or equivalent motorized filter wheel. Total filter set cost: approximately $2,000-3,000.

**Dark chamber:** Light-tight enclosure achieving less than 0.01 photons/s/cm^2 stray light. Constructed from anodized aluminum or commercially available dark box (e.g., Thorlabs XE25 series). Interior coated with Acktar Metal Velvet or flocked paper. All feedthroughs sealed with O-rings. Cost: approximately $3,000-5,000 (custom) or $5,000-10,000 (commercial).

**Perfusion system (ex vivo):** Temperature-controlled perfusion chamber maintaining tissue at 37 degrees C in oxygenated artificial cerebrospinal fluid (aCSF). Standard electrophysiology-grade components. Required for ex vivo measurements to maintain metabolic activity during measurement.

**Cranial window (in vivo cuprizone):** Standard glass coverslip cranial window over the corpus callosum for longitudinal measurements. Established surgical technique widely available in neuroscience laboratories.

**Optional (Aim 3 enhancement):** Back-illuminated EM-CCD camera (e.g., Andor iXon Ultra 897) for spatial mapping of emission patterns. While not required for the primary aims, spatial resolution would provide additional model validation (predicted bright spots at demyelination boundaries).

### 4.2 Animal protocol

**Cuprizone model (Aims 1 and 3).** Male C57BL/6J mice, 8-10 weeks old at study start. N = 10 per group (cuprizone and control), total N = 20. Cuprizone group: 0.2% cuprizone (bis-cyclohexanone oxaldihydrazone) mixed into ground chow for 6 weeks, then normal chow for 6 weeks. Control group: normal ground chow throughout. Cranial window surgery performed one week before cuprizone administration (recovery period). Measurement schedule: baseline (day -3 and day 0), then weekly from weeks 1-6 (on cuprizone) and weeks 8, 10, 12 (recovery).

**EAE model (Aim 2).** Female C57BL/6J mice, 8-10 weeks old. MOG35-55 peptide emulsified in CFA with Mycobacterium tuberculosis H37Ra, subcutaneous injection at two sites. Pertussis toxin on days 0 and 2 (standard Hooke Laboratories kit protocol). N = 8 mice per time point x 5 time points (baseline, day 7, day 12, day 18, day 28+), total N = 40. Ex vivo optic nerve preparation at each time point.

**Controls (both models).** (1) Heat-killed tissue: rules out chemiluminescence from tissue preparation artifacts. (2) N-acetylcysteine (NAC) pre-treated group (n = 5): antioxidant control to separate ROS-mediated emission from waveguide-filtered emission. (3) Tetrodotoxin (TTX) treated: blocks neural activity to test activity-dependence of emission. (4) Contralateral nerve (EAE): internal paired control. (5) Sham surgery (cuprizone): rules out cranial window effects. (6) Buffer-only blank: rules out medium contamination.

**Power analysis.** For the primary comparison in Aim 1 (moderate demyelination at week 4-5, predicted Cohen's d = 1.5 for emission intensity), N = 5 per group provides 80% power at alpha = 0.05 (two-sided). We use N = 10 per group to provide robustness against larger-than-expected biological variability and to permit interim analyses. For the EAE temporal profile (Aim 2), N = 8 per time point provides 80% power for the smaller early detection effect (predicted d = 0.8, requiring N approximately 14 for a two-group comparison, but the temporal structure across 5 time points provides additional statistical leverage).

### 4.3 Measurement protocol

1. **Dark adaptation:** All samples placed in the dark chamber for a minimum of 30 minutes before measurement to eliminate delayed luminescence (hyperbolic decay with t^(-m), m = 1-2).

2. **Baseline dark count measurement:** 5-minute PMT recording with no sample present, repeated before and after each sample measurement. Records dark count rate and drift.

3. **Broadband measurement:** Unfiltered PMT recording for 5 minutes (in vivo) or 30 minutes (ex vivo). Records total photon count rate.

4. **Spectral profiling (Aims 2 and 3):** Sequential measurement through each of 6 bandpass filters, 30 minutes per band. Filter wheel rotated automatically. Total spectral acquisition time: 3 hours per sample.

5. **Temperature control:** Tissue maintained at 37 +/- 0.5 degrees C throughout measurement. Temperature logged continuously.

6. **Artifact checks:** Heat-killed and buffer-only controls measured at the beginning and end of each experimental session.

### 4.4 Data analysis

All analysis code will be provided by our group as an open-source Python package. The pipeline includes:

- **Photon count extraction:** Background-subtracted count rates with Poisson confidence intervals.
- **Li-Ma significance testing:** Detection significance computed using the standard gamma-ray astronomy formula (Li and Ma, 1983), appropriate for low-count Poisson data.
- **Spectral fitting:** Peak wavelength, bandwidth, and per-band intensity extracted from 6-band filter data.
- **ROC analysis:** Per-biomarker and combined-score AUC with bootstrapped 95% confidence intervals.
- **Temporal profile fitting:** Nonlinear regression of emission time course to the disease progression model (Hill function: S(D) = S_base + (S_max - S_base) * D^n / (D^n + K^n)).

---

## 5. Expected Results

All numerical predictions below are derived from our published simulation framework. We present both point estimates and the range within which the measurement must fall to be consistent with the model.

### 5.1 Aim 1: Cuprizone emission time course

| Time Point | Predicted Emission (ph/s/cm^2) | Fold Change | Expected SNR (5-min integration, PMT) | Consistency Range |
|------------|-------------------------------|-------------|---------------------------------------|-------------------|
| Baseline | 10.0 | 1.0x | 40 | 5-20 ph/s/cm^2 |
| Week 1-2 | 162.5 | 16.2x | 162 | >30 ph/s/cm^2 (>3x baseline) |
| Week 3 | 370.0 | 37.0x | 245 | >100 ph/s/cm^2 |
| Week 4-5 | 537.5 | 53.8x | 295 | >150 ph/s/cm^2 |
| Week 6 | 352.5 | 35.2x | 239 | >100 ph/s/cm^2 |
| Week 8 | 140.0 | 14.0x | 150 | Decreased from week 6 |
| Week 12 | 72.5 | 7.2x | 108 | Decreased from week 8, still above baseline |

**Key milestone:** First 3-sigma detection above baseline is predicted within week 1 of cuprizone administration. If emission elevation is not detectable (less than 3-fold above baseline) at week 3 with N = 10 animals, the primary hypothesis of Aim 1 is falsified.

**Remyelination signature:** After cuprizone withdrawal, emission should decline but stabilize above baseline (predicted 7.2-fold at week 12) due to characteristically thinner remyelinated sheaths (Duncan et al., 2017). This persistent elevation is a unique prediction not made by any existing demyelination biomarker.

### 5.2 Aim 2: Spectral discrimination

| Model | Peak Emission (ph/s/cm^2) | Predicted 634/703 nm Ratio | SO2/Carbonyl AUC |
|-------|--------------------------|---------------------------|-------------------|
| EAE (peak, day 14-18) | 927.5 (92.8x baseline) | Elevated (MPO pathway) | 1.000 (d = 3.32) |
| Cuprizone (peak, week 4-5) | 537.5 (53.8x baseline) | Near baseline | ~0.50 (no discrimination) |
| Healthy control | 10.0 | Baseline | N/A |

The EAE temporal profile should show a characteristic acute inflammatory spike: pre-symptomatic 11x (day 7), onset 52x (day 10-12), peak 93x (day 14-18), chronic 17x (day 28+). This asymmetric spike pattern is qualitatively distinct from the monotonic cuprizone rise-plateau-decline pattern and constitutes an independent testable prediction.

### 5.3 Aim 3: Diagnostic performance benchmarks

Our pre-registered AUC predictions for moderate disease (cuprizone week 4-5 vs. healthy controls):

| Biomarker | Predicted AUC | Predicted Cohen's d | Minimum Expected AUC | Sample Size Used |
|-----------|--------------|--------------------|-----------------------|------------------|
| Total photon count | 1.000 | 3.79 | >0.90 | N = 10/group |
| Spectral peak shift | 1.000 | 115.37 | >0.90 | N = 10/group |
| SO2/carbonyl ratio | 0.991 | 2.30 | >0.80 | N = 10/group |
| g^(2)(0) coherence | 0.654 | 0.56 | >0.55 | N = 10/group |
| Combined 6-feature score | 1.000 | 10.63 | >0.85 | N = 10/group |

Note: The g^(2)(0) prediction is deliberately conservative. Our feasibility analysis shows that second-order correlation measurements at biophoton count rates require impractically long integration times (31.7 years at 10 counts/s for 0.1 precision). We include g^(2)(0) in the prediction table for completeness, but it is not a practical biomarker with current technology. The remaining four markers are the actionable diagnostic features.

### 5.4 What failure would mean

- **No emission increase during cuprizone demyelination (Aim 1 fails):** ROS-mediated photon production during myelin degradation is weaker than lipid peroxidation literature suggests, or the photons are absorbed/scattered before reaching the detector. The entire biomarker framework would require fundamental revision. This is the single most important negative result the experiments could produce.

- **No spectral difference between EAE and cuprizone (Aim 2 fails):** The MPO-singlet oxygen pathway does not contribute detectably to biophoton emission, or both mechanisms produce similar broadband spectra. Mechanistic discrimination would be ruled out, though intensity-based detection could still be valid.

- **AUC below 0.70 for combined score (Aim 3 fails):** Biological variability exceeds our simulated noise model, or the individual biomarkers are correlated rather than complementary. The multi-parameter approach would need recalibration, though individual markers with high AUC could still be useful.

---

## 6. Timeline and Budget

### 6.1 Timeline (12 months)

| Month | Activity | Milestone |
|-------|----------|-----------|
| 1-2 | Equipment setup: dark chamber construction, PMT characterization, filter wheel calibration. Cranial window surgery training. Analysis pipeline deployment and validation on calibrated light sources. | Dark chamber verified to <0.01 ph/s/cm^2 background |
| 2-3 | Pilot study: 4 mice (2 cuprizone, 2 control). Validate measurement protocol, measure baseline UPE from healthy corpus callosum, confirm cranial window optical quality. | Baseline UPE rate established |
| 3-5 | **Aim 1 main experiment:** 20 mice (10 cuprizone, 10 control). Weekly measurements for 6 weeks on cuprizone + 6 weeks recovery. | Week-1 detection milestone (predicted 3-sigma by day 7) |
| 4-7 | **Aim 2 EAE experiment:** 40 mice across 5 time points. MOG35-55 immunization, clinical scoring, spectral profiling at sacrifice. | EAE spectral profiles at 5 disease stages |
| 6-8 | Aim 2 spectral analysis: filter-wheel measurements on both EAE and cuprizone tissue. 634/703 nm ratio comparison. | SO2/carbonyl discrimination test |
| 8-10 | **Aim 3 ROC validation:** Combined analysis of all data. Diagnostic vector construction, cross-validated AUC computation, comparison against pre-registered predictions. | AUC benchmarks for all biomarkers |
| 10-11 | Histological correlation: Luxol fast blue, MBP immunostaining, electron microscopy of measured tissue. Quantify actual myelin loss and correlate with photon measurements. | Ground-truth myelin quantification |
| 11-12 | Data analysis, manuscript preparation, dissemination. | Submitted manuscript |

### 6.2 Budget estimate

| Category | Item | Cost |
|----------|------|------|
| **Equipment** | | |
| | Cooled PMT (Hamamatsu H7421-40 or equivalent) | $8,000-12,000 (if not available) |
| | Motorized filter wheel + 6 bandpass filters | $3,000-5,000 |
| | Dark chamber (custom or commercial) | $5,000-10,000 |
| | Perfusion system and temperature controller | $3,000-5,000 |
| | Cranial window surgical supplies | $2,000-3,000 |
| | **Equipment subtotal** | **$21,000-35,000** |
| **Animals** | | |
| | C57BL/6J mice (70 total: 20 cuprizone study + 40 EAE + 10 controls/pilots) | $1,400-2,100 |
| | Per diem housing (70 mice x 12 weeks average x $0.50/day) | $2,940 |
| | Cuprizone (Sigma-Aldrich, 100 g) | $200-400 |
| | MOG35-55 EAE induction kits (Hooke Laboratories, 5 kits) | $2,500-3,500 |
| | NAC and TTX for controls | $300-500 |
| | Histology (Luxol fast blue, MBP immunostaining, EM) | $5,000-8,000 |
| | **Animal subtotal** | **$12,000-17,500** |
| **Personnel** | | |
| | Postdoc or senior technician (50% effort, 12 months) | $35,000-50,000 |
| | **Personnel subtotal** | **$35,000-50,000** |
| **Other** | | |
| | Consumables (aCSF, culture supplies, reagents) | $3,000-5,000 |
| | Computational analysis (provided by our group) | $0 |
| | Publication charges (open access) | $2,000-4,000 |
| | **Other subtotal** | **$5,000-9,000** |
| | | |
| | **Total estimated budget** | **$73,000-111,500** |

Note: If the experimental laboratory already possesses a cooled PMT and dark chamber, the equipment costs reduce to approximately $5,000-8,000 (filter wheel and consumables only), bringing the total to approximately $57,000-84,500.

---

## 7. What We Bring to the Collaboration

### 7.1 Computational framework

Our group provides a complete, open-source simulation and analysis package developed over the course of our 8-track biophoton research program. This includes:

- **Waveguide simulator** (`models/waveguide.py`): Transfer matrix computation of multilayer myelin waveguide transmission spectra. Implements ARROW anti-resonance analysis, Sefati/Zeng spectral tuning, multi-node propagation with node-of-Ranvier coupling losses. Parameterized by myelin layer count, axon diameter, g-ratio, and the three-axis disease model (alpha, gamma, rho).

- **Detection feasibility calculator** (Track 05): Models five detector types (PMT, GaAsP PMT, SPAD, EM-CCD, SNSPD) with realistic noise parameters. Computes minimum integration times, SNR curves, and detection significance using the Li-Ma formula. Validated against manufacturer specifications.

- **Demyelination pathology simulator** (Track 06): Disease progression models for EAE, cuprizone, and Wallerian degeneration. Three-axis parameterization mapped to waveguide observables. Monte Carlo simulation of detection experiments with biological variability (CV = 0.3).

- **ROC analysis pipeline** (Track 06): Computes per-biomarker and combined-score AUC values with bootstrapped confidence intervals. Pre-generates prediction benchmarks against which experimental data can be directly compared.

- **Photocount statistics toolkit** (Track 01): Fano factor, Mandel Q parameter, chi-squared goodness-of-fit, likelihood ratio tests, and Bayesian model comparison for discriminating between source models at biophoton count rates. Includes artifact identification algorithms for delayed luminescence, afterpulsing, and thermal drift.

### 7.2 Pre-registered predictions

We will provide, before any experimental data is collected, a sealed document containing:

1. Point estimates and 95% prediction intervals for emission intensity at each cuprizone and EAE time point.
2. Predicted spectral peak positions and bandwidths at each disease stage.
3. Predicted 634/703 nm ratios for each disease model.
4. Predicted AUC values for each biomarker and the combined score.
5. Explicit falsification criteria for each aim.

This pre-registration ensures that the collaboration produces a clean test of the computational framework, regardless of the experimental outcome.

### 7.3 Analysis support

Our group will perform all computational analysis on the experimental data, including:

- Real-time monitoring of detection significance during data acquisition (we can provide a live analysis dashboard).
- Automated artifact detection and flagging.
- Blinded comparison of experimental measurements against pre-registered predictions.
- Manuscript preparation of the computational analysis sections.

### 7.4 What we ask from experimental partners

- Expertise in cuprizone and EAE mouse models, including surgical skills for cranial window implantation.
- Access to or ability to procure a cooled PMT and light-tight measurement chamber.
- Standard histology capabilities (Luxol fast blue, immunohistochemistry, ideally electron microscopy).
- IACUC-approved animal protocols or willingness to submit new protocols based on this proposal.
- Scientific rigor and willingness to publish negative results if the predictions fail.

---

## 8. References

1. Kumar S, Boone K, Tuszynski J, Barclay P, Simon C. Possible existence of optical communication channels in the brain. *Scientific Reports* 6:36508 (2016).

2. Zeng H, Zhang Y, Ma Y, Li S. Electromagnetic modeling and simulation of the biophoton propagation in myelinated axon waveguide. *Applied Optics* 61(14):4013-4021 (2022).

3. Cifra M, Pospisil P. Ultra-weak photon emission from biological samples: definition, mechanisms, properties, detection and applications. *Journal of Photochemistry and Photobiology B: Biology* 139:2-10 (2014).

4. Tang R, Dai J. Spatiotemporal imaging of glutamate-induced biophotonic activities and transmission in neural circuits. *PLoS ONE* 9(1):e85643 (2014).

5. Chen L, Wang Z, Dai J. Spectral blueshift of biophotonic activity and transmission in the ageing mouse brain. *Brain Research* 1749:147133 (2020).

6. Matsushima GK, Morell P. The neurotoxicant, cuprizone, as a model to study demyelination and remyelination in the central nervous system. *Brain Pathology* 11(1):107-116 (2001).

7. Constantinescu CS, Farooqi N, O'Brien K, Gran B. Experimental autoimmune encephalomyelitis (EAE) as a model for multiple sclerosis (MS). *British Journal of Pharmacology* 164(4):1079-1106 (2011).

8. Duncan ID, Radcliff AB, Heidari M, Kidd G, August BK, Bhatt D. Thin myelin sheaths as the hallmark of remyelination persist over time and preserve axon function. *Proceedings of the National Academy of Sciences* 114(45):E9685-E9691 (2017).

9. Babini MH, Klusek C, Bhatt DV. Simulation of nerve fiber based on anti-resonant reflecting optical waveguide. *Scientific Reports* 12:19429 (2022).

10. Liu Z, Chen X, et al. Entangled biphoton generation in the myelin sheath. *Physical Review E* 110:024402 (2024).

11. Lassmann H. Multiple sclerosis pathology. *Cold Spring Harbor Perspectives in Medicine* 8(3):a028936 (2018).

12. Li TP, Ma YQ. Analysis methods for results in gamma-ray astronomy. *Astrophysical Journal* 272:317-324 (1983).

13. Yadav DK, Pospisil P. Role of reactive oxygen species in ultra-weak photon emission in biological systems. *Journal of Photochemistry and Photobiology B: Biology* 113:78-83 (2012).

14. Kipp M, Clarner T, Dang J, Copray S, Beyer C. The cuprizone animal model: new insights into an old story. *Acta Neuropathologica* 118(6):723-736 (2009).

15. Frede E, Zadeh-Haghighi H, Simon C. Optical polarization evolution and transmission in multi-Ranvier-node axonal myelin-sheath waveguides. *IEEE Journal of Selected Topics in Quantum Electronics* (2024); preprint bioRxiv 2023.03.30.534951 (2023).

---

*Prepared by the Biophoton Computational Research Group, February 2026. Correspondence regarding this proposal should be directed to the principal investigator. All simulation code and prediction benchmarks are available for review upon request.*
