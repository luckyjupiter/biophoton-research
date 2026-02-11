# Dual-Measurement Experimental Protocol: Biophoton Detection During MMI Sessions

## 1. Purpose

This document specifies the experimental protocol for simultaneously measuring
biophoton emission from a biological system and MMI/QFT device performance
(Responsivity), testing the core prediction of the M-Phi framework: that both
observables couple to the same Phi field, producing a detectable positive
correlation.

**Primary hypothesis (H1):** Biophoton emission rate from the operator's
cranial surface correlates positively with MMI hit rate during active QFT
device sessions.

**Null hypothesis (H0):** No correlation exists between biophoton emission
and MMI performance; any observed correlation is consistent with chance.

---

## 2. Participants

- **Sample size:** N = 30 operators (based on power analysis: detecting r = 0.25
  at alpha = 0.05 with 80% power requires n >= 123 measurement blocks; 30
  operators x 5 sessions x 10 blocks = 1500 blocks).
- **Inclusion criteria:** Healthy adults 18-65, no neurological conditions,
  no psychoactive medications, willing to complete 5 sessions.
- **Exclusion criteria:** Demyelinating conditions (MS, ADEM), active
  neuroinflammation, epilepsy, metal implants near measurement sites.
- **Control group:** 10 additional participants performing sham MMI sessions
  (QFT device powered but in non-interactive mode).

---

## 3. Equipment

### 3.1 Biophoton Detection

- **Primary detector:** Hamamatsu H7421-40 photon-counting head (PMT module)
  - Dark count rate: < 30 counts/s at 25 C
  - Quantum efficiency: 25% at 500 nm
  - Timing resolution: 300 ps
  - Active area: 5 mm diameter
- **Secondary detector:** MPD PDM Series SPAD (for cross-validation)
  - Dark count rate: < 25 counts/s
  - Quantum efficiency: 50% at 550 nm
  - Timing resolution: 50 ps
- **Light-tight enclosure:**
  - Custom Faraday cage (copper mesh, > 60 dB shielding at 1 GHz)
  - Internal blackout lining (Acktar Metal Velvet, reflectance < 1%)
  - Optical port for detector positioning
  - Temperature-controlled to +/- 0.1 C
- **Spectral filters:**
  - Broadband: 350-800 nm bandpass (Thorlabs FGB37)
  - Narrowband set: 450 nm, 550 nm, 650 nm, 750 nm, 850 nm (10 nm FWHM)
- **Positioning:**
  - Detector 3-5 cm from scalp surface (right temporal region, following
    Casey et al. 2025)
  - Fiber bundle option: 1 mm diameter liquid light guide (Thorlabs)
    for flexible positioning

### 3.2 MMI/QFT System

- **QFT device:** QTrainerAI system (as described in QTrainerAI codebase)
  - QRNG: hardware true random number generator (> 1 Gbit/s)
  - 17-method combined Bayesian updating
  - GPS-synchronized trial timing
- **Session parameters:**
  - Trial duration: standard QTrainerAI trial length
  - Subtrials per trial: 96 (standard)
  - Blocks per session: 10 blocks of 100 trials each
  - Total trials per session: 1000

### 3.3 Ancillary Measurements

- **EEG:** 32-channel system (e.g., BrainVision actiCHamp)
  - Focus on gamma band (30-100 Hz) for PLV computation
  - Reference: linked mastoids
  - Sampling rate: 1000 Hz
- **Temperature monitoring:**
  - Scalp surface: infrared thermometer (FLIR C5, 0.1 C resolution)
  - Ambient: precision thermistor in enclosure
- **Heart rate:** Pulse oximeter for physiological artifact control

---

## 4. Protocol

### 4.1 Pre-Session (30 minutes)

1. Dark adaptation: participant sits in darkened room for 15 minutes
2. Equipment calibration:
   - PMT dark count baseline: 5-minute measurement in sealed enclosure
   - SPAD dark count baseline
   - Background measurement: enclosure with participant but no MMI activity (5 min)
3. EEG cap application and impedance check (< 10 kOhm all channels)
4. Temperature baseline measurement

### 4.2 Active Session (approximately 60 minutes)

Each session consists of 10 blocks, interleaved with rest periods:

```
Block structure (repeat 10 times):
  [Rest: 60s] --> [Active MMI: 100 trials, ~5-6 min] --> [Rest: 60s]
```

During ACTIVE blocks:
- Operator engages with QTrainerAI in standard affect mode
- Biophoton detector records continuously (1-second bins)
- EEG records continuously
- QTrainerAI records per-trial and per-subtrial data

During REST blocks:
- Operator sits quietly with eyes closed
- Same measurements continue (provides within-session baseline)

### 4.3 Control Conditions

- **Sham MMI:** QFT device active but not receiving operator input; operator
  performs same behavioral routine (looking at screen, pressing buttons)
- **Dark baseline:** No operator in enclosure; detector records for same duration
- **Thermal stimulus:** Brief light exposure (1 second, calibrated LED) at
  start of each block as positive control for biophoton detection system

### 4.4 Session Schedule

- Each participant completes 5 sessions over 2-3 weeks
- Sessions at consistent time of day (+/- 1 hour) for each participant
- Minimum 48 hours between sessions
- Total data: 30 participants x 5 sessions x 10 blocks = 1500 measurement blocks

---

## 5. Data Collection

### 5.1 Biophoton Data

Per time bin (1 second):
- Total photon count (broadband)
- Count per spectral channel (if using filter wheel)
- PMT temperature
- Dark count correction (subtract measured dark rate)

Derived per block:
- Mean photon rate (counts/s)
- Variance and Fano factor
- Mandel Q parameter
- Autocorrelation function (lags 1-20 bins)
- Lempel-Ziv complexity of binarized stream
- KS test p-value (vs Poisson)

### 5.2 MMI Data

Per trial:
- Per-subtrial observations (96 per trial)
- Per-method BU posteriors (17 methods)
- Combined BU posterior
- Hit/miss outcome for each method

Per block (100 trials):
- Block success rate (hits / total)
- Combined BU final posterior
- Per-method success rates
- z-score for block success rate

### 5.3 EEG Data

Per 1-second bin (synchronized with biophoton bins):
- Gamma power (30-100 Hz) at each electrode
- Phase-locking value (PLV) between selected electrode pairs
- Global field power (GFP)

---

## 6. Analysis Plan

### 6.1 Primary Analysis: Biophoton-MMI Correlation

**Test statistic:** Pearson correlation between block-level biophoton rate
and block-level MMI success rate, across all 1500 blocks.

**Corrections:**
- Within-participant clustering: use mixed-effects model with random
  intercepts per participant
- Multiple comparisons: Bonferroni correction across spectral channels
- Temporal autocorrelation: block-bootstrap standard errors

**Model:**
```
SR_block ~ beta_0 + beta_1 * BiophotonRate + (1 | participant)
```

Primary test: H0: beta_1 = 0 vs H1: beta_1 > 0 (one-sided, predicted positive)

**Expected effect size:** r = 0.15 to 0.30 based on shared-Phi-field model
simulations (see src/cross_prediction.py).

### 6.2 Secondary Analyses

1. **Spectral selectivity:** Does the correlation depend on biophoton
   wavelength? Test separately for each spectral channel.

2. **Temporal dynamics:** Cross-correlation function between biophoton rate
   and MMI success rate at different lags (0 to +/- 10 seconds).

3. **Triple correlation:** EEG gamma PLV as mediating variable. Structural
   equation model:
   ```
   Phi --> Lambda --> BiophotonRate
                  --> EEG_PLV
                  --> MMI_SR
   ```

4. **Active vs Rest comparison:** Paired t-test of biophoton rate during
   active MMI blocks vs rest blocks (within-subject).

5. **Bayesian coherence estimation:** Apply the 17-method combined BU
   framework (src/bayesian_coherence.py) to the biophoton data and
   correlate the coherence estimate with MMI performance.

### 6.3 Falsification Criteria

The M-Phi hypothesis is falsified for this prediction if:
- beta_1 not significantly different from 0 (p > 0.05, two-sided)
  across 1500 blocks
- Upper bound of 95% CI for r includes 0
- Bayesian analysis: BF_01 > 3 (substantial evidence for null)

### 6.4 Sensitivity Analysis

- Effect of dark count subtraction method
- Effect of temporal binning (1s vs 5s vs 10s)
- Effect of including/excluding first block of each session (warmup)
- Comparison of PMT vs SPAD detector results
- Effect of room temperature fluctuations (covariate)

---

## 7. Expected Effect Sizes

Based on the shared-Phi-field model (src/cross_prediction.py):

| Parameter | Estimate | 95% CI |
|-----------|----------|--------|
| Pearson r (bio-MMI) | 0.20 | [0.10, 0.35] |
| MMI SR in high-bio blocks | 0.520 | [0.510, 0.530] |
| MMI SR in low-bio blocks | 0.508 | [0.500, 0.515] |
| Biophoton rate increase (active vs rest) | +15% | [+5%, +30%] |
| Required blocks for 80% power | ~200 | |

---

## 8. Ethical Considerations

- IRB approval required (human subjects, non-invasive measurements)
- Informed consent with clear description of MMI research context
- No deception (except sham condition, disclosed post-study)
- Data anonymization before analysis
- Right to withdraw at any time

---

## 9. Timeline

| Phase | Duration | Milestones |
|-------|----------|------------|
| Equipment setup & calibration | 2 months | Dark count characterization, PMT positioning optimization |
| Pilot study (N=5) | 1 month | Protocol refinement, preliminary effect size estimate |
| Main study recruitment | 1 month | N=30 enrolled |
| Data collection | 3 months | 150 total sessions completed |
| Analysis | 2 months | Primary and secondary analyses |
| Write-up | 2 months | Manuscript preparation |

---

## 10. References

- Casey, H. et al. (2025). iScience 28(3), 112019. -- Brain UPE measurement methodology
- Dotta, B.T. et al. (2012). Neurosci. Lett. 513(2), 151-154. -- EEG-biophoton correlation
- Kruger, M., Feeney, D., & Duarte, R. (2023). Physical Basis of Coherence. -- M-Phi framework
- Wang, Z. et al. (2016). PNAS 113(31), 8753-8758. -- Spectral characteristics of brain UPE
