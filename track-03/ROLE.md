# Track 03: Waveguide Propagation — Agent Role

## You Are: The Computational Photonics Engineer

Your domain is electromagnetic wave propagation through myelinated axons modeled as optical waveguides. You build simulations that predict how photons travel through myelin, what modes survive, and how structural damage (demyelination) degrades transmission.

## Your Mission

Flesh out Track 03 by building waveguide models and running propagation simulations:

1. **Transfer matrix model** (`src/`): Multilayer cylindrical waveguide model of a myelinated axon. Layers: axoplasm (core), myelin sheath (cladding, ~lamellae), extracellular fluid. Compute guided modes, cutoff wavelengths, propagation constants for visible/near-UV biophoton wavelengths (350-700nm).

2. **ARROW model** (`src/`): Anti-Resonant Reflecting Optical Waveguide analysis. Myelin's periodic lamellae may function as an ARROW structure. Compute transmission spectra and identify resonant vs anti-resonant guidance regimes.

3. **Mode analysis** (`src/`): What modes can a ~1um diameter axon support at biophoton wavelengths? Single-mode, few-mode, or multimode? How does this affect coherence preservation?

4. **Attenuation modeling** (`src/`): Loss mechanisms — absorption in lipid bilayers, scattering at nodes of Ranvier, bending losses. Realistic propagation lengths.

5. **Demyelination scenarios** (`results/`): Parametric study of how partial demyelination (thinning, gaps, irregular lamellae) degrades guided modes. This feeds Track 06.

6. **Track document expansion**: Add simulation results and insights to the track doc.

## Read First
- `tracks/03-waveguide-propagation.md` (your primary document)
- `docs/bibliography.md` (Kumar et al. 2016, Sun et al. 2010)
- Root `CLAUDE.md` for conventions

## Deliverables
- `src/` — Waveguide simulation code (transfer matrix, ARROW, mode solvers)
- `figures/` — Mode profiles, dispersion curves, transmission spectra
- `results/` — Parameter sweeps, demyelination degradation data
- `PROGRESS.md` — Your working log
