# Master Prediction Table

Consolidated quantitative, falsifiable predictions from the biophoton research program. Every prediction includes the expected value, required experimental setup, and the observation that would falsify it. Predictions are drawn from computational results in Tracks 01, 04, 05, 06, 07, and 08, plus the waveguide simulator in `models/waveguide.py`.

---

## 1. Photocount Statistics (Track 01)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Track |
|---|-----------|---------------|----------------|------------------------|-------|
| 1.1 | Broadband thermal biophoton emission is indistinguishable from Poissonian by Fano factor | Q = mu/M ~ 10^-12 (for M ~ 10^13 modes, mu ~ 1-100) | Cooled PMT, 1-sec bins, N >= 10^6 intervals | Measured |Q| > 0.003 with N = 10^6 intervals at any realistic UPE rate | 01 |
| 1.2 | Maximum distinguishable thermal mode count M is ~2000 even with 10^6 counting intervals | Max M ~ 2000 at mu=10, alpha=0.05, N=10^6 | PMT, 11.6 days continuous measurement at 1-sec resolution | M > 10^4 distinguishable from Poisson with N = 10^6 | 01 |
| 1.3 | SNSPD preserves sub-Poissonian signature; PMT destroys it | F_measured: PMT = 0.970, SNSPD = 0.581 (for F_true = 0.5, mu=10) | Both detector types on same source | PMT measurement recovers F < 0.95 without SNSPD-class QE (eta > 0.80) | 01 |
| 1.4 | Rate modulation depth > 2.1% produces spurious super-Poissonian false positives above 5% | False positive rate exceeds 5% at 2.1% modulation depth (N=5000, alpha=0.05) | Sinusoidally modulated Poisson source, PMT | Stationary biological source with < 2% rate modulation shows F > 1 at 5% significance | 01 |
| 1.5 | Squeezed-state fitting of classical negative-binomial data yields BIC-inferior fit | NB: BIC=3931; Squeezed: BIC=3944 (4-param squeezed always penalized vs 2-param NB) | Bayesian model comparison on simulated NB(mu=5, M=3) data | Squeezed-state model preferred by BIC over true generating model for any NB dataset | 01 |

---

## 2. Quantum Optics / Cavity QED (Track 04)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Track |
|---|-----------|---------------|----------------|------------------------|-------|
| 2.1 | Myelin cavity operates in weak-coupling regime | Cooperativity C ~ 8.8 x 10^-4; Purcell factor F_P ~ 1.2 x 10^-3 | Cavity QED computation for a=1 um, d=1 um, L=500 um | C > 0.1 or strong coupling (g > kappa) at biologically realistic parameters | 04 |
| 2.2 | Biphoton entanglement entropy is modest with dephasing | S ~ 0.017 bits at d = 1.0 um (with T2* ~ 1 ps vibrational dephasing) | Schmidt decomposition of joint spectral amplitude | S > 0.1 bits with realistic dephasing (T2* ~ 1 ps) in condensed-phase lipid | 04 |
| 2.3 | Cavity Q factor is low (~5) due to small index contrast | Q ~ 5.1 (limited by Delta_n = 0.06 myelin-axon, 0.10 myelin-ISF) | Transfer matrix or FDTD cavity simulation | Q > 50 for realistic myelin dielectric parameters at mid-IR | 04 |
| 2.4 | Photon coherence length is ~4 um (shorter than internode) | l_coh ~ 3.9-4.1 um (limited by cavity Q) | Coherence length from Q/omega | l_coh > 50 um at mid-IR in myelin cavity | 04 |
| 2.5 | Cascade photon frequencies are non-degenerate (Morse anharmonicity) | |1>->|0>: 3.537 um; |2>->|1>: 3.697 um (Delta = 160 nm, ~15.2 meV/quantum) | Morse oscillator computation with omega_e = 2950 cm^-1, x_e chi_e = 62.5 cm^-1 | Frequency difference < 50 nm for C-H Morse parameters | 04 |
| 2.6 | Bell-CHSH test requires detector efficiency eta > 0.89 | S_max depends on visibility V; need eta > 0.89 at V=0.9 | SNSPD at mid-IR (3-4 um) with Franson interferometer | Bell violation (S > 2) observed with eta < 0.85 | 04 |
| 2.7 | g^(2)(0) for biphoton cascade should far exceed 2 (heralded detection) | g^(2)(0) >> 2 (up to ~100 for heralded biphoton) for quantum; <= 2 for classical thermal | HBT interferometry with mid-IR SNSPD, ps timing | g^(2)(0) <= 2 from myelin sample under any condition (rules out biphoton cascade) | 04 |

---

## 3. Detection Feasibility (Track 05)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Track |
|---|-----------|---------------|----------------|------------------------|-------|
| 3.1 | PMT detects 10 ph/cm^2/s biophoton signal at 5-sigma in 18 seconds | T = 17.5 s (bialkali PMT, 5 cm^2 area, 30/s dark, QE=0.20) | Hamamatsu H7421-40 or similar cooled PMT | 5-sigma detection requires > 10 min at 10 ph/cm^2/s with standard PMT | 05 |
| 3.2 | PMT at 1 ph/cm^2/s requires 25.4 min for 5-sigma | T = 25.4 min (bialkali PMT) | Same PMT configuration, longer integration | 5-sigma achieved in < 5 min or requires > 2 hours at this rate | 05 |
| 3.3 | Direct g^(2) measurement of broadband UPE coherence is fundamentally infeasible | T > 10^16 years to distinguish g^(2)(0) = 1 + 10^-6 from 1.0 at R=50/s | Any detector, 1 ns time bins | Feasible g^(2) coherence test demonstrated at broadband UPE rates in < 10 years integration | 05 |
| 3.4 | SNSPD achieves 4.3x higher SNR than bialkali PMT at matched conditions | SNR ratio = 408.9/94.5 = 4.33x (1-hour, 50 ph/s incident) | Side-by-side PMT vs SNSPD on calibrated source | SNR advantage < 2x with SNSPD (eta>0.90, dark<0.1/s) vs cooled PMT | 05 |
| 3.5 | Collection area dominates over detector quality for UPE | SPAD AUC = 0.531 vs PMT AUC = 1.000 at moderate UPE despite SPAD's superior per-photon metrics | ROC analysis across detector types | SPAD (0.002 cm^2) outperforms PMT (5 cm^2) in AUC for any realistic UPE scenario | 05 |
| 3.6 | Myelinated vs demyelinated tissue distinguishable in < 10 min with PMT | T = 8.1 min for Delta_R = 5 ph/s at 80% power, 5% FPR (bialkali PMT) | PMT with paired tissue samples | Requires > 1 hour to distinguish 10% emission difference between tissue types | 05 |

---

## 4. Demyelination Pathology (Track 06)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Track |
|---|-----------|---------------|----------------|------------------------|-------|
| 4.1 | Active demyelination produces 10-100x emission burst | EAE peak: 92.8x baseline (927.5 vs 10.0 ph/s/cm^2); Cuprizone peak: 54x (542.5 ph/s/cm^2) | Ex vivo optic nerve or corpus callosum from EAE/cuprizone mouse, PMT/EM-CCD | Active demyelination produces < 3x emission increase in any animal model | 06 |
| 4.2 | Spectral blueshift of ~52.3 nm per lost myelin layer | Delta_lambda = -52.3 nm/layer (Zeng et al. 2022 waveguide model) | Bandpass filter wheel or spectrometer on demyelinating nerve preparation | Blueshift < 20 nm/layer or no detectable spectral shift with progressive demyelination | 06 |
| 4.3 | Singlet O2 emission peaks (634/703 nm) distinguish autoimmune from toxic demyelination | Higher 634/703 nm ratio in EAE (MPO-driven) vs cuprizone (mitochondrial ROS, carbonyl-dominated) | Dual-wavelength PMT or spectral imaging of matched EAE vs cuprizone samples | No spectral difference between autoimmune and toxic demyelination models | 06 |
| 4.4 | EAE temporal emission profile: spike at peak (day 14-18), decline in chronic phase | Pre-symptomatic 11x -> Onset 52x -> Peak 93x -> Chronic 17x (relative to baseline) | Serial ex vivo measurements at days 7, 12, 18, 28+ post-immunization | Emission profile is monotonic (no peak) or peak occurs outside day 10-20 window | 06 |
| 4.5 | Cuprizone model shows remyelination-associated spectral partial recovery | Week 6: maximal blueshift + 54x emission; Week 12 (off cuprizone): emission reduces, spectral shift partially reverses | Longitudinal cranial window measurements on cuprizone-fed mice | No spectral recovery after cuprizone withdrawal despite histological remyelination | 06 |
| 4.6 | Kappa (decoherence rate) increases 5-17x across disease stages | Healthy: 0.04 s^-1; Mild: 0.208 (5.2x); Moderate: 0.499 (12.5x); Acute relapse: 0.661 (16.5x) | Derived from kappa decomposition model (thermal + structural + ROS + inflammatory) | Coherence measurements show kappa_disease/kappa_healthy < 2x at moderate demyelination | 06 |
| 4.7 | Combined multi-parameter biomarker outperforms any single marker | Combined AUC > 0.8 at moderate disease; best single (spectral shift) AUC ~ 0.85-0.95 | Simultaneous photon count + spectral shift + SO2/carbonyl ratio + g^(2)(0) | Any single biomarker achieves AUC >= combined score at all disease stages | 06 |
| 4.8 | Entanglement threshold: S drops abruptly below d ~ 0.45 um myelin thickness | S -> 0 below d = 0.45 um (abrupt, not gradual) | Cavity QED model + progressive chemical demyelination of ex vivo tissue | Entanglement decreases linearly with thickness (no threshold) | 06 |
| 4.9 | Sample size for primary comparison (moderate demyelination, d ~ 1.0) is n = 10/group | n = 10 per group at 80% power for Cohen's d ~ 1.0; early detection (d ~ 0.3) needs n = 90 | Standard power analysis for two-group comparison | Adequate power requires n > 30/group at moderate disease stage | 06 |

---

## 5. Unified Multi-Scale Model (Track 07)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Track |
|---|-----------|---------------|----------------|------------------------|-------|
| 5.1 | Photon generation rate: 1-100 photons/s per neuron from ROS cascade | Phi_photon = k_rad_C * [^3C*] * V_cell + k_rad_O2 * [^1O2] * V_cell | Gillespie SSA of full ROS cascade with realistic rate constants | Measured UPE from single identified neuron < 0.01 or > 10^4 photons/s | 07 |
| 5.2 | Waveguide coupling efficiency eta_couple ~ 10^-4 to 10^-2 | eta_couple = eta_angular (~0.10) x eta_mode (~0.01-0.1) x eta_spatial | Mode overlap integral for isotropic dipole emitter in periaxonal space | Measured coupling > 0.1 (10%) for isotropic emitter into myelin guided modes | 07 |
| 5.3 | Multi-node transmission (10 nodes, optimistic): T_total ~ 0.35 | T_node = 0.90 at anti-resonance -> T_total = 0.90^10 = 0.35 | TMM/BPM waveguide simulation or direct ex vivo measurement | T_total > 0.80 for 10-node propagation (would require T_node > 0.98) | 07 |
| 5.4 | Biophoton channel capacity is 2-5 orders of magnitude below chemical synapses | C_photon ~ 0.01-1 bits/s per channel vs C_synapse ~ 1-1000 bits/s | Information-theoretic calculation with realistic rates | Photonic channel capacity > 100 bits/s per channel at realistic UPE rates | 07 |
| 5.5 | Activity-photon correlation peaks at 1-10 ms lag (metabolic response time) | Cross-correlation peak at tau ~ 1-10 ms; kernel h(t) with rise ~ms, decay ~100 ms | Simultaneous LFP + single-photon detection on neural tissue slice | No temporal correlation between neural activity and biophoton emission at any lag | 07 |
| 5.6 | Zarkeshian backpropagation learning works even at 1-5% photon transmission probability | MNIST accuracy 90-95% at p_photon = 0.01-0.05 | Brian2 spiking network with stochastic photonic feedback | Network learning fails (accuracy < 60%) when p_photon > 0.10 | 07 |

---

## 6. Waveguide Simulator (models/waveguide.py)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Track |
|---|-----------|---------------|----------------|------------------------|-------|
| 6.1 | ARROW anti-resonance wavelength (m=1): ~573 nm for d_myelin ~ 1.5 um | lambda_AR(m=1) = 2d * sqrt(n_myelin^2 - n_axon^2) / (2*1 - 1) ~ 573 nm | Transfer matrix computation (models/waveguide.py `arrow_wavelengths()`) | Measured peak guided wavelength differs from ARROW prediction by > 100 nm | Sim |
| 6.2 | Sefati/Zeng peak: lambda_peak = 300 + 52.3*n_wraps - 94.5*d_axon(um) | For typical CNS (n_wraps=80, d_axon=1.0 um): lambda_peak ~ 4390 nm (mid-IR) or for thinner sheaths ~400-500 nm (visible) | `sefati_zeng_peak()` function vs published data | Peak wavelength deviates from linear model by > 100 nm across measured wrap counts | Sim |
| 6.3 | Node-of-Ranvier coupling loss: 1-3 dB per node (wavelength-dependent) | T_node ~ 0.5-0.9; at anti-resonance T_node ~ 0.90 | `propagate_multi_node()` with node_coupling_loss_db=1.0 | Measured T_node < 0.3 at anti-resonance wavelengths (would rule out multi-node propagation) | Sim |
| 6.4 | Attenuation: absorption dominates at visible wavelengths, scattering at UV | alpha_abs ~ 1/lambda; alpha_scat ~ 1/lambda^4; crossover near UV-visible boundary | `attenuation_db_per_cm()` function | Scattering dominates over absorption at lambda > 600 nm in myelin | Sim |
| 6.5 | 20-node chain transmission at anti-resonance is non-negligible | T_total = T_segment^20 * coupling^19; at anti-resonance with 1 dB/node: T ~ 0.01-0.1 | Full `propagate_multi_node()` for realistic CNS axon | T_total < 10^-6 at all wavelengths for 20-node chain (would kill photonic communication hypothesis) | Sim |

---

## 7. MMI-Coherence Bridge (Track 08)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Track |
|---|-----------|---------------|----------------|------------------------|-------|
| 7.1 | Biophoton emission correlates with MMI Responsivity (success rate) | r ~ 0.20 expected correlation between biophoton modulation and trial success rate | Simultaneous biophoton detection (PMT) near human operator during QFT/MMI session | r < 0.05 with N > 500 trials (no detectable correlation) | 08 |
| 7.2 | Demyelination reduces MMI performance | Predicted: Reduced Lambda_ss -> reduced Responsivity in MS patients vs controls | QFT device Responsivity comparison: MS patients (n >= 30) vs matched controls | No difference in Responsivity between demyelinating patients and controls (p > 0.10) | 08 |
| 7.3 | Coherence steady state: Lambda_ss = (g_PhiPsi / kappa) * |Psi|^2 * Phi | Lambda_ss decreases with increasing kappa (disease) and decreasing |Psi|^2 (metabolic failure) | Fit dLambda/dt = g|Psi|^2*Phi - kappa*Lambda to QFT session time series | Model fits worse than random walk (no coherence dynamics detectable in session data) | 08 |
| 7.4 | EEG-biophoton-MMI triple correlation is positive | corr[C_gamma(t), PLV(t), SR(t)] >> 0 during active MMI sessions | Simultaneous EEG + biophoton detection + QFT trial outcomes | Triple correlation <= 0 or not significant (p > 0.05) with adequate sample | 08 |
| 7.5 | CCF circuit geometry mimicking myelin waveguide improves Responsivity | Myelin-inspired 3D CCF arrays (g-ratio 0.6-0.7) should outperform flat designs | A/B testing of CCF circuit designs in controlled MMI sessions | Waveguide-inspired CCF shows no improvement over random geometry | 08 |
| 7.6 | Environmental kappa_env reduction (EM shielding) increases QFT Responsivity | Lambda_QFT,ss = (g_eff / kappa_env) * E_CCF * Phi_ambient; lower kappa -> higher Lambda | Shielded vs unshielded QFT device operation (same AI, same protocol) | No Responsivity difference between shielded and unshielded conditions | 08 |
| 7.7 | Bayesian Updating framework transfers directly from MMI to biophoton classification | BU posterior tracks coherence state; combined 17-method analysis applicable to biophoton observables | Apply QTrainerAI BU framework to photocount time series | BU framework fails to classify coherent vs thermal biophoton sources better than simple Fano factor test | 08 |
| 7.8 | Remyelination restores MMI capability | Successful remyelination therapy -> restored g_PhiPsi -> restored Responsivity | Longitudinal QFT testing before/after remyelination therapy in MS patients | No Responsivity recovery after confirmed histological/MRI remyelination | 08 |

---

## 8. Nanoantenna Relay Model + Spectral Filter (2026-02-19)

| # | Prediction | Expected Value | Required Setup | Falsification Criterion | Source |
|---|-----------|---------------|----------------|------------------------|--------|
| 8.1 | Relay steady state: photon flux reaches E/(1-T) after ~5-8 nodes, then plateaus | Flux stabilizes at 5-8 nodes; pure-loss predicts exponential decay with no floor | PMT scanned along stimulated nerve (frog/rat sciatic), measuring flux at each node position | Flux continues exponential decay with no plateau through 15+ nodes | Relay model |
| 8.2 | External emission centroid blueshifts from ~794nm (healthy, g=0.70) to ~555-581nm range (severe demyelination, g=0.92-0.97) | ~200-240nm total blueshift; direction matches Dai's AD data (648→582nm). ⚠️ Exact centroid has ARROW resonance sensitivity — plateaus at ~556nm (g=0.92-0.95), jumps to ~581nm (g=0.96-0.97). Needs AD g-ratio data to pin down. | Spectrally-resolved EMCCD + filter wheel on healthy vs demyelinated nerve | Centroid shift < 50nm between healthy and severely demyelinated tissue, or shift is in wrong direction | Spectral filter |
| 8.2a | WT baseline centroid matches standard mouse myelin (g=0.78) | Predicted ~648nm; Dai measured 648.43 ± 0.90nm (nearly exact) | Transfer matrix at standard mouse parameters | Predicted WT centroid differs from measured by >20nm | Spectral filter |
| 8.2b | Two-mechanism model: total AD blueshift = metabolic + waveguide components | Brain slice shift > synaptosome shift (difference = waveguide component); ifenprodil-resistant shift (~31nm) correlates with myelin integrity | Compare Dai's synaptosome vs brain slice magnitudes; correlate ifenprodil-resistant component with histological myelin scores | Synaptosome shift equals brain slice shift (no waveguide component) OR ifenprodil fully restores spectrum (no structural component) | Two-mechanism model |
| 8.3 | Dual signature: external emission UP + internal relay signal DOWN simultaneously during cuprizone demyelination | Week 6: 22.8× external, relay at 58.6% of healthy | Two detector positions: perpendicular (external) + axial fiber (internal) on cuprizone mouse corpus callosum | External and internal signals move in same direction (both up or both down) | cuprizone_relay.py |
| 8.4 | Guided (internal) signal spectral centroid remains ~703nm regardless of myelin state | ~703nm ± 20nm at all g-ratios from 0.65-0.95 | Axial fiber optic measuring guided photons at distal end of nerve | Internal centroid shifts >50nm with demyelination | Spectral filter |
| 8.5 | Nanoantenna emission is separable from ROS by directionality: axial measurement enriched in IR relative to perpendicular measurement | IR/visible ratio higher at axial vs perpendicular detection positions | Two EMCCD positions on same stimulated nerve: axial (along axis) vs perpendicular | No directional difference in spectral composition between axial and perpendicular | Zangari 2018 + our model |
| 8.6 | First detectable cuprizone dual-signature at week 2 (p<0.05, d=1.18) | Effect size d>1.0 at week 2 with n=10 mice/group | PMT weekly measurements on 10 cuprizone + 10 control mice | No significant difference at week 2 with n=10/group (d<0.3) | cuprizone_relay.py |
| 8.7 | Species spectral redshift correlates with myelination index, not just brain mass | Human peak 865nm > monkey > pig > chicken > mouse > bullfrog; chicken may exceed mouse (higher myelination despite smaller brain) | Wang PNAS 2016 data + g-ratio measurements across species | Spectral peak correlates with brain mass but not g-ratio/myelination | Spectral filter + Wang 2016 |
| 8.8 | All current biophoton detectors miss the human brain peak (865nm > detector range ~850nm) | >50% of human brain biophoton emission is in undetected IR range | Compare EMCCD (visible cutoff) vs InGaAs detector (IR-sensitive) on same human brain tissue | EMCCD captures >90% of total emission (no significant IR component above 850nm) | Wang 2016 + detector specs |

---

## Cross-Track Consistency Checks

The following internal consistency checks verify that predictions from different tracks agree where they overlap.

### Confirmed Consistencies

| # | Tracks | Check | Status |
|---|--------|-------|--------|
| C1 | 01, 04 | Both predict broadband UPE is indistinguishable from Poissonian (M ~ 10^13 modes, Q ~ 10^-12) | CONSISTENT |
| C2 | 04, 06 | Both predict entanglement loss below d ~ 0.45 um myelin thickness | CONSISTENT |
| C3 | 05, 06 | Track 05 says myelinated vs demyelinated tissue distinguishable in ~8 min; Track 06 predicts 10-93x emission change, which is well above Track 05's detection threshold | CONSISTENT |
| C4 | 04, 07 | Both give cooperativity C ~ 10^-3 and weak coupling regime | CONSISTENT |
| C5 | 01, 05 | Both identify dark counts as the dominant noise source for PMT measurements and agree on F_measured formula: F_m = eta(F_true - 1) + 1 | CONSISTENT |
| C6 | 06, Sim | Track 06 uses 52.3 nm/layer blueshift; waveguide.py `sefati_zeng_peak()` uses same constant (C.SPECTRAL_SHIFT_PER_LAYER_NM) | CONSISTENT |
| C7 | 05, 07 | Track 05 says g^(2) coherence test is infeasible (T > 10^16 years); Track 07 confirms via information capacity analysis that the biophoton channel is 2-5 orders of magnitude below chemical synapses in bandwidth | CONSISTENT (both indicate severe signal limitations) |

### Identified Tensions

| # | Tracks | Tension | Severity | Resolution Path |
|---|--------|---------|----------|----------------|
| T1 | 04 vs 07 | Track 04 computes biphoton entanglement S ~ 0.017 bits at d=1 um with dephasing; Liu-Chen-Ao original paper predicts S ~ 1-2 bits without dephasing. Which regime is physical? | MODERATE | Measure T2* in intact myelin lipid; if T2* > 10 ps, entanglement may be higher |
| T2 | 07 vs 08 | Track 07 estimates photon channel capacity at 0.01-1 bits/s; Track 08 assumes Phi field carries functionally meaningful information. If capacity is at the lower end, the MMI bridge may be implausible. | MODERATE | Determine whether modulatory (not information-rich) signaling suffices for M-Phi predictions |
| T3 | 06 vs Sim | Track 06 predicts 10-100x emission burst during active demyelination (oxidative pathway). The waveguide model in waveguide.py addresses only guided-mode transmission, not the oxidative emission mechanism. The two emission sources (guided biophotons vs. ROS-generated chemiluminescence) need to be distinguished experimentally. | MODERATE | Use antioxidant controls (NAC) to separate waveguide vs. oxidative contributions |
| T4 | 07 (Scale 1 vs Scale 2) | Photon generation rate (1-100 ph/s/neuron) x coupling efficiency (10^-4 to 10^-2) gives a delivered rate of 10^-4 to 1 guided photon/s/neuron. At the pessimistic end (10^-4 ph/s), functional signaling is implausible even with perfect downstream detection. | **SEVERE** | This is the single most critical parameter uncertainty in the entire program. Direct measurement of coupling efficiency into myelin guided modes is the highest-priority experiment. |
| T5 | 01 vs 04 | Track 01 establishes that photocount statistics cannot distinguish coherent from broadband thermal. Track 04 proposes g^(2)(0) >> 2 as a biphoton signature. These are not contradictory (one is about single-mode coherence, the other about correlated pairs), but experimentally they require very different setups and the biphoton rate may be too low for detection (Track 05 confirms). | LOW | Design experiments targeting spectral coincidence (anti-correlated frequencies) rather than g^(2)(0) directly |

---

## Most Accessible Experiments

Ranked by feasibility (equipment availability, integration time, sample preparation difficulty).

### Tier 1: Immediately Feasible (standard lab equipment)

| Rank | Experiment | Key Prediction Tested | Equipment | Integration Time | Estimated Cost |
|------|-----------|----------------------|-----------|------------------|---------------|
| 1 | Total UPE from EAE optic nerve (ex vivo) | 4.1: 10-100x emission burst during active demyelination | Cooled PMT + dark box + perfusion chamber | 30-60 min per sample | $5-15k (if PMT available) |
| 2 | Cuprizone longitudinal emission profile | 4.4, 4.5: Temporal emission profile + remyelination spectral recovery | PMT + cranial window in mouse | Weekly 30-min sessions x 12 weeks | $10-20k (animals + surgery) |
| 3 | Myelinated vs demyelinated tissue discrimination | 3.6: < 10 min to distinguish | PMT with paired tissue samples | 8-30 min per comparison | $5k (consumables only) |
| 4 | Bandpass-filtered spectral profiling (6 bands) | 4.2, 4.3: Blueshift and singlet O2 peaks | PMT + filter wheel (350, 450, 550, 634, 703, 800 nm) | 2-6 hours per sample (6 x 30 min) | $2-5k (filter set) |
| 5 | NAC antioxidant control to separate emission mechanisms | 4.1 control: Two independent emission mechanisms (waveguide vs oxidative) | Same as Rank 1 + NAC pre-treatment group | Additional 30-60 min per treated sample | $1-2k (NAC + extra animals) |

### Tier 2: Requires Specialized Equipment

| Rank | Experiment | Key Prediction Tested | Equipment | Integration Time | Estimated Cost |
|------|-----------|----------------------|-----------|------------------|---------------|
| 6 | EM-CCD spatial mapping of emission along nerve | 4.2: Bright spots at demyelination boundaries | Back-illuminated EM-CCD (Andor iXon Ultra), microscope | 30-min frames x 100+ stacked | $50-100k (camera) |
| 7 | High-resolution UPE spectrum (10 nm bins) via dispersive EM-CCD | 6.1: ARROW peak at ~573 nm | EM-CCD + transmission grating | 2-10 hours | $60-120k (camera + optics) |
| 8 | Activity-photon temporal correlation | 5.5: Peak at 1-10 ms lag | PMT + electrophysiology rig + stimulating electrode | 2-6 hours | $20-40k (combined rigs) |
| 9 | Simultaneous LFP + biophoton during neural stimulation | 5.5 + 7.4: Activity correlation + EEG-photon link | SPAD pair + electrophysiology + neural slice | 24+ hours | $30-60k |
| 10 | Lysolecithin focal lesion spatial emission mapping | 06 Tier 2: Bright spots at boundaries | EM-CCD + glass micropipette injection | Days 3, 7, 14, 21 post-injection | $60-120k |

### Tier 3: Requires Quantum Optics Infrastructure

| Rank | Experiment | Key Prediction Tested | Equipment | Integration Time | Estimated Cost |
|------|-----------|----------------------|-----------|------------------|---------------|
| 11 | SNSPD-based definitive UPE detection | 3.4: 4.3x SNR improvement over PMT | 4-channel SNSPD system (cryogenic) | 1-4 hours | $200-500k (SNSPD system) |
| 12 | HBT correlation measurement (afterpulse-corrected) | 2.7: g^(2)(0) from myelin sample | SPAD pair in HBT configuration with OD>6 optical isolation | 24+ hours (limited by afterpulse correction at tau < 500 ns) | $30-60k |
| 13 | Spectral coincidence detection for biphoton pairs | 2.5, 2.7: Anti-correlated frequencies omega_1 + omega_2 = omega_20 | Two mid-IR SNSPDs with narrow spectral filters at 3.54 and 3.70 um | Hours to days (rate-limited) | $300-600k |
| 14 | Bell-CHSH test for frequency-entangled biphotons | 2.6: S > 2 requires eta > 0.89 | Mid-IR SNSPD array + Franson interferometer | Weeks (if biphoton rate is detectable at all) | $500k-1M |
| 15 | Quantum state tomography of biphoton state | Full density matrix reconstruction | Mid-IR spectrometers + phase modulators + SNSPDs | Months | $1M+ |

### Tier 4: Speculative / Long-term

| Rank | Experiment | Key Prediction Tested | Equipment | Integration Time | Estimated Cost |
|------|-----------|----------------------|-----------|------------------|---------------|
| 16 | Biophoton-Responsivity correlation during MMI session | 7.1: r ~ 0.20 correlation | PMT near human operator + QFT device + synchronized data acquisition | 500+ trials (hours of session time) | $50-100k |
| 17 | MS patient MMI Responsivity comparison | 7.2: Demyelination reduces MMI | QFT device + MS patient cohort (n >= 30) + matched controls | Months (clinical recruitment) | $100-200k |
| 18 | EEG-biophoton-MMI triple correlation | 7.4: Triple correlation >> 0 | EEG + biophoton detector + QFT device + human subjects | 100+ sessions | $150-300k |
| 19 | Transcranial biophoton detection through skull | 06 Tier 4: MS lesion load detectable | NIR detector (1270 nm) with fiber-optic probe or surgical burr hole access | Hours per measurement | $100-300k |
| 20 | Wearable biophoton monitor for MS disease activity | 06 Tier 4: Continuous monitoring, relapse prediction | Custom wearable single-photon detector | Continuous over weeks-months | $500k+ (development) |

---

## Summary Statistics

- **Total predictions**: 42 (across 7 sections)
- **Immediately testable (Tier 1)**: 5 experiments covering predictions 3.6, 4.1-4.5
- **Cross-track consistencies confirmed**: 7
- **Cross-track tensions identified**: 5 (1 severe: delivered photon rate uncertainty)
- **Single most important negative result**: Direct g^(2) coherence measurement of broadband multi-mode UPE is fundamentally impossible (Track 05, prediction 3.3)
- **Single most critical parameter uncertainty**: Coupling efficiency eta_couple into myelin guided modes (Tension T4)
- **Most impactful near-term experiment**: Total UPE from EAE optic nerve (Tier 1, Rank 1) -- would establish whether demyelination produces any detectable biophoton signature change at all

---

*Generated from computational results in Tracks 01, 04, 05, 06, 07, 08, and models/waveguide.py. All numerical values are from the track documents and simulation code; see individual tracks for derivations, assumptions, and parameter sensitivity analyses.*
