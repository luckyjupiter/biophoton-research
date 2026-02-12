# Biophoton Research Findings Log

Breakthroughs and notable results from simulation and analysis work. Each entry feeds into the content pipeline (see `docs/content-pipeline.md`).

---

## 2026-02-11 [SIMULATOR] Demyelination Simulator Package Complete

**What:** Built complete 10-file Python simulation package (`models/`) modeling biophoton emission from healthy vs. demyelinated tissue.
**Numbers:**
- Healthy CNS axon: peak emission at 456 nm, ~4470 photons/cm²/s
- 50% demyelination: 9.3× emission enhancement
- Cuprizone experiment: first 3σ detection at week 1 (PMT, 10 mice, 5-min, 1mm²)
- ROC AUC: 1.000 (total_intensity), 0.999 (coherence), 0.995 (polarization)
**Why it matters:** First runnable end-to-end simulation predicting what experiments would actually measure. Confirms detection is feasible with standard equipment.
**Files:** `models/` (10 files), `cuprizone_experiment.png`, `spectrum.png`, `roc_curve.png`
**Podcast potential:** HIGH — Episode 4 anchor. "We built a simulator and the first thing it told us is: you could detect demyelination in week 1."

---

## 2026-02-11 [TRACK-01] Photocount Statistics Cannot Distinguish Coherence

**What:** Track 01 proved that photocount statistics alone are fundamentally insufficient to verify biophoton coherence claims.
**Numbers:** M~10^13 thermal modes, Fano departure ~10^-12, undetectable at any feasible sample size. Only g^(2)(τ) works.
**Why it matters:** Kills the easy path — forces the field toward correlation measurements. Honest negative result that saves years of wasted effort.
**Files:** `worktrees/track-01/figures/` (10 figs), `worktrees/track-01/results/` (8 npz)
**Podcast potential:** HIGH — Episode 2 anchor. "We proved the most popular measurement approach can't work."

---

## 2026-02-11 [TRACK-04] Myelin Cavity Is Weak Coupling, But Measurable

**What:** Cavity QED analysis shows myelin Q~5, cooperativity C~10^-3. Weak coupling. But entanglement S~0.06 bits is nonzero, and Bell violation achievable with SNSPD (η>0.89).
**Numbers:** g^(2)(0)=101 for biphoton state, coherence length ~4 μm, Bell S=2.06 at η=0.90.
**Why it matters:** Sets honest bounds on the quantum claims. Not magic, but not nothing either.
**Files:** `worktrees/track-04/figures/` (8 figs), `worktrees/track-04/results/` (2 txt)
**Podcast potential:** HIGH — Episode 3 anchor. "How quantum is the light in your nerves? We calculated the answer."

---

## 2026-02-11 [TRACK-07] Deep Analysis: Quantitative Bottleneck and Sensitivity Hierarchy

**What:** Comprehensive 6-analysis deep dive into the unified multi-scale model. Quantified the full molecular-to-network photon pipeline, identified the dominant parameters, mapped the synchronization phase diagram, and showed demyelination coherence degradation.
**Numbers:**
- Bottleneck factor (10 internodes): 8.4x10^4 — waveguide loss dominates by 4-5 orders of magnitude
- Loss budget: node coupling loss dominates over absorption for >2 internodes; 20 internodes yields T=4.3x10^-11
- Sensitivity ranking: n_internodes (52,840%) >> node_transmission (3,844%) >> kappa (133%) > j_leak (105%) > g_PhiPsi (100%) > alpha_myelin (51%) >> coupling_K (2%)
- Synchronization critical K: scales with N (K_c=0.22 for N=10, K_c=3.9 for N=50, K_c=4.9 for N=100)
- Demyelination: mild lesion (kappa=0.3) causes 32% coherence reduction; severe (kappa=1.0) causes 81% — consistent with Track 06 biomarker predictions
- End-to-end: M-function = 14.77 (50 axons, K=0.01, 10 internodes)
**Key insight:** The two parameters that overwhelmingly matter are structural (number of internodes, node transmission). All molecular and network parameters are secondary. This means the experimental priority is measuring node-of-Ranvier optical transmission, not refining ROS kinetics.
**Cross-track consistency:** The 81% coherence reduction under severe demyelination aligns with Track 06's predicted >50x emission enhancement and Track 08's critical damage threshold of ~30%.
**Files:** `worktrees/track-07/figures/` (8 figs total), `worktrees/track-07/results/` (8 files: 5 JSON, 1 NPZ, 1 TXT)
**Podcast potential:** HIGH — Episode 6 anchor upgraded. "We swept every parameter in the model and found that just two things matter: how many nodes of Ranvier the light crosses, and how much each node leaks."

---

## 2026-02-11 [TRACK-08] MMI Bridge Figures Generated

**What:** First visualization of the biophoton-MMI connection: 8 figures showing coherence dynamics, responsivity mapping, demyelination impact on MMI, cross-correlations, Bayesian updating, and triple EEG-Bio-MMI correlation.
**Numbers:** Predicted bio-MMI Pearson r=0.20, critical damage ~30%, triple correlation all positive.
**Why it matters:** Makes the theoretical bridge visual and concrete. The triple correlation figure is the money shot for the M-Φ hypothesis.
**Files:** `worktrees/track-08/figures/` (8 figs), `worktrees/track-08/results/` (2 md)
**Podcast potential:** HIGH — Episode 5 anchor. "What if the same field that carries light in your nerves is what MMI devices interact with?"

---

## 2026-02-11 [TRACK-06] Biomarker Predictions Quantified

**What:** Full biomarker analysis across 5 disease stages. Spectral shift and emission intensity achieve AUC=1.000. Combined score AUC>0.8 at all stages.
**Numbers:** EAE onset: 51× fold increase. Cuprizone week 3: 37× fold. Singlet O₂ discriminates autoimmune vs toxic. Sample size N=5/group for moderate effect.
**Why it matters:** These are specific, falsifiable, experimentally testable predictions. Ready for the bench.
**Files:** `worktrees/track-06/results/testable_predictions.txt`, `experimental_protocol.txt`
**Podcast potential:** HIGH — reinforces Episode 1 narrative with hard numbers.
