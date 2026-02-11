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

## 2026-02-11 [TRACK-07] Waveguide Transport Is the Bottleneck

**What:** Multi-scale model shows delivered photon rate at axon terminals is 3.2×10^-11 photons/s — transmission through 10 internodes is 1.2×10^-5.
**Numbers:** Generation: 2.7×10^-6 photons/s/axon. Transmission: 1.2×10^-5. Network sync: r=0.12.
**Why it matters:** Identifies the critical bottleneck — waveguide loss dominates everything. Interventions should focus on reducing propagation loss.
**Files:** `worktrees/track-07/figures/coherence_1d_demo.png`, `sweep_coupling_K.png`
**Podcast potential:** MEDIUM — supports Episode 6 narrative on multi-scale challenges.

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
