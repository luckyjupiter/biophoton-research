# Biophoton Research - Active Work Plan

**Generated**: 2026-02-20 12:06 PM  
**Status**: Post-collaboration outreach, repo cleanup phase

---

## 🔴 CRITICAL GAPS (Block Publication)

### 1. Two-Mechanism Model Calibration ⚠️
**Problem**: Peak demyelination prediction off by 156.7nm (target 581nm, predicted 737.7nm)

**Root cause** (from SIMULATIONS_TODO.md):
- Current quadratic fit assumes same optical properties for all myelin states
- Missing: disordered remyelinated myelin model
- Missing: proper metabolic vs waveguide component separation

**Evidence**: Dai's synaptosome data shows blueshift WITHOUT myelin (metabolic component exists)

**Action items**:
- [ ] Implement `effective_n_myelin(g_ratio, is_remyelinated, disorder_factor)`
- [ ] Separate metabolic shift (~35nm, drug-reversible) from waveguide shift (~31nm, structural)
- [ ] Test against ifenprodil data (NMDA antagonist partial reversal)
- [ ] Re-run cuprizone predictions with two-mechanism model

**Files to modify**:
- `models/two_mechanism.py` - already exists but needs better calibration
- `models/cuprizone_v2.py` - add disorder parameter for remyelination

---

### 2. Missing Paper Draft in Repo
**Problem**: Current paper (`docs/paper2-waveguide-demyelination.md`) is marked SUPERSEDED

**New draft location**: `/home/yesh/.openclaw/workspace/biophoton_relay_paper_draft.md`

**Action**:
- [ ] Review workspace draft for quality
- [ ] Copy to repo as `docs/relay-model-paper.md`
- [ ] Update with validated baseline (g=0.78 → 648nm match)
- [ ] Remove outdated quantitative claims (keep qualitative predictions)

---

## 🟡 HIGH PRIORITY (Strengthen Collaboration Pitch)

### 3. Waveguide Mode Solver (Physics-Based)
**Current**: Empirical quadratic fit to reference points  
**Needed**: Actual eigenmode solver using Bessel functions

**Why it matters**: Collaborators will ask "where do these wavelength predictions come from?"

**Action**:
- [ ] Create `models/waveguide_modes.py` with proper V-number calculation
- [ ] Implement ARROW resonance condition: λ_AR(m) = (2d / (2m - 1)) * √(n_clad² - n_core²)
- [ ] Replace empirical fits with physics-based mode calculations
- [ ] Validate against Kumar 2016 FDTD results

**Tools**:
- Python `scipy.special.jv` for Bessel functions
- Or interface with Lumerical MODE (if available)

---

### 4. Experimental Validation Data
**Current**: Using secondary sources, missing raw data

**Papers to get full text + extract data**:
- [ ] Sachs et al. 2014 (ASN Neuro) - MOG quantification timeline
- [ ] Tang et al. 2016 (PNAS) - actual spectrum data (not just peak wavelength)
- [ ] Liu et al. 2019 (Adv Funct Mater) - refractive index measurements
- [ ] Zeng et al. 2022 (Applied Optics) - EM model details

**Action**:
- [ ] Download papers from Sci-Hub or institutional access
- [ ] Extract numerical data to `models/constants.py`
- [ ] Add literature_data.json with sources

---

### 5. Detection Sensitivity Curves
**Problem**: Models assume flat detector response across wavelengths

**Reality**:
- Si PMT: Efficient 300-800nm, drops rapidly >850nm
- InGaAs: 900-1700nm
- Human brain peak at 865nm is at edge of Si detector range

**Action**:
- [ ] Add `detector_efficiency_curve(wavelength, detector_type)` to `models/detection.py`
- [ ] Update cuprizone simulations with realistic spectral response
- [ ] Document detector gap: "50% of human signal missed by standard detectors"

---

## 🟢 MEDIUM PRIORITY (Polish & Documentation)

### 6. Chronic Cuprizone Timeline
**Current**: Only acute 6-week model  
**Needed**: 13-week chronic impaired recovery scenario

**Why**: Shows model generalizability, important for MS (chronic disease)

**Action**:
- [ ] Add `cuprizone_gratio(week, protocol='acute'|'chronic')` parameter
- [ ] Chronic: more severe peak, slower recovery, lower final plateau
- [ ] Predicted: ~720-740nm stable remyelinated (vs ~768nm acute)

---

### 7. Spatial Distribution Model
**Current**: Three discrete regions (splenium, DHC, genu)  
**Needed**: Continuous rostro-caudal gradient

**Why**: More realistic, shows we understand the biology

**Action**:
- [ ] `spatial_gratio_distribution(week, position_rostral_to_caudal)`
- [ ] Position: 0 (rostral/genu) → 1 (caudal/splenium)
- [ ] Severity gradient for cuprizone week 6 visualization

---

### 8. Liu et al. 2024 Cavity QED Integration
**Paper**: "Entangled biphoton generation in myelin sheath" (Phys Rev E)

**Their claim**: C-H bond vibrations generate entangled photon pairs

**Our stance**: Entanglement is weak (C~10⁻³, S~0.02 bits with dephasing)

**Action**:
- [ ] Read Liu full text
- [ ] Check if their emission rate formulas improve ROS model
- [ ] Add to bibliography with caveat about weak coupling
- [ ] DON'T overstate quantum effects in presentations

---

## 🔵 LOW PRIORITY (Nice to Have)

### 9. Visualization Improvements
**Current**: Individual scripts generate figures ad-hoc

**Action**:
- [ ] Create `tools/generate_all_figures.py` master script
- [ ] Add publication-quality formatting (300 DPI, vector graphics where possible)
- [ ] Generate figure panel for paper submission

---

### 10. Nanoantenna vs ROS Balance
**Current**: Model shows nanoantenna dominates ROS by 177×

**Reality**: Both sources important, different spatial patterns

**Action**:
- [ ] Separate external leakage (ROS-dominated) from internal relay (nanoantenna)
- [ ] Already partially in `node_emission.py`, needs refinement
- [ ] Low priority: doesn't affect cuprizone experiment design

---

## 📋 COMPLETED (Reference)

✅ **Baseline validation**: g=0.78 → 648nm matches Dai exactly  
✅ **Research gap confirmation**: Zero demyelination-biophoton studies  
✅ **Relay model math**: E/(1-T) geometric series  
✅ **Repository cleanup**: Removed misleading "100nm off" warning  
✅ **Status report rewrite**: Emphasizes validated components  
✅ **Collaboration outreach**: Emails to Dai (Wuhan) & Chen (Shanghai)  
✅ **Visual-first README**: Hero figure, predictions table, funding badge  

---

## 🎯 THIS WEEK'S FOCUS

**If Dai/Chen respond positively:**
1. Fix two-mechanism calibration (Critical #1)
2. Add waveguide mode solver (High Priority #3)
3. Get validation data from papers (High Priority #4)

**If no response yet:**
1. Work on two-mechanism model anyway (strengthens research)
2. Write proper relay model paper
3. Add detector sensitivity curves

**Time estimate**:
- Two-mechanism fix: 4-6 hours
- Waveguide mode solver: 6-8 hours
- Paper draft: 8-10 hours
- Total: ~20 hours for critical items

---

## 🚫 DO NOT DO (Waste of Time)

❌ **Don't** build elaborate ML models for g-ratio prediction  
❌ **Don't** try to fit 10+ parameters to sparse data  
❌ **Don't** chase perfect quantitative match before experiment  
❌ **Don't** add quantum entanglement claims without new evidence  
❌ **Don't** rewrite working code just for style  

**Why**: Experiment will provide real data. Model refinement is infinite. Ship the proposal first.

---

## 📊 Success Metrics

**Short-term** (next 2 weeks):
- [ ] Two-mechanism model predicts peak demyelination within 50nm of target
- [ ] Waveguide mode solver replaces empirical fits
- [ ] Paper draft ready for submission-quality polish

**Medium-term** (if collaboration proceeds):
- [ ] Dai/Chen collaboration established
- [ ] Cuprizone experiment designed with their input
- [ ] Funding commitment confirmed

**Long-term** (8-12 months):
- [ ] Experimental data validates or falsifies model
- [ ] Publication in Scientific Reports / Brain / PLOS ONE
- [ ] Novel MS biomarker established OR hypothesis falsified (both valuable)

---

**Last Updated**: 2026-02-20 12:06 PM  
**Next Review**: After Dai/Chen response or in 1 week (whichever comes first)
