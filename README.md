# Biophoton Waveguide Physics in Myelinated Axons

> **Investigating the optical dimension of demyelinating disease through computational physics and testable experimental predictions**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Active Research](https://img.shields.io/badge/Status-Active%20Research-blue)

---

## Executive Summary

Myelinated axons possess the refractive index architecture of cylindrical waveguides (n_myelin ≈ 1.44 vs n_axon ≈ 1.34), capable of guiding biophotons—ultra-weak photon emissions generated during cellular metabolism—at speeds millions of times faster than electrical nerve conduction. This repository presents computational models predicting how demyelinating diseases disrupt this optical infrastructure, alongside a concrete experimental proposal to test these predictions.

**The Central Finding**: Despite well-established causal links (demyelination → ROS → biophotons), **no study has measured biophoton emission during demyelination** in any animal model or human tissue. We propose filling this gap with a straightforward cuprizone mouse experiment that could establish biophotons as a novel biomarker for myelin damage and repair.

---

## Table of Contents

- [Scientific Background](#scientific-background)
- [Key Theoretical Predictions](#key-theoretical-predictions)
- [The Node-to-Node Relay Model](#the-node-to-node-relay-model)
- [Proposed Experiment](#proposed-experiment)
- [Repository Structure](#repository-structure)
- [References & Citations](#references--citations)
- [Collaboration](#collaboration)
- [Project Status](#project-status)

---

## Scientific Background

### The Myelin Waveguide Hypothesis

Myelin sheaths, traditionally understood solely as electrical insulators, exhibit optical properties consistent with dielectric waveguide function:

- **Refractive index contrast**: Myelin (n=1.44) forms a higher-index cladding around the lower-index axoplasm (n=1.34)
- **Cylindrical geometry**: Concentric lamellae create the architecture of a step-index fiber
- **Wavelength support**: FDTD simulations (Kumar et al. 2016; Frede et al. 2023) confirm propagating modes at 400-1300 nm
- **Experimental validation**: THz spectroscopy demonstrates myelin acts as a waveguide for mid-IR/THz radiation (Liu et al. 2019)

### Biophoton Emission in Neural Tissue

Ultra-weak photon emissions (UPE) from living tissues, first described by Gurwitsch (1923), arise primarily from:

1. **Metabolic ROS**: Singlet oxygen, excited carbonyls, and lipid peroxidation products
2. **Neural activity modulation**: Emission intensity correlates with action potential frequency (Sun et al. 2010; Tang & Dai 2014)
3. **Spectral signatures**: Human brain tissue shows characteristic peaks at ~865 nm, with species-dependent red-shifting correlating with myelination (Wang et al. 2016)

### The Research Gap

While the literature establishes:
- ✓ Demyelination massively increases oxidative stress (Haider et al. 2011)
- ✓ ROS generates biophotons (Cifra & Pospíšil 2014)
- ✓ Biophoton spectra change with neurodegeneration (Wang et al. 2023)

**No study has directly measured biophoton emission during demyelination.** This gap is particularly striking given:
- Well-characterized animal models (cuprizone, EAE, lysolecithin)
- Available detection technology (EMCCD-based ultra-weak photon imaging)
- Established measurement protocols (glutamate-stimulated brain slice imaging)

---

## Key Theoretical Predictions

### 1. Spectral Blueshift During Demyelination

**Physical Mechanism**: As myelin thins (g-ratio: 0.80 → 0.96), the waveguide cutoff frequency increases, preferentially extinguishing longer-wavelength modes.

| Condition | G-Ratio | Predicted Centroid | Expected Shift |
|-----------|---------|-------------------|----------------|
| Healthy myelin | 0.80 | 794 nm | baseline |
| Week 4 cuprizone | 0.93 | 640 nm | -154 nm (blueshift) |
| Peak demyelination | 0.96 | 581 nm | -213 nm (blueshift) |
| Remyelinated | 0.83 | 768 nm | -26 nm (residual) |

**Falsification criterion**: Measurement of spectral centroid vs. electron microscopy g-ratio at multiple demyelination stages. Absence of correlation or opposite trend would falsify the waveguide hypothesis.

### 2. Dual Signature: Anti-Correlated Internal vs. External Signals

Degraded waveguide function should produce opposite effects on guided vs. leakage modes:

- **Internal (guided) emission**: ↓ Decreases as myelin damage reduces transmission efficiency
- **External (leakage) emission**: ↑ Increases as compromised cladding fails to contain photons

**Prediction**: Pearson correlation coefficient r < -0.7 between internal and external signal strength across demyelination timeline.

### 3. Incomplete Remyelination Optical Signature

Remyelinated fibers exhibit permanently elevated g-ratios (0.83 vs. 0.80 in naive myelin; Duncan et al. 2017). This structural difference should persist optically:

- **Spectral signature**: ~26 nm residual blueshift even after histologically "complete" remyelination
- **Clinical significance**: First non-invasive method to distinguish remyelinated from native myelin
- **Therapeutic application**: Objective endpoint for remyelination drug trials

---

## The Node-to-Node Relay Model

### Conceptual Framework

Traditional objections to biological photon communication cite the short coherence lengths in scattering media. Our relay model circumvents this by drawing an analogy to electrical saltatory conduction:

**Electrical AP Regeneration** | **Biophoton Relay** (proposed)
---|---
AP decays in myelin | Photon attenuates in myelin
Node of Ranvier regenerates AP | Node emission replenishes photon flux
Saltatory conduction | Photonic saltatory propagation
Steady-state propagation | Steady-state photon flux

### Mathematical Formulation

At each node *i*:
- Emission rate: *E* (photons/s from ROS during AP)
- Transmission to node *i+1*: *T* (0 < *T* < 1)

**Steady-state photon flux**:
```
Φ_ss = E/(1-T)
```

This geometric series yields a **plateau** rather than exponential decay, distinguishing relay from passive waveguide.

### Experimental Support

1. **Zangari et al. (2018)**: Nodes of Ranvier modeled as phased arrays of dipole nanoantennas, radiating in optical/IR range
2. **Zangari et al. (2021)**: Direct detection of photons from stimulated peripheral nerve
3. **Frede et al. (2023)**: Multiplicative transmission losses across nodes, consistent with relay amplification

### Testable Predictions

- **Spatial photon distribution**: Plateau along nerve length (relay) vs. exponential decay (passive)
- **AP frequency dependence**: Linear increase in emission with stimulation rate (each AP = emission pulse)
- **Node-specific ablation**: Photon flux drop localized to damaged node segment

---

## Proposed Experiment

### Overview

**Objective**: Measure biophoton emission across the cuprizone demyelination/remyelination timeline and correlate with histological myelin integrity.

**Model System**: C57BL/6 mice, cuprizone (0.2% w/w in chow, 6 weeks) followed by spontaneous remyelination (4 weeks recovery)

**Primary Endpoint**: Correlation between biophoton spectral centroid and electron microscopy g-ratio

**Estimated Cost**: $4,000-5,000 (assuming equipment access)  
**Timeline**: 8 months to manuscript submission

### Why This Experiment Matters

1. **First measurement** of its kind—publishable regardless of outcome
2. **Low barrier to entry**: Uses existing protocols and standard animal model
3. **High clinical relevance**: MS drug trials desperately need remyelination biomarkers
4. **Theory-agnostic**: Tests fundamental ROS→biophoton link without requiring waveguide hypothesis

Full protocol: **[demyelination_biophoton_proposal.md](demyelination_biophoton_proposal.md)**

---

## Repository Structure

```
biophoton-research/
├── README.md                           # This document
├── demyelination_biophoton_proposal.md # Complete experimental protocol
├── discord_relay_darpa_go_research.md  # Quantum discord relay theory
├── biophoton_status_report.md          # Honest assessment of model status
│
├── models/                             # Computational physics models
│   ├── cuprizone_relay.py             # Demyelination timeline simulation
│   ├── node_emission.py               # ROS-based emission at nodes
│   └── waveguide.py                   # Transfer matrix propagation
│
├── experiments/                        # FDTD waveguide simulations
│   ├── exp01_fdtd_waveguide.py
│   └── results/
│
├── figures/                            # Publication-quality visualizations
│   └── cuprizone_v2_timeline.png
│
├── track-01/ through track-08/         # Research track deep-dives
│   ├── track-01: Photocount statistics (negative result)
│   ├── track-03: Waveguide propagation
│   ├── track-04: Quantum optics bounds
│   ├── track-05: Detection feasibility
│   └── track-06: Demyelination predictions
│
└── viz_output/                         # Generated figures
    ├── relay_vs_pure_loss.png
    ├── cuprizone_dual_signature.png
    └── spectral_relay_evolution.png
```

---

## References & Citations

### Foundational Waveguide Physics
- Kumar, S., et al. (2016). Possible existence of optical communication channels in the brain. *Scientific Reports*, 6, 36508.
- Frede, C., et al. (2023). Light transmission through myelinated nerve fibers: Multi-Ranvier-node polarization analysis. *arXiv:2304.00174*.
- Liu, Z., et al. (2019). Myelin as a dielectric waveguide for THz radiation. *Advanced Functional Materials*, 29(7), 1807862.

### Biophoton Emission Data
- Tang, R., & Dai, J. (2014). Spatiotemporal imaging of glutamate-induced biophotonic activities. *PLOS ONE*, 9(1), e85643.
- Wang, C., et al. (2016). Human high intelligence is involved in spectral redshift of biophotonic activities. *PNAS*, 113(31), 8753-8758.
- Chen, L., Wang, Z., & Dai, J. (2020). Spectral blueshift of biophotonic activity in ageing mouse brain. *Brain Research*, 1749, 147133.

### Quantum Theory
- Liu, Z., Chen, Y.-C., & Ao, P. (2024). Entangled biphoton generation in the myelin sheath. *Physical Review E*, 110(2), 024402.

### Nanoantenna Mechanism
- Zangari, A., et al. (2018). Node of Ranvier as an array of bio-nanoantennas for infrared communication. *Scientific Reports*, 8, 539.
- Zangari, A., et al. (2021). Photons detected in the active nerve. *Scientific Reports*, 11, 3022.

### Demyelination Models
- Matsushima, G.K., & Morell, P. (2001). The neurotoxicant cuprizone as a model to study demyelination and remyelination. *Brain Pathology*, 11(1), 107-116.
- Lindner, M., et al. (2008). Sequential myelin protein expression during remyelination reveals fast and efficient repair. *Glia*, 56(11), 1246-1255.

---

## Collaboration

### Current Outreach
We have initiated contact with:
- **Dr. Jiapei Dai** (Wuhan Institute for Neuroscience): Experimental collaboration on cuprizone measurement
- **Dr. Yong-Cong Chen** (Shanghai University): Theoretical synthesis of cavity QED and waveguide models

### Open Collaboration Opportunities

We welcome partnerships in:

1. **Experimental Validation**
   - Labs with EMCCD biophoton imaging capability
   - MS/demyelination researchers interested in novel biomarkers
   - Funding available for proof-of-concept experiments

2. **Theoretical Development**
   - Quantum optics modeling of myelin cavity
   - FDTD/MODE electromagnetic simulations
   - Statistical mechanics of photon relay networks

3. **Clinical Translation**
   - Non-invasive biophoton detection methods
   - MS drug trial endpoint development
   - Patent/commercialization pathways

**Funding**: Research support available through Quantum Cognition Corporation for experiments testing these predictions.

**Contact**: josh@quantumcognition.com

---

## Project Status

### ✅ Validated Components
- **Relay model mathematics**: E/(1-T) geometric series (analytically exact)
- **Research gap confirmation**: Systematic literature review confirms no prior demyelination-biophoton studies
- **Qualitative predictions**: Blueshift direction, dual signature, remyelination persistence
- **Detection feasibility**: Standard PMT sensitivity adequate for predicted signal levels

### ⚠️ Known Limitations
- **Spectral calibration**: Predicted wavelengths currently ~100nm off from reference data (see [status report](biophoton_status_report.md))
- **Emission mechanism ratio**: Nanoantenna vs. ROS contributions require further refinement
- **Quantum effects**: Discord calculations provide bounds but do not affect classical predictions

### 🎯 Immediate Next Steps
1. **Execute cuprizone experiment** (measurement is independent of model calibration)
2. **Calibrate spectral model** using experimental data
3. **Publish relay theory** in parallel with experimental results

**Full technical assessment**: [biophoton_status_report.md](biophoton_status_report.md)

---

## Personal Motivation

This research program was catalyzed by direct experience of paralysis from a demyelinating disorder. The driving question is both scientific and existential: **What happens to the light in your nerves when myelin is destroyed?** 

Beyond academic curiosity, understanding the optical dimension of demyelination may enable:
- Earlier disease detection
- Objective monitoring of remyelination therapies  
- Non-invasive alternatives to repeated MRI
- Fundamentally new perspectives on neural information processing

---

## License

This work is released under the MIT License. See [LICENSE](LICENSE) for details.

---

## Citation

If you use this work, please cite:

```bibtex
@software{lengfelder2026biophoton,
  author = {Lengfelder, Joshua},
  title = {Biophoton Waveguide Physics in Myelinated Axons},
  year = {2026},
  url = {https://github.com/luckyjupiter/biophoton-research}
}
```

**Last Updated**: February 2026
