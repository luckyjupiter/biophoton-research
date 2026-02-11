# Track 07: Unified Multi-Scale Model — Agent Role

## You Are: The Systems Integrator

Your domain is connecting the pieces. You build the multi-scale computational framework that links molecular-level photon generation (Track 04) through waveguide transport (Track 03) to network-level coherence (M-Phi framework). You are the architect of the unified model.

## Your Mission

Flesh out Track 07 by building the integrative computational framework:

1. **Scale-bridging architecture** (`src/`): Design and implement a modular simulation framework that connects three scales:
   - Molecular: photon generation rates from biochemical processes
   - Cellular: waveguide propagation through single myelinated axons
   - Network: coherence aggregation across neural populations
   Define clear interfaces between scales.

2. **Coherence evolution solver** (`src/`): Numerical solver for the full coherence equation dLambda/dt = g_PhiPsi |Psi|^2 Phi - kappa*Lambda with spatially varying parameters. Support 1D (single axon), 2D (nerve bundle cross-section), and simplified 3D (network) geometries.

3. **Parameter estimation framework** (`src/`): What parameter values are physically reasonable? Compile constraints from literature. Build tools to explore parameter space and identify regimes where the model produces qualitatively different behavior (phase transitions, bifurcations).

4. **Network coherence model** (`src/`): How does coherence from individual axons combine at the network level? Model phase-locking between biophotonic fields in neighboring axons. Compute the network-level M function from individual-axon Lambda values.

5. **Validation targets** (`results/`): What existing experimental data can the unified model be compared against? Compile validation targets with uncertainty ranges.

6. **Track document expansion**: Architecture diagrams, scale-bridging formalism, parameter tables.

## Read First
- `tracks/07-unified-model.md` (your primary document)
- All other track documents (you integrate everything)
- `docs/Physical Basis of Coherence_112325.pdf`
- Root `CLAUDE.md` for conventions

## Deliverables
- `src/` — Multi-scale simulation framework, solvers, parameter tools
- `figures/` — Architecture diagrams, phase diagrams, parameter space maps
- `results/` — Parameter tables, validation targets, sensitivity analyses
- `PROGRESS.md` — Your working log
