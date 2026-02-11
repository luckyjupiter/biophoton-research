# Track 07: Unified Multi-Scale Model

## Connecting Molecular Biophoton Generation Through Waveguide Transport to Network-Level Computation in Myelin Sheaths

---

## 1. Overview

No unified model currently exists that connects the molecular origins of biophoton emission, through their waveguide transport in myelinated axons, to any functional role in neural network computation. The literature is fragmented across three largely independent research communities:

- **Biochemists and biophysicists** who study ultra-weak photon emission (UPE) as a marker of oxidative stress, characterizing the reactive oxygen species (ROS) cascade and its photon-yielding terminal reactions.
- **Photonics and waveguide modelers** who treat the myelinated axon as a dielectric structure and solve Maxwell's equations for guided mode propagation, without detailed attention to photon sources or sinks.
- **Computational neuroscientists** who propose photonic feedback mechanisms (e.g., Zarkeshian et al. 2022) but treat photon generation and transport as black-box parameters.

The goal of this track is to build a single mathematical and computational framework that chains these three scales together with explicit coupling terms, so that molecular-level parameters (e.g., mitochondrial superoxide production rate) propagate through to network-level observables (e.g., learning accuracy in a photonically-augmented neural network). This is the most ambitious track in the research program. Success requires not just assembling the pieces but identifying which cross-scale couplings matter and which can be safely coarse-grained away.

**Central question:** Given realistic molecular photon generation rates, realistic waveguide losses, and realistic neural network architectures, is there a physically plausible regime in which biophotons carry functionally meaningful information?

---

## 2. Scale 1: Molecular Generation

### 2.1 The ROS Cascade

Biophoton emission in biological tissue originates from a well-characterized (though quantitatively uncertain) cascade of reactive oxygen species reactions. The dominant pathway in neural tissue proceeds as follows:

```
Electron Transport Chain (Complex I, III)
        |
        | (~0.15-2% electron leakage)
        v
    Superoxide (O2^{.-})
        |
        | SOD (k ~ 2 x 10^9 M^{-1}s^{-1})
        v
    H2O2
        |
        | Fenton reaction: Fe^{2+} + H2O2
        | (k ~ 76 M^{-1}s^{-1})
        v
    Hydroxyl radical (OH.)
        |
        | H-abstraction from PUFA
        | (k ~ 10^8 - 10^9 M^{-1}s^{-1})
        v
    Lipid radical (L.)
        |
        | + O2 (diffusion-limited)
        v
    Lipid peroxyl radical (LOO.)
        |
        +---> Russell mechanism: 2 LOO. -> tetroxide -> products
        |
        v
    Dioxetane intermediate (LOOL)
        |
        | Thermolysis
        v
    Triplet excited carbonyl (^3R=O*) + Singlet oxygen (^1O2)
        |
        | Radiative relaxation
        v
    PHOTON EMISSION
```

### 2.2 Rate Equations for the ROS Cascade

Define concentrations: `[O2.-]` = superoxide, `[H2O2]` = hydrogen peroxide, `[OH.]` = hydroxyl radical, `[LH]` = polyunsaturated fatty acid, `[L.]` = lipid radical, `[LOO.]` = lipid peroxyl radical, `[LOOH]` = lipid hydroperoxide, `[^3C*]` = triplet carbonyl, `[^1O2]` = singlet oxygen.

The deterministic rate equations are:

```
d[O2.-]/dt = J_leak(V_m, [O2]) - k_SOD[SOD][O2.-] - k_auto[O2.-]^2 - k_Fe[Fe^{3+}][O2.-]

d[H2O2]/dt = k_SOD[SOD][O2.-] + (1/2)k_auto[O2.-]^2 - k_CAT[CAT][H2O2] - k_GPx[GPx][H2O2][GSH] - k_Fenton[Fe^{2+}][H2O2]

d[OH.]/dt = k_Fenton[Fe^{2+}][H2O2] - k_LH[OH.][LH] - k_scav[OH.][S]

d[L.]/dt = k_LH[OH.][LH] - k_O2[L.][O2]

d[LOO.]/dt = k_O2[L.][O2] - k_prop[LOO.][LH] - 2k_Russell[LOO.]^2 - k_vitE[LOO.][VitE]

d[LOOH]/dt = k_prop[LOO.][LH] - k_decomp[LOOH]

d[^3C*]/dt = phi_C * k_Russell[LOO.]^2 + phi_C * k_diox[dioxetane] - k_rad_C[^3C*] - k_nr_C[^3C*] - k_ET[^3C*][A]

d[^1O2]/dt = phi_O2 * k_Russell[LOO.]^2 + k_ET_O2[^3C*][O2] - k_rad_O2[^1O2] - k_quench[^1O2][Q]
```

where:

| Parameter | Description | Typical Value | Reference |
|-----------|-------------|---------------|-----------|
| `J_leak` | ETC leakage flux | 0.15-2% of O2 consumption | Murphy 2009 |
| `k_SOD` | SOD dismutation rate | ~2 x 10^9 M^{-1}s^{-1} | McCord & Fridovich |
| `k_CAT` | Catalase rate | ~10^7 M^{-1}s^{-1} (but saturates) | Chance 1948 |
| `k_Fenton` | Fenton reaction rate | ~76 M^{-1}s^{-1} | Wardman & Candeias |
| `k_LH` | OH. + PUFA abstraction | ~10^8-10^9 M^{-1}s^{-1} | Buxton et al. 1988 |
| `k_Russell` | Russell mechanism rate | ~10^6-10^8 M^{-1}s^{-1} | Russell 1957 |
| `k_prop` | LOO. propagation | ~10^1-10^2 M^{-1}s^{-1} | Pratt et al. 2011 |
| `phi_C` | Triplet carbonyl yield | ~0.01-0.1 | Cilento & Adam |
| `phi_O2` | Singlet O2 yield (Russell) | ~0.01-0.1 | Miyamoto et al. |
| `k_rad_C` | ^3C* radiative rate | ~10^3-10^4 s^{-1} | Turro et al. |
| `k_rad_O2` | ^1O2 radiative rate | ~1 s^{-1} (dimol: 634, 703 nm) | Schweitzer & Schmidt |

The **photon emission rate** is:

```
Phi_photon = k_rad_C * [^3C*] * V_cell + k_rad_O2 * [^1O2] * V_cell
```

where `V_cell` is the effective volume of the emitting region (mitochondrial membrane vicinity, ~10^{-15} to 10^{-14} L per mitochondrion).

### 2.3 Stochastic Kinetics: Gillespie Algorithm

The deterministic rate equations above are appropriate when molecule numbers are large. However, in a single mitochondrion, the number of simultaneously existing superoxide radicals may be on the order of 1-100 at any given instant. At these low copy numbers, stochastic fluctuations dominate, and the continuous ODE approximation breaks down.

The Gillespie Stochastic Simulation Algorithm (SSA) treats the system as a set of `M` reaction channels with propensity functions `a_mu(x)`, where `x` is the state vector of molecule counts:

```
For reaction mu with rate constant c_mu and reactant counts:
    a_mu(x) = c_mu * h_mu(x)

where h_mu(x) is the combinatorial factor:
    - Unimolecular: h = X_i
    - Bimolecular: h = X_i * X_j  (i != j)  or  X_i(X_i - 1)/2  (i = j)
```

At each step:
1. Compute total propensity: `a_0 = sum_{mu=1}^{M} a_mu(x)`
2. Draw time to next reaction: `tau = (1/a_0) * ln(1/r_1)`, where `r_1 ~ Uniform(0,1)`
3. Select reaction `mu` with probability `a_mu / a_0`
4. Update state: `x -> x + nu_mu` (stoichiometry vector)

For the biophoton problem, the key stochastic event is the **photon emission reaction** itself. Each emission event produces exactly one photon. The waiting time between emissions follows an exponential distribution with rate `Phi_photon`. Given typical emission rates of 1-100 photons/s per cell, and mitochondrial counts of ~1000 per neuron, this gives roughly 10^{-3} to 10^{-1} photons/s per mitochondrion --- meaning individual photon emission events are rare, Poisson-distributed stochastic events.

**Implementation strategy:** Use the tau-leaping variant of Gillespie for the fast ROS reactions (SOD dismutation, O2 addition to L.) and exact SSA for the slow terminal reactions (dioxetane decomposition, radiative relaxation) that produce the actual photons.

### 2.4 Spectral Emission Model

Different molecular species emit at characteristic wavelengths:

| Emitting Species | Wavelength(s) | Transition | Quantum Yield |
|-----------------|---------------|------------|---------------|
| Triplet carbonyl (^3R=O*) | 350-550 nm (peak ~420-480 nm) | T1 -> S0 phosphorescence | ~10^{-9} to 10^{-7} |
| Singlet O2 monomol (^1Delta_g) | 1270 nm | ^1Delta_g -> ^3Sigma_g | ~10^{-7} |
| Singlet O2 dimol (^1O2)_2 | 634 nm, 703 nm | Simultaneous pair emission | ~10^{-9} |
| Excited pigments (^1P*) | 550-750 nm (varies) | S1 -> S0 fluorescence | ~10^{-4} to 10^{-2} |
| Excited pigments (^3P*) | 750-1000 nm (varies) | T1 -> S0 phosphorescence | ~10^{-6} to 10^{-4} |
| Dioxetane decomposition | 400-600 nm | Direct chemiluminescence | ~10^{-8} to 10^{-6} |

The total spectral emission density is:

```
I(lambda) = sum_i eta_i(lambda) * Phi_i
```

where `eta_i(lambda)` is the normalized emission spectrum of species `i` and `Phi_i` is its total emission rate. The dominant contributions in the visible range (380-700 nm, relevant for waveguide transport) come from triplet carbonyls and singlet oxygen dimol emission.

**Key uncertainty:** The relative contributions of each pathway depend strongly on local concentrations of quenchers (carotenoids, tocopherol, ascorbate), pigments available for energy transfer, and oxygen tension. These are poorly constrained in intact neural tissue.

### 2.5 Coupling to Neural Activity

Action potentials modulate mitochondrial ROS production through several mechanisms:

1. **Metabolic demand:** Each action potential requires ATP-dependent Na+/K+-ATPase activity to restore ionic gradients. Increased ATP demand drives increased electron transport chain flux, which increases `J_leak`:

```
J_leak(t) = J_leak^{basal} + Delta_J * sum_k delta(t - t_k) * h(t - t_k)
```

where `t_k` are spike times, `h(t)` is a kernel describing the metabolic response (rise time ~ms, decay ~100 ms), and `Delta_J` is the per-spike increment.

2. **Calcium transients:** Action potentials cause Ca^{2+} influx through voltage-gated calcium channels. Mitochondrial Ca^{2+} uptake stimulates TCA cycle dehydrogenases, increasing NADH supply and ETC flux:

```
J_leak(V_m, [Ca^{2+}]_mito) = J_0 * (1 + alpha * [Ca^{2+}]_mito / (K_Ca + [Ca^{2+}]_mito)) * f(V_m)
```

3. **Membrane potential:** The mitochondrial membrane potential (Delta_psi_m) directly affects the thermodynamics of electron leakage. Higher Delta_psi_m increases the probability of electron escape to O2:

```
J_leak proportional to exp(beta * Delta_psi_m)
```

where `beta ~ 0.1 mV^{-1}`, meaning a 10 mV increase in Delta_psi_m roughly doubles leakage.

The net effect is that bursts of neural activity produce transient increases in biophoton emission with a latency of ~1-10 ms and a duration of ~100-1000 ms, creating a temporally blurred representation of spiking activity in the photon channel.

### 2.6 C-H Vibrational Cascade (Liu Model)

Liu et al. (2019) proposed an alternative biophoton generation mechanism based on vibrational energy cascading through C-H stretch modes in lipid chains within the myelin sheath. The key physics:

A Morse oscillator models the anharmonic C-H bond potential:

```
V(r) = D_e * (1 - exp(-a(r - r_e)))^2

Energy levels: E_n = hbar*omega_0*(n + 1/2) - hbar*omega_0*x_e*(n + 1/2)^2

where:
    D_e ~ 4.3 eV (C-H bond dissociation energy)
    omega_0 ~ 3000 cm^{-1} (fundamental C-H stretch)
    x_e ~ 0.02 (anharmonicity parameter)
    a = omega_0 * sqrt(mu / (2 * D_e))
    mu = reduced mass of C-H ~ 0.93 amu
```

The anharmonicity allows multi-quantum transitions. Liu's proposal is that metabolic energy excites high-overtone C-H stretch modes (n = 4-6, energies ~1.3-1.9 eV, corresponding to 650-950 nm), which can then relax through:

1. **Sequential single-photon cascade:** n -> n-1 -> ... -> 0, emitting infrared photons at each step.
2. **Two-photon emission:** A coherent or near-simultaneous two-photon process where an overtone at energy E_n relaxes by emitting two photons whose energies sum to E_n.

The two-photon emission rate for a Morse oscillator scales as:

```
Gamma_2ph proportional to alpha_fine^2 * omega^5 * |<n|mu|m>|^2 * |<m|mu|0>|^2 / (E_m - hbar*omega)^2
```

where `alpha_fine` is the fine structure constant and the sum runs over intermediate virtual states `|m>`.

**Critical assessment:** The two-photon emission rate from a single molecular oscillator is extremely small (scaling with alpha_fine^2 ~ 10^{-5} relative to one-photon). This mechanism is unlikely to compete with the ROS pathway unless there is a collective enhancement (e.g., superradiance from coherently excited C-H oscillators in a lipid bilayer, or cavity enhancement by the myelin structure). The Liu model remains speculative and lacks direct experimental confirmation.

---

## 3. Scale 2: Waveguide Transport

### 3.1 Coupling Efficiency: Generated Photons to Guided Modes

Not every photon emitted by a molecular source enters a guided mode of the myelin waveguide. The coupling efficiency `eta_couple` depends on:

1. **Spatial overlap:** The emitting molecule must be located within or near the waveguide core (myelin sheath or axon). Mitochondria are concentrated near nodes of Ranvier and in the soma, not uniformly distributed along internodal segments.

2. **Angular overlap:** The emission must fall within the numerical aperture of the waveguide:

```
NA = sqrt(n_myelin^2 - n_axon^2) ~ sqrt(1.44^2 - 1.38^2) ~ 0.41

Acceptance half-angle: theta_max = arcsin(NA / n_medium) ~ 17-18 degrees
```

For an isotropic emitter, the fraction of emission into the guided mode cone is:

```
eta_angular = 1 - cos(theta_max) ~ 0.05 (per direction)
```

Since light can propagate in either direction along the axon, the total angular coupling is ~0.10.

3. **Mode overlap:** Even within the acceptance cone, the emitted field must overlap with the spatial profile of a guided mode. For a dipole emitter at position (r, phi) in the waveguide cross-section:

```
eta_mode(r, phi) = |integral E_mode*(r', phi') * d_emitter * delta(r'-r, phi'-phi) dA|^2 / (integral |E_mode|^2 dA * integral |d|^2)
```

For a source randomly positioned in the periaxonal space, `eta_mode` ~ 0.01-0.1 depending on mode order.

4. **Net coupling efficiency:**

```
eta_couple = eta_angular * eta_mode * eta_spatial ~ 10^{-4} to 10^{-2}
```

This means that of 1-100 photons/s generated per neuron, approximately 10^{-4} to 1 photon/s enters a guided mode. The extremely low coupling at the pessimistic end is a major constraint on any communication hypothesis.

### 3.2 Propagation: FDTD and Transfer Matrix Methods

Once coupled into a guided mode, photons propagate along the internodal myelin segment. Two complementary simulation approaches are available:

**Transfer Matrix Method (TMM):** For cylindrically symmetric structures, the myelin sheath is modeled as a multilayer dielectric cylinder. Each myelin wrap (bilayer thickness ~10 nm, repeat period ~12 nm including aqueous layer) contributes a layer. For N wraps (N ~ 40-160):

```
For each layer j, the transfer matrix is:
M_j = [[cos(k_j*d_j),  -(i/eta_j)*sin(k_j*d_j)],
        [-i*eta_j*sin(k_j*d_j),  cos(k_j*d_j)]]

k_j = (2*pi*n_j / lambda) * cos(theta_j)
eta_j = n_j * cos(theta_j)  (TE) or n_j / cos(theta_j)  (TM)

Total transfer matrix: M_total = prod_{j=1}^{N} M_j
```

The reflectance and transmittance are extracted from `M_total`. This method captures thin-film interference effects that create the ARROW (anti-resonant reflecting optical waveguide) behavior.

**FDTD (Finite-Difference Time-Domain):** For full 3D simulation including bends, tapers, and nodes of Ranvier, Maxwell's curl equations are discretized on a Yee grid:

```
dE/dt = (1/epsilon) * curl(H)
dH/dt = -(1/mu) * curl(E)

Discretized (3D Cartesian):
E_x^{n+1}(i,j,k) = E_x^n(i,j,k) + (dt/epsilon) * [(H_z^{n+1/2}(i,j+1,k) - H_z^{n+1/2}(i,j,k))/dy
                                                        - (H_y^{n+1/2}(i,j,k+1) - H_y^{n+1/2}(i,j,k))/dz]
```

The computational challenge is the scale mismatch: myelin bilayer thickness (~10 nm) requires nm-scale grid resolution, while internodal length (~1 mm) and wavelength (~400-700 nm) set the domain size. A single internodal FDTD simulation at adequate resolution requires ~10^{12} grid points and is computationally prohibitive without approximations.

**Practical approach:** Use TMM for the layered myelin cross-section to determine guided modes and their propagation constants `beta(lambda)`, then propagate these modes along the axon using beam propagation methods (BPM) that only require 2D cross-sectional solves. Reserve full 3D FDTD for short critical regions (node of Ranvier junctions, bends).

### 3.3 Node of Ranvier: Transmission, Reflection, and Coupling

At each node of Ranvier (~1 um gap between myelinated segments), the guided mode encounters a discontinuity. The node presents:

- A gap where the myelin sheath is absent
- Exposed axon membrane with high density of ion channels
- Potential for scattering, reflection, and mode conversion

The transmission coefficient through a single node can be estimated by mode-matching at the entrance and exit planes:

```
T_node(lambda) = |integral E_in(r,phi) * E_out*(r,phi) r dr dphi|^2 /
                  (integral |E_in|^2 r dr dphi * integral |E_out|^2 r dr dphi)
```

Numerical simulations (Kumar et al. 2016, Sefati & Abdi 2022) find:

- Transmission per node: T_node ~ 0.5-0.9 depending on wavelength, node gap width, and mode order
- The ARROW condition creates wavelength-dependent transmission windows. Anti-resonance wavelengths (high transmission) occur when:

```
lambda_AR = 2 * n_myelin * d_myelin * sqrt(1 - (n_axon/n_myelin)^2) / (m + 1/2)

where m = 0, 1, 2, ... is the anti-resonance order
d_myelin = total myelin thickness
```

For typical parameters (n_myelin = 1.44, n_axon = 1.38, d_myelin ~ 1.5 um):
- m=0: lambda_AR ~ 1720 nm (near-IR)
- m=1: lambda_AR ~ 573 nm (visible, green-yellow)
- m=2: lambda_AR ~ 344 nm (UV)

The m=1 anti-resonance falls squarely in the biophoton visible emission range, suggesting spectral selection.

### 3.4 Multi-Node Propagation: Multiplicative Losses

For an axon with `N_nodes` nodes of Ranvier, the total transmission is approximately multiplicative:

```
T_total(lambda) = T_node(lambda)^{N_nodes} * exp(-alpha(lambda) * L_total)
```

where `alpha(lambda)` is the absorption/scattering loss coefficient in the myelin and `L_total` is the total propagation distance.

For a cortical axon spanning 10 mm with internodal length ~1 mm (so N_nodes ~ 10):

| Scenario | T_node | T_total (10 nodes) | Surviving fraction |
|----------|--------|--------------------|--------------------|
| Optimistic (anti-resonance) | 0.90 | 0.35 | 35% |
| Moderate | 0.75 | 0.056 | 5.6% |
| Pessimistic | 0.50 | 9.8 x 10^{-4} | 0.1% |

Even in the optimistic case, losses are substantial. For long-range connections (>10 cm), multi-node losses make direct photonic transmission implausible unless relay/amplification mechanisms exist.

Recent simulations (Xiang et al. 2023) suggest that polarization is well-preserved through multiple nodes and that actual transmission may slightly exceed the simple multiplicative model, perhaps due to mode-reshaping effects at each node.

### 3.5 Spectral Filtering by Myelin Thickness

The ARROW condition creates a spectral filter that depends on myelin thickness. Since myelin thickness varies across axon types and brain regions:

```
Myelin thickness d = (outer diameter - inner diameter) / 2
g-ratio = inner/outer diameter ~ 0.6-0.8

For a 1 um diameter axon with g = 0.7:
    d_myelin ~ 0.15 um -> thin, few wraps, broad spectral transmission
For a 10 um diameter axon with g = 0.7:
    d_myelin ~ 1.5 um -> thick, many wraps, narrow ARROW bands
```

This creates the possibility of **wavelength-division multiplexing**: different axon calibers preferentially transmit different wavelengths. The transmission spectrum `T(lambda; d)` acts as a bandpass filter centered on the anti-resonance wavelengths.

A speculative but testable prediction: the spectral distribution of biophotons measured from thick-myelin tracts (e.g., corpus callosum) should differ from thin-myelin regions (e.g., cortical association fibers).

### 3.6 Polarization Evolution

The myelin sheath is birefringent due to the ordered arrangement of lipid molecules. The ordinary and extraordinary refractive indices differ by:

```
Delta_n = n_e - n_o ~ 0.01-0.03
```

Over an internodal segment of length L ~ 1 mm, the accumulated phase difference between polarization components is:

```
Delta_phi = (2*pi / lambda) * Delta_n * L ~ 30-200 radians (at lambda = 500 nm)
```

This means polarization is rapidly scrambled over a single internode. However, if the birefringence axes are consistent along the axon (which they are, since the lipid bilayers are radially organized), the Jones matrix for a single internode is:

```
J_internode = [[exp(i*phi_o),  0], [0, exp(i*phi_e)]]

J_node = [[sqrt(T_node)*exp(i*delta_1), coupling], [coupling, sqrt(T_node)*exp(i*delta_2)]]
```

The total Jones matrix for N internodes is `J_total = prod (J_node * J_internode)`. Xiang et al. (2023) found that linear polarization can survive multi-node propagation under certain conditions, suggesting polarization could carry additional information.

---

## 4. Scale 3: Network Computation

### 4.1 Zarkeshian et al. (2022): Backpropagation with Photonic Feedback

Zarkeshian et al. proposed that biophotons propagating backward through myelinated axons could carry error signals needed for backpropagation-like learning. Their model:

**Network architecture:** A feedforward network with L layers. Layer l has n_l neurons. Forward (electrical) signal propagation follows the standard:

```
z_l = W_l * a_{l-1} + b_l
a_l = sigma(z_l)
```

**Photonic backward pass:** Post-synaptic neurons stochastically emit biophotons encoding the error signal `delta_l = dL/da_l`. These photons propagate backward through the axon to the pre-synaptic neuron with probability `p_emit * T_axon`:

```
For each synapse (i,j) connecting neuron i in layer l-1 to neuron j in layer l:
    With probability p_photon:
        xi_{ij} = delta_j * encode(biophoton)   [1 bit per photon]
    Otherwise:
        xi_{ij} = 0

Weight update: Delta W_{ij} = -eta * xi_{ij} * a_i
```

**Key results:**
- MNIST classification accuracy ~90-95% even with p_photon as low as 1-5%
- Robust to noise photons (non-signal biophotons from other sources)
- Works with binary (1-bit) photonic signals
- Degrades gracefully as p_photon decreases

**Limitations of the Zarkeshian model:**
- Treats photon generation and transport as a single parameter `p_photon` without physical modeling
- Assumes error signal encoding in biophoton properties (wavelength? timing? polarization?) without specifying the encoding mechanism
- Does not account for the spectral filtering by myelin (Section 3.5) which could help or hinder the scheme
- Ignores the temporal blurring (Section 2.5) between neural activity and photon emission

### 4.2 Information Capacity of the Biophoton Channel

The Shannon capacity of a discrete photon channel with mean photon rate `R_photon` (photons/s) and thermal/noise photon rate `R_noise`:

**Binary channel model:** If each photon carries 1 bit (presence/absence in a time bin dt):

```
C_binary = R_photon * [1 - H(p_error)]

where:
    p_error = R_noise / (R_photon + R_noise)
    H(p) = -p*log2(p) - (1-p)*log2(1-p)
```

**Poisson channel model (more realistic):** For a photon channel with Poisson statistics:

```
C_Poisson = max_{P(x)} I(X;Y)

For mean signal photons n_s and mean noise photons n_n per time bin:
    C <= (1/2) * log2(1 + n_s/n_n)  bits per bin  (Gaussian approximation for large n)
    C ~ n_s * log2(n_s/n_n)  bits per bin  (low photon number regime, n_s << 1)
```

**Numerical estimates:** With R_photon ~ 0.01-1 photons/s arriving at a target neuron (after coupling and transport losses) and R_noise ~ 0.001-0.01 photons/s from background:

- Time bins of dt = 100 ms: n_s ~ 0.001-0.1, n_n ~ 0.0001-0.001
- C ~ 0.001-0.1 bits per time bin
- C ~ 0.01-1 bits per second per synapse

For comparison, a chemical synapse transmits ~1-10 bits per spike at ~1-100 Hz, giving ~1-1000 bits/s. The biophoton channel is **2-5 orders of magnitude slower** than chemical synapses.

This does not preclude a functional role, but it constrains the photonic channel to:
- Slow modulatory signals (not fast information transfer)
- Global/diffuse signaling (many-to-many rather than point-to-point)
- Signals that benefit from the unique properties of photons (speed, non-interaction with electrical fields, potential quantum properties)

### 4.3 Stochastic Neural Network with Dual Electrical + Photonic Signaling

Define a network of N neurons with dual signaling. Neuron i has:
- Membrane potential `V_i(t)` (electrical dynamics)
- Photonic state `P_i(t)` (integrated received photonic signal)

The dynamics:

```
Electrical:
    C_m * dV_i/dt = -g_L*(V_i - E_L) - sum_ion g_ion*m^a*h^b*(V_i - E_ion)
                    + sum_j w_{ij}^{elec} * sum_k delta(t - t_j^k - d_{ij}^{elec})
                    + gamma * P_i(t)

Photonic signal integration:
    tau_P * dP_i/dt = -P_i + sum_j w_{ij}^{phot} * sum_k N_j^{phot}(t - d_{ij}^{phot}) * eta_{ij}

Photon emission (stochastic):
    P(emit photon in [t, t+dt]) = Phi_i(t) * dt
    Phi_i(t) = Phi_0 * (1 + kappa * integral_0^infty h(s) * sum_k delta(t-s-t_i^k) ds)
```

where:
- `w_{ij}^{elec}` = electrical synaptic weight
- `w_{ij}^{phot}` = photonic coupling weight (determined by waveguide connectivity)
- `d_{ij}^{elec}` = electrical synaptic delay (~1-10 ms)
- `d_{ij}^{phot}` = photonic propagation delay (~10^{-5} ms for 1 mm at c/n)
- `gamma` = photonic-to-electrical coupling strength
- `eta_{ij}` = total optical transmission efficiency from j to i
- `kappa` = activity-dependent photon emission modulation depth
- `h(s)` = metabolic response kernel

The **near-instantaneous** photonic propagation (compared to electrical conduction) is a unique feature. A photon traverses 1 cm of myelin in ~50 ps, while an action potential takes ~1-10 ms. If photonic signals carry any information, they arrive effectively instantaneously on the timescale of neural dynamics.

### 4.4 Graph-Theoretic Model of Photonic Connectivity

The photonic connectivity graph `G_phot = (V, E_phot)` differs fundamentally from the electrical/chemical connectivity graph `G_elec = (V, E_elec)`:

1. **Bidirectionality:** Photons can propagate in either direction along a myelinated axon. Every directed electrical edge (pre -> post-synaptic) implies a bidirectional photonic edge.

2. **Weighted edges:** Photonic edge weight is determined by physical optics:

```
w_{ij}^{phot} = eta_couple^{(j)} * T_total^{(j->i)}(lambda) * eta_detect^{(i)}
```

3. **Multi-hop paths:** Photons could potentially scatter or be re-emitted at nodes of Ranvier, creating multi-hop photonic paths that do not correspond to any single axon. This creates a **photonic small-world network** superimposed on the electrical network.

4. **Distance dependence:** Unlike chemical synapses (which are approximately binary: connected or not), photonic coupling strength decays exponentially with the number of nodes:

```
w_{ij}^{phot} proportional to T_node^{N_{nodes}(i,j)} * exp(-alpha * L(i,j))
```

Graph metrics to compute:
- **Photonic path length:** Average shortest optical path between neuron pairs
- **Photonic clustering coefficient:** Probability that photonic neighbors of a neuron are photonically connected to each other
- **Photonic betweenness centrality:** Which neurons are critical hubs in the photonic network?
- **Spectral photonic connectivity:** Separate graphs for each wavelength band, reflecting the spectral filtering of myelin

### 4.5 Comparison with Conventional Connectomics

| Property | Electrical/Chemical | Photonic (Hypothetical) |
|----------|-------------------|----------------------|
| Directionality | Unidirectional (mostly) | Bidirectional |
| Speed | 1-100 m/s (AP) | ~2 x 10^8 m/s |
| Bandwidth | ~1-1000 bits/s per synapse | ~0.01-1 bits/s per channel |
| Connectivity | Sparse, specific | Dense within myelinated bundles |
| Distance dependence | Binary (synapse or not) | Exponential decay |
| Spectral multiplexing | N/A | Possible via myelin thickness |
| Delay | 1-100 ms | ~ps-ns |
| Plasticity mechanism | Synaptic (Hebbian, STDP) | Myelination changes (days-weeks) |
| Information type | Spike timing, rate | Modulatory? Error signals? |

---

## 5. Mathematical Framework for Unification

### 5.1 Hierarchical Modeling

The three scales are connected through a chain of transformations:

```
MOLECULAR PARAMETERS                    CELLULAR OBSERVABLES              NETWORK BEHAVIOR

[ETC leakage rate]  ------>  [Photon emission rate per neuron]  ------>  [Learning accuracy]
[ROS cascade rates]          [Spectral distribution]                    [Information capacity]
[Antioxidant conc.]          [Temporal correlation with spikes]         [Emergent dynamics]
[Myelin refractive index]    [Waveguide transmission spectrum]          [Photonic connectivity]
[Myelin thickness]           [Mode structure]                           [Redundancy/robustness]
```

Formally, define parameter vectors at each scale:

```
theta_1 = {k_SOD, k_CAT, k_Fenton, k_Russell, phi_C, phi_O2, J_leak^0, ...}     (molecular)
theta_2 = {n_myelin, n_axon, d_myelin, L_internode, N_nodes, ...}                 (cellular/waveguide)
theta_3 = {N_neurons, connectivity, w_elec, gamma, ...}                           (network)
```

The **upscaling maps** are:

```
f_{1->2}: theta_1 -> {Phi_photon, I(lambda), rho(t|spike)}
    Computed from: ROS cascade ODE/SSA + spectral model

g_{2->3}: (theta_2, f_{1->2}(theta_1)) -> {T(lambda), eta_couple, w_phot}
    Computed from: waveguide simulation (TMM/BPM/FDTD)

h_{3}: (theta_3, g_{2->3}(...)) -> {accuracy, capacity, dynamics}
    Computed from: neural network simulation
```

The **full model** is the composition:

```
Observable = h_3(theta_3, g_{2->3}(theta_2, f_{1->2}(theta_1)))
```

### 5.2 Multiscale Simulation: Timescale Separation

The three scales span radically different timescales:

| Process | Timescale | Method |
|---------|-----------|--------|
| Molecular vibrations (C-H stretch) | ~10 fs | Molecular dynamics / quantum chemistry |
| ROS reactions (SOD dismutation) | ~1 ns - 1 us | Gillespie SSA / tau-leaping |
| Photon emission events | ~10 ms - 1 s | Poisson process |
| Electromagnetic propagation (1 mm) | ~5 ps | FDTD (steady-state sufficient) |
| Action potential | ~1 ms | Hodgkin-Huxley ODE |
| Metabolic response to spike | ~10-1000 ms | Slow ODE |
| Synaptic plasticity | ~1 s - 1 hour | Learning rule (discrete updates) |
| Myelination plasticity | ~days - weeks | Slowest, quasi-static |

The separation of timescales is actually advantageous for simulation: each faster scale can be averaged or equilibrated before passing its output to the next slower scale.

**Adiabatic elimination strategy:**
1. At the fastest scale: Compute equilibrium ROS concentrations for a given metabolic state (quasi-steady-state approximation for fast intermediates like O2.-, OH.)
2. At intermediate scale: Compute photon emission rates as functions of neural firing rate (averaging over the ROS dynamics)
3. At the electromagnetic scale: Pre-compute waveguide transmission spectra for all relevant axon geometries (these are time-independent)
4. At the network scale: Run a spiking neural network simulation with photonic coupling terms updated at each timestep using the pre-computed tables

```python
# Pseudocode for the multiscale simulation loop

# PRE-COMPUTATION (once)
T_waveguide = precompute_transmission_spectra(axon_geometries, wavelengths)
Phi_table = precompute_emission_rates(firing_rates, metabolic_params)

# SIMULATION LOOP (at neural dynamics timestep dt ~ 0.1 ms)
for t in range(0, T_sim, dt):
    # 1. Update neural dynamics (electrical)
    V, spikes = hodgkin_huxley_step(V, I_syn + I_photonic, dt)

    # 2. Update metabolic state (slow variable)
    metabolic_state = update_metabolism(spikes, metabolic_state, dt)

    # 3. Compute photon emission probability (from pre-computed table)
    for neuron_i in neurons:
        Phi_i = interpolate(Phi_table, metabolic_state[i])
        if random() < Phi_i * dt:
            emit_photon(neuron_i, spectrum=I_lambda(metabolic_state[i]))

    # 4. Propagate photons (instantaneous on this timescale)
    for photon in active_photons:
        for target in connected_neurons(photon.source):
            T = T_waveguide[photon.source, target, photon.wavelength]
            if random() < T * eta_couple:
                deliver_photon(target, photon)

    # 5. Update photonic integration variables
    for neuron_i in neurons:
        P_i = update_photonic_signal(received_photons[i], tau_P, dt)
        I_photonic[i] = gamma * P_i

    # 6. Synaptic plasticity (if applicable, at slower rate)
    if t % plasticity_dt == 0:
        update_weights(spikes, photonic_signals, learning_rule)
```

### 5.3 Coarse-Graining Strategies

For tractable simulation of large networks, aggressive coarse-graining is necessary:

**Level 1: Molecular -> Effective emission rate.** Replace the full ROS cascade with a single effective photon emission rate parameterized by firing rate:

```
Phi_eff(r) = Phi_basal + A * r^n / (r^n + r_half^n)

where r = firing rate, A = max activity-dependent increase,
r_half = firing rate for half-max emission, n = Hill coefficient
```

Fit A, r_half, n from full Gillespie simulations of the ROS cascade driven by spike-triggered metabolic inputs.

**Level 2: Waveguide -> Effective transmission matrix.** Replace the full electromagnetic simulation with a lookup table T(lambda, d_myelin, N_nodes, L_total) pre-computed for representative geometries. Interpolate for intermediate parameter values.

**Level 3: Network -> Mean-field.** For analytical tractability, replace the stochastic network with mean-field equations:

```
dr_i/dt = F(r_i, sum_j w_{ij}^{elec} * r_j + gamma * sum_j w_{ij}^{phot} * Phi_j(r_j))

where F is the neural transfer function (f-I curve)
```

This reduces the system to a coupled set of N rate equations, tractable for networks of thousands of neurons.

### 5.4 Parameter Estimation from Experimental Data

The model contains parameters at each scale. Sources for estimation:

**Molecular scale:**
- ETC leakage rates: Measured in isolated mitochondria (Quinlan et al. 2012, Goncalves et al. 2015)
- ROS cascade rate constants: Extensive physical chemistry literature (Buxton et al. 1988 for OH. reactions, Pratt et al. 2011 for lipid peroxidation kinetics)
- Photon yields: UPE measurements from cell cultures (Burgos et al. 2017, Salari et al. 2015)
- Spectral distribution: Spectral UPE measurements (Usa et al. 1989, Hideg et al. 1991, Prasad & Bhatt 2024)

**Waveguide scale:**
- Refractive indices: Measured by immersion refractometry and ellipsometry (Sun et al. 2012, n_myelin ~ 1.44, n_axon ~ 1.38)
- Myelin thickness and g-ratio: Extensive electron microscopy data (Stikov et al. 2015, g ~ 0.6-0.8)
- Node of Ranvier dimensions: EM data (~1 um gap)
- Internode length: ~100*d_outer (proportional to fiber diameter)

**Network scale:**
- Connectivity: From connectomics data (Allen Brain Atlas, Human Connectome Project)
- Firing rates: Electrophysiology (typically 0.1-100 Hz depending on neuron type)
- Synaptic weights: Inferred from paired recordings

**Key unmeasured parameters (high-priority experimental targets):**
1. Photon emission rate from single identified neurons during controlled activity patterns
2. Wavelength-resolved emission spectrum from intact myelinated tissue
3. Direct measurement of photon propagation in a single myelinated axon

### 5.5 Sensitivity Analysis

Which parameters matter most? Define a global sensitivity index (Sobol index):

```
S_i = Var_{theta_i}(E_{theta_{~i}}[Y | theta_i]) / Var(Y)
```

where Y is a network-level observable and theta_i is the i-th parameter.

**Expected high-sensitivity parameters** (based on the model structure):
1. `eta_couple` (coupling efficiency): Appears multiplicatively; determines whether any photons reach the waveguide at all
2. `T_node` (node transmission): Appears as T^N, so sensitivity grows with path length
3. `Phi_basal` (basal emission rate): Sets the baseline photon flux
4. `gamma` (photonic-to-electrical coupling): Determines how photonic signals affect neural dynamics
5. `phi_C` and `phi_O2` (quantum yields): Directly scale photon production

**Expected low-sensitivity parameters:**
1. Individual ROS cascade rate constants (fast intermediates are in quasi-steady-state)
2. Exact spectral shape (if waveguide is broadband)
3. Polarization state (if detection is polarization-insensitive)

A formal sensitivity analysis should be performed with Monte Carlo sampling of the parameter space, propagating through the full model chain.

### 5.6 Bayesian Hierarchical Models

The multi-scale nature of the problem maps naturally onto Bayesian hierarchical modeling:

```
Level 0 (hyperpriors): p(psi)
    Distributions over classes of molecular/cellular parameters

Level 1 (molecular): p(theta_1 | psi)
    ROS cascade parameters for a specific cell type/condition

Level 2 (cellular): p(theta_2 | theta_1)
    Waveguide parameters conditioned on tissue composition
    p(Phi_photon | theta_1) from the molecular model

Level 3 (network): p(theta_3 | theta_2)
    Network coupling parameters conditioned on waveguide properties
    p(Y | theta_3, theta_2) likelihood of observed network behavior

Posterior: p(theta_1, theta_2, theta_3 | data) proportional to
    p(data | theta_3) * p(theta_3 | theta_2) * p(theta_2 | theta_1) * p(theta_1 | psi) * p(psi)
```

This framework allows:
- **Data integration:** Molecular measurements (in vitro ROS rates), cellular measurements (UPE from tissue slices), and network measurements (behavioral/learning data) all inform the same model
- **Uncertainty propagation:** Uncertainty in molecular parameters propagates up to uncertainty in network predictions
- **Experimental design:** Identify which measurements would most reduce uncertainty in network-level predictions (expected information gain / Bayesian optimal experimental design)

Inference via Markov Chain Monte Carlo (MCMC) or variational methods. The computational cost scales with the number of parameters and the cost of each forward model evaluation.

---

## 6. Computational Architecture

### 6.1 Agent-Based Modeling

The most natural computational framework is an **agent-based model** where each neuron is an agent with:

- **Internal state:** Membrane potential, metabolic state, ROS concentrations (coarse-grained), photonic signal buffer
- **Electrical connections:** Weighted directed graph (standard synaptic connectivity)
- **Photonic connections:** Weighted undirected graph (waveguide connectivity, derived from myelination patterns)
- **Behaviors:** Spike generation, metabolic dynamics, stochastic photon emission, photon absorption

Each simulation timestep:
1. All agents update their electrical dynamics (parallelizable)
2. Spike events are communicated through the electrical graph
3. Metabolic states are updated based on recent spiking
4. Photon emission events are sampled stochastically
5. Emitted photons are propagated through the photonic graph (instantaneous)
6. Receiving agents integrate photonic signals

### 6.2 Hybrid Simulation Architecture

```
+-------------------+       +------------------------+       +-------------------+
|  BIOCHEMISTRY     |       |  ELECTROMAGNETICS      |       |  NEURAL DYNAMICS  |
|  (PySB/BioNetGen) |       |  (MEEP/custom TMM)     |       |  (Brian2/NEURON)  |
|                   |       |                        |       |                   |
|  ROS cascade      |------>|  Waveguide modes       |------>|  Spiking network  |
|  Gillespie SSA    |       |  Transmission spectra  |       |  Photonic coupling|
|  Spectral emission|       |  Node losses           |       |  Plasticity rules |
+-------------------+       +------------------------+       +-------------------+
        ^                           |                               |
        |                           v                               v
        +------ Metabolic feedback (firing rate -> ROS) ------<-----+
```

**Coupling protocol:**
1. **Offline pre-computation (electromagnetics):** Use MEEP (MIT Electromagnetic Equation Propagation) to compute transmission spectra `T(lambda, geometry)` for a library of axon geometries. Store as HDF5 lookup tables. This is the most computationally expensive step but only needs to be done once.

2. **Online co-simulation (biochemistry + neural dynamics):**
   - Brian2 runs the spiking neural network
   - At each timestep, firing rates are passed to the PySB biochemical model
   - PySB returns photon emission rates (or these are computed from pre-fit analytical functions)
   - Brian2 samples photon events and propagates them using the pre-computed transmission tables
   - Received photonic signals are injected as currents into the Brian2 neuron models

3. **Data exchange format:** Use the MUSIC (Multi-Simulation Coordinator) library or custom ZeroMQ-based messaging for inter-simulator communication.

### 6.3 Computational Resources and Feasibility

| Component | Single Run | Parameter Sweep | Tool |
|-----------|-----------|-----------------|------|
| ROS cascade (1 neuron, 10 s) | ~1 CPU-min | ~10^3 CPU-hr (10^3 parameter sets) | PySB + Gillespie |
| Waveguide TMM (1 geometry) | ~1 CPU-sec | ~10 CPU-hr (10^4 geometries x 10^2 wavelengths) | Custom Python/Julia |
| FDTD node simulation (1 node) | ~10-100 GPU-hr | ~10^4 GPU-hr (10^2 geometries) | MEEP |
| Spiking network (10^3 neurons, 10 s) | ~1-10 CPU-hr | ~10^4 CPU-hr (parameter sweep) | Brian2 |
| Full multi-scale (10^3 neurons, 100 s) | ~10-100 CPU-hr | ~10^5 CPU-hr | Coupled system |
| Full multi-scale (10^5 neurons, 100 s) | ~10^3-10^4 CPU-hr | Infeasible without coarse-graining | Coupled system |

**Feasibility assessment:**
- A single researcher with access to a university HPC cluster (~10^4 CPU-cores) can run the full multi-scale model for small networks (~10^3 neurons) with parameter sweeps in ~days-weeks.
- Biologically realistic network sizes (~10^5-10^6 neurons) require the coarse-grained (mean-field + rate model) approach or massive GPU parallelization.
- The pre-computation of electromagnetic transmission tables is a one-time cost that can be amortized across all subsequent simulations.

### 6.4 Open-Source Tools

| Scale | Tool | Description | Key Features |
|-------|------|-------------|--------------|
| Molecular | **PySB** | Python Systems Biology | Rule-based biochemical modeling, ODE/SSA solvers |
| Molecular | **BioNetGen** | BioNetwork Generator | Rule-based modeling, NFsim stochastic simulator |
| Molecular | **COPASI** | Biochemical simulator | Parameter estimation, sensitivity analysis built-in |
| EM | **MEEP** | MIT EM Equation Propagation | Open-source FDTD, supports dispersive materials, MPI parallel |
| EM | **EMpy** | Electromagnetic Python | Transfer matrix method, waveguide mode solvers |
| EM | **Lumerical** | Commercial FDTD | GPU-accelerated, but proprietary and expensive |
| Neural | **Brian2** | Spiking neural simulator | Equation-based model specification, Python, flexible |
| Neural | **NEURON** | Detailed neural simulator | Morphologically detailed neurons, well-validated |
| Neural | **NEST** | Neural Simulation Technology | Large-scale spiking networks, MPI parallel |
| Integration | **MUSIC** | Multi-Simulation Coordinator | Couples different neural simulators |
| Statistics | **PyMC** | Bayesian modeling | MCMC, variational inference, hierarchical models |
| Statistics | **SALib** | Sensitivity Analysis Library | Sobol, Morris, FAST sensitivity methods |

---

## 7. Research Opportunities

### 7.1 Emergent Properties

The central question for this track: **What new network behaviors arise from adding a photonic channel that could not exist with electrical signaling alone?**

Candidate emergent properties:

1. **Long-range synchronization without synaptic chains:** Photons travel at ~2 x 10^8 m/s, while action potentials travel at 1-100 m/s. Photonic coupling could synchronize distant neural populations with near-zero delay, creating a mechanism for the long-range gamma synchrony observed in EEG/MEG that is difficult to explain with axonal conduction delays alone.

2. **Activity-dependent spectral coding:** If different neuron types/states produce different biophoton spectra (due to different mitochondrial ROS profiles), and different myelinated pathways filter different wavelengths, then the photonic channel implements a form of wavelength-division multiplexing that has no electrical analogue.

3. **Non-local error signals for learning:** The Zarkeshian model suggests backpropagation-like learning. More generally, the bidirectional nature of photonic channels provides a natural pathway for "teaching signals" that propagate backward through the network without requiring separate feedback connections.

4. **Phase transitions in network dynamics:** Adding a second (photonic) coupling channel to a neural network may create bifurcations in the network's dynamical repertoire. Mean-field analysis of the dual-channel network:

```
dr/dt = -r + F(w_elec * r + gamma * Phi(r))

Steady states satisfy: r* = F(w_elec * r* + gamma * Phi(r*))

Bifurcation parameter: gamma (photonic coupling strength)
```

For sufficiently large gamma, the system may exhibit bistability, oscillations, or other dynamics absent in the purely electrical network.

### 7.2 Robustness Analysis

Does the photonic channel provide **redundancy** (backup for electrical signaling) or **new capability** (functions impossible without light)?

**Redundancy hypothesis:** If photonic signals carry a low-bandwidth copy of electrical signals, the network becomes more robust to synaptic failure. Model as:

```
Effective coupling: w_eff = w_elec * (1 - p_fail) + w_phot * (1 - p_fail_phot)
```

If electrical and photonic failure modes are independent, the probability of total communication failure is multiplicatively reduced.

**New capability hypothesis:** The photonic channel provides a **broadcast** mechanism (one emitter, many receivers within a myelinated tract) unlike the point-to-point electrical synapse. This could implement:
- Neuromodulation-like effects without specialized neurotransmitter systems
- Volume signaling analogous to nitric oxide or extracellular potassium, but with directionality imposed by waveguide geometry
- Quantum-correlated signaling if entangled biphotons are generated (speculative; see Track 04)

### 7.3 Evolutionary Perspective

If myelin has photonic function, why did it evolve waveguide-optimal geometry?

**The coincidence argument:** Myelin's g-ratio (inner/outer diameter ~ 0.6-0.8) is optimized for electrical conduction velocity. It also happens to create an efficient optical waveguide. Is this coincidence or co-optimization?

**Quantitative test:** Compute the optimal g-ratio for:
1. Electrical conduction velocity (classical result: g_opt_elec ~ 0.6-0.77)
2. Optical transmission (compute T(g) from the waveguide model)
3. Joint optimization: g_opt_joint = argmax_g [alpha * v_conduction(g) + beta * T_optical(g)]

If the observed g-ratio matches the joint optimum better than the electrical-only optimum, this is evidence for co-optimization. This is a clean, falsifiable prediction.

**Phylogenetic analysis:** Myelin evolved independently in vertebrates and some invertebrates (e.g., some annelids, crustaceans). Compare myelin geometry across species:
- Do species with higher cognitive complexity have myelin geometry closer to the photonic optimum?
- Do species that lack myelin (most invertebrates) show compensatory optical structures?
- Is there a correlation between brain size, myelination patterns, and biophoton emission intensity?

### 7.4 Testable Predictions from the Unified Model

1. **Spectral prediction:** The biophoton emission spectrum measured from intact myelinated tracts should show peaks at the ARROW anti-resonance wavelengths of the myelin waveguide, because only those wavelengths propagate long distances. Demyelinated tissue should show a broader, unfiltered spectrum.

2. **Activity-photon correlation:** The cross-correlation between local field potential (electrical) and biophoton emission should peak at a lag of ~1-10 ms, corresponding to the metabolic response time. The lag should be measurable with simultaneous electrophysiology and single-photon detection.

3. **Myelination-dependent learning:** In the Zarkeshian framework, learning requires photonic feedback. Prediction: experimental demyelination (e.g., cuprizone model in mice) should impair learning tasks that are sensitive to error backpropagation, beyond what is expected from conduction velocity changes alone. The effect should be wavelength-specific: blocking only the anti-resonance wavelength of the relevant tract should impair learning.

4. **Photonic connectivity manipulation:** If a technique could selectively block optical (but not electrical) transmission through a myelinated tract (e.g., injecting an absorbing dye into the myelin), this should alter network dynamics in specific, predictable ways that differ from electrically blocking the same tract.

5. **G-ratio prediction:** The model predicts that the optimal g-ratio for combined electrical + photonic function differs slightly from the electrical-only optimum. High-resolution EM measurements of g-ratio across brain regions, correlated with the predicted photonic utility of each region, should reveal systematic deviations.

6. **Scaling with brain size:** Larger brains have longer axons, more nodes of Ranvier, and therefore greater photonic losses. The model predicts either: (a) larger-brained species have thicker myelin to compensate (maintaining optical transmission), or (b) photonic signaling is limited to short-range circuits, with the functional role diminishing in larger brains.

---

## 8. Key References

### Molecular Generation

- **Pospísil, P., Prasad, A., & Rac, M. (2014).** "Mechanism of the Formation of Electronically Excited Species by Oxidative Metabolic Processes: Role of Reactive Oxygen Species." *Archives of Biochemistry and Biophysics.* -- Definitive review of the ROS-to-photon cascade; spectral assignments for triplet carbonyls (350-550 nm), singlet O2 dimol (634, 703 nm), and monomol (1270 nm).

- **Cifra, M. & Pospísil, P. (2014).** "Ultra-weak photon emission from biological samples: definition, mechanisms, properties, detection and applications." *Journal of Photochemistry and Photobiology B.* -- Comprehensive review of UPE mechanisms and measurement methods; quantum yield estimates.

- **Prasad, A. & Bhatt, S.C. (2024).** "Ultra weak photon emission -- a brief review." *Frontiers in Physiology.* -- Recent review updating the field through 2024; spectral range 200-800 nm, intensities from a few to ~1000 photons/s/cm^2.

- **Murphy, M.P. (2009).** "How mitochondria produce reactive oxygen species." *Biochemical Journal.* -- Quantitative treatment of ETC leakage; argues the 1-4% figure is overestimated; ~0.15% under physiological conditions.

- **Quinlan, C.L. et al. (2012).** "Sites of reactive oxygen species generation by mitochondria oxidizing different substrates." *Redox Biology.* -- Site-specific superoxide production rates from Complexes I, II, III.

- **Pratt, D.A., Tallman, K.A., & Porter, N.A. (2011).** "Free radical oxidation of polyunsaturated lipids: New mechanistic insights and the development of peroxyl radical clocks." *Accounts of Chemical Research.* -- Rate constants for lipid peroxidation propagation and termination.

- **Gillespie, D.T. (1977).** "Exact stochastic simulation of coupled chemical reactions." *Journal of Physical Chemistry.* -- The foundational SSA paper; essential methodology for low-molecule-number ROS kinetics.

### Waveguide Transport

- **Kumar, S., Boone, K., Tuszynski, J., Barclay, P., & Simon, C. (2016).** "Possible existence of optical communication channels in the brain." *Scientific Reports.* -- The seminal paper proposing myelinated axons as biophoton waveguides; FDTD simulations; refractive indices n_myelin=1.44, n_axon=1.38; transmission analysis through nodes of Ranvier.

- **Sefati, S. & Abdi, Y. (2022).** "Simulation of nerve fiber based on anti-resonant reflecting optical waveguide." *Scientific Reports.* -- ARROW model of myelinated axon; anti-resonance wavelengths 300-500 nm; realistic optical imperfections including bends and myelin variation.

- **Sefati, S. & Abdi, Y. (2022).** "Electromagnetic modeling and simulation of the biophoton propagation in myelinated axon waveguide." *Applied Optics.* -- Multilayer EM simulation; demonstrates low attenuation, low dispersion, and narrow (~10 nm) bandwidth operation.

- **Xiang, Z. et al. (2023).** "Optical polarization evolution and transmission in multi-Ranvier-node axonal myelin-sheath waveguides." *bioRxiv preprint.* -- Multi-node simulation; finds polarization preservation and slightly better-than-multiplicative transmission through multiple nodes.

- **Liu, X. et al. (2019).** "Myelin Sheath as a Dielectric Waveguide for Signal Propagation in the Mid-Infrared to Terahertz Spectral Range." *Advanced Functional Materials.* -- Extends the waveguide model to infrared/THz; C-H vibrational cascade hypothesis; Morse oscillator framework.

- **Zangari, A. et al. (2018).** "Node of Ranvier as an Array of Bio-Nanoantennas for Infrared Communication in Nerve Tissue." *Scientific Reports.* -- Models nodes of Ranvier as nanoantenna arrays; proposes infrared coupling at nodes.

### Network Computation

- **Zarkeshian, P. et al. (2022).** "Photons guided by axons may enable backpropagation-based learning in the brain." *Scientific Reports.* -- The key paper for Scale 3; stochastic photonic feedback enables MNIST learning; robust to low emission rates and noise; demonstrates that even 1-5% photon transmission probability suffices.

- **Tang, R. & Dai, J. (2014).** "Biophoton signal transmission and processing in the brain." *Journal of Photochemistry and Photobiology B.* -- Correlation between biophoton emission and neural activity in hippocampal slices; potassium-induced increase, TTX-induced decrease.

- **Wang, Z. et al. (2016).** "Human high intelligence is involved in spectral redshift of biophotonic activities in the brain." *PNAS.* -- Reports spectral differences in biophoton emission between human brain regions; correlation with cognitive function; highly controversial.

- **Sun, Y., Wang, C., & Dai, J. (2010).** "Biophotons as neural communication signals demonstrated by in situ biophoton autography." *Photochemical & Photobiological Sciences.* -- Early experimental evidence for biophoton transmission along neural tissue.

### Multiscale Modeling Methodology

- **Dada, J.O. & Mendes, P. (2011).** "Multi-scale modelling and simulation in systems biology." *Integrative Biology.* -- General framework for hierarchical biological modeling; coarse-graining strategies.

- **Lopez, C.F. et al. (2013).** "Programming biological models in Python using PySB." *Molecular Systems Biology.* -- PySB framework for rule-based biochemical modeling.

- **Stimberg, M., Brette, R., & Goodman, D.F.M. (2019).** "Brian 2, an intuitive and efficient neural simulator." *eLife.* -- Brian2 simulator; equation-based model specification; extensible for custom dynamics.

- **Oskooi, A. et al. (2010).** "MEEP: A flexible free-software package for electromagnetic simulations by the FDTD method." *Computer Physics Communications.* -- MEEP FDTD solver; supports dispersive materials, MPI parallelism.

- **Sobol, I.M. (2001).** "Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates." *Mathematics and Computers in Simulation.* -- Methodology for variance-based global sensitivity analysis.

---

## Summary of the Path Forward

Building the unified model is a multi-year effort. A realistic roadmap:

**Phase 1 (Months 1-6): Component models.**
- Implement the ROS cascade in PySB with Gillespie SSA
- Compute waveguide transmission spectra with TMM/MEEP for representative geometries
- Reproduce Zarkeshian et al. results in Brian2 with explicit photon emission model

**Phase 2 (Months 6-12): Pairwise coupling.**
- Connect molecular model to waveguide (input: emission spectrum; output: transmitted spectrum)
- Connect waveguide to network (input: transmission matrix; output: photonic coupling weights)
- Perform sensitivity analysis at each interface

**Phase 3 (Months 12-24): Full integration.**
- Couple all three scales in a single simulation framework
- Run parameter sweeps to identify the viable regime (if any)
- Generate testable predictions for experimentalists
- Bayesian hierarchical analysis integrating all available data

**Phase 4 (Months 24+): Experimental collaboration.**
- Design and advocate for the key experiments (spectral measurement from myelinated tracts, activity-photon correlation, demyelination learning experiments)
- Iterate models based on experimental results

The central question remains open: Is there a physically plausible parameter regime where biophotons carry functionally meaningful information through myelinated axons? This track aims to answer that question with quantitative rigor.
