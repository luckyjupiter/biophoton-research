# Track 07: Unified Multi-Scale Model — Progress Log

## 2026-02-11: Initial Implementation

### Completed
- **constants.py**: Physical constants across all three scales (molecular rates, waveguide geometry, network parameters)
- **molecular_generation.py**: ROS cascade ODE system with 6 species, steady-state analytical solver, photon rate calculator
- **waveguide_transport.py**: Transfer matrix method for multilayer myelin, V-number mode analysis, multi-segment propagation with node losses, wavelength sweep
- **network_coherence.py**: Kuramoto phase coupling model, order parameter computation, build_coupling_matrix (nearest-neighbor/random/all-to-all), M-function calculator
- **coherence_solver.py**: Method-of-lines PDE solver for dLambda/dt = g|Psi|^2*Phi - kappa*Lambda + D*nabla^2(Lambda), demyelination lesion model, bifurcation analysis
- **multiscale_simulator.py**: Top-level orchestrator chaining Scale 1 -> 2 -> 3, parameter sweep utility
- **run_simulation.py**: CLI entry point with argparse, demo outputs, figure generation

### Architecture
```
Scale 1 (Molecular)          Scale 2 (Cellular)           Scale 3 (Network)
─────────────────           ──────────────────           ─────────────────
ROS cascade ODE  ──────>  Transfer matrix     ──────>  Kuramoto coupling
 ↓                         waveguide model               ↓
Triplet carbonyl            ↓                           Order parameter r
 ↓                         Multi-segment                  ↓
Photon rate      ──────>  transmission        ──────>  Lambda_network
(photons/s)                efficiency                     ↓
                                                        M-function
```

### Key Findings (Preliminary)
- Photon generation rate from ROS cascade: order ~10^1-10^3 photons/s per pL depending on oxidative stress level
- Waveguide transmission over 10 internodes (~5mm): extremely low due to node-of-Ranvier losses and absorption
- Network synchronization: Kuramoto model shows phase transition at critical coupling strength
- The delivered photon rate at axon terminals is the critical bottleneck — most photons are lost in transport

### Next Steps
- Add parameter estimation from literature (constrain rate constants)
- Sensitivity analysis (which parameters dominate uncertainty)
- Connect to Track 03's more detailed waveguide models
- Add noise/stochastic terms to the coherence solver
