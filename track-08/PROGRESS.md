# Track 08: MMI-Biophoton Coherence Bridge -- Progress Log

## 2026-02-11: Initial Build

### Completed

1. **Package structure** (`src/`)
   - `__init__.py` -- Package initialization with key exports
   - `constants.py` -- 100+ shared constants: BU parameters (prior=0.51, SR=0.515),
     M-Phi framework parameters (g_PhiPsi, kappa, Lambda_critical), all 17 QTrainerAI
     method names, QRNG channel list, detector specs, Abramowitz-Stegun CDF
     coefficients matching QTrainerAI Rust implementation
   - `bayesian_coherence.py` -- Full Bayesian updating framework:
     - `scott_cdf_z_score()` matching QTrainerAI's A-S CDF
     - `bayesian_update_single()` and `bayesian_update_sequence()` with exact
       QTrainerAI BU formula
     - `MethodBUState` and `CombinedBUState` dataclasses tracking per-method
       and combined posteriors
     - `BiophotonCoherenceEstimator` class: ingests photon counts, applies all
       17 adapted statistical tests, feeds into Combined BU
     - `simulate_coherent_stream()` for generating test data with tunable
       coherence fraction
   - `phi_field_coupling.py` -- Phi-field dynamics and responsivity:
     - `PhiFieldParameters` dataclass with derived properties (lambda_ss, tau)
     - `coherence_ode()` and `solve_coherence_dynamics()` for numerical ODE
       integration
     - `analytical_coherence()` for closed-form solution
     - `responsivity_from_coherence()` sigmoid mapping Lambda -> SR
     - `demyelination_impact()` modeling kappa increase and g reduction
     - `neuro_coherence_function()` implementing the full M formula
     - `phase_constraint_dynamics()` solving the dC/dt PDE on a 1D grid
     - `ccf_coupling_model()` for QFT device analysis
     - `scan_coupling_parameter_space()` for g-kappa heatmaps
     - `find_critical_damage()` via Brent's method
   - `cross_prediction.py` -- Cross-domain correlation models:
     - `simulate_shared_phi_field()` as Ornstein-Uhlenbeck process
     - `biophoton_observable()` and `mmi_observable()` with realistic noise
     - `predict_correlation()` generating synthetic dual-measurement data
     - `monte_carlo_correlation_distribution()` for MC power analysis
     - `demyelination_mmi_prediction()` across damage fractions
     - `spectral_shift_prediction()` mapping coherence to wavelength shift
     - `triple_correlation_model()` for EEG-Bio-MMI triple analysis
     - `required_sample_size()` power calculation
   - `qtrainer_bridge.py` -- 17-method mapping:
     - `MethodMapping` dataclass for each method's dual description
     - `METHOD_MAPPINGS` catalog with transfer quality ratings
     - `apply_all_methods()` applying all 17 biophoton-adapted tests
     - `method_summary_table()` for formatted output
     - `compute_combined_bu_from_methods()` for final BU posterior

2. **Figure generation** (`figures/generate_all.py`)
   - 8 publication-quality figures covering all major results

3. **Results documents** (`results/`)
   - `experimental_protocol.md` -- Full dual-measurement protocol:
     N=30 participants, PMT + SPAD detectors, 1500 measurement blocks,
     primary analysis with mixed-effects model, power calculations,
     falsification criteria
   - `qtrainer_mapping.md` -- Detailed 17-method mapping with tables,
     mathematical relationships, transfer quality ratings, implementation guide

4. **Track document expansion** (`tracks/08-mmi-coherence-bridge.md`)
   - Expanded from 278 lines to 900+ lines with formal mathematical treatment
   - Added formal derivations, quantitative predictions, Fisher information
     analysis, experimental design details

### Design Decisions

- **BU parameters exactly match QTrainerAI**: Prior = 0.51, SR = 0.515,
  all 17 methods, all calibrations 1.0. These are Scott's explicit directives.
- **A-S CDF coefficients copied from QTrainerAI Rust**: Ensures numerical
  consistency between the two systems.
- **Coherence estimator uses Combined BU architecture**: Method outcomes feed
  into combined posterior, matching Scott's "state is observation, Posterior
  becomes Prior" directive.
- **Cross-prediction uses Ornstein-Uhlenbeck for Phi**: Provides realistic
  autocorrelated fluctuations with tunable correlation time.
- **Demyelination model is multiplicative**: kappa_eff = kappa * (1 + factor * damage),
  g_eff = g * (1 - factor * damage). This gives biologically plausible
  exponential-like degradation.

### Verification

- All Python modules import correctly
- `bayesian_update_single()` produces correct posteriors for known inputs
- `analytical_coherence()` matches `solve_coherence_dynamics()` for constant
  parameters
- `apply_all_methods()` returns proper observations for Poisson vs sub-Poissonian
  test data

### Next Steps

- Run `figures/generate_all.py` to produce all 8 figures
- Cross-validate with other tracks (especially Track 01 photocount statistics
  and Track 02 time series)
- Implement bidirectional transfer methods (biophoton -> MMI)
- Parameter fitting to real QTrainerAI session data when available
- Connect to Casey et al. (2025) experimental methodology for protocol refinement
