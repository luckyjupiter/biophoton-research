# Biophoton Research: Honest Status Report
**February 19, 2026**

---

## What We Built

Over the past ~10 days, we built a research program with:
- **10-file simulation package** (`models/`) — waveguide propagation, emission spectra, node coupling, detection feasibility, cuprizone timeline
- **8 research tracks** — photocount statistics, time series, waveguide, quantum optics, SNR, demyelination, unified model, MMI bridge
- **42 falsifiable predictions** with experimental designs and cost estimates
- **Relay model** — node-to-node photon relay with E/(1-T) steady state
- **Spectral filter hypothesis** — myelin waveguide shapes emission spectrum
- **Deep literature review** — Zangari group, Dai lab, Frede/Simon, DARPA GO, Kumar/Bhatt
- **Experimental proposal** — cuprizone demyelination biophoton measurement

---

## What's Solid (Doesn't Need Fixing)

### 1. Relay Model Math
The E/(1-T) steady state is a geometric series. If nodes emit and re-emit, this is the result. Period.
- **Testable**: Measure photon flux along a stimulated nerve at each node. Relay predicts plateau. Pure-loss predicts exponential decay.
- **Novel**: Nobody has modeled it this way. Frede/Simon called nodes "relay amplifiers" qualitatively but didn't write the equation.
- **Files**: `models/node_emission.py`, `tools/viz_relay_suite.py`

### 2. The Gap
Nobody has measured biophotons during demyelination. Zero papers. Confirmed by deep literature search. This is a real, publishable observation.
- ROS → biophotons (proven by many groups)
- Demyelination → ROS (proven by many groups)  
- Demyelination → biophotons (never measured)
- **File**: `biophoton_demyelination_deep_research.md`

### 3. Dual Signature Prediction (Qualitative)
If myelin is a waveguide, damage should simultaneously:
- Increase external leakage (less containment)
- Decrease internal guided signal (worse waveguide)

This is qualitatively robust — it follows from any waveguide model, not just ours. Anti-correlated internal/external signals during demyelination would be strong evidence.

### 4. Detection Feasibility (Track 05)
Standard PMT can detect myelinated vs demyelinated tissue in <10 min. The photon rates from ROS during demyelination (10-100× baseline) are well within detector range. This is not an exotic measurement.

### 5. Photocount Statistics Kill (Track 01)
Broadband biophoton photocount statistics cannot distinguish coherent from thermal. This is a legit negative result — Q ≈ 10⁻¹² at M ≈ 10¹³ modes. Forces the field toward correlation measurements. Saves people time.

### 6. Cavity QED Bounds (Track 04)
Myelin is weak coupling (Q~5, C~10⁻³). Not magic, not nothing. Honest bounds on quantum claims.

### 7. Literature Landscape
- Zangari group: dormant since 2021, but 2018 paper is solid (experimental confirmation in 2021)
- Dai lab: best equipment, most data, hasn't connected to waveguide theory
- Frede/Simon: qualitative hypothesis exists, no quantitative model
- Nobody has connected Zangari's nanoantenna to Dai's spectral data — we tried, partially failed (see below)
- **Files**: `zangari_deep_research.md`, `biophoton_research_landscape.md`

---

## What's Broken (Needs Fixing or Discarding)

### 1. Spectral Centroid Predictions — OFF
- Model predicts WT centroid at **743nm**. Dai measured **648nm**. Off by 95nm.
- Model predicts AD shift of **-188nm**. Dai measured **-66nm**. 3× too large.
- Root cause: nanoantenna emission dominates ROS by **177×** at 500nm, pulling everything into IR.
- Transfer matrix transmission is nearly flat (T>0.997 across 400-800nm) — the "filtering" comes from tiny differences amplified by weighting.
- Previous "matches" (648/648 for WT, 581/582 for AD) were both **coding errors** (array indexing bug).

**Verdict**: The spectral filter MECHANISM is real (right direction), but our model can't make specific wavelength predictions yet. Don't cite any specific numbers.

### 2. Cuprizone Quantitative Predictions — UNCERTAIN
- The "22.8× external, 58.6% internal at week 6" numbers come from `cuprizone_relay.py` which uses the same broken emission model.
- The QUALITATIVE prediction (external up, internal down) is fine.
- The specific multipliers are unreliable.

### 3. Prediction 8.2a — WRONG
- "WT baseline centroid matches standard mouse myelin (g=0.78), predicted ~648nm" — this was the indexing bug. Actual prediction is 743nm.
- Needs to be corrected or removed from master predictions.

### 4. Two-Mechanism Model — SPECULATIVE
- The idea (metabolic + waveguide components) is reasonable but we can't quantify either component reliably.
- Dai's synaptosome data complicates any pure waveguide interpretation.
- We don't know if the spectral data is from synaptosomes or brain slices (paper is ambiguous).

### 5. Some Track Numbers — UNCHECKED
- Tracks 01-08 were generated in a single session. The math looks right but I haven't systematically audited every number like I did the spectral predictions.
- The Track 07 sensitivity hierarchy is particularly important (n_internodes >> everything else) and should be verified.
- Track 08 MMI predictions are highly speculative by nature.

---

## What's Interesting But Unproven

### 1. Species Redshift Correlation
Wang 2016 shows human biophotons peak at 865nm, with a species progression correlating with myelination. Our waveguide model predicts this direction. But we haven't quantitatively tested whether our model reproduces the species progression.

### 2. Aging Blueshift
Chen/Dai 2020 show blueshift with aging. Myelin thins with age. Direction matches. Quantitative match unknown.

### 3. Herald Signals
Photons propagate through myelin ~10⁴× faster than APs. In the relay model, photons from node N arrive at node N+1 microseconds before the AP. This is physically true (speed of light vs ionic conduction) but whether it's biologically functional is unknown.

### 4. Detector Gap at 865nm
If human brain peak really is 865nm and EMCCD cuts off at ~850nm, we're missing most of the signal. This is a real practical observation, independent of our model.

---

## What Should We Do With All This?

### Option A: Experimental Proposal Paper
**"Biophoton Emission During Demyelination: The Missing Measurement"**
- Lead with the gap (nobody's done it)
- Describe the cuprizone experiment (straightforward, ~$5K)
- Qualitative predictions only (intensity up, spectrum shifts, dual signature)
- No broken quantitative predictions
- Cite Zangari, Dai, Frede/Simon for context
- Target: Scientific Reports, PLOS ONE, or similar
- **Status**: Draft proposal exists (`demyelination_biophoton_proposal.md`), needs polish into paper format

### Option B: Relay Model Theory Paper  
**"Photonic Saltatory Conduction: A Node-to-Node Relay Model for Biophoton Propagation in Myelinated Axons"**
- The E/(1-T) math
- Qualitative predictions (steady state vs decay, dual signature)
- Parameter space analysis (what ranges of T give interesting behavior)
- Comparison with pure-loss models in literature
- Target: Physical Biology, J. Theoretical Biology
- **Status**: Math is done, visualizations done, needs writing

### Option C: Review/Perspective
**"Biophotons and Myelin: What We Know, What We Don't, and What to Measure Next"**
- Synthesize Zangari + Dai + Frede/Simon + Kumar/Bhatt
- Note that nobody has connected these threads quantitatively
- Highlight the demyelination gap
- Honest about model limitations
- Target: Frontiers in Neuroscience, Neuroscience & Biobehavioral Reviews
- **Status**: All the research is done, needs organizing

### Option D: Pause and Fix the Model
- Figure out why centroids are 100nm off
- Fix the antenna/ROS ratio
- See if a calibrated model can actually match Dai's data
- Then decide what to publish
- **Risk**: Could take weeks and might not work

### My Recommendation
**A + B in parallel.** The experimental proposal doesn't depend on the model at all — it's "here's a gap, here's how to fill it." The relay model paper is pure math with qualitative predictions. Neither requires fixing the spectral calibration. Option C is safe but less impactful. Option D is important long-term but shouldn't block the papers.

---

## Files Inventory

### Core Model Code
| File | What | Status |
|------|------|--------|
| `models/waveguide.py` | Transfer matrix, multi-node propagation | Working but calibration off |
| `models/emission.py` | ROS + waveguide-filtered emission spectra | Working but ratio wrong |
| `models/node_emission.py` | Nanoantenna relay model | Working, math is solid |
| `models/constants.py` | All physical parameters | Needs antenna/ROS ratio review |
| `models/cuprizone_relay.py` | Cuprizone timeline simulation | Qualitative OK, quantitative suspect |
| `models/detection.py` | SNR, integration time, ROC | Working |
| `models/axon.py` | Axon geometry (g-ratio, diameters) | Working |

### Visualization
| File | What | Status |
|------|------|--------|
| `tools/viz_relay_suite.py` | 5 relay model figures | Clean, sent to Telegram |
| `tools/viz.py` | General dashboard | Working |
| `tools/viz_relay.py` | Earlier relay visualizations | Working |

### Research Documents
| File | What | Status |
|------|------|--------|
| `demyelination_biophoton_proposal.md` | Experimental proposal | Clean, ready to polish |
| `zangari_deep_research.md` | Zangari group due diligence | Complete |
| `biophoton_demyelination_deep_research.md` | Literature gap confirmation | Complete |
| `biophoton_relay_paper_draft.md` | Paper draft | **STALE** — based on debunked claims, needs rewrite |
| `biophoton_research_landscape.md` | 8 active groups | Complete |
| `zangari_model_proposal.md` | Earlier proposal | Partially stale |
| `discord_relay_darpa_go_research.md` | Quantum discord + DARPA GO | Complete |
| `FINDINGS_LOG.md` | All findings | Updated with corrections |
| `docs/master-predictions.md` | 42 predictions | Predictions 8.2a needs correction |

### Track Results
| Track | Topic | Status |
|-------|-------|--------|
| 01 | Photocount statistics | Solid negative result |
| 02 | Time series fractal | Not audited |
| 03 | Waveguide propagation | Core model, calibration off |
| 04 | Quantum optics / cavity QED | Solid bounds |
| 05 | Signal-to-noise | Solid feasibility |
| 06 | Demyelination pathology | Qualitative predictions solid, quantitative suspect |
| 07 | Unified model | Important but not audited |
| 08 | MMI bridge | Highly speculative |

---

## Bottom Line

We have genuine contributions:
1. **The relay model** — novel, clean math, testable
2. **The demyelination gap** — real, important, nobody's done it
3. **The dual signature prediction** — qualitatively robust
4. **Track 01 negative result** — honest, useful

We overreached on:
1. **Specific wavelength predictions** — broken
2. **"Three datasets unified"** — the unification is qualitative, not quantitative
3. **Paper draft** — needs complete rewrite

The honest path: publish what's solid, fix what's broken separately, don't claim what we can't back up.
