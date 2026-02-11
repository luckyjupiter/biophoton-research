# Track 04: Quantum Optics Formalism -- Progress Log

## Session 2026-02-11: Initial Build

### Completed

#### 1. Physical Constants and Parameters (`src/constants.py`)
- Implemented all fundamental constants (CODATA 2018)
- Myelin geometry parameters (axon radius, myelin thickness, internode length)
- C-H Morse oscillator parameters from spectroscopy data
- Computed transition frequencies: omega_10 = 5.33e14 rad/s (3.54 um), omega_21 = 5.10e14 rad/s (3.70 um)
- Thermal photon numbers at 310 K: n_th ~ 2e-6 (negligible)
- Free-space decay rates, dephasing parameters

#### 2. Morse Oscillator Model (`src/morse_oscillator.py`)
- Energy levels for C-H vibrational states (E0=0.18 eV, E1=0.53 eV, E2=0.87 eV)
- Morse parameter s = 24.06, supporting 23 bound states
- Anharmonicity analysis: 15.2 meV shift per quantum number
- Transition dipole matrix elements (harmonic approximation, numerically stable)
- Wigner functions for Fock, coherent, squeezed, and thermal states
- Density matrix constructors for all state types

#### 3. Cavity QED Model (`src/cavity_qed.py`)
- Cylindrical shell cavity mode structure
- Q factor estimation from absorption + Fresnel reflection: Q ~ 5 (very lossy)
- Purcell factor: F_P ~ 1e-3 (negligible enhancement)
- Vacuum Rabi coupling: g ~ 5e5 rad/s
- Cavity decay rate: kappa ~ 5e13 rad/s
- Cooperativity: C ~ 9e-4
- **Key finding**: System is firmly in weak coupling regime (g << kappa)
- Strong coupling criterion never met for realistic parameters
- Thickness scan implemented for parametric studies

#### 4. Biphoton State Generation (`src/biphoton_state.py`)
- Second-order perturbation theory amplitude C(omega1, omega2)
- Joint spectral amplitude computation on cavity mode grids
- Schmidt decomposition and entanglement entropy
- **Key finding**: Entanglement entropy S ~ 0.02-0.06 bits for realistic parameters
  - Dominated by vibrational dephasing (Gamma_deph ~ 1e12 rad/s >> g)
  - Entropy increases monotonically with thickness in our model
  - The non-monotonic behavior predicted by Liu-Chen-Ao requires
    more detailed mode structure modeling (transverse mode discretization)
- Thickness dependence computed from 0.3 to 2.5 um

#### 5. Coherence Propagation (`src/coherence_propagation.py`)
- Absorption coefficient model for mid-IR in myelin (C-H band, O-H overtone)
- Rayleigh scattering from structural inhomogeneities
- Decoherence length: ~4 um at transition wavelengths
- g^(1) and g^(2) correlation functions for all major state types
- Lindblad master equation solver (Fock state decay in lossy cavity)
- Entanglement decay model with amplitude damping
- Coherence length survey across 0.5-5.0 um wavelength range

#### 6. Phi-Field Quantum Representation (`src/phi_field_quantum.py`)
- Mapped M-Phi neuro-coherence function M to quantum optical parameters:
  - alpha (displacement) proportional to M * Psi
  - r (squeeze) proportional to M
  - n_thermal proportional to (1-M)
- Constructed displaced squeezed thermal density matrices
- Computed all observables: <n>, Mandel Q, g^(2)(0), purity, entropy
- **Key mapping**:
  - M=0 -> thermal/vacuum (decoherent, g^(2)(0)=2)
  - M=0.5 -> displaced squeezed thermal (super-thermal bunching)
  - M=1 -> displaced squeezed vacuum (pure state, g^(2)(0)>2)

#### 7. Observable Predictions (`src/observable_predictions.py`)
- Quantum vs classical discrimination table
- g^(2)(0) predictions: thermal=2, coherent=1, Fock=0, squeezed=6.7, biphoton=101
- Bell inequality: requires detection efficiency eta > 0.89 (V=0.9)
- Spectral correlation map with energy conservation line
- Demyelination signature: entanglement drops abruptly below 0.45 um

#### 8. Figure Generation (`src/run_all.py`)
Generated 8 publication-quality figures:
- `wigner_functions.png`: Vacuum, Fock |1>, Fock |2>, coherent, squeezed, thermal
- `g2_correlation_curves.png`: g^(2)(tau) for all state types
- `entanglement_vs_thickness.png`: S and K vs myelin thickness
- `joint_spectral_intensity.png`: |C(omega1, omega2)|^2 with energy conservation
- `coherence_length_survey.png`: Loss and coherence length vs wavelength
- `phi_field_properties.png`: Phi-field quantum properties vs M
- `cavity_qed_parameters.png`: Q, F_P, g, kappa, C vs thickness
- `demyelination_signature.png`: Entanglement, Purcell, g^(2)(0) vs thinning

### Key Physical Findings

1. **Weak coupling regime**: The myelin cavity has Q ~ 5 and cooperativity C ~ 1e-3.
   Strong coupling is not achievable. Purcell enhancement is negligible (~0.1%).

2. **Dephasing dominates**: Vibrational dephasing (T2* ~ 1 ps, rate ~ 1e12 s^-1)
   overwhelms the vacuum Rabi coupling (g ~ 5e5 s^-1) by six orders of magnitude.
   This limits the biphoton entanglement entropy.

3. **Energy-time entanglement is robust**: Despite dephasing, frequency
   anti-correlations from energy conservation (omega_1 + omega_2 = omega_20)
   persist, providing the basis for entanglement.

4. **Thermal noise is negligible**: At mid-IR frequencies, thermal photon
   occupation n_th ~ 1e-6 at 310 K. Thermal background is not a concern.

5. **Coherence length ~ 4 um**: Limited by cavity Q, not absorption (which
   gives 1/e ~ 850 um at 3.54 um). Coherence is lost long before photons
   are absorbed.

6. **Bell test requires high detection efficiency**: eta > 89% needed for
   CHSH violation with visibility 0.9. This is achievable with modern
   superconducting nanowire detectors but challenging at mid-IR.

7. **Phi field maps naturally to displaced squeezed states**: The M-Phi
   coherence function M interpolates between thermal (M=0) and
   squeezed-coherent (M=1), with measurable g^(2)(0) differences.

### Open Questions / Next Steps

- Implement transverse mode discretization (HE/EH hybrid modes) for
  more accurate entanglement vs thickness prediction
- Non-Markovian decoherence model (spectral density from MD simulations)
- Collective (superradiant) enhancement from ~10^9 emitters
- Cross-check with Track 03 waveguide propagation parameters
- Temperature dependence study (hypothermia -> fever range)
