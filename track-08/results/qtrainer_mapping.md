# QTrainerAI 17-Method Mapping to Biophoton Analysis

## 1. Overview

This document maps each of the 17 statistical methods implemented in QTrainerAI
for mind-matter interaction (MMI) detection to their biophoton analysis counterparts.
The mapping exploits the structural isomorphism between the two signal extraction
problems:

**MMI problem:** Extract a tiny intentional bias (SR ~ 0.51-0.52) from a
high-speed random bit stream. The bias is real but near the noise floor.

**Biophoton problem:** Extract a biological coherence signal (~1-100 photons/s/cm^2)
from detector noise (~10-50 dark counts/s). The signal is real but near the noise floor.

Both problems benefit from:
- Multiple independent statistical tests (sensitivity from diverse perspectives)
- Bayesian combination of evidence (principled aggregation)
- Careful handling of low signal-to-noise regimes

All 17 methods participate in the Combined BU (Scott directive: no exclusions,
all calibrations = 1.0). The same principle applies in the biophoton context:
all 17 adapted methods contribute to the coherence estimate.

---

## 2. Method-by-Method Mapping

### 2.1 MV -- Majority Vote / Mandel Q Parameter

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Binary QRNG bits (subtrial block) | Photon counts per time bin |
| **Computation** | Count hits in block; hit if majority match target | Compute Q = (Var - Mean) / Mean |
| **Hit criterion** | > 50% bits match | Q < 0 (sub-Poissonian) |
| **What it detects** | Simple majority bias | Variance suppression below shot noise |
| **Transfer quality** | Adapted | |
| **Relevant tracks** | Track 01 (photocount statistics) | |

**Mathematical relationship:**
- MMI: P(majority hit | SR) follows binomial statistics
- Biophoton: Q < 0 is a necessary condition for nonclassical light states
- Both test whether the observed data departs from the null (unbiased/Poissonian)

### 2.2 RWBA -- Random Walk Bias Amplification / Cumulative Photon Deviation

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Binary stream mapped to +1/-1 | Photon counts minus expected rate |
| **Computation** | Cumulative sum with absorbing barriers | Cumulative sum of (count - mean) |
| **Hit criterion** | Boundary crossing before trial end | Max |cumsum| > 2 sqrt(mean * N) |
| **What it detects** | Persistent directional bias | Sustained photon excess or deficit |
| **Transfer quality** | Direct | |
| **Relevant tracks** | Track 02 (time series) | |

**Mathematical relationship:**
- Both are random walk analyses testing for drift
- Under null, cumulative sum is a martingale with sqrt(N) diffusion
- Under alternative, drift term causes boundary crossing with probability dependent on effect size

### 2.3 AC1 -- Autocorrelation Lag-1

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Binary stream | Photon count time series |
| **Computation** | Normalized lag-1 autocorrelation | Same: C(1) = Cov(x_t, x_{t+1}) / Var(x) |
| **Hit criterion** | AC > significance threshold | AC > 2/sqrt(N) |
| **What it detects** | Short-range temporal structure in QRNG | Photon bunching/antibunching at shortest timescale |
| **Transfer quality** | Direct | |
| **Relevant tracks** | Track 02 | |

**Note:** In biophoton optics, this relates to the intensity autocorrelation
g^(1)(tau). Positive AC at lag 1 indicates photon bunching (super-Poissonian
temporal structure), while negative AC could indicate antibunching.

### 2.4 AC2 -- Autocorrelation Lag-2

Same as AC1 but at 2-bin lag. Probes longer-range temporal correlations.
Transfer is direct.

### 2.5-2.9 RA1-RA5 -- Running Average (Windows 3, 5, 10, 20, 50)

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Binary stream | Photon count time series |
| **Computation** | Moving average of hit rate over window W | Moving average of photon count over W bins |
| **Hit criterion** | Fraction of positive trends > 55% | Same |
| **What it detects** | Gradual bias onset at different timescales | Gradual emission rate changes |
| **Transfer quality** | Direct | |
| **Relevant tracks** | Track 02 | |

The five windows (3, 5, 10, 20, 50 bins) probe trend detection at different
timescales, from rapid onset to slow drift. This multi-scale approach is
valuable because coherence phenomena may build up gradually.

### 2.10-2.12 CA7, CA15, CA23 -- Cumulative Advantage (Windows 7, 15, 23)

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Binary stream in blocks | Photon counts in non-overlapping blocks |
| **Computation** | Linear trend across block means | Same: polyfit slope of block means |
| **Hit criterion** | Positive slope | Positive slope |
| **What it detects** | Progressive bias accumulation | Progressive emission increase |
| **Transfer quality** | Direct | |
| **Relevant tracks** | Track 02 | |

### 2.13 LZT -- Lempel-Ziv Complexity Test

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Binary QRNG stream | Binarized photon counts (above/below median) |
| **Computation** | LZ76 complexity | Same algorithm on binarized stream |
| **Hit criterion** | LZ < 90% of expected | Same threshold |
| **What it detects** | Low algorithmic complexity = structured bias | Low complexity = structured emission pattern |
| **Transfer quality** | Adapted (binarization step required) | |
| **Relevant tracks** | Track 02, Track 05 | |

**Binarization note:** Photon counts are continuous-valued, so we binarize by
comparing to the window median. This is the simplest approach; more sophisticated
binarizations (e.g., relative to Poisson expectation) are possible.

### 2.14 KS -- Kolmogorov-Smirnov Test

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | QRNG output distribution | Photon count distribution |
| **Computation** | D_max = sup |F_n(x) - F_0(x)| | D = sup |F_n(x) - Poisson_CDF(x; mean)| |
| **Hit criterion** | p < 0.05 (KS test) | p < 0.05 |
| **What it detects** | Distribution deviates from expected | Counts deviate from Poisson |
| **Transfer quality** | Direct | |
| **Relevant tracks** | Track 01, Track 05 | |

**Critical note (from QTrainerAI KS bug fix, Feb 6 2026):** The KS test uses
only |F_n(k) - F_0(k)| for D_max (not the left-side check |F_n(k-1) - F_0(k)|
which inflates D for discrete distributions with the same support). This same
careful treatment applies to the biophoton version.

### 2.15 M2 -- Fano Factor Test

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Block-level statistics | Photon counts |
| **Computation** | Higher-order bias detection | F = Var(n) / Mean(n) |
| **Hit criterion** | Method-specific | F < 0.95 (sub-Poissonian) |
| **What it detects** | Secondary bias signature | Variance suppression |
| **Transfer quality** | Adapted | |
| **Relevant tracks** | Track 01 | |

**Relationship to MV:** The Fano factor (F = 1 + Q) is mathematically equivalent
to the Mandel Q test but uses a different threshold. Having both provides
robustness -- if the distribution is near the boundary, one may trigger while
the other does not.

### 2.16 M3 -- Second-Order Coherence g^(2)(0)

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Block-level statistics | Photon counts |
| **Computation** | Tertiary bias detection | g^(2)(0) = <n(n-1)> / <n>^2 |
| **Hit criterion** | Method-specific | g^(2) < 1.0 (antibunched) |
| **What it detects** | Third-level bias pattern | Photon antibunching (nonclassical) |
| **Transfer quality** | Analogous | |
| **Relevant tracks** | Track 01, Track 04 | |

**This is the most physics-rich adaptation.** In quantum optics, g^(2)(0) < 1
is a definitive signature of nonclassical light. No classical source can produce
antibunching. If biophotons show g^(2)(0) < 1, this is strong evidence for
quantum coherence in biological emission.

### 2.17 M4 -- Shannon Entropy Test

| Aspect | QTrainerAI (MMI) | Biophoton Adaptation |
|--------|------------------|---------------------|
| **Input** | Block-level statistics | Photon count distribution |
| **Computation** | Quaternary bias detection | H = -sum(p_k log2 p_k) |
| **Hit criterion** | Method-specific | H < H_Poisson |
| **What it detects** | Entropy-based anomaly | Low-entropy = ordered emission |
| **Transfer quality** | Adapted | |
| **Relevant tracks** | Track 01, Track 05 | |

**Reference entropy:** For Poisson distribution with mean lambda,
H_Poisson ~ 0.5 * log2(2 pi e lambda) for large lambda. Lower entropy
indicates more ordered emission than thermal/random.

---

## 3. Transfer Quality Summary

| Quality | Methods | Count | Description |
|---------|---------|-------|-------------|
| **Direct** | rwba, ac1, ac2, ra1-ra5, ca7, ca15, ca23, ks | 12 | Identical algorithm on different data type |
| **Adapted** | mv, lzt, m2, m4 | 4 | Same principle, modified input preprocessing |
| **Analogous** | m3 | 1 | Different domain-specific interpretation |

12 of 17 methods transfer directly from binary QRNG streams to photon count
streams. This high transfer rate validates the structural isomorphism between
the two signal extraction problems.

---

## 4. Combined BU for Biophoton Coherence

The Combined BU operates identically in both domains:

1. Each method produces an observation (+1 hit or 0 miss) per analysis window
2. Each method maintains its own BU posterior (prior 0.51, SR 0.515)
3. Method outcomes (posterior > 0.5 = hit) feed into the Combined BU
4. Combined posterior estimates overall coherence confidence

**Scott's directives apply equally:**
- Initial prior: 0.51 (NOT 0.515)
- Likelihood: 0.515
- All 17 methods participate (no exclusions)
- All calibrations: 1.0
- One code path (no separate calculation branches)
- "State is observation, Posterior becomes Prior"

---

## 5. Implementation

The full implementation is in `src/qtrainer_bridge.py` and `src/bayesian_coherence.py`.

Usage:
```python
from src.qtrainer_bridge import apply_all_methods, compute_combined_bu_from_methods
import numpy as np

# Photon counts (e.g., from PMT, 1-second bins)
counts = np.array([52, 48, 55, 47, 53, 49, 51, 48, 54, 50, ...])

# Apply all 17 methods
results = apply_all_methods(counts)

# Compute combined BU posterior
posterior, history = compute_combined_bu_from_methods(results)

print(f"Combined posterior: {posterior:.4f}")
print(f"Coherence state: {'high' if posterior > 0.6 else 'indeterminate' if posterior > 0.4 else 'low'}")
```

---

## 6. Bidirectional Transfer

The mapping is not one-way. Biophoton analysis methods also transfer back to MMI:

| Biophoton Method | MMI Application | Track |
|------------------|-----------------|-------|
| Fractal/DFA analysis | Temporal structure in QRNG output | Track 02 |
| Waveguide mode analysis | CCF circuit geometry optimization | Track 03 |
| Cavity QED formalism | Quantum state of CCF circuit | Track 04 |
| Feldman-Cousins statistics | Low-effect-size MMI significance | Track 05 |
| Photocount distribution fitting | QRNG output classification | Track 01 |

These reverse-transfer methods are not yet implemented but represent future
work for the Track 08 bridge.
