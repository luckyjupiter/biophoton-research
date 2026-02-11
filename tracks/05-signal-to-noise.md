# Track 05: Signal-to-Noise and Detection Theory for Biophoton Research

## 1. Overview

The central experimental challenge in biophoton research -- and the reason the field remains contested after four decades -- is that biological ultra-weak photon emission (UPE) rates are comparable to, and often indistinguishable from, detector noise. Typical UPE intensities range from 1 to 1000 photons/cm^2/s across the 300--800 nm window, while cooled photomultiplier dark count rates sit at 10--50 counts/s and other detectors introduce their own noise floors through distinct physical mechanisms.

This is not merely an engineering inconvenience. It places biophoton detection squarely in the regime where:

- **Gaussian approximations fail**: Count rates of O(1--10) per bin violate the central limit theorem assumptions underlying standard error propagation.
- **Background subtraction is non-trivial**: The "signal = total minus background" formula can produce negative counts, and its uncertainty is not symmetric.
- **Systematic effects dominate**: Afterpulsing, cosmic rays, chemiluminescent contamination, and temperature-dependent dark rate drifts can mimic or mask real signals.
- **Spectral and temporal resolution trade against detection significance**: Resolving a 1 nm spectral band from a 500 nm range reduces the photon budget by a factor of ~500, pushing integration times from minutes to days.

This track develops the statistical and information-theoretic framework needed to rigorously design and analyze biophoton experiments, drawing heavily on methods from particle physics, gravitational wave astronomy, and quantum optics -- fields that have solved analogous low-count problems at scale.

The specific application to myelin sheath biophotons compounds the difficulty: we are asking whether photons emitted within a biological waveguide (Track 03) exhibit non-classical statistics (Track 04) at rates barely above the noise floor. Getting the detection theory right is prerequisite to every other track in this program.

---

## 2. Background Theory

### 2.1 Detection Theory Fundamentals

The mathematical framework for deciding whether a signal is present in noisy data was formalized by Neyman and Pearson (1933) and extended by Wald (1947). The core concepts:

**Binary hypothesis test.** Given observed data **x**, choose between:
- H_0 (null): data contain only background noise
- H_1 (signal): data contain signal plus background

**Likelihood ratio test.** The most powerful test at a given significance level alpha (by the Neyman-Pearson lemma) is to reject H_0 when the likelihood ratio exceeds a threshold:

```
Lambda(x) = L(x | H_1) / L(x | H_0) > k_alpha
```

where k_alpha is chosen so that P(Lambda > k_alpha | H_0) = alpha.

**For Poisson data** with expected background b and signal s, the observed count n follows:
- Under H_0: n ~ Poisson(b)
- Under H_1: n ~ Poisson(s + b)

The log-likelihood ratio is:

```
ln Lambda(n) = n * ln(1 + s/b) - s
```

**Significance and power.** Two error rates control the test:
- Type I error (false positive rate): alpha = P(reject H_0 | H_0 true)
- Type II error (missed detection rate): beta = P(fail to reject H_0 | H_1 true)
- Power: 1 - beta = P(detect signal | signal present)

For Poisson counting with background rate b (counts per integration time T), the minimum detectable signal rate s_min at significance alpha and power 1 - beta is approximately (for large bT):

```
s_min * T ≈ z_alpha * sqrt(b*T) + (1/2) * z_alpha^2 + z_beta * sqrt((s_min + b)*T)
```

where z_alpha and z_beta are standard normal quantiles. For small bT (the UPE regime), this Gaussian approximation fails and exact Poisson calculations are required.

### 2.2 Photon Detection Physics

Every photon detector converts an incident photon into a measurable electrical signal through a chain of physical processes, each introducing noise or loss.

**Quantum efficiency (QE).** The probability that an incident photon produces a detected event. If the true photon arrival rate is R_photon, the detected rate is:

```
R_detected = eta * R_photon
```

where eta is the QE, typically 0.2--0.9 depending on detector type and wavelength. This is a binomial thinning of the photon stream, preserving Poisson statistics if the input is Poisson.

**Dark counts.** Thermally or tunneling-generated events indistinguishable from photon detections. Dark count rate R_dark adds directly to the signal:

```
R_total = eta * R_photon + R_dark
```

Dark counts follow Poisson statistics (to good approximation) and are the primary noise source in UPE measurements.

**Afterpulsing.** A detected event can trigger secondary events with probability P_ap and characteristic delay tau_ap. This introduces correlations in the count record:

```
g^(2)(tau) = 1 + (P_ap / R_total) * h(tau)
```

where h(tau) is the afterpulse delay distribution (typically exponential or multi-exponential). This is critical because afterpulsing mimics photon bunching -- the very signature used to test coherence hypotheses (Track 04). A detector with P_ap = 0.02 and R_total = 100/s contributes a g^(2)(0) excess of ~0.0002 per ns time bin, which can be significant when trying to measure deviations of 10^-3 from unity.

**Dead time.** After a detection event, the detector is insensitive for a period tau_d. This modifies the count rate:

```
R_measured = R_true / (1 + R_true * tau_d)
```

At UPE rates (R_true ~ 10--100/s) with typical dead times (tau_d ~ 10--100 ns), the correction is negligible (<10^-5). Dead time is not a concern for UPE measurements but must be accounted for in calibration with brighter sources.

**Timing jitter.** The uncertainty in the time assignment of a detected photon, typically 30--300 ps for SPADs and 0.3--1 ns for PMTs. This limits the temporal resolution of correlation measurements (Track 04).

### 2.3 Detector Types and Noise Characteristics

#### 2.3.1 Photomultiplier Tubes (PMTs)

PMTs remain the workhorse of biophoton research due to their simplicity and well-characterized noise.

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| QE | 15--25% (bialkali), up to 40% (GaAsP) | Peaks at 350--450 nm; poor in red |
| Dark count rate | 10--50/s (cooled to -20 C) | Thermionic emission from photocathode |
| Afterpulse probability | 0.5--5% | From residual gas ionization in dynode chain |
| Dead time | 10--20 ns | Non-paralyzable in most counting electronics |
| Timing jitter | 0.3--1 ns (TTS) | Transit time spread |
| Gain | 10^5 -- 10^7 | Single-photon pulse height ~1--50 mV into 50 Ohm |
| Active area | 1--50 cm^2 | Large area available (good for collection) |
| Spectral range | 300--650 nm (bialkali), 300--900 nm (multialkali/GaAsP) | |
| Operating temperature | -20 to -30 C typical | Peltier cooling sufficient |
| Cost | $1k--$10k | Mature technology |

**Strengths for UPE:** Large collection area, very low dark counts when cooled, well-understood statistics, decades of biophoton literature use this detector.

**Weaknesses:** No spatial resolution (single-channel), moderate QE means 75--85% of photons are lost, spectral response drops sharply above 600 nm.

**Key noise model:** For a PMT in photon counting mode, the output count in time bin Delta_t is:

```
n ~ Poisson(eta * R_signal * Delta_t + R_dark * Delta_t + R_afterpulse * Delta_t)
```

The afterpulse rate depends on the recent count history, introducing temporal correlations.

#### 2.3.2 Electron-Multiplying CCD (EM-CCD)

EM-CCDs provide spatial imaging of biophoton emission patterns, which is essential for studying emission from specific tissue structures (e.g., myelin tracts).

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| QE | >90% (back-illuminated) | Exceptional; best available |
| Read noise | <1 e- (with EM gain) | Effectively eliminated by multiplication |
| Dark current | 0.001--0.01 e-/pixel/s (at -85 C) | Deep cooling essential |
| EM gain | 100--1000x | Stochastic multiplication; excess noise factor F^2 = 2 |
| Pixel count | 512x512 to 1024x1024 | |
| Pixel size | 13--16 um | |
| Clock-induced charge (CIC) | 0.001--0.01 e-/pixel/frame | Spurious charge from clocking; irreducible |
| Frame rate | 1--30 fps (full frame) | Longer exposures by on-chip accumulation |
| Spectral range | 300--1000 nm | Broad; good red response |
| Cost | $30k--$100k | Specialized cameras (Andor iXon, Hamamatsu) |

**Strengths for UPE:** Highest QE of any detector, spatial imaging enables tissue-level mapping, proven in biophoton imaging studies (Kobayashi et al., 1999; Usa et al., 1989).

**Weaknesses:** Stochastic multiplication introduces an excess noise factor of F^2 = 2, which effectively halves the SNR compared to an ideal noiseless detector at the same QE. Integration times of 10--30 minutes per frame are typical for UPE, during which cosmic ray hits accumulate. CIC sets a floor on the per-pixel noise.

**Key noise model:** For an EM-CCD pixel in photon-counting mode, the signal is amplified by a stochastic gain register. The probability of detecting k output electrons given m input photoelectrons follows a cascaded Poisson-gamma distribution. In the high-gain limit, the output per pixel per frame is:

```
For thresholded photon counting:
P(detection | 0 photons) = P_dark + P_CIC    (false positive per pixel per frame)
P(detection | 1 photon) ≈ 1 - exp(-G/T_thresh)    (detection efficiency)
```

where G is the EM gain and T_thresh is the counting threshold. The excess noise factor means that for analog (non-thresholded) integration:

```
SNR = eta * N_photon / sqrt(F^2 * eta * N_photon + n_pix * sigma_dark^2 + n_pix * R_CIC)
```

where F^2 = 2 for the EM gain register.

#### 2.3.3 Scientific CMOS (sCMOS)

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| QE | 60--82% (back-illuminated) | Improving; approaching EM-CCD |
| Read noise | 1--2 e- (median), 0.7 e- (best pixels) | Per-pixel variation is significant |
| Dark current | 0.1--0.5 e-/pixel/s (at -25 C) | Higher than EM-CCD |
| Pixel count | 2048x2048 to 4096x4096 | Much larger field of view |
| Pixel size | 6.5 um | Smaller than EM-CCD |
| Frame rate | 30--100 fps | |
| Cost | $10k--$40k | |

**Strengths for UPE:** Higher pixel count enables larger area imaging, lower cost, improving QE.

**Weaknesses:** Read noise of ~1 e- is a hard floor; at UPE levels (<<1 photon/pixel/frame), the read noise dominates. Each pixel has a different read noise, requiring per-pixel calibration. Not competitive with EM-CCD for true single-photon work, but the gap is narrowing with quanta-mode sCMOS designs.

**Recent development:** Photon-number-resolving sCMOS sensors (e.g., Hamamatsu ORCA-Quest) achieve 0.27 e- read noise, enabling photon counting without multiplication gain. This could be transformative for biophoton imaging if dark current is sufficiently controlled.

#### 2.3.4 Single-Photon Avalanche Diodes (SPADs)

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| QE | 50--80% (Si, 400--700 nm) | Good across visible range |
| Dark count rate | 10--100/s (cooled, 50 um diameter) | Scales with active area |
| Afterpulse probability | 0.5--5% | Depends on hold-off time |
| Dead time | 20--100 ns | Limits max count rate to ~10 MHz |
| Timing jitter | 30--100 ps | Excellent for timing; enables HBT measurements |
| Active area | 20--200 um diameter | Very small; limits collection efficiency |
| Spectral range | 350--900 nm (Si), 900--1700 nm (InGaAs) | |
| Cost | $5k--$20k per channel | |

**Strengths for UPE:** Best timing resolution for photon correlation measurements (Track 04), good QE, well-established photon counting statistics.

**Weaknesses:** Small active area is a severe limitation -- collecting photons from a ~50 um spot covers only a tiny fraction of a tissue sample. Array SPADs (SPAD arrays, 32x32 to 512x512) exist but have high dark rates per pixel and limited fill factor.

**Critical concern -- photon emission during avalanche:** When a SPAD undergoes avalanche breakdown, secondary photons are emitted (typically 10^-5 to 10^-4 photons per avalanche). In a coincidence measurement with two SPADs facing the same sample, photons from one detector's avalanche can reach the other detector, creating correlated false coincidences. This directly mimics the entangled photon pair signature that Track 04 aims to test. Optical isolation (>OD 6) between detector channels is mandatory.

#### 2.3.5 Superconducting Nanowire Single-Photon Detectors (SNSPDs)

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| QE | >90% (with optical cavity) | Broadband; 400--2000 nm |
| Dark count rate | <0.1/s | Extraordinarily low |
| Afterpulse probability | Negligible | No avalanche mechanism |
| Dead time | 10--50 ns | Fast recovery |
| Timing jitter | 15--70 ps | Best available |
| Active area | 10--20 um (single pixel), up to ~300 um (arrays) | Small |
| Operating temperature | 0.8--3 K | Requires closed-cycle cryostat |
| Cost | $100k--$500k (system) | Including cryogenics |
| Spectral range | 400--2000 nm (broadband) | |

**Strengths for UPE:** The combination of >90% QE, <0.1/s dark counts, and ~30 ps jitter is unmatched. An SNSPD-based biophoton detector would improve SNR by 1--2 orders of magnitude over PMTs and essentially eliminate dark count contamination.

**Weaknesses:** Prohibitive cost, small active area (fiber-coupled), cryogenic infrastructure. Currently impractical for most biophoton labs but worth considering for definitive measurements where the question is "is there any signal at all?"

**Potential:** If the biophoton field is to make definitive claims about coherent or quantum emission, SNSPD-based measurements may be the only way to achieve sufficient SNR within practical integration times. A collaboration with a quantum optics lab possessing SNSPD infrastructure could be transformative.

### 2.4 Signal Rates in Context

To calibrate intuition, here are representative signal levels across the detection chain:

| Source/Component | Rate | Notes |
|------------------|------|-------|
| UPE from living tissue | 1--1000 photons/cm^2/s | Integrated over 300--800 nm |
| UPE from neural tissue (in vivo) | ~10--100 photons/cm^2/s | Rat brain slices (Kobayashi et al.) |
| Myelin-enriched preparation | Unknown | No published measurements |
| PMT dark counts (cooled) | 10--50/s | Entire photocathode |
| EM-CCD dark current | 0.001 e-/pixel/s | At -85 C; 262,144 pixels = 262 total dark e-/s |
| EM-CCD CIC | 0.005 e-/pixel/frame | Per frame, not per second |
| SPAD dark counts | 25--100/s | Per channel |
| SNSPD dark counts | <0.1/s | Per channel |
| Cosmic ray rate | ~1/cm^2/min | At sea level; ~0.017/cm^2/s |
| Cherenkov emission in optics | Variable | Can be triggered by cosmic rays in glass |

The signal-to-background ratio for a PMT-based UPE measurement of neural tissue is approximately:

```
SBR = eta * R_UPE * A_collection / R_dark
     = 0.20 * 50 * 5 / 30
     ≈ 1.7
```

for QE=20%, UPE rate of 50 photons/cm^2/s, 5 cm^2 collection area, and 30/s dark rate. This is marginal -- the signal is comparable to the noise -- requiring careful statistical treatment.

### 2.5 Background Subtraction Protocols

Standard biophoton protocol alternates between "sample in" and "sample out" measurements:

```
R_signal = R_on - R_off
```

where R_on is the measured rate with sample present and R_off is the rate without. This assumes:

1. The dark rate is identical in both measurements (requires temperature stability to ~0.01 C).
2. No other photon sources are present (chemiluminescence from mounting media, fluorescence from optical elements, scattered ambient light).
3. The sample does not alter the thermal environment of the detector.

**Systematic checks required:**
- Dead sample control (same tissue, killed by fixation or heat, to test for chemiluminescence).
- Optical blank (mounting medium without tissue).
- Dark rate monitoring throughout the measurement (interleaved blank frames).
- Temperature logging of detector housing.
- Cosmic ray flagging (pulse height discrimination or multi-pixel rejection in imaging detectors).

---

## 3. Statistical Framework for Ultra-Low Count Rates

### 3.1 Poisson Statistics: The Exact Treatment

When the expected count per bin is small (mu < ~20), the Poisson distribution must be used exactly, not approximated as Gaussian.

For observed count n from a Poisson process with unknown rate mu:

```
P(n | mu) = mu^n * exp(-mu) / n!
```

**Confidence intervals.** The classical (Garwood, 1936) exact confidence interval for mu given observed n is:

```
mu_lower = (1/2) * chi^2(alpha/2, 2n)
mu_upper = (1/2) * chi^2(1 - alpha/2, 2n + 2)
```

where chi^2(p, k) is the p-th quantile of the chi-squared distribution with k degrees of freedom. For n = 0 (critical in UPE -- "did we detect anything?"), the 90% upper limit is:

```
mu_upper(n=0, 90% CL) = (1/2) * chi^2(0.90, 2) = 2.303
```

This means: if you observe zero counts, you can only claim the true rate is below 2.3 counts per measurement interval at 90% confidence. For UPE experiments where the expected signal might be 1--5 counts per hour, this is a real constraint.

**Selected Poisson confidence intervals (90% CL):**

| Observed n | Lower bound | Upper bound | Interval width |
|-----------|-------------|-------------|----------------|
| 0 | 0 | 2.30 | 2.30 |
| 1 | 0.051 | 4.74 | 4.69 |
| 2 | 0.355 | 6.68 | 6.33 |
| 3 | 0.818 | 8.38 | 7.56 |
| 5 | 2.09 | 11.3 | 9.16 |
| 10 | 5.49 | 17.1 | 11.6 |
| 20 | 13.3 | 29.1 | 15.8 |
| 50 | 39.0 | 63.3 | 24.3 |

Note the severe asymmetry at low counts: for n=1, the lower bound is 0.051 but the upper bound is 4.74 -- nearly a factor of 100 ratio.

### 3.2 Background-Subtracted Rates and Their Uncertainties

The signal rate is estimated from "on-source" and "off-source" measurements:

```
s_hat = n_on / t_on - n_off / t_off
```

where t_on and t_off are the respective exposure times. The variance of this estimator is:

```
Var(s_hat) = (s + b) / t_on + b / t_off
```

where s is the true signal rate and b the true background rate. Since s and b are unknown, they are estimated from the data, introducing additional uncertainty.

**The problem of negative estimates.** When the true signal is small, s_hat < 0 occurs with non-negligible probability. For example, if s = 0 and b = 10/hr with t_on = t_off = 1 hr, P(s_hat < 0) = P(n_on < n_off) ≈ 0.43. Reporting negative count rates is physically meaningless but statistically informative -- it indicates the signal is consistent with zero.

**Naive approaches fail here:**
- Setting negative results to zero introduces bias.
- Discarding negative results biases the average upward.
- Gaussian error propagation gives symmetric intervals that include negative rates.

### 3.3 The Feldman-Cousins Unified Approach

Feldman and Cousins (1998) developed a unified method for constructing confidence intervals that handles the transition between upper limits (no signal detected) and two-sided intervals (signal detected) without the experimenter choosing which to report after seeing the data. This eliminates the "flip-flopping" problem that biases published results.

**Method.** For each hypothesized true signal s, construct an acceptance region in the observable n by ordering possible outcomes by the likelihood ratio:

```
R(n | s) = P(n | s + b) / P(n | s_best + b)
```

where s_best = max(0, n - b) is the physically constrained best-fit signal. Include values of n in the acceptance region in decreasing order of R until the region contains probability >= 1 - alpha.

The confidence interval for s given observed n is then the set of all s values whose acceptance region includes n.

**Key properties:**
- Automatically transitions from upper limit to two-sided interval.
- Always gives physical (non-negative) intervals.
- Exact coverage by construction.
- Widely used in particle physics (neutrino oscillations, dark matter searches).

**Example (directly relevant to biophoton measurements):** For known background b = 3.0 counts and observed n = 5 counts:

| Confidence Level | Lower bound on s | Upper bound on s |
|-----------------|-----------------|-----------------|
| 90% | 0.0 | 6.37 |
| 95% | 0.0 | 7.75 |

The lower bound is zero, meaning the data are consistent with no signal. Compare to the naive Gaussian result: s_hat = 5 - 3 = 2, sigma_s = sqrt(5 + 3) = 2.83, giving a 90% interval of (-2.66, 6.66) -- which includes unphysical negative values.

For observed n = 10 counts with b = 3.0:

| Confidence Level | Lower bound on s | Upper bound on s |
|-----------------|-----------------|-----------------|
| 90% | 2.94 | 12.0 |

Now the lower bound is positive -- a detection at 90% CL.

**Recommendation:** All biophoton count rate measurements should be reported using Feldman-Cousins intervals, not Gaussian approximations. This is especially important for spectral measurements where individual wavelength bins have very low counts.

### 3.4 Bayesian Inference with Informative Priors

The Bayesian approach provides a natural framework for incorporating prior knowledge about detector characteristics, which are often well-calibrated from independent measurements.

**Model.** Let s >= 0 be the signal rate, b >= 0 the background rate. Given "on" measurement (n_on counts in t_on) and "off" measurement (n_off counts in t_off):

```
n_on ~ Poisson((s + b) * t_on)
n_off ~ Poisson(b * t_off)
```

With priors pi(s) and pi(b), the joint posterior is:

```
p(s, b | n_on, n_off) proportional to
    Poisson(n_on | (s+b)*t_on) * Poisson(n_off | b*t_off) * pi(s) * pi(b)
```

**Choice of priors:**

For the background rate b, an informative prior based on detector characterization is appropriate and recommended. If the dark count rate has been measured to be b_0 +/- sigma_b from calibration data, use:

```
pi(b) = Gamma(b | alpha_b, beta_b)
```

with alpha_b = (b_0 / sigma_b)^2 and beta_b = b_0 / sigma_b^2, encoding the calibration information.

For the signal rate s, the choice depends on the analysis goal:
- **Discovery (is there a signal?):** Use a flat prior pi(s) = 1 for s >= 0. This is equivalent to the reference prior and gives results close to Feldman-Cousins.
- **Parameter estimation (how bright is it?):** Use the Jeffreys prior pi(s) proportional to 1/sqrt(s) for s > 0, which is invariant under reparameterization.
- **Incorporating published UPE rates:** Use a log-normal prior centered on published values for the tissue type, encoding the order-of-magnitude variability across studies.

**Marginalization over nuisance parameters.** The posterior for s alone is obtained by integrating out b:

```
p(s | n_on, n_off) = integral from 0 to infinity of p(s, b | n_on, n_off) db
```

This integral is analytically tractable when pi(b) is a Gamma distribution (conjugate prior for Poisson), yielding a closed-form expression involving the confluent hypergeometric function. Otherwise, numerical integration or MCMC sampling is used.

**Bayes factor for detection.** To quantify evidence for a signal, compute:

```
B_10 = P(n_on, n_off | H_1: s > 0) / P(n_on, n_off | H_0: s = 0)
```

Using the Jeffreys scale: B_10 > 3 is "substantial evidence," B_10 > 10 is "strong evidence," B_10 > 30 is "very strong evidence" for the signal hypothesis.

### 3.5 Profile Likelihood Methods

The profile likelihood provides a frequentist alternative that handles nuisance parameters (background rate, detector efficiency) without requiring priors.

**Definition.** The profile likelihood for the signal rate s is:

```
L_p(s) = max over b of L(s, b | data) = L(s, b_hat(s) | data)
```

where b_hat(s) is the conditional MLE of b for fixed s. The profile likelihood ratio test statistic is:

```
q(s) = -2 * ln[L_p(s) / L_p(s_hat)]
```

where s_hat is the global MLE. Under regularity conditions, q(s) ~ chi^2(1) (Wilks' theorem), giving approximate confidence intervals.

**For the on/off problem** with n_on Poisson counts in t_on and n_off Poisson counts in t_off, with tau = t_on / t_off:

```
b_hat(s) = [n_on + n_off - (1+tau)*s + sqrt(D)] / [2*(1+tau)]

where D = [(n_on + n_off) - (1+tau)*s]^2 + 4*(1+tau)*n_off*s
```

This has an exact analytic form (derived by Rolke, Lopez, and Conrad, 2005), avoiding the need for numerical optimization.

**Advantage over simple chi-squared:** The profile likelihood correctly accounts for the uncertainty in b from the off-source measurement and does not require b to be known exactly. It also naturally respects the physical constraint s >= 0.

### 3.6 The On/Off Problem

The "on/off" problem is the prototypical statistical problem in low-background counting experiments: you have a measurement of signal + background (on) and a separate measurement of background only (off), with different exposure times or effective areas.

**Formal setup:**
- n_on ~ Poisson(s * t_on + b * t_on) : counts in signal region
- n_off ~ Poisson(b * t_off) : counts in background region
- tau = t_off / t_on : ratio of background to signal exposure
- Known: n_on, n_off, tau
- Unknown: s (signal rate), b (background rate)

**The Li-Ma significance** (Li and Ma, 1983, widely used in gamma-ray astronomy):

```
S_LM = sqrt(2) * {n_on * ln[(1+tau)/tau * n_on/(n_on+n_off)]
                   + n_off * ln[(1+tau) * n_off/(n_on+n_off)]}^(1/2)
```

This is the square root of the profile likelihood ratio statistic and is asymptotically standard normal under H_0. It is the recommended significance measure for moderate-to-large counts (n_on + n_off > ~20).

**For small counts**, the exact probability must be computed:

```
P(n_on >= n_obs | s = 0) = sum from k=n_obs to infinity of
    sum from j=0 to infinity of Poisson(k | b*t_on) * Poisson(j | b*t_off) * [j == n_off]
```

which marginalizes over the unknown b. This is implemented in standard statistics packages.

---

## 4. Information-Theoretic Limits

### 4.1 Shannon Capacity of the UPE Channel

Consider the photon channel from a biological emitter to a detector. The information capacity places a fundamental upper bound on how much can be learned from the measurement.

**Poisson channel capacity.** For a photon channel with mean photon number n_s (signal) and n_b (background per mode), the capacity per mode is bounded by (Gordon, 1962; Giovannetti et al., 2014):

```
C <= g(n_s + n_b) - g(n_b)
```

where g(x) = (1+x) * ln(1+x) - x * ln(x) is the bosonic entropy function, measured in nats per mode.

For UPE parameters: n_s ~ 10^-6 photons per mode (signal), n_b ~ 10^-6 per mode (dark counts), at visible wavelengths (~500 nm, bandwidth ~500 nm):

The number of temporal-spectral modes per second is approximately:

```
M ≈ Delta_nu * 1 second ≈ (c * Delta_lambda / lambda^2) * 1 s ≈ 6 * 10^14
```

But the photon occupation per mode is:

```
n_s per mode = R_signal / M ≈ 50 / (6 * 10^14) ≈ 8 * 10^-14
```

In this ultra-low occupation limit, the capacity per mode simplifies to:

```
C ≈ n_s * ln(1/n_s) nats/mode  (for n_s << 1, n_b << n_s)
```

or, if background dominates (n_b >> n_s):

```
C ≈ n_s * ln(1 + n_s/n_b) ≈ n_s^2 / n_b nats/mode  (for n_s << n_b << 1)
```

The total capacity is:

```
C_total = M * C ≈ R_signal * ln(M / R_signal) nats/s   (background-free)
```

For R_signal = 50 photons/s:

```
C_total ≈ 50 * ln(6*10^14 / 50) ≈ 50 * 30 ≈ 1500 nats/s ≈ 2160 bits/s
```

This is the theoretical maximum information rate from the photon stream -- not the information about the signal rate, but the information carried by the photons themselves. In practice, the information extractable about the emission process is far less, limited by the number of detected photons.

### 4.2 Minimum Detectable Signal

The minimum signal rate detectable above a background rate b at significance alpha with integration time T is:

**Exact (Poisson):** Find the smallest s such that:

```
P(n >= n_crit | b*T) <= alpha
P(n >= n_crit | (s+b)*T) >= 1 - beta
```

where n_crit is the critical count (smallest n for which we reject H_0).

**Approximate (large bT):**

```
s_min ≈ (z_alpha + z_beta) * sqrt(b/T) + z_alpha^2 / (2*T)
```

For a PMT measurement with b = 30/s, T = 3600 s (1 hour), alpha = 0.05, beta = 0.20:

```
s_min ≈ (1.645 + 0.842) * sqrt(30/3600) + 1.645^2 / 7200
       ≈ 2.487 * 0.0913 + 0.000375
       ≈ 0.227 counts/s
```

So a 1-hour integration with a PMT (30/s dark rate) can detect a signal rate as low as ~0.23/s, or equivalently ~1.1 photons/cm^2/s for a 1 cm^2 collection area and 20% QE. This is marginal for UPE from neural tissue.

**With an SNSPD** (b = 0.1/s, eta = 90%):

```
s_min ≈ 2.487 * sqrt(0.1/3600) + 0.000375
       ≈ 2.487 * 0.00527 + 0.000375
       ≈ 0.0135 counts/s
```

This is ~0.015 photons/cm^2/s -- a factor of ~70 improvement, pushing well below the UPE floor.

### 4.3 Integration Time Requirements

The integration time T required to detect a signal rate s above background rate b at significance z_sigma is:

```
T ≈ (z_sigma / s)^2 * (s + 2*b)   [for Gaussian regime, bT >> 10]
```

**Table: Required integration times for 5-sigma detection (z=5)**

| Signal (photons/cm^2/s) | Detector | Background (counts/s) | QE | T (hours) | T (days) |
|--------------------------|----------|----------------------|-----|-----------|----------|
| 100 | PMT | 30 | 0.20 | 0.08 | -- |
| 50 | PMT | 30 | 0.20 | 0.26 | -- |
| 10 | PMT | 30 | 0.20 | 4.3 | 0.18 |
| 5 | PMT | 30 | 0.20 | 15.6 | 0.65 |
| 1 | PMT | 30 | 0.20 | 389 | 16.2 |
| 10 | EM-CCD (10x10 bin) | 0.01 | 0.90 | 0.0009 | -- |
| 1 | EM-CCD (10x10 bin) | 0.01 | 0.90 | 0.077 | -- |
| 0.1 | EM-CCD (10x10 bin) | 0.01 | 0.90 | 7.7 | 0.32 |
| 10 | SNSPD | 0.1 | 0.90 | 0.0004 | -- |
| 1 | SNSPD | 0.1 | 0.90 | 0.039 | -- |
| 0.1 | SNSPD | 0.1 | 0.90 | 3.9 | 0.16 |

Key observations:
- PMT measurements of faint UPE (1 photon/cm^2/s) require **16 days** of continuous integration at 5-sigma. This is why many published studies use 3-sigma or even 2-sigma thresholds.
- EM-CCD binning over 10x10 pixels dramatically reduces the effective background, making moderate UPE rates accessible in minutes.
- SNSPD reduces integration times by 2 orders of magnitude over PMTs.

### 4.4 Spectral Resolution vs. Signal Strength

The tradeoff between spectral information and statistical significance is severe in UPE research.

If the total UPE rate across 300--800 nm is R_total, and we divide the spectrum into N_lambda bins of width Delta_lambda = 500 nm / N_lambda, the rate per spectral bin is:

```
R_bin ≈ R_total / N_lambda * S(lambda) / <S>
```

where S(lambda) is the spectral shape (not flat -- UPE tends to peak at 500--600 nm).

**Spectral resolution cost:**

| Resolution | Bins | Photons/bin (if R_total = 50/s) | T for 5-sigma per bin (PMT) |
|-----------|------|--------------------------------|----------------------------|
| 500 nm (total) | 1 | 50/s | 15 min |
| 100 nm | 5 | ~10/s | 4.3 hr |
| 50 nm | 10 | ~5/s | 15.6 hr |
| 10 nm | 50 | ~1/s | 16 days |
| 1 nm | 500 | ~0.1/s | 4.4 years |

This explains a critical gap in the literature: **no complete high-resolution UPE spectrum has ever been acquired.** Published spectra (e.g., Cifra et al., 2007; Kobayashi et al., 1999) use broadband filters (50--100 nm width), not spectrometers, because the photon budget does not support spectral resolution finer than ~50 nm within practical integration times.

### 4.5 What Would a Complete UPE Spectrum Require?

To acquire a UPE spectrum at 10 nm resolution across 300--800 nm with 5-sigma significance in each bin:

**Scenario A: PMT with scanning monochromator**
- 50 spectral bins, ~1 count/s per bin in the peak, less at edges
- Need ~16 days per bin at the faintest wavelengths
- Total: ~800 days sequential scanning (absurd)
- Multiplexed with 50-channel PMT array: ~16 days (very expensive)

**Scenario B: EM-CCD with transmission grating**
- Disperses spectrum across pixel columns
- Each column receives ~0.1--1 photon/s
- With 10x1 pixel binning (spatial x spectral): background ~0.01 e-/s per bin
- Integration time per frame: ~2 hours for 3-sigma per spectral bin
- Total: ~10 hours for a reasonable spectrum (feasible!)

**Scenario C: SNSPD with fiber-coupled spectrometer**
- 50 fiber channels, each to an SNSPD element
- Background: 0.1/s per channel
- Integration: ~4 hours for 5-sigma in faintest bin (feasible but costly)

The conclusion: **an EM-CCD with dispersive optics is the most practical path to the first high-resolution UPE spectrum.** This has been attempted in limited form (Nakamura and Hiramatsu, 2005) but not with modern back-illuminated EM-CCDs.

---

## 5. Simulation Framework

### 5.1 Monte Carlo Photon Detection Simulation

A Monte Carlo simulation of the complete detection chain is essential for:
1. Validating statistical analysis methods
2. Designing optimal experimental protocols
3. Understanding systematic biases
4. Testing analysis pipelines on data with known truth

**Simulation architecture:**

```
Source Model          -->  Photon Transport  -->  Detector Model  -->  Electronics  -->  Analysis
(rate, spectrum,          (collection         (QE, dark counts,    (thresholds,       (statistical
 statistics,               efficiency,          afterpulse,         binning,           tests,
 temporal structure)       fiber coupling)      dead time)          digitization)      intervals)
```

**Step 1: Source model.** Generate photon arrival times from the emission model:

For thermal (chaotic) light:
```
Inter-arrival times ~ Exponential(R_signal)   [for single-mode thermal]
```

For coherent light:
```
Inter-arrival times ~ Exponential(R_signal)   [same marginal distribution]
```

The difference appears only in correlations (g^(2) function):
```
Thermal: g^(2)(0) = 2   (bunching)
Coherent: g^(2)(0) = 1  (no bunching)
Poisson: g^(2)(0) = 1   (same as coherent for single mode)
```

For multi-mode thermal light with M modes:
```
g^(2)(0) = 1 + 1/M
```

When M >> 1 (many spectral/spatial modes), g^(2)(0) approaches 1, making thermal and coherent light indistinguishable by intensity correlation. This is the fundamental difficulty of Track 04.

**Step 2: Transport and collection.** Apply collection efficiency:
```
For each photon, keep with probability eta_coll (typically 0.01--0.10)
```

**Step 3: Detector response.** For each surviving photon:
```
1. Apply QE: detect with probability eta_QE(lambda)
2. Check dead time: if time since last detection < tau_dead, discard
3. Apply timing jitter: t_detected = t_arrival + Normal(0, sigma_jitter)
4. Generate afterpulses: for each detection, with probability P_ap,
   add secondary event at t_detected + Exponential(1/tau_ap)
```

Add dark counts:
```
Generate Poisson(R_dark * T_total) events uniformly distributed over [0, T_total]
```

**Step 4: Merge and sort.** Combine signal detections, afterpulses, and dark counts into a single time-ordered event stream.

**Step 5: Analysis.** Apply the same analysis pipeline used on real data to the simulated event stream. Compare recovered parameters to known truth.

### 5.2 Detector Response Functions

Each detector type requires a specific response model.

**PMT response function:**

The single-photoelectron response (SPER) of a PMT is the pulse height distribution for true single-photon events. It is well-modeled by:

```
P(q | 1 p.e.) = (1-w) * Gamma(q | alpha, beta) + w * Exponential(q | mu_exp)
```

where the first term is the main peak (amplified single photoelectron) and the second is a low-amplitude exponential tail (incomplete multiplication in the first dynode). Typical parameters: w ~ 0.1--0.2, alpha ~ 4--10, beta ~ 0.2--0.5 mV*ns.

Setting the discriminator threshold requires balancing:
- Too low: dark pulses and electronic noise leak through.
- Too high: real photon events are lost.

Optimal threshold is typically at the valley between the noise pedestal and the single-p.e. peak, giving ~95% detection efficiency for real photons.

**EM-CCD response function:**

The output of the EM register for m input electrons follows:

```
P(x | m) = x^(m-1) * exp(-x/g) / [g^m * (m-1)!]    for m >= 1
P(x | 0) = delta(x) + CIC contribution               for m = 0
```

where g is the mean EM gain. In photon-counting mode, a threshold is applied:

```
Detection if x > T_thresh
```

The optimal threshold depends on g, read noise, and the CIC rate. For high gain (g > 1000), T_thresh = 5 * sigma_read is typical.

### 5.3 Optimal Filtering for Periodic Signals in Poisson Noise

If biophoton emission is modulated by neural oscillations (e.g., at frequencies corresponding to alpha, beta, or gamma rhythms), the signal has a periodic component:

```
R(t) = R_0 + R_1 * cos(2*pi*f_0*t + phi) + noise
```

where R_0 is the mean rate, R_1 is the modulation amplitude, and f_0 is the neural oscillation frequency.

**Rayleigh test for periodicity in event data.** Given N detected photon arrival times {t_i}, the Rayleigh statistic at frequency f is:

```
Z^2(f) = (2/N) * [(sum cos(2*pi*f*t_i))^2 + (sum sin(2*pi*f*t_i))^2]
```

Under the null hypothesis (no periodicity), 2*N*Z^2 ~ chi^2(2). The significance is:

```
P(Z^2 > z | H_0) = exp(-N*z/2)
```

**Minimum detectable modulation.** The modulation depth m = R_1/R_0 detectable at significance alpha with N total counts is approximately:

```
m_min ≈ sqrt(-2 * ln(alpha) / N)
```

For N = 10,000 counts (typical 1-hour PMT measurement at 50 counts/s including background) and alpha = 0.001:

```
m_min ≈ sqrt(2 * 6.91 / 10000) ≈ 0.037
```

So modulation depths above ~4% should be detectable with 1 hour of data. This is potentially accessible if neural oscillations modulate biophoton emission.

### 5.4 Matched Filtering from Gravitational Wave Detection

Gravitational wave detection faces a conceptually similar problem: extracting a known (or parameterized) signal waveform from noise that is much larger than the signal. The matched filter maximizes SNR when the signal shape is known.

**Adaptation to biophoton Poisson data.** In the Poisson regime, the log-likelihood for a signal template s(t) in the presence of background b is:

```
ln L = sum over bins i of [n_i * ln(s_i + b) - (s_i + b) - ln(n_i!)]
```

The optimal filter weights for detecting a signal with shape h(t) and unknown amplitude A (so s(t) = A * h(t)) are:

```
w_i = h_i / (A*h_i + b)
```

and the test statistic is:

```
T = sum_i w_i * n_i
```

In the background-dominated regime (A*h_i << b for all bins):

```
w_i ≈ h_i / b    (proportional to signal-to-background ratio)
```

This is the Poisson equivalent of the inverse-noise-weighted matched filter used in gravitational wave astronomy.

**Application:** If we have a theoretical prediction for the temporal or spectral shape of biophoton emission from a specific process (e.g., lipid peroxidation spectrum, or neural-activity-correlated emission modulation), the matched filter provides the optimal linear statistic for detecting it.

---

## 6. Research Opportunities

### 6.1 Integration Times for Coherence Tests

**Central question:** Can we distinguish coherent from thermal biophoton emission at realistic UPE rates?

The key observable is the second-order correlation function g^(2)(tau). For a single-mode source:
- Thermal: g^(2)(0) = 2
- Coherent: g^(2)(0) = 1
- Quantum (sub-Poissonian): g^(2)(0) < 1

But UPE is multi-mode. For M effective modes:
```
g^(2)(0) = 1 + 1/M
```

With M ~ 10^6 (estimated from spectral bandwidth / coherence bandwidth), the excess bunching is g^(2)(0) - 1 ~ 10^-6. The uncertainty in a g^(2)(0) measurement from N coincidence counts in time bin Delta_t is approximately:

```
sigma[g^(2)(0)] ~ 1 / sqrt(N_pairs)
```

where N_pairs is the number of photon pairs detected within the coherence time tau_c. For a count rate R and coherence time tau_c:

```
N_pairs ≈ R^2 * tau_c * T
```

To measure an excess of 10^-6, we need:

```
N_pairs > (10^6)^2 = 10^12
T > 10^12 / (R^2 * tau_c)
```

For R = 50 counts/s, tau_c = 10^-14 s (optical coherence time for ~500 nm bandwidth):

```
T > 10^12 / (2500 * 10^-14) = 4 * 10^23 seconds ≈ 10^16 years
```

**This is utterly infeasible.** The multi-mode nature of broadband UPE makes direct g^(2) measurement of coherence impossible without spectral filtering to a single mode (which reduces the rate by a factor of ~10^6, making it worse).

**Alternative approaches:**
1. **Spectral filtering to narrow bandwidth** (~0.01 nm, reducing M to ~1): Rate drops to ~0.00005/s. Need T > 10^12 / (2.5*10^-9 * 10^-14) = 4*10^34 s. Still impossible.

2. **Interferometric measurement** (Michelson or Mach-Zehnder): Measures first-order coherence g^(1)(tau). The fringe visibility V = |g^(1)(tau)| decays with path difference according to the spectral bandwidth. For broadband light, V drops to zero within ~1 um path difference. Detecting the fringes requires accumulating enough photons per phase bin -- approximately 1/V^2 photons for SNR = 1 on the visibility measurement. This is feasible for first-order coherence over short path differences.

3. **Hong-Ou-Mandel (HOM) interferometry**: Tests quantum indistinguishability of photon pairs. Requires coincident photon pairs from the source, which for thermal UPE are extraordinarily rare (see above).

4. **Photon number distribution**: Over integration times of seconds to minutes, the count distribution should be super-Poissonian (bunched) for thermal light and Poissonian for coherent light. The Fano factor F = Var(n) / <n> is 1 for Poisson and 1 + <n>/M for thermal. With <n> ~ 50 counts per 1-second bin and M ~ 10^6, the excess variance is ~5*10^-5. Detecting this requires ~(1/5*10^-5)^2 ≈ 4*10^8 measurement bins, or ~13 years. Still impractical.

**Bottom line:** Distinguishing coherent from multi-mode thermal biophoton emission by any known statistical method requires integration times vastly exceeding experimental practicality. The only tractable approaches are:
- Narrow-band spectral filtering combined with HBT correlation (reduces M but also reduces rate -- net effect is usually negative).
- Detecting non-classical statistics (g^(2)(0) < 1, photon antibunching) which cannot arise from any classical source, regardless of mode count.
- Looking for spectral signatures inconsistent with thermal emission (e.g., emission lines).

This is a fundamental result that constrains the entire research program and should be established rigorously through simulation (Section 5).

### 6.2 Optimal Experimental Design for Myelin Biophoton Detection

No published study has specifically measured biophoton emission from myelin-enriched tissue preparations. The experimental design must address:

**Sample preparation options:**
1. Intact myelinated nerve (e.g., rat sciatic nerve): contains both myelin and axonal cytoplasm.
2. Myelin membrane fraction (biochemically purified): pure myelin lipids and proteins, no live cells.
3. Oligodendrocyte culture (CNS) or Schwann cell culture (PNS): live cells actively producing myelin.
4. Brain slice (hippocampal or cortical): contains myelinated axon tracts.

**Key design parameters:**
- Sample area: maximize to increase total photon collection.
- Detector: EM-CCD for spatial mapping (to correlate emission with myelin tracts), PMT for highest temporal resolution.
- Integration time: minimum 30 minutes per measurement, based on Table in Section 4.3.
- Controls: demyelinated tissue (lysolecithin-treated), heat-killed tissue, buffer blank.
- Temperature: 37 C for live tissue (increases dark counts -- must use Peltier-cooled detector with shield).

**Sample size calculation:** To detect a difference of Delta_R = 5 photons/cm^2/s between myelinated and demyelinated tissue at 5-sigma with a PMT (b = 30/s, eta = 0.20):

```
N_measurements = 2 * (z_alpha + z_beta)^2 * [2*b + R_mean] / (eta * Delta_R)^2

For alpha = 0.05, beta = 0.10, R_mean = 50/s, Delta_R = 5/s:
N_measurements ≈ 2 * (1.645 + 1.282)^2 * [60 + 50] / (1.0)^2
              ≈ 2 * 8.57 * 110
              ≈ 1886 one-second bins per condition
              ≈ 31.4 minutes per condition
```

So a comparison between myelinated and demyelinated tissue requires ~30 minutes per condition, which is feasible.

### 6.3 Machine Learning for Photon Classification

At low count rates, each detected event's provenance is uncertain: is it a signal photon, a dark count, an afterpulse, or a cosmic ray? Machine learning could potentially classify events using features beyond simple threshold discrimination:

**Available features per event:**
- Pulse height (amplitude)
- Pulse shape (rise time, fall time, width)
- Time since last event (afterpulse indicator)
- Time since second-to-last event
- Local count rate (running average)
- Detector temperature at event time

**Approach:** Train a classifier (random forest or neural network) on labeled data:
- Dark counts: data with detector in complete darkness.
- Afterpulses: correlated secondary events identified by timing.
- Signal photons: calibrated attenuated laser source.
- Cosmic rays: events flagged by coincidence with a scintillator.

**Expected improvement:** Pulse shape discrimination alone can reduce dark counts by ~50% while retaining >95% signal efficiency in PMTs (established in nuclear physics). Adding timing information could reduce afterpulse contamination by >90%.

**Caution:** The classifier must be validated on independent data and its efficiency/contamination rates must be incorporated into the statistical analysis. A classifier that preferentially accepts events that "look like signal" will bias the measurement.

### 6.4 Multi-Detector Coincidence Counting

Using two or more detectors viewing the same sample, coincident detections (within a time window tau_coin) strongly suppress dark count contamination:

**Coincidence rate:**
```
R_coin_signal = eta_1 * eta_2 * R_pair * Omega_1 * Omega_2    (true coincidences from paired emission)
R_coin_accidental = 2 * tau_coin * R_1 * R_2                   (random coincidences)
```

where Omega_i is the solid angle fraction collected by detector i and R_pair is the pair emission rate (if any).

For independent (non-paired) emission, R_coin_signal = 0 and all coincidences are accidental. The accidental rate with R_1 = R_2 = 50/s and tau_coin = 10 ns:

```
R_coin_accidental = 2 * 10^-8 * 50 * 50 = 5 * 10^-5 /s = 0.18/hr
```

This is negligible compared to single-detector backgrounds, providing a nearly background-free measurement -- but only for correlated photon pairs. If UPE consists of independent single-photon events (as expected from thermal emission), coincidence counting gives zero signal.

**The coincidence technique is therefore a test of paired emission** (entangled photon generation, as hypothesized in Track 04). Its feasibility depends on the pair emission rate, which is unknown and potentially zero.

### 6.5 Adapting Particle Physics Methods

Several statistical methods from particle physics have direct applicability to biophoton research:

**CLs method (Read, 2002).** Used for setting upper limits at the LHC. The CLs value is:

```
CLs = P(q >= q_obs | s + b) / P(q >= q_obs | b)
```

This prevents excluding signal hypotheses to which the experiment has no sensitivity (the "empty region" problem). Directly applicable to setting upper limits on UPE from specific tissue types.

**Asymptotic formulae (Cowan et al., 2011).** Provide analytic approximations to the distributions of profile likelihood ratio test statistics, avoiding the need for computationally expensive toy MC studies. The key result: for a signal strength parameter mu, the discovery significance is:

```
Z_0 = sqrt(2 * [(s+b) * ln(1 + s/b) - s])
```

This is exact for the Poisson on/off problem and should replace ad-hoc significance estimates in biophoton papers.

**Look-elsewhere effect (Gross and Vitells, 2010).** When scanning for a signal at an unknown location (e.g., searching for spectral features across the UPE bandwidth), the probability of finding a significant fluctuation anywhere increases with the number of independent resolution elements. The global p-value is:

```
p_global ≈ p_local + <N_up(Z)>
```

where <N_up(Z)> is the expected number of upward crossings of the test statistic above level Z, related to the number of independent trials. For a spectrum with N_lambda bins, the naive Bonferroni correction is p_global <= N_lambda * p_local, but the Gross-Vitells formula is tighter when the bins are correlated.

---

## 7. Proposed Methodology

### 7.1 Simulation Studies

**Study 1: Feasibility of coherence detection.**
- Simulate thermal multi-mode UPE at realistic rates (10--100 photons/cm^2/s) with realistic detector models (PMT, EM-CCD, SNSPD).
- For each detector configuration, compute the integration time required to reject the coherent hypothesis (g^(2)(0) = 1) at 95% CL as a function of the number of modes M.
- Vary spectral filtering bandwidth from 500 nm (no filter) to 0.01 nm (single mode).
- Determine the optimal bandwidth that minimizes total integration time (trading mode count reduction against signal loss).
- **Expected output:** A phase diagram in (M, R_signal) space showing the feasibility boundary for each detector type.

**Study 2: Background subtraction systematics.**
- Simulate 1000 mock UPE experiments with realistic systematic effects: dark rate drift (0.1%/hour), afterpulsing (P_ap = 0.01--0.05), cosmic ray hits (1/cm^2/min), temperature fluctuation (+/- 0.1 C).
- Apply standard background subtraction protocols and Feldman-Cousins analysis.
- Quantify the bias and coverage of the confidence intervals under systematic contamination.
- **Expected output:** Recommendations for maximum acceptable levels of each systematic effect, and required monitoring precision.

**Study 3: Spectral measurement optimization.**
- Simulate a dispersive spectrometer (transmission grating + EM-CCD) for UPE spectral acquisition.
- Optimize the dispersion (spectral resolution) and binning strategy to maximize spectral information per unit integration time.
- Compare scanning monochromator (sequential) vs. dispersive (parallel) approaches.
- Include realistic EM-CCD noise (CIC, dark current, excess noise factor).
- **Expected output:** Recommended spectrometer design and integration time for 10 nm resolution spectrum with 5-sigma per bin.

**Study 4: Matched filter sensitivity for neural modulation.**
- Simulate UPE modulated at neural oscillation frequencies (1--100 Hz) with modulation depths of 1--50%.
- Apply the Rayleigh test and matched filter detection to simulated event streams.
- Determine minimum detectable modulation as a function of mean count rate and integration time.
- Include afterpulse contamination, which introduces spurious periodicity at the afterpulse timescale.
- **Expected output:** Sensitivity curves for modulation detection, with and without afterpulse correction.

### 7.2 Power Analysis for Planned Experiments

For each experiment in the research program, a formal power analysis should be conducted before data collection. The general procedure:

1. **Define the null and alternative hypotheses** precisely (e.g., H_0: emission rate from myelin = emission from demyelinated control; H_1: difference > Delta_R).
2. **Specify the test statistic** (likelihood ratio, Feldman-Cousins interval, Bayes factor).
3. **Set alpha and power** (typically alpha = 0.05, power = 0.90).
4. **Estimate nuisance parameters** from pilot data or the literature (background rate, detector efficiency, systematic uncertainty).
5. **Compute required sample size / integration time** either analytically (for simple models) or via MC simulation (for complex models with systematics).
6. **Check feasibility** against practical constraints (sample viability time, detector availability, total experimental time).

### 7.3 Recommended Detector Configurations

**Configuration A: Discovery (is there UPE from myelin?)**
- Detector: Cooled PMT (Hamamatsu H7421-40 or similar), R_dark < 30/s, QE ~40% at 500 nm.
- Optics: f/1 collection lens, 50 mm diameter, giving ~5 cm^2 effective collection area.
- Measurement: 1-hour integrations, alternating sample/blank every 10 minutes.
- Analysis: Feldman-Cousins unified intervals on background-subtracted rate.
- Sensitivity: ~1 photon/cm^2/s at 5-sigma in 4 hours.

**Configuration B: Spatial mapping (where does myelin emit?)**
- Detector: Back-illuminated EM-CCD (Andor iXon Ultra 897), QE > 90%, -85 C cooling.
- Optics: Microscope objective (10x or 20x) imaging tissue section onto CCD.
- Measurement: 30-minute frames in photon-counting mode, 100+ frames stacked.
- Analysis: Per-pixel Poisson significance map; spatial correlation with myelin stain (post-hoc fluorescence).
- Sensitivity: ~5 photons/cm^2/s per 100x100 um^2 region at 5-sigma in 10 hours.

**Configuration C: Temporal correlations (is emission structured?)**
- Detector: SPAD pair (Excelitas SPCM-AQRH-14) in Hanbury Brown-Twiss geometry.
- Optics: 50:50 beamsplitter, fiber-coupled to two SPADs.
- Measurement: Continuous time-tagged photon stream at 50 ps resolution, 24+ hours.
- Analysis: g^(2)(tau) computed from time-tagged data; Rayleigh test for periodicity.
- Sensitivity: Afterpulse-corrected g^(2) accuracy of ~0.01 at tau > 100 ns (limited by afterpulse uncertainty at shorter delays).
- **Critical:** Optical isolation between SPADs to prevent cross-talk (OD > 6).

**Configuration D: Definitive measurement (SNSPD-based)**
- Detector: 4-channel SNSPD system (e.g., Quantum Opus or PhotonSpot), R_dark < 0.1/s, QE > 85%.
- Optics: Fiber-coupled from cryostat-compatible sample mount.
- Measurement: Multi-channel coincidence and singles counting, 1+ hours.
- Analysis: Full Bayesian inference with informative priors from calibration.
- Sensitivity: ~0.01 photons/cm^2/s at 5-sigma in 4 hours (sufficient for even the faintest published UPE claims).
- **Limitation:** Requires collaboration with quantum optics laboratory. Small active area limits spatial coverage.

---

## 8. Key References

### Detection Theory and Low-Count Statistics

1. **Feldman, G.J. and Cousins, R.D.** (1998). "Unified approach to the classical statistical analysis of small signals." *Physical Review D*, 57(7), 3873. -- *The foundational paper for confidence intervals in low-count experiments. Should be the default method for all biophoton count rate reporting. Freely available as arXiv:physics/9711021.*

2. **Li, T.P. and Ma, Y.Q.** (1983). "Analysis methods for results in gamma-ray astronomy." *The Astrophysical Journal*, 272, 317--324. -- *Derives the likelihood-ratio significance test for on/off counting experiments. The Li-Ma formula is the standard in gamma-ray astronomy and directly applicable to biophoton background subtraction.*

3. **Rolke, W.A., Lopez, A.M., and Conrad, J.** (2005). "Limits and confidence intervals in the presence of nuisance parameters." *Nuclear Instruments and Methods in Physics Research A*, 551, 493--503. -- *Profile likelihood method for the on/off problem with exact analytic solution. Handles nuisance parameters (background rate, efficiency) without Bayesian priors.*

4. **Cowan, G., Cranmer, K., Gross, E., and Vitells, O.** (2011). "Asymptotic formulae for likelihood-based tests of new physics." *European Physical Journal C*, 71, 1554. -- *Provides analytic approximations to discovery significance and exclusion limits. The formula Z_0 = sqrt(2[(s+b)ln(1+s/b) - s]) is exact for Poisson counting.*

5. **Read, A.L.** (2002). "Presentation of search results: the CLs technique." *Journal of Physics G*, 28, 2693. -- *The CLs method for upper limits, used extensively at LEP and LHC. Prevents excluding hypotheses to which the experiment is insensitive.*

6. **Gross, E. and Vitells, O.** (2010). "Trial factors for the look elsewhere effect in high energy physics." *European Physical Journal C*, 70, 525--530. -- *Correcting for multiple hypothesis testing when scanning for spectral features.*

### Photon Detection and Detector Physics

7. **Hamamatsu Photonics.** (2017). *Photomultiplier Tubes: Basics and Applications*, 4th ed. -- *Comprehensive technical reference for PMT operation, noise characteristics, and photon counting. Available free from Hamamatsu website.*

8. **Robbins, M.S. and Bhatt, R.** (2004). "Review of the gain and noise characteristics of EM-CCDs." *Proceedings of SPIE*, 5555, 41--50. -- *Derives the excess noise factor F^2 = 2 for EM-CCD gain registers and its impact on photon counting.*

9. **Cova, S., Ghioni, M., Lacaita, A., Samori, C., and Zappa, F.** (1996). "Avalanche photodiodes and quenching circuits for single-photon detection." *Applied Optics*, 35(12), 1956--1976. -- *Comprehensive review of SPAD physics, including afterpulsing, dead time, and photon emission during avalanche -- the last point being critical for coincidence measurements.*

10. **Marsili, F. et al.** (2013). "Detecting single infrared photons with 93% system detection efficiency." *Nature Photonics*, 7, 210--214. -- *Demonstrates SNSPD performance that would be transformative for biophoton detection.*

### Biophoton Detection and Measurement

11. **Kobayashi, M., Takeda, M., Sato, T., Yamazaki, Y., Kaneko, K., Ito, K., Kato, H., and Inaba, H.** (1999). "In vivo imaging of spontaneous ultraweak photon emission from a rat's brain correlated with cerebral energy metabolism and oxidative stress." *Neuroscience Research*, 34, 103--113. -- *Landmark paper demonstrating EM-CCD imaging of brain biophotons. Key reference for signal levels and experimental protocol.*

12. **Cifra, M., Van Wijk, E.P.A., Koch, H., Bosman, S., and Van Wijk, R.** (2007). "Spontaneous ultra-weak photon emission from human hands is time dependent." *Radioengineering*, 16(2), 15--19. -- *Example of PMT-based UPE measurement protocol with background subtraction.*

13. **Salari, V., Valian, H., Bassereh, H., Bókkon, I., and Barkhordari, A.** (2015). "Ultraweak photon emission in the brain." *Journal of Integrative Neuroscience*, 14(3), 419--429. -- *Review of neural biophoton measurements and their proposed significance.*

14. **Usa, M., Kobayashi, M., and Inaba, H.** (1989). "Biophoton emission from heat-shocked HeLa cells." *Proceedings of the International Congress on Stress*, 231--237. -- *Early EM-CCD biophoton imaging demonstrating spatial emission patterns.*

### Information Theory and Quantum Optics

15. **Giovannetti, V., Garcia-Patron, R., Cerf, N.J., and Holevo, A.S.** (2014). "Ultimate classical communication rates of quantum optical channels." *Nature Photonics*, 8, 796--800. -- *Information capacity of bosonic channels; provides the upper bound on information extractable from UPE.*

16. **Mandel, L. and Wolf, E.** (1995). *Optical Coherence and Quantum Optics*. Cambridge University Press. -- *The definitive textbook on photon statistics, coherence functions, and detection theory. Chapters 9 (photon counting) and 14 (second-order coherence) are directly relevant.*

17. **Loudon, R.** (2000). *The Quantum Theory of Light*, 3rd ed. Oxford University Press. -- *More accessible than Mandel and Wolf. Chapter 6 (single-mode quantization) and Chapter 8 (photon counting) provide the formalism for interpreting UPE statistics.*

### Signal Processing and Optimal Detection

18. **Allen, B., Anderson, W.G., Brady, P.R., Brown, D.A., and Creighton, J.D.E.** (2012). "FINDCHIRP: An algorithm for detection of gravitational wave chirps." *Physical Review D*, 85, 122006. -- *The matched filter framework used in LIGO. Adaptable to searching for predicted spectral or temporal signatures in UPE data.*

19. **Scargle, J.D.** (1998). "Studies in astronomical time series analysis. V. Bayesian blocks, a new method to analyze structure in photon data." *The Astrophysical Journal*, 504, 405--418. -- *Bayesian method for finding change points and structure in photon arrival time series. Directly applicable to detecting temporal variability in UPE.*

20. **Cash, W.** (1979). "Parameter estimation in astronomy through application of the likelihood ratio." *The Astrophysical Journal*, 228, 939--947. -- *The Cash statistic (C-stat), a Poisson likelihood ratio that replaces chi-squared for low-count spectral fitting. Should be used instead of chi-squared for UPE spectral analysis.*

---

## Appendix A: Quick Reference Formulae

**Poisson significance for excess over background:**
```
Z = sqrt(2) * sqrt(n_on * ln[(1+tau)/tau * n_on/(n_on+n_off)]
                    + n_off * ln[(1+tau) * n_off/(n_on+n_off)])
```
(Li-Ma formula; tau = t_off/t_on)

**Minimum detectable rate (Gaussian approximation):**
```
s_min = (z_alpha + z_beta) * sqrt(b/T) + z_alpha^2 / (2T)
```

**Integration time for given significance:**
```
T = z^2 * (s + 2b) / s^2
```

**Poisson upper limit (90% CL, n observed):**
```
mu_upper = (1/2) * chi^2_inv(0.90, 2n + 2)
```

**Feldman-Cousins ordering principle:**
```
R(n) = P(n | s+b) / P(n | max(0, n-b) + b)
```

**g^(2) measurement uncertainty:**
```
sigma[g^(2)(tau)] ≈ sqrt(1 + g^(2)(tau))^2 / sqrt(R^2 * Delta_tau * T)
```
where R is the count rate, Delta_tau is the correlation time bin, and T is the total measurement time.

**EM-CCD SNR (photon counting mode):**
```
SNR = eta * N_photon / sqrt(F^2 * eta * N_photon + n_pix * (sigma_dark^2 + R_CIC))
```
with F^2 = 2.

**Coincidence rate (accidental):**
```
R_acc = 2 * tau_coin * R_1 * R_2
```

**Rayleigh test minimum detectable modulation:**
```
m_min = sqrt(-2 * ln(alpha) / N)
```

---

## Appendix B: Comparison with Other Low-Signal Fields

| Field | Signal Rate | Background Rate | Method | Integration Time | Key Innovation |
|-------|------------|-----------------|--------|-----------------|----------------|
| Biophoton UPE | 1--1000 /cm^2/s | 10--50 /s (PMT) | Single detector | Minutes--hours | Needs improvement |
| Dark matter (XENON) | <0.1 events/year | ~1 event/year | Coincidence + fiducial cuts | Years | Multi-parameter discrimination |
| Neutrino (SNO) | ~10 events/day | ~1 event/day | Cherenkov ring + PMT array | Years | Spatial + temporal pattern |
| Gamma-ray astronomy (Fermi) | 0.01--1 /s | 1--10 /s | Coded mask + spectral | Hours--days | Background modeling |
| Gravitational waves (LIGO) | h ~ 10^-21 strain | Seismic, thermal, quantum | Matched filter | Seconds (per event) | Template bank |
| CMB B-modes | ~0.01 uK polarization | Foreground: ~10 uK | Component separation | Years | Multi-frequency |

The biophoton field is unusual in having relatively straightforward detection physics (photon counting) but lacking the sophisticated statistical analysis infrastructure that other fields have developed. The methods described in this track aim to bridge that gap.

---

*Track 05 connects to: Track 01 (photocount statistics provide the signal model), Track 03 (waveguide models predict spatial emission patterns for matched filtering), Track 04 (coherence tests require the SNR analysis developed here), Track 06 (demyelination predictions require power analysis for experimental design).*
