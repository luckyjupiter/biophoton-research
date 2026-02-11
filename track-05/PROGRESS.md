# Track 05: Signal-to-Noise & Detection Theory -- Progress Log

## Status: Computational Framework Complete

### Deliverables Completed

#### 1. Detector Simulators (`src/detectors.py`)
- Monte Carlo simulation of complete detection chain for PMT, SPAD, EMCCD, SNSPD
- Spectral QE curves from manufacturer data (bialkali, GaAsP, Si, BI-CCD, SNSPD)
- Noise models: dark counts (Poisson), afterpulsing (exponential delay), dead time
  (non-paralyzable), timing jitter (Gaussian)
- EMCCD frame simulator with EM gain register (Gamma distribution), CIC, read noise
- Verified: 1-hour simulation of 50 ph/s signal shows expected SNR for all detectors

#### 2. SNR Calculators (`src/snr_calculator.py`)
- Analytic SNR for photon counting: `SNR = eta*S*T / sqrt(F^2*eta*S*T + B*T)`
- Background-subtracted on/off measurement SNR
- Li-Ma significance for on/off counting experiments
- Cowan asymptotic discovery significance (exact for Poisson)
- Minimum detectable signal: both Gaussian approximation and exact Poisson
- Integration time calculator for arbitrary significance target
- Poisson confidence intervals (Garwood exact method)
- Feldman-Cousins unified confidence intervals (numerically computed)
- Feasibility tables for all detector types across UPE signal range

#### 3. ROC Analysis (`src/roc_analysis.py`)
- Poisson ROC curves with Gaussian approximation for large counts
- AUC computation for detection scenarios
- Operating point finder (threshold for given FPR)
- Power analysis: integration time for given power
- Rate difference detection: time to distinguish two emission rates
- Seven standard biophoton detection scenarios analyzed

#### 4. Optimal Protocol Design (`src/optimal_protocol.py`)
- Optimal on/off time ratio calculation
- Time-gating SNR improvement analysis
- Coincidence window optimization for pair detection
- Spectral binning optimization (information vs resolution tradeoff)
- Adaptive integration strategy simulation
- g(2) measurement requirement calculator

#### 5. Artifact Catalog (`src/artifacts.py`)
- 10 artifact sources cataloged with rates, signatures, and mitigations
- Delayed luminescence simulator (power-law decay)
- Chemiluminescence simulator (with drift)
- Afterpulse g(2) contamination calculator
- Cosmic ray event simulator
- Critical finding: chemiluminescence is NOT easily distinguished from true UPE

#### 6. Figures (`figures/`)
- `qe_curves.png`: Spectral QE curves for all five detector types
- `snr_maps.png`: 2D SNR feasibility maps (signal rate vs integration time)
- `integration_times.png`: Required integration time vs signal rate
- `roc_curves.png`: ROC curves for PMT and alternative detector scenarios
- `detector_comparison.png`: Bar chart comparison of key detector metrics
- `afterpulse_g2_contamination.png`: g(2) excess from afterpulsing vs time lag
- `poisson_confidence_intervals.png`: Exact Poisson confidence intervals
- `discovery_significance.png`: Cowan significance vs expected counts

#### 7. Results (`results/`)
- `feasibility_table.txt`: Complete detection feasibility across detectors
- `minimum_integration_times.txt`: Integration times for four measurement scenarios
- `artifact_characterization.txt`: Full artifact catalog with control experiments

### Key Findings

1. **PMT is adequate for moderate UPE (>10 ph/cm2/s)**: 4 hours for 5-sigma
   detection with standard cooled bialkali PMT and 5 cm2 collection area.

2. **Faint UPE (<1 ph/cm2/s) requires 16+ days with PMT**: Impractical without
   extraordinary stability. SNSPD reduces this to ~4 hours but at prohibitive cost.

3. **g(2) coherence detection is fundamentally infeasible**: Multi-mode broadband
   UPE has g(2)(0) - 1 ~ 10^-6, requiring >10^16 years of integration. This is
   the single most important negative result for the research program.

4. **EM-CCD is the optimal path to first UPE spectrum**: With pixel binning and
   dispersive optics, 10 nm resolution spectrum achievable in ~10 hours.

5. **Chemiluminescence is the most dangerous artifact**: Broad spectrum, steady
   rate, indistinguishable from UPE without careful controls. Every biophoton
   experiment must include dead tissue and antioxidant controls.

6. **Afterpulsing dominates g(2) at tau < 100 ns**: PMT afterpulse probability
   of 2% creates g(2) excess of ~3000 at 1 ns delay. Correlation measurements
   below 100 ns time lag are dominated by this artifact.

7. **Spectral resolution costs photon budget severely**: Going from 500 nm
   (broadband) to 10 nm resolution requires 50x longer integration per bin.
   No published study has achieved better than ~50 nm spectral resolution on UPE.

### Dependencies on Other Tracks
- Track 01: Photocount statistics provide the signal model (Poisson vs thermal)
- Track 03: Waveguide models predict spatial emission patterns
- Track 04: Coherence tests require the SNR analysis developed here
- Track 06: Demyelination predictions need power analysis from this track
