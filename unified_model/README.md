# Unified Multi-Scale Biophoton Engine (Track 07)

This package implements a runnable, multi-scale simulation that links:

1. **Molecular emission** (ROS-driven biophoton rates + spectrum)
2. **Waveguide transport** (transfer-matrix + ARROW + demyelination losses)
3. **Network propagation** (photonic graph coupled to neuronal activity)
4. **Detector & inference** (PMT/EMCCD/SPAD/SNSPD simulation + low-count stats)

It is intentionally modular so more detailed physics (FDTD, TMM, cQED) can be swapped in later.

## Quick Start

```bash
python -m unified_model.cli demo --detector PMT --exposure-s 10
python -m unified_model.cli sweep --levels 0.0,0.4,0.8 --detector EMCCD
python -m unified_model.cli cuprizone --weeks 1,3,5,7,10 --detector SNSPD
python -m unified_model.cli invert-spectrum --alpha 0.6 --gamma 0.4 --rho 0.5 --stride 8
python -m unified_model.cli optimize-design --detectors PMT,SPAD,SNSPD --exposures 1,5,10
```

## Architecture

- `config.py` — parameter bundles (axon, demyelination, molecular, network)
- `molecular.py` — ROS emission model and spectrum
- `waveguide.py` — ARROW-style passband and demyelination attenuation (network coupling)
- `../models/waveguide.py` — full transfer-matrix waveguide transmission
- `../models/emission.py` — ROS spectrum + waveguide-filtered emission
- `../models/detection.py` — detector models + low-count statistics
- `network.py` — photonic + electrical connectivity
- `engine.py` — unified simulation loop (emission → propagation → coupling)
- `experiments.py` — demyelination sweeps and cuprizone timeline
- `analysis.py` — fano factor, g²(0), and summary stats
- `inversion.py` — grid-search inversion for demyelination parameters
- `optimize.py` — experiment design optimization (detector + exposure)
- `cli.py` — command-line runner

## Output

Each run returns a `SimulationResult` with time series for spikes, metabolic state, emitted photons, and received photons, plus detected counts, spectra, and summary metrics like Fano factor and g²(0).

## Extensibility

- Replace `waveguide.py` with full transfer-matrix / FDTD
- Add spectral filtering in `engine.py` using `molecular.spectrum` × `waveguide.transmission`
- Couple to disease-specific timelines with real parameter trajectories
