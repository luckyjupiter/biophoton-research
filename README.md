# Biophotons in Myelinated Axons: Computational Research Program

A systematic computational investigation into ultra-weak photon emissions (biophotons) in myelinated neural tissue — exploring the hypothesis that myelin sheaths function as biological optical waveguides and deriving testable predictions for demyelinating diseases.

## Overview

Myelinated axons have a refractive index profile (myelin ~1.44, axoplasm ~1.38, extracellular fluid ~1.34) that mirrors the architecture of optical fibers. Multiple independent FDTD simulations have confirmed that guided electromagnetic modes exist at biophoton wavelengths (300–1300 nm). This research program develops the mathematical frameworks, computational models, and experimental predictions needed to test whether this waveguiding is biologically functional — and what happens when the waveguide is damaged by disease.

## Research Tracks

| # | Track | Focus |
|---|-------|-------|
| 1 | [Photocount Statistics](tracks/01-photocount-statistics.md) | Rigorous reanalysis of biophoton count distributions using quantum optics protocols |
| 2 | [Time-Series & Fractal Analysis](tracks/02-time-series-fractal.md) | Temporal structure, memory, and self-similarity in emission sequences |
| 3 | [Waveguide Propagation Modeling](tracks/03-waveguide-propagation.md) | FDTD, ARROW, and multilayer transfer matrix models of myelinated axons |
| 4 | [Quantum Optics Formalism](tracks/04-quantum-optics.md) | Cavity QED, entangled biphoton generation, squeezed states in myelin |
| 5 | [Signal-to-Noise & Detection Theory](tracks/05-signal-to-noise.md) | Statistical inference at ultra-low photon rates, detector modeling |
| 6 | [Demyelination & Pathology](tracks/06-demyelination-pathology.md) | Testable predictions for MS, GBS, and other demyelinating conditions |
| 7 | [Unified Multi-Scale Model](tracks/07-unified-model.md) | Connecting molecular generation → waveguide transport → network computation |
| 8 | [MMI & Coherence Bridge](tracks/08-mmi-coherence-bridge.md) | Mind-matter interaction via the M-Φ coherence framework |

## Simulation Code

- **`models/`** — Core computational models: waveguide physics, demyelination parameters, emission spectra, detection simulation, and visualization tools
- **`unified_model/`** — Multi-scale simulation engine connecting molecular, waveguide, and network layers

```bash
# Run waveguide simulation
cd models && python -m models

# Run unified model
cd unified_model && python -m unified_model
```

## Key Predictions

- **Spectral shift:** Each lost myelin layer blueshifts the operating wavelength by ~52.3 nm (Zeng et al. 2022)
- **Scattering signature:** Fragmented myelin produces spatially patterned lateral emission at break points
- **Oxidative burst:** Active demyelination generates characteristic singlet oxygen (634/703 nm) and triplet carbonyl (350–550 nm) emission peaks
- **Remyelination marker:** Thin remyelinated sheaths produce a permanently blueshifted but present waveguiding signature, distinguishable from both healthy and demyelinated tissue

## Key References

- Kumar et al. (2016) "Possible existence of optical communication channels in the brain." *Scientific Reports* 6, 36508
- Zeng et al. (2022) "Electromagnetic modeling and simulation of biophoton propagation in myelinated axon waveguide." *Applied Optics* 61(14), 4013–4021
- Babini et al. (2022) "Simulation of nerve fiber based on anti-resonant reflecting optical waveguide." *Scientific Reports* 12, 19429
- Frede et al. (2023) "Optical polarization evolution and transmission in multi-Ranvier-node axonal myelin-sheath waveguides." *bioRxiv* 2023.03.30.534951
- Liu et al. (2024) "Entangled biphoton generation in the myelin sheath." *Physical Review E* 110, 024402

See [docs/bibliography.md](docs/bibliography.md) for the full annotated bibliography.

## Contributing

This is an open research program. Contributions welcome:

- **Computational:** MEEP/FDTD simulations, Monte Carlo photon transport, parameter sensitivity analysis
- **Theoretical:** Extensions to the waveguide models, quantum optics formalism, statistical frameworks
- **Experimental:** If you have access to biophoton detection equipment and demyelination animal models, we want to talk

Open an issue or reach out directly.

## Citation

```bibtex
@misc{lengfelder2026biophoton,
  author = {Lengfelder, Joshua},
  title = {Biophotons in Myelinated Axons: Computational Research Program},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/luckyjupiter/biophoton-research}
}
```

## License

Research documents: [CC BY 4.0](LICENSE)
Simulation code (models/, unified_model/): [MIT](LICENSE)

## Author

**Joshua Lengfelder** — [Quantum Cognition Corporation](https://quantumcognition.com)
