# Track 01: Photocount Statistics -- Progress Log

## Agent: Quantum Optics Statistician

---

### Build 1: Complete Simulation Suite (2026-02-11)

#### Modules Created

1. **src/photocount_distributions.py** -- Core distribution functions
   - Poisson (coherent state)
   - Bose-Einstein (single-mode thermal)
   - Negative binomial (M-mode thermal)
   - Squeezed coherent state (via Fock-space recurrence)
   - Cox process (doubly stochastic Poisson with OU intensity)
   - Mixture distributions
   - Convolution with dark counts, Bernoulli thinning for efficiency
   - All verified against analytic moments

2. **src/statistical_tests.py** -- Statistical analysis toolkit
   - Fano factor estimation with chi-squared confidence intervals
   - Chi-squared goodness-of-fit test (with bin merging)
   - Likelihood ratio test: Poisson vs. Negative Binomial
   - Bayesian model comparison via analytic marginal likelihoods
   - Power analysis for the Fano factor test
   - Measured Fano factor with full detector artifact chain

3. **src/detector_model.py** -- Detector artifact modeling
   - DetectorModel class with quantum efficiency, dark counts, dead time, afterpulsing
   - Sample-level Monte Carlo application of artifacts
   - Analytic Fano transformation through the full chain
   - Preset configurations: COOLED_PMT, ROOM_TEMP_PMT, SNSPD, SPAD, IDEAL

4. **src/sensitivity_analysis.py** -- Parameter sweep engine
   - Power vs. count rate analysis
   - Required counting intervals heatmap (signal rate x dark rate)
   - Multimode thermal distinguishability boundary
   - Squeezed state detection threshold for different detectors
   - Nonstationarity false positive rate (Monte Carlo)
   - Dark count masking analysis

5. **src/critical_reanalysis.py** -- Critique of prior claims
   - Squeezed-state fit flexibility demonstration
   - Low count rate distribution convergence analysis
   - Popp and Chang (2002) sub-Poissonian claim critique
   - Bajpai (2005) Parmelia tinctorum reanalysis with AIC/BIC

6. **src/generate_figures.py** -- Publication figure generation (10 figures)

7. **src/simulate_photocount.py** -- Master runner for all analyses

#### Figures Generated

| Figure | Description |
|--------|-------------|
| fig01 | Distribution comparison (Poisson, thermal, NB, squeezed) |
| fig02 | Fano factor vs. mode number (why broadband thermal is Poissonian) |
| fig03 | Detector artifact chain (4 panels) |
| fig04 | Squeezed detection landscape |
| fig05 | Dark count masking heatmaps |
| fig06 | Nonstationarity false positive rate |
| fig07 | Power analysis landscape |
| fig08 | Bayesian discrimination Monte Carlo |
| fig09 | Squeezed-state fit to classical data (critique) |
| fig10 | Low count rate distribution convergence |

#### Results Data (in results/)

- power_vs_count_rate.npz
- required_intervals.npz
- multimode_distinguishability.npz
- squeezed_threshold_{cooled_pmt,snspd,room_pmt}.npz
- nonstationarity_fpr.npz
- dark_count_masking.npz

---

### Key Findings

#### 1. The Fundamental Indistinguishability Problem

For broadband biophoton emission (bandwidth approx 10^14 Hz), the number of thermal
modes M approx T * Delta_nu approx 10^13. The Fano factor departure for M-mode thermal
light is Q = mu/M approx 10^-12. With any feasible sample size (N < 10^7), the
minimum detectable departure is |F-1| > approx 0.001.

Photocount statistics cannot distinguish coherent from broadband thermal light
at biophoton intensities. Even for narrowband thermal light, distinguishability
requires M < approx 600 modes with N = 10^5 intervals.

#### 2. Detector Artifact Budget

For a sub-Poissonian source with F_true = 0.5 (strong squeezing):

| Detector      | eta  | dark | F_measured | Departure |
|--------------|------|------|------------|-----------|
| Cooled PMT   | 0.15 | 2/s  | 0.970      | 0.030     |
| Room-temp PMT| 0.12 | 20/s | 0.997      | 0.003     |
| SNSPD        | 0.85 | 0.1/s| 0.581      | 0.419     |

Only SNSPDs preserve enough sub-Poissonian signature to be detectable.

#### 3. Nonstationarity Is the Killer

A mere 2.1% sinusoidal rate modulation causes the Fano factor test to
reject the Poisson null at >5% rate. Biological systems have much
larger rate fluctuations.

#### 4. Squeezed-State Fitting Is Not Evidence

4-parameter squeezed fits match classical NB data comparably well.
AIC/BIC consistently prefer simpler models. Supports Cifra et al. (2015).

#### 5. Implications for the M-Phi Framework

Photocount statistics alone cannot verify the coherent photon field claim.
The most promising approach is g^(2)(tau) correlation measurements.
