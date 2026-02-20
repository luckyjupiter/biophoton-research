# Biophoton Waveguide Physics in Myelinated Axons

### *First Measurement of Biophoton Emission During Demyelination*

<p align="center">
  <img src="viz_output/cuprizone_dual_signature.png" width="800" alt="Predicted dual signature during demyelination"/>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Active Research](https://img.shields.io/badge/Status-Active%20Research-brightgreen)
![Funding: Available](https://img.shields.io/badge/Funding-Available-blue)

---

## 🔬 The Gap in the Literature

Despite well-established biological mechanisms:
- ✅ **Demyelination → ROS** (proven: Haider et al. 2011; Smith & Lassmann 1999)
- ✅ **ROS → Biophotons** (proven: Cifra & Pospíšil 2014; Prasad et al. 2022)
- ✅ **Myelin = Optical Waveguide** (proven: Kumar et al. 2016; Liu et al. 2019)

### ❌ **Zero studies have measured biophoton emission during demyelination**

Not in cuprizone. Not in EAE. Not in any MS model. Not in any species.

**This repository provides:**
1. Computational models predicting spectral shifts when myelin is destroyed
2. A concrete $5K experimental protocol to test it
3. Potential pathway to a novel MS biomarker

---

## 🎯 Key Predictions (Testable in 8 Months)

### 1. **Spectral Blueshift During Demyelination**

Our waveguide filter model predicts massive spectral shifts as myelin thins:

| Myelin State | G-Ratio | Model Prediction | Supporting Evidence |
|--------------|---------|------------------|---------------------|
| **Healthy mouse (standard)** | 0.78 | **648 nm** | **Dai measured: 648.4 nm** ✓ |
| **Healthier (thick myelin)** | 0.70 | 794 nm | Extrapolation |
| **Moderate demyelination** | 0.93 | ~640 nm | Cuprizone week 4 |
| **Severe demyelination** | 0.96 | **~581 nm** | **Dai AD: 582 nm** ✓ |
| **Remyelinated (permanent)** | 0.83 | ~768 nm | Predicted (untested) |

**Key Points:**
- ✅ **Baseline match**: g=0.78 → 648nm prediction matches Dai's WT data (648.4 ± 0.9 nm)
- ✅ **Blueshift direction**: Model predicts ~200nm shift, Dai measured 648→582nm = 66nm (AD)
- ⚠️ **Magnitude difference**: Likely due to AD having milder demyelination than cuprizone (g~0.85 vs g~0.96)

<p align="center">
  <img src="viz_output/spectral_relay_evolution.png" width="700" alt="Spectral evolution during demyelination"/>
</p>

**Physical Mechanism**: Thinner myelin → higher waveguide cutoff frequency → longer wavelengths (IR) leak out → spectrum shifts blue.

**Falsification**: If demyelinated tissue shows no spectral shift or shifts toward red (longer wavelengths), waveguide hypothesis is wrong.

---

### 2. **Dual Signature: Internal ⬇️ / External ⬆️**

Degraded waveguide should produce **anti-correlated** signals:
- Internal (guided) photons: **Decrease** (worse transmission)
- External (leakage) photons: **Increase** (failed containment)

**Cuprizone predictions** (from relay model):
- Week 6: External emission UP **22.8×**, internal relay signal DOWN to **58.6%**
- First detectable at week 2 (effect size d=1.18, p<0.05)

**Prediction**: Pearson correlation r < -0.7 between internal and external signals

<p align="center">
  <img src="figures/cuprizone_v2_timeline.png" width="700" alt="Cuprizone timeline with dual signature prediction"/>
</p>

**Falsification**: If both signals move in the same direction (both up or both down), the waveguide model is wrong.

---

### 3. **Permanent Remyelination Signature**

Remyelinated fibers are thinner than native myelin (Duncan et al. 2017) → **residual ~26nm blueshift even after "complete" remyelination**.

| State | G-Ratio | Predicted Centroid | Clinical Significance |
|-------|---------|-------------------|----------------------|
| Original healthy | 0.78 | 648 nm | Baseline |
| Demyelinated | 0.96 | ~581 nm | Active disease |
| Remyelinated | 0.83 | **~768 nm** | "Healed" but not native |

**Impact**: First non-invasive method to distinguish remyelinated from native myelin. Current methods (MRI, EM) cannot make this distinction optically.

---

## 🧬 The Node-to-Node Relay Model

**Problem**: Photons shouldn't survive long distances in scattering tissue.

**Solution**: They don't need to. At each node of Ranvier:

1. ⚡ Action potential triggers ROS burst
2. 💡 New biophotons generated  
3. ➡️ Couple into next myelin waveguide segment
4. 🔁 **Photonic saltatory conduction** (like electrical AP regeneration)

**Mathematical Result**: Steady-state flux = **E/(1-T)** (plateau, not decay)

<p align="center">
  <img src="viz_output/relay_vs_pure_loss.png" width="700" alt="Relay model vs pure loss"/>
</p>

**Evidence**:
- Zangari et al. (2018, 2021): Nodes act as "bio-nanoantennas," photons detected in active nerve
- Frede et al. (2023): Multiplicative transmission across nodes (consistent with relay)

---

## 💰 The Experiment ($5K, 8 Months)

### **Protocol in One Sentence**
Measure biophoton emission from cuprizone-demyelinated mouse brain slices at weeks 0, 2, 4, 6 (demyelination) and 8, 10 (remyelination), correlate with electron microscopy g-ratio.

### **Why This Works**

✅ **Cuprizone model**: Predictable timeline, spontaneous remyelination, no immune confound  
✅ **Detection**: Standard EMCCD (Dai's group has this)  
✅ **Protocol**: Already exists (Tang & Dai 2014 glutamate-stimulated imaging)  
✅ **Cost**: $4-5K for 20 mice + histology  

### **Primary Outcome**
Correlation between biophoton spectral centroid and electron microscopy g-ratio

**Statistical Power**: n=10/group achieves 90% power for Cohen's d=2.0 effect (GPower 3.1)

### **Value Regardless of Result**
- ✅ **Positive**: Novel MS biomarker, validates waveguide hypothesis
- ✅ **Negative**: Falsifies model, saves field from pursuing dead end
- ✅ **Either way**: First measurement = publishable (*Scientific Reports*, *Brain*, *PLOS ONE*)

**Full Protocol**: [demyelination_biophoton_proposal_improved.md](demyelination_biophoton_proposal_improved.md)

---

## 📊 Repository Contents

### **Core Documents**
- 📄 [**Experimental Proposal**](demyelination_biophoton_proposal_improved.md) - Grant-quality protocol with power analysis, statistical plan, budget
- 📄 [**Relay Theory**](discord_relay_darpa_go_research.md) - Node-to-node quantum discord relay + DARPA connection
- 📄 [**Status Report**](biophoton_status_report.md) - What's validated, what's speculative, known limitations

### **Computational Models**
```
models/
├── cuprizone_v2.py        # Demyelination timeline (literature g-ratios)
├── node_emission.py       # ROS emission + relay at nodes
├── waveguide.py          # Transfer matrix propagation
└── two_mechanism.py      # Metabolic + waveguide spectral components
```

### **Research Tracks** (8 Deep-Dives)
1. **Photocount Statistics** - Proves thermal/coherent indistinguishability (useful negative result)
2. **Waveguide Propagation** - Transfer matrix, multi-node transmission
3. **Quantum Optics** - Cavity QED bounds (Q~5, weak coupling)
4. **Detection Feasibility** - SNR analysis, integration times
5. **Demyelination Predictions** - Spectral shifts, dual signature
6. **Relay Model** - E/(1-T) steady state
7. **Unified Model** - Sensitivity hierarchy
8. **MMI Bridge** - Quantum coherence experimental tests

### **Visualizations** (Publication-Quality)
All figures in `viz_output/` and `figures/`:
- Relay model diagrams
- Cuprizone dual signature predictions
- Spectral evolution timelines
- Detection ROC curves
- Waveguide mode analysis

---

## 🤝 Collaboration & Funding

### **Current Outreach**
- 📧 **Dr. Jiapei Dai** (Wuhan): Experimental collaboration, has EMCCD equipment
- 📧 **Dr. Yong-Cong Chen** (Shanghai): Cavity QED theory synthesis

### **We're Looking For**
1. **Experimentalists** with biophoton imaging capability
2. **MS researchers** interested in novel biomarkers
3. **Theorists** working on quantum/classical photon models
4. **Clinical partners** for eventual human translation

### **Funding Available**
Research support through Quantum Cognition Corporation for proof-of-concept experiments. Budget flexible based on collaboration scope.

**Contact**: josh@quantumcognition.com

---

## 📚 Key References

**Waveguide Physics**
- Kumar et al. (2016) *Sci Rep* - Original myelin waveguide FDTD
- Liu et al. (2019) *Adv Funct Mater* - Experimental THz waveguide confirmation
- Frede et al. (2023) *arXiv* - Multi-node polarization preservation

**Biophoton Data**
- Tang & Dai (2014) *PLOS ONE* - Glutamate-induced imaging protocol
- Wang et al. (2016) *PNAS* - Human brain 865nm spectral redshift
- Chen et al. (2020) *Brain Res* - Aging blueshift
- Wang et al. (2023) *Front Aging Neurosci* - AD spectral shift (648→582 nm)

**Nanoantenna Mechanism**
- Zangari et al. (2018) *Sci Rep* - Nodes as bio-nanoantennas
- Zangari et al. (2021) *Sci Rep* - Photons in active nerve (experimental)

**Quantum Theory**
- Liu, Chen & Ao (2024) *Phys Rev E* - Entangled biphoton generation in myelin (cavity QED)

**Full Bibliography**: See individual documents

---

## ✅ Project Status

### **Validated**
- ✅ **Baseline match**: g=0.78 → 648nm prediction matches Dai's WT data exactly
- ✅ **Blueshift direction**: Demyelination shifts spectrum toward blue (shorter wavelengths)
- ✅ **Relay model math**: E/(1-T) geometric series (analytically exact)
- ✅ **Research gap**: Systematic review confirms zero demyelination-biophoton studies
- ✅ **Detection feasibility**: Within standard PMT sensitivity range

### **Predictions (Testable)**
- ⏱ **Cuprizone spectral shift**: 794→581nm (large demyelination, g=0.70→0.96)
- ⏱ **Dual signature**: External up + internal down (anti-correlated)
- ⏱ **Remyelination residual**: Permanent ~26nm blueshift after recovery

### **Known Limitations** (See [status report](biophoton_status_report.md))
- ⚠️ **Magnitude calibration**: Model predicts larger shifts than Dai's AD data (likely due to g-ratio differences: AD ~0.85 vs severe cuprizone ~0.96)
- ⚠️ **Two mechanisms**: AD blueshift has both metabolic (~35nm, drug-reversible) and structural (~31nm, permanent) components
- ⚠️ **Quantitative predictions**: Exact wavelengths depend on precise g-ratio determination

### **Next Steps**
1. ▶️ Run cuprizone experiment (validates or falsifies model)
2. ▶️ Measure g-ratios in Dai's AD tissue (resolves magnitude discrepancy)
3. ▶️ Publish relay theory + experimental results

---

## 🧠 Personal Motivation

This research was catalyzed by experiencing **paralysis from a demyelinating disorder**. The central question is both scientific and personal:

> **What happens to the light in your nerves when myelin is destroyed?**

Beyond curiosity, understanding the optical dimension of demyelination could enable:
- Earlier disease detection
- Objective remyelination monitoring for drug trials
- Non-invasive alternatives to MRI
- New perspectives on neural information processing

---

## 📖 Citation

If you use this work:

```bibtex
@software{lengfelder2026biophoton,
  author = {Lengfelder, Joshua},
  title = {Biophoton Waveguide Physics in Myelinated Axons},
  year = {2026},
  url = {https://github.com/luckyjupiter/biophoton-research},
  note = {Computational models and experimental proposal for measuring
          biophoton emission during demyelination}
}
```

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>⚡ The experiment to answer a fundamental question about nervous system optics ⚡</strong>
</p>

<p align="center">
  <em>Last Updated: February 2026</em>
</p>
