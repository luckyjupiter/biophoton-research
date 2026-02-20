# Biophoton Waveguide Physics & Demyelination

Computational research into ultra-weak photon emissions in myelinated neural tissue. Classical waveguide models, quantum discord relay theory, and testable predictions for demyelinating diseases.

## The Core Question

**What happens to light in your nerves when myelin is destroyed?**

Myelinated axons have the refractive index profile of fiber optic cables (n_myelin ≈ 1.44 vs n_axon ≈ 1.34). Multiple independent simulations confirm they can guide photons at visible and near-IR wavelengths—2 million times faster than electrical nerve signals.

Demyelinating diseases (MS, GBS, leukodystrophies) damage this waveguide. The physics makes quantitative, testable predictions about what should change.

## The Research Gap

**Nobody has ever measured biophoton emission during demyelination.**

Despite well-established links:
- ROS → biophotons (proven)
- Demyelination → ROS (proven)  
- Demyelination → biophotons (never measured)

Not in cuprizone. Not in EAE. Not in lysolecithin. Not in any MS model. Not in any species.

## Key Predictions

### 1. Spectral Blueshift During Demyelination
As myelin thins (g-ratio increases from ~0.8 → 0.96), the waveguide cutoff frequency shifts:
- **Healthy myelin (g=0.80):** ~794nm emission centroid
- **Demyelinated (g=0.96):** ~581nm emission centroid  
- **Shift:** ~213nm blueshift

This is a classical waveguide effect—higher-order modes cut off as the cladding thins, leaving only shorter wavelengths guided.

### 2. Dual Signature (Internal vs External)
Myelin damage should simultaneously:
- ↑ External leakage (worse waveguide containment)
- ↓ Internal guided signal (degraded transmission)

Anti-correlated internal/external signals during demyelination would be strong evidence for waveguide function.

### 3. Incomplete Remyelination Signature
Remyelinated myelin is permanently thinner than original (g-ratio ~0.83 vs 0.80). This means:
- Spectral centroid after remyelination: ~768nm
- Permanent residual blueshift: ~26nm from healthy baseline
- **No other biomarker can distinguish remyelinated from healthy myelin optically**

## Node-to-Node Relay Model

Classical waveguide physics + biological saltatory conduction = photonic relay.

**Key insight:** Photons don't need to survive the entire axon length. At each node of Ranvier:
1. Incoming photon arrives through myelin waveguide
2. Action potential triggers ROS burst → new biophoton emission
3. New photon couples into next internode's waveguide
4. Steady-state flux: E/(1-T) where E=emission rate, T=transmission per node

This is photonic saltatory conduction—the optical analog of electrical AP regeneration.

**Evidence:**
- Zangari et al. (2018): Nodes of Ranvier act as "bio-nanoantennas" radiating EM in optical/IR range
- Kumar/Frede: Myelin waveguides support propagating modes at 400-1300nm
- Our relay model predicts plateau instead of exponential decay along stimulated nerves

## Proposed Experiment: Cuprizone Demyelination

**Model:** C57BL/6 mice, 0.2% cuprizone, 6 weeks + recovery  
**Measurement:** EMCCD biophoton imaging (same protocol as Dai 2014)  
**Target:** Corpus callosum, 450μm slices, glutamate stimulation  
**Timeline:** Weeks 0, 2, 4, 6 (demyelination), 8, 11 (remyelination)  
**Cost:** ~$5K (assuming equipment access)

**Primary outcomes:**
1. Intensity vs. demyelination stage
2. Spectral centroid vs. g-ratio (EM correlation)
3. NAC blocks enhancement (confirms ROS source)
4. Remyelination reversal (partial or complete?)

Full experimental design: [demyelination_biophoton_proposal.md](demyelination_biophoton_proposal.md)

## Repository Contents

### Core Documents
- `demyelination_biophoton_proposal.md` - Full experimental protocol for cuprizone measurement
- `discord_relay_darpa_go_research.md` - Node-to-node quantum discord relay theory + DARPA GO connection
- `biophoton_status_report.md` - Honest assessment of what's solid, what's broken, what's speculative

### Research Tracks (see individual files for details)
1. **Photocount Statistics** - Proves broadband biophotons can't distinguish coherent from thermal (useful negative result)
2. **Waveguide Propagation** - Transfer matrix model, multi-node transmission
3. **Quantum Optics** - Cavity QED bounds (weak coupling, Q~5, C~10⁻³)
4. **Detection Feasibility** - Standard PMT can detect myelinated vs demyelinated in <10min
5. **Demyelination Predictions** - Quantitative spectral shifts, dual signature
6. **Relay Model** - E/(1-T) steady state, photonic saltatory conduction

## Key References

**Waveguide Simulations:**
- Kumar et al. (2016) *Sci Rep* - Original myelin waveguide FDTD simulation
- Frede et al. (2023) *arXiv* - Multi-Ranvier-node polarization preservation
- Liu et al. (2019) *Adv Funct Mater* - Experimental THz/mid-IR myelin waveguide

**Biophoton Data:**
- Tang & Dai (2014) *PLOS ONE* - Glutamate-induced biophoton imaging protocol
- Wang et al. (2016) *PNAS* - Human brain spectral redshift (865nm peak)
- Chen, Wang & Dai (2020) *Brain Res* - Aging blueshift

**Quantum Theory:**
- Liu, Chen & Ao (2024) *Phys Rev E* - Entangled biphoton generation via C-H bond vibrations (cavity QED)

**Demyelination Models:**
- Matsushima & Morell (2001) - Cuprizone model review
- Lindner et al. (2008) - G-ratio measurements at weeks 4, 6

**Nanoantenna Mechanism:**
- Zangari et al. (2018) *Sci Rep* - Nodes of Ranvier as bio-nanoantennas
- Zangari et al. (2021) *Sci Rep* - Photons detected in active nerve (experimental confirmation)

## Personal Context

This research was driven by experiencing paralysis from a demyelinating disorder. The goal is to understand what happens to the optical dimension of the nervous system when myelin is destroyed—and potentially develop new ways to monitor disease progression and remyelination.

## Collaboration

Open to collaborations on:
- **Experimental validation** (cuprizone measurement with EMCCD)
- **Theory synthesis** (cavity QED + waveguide models)
- **Clinical translation** (MS biomarker development)

Funding available through Quantum Cognition Corporation for experiments that test these predictions.

**Contact:** josh@quantumcognition.com

## Status

**What's solid:**
- Relay model math (E/(1-T) geometric series)
- Research gap confirmation (nobody's measured demyelination)
- Qualitative predictions (dual signature, blueshift direction)
- Detection feasibility (within standard PMT range)

**What's broken:**
- Specific wavelength predictions off by ~100nm (calibration issue)
- Nanoantenna/ROS emission ratio needs fixing

**What's next:**
- Run the cuprizone experiment (the measurement doesn't depend on the model)
- Fix spectral calibration with real data
- Publish relay model theory separately

Full honest assessment: [biophoton_status_report.md](biophoton_status_report.md)

---

**License:** MIT  
**Last updated:** February 2026
