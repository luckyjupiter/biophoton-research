# Track 06: Demyelination and Pathology

## 1. Overview

If myelinated axons function as biological optical waveguides -- as proposed by Kumar et al. (2016), Zeng et al. (2022), and others -- then diseases that destroy or degrade myelin should produce measurable changes in biophoton transmission characteristics. This is not speculation layered on speculation: the waveguide models make quantitative, falsifiable predictions about what happens when the waveguide is damaged. A myelin sheath thinned by 5 layers should blueshift the operating wavelength by approximately 260 nm. A sheath fragmented into discontinuous segments should scatter guided photons into radiation modes. A sheath that is absent entirely should eliminate waveguiding. These are straightforward consequences of electromagnetic theory applied to a dielectric waveguide whose structural parameters are changing.

No study has ever measured biophoton emission signatures specifically in the context of demyelinating disease. Not in animal models. Not in tissue preparations. Not in patients. This is a wide-open field representing what may be the most impactful translational research direction in the entire biophoton program, because it connects fundamental photonic physics to diseases affecting approximately 2.8 million people worldwide (MS alone) and for which no non-invasive, real-time biomarker of myelin integrity currently exists.

The research gap is not due to technical impossibility. Ultra-sensitive photon detectors (PMTs, EM-CCDs, SPADs) capable of single-photon counting already exist. Well-characterized animal models of demyelination (EAE, cuprizone, lysolecithin) with predictable timelines of myelin loss and repair are standard tools in neuroimmunology. The optic nerve -- one of the most heavily myelinated structures in the CNS -- is surgically accessible and routinely used in both demyelination and electrophysiology studies. What has been missing is the hypothesis: the recognition that biophoton measurements, informed by waveguide theory, could provide a fundamentally new window into myelin pathology.

This track develops that hypothesis systematically. It synthesizes waveguide physics, oxidative stress photochemistry, and quantum optics models to derive specific, quantitative predictions for how demyelination should alter biophoton emission. It then proposes experimental designs using standard animal models and available detection technology to test those predictions.

---

## 2. Background: Demyelinating Diseases

Demyelinating diseases are a heterogeneous group of conditions unified by a single pathological feature: damage to or loss of the myelin sheath that insulates axons in the central and/or peripheral nervous system. Understanding their diversity is essential for designing experiments that can distinguish biophoton signatures across different mechanisms and stages of myelin damage.

### 2.1 Multiple Sclerosis (MS)

MS is the most common demyelinating disease, affecting approximately 2.8 million people worldwide. It is an autoimmune condition in which the immune system attacks oligodendrocytes and myelin in the CNS.

**Pathological features:**
- **Relapsing-remitting MS (RRMS):** Acute inflammatory lesions with focal demyelination, followed by partial remyelination during remission. Affects ~85% of patients at onset. Lesions are characterized by perivascular T-cell and macrophage infiltration, complement activation, and antibody deposition on myelin.
- **Secondary progressive MS (SPMS):** Transition from relapsing to gradual neurodegeneration with chronic, slowly expanding demyelinated plaques, diffuse white matter damage, and cortical demyelination. Remyelination becomes increasingly ineffective.
- **Primary progressive MS (PPMS):** Steady neurodegeneration from onset without clear relapses. Characterized by diffuse, low-grade inflammation and widespread axonal loss in addition to demyelination.

**Key myelin pathology:** Lesions progress through stages: (1) active demyelination with macrophage-mediated myelin stripping and lipid-laden macrophages, (2) chronic inactive plaques with sharp demyelinated borders and gliotic scarring, (3) shadow plaques representing areas of incomplete remyelination with characteristically thin, short-internode myelin sheaths.

**Relevance to biophoton measurements:** MS provides a spectrum of myelin pathology from acute inflammatory destruction through chronic loss to partial repair, each of which should produce distinct waveguide perturbations.

### 2.2 Guillain-Barre Syndrome (GBS)

GBS is an acute autoimmune polyneuropathy affecting the peripheral nervous system (PNS). The demyelinating form (acute inflammatory demyelinating polyneuropathy, AIDP) accounts for approximately 85-90% of cases in Western countries.

**Pathological features:**
- Lymphocytic infiltration of spinal roots and peripheral nerves
- Macrophage-mediated multifocal stripping of myelin: macrophages penetrate the Schwann cell basement membrane and physically strip myelin lamellae from axons
- Complement-mediated attack on the Schwann cell surface (abaxonal plasmalemma), followed by vesicular paranodal myelin degeneration and retraction
- Segmental demyelination affecting multiple nerve segments simultaneously
- Potential for rapid, near-complete recovery due to Schwann cell remyelination capacity in PNS

**Relevance to biophoton measurements:** GBS offers a peripheral nerve model where demyelination and remyelination occur on a compressed timeline (weeks to months) with accessible nerves suitable for non-invasive or minimally invasive photon detection.

### 2.3 Charcot-Marie-Tooth Disease (CMT)

CMT is the most common inherited neuropathy (prevalence ~1:2500), affecting the peripheral nervous system. The demyelinating forms (CMT1) involve progressive peripheral nerve demyelination.

**Pathological features:**
- **CMT1A** (most common, ~50% of all CMT): Caused by duplication of the PMP22 gene encoding peripheral myelin protein-22. Overexpression of PMP22 leads to abnormal myelin formation, chronic demyelination, and remyelination.
- Nerve conduction velocities severely reduced (< 38 m/sec due to demyelination)
- Characteristic "onion bulb" formations: concentric layers of Schwann cell cytoplasm and basal lamina from repeated cycles of demyelination and remyelination
- Slowly progressive distal muscle atrophy and weakness
- Average age of clinical symptom onset: 12.2 +/- 7.3 years

**Relevance to biophoton measurements:** CMT provides a chronic, slowly progressive model of peripheral demyelination where the "onion bulb" formations create a structurally distinct waveguide geometry (additional concentric layers of abnormal composition) that should produce unique optical signatures different from any other demyelinating condition.

### 2.4 Leukodystrophies

Leukodystrophies are a group of rare, primarily inherited disorders that affect the white matter of the CNS through abnormal production, processing, or development of myelin.

**Key examples:**

- **Metachromatic leukodystrophy (MLD):** Caused by deficiency of arylsulfatase A, leading to toxic accumulation of sulfatides that destroy myelin-producing oligodendrocytes. Progressive demyelination from infancy or childhood.
- **Krabbe disease (globoid cell leukodystrophy):** Caused by deficiency of galactocerebrosidase, leading to accumulation of psychosine (a toxic myelin breakdown product) and characteristic multinucleated "globoid" cells. Rapid, devastating demyelination in infancy.
- **Pelizaeus-Merzbacher disease (PMD):** Caused by mutations in PLP1 encoding proteolipid protein, a major structural component of myelin. Results in failure of myelin formation (hypomyelination) rather than destruction of existing myelin.

**Relevance to biophoton measurements:** Leukodystrophies are particularly informative because they include both demyelinating conditions (MLD, Krabbe -- where myelin is formed and then destroyed) and hypomyelinating conditions (PMD -- where myelin never forms properly). Comparing biophoton signatures between these two pathological mechanisms would test whether the waveguide model can distinguish "degraded waveguide" from "absent waveguide."

### 2.5 Wallerian Degeneration

Wallerian degeneration is the process of axonal and myelin breakdown distal to a site of axonal injury (transection, crush, or ischemia).

**Timeline in PNS:**
- 0-36 hours: Acute axonal degeneration; rapid separation of proximal and distal stumps within 30 minutes, followed by granular disintegration of the axonal cytoskeleton
- 36-72 hours: Axon destruction detected; macrophage recruitment begins; myelin disintegration initiates
- 3-5 days: Distal axon and myelin break into ellipsoid segments (ovoids of Bungner)
- 1-3 weeks: Active macrophage-mediated debris clearance; Schwann cells proliferate and form regeneration tubes (bands of Bungner)
- Complete within ~3 weeks in PNS

**Timeline in CNS:**
- Dramatically slower than PNS
- Myelin sheaths may persist for up to 22 months in rodent CNS
- Microglial clearance of debris is far less efficient than macrophage clearance in PNS

**Relevance to biophoton measurements:** Wallerian degeneration provides a precisely timed model of myelin breakdown stages. The PNS timeline (complete in 3 weeks) is ideal for longitudinal biophoton measurements. The dramatic CNS/PNS difference in clearance rate also provides a natural control for distinguishing "fragmented but present" myelin from "cleared" myelin.

### 2.6 Key Pathological Features Across Conditions

All demyelinating conditions share a common set of structural changes to the myelin sheath, though the mechanism, speed, and extent vary:

| Feature | Description | Waveguide Consequence |
|---------|-------------|----------------------|
| **Thinning** | Reduction in number of myelin lamellae | Altered guided mode structure; wavelength shift |
| **Fragmentation** | Myelin sheath breaks into discontinuous segments | Scattering at segment boundaries; mode coupling |
| **Complete loss** | No myelin remaining on axon segment | No waveguiding; photons radiate into surrounding tissue |
| **Paranodal retraction** | Myelin pulls back from nodes of Ranvier | Effective internode shortening; increased node exposure |
| **Vesicular degeneration** | Myelin splits into vacuoles and vesicles | Massive scattering; loss of refractive index contrast |
| **Remyelination** | New myelin: thinner sheaths, shorter internodes | Distinct spectral signature; shifted but present waveguiding |

---

## 3. Predicted Biophoton Signatures of Demyelination

Three independent theoretical frameworks -- waveguide optics, oxidative stress photochemistry, and quantum electrodynamics -- each generate specific, testable predictions for how demyelination should alter biophoton emission. Critically, these predictions are not mutually exclusive; they address different aspects of the same physical system and could be observed simultaneously.

### 3.1 Predictions from Waveguide Models

The myelinated axon functions as a cylindrical dielectric waveguide with refractive indices of approximately 1.44 (compact myelin), 1.38 (axoplasm), and 1.34 (interstitial fluid). This index contrast supports guided electromagnetic modes within the myelin sheath.

#### 3.1.1 Thinning Myelin: Wavelength Shift

Zeng et al. (2022) demonstrated that the operating wavelength of the myelinated axon waveguide is almost linearly related to the number of myelin layers, with each additional layer shifting the operating wavelength 52.3 nm toward longer wavelengths (redshift). The waveguide operates in a narrow bandwidth on the order of 10 nm.

**Prediction:** If demyelination removes N layers of myelin, the operating wavelength should blueshift by approximately N x 52.3 nm.

| Myelin Loss | Wavelength Shift | Expected Signature |
|------------|-----------------|-------------------|
| 1 layer lost | -52.3 nm blueshift | Subtle spectral shift; detectable with spectrometer |
| 3 layers lost | -156.9 nm blueshift | Major spectral shift; emission band moves substantially |
| 5 layers lost | -261.5 nm blueshift | Emission may shift into UV range or below cutoff |
| 10 layers lost | -523 nm blueshift | If original emission was in visible/NIR, shifts entirely out of guided range |
| All layers lost | N/A | No waveguiding; see section 3.1.3 |

This prediction is independently supported by Chen, Wang, and Dai (2020), who observed spectral blueshift of biophotonic activity in aging mouse brain -- a process known to involve progressive myelin thinning. Wang et al. (2023) further demonstrated reduced biophotonic activities and spectral blueshift in Alzheimer's disease and vascular dementia models, both conditions associated with white matter degeneration.

**Critical note:** The 52.3 nm/layer figure comes from an idealized cylindrical waveguide model. Real demyelination is non-uniform: some lamellae may be disrupted while others remain intact, and the remaining layers may swell or change refractive index due to edema or lipid degradation. The actual wavelength shift per unit of pathological change must be determined experimentally.

#### 3.1.2 Fragmented Myelin: Scattering Losses

When myelin breaks into discontinuous segments (as in early Wallerian degeneration, or the edge zones of MS plaques), each boundary between myelinated and unmyelinated segments acts as a scattering interface. At each boundary:

- Guided modes in the myelinated segment encounter an abrupt change in waveguide geometry
- A fraction of the guided power radiates into the surrounding medium (mode mismatch loss)
- Additional power may couple into higher-order or radiation modes

**Prediction:** Fragmented myelin should produce:
1. **Increased total biophoton emission** from the nerve surface (scattered photons escaping the waveguide laterally, detected by external PMT/CCD)
2. **Decreased transmission** along the axon (fewer photons reaching the distal end)
3. **Spatial patterning** of emission: bright spots at fragmentation boundaries, dark regions between

The magnitude of scattering loss at each boundary depends on the mode structure and the geometry of the discontinuity. For a simple step discontinuity (myelinated to unmyelinated and back), standard waveguide junction theory predicts coupling losses of:

```
L_junction = -10 log10(|overlap integral|^2)  [dB per junction]
```

where the overlap integral is computed between the guided mode of the intact waveguide and the field distribution in the unmyelinated gap. For typical myelin parameters, estimated junction losses are 3-10 dB per boundary, meaning that even 2-3 fragmentation breaks would reduce transmission by 90-99.9%.

#### 3.1.3 Complete Myelin Loss: Elimination of Waveguiding

When myelin is completely absent, the refractive index contrast that supports guided modes vanishes. The axon alone (n = 1.38) surrounded by interstitial fluid (n = 1.34) has a much lower numerical aperture:

```
NA_myelinated = sqrt(n_myelin^2 - n_axon^2) = sqrt(1.44^2 - 1.38^2) = 0.41
NA_bare_axon  = sqrt(n_axon^2 - n_fluid^2)  = sqrt(1.38^2 - 1.34^2) = 0.33
```

While a bare axon retains some weak guiding capacity due to this residual index contrast, the mode structure is fundamentally different: the axon supports only the lowest-order mode at visible wavelengths, with much higher propagation losses. The myelin sheath, by contrast, is the primary waveguide, supporting multiple modes with low attenuation.

**Prediction:** Completely demyelinated axon segments should show:
1. Near-total loss of wavelength-selective waveguiding
2. Dramatically increased attenuation (photons leak out within a few micrometers)
3. Emission from the demyelinated segment that is spectrally broad (no mode selection) and spatially diffuse

#### 3.1.4 Remyelination: Distinct Spectral Signature

Remyelination in the CNS produces myelin sheaths that are characteristically thinner and have shorter internodes than the original myelin (Fancy et al., 2011; Duncan et al., 2017). These thin sheaths persist for years and do not thicken to normal dimensions, as confirmed by studies showing they remain stable for over 2 years (Duncan et al., 2017). Despite their thinness, remyelinated sheaths preserve axon function and restore nerve conduction.

**Prediction:** Remyelinated segments should produce a biophoton signature that is:
1. **Spectrally blueshifted** relative to normally myelinated tissue (fewer layers -> shorter operating wavelength, per the 52.3 nm/layer rule)
2. **Spectrally redshifted** relative to completely demyelinated tissue (some waveguiding restored)
3. **Temporally variable** during the remyelination process as new wraps are added
4. **Spatially distinct** with shorter segments of guided emission (shorter internodes) separated by more frequent gaps (nodes)

This makes remyelination potentially distinguishable from both healthy tissue and ongoing demyelination by spectral analysis alone -- a prediction with direct clinical relevance for monitoring remyelination therapies.

### 3.2 Predictions from Oxidative Stress Models

Biophoton emission in biological tissue is fundamentally linked to oxidative metabolism. The primary photon-generating pathway involves reactive oxygen species (ROS) driving lipid peroxidation, which produces electronically excited species that emit photons upon relaxation.

#### 3.2.1 Active Demyelination: Lipid Peroxidation Burst

Myelin is approximately 70-80% lipid by dry weight, making it one of the most lipid-rich structures in the body. Active immune-mediated demyelination involves:

1. **Oxidative burst** from activated macrophages and microglia (superoxide O2-, hydrogen peroxide H2O2, hydroxyl radical OH-)
2. **Massive lipid peroxidation** as ROS attack the polyunsaturated fatty acids in myelin membranes
3. **Chain reactions** propagating through the lipid bilayers of multiple myelin lamellae

The photochemistry of lipid peroxidation generates photon-emitting species through well-characterized pathways:

```
Lipid-H + OH- -> Lipid- + H2O              (initiation)
Lipid- + O2 -> Lipid-OO-                    (propagation)
Lipid-OO- + Lipid-H -> Lipid-OOH + Lipid-  (propagation)
2 Lipid-OO- -> Lipid-OOOO-Lipid             (Russell mechanism)
              -> triplet carbonyl* + singlet O2* + ROH  (decomposition)
```

**Prediction:** Active demyelination should produce a transient but large increase in biophoton emission intensity, with a spectral signature dominated by:
- **Triplet excited carbonyls** emitting at 350-550 nm (near-UV to blue-green)
- **Singlet oxygen (^1O2)** emitting at 634 nm and 703 nm (monomol phosphorescence) and 1270 nm (near-IR)
- **Excited pigments** (chlorin-type, porphyrin-type) emitting at 550-750 nm

The intensity of this emission burst should correlate with the volume of myelin undergoing active peroxidation and thus with disease activity.

#### 3.2.2 Immune Attack: Characteristic Emission Spectrum

The immune attack on myelin involves specific ROS-generating mechanisms with characteristic spectral signatures:

- **NADPH oxidase** in activated macrophages/microglia produces superoxide, leading to downstream peroxidation products (broadband emission 400-700 nm)
- **Myeloperoxidase (MPO)** in infiltrating neutrophils generates hypochlorous acid (HOCl), which reacts with amines to produce electronically excited singlet oxygen and carbonyls (emission peaks at 570 nm, 634 nm, 703 nm)
- **Mitochondrial ROS** from stressed oligodendrocytes (primarily superoxide from complexes I and III)

**Prediction:** The spectral profile of biophoton emission during active demyelination should be distinguishable from basal oxidative metabolism by:
1. Elevated intensity (10-100x above baseline, based on lipid peroxidation studies in other tissues)
2. Specific spectral peaks at 634 nm and 703 nm (singlet oxygen signature)
3. Enhanced blue-green component (350-550 nm) from triplet carbonyls
4. Temporal correlation with immune cell infiltration (measurable by parallel histology in animal models)

#### 3.2.3 Spectral Biomarkers from ROS Cascade Products

Different ROS cascade products have distinct emission wavelengths, offering the possibility of spectral decomposition to identify which oxidative pathways are active:

| Species | Emission Wavelength | Pathway |
|---------|-------------------|---------|
| Singlet oxygen (^1O2) monomol | 634 nm, 703 nm | Lipid peroxidation (Russell mechanism) |
| Singlet oxygen dimol | 478 nm, 534 nm, 634 nm | High [^1O2] conditions |
| Singlet oxygen (NIR) | 1270 nm | Direct ^1O2 phosphorescence |
| Triplet carbonyls | 350-550 nm (broad) | Dioxetane decomposition |
| Excited pigments | 550-750 nm | Energy transfer from carbonyls to tissue chromophores |

**Prediction:** The ratio of singlet oxygen emission (634/703 nm) to triplet carbonyl emission (350-550 nm) should differ between:
- Active autoimmune demyelination (high MPO activity -> high singlet O2)
- Toxic demyelination (cuprizone: mitochondrial ROS -> more carbonyl-dominated)
- Mechanical injury (Wallerian degeneration: mixed, progressing through phases)

This spectral ratio could serve as a mechanistic biomarker distinguishing different types of demyelination -- a capability no existing biomarker possesses.

### 3.3 Predictions from Quantum Models

Liu et al. (2024) demonstrated theoretically that the cylindrical cavity formed by the myelin sheath can facilitate spontaneous photon emission from vibrational modes of C-H bonds in lipid molecules and generate entangled photon pairs through cavity quantum electrodynamics (cQED).

#### 3.3.1 Entangled Pair Generation and Myelin Thickness

The key finding of Liu et al. is that entangled biphoton generation depends critically on myelin thickness, parameterized by the g-ratio (ratio of inner axon diameter to outer myelinated fiber diameter):

- **Peak entanglement** occurs at g-ratios corresponding to myelin thickness of 0.8-1.1 micrometers
- **Entanglement decreases rapidly** as myelin thickness decreases below a g-ratio of approximately 0.8
- The cavity quality factor Q depends on myelin thickness and regularity

**Prediction:** Demyelination should reduce or eliminate entangled photon pair production by:
1. Reducing cavity Q factor (thinner, irregular myelin = lower Q)
2. Shifting cavity resonance frequencies away from C-H vibrational emission lines
3. Destroying cavity geometry entirely in regions of complete myelin loss

The authors note that their calculations are consistent with the observation that neurodegenerative diseases increase with age as myelin thickness decreases -- suggesting a natural experiment already in progress.

#### 3.3.2 Quantum Coherence as a Demyelination Marker

If entangled photon pairs are indeed generated in healthy myelin, then demyelination should produce a measurable transition from quantum-correlated to classical (uncorrelated) photon emission:

- **Healthy myelin:** Entangled biphoton pairs with characteristic temporal correlations (bunching in coincidence detection)
- **Thinned myelin:** Reduced entanglement; partial correlations
- **Absent myelin:** Classical photon emission only; no excess coincidences above accidental rate

**Prediction:** Coincidence counting measurements (using two detectors in a Hanbury Brown-Twiss configuration) should reveal a progressive loss of photon-photon correlations as demyelination progresses. The second-order correlation function g^(2)(0) should decrease from > 1 (bunched/entangled) toward 1 (coherent/classical) with increasing myelin loss.

**Caveat:** This prediction requires that the entangled photon production rate is sufficient to be detected above background. Liu et al. estimate production rates that are marginal for current detection technology. This remains the most speculative of the three sets of predictions.

---

## 4. Mathematical Modeling

### 4.1 Parametric Waveguide Model with Variable Myelin

We define a cylindrical waveguide model parameterized by pathological variables:

**Geometry:**
- Inner radius (axon): a
- Outer radius (myelinated fiber): b = a / g, where g is the g-ratio
- Myelin thickness: d = b - a = a(1/g - 1)
- Number of myelin layers: N = d / t_layer, where t_layer ~ 12-17 nm (bilayer repeat distance)

**Pathological parameters:**
- **Thickness factor** alpha in [0, 1]: fraction of normal myelin thickness remaining (alpha = 1 is healthy, alpha = 0 is completely demyelinated)
- **Continuity factor** gamma in [0, 1]: fraction of internode length with intact myelin (gamma = 1 is continuous, gamma = 0 is completely fragmented)
- **Regularity factor** rho in [0, 1]: uniformity of remaining myelin (rho = 1 is uniform, rho = 0 is maximally irregular/vesiculated)

**Effective waveguide parameters under pathology:**

The effective refractive index of the myelin layer under pathological conditions:

```
n_eff(alpha, rho) = n_fluid + alpha * rho * (n_myelin - n_fluid)
                   = 1.34 + alpha * rho * 0.10
```

The operating wavelength shifts as:

```
lambda_op(alpha) = lambda_healthy - (1 - alpha) * N_original * 52.3 nm
```

The effective propagation loss per unit length:

```
alpha_prop(alpha, gamma, rho) = alpha_0 / (alpha * gamma * rho) + L_junction * (1 - gamma) / l_internode
```

where alpha_0 is the intrinsic loss of healthy myelin, L_junction is the scattering loss per fragmentation boundary (~3-10 dB), and l_internode is the internode length.

### 4.2 Monte Carlo Simulation of Photon Propagation

For a partially demyelinated axon, analytical solutions are intractable. We propose a Monte Carlo ray-tracing approach:

**Algorithm:**

```
1. Define axon geometry: cylinder of length L, radius a
2. Define myelin map M(z): for each position z along the axon,
   specify local myelin state {alpha(z), rho(z)}
3. Generate N_photon source photons at z=0 with:
   - Wavelength drawn from source spectrum S(lambda)
   - Launch angle drawn from guided mode angular distribution
4. For each photon:
   a. Propagate through myelin segment using wave optics:
      - Check total internal reflection condition at each interface
      - Apply absorption loss: P(z+dz) = P(z) * exp(-mu_abs * dz)
   b. At each fragmentation boundary:
      - Compute mode overlap integral with next segment
      - Transmit with probability |overlap|^2
      - Scatter (escape) with probability 1 - |overlap|^2
      - Record scattered photon position and angle
   c. At unmyelinated gaps:
      - Propagate as radiation mode in bare axon
      - Apply diffraction-based spreading loss
   d. Record: (i) whether photon reaches z=L (transmitted)
              (ii) where photon escapes (lateral emission profile)
              (iii) final wavelength (if wavelength-dependent interactions)
5. Accumulate statistics over all photons
```

**Output metrics:**
- Transmittance T(alpha, gamma) = fraction reaching distal end
- Lateral emission profile I(z, theta) = spatial/angular distribution of escaped photons
- Spectral transmission S_out(lambda) / S_in(lambda) = wavelength-dependent transfer function

### 4.3 Statistical Model for Healthy vs. Demyelinated Tissue

Given a biophoton measurement from a nerve segment, we want to classify it as healthy (H) or demyelinated (D).

**Feature vector** from a measurement:

```
x = [I_total, lambda_peak, sigma_lambda, I_634/I_500, g2_0, tau_corr]
```

where:
- I_total = total photon count rate (photons/s)
- lambda_peak = peak emission wavelength (nm)
- sigma_lambda = spectral width (nm)
- I_634/I_500 = ratio of singlet oxygen emission to carbonyl emission
- g2_0 = second-order correlation at zero delay
- tau_corr = temporal correlation decay time

**Likelihood models:**

Under healthy conditions (H):
```
P(x | H) = N(I_total; mu_H, sigma_H) * N(lambda_peak; lambda_H, delta_H) * ...
```

Under demyelinated conditions (D, parameterized by severity s):
```
P(x | D, s) = N(I_total; mu_D(s), sigma_D(s)) * N(lambda_peak; lambda_D(s), delta_D(s)) * ...
```

**Bayesian classifier:**
```
P(D | x) = P(x | D) * P(D) / [P(x | D) * P(D) + P(x | H) * P(H)]
```

### 4.4 ROC Curves for Diagnostic Detection

The diagnostic performance of biophoton-based demyelination detection depends on:
1. The signal-to-noise ratio of the measurement
2. The magnitude of the biophoton signature change at each disease stage
3. The measurement integration time

**Projected ROC analysis at various stages:**

| Disease Stage | Expected Signal Change | Projected AUC (optimistic) | Projected AUC (conservative) |
|---------------|----------------------|---------------------------|------------------------------|
| Preclinical (< 5% myelin loss) | < 10% intensity change; ~2.5 nm spectral shift | 0.55-0.65 | 0.50-0.55 |
| Early clinical (10-20% loss) | 20-50% intensity change; ~10 nm shift | 0.70-0.80 | 0.60-0.70 |
| Moderate (30-50% loss) | 2-5x intensity change; ~25 nm shift | 0.85-0.95 | 0.75-0.85 |
| Severe (> 50% loss) | > 5x intensity change; > 50 nm shift | 0.95-0.99 | 0.85-0.95 |
| Active inflammation | 10-100x intensity burst | 0.95-0.99 | 0.90-0.95 |

**Critical caveat:** These AUC projections are extrapolations from waveguide models and oxidative stress literature. They have not been validated experimentally. The conservative estimates assume high biological variability and limited detector sensitivity; the optimistic estimates assume low background and stable measurement conditions. The primary purpose of this ROC analysis is to guide experimental design (how many subjects, what integration times) rather than to make clinical claims.

### 4.5 Dose-Response Modeling: Biophoton Signature vs. Degree of Demyelination

We model the relationship between degree of demyelination (D, as fraction of myelin lost) and the composite biophoton signal S as a sigmoidal function:

```
S(D) = S_baseline + (S_max - S_baseline) * D^n / (D^n + K^n)
```

where:
- S_baseline = signal from healthy tissue
- S_max = asymptotic signal at complete demyelination
- K = demyelination fraction producing half-maximal signal change (EC50 analog)
- n = Hill coefficient (steepness of transition)

**Expected parameter ranges (from waveguide model extrapolation):**

For total emission intensity (lateral escape):
- K ~ 0.15-0.30 (half-maximal change at 15-30% demyelination)
- n ~ 1.5-3.0 (moderately steep transition due to nonlinear scattering)

For spectral peak shift:
- Linear relationship expected: delta_lambda ~ -52.3 * N_lost (nm)
- K ~ 0.50 (linear implies K at midpoint)
- n ~ 1.0

For singlet oxygen / carbonyl ratio:
- Threshold behavior expected during active inflammation
- K ~ 0.05-0.10 (detectable early due to inflammatory amplification)
- n ~ 2-4 (steep onset reflecting immune activation threshold)

The differential sensitivity of these biomarkers at different stages of demyelination suggests a multi-parameter approach will outperform any single measurement.

---

## 5. Experimental Design

### 5.1 Animal Model: EAE in Mice

**Model:** Experimental autoimmune encephalomyelitis (EAE) induced by immunization with myelin oligodendrocyte glycoprotein peptide (MOG35-55) in C57BL/6 mice.

**Rationale:** EAE is the standard animal model for MS, producing autoimmune-mediated CNS demyelination with a well-characterized clinical course. The MOG-induced model produces optic neuritis (inflammation and demyelination of the optic nerve) in a substantial fraction of animals, making it directly relevant to biophoton measurements.

**Protocol outline:**
1. Immunize mice with MOG35-55 in complete Freund's adjuvant + pertussis toxin
2. Monitor clinical scores daily (0 = normal, 5 = moribund)
3. At defined clinical stages (pre-symptomatic day 7, onset day 10-12, peak day 14-18, chronic day 28+), sacrifice subgroups for:
   - Ex vivo biophoton measurements of optic nerve and spinal cord
   - Parallel histological assessment (luxol fast blue, MBP immunostaining)
   - Electron microscopy for g-ratio quantification
4. Correlate biophoton signatures with histological demyelination scores

**Expected findings:**
- Pre-symptomatic: possible early biophoton changes (oxidative stress begins before clinical signs)
- Onset: increased total emission (inflammation) + beginning spectral shift
- Peak: maximal emission intensity, significant spectral shift, possible loss of photon correlations
- Chronic: reduced emission (inflammation resolved), persistent spectral shift (residual demyelination)

### 5.2 Ex Vivo: Optic Nerve Preparations

**Rationale:** The optic nerve is one of the most heavily myelinated structures in the CNS, with axon diameters of 0.2-5 micrometers and thick myelin sheaths (g-ratios of 0.6-0.8). It is surgically accessible, can be dissected intact, and can be maintained in physiological solution for hours. It is commonly affected in MS and EAE. Importantly, the optic nerve has no cell bodies -- only axons and glia -- which simplifies interpretation of biophoton signals.

**Protocol outline:**
1. Dissect optic nerves from normal and EAE mice under dim red light
2. Mount in a perfusion chamber with oxygenated artificial CSF at 37 degrees C
3. Apply electrical stimulation (compound action potential) via suction electrode at one end
4. Measure biophoton emission using:
   - Cooled EM-CCD camera (Hamamatsu ImagEM X2) for spatial imaging
   - PMT (Hamamatsu H7421-40) for photon counting and temporal analysis
   - Bandpass filter wheel (350, 450, 550, 634, 703, 800 nm) for spectral analysis
5. Record: (a) photon count rate vs. stimulation, (b) spatial emission profile, (c) spectral composition

**Controls:**
- Contralateral optic nerve from EAE animal (may be unaffected or less affected)
- Optic nerves from age-matched non-immunized controls
- Unstimulated nerve (baseline emission)
- Nerve in calcium-free solution (blocks synaptic/neural activity)
- Heat-killed nerve (no biological activity; establishes autofluorescence baseline)

### 5.3 Cuprizone Model: Toxic Demyelination

**Model:** Feeding mice 0.2-0.3% cuprizone (bis-cyclohexanone oxaldihydrazone) in powdered chow produces reproducible, non-immune-mediated demyelination of the corpus callosum and other white matter tracts.

**Rationale:** Unlike EAE, the cuprizone model produces demyelination through direct oligodendrocyte toxicity (mitochondrial injury and oxidative stress) without T-cell-mediated inflammation. This allows isolation of the demyelination signal from the inflammatory signal. The timeline is highly predictable:

| Time Point | Pathological State | Predicted Biophoton Change |
|-----------|-------------------|---------------------------|
| Week 0 | Normal myelin | Baseline measurement |
| Week 1-2 | Oligodendrocyte stress, myelin intact | Increased emission (mitochondrial ROS) |
| Week 3 | Microglial activation, early demyelination | Rising emission + beginning spectral shift |
| Week 4-5 | Active demyelination and debris clearance | Peak emission; significant spectral shift |
| Week 6 | Near-complete corpus callosum demyelination | Reduced emission (less substrate); maximal spectral shift |
| Week 7-8 (off cuprizone) | Active remyelination | Emission normalizing; spectral shift partially reversing |
| Week 10-12 (off cuprizone) | Substantial remyelination (thin sheaths) | Near-baseline emission; persistent intermediate spectral shift |

**Protocol advantage:** The cuprizone model allows longitudinal within-animal comparisons because corpus callosum can be measured through a cranial window. Serial biophoton measurements on the same animal at weekly intervals would provide the first direct observation of biophoton changes tracking demyelination and remyelination in real time.

### 5.4 Lysolecithin Injection: Focal Demyelination

**Model:** Direct injection of lysolecithin (lysophosphatidylcholine, LPC) into a nerve produces focal demyelination at the injection site with a well-defined lesion boundary.

**Rationale:** LPC creates a spatially circumscribed demyelinated lesion with a sharp border between normal and demyelinated tissue. This is ideal for testing the spatial predictions of the waveguide model (bright emission at boundaries, dark in demyelinated zones). The timeline is well-characterized:

- Days 1-3: Active demyelination at injection site
- Days 3-7: OPC (oligodendrocyte precursor cell) recruitment
- Days 7-10: Oligodendrocyte differentiation
- Days 10-21: Active remyelination

**Protocol for optic nerve:**
- LPC injection (1% in saline) via glass micropipette 2 mm posterior to the globe
- Serial ex vivo measurements at days 3, 7, 14, 21
- Spatial mapping of emission along nerve length to locate lesion boundary

**Protocol for sciatic nerve (PNS):**
- Topical application of LPC (15 mg/mL) to exposed saphenous nerve
- Advantage: peripheral nerve accessible for non-invasive measurement through skin in vivo
- Potential for longitudinal measurements in living animal

### 5.5 Controls and Confounds

Rigorous experimental design requires addressing the following confounds:

**Biological controls:**
- Contralateral nerve (within-animal control for systemic effects)
- Pre-treatment baseline (within-animal temporal control)
- Age-matched naive controls (between-animal control)
- Sham surgery controls (for lysolecithin experiments: vehicle injection without LPC)

**Technical controls:**
- Dark counts: detector measurements with no sample (electronic noise baseline)
- Autofluorescence: fixed tissue measurements (no active metabolism)
- Chemiluminescence blanks: solution-only measurements (chamber and media contribution)
- Stimulation artifacts: electrical stimulation of dead nerve (electrode emission)

**Pharmacological controls:**
- Antioxidant pre-treatment (e.g., N-acetylcysteine): should reduce oxidative stress-derived emission while leaving waveguide-derived emission unchanged
- Tetrodotoxin (TTX): blocks action potentials, eliminating activity-dependent emission while leaving basal emission
- FCCP (mitochondrial uncoupler): maximizes mitochondrial ROS production as positive control for oxidative emission

### 5.6 Detection Technology

**Recommended primary detector:** Cooled EM-CCD camera (e.g., Hamamatsu ImagEM X2 or Andor iXon Ultra 897)
- Single-photon sensitivity with > 90% quantum efficiency at 500-700 nm
- Spatial resolution (512 x 512 pixels) for mapping emission along nerve
- Cooling to -100 degrees C for negligible dark current
- Integration times of 10-60 minutes per measurement

**Recommended secondary detector:** PMT module (e.g., Hamamatsu H7421-40)
- Single-photon counting mode for temporal analysis
- Time resolution < 1 ns for correlation measurements
- Paired with bandpass filters for spectral discrimination

**For quantum correlation measurements:** Two matched SPADs (single-photon avalanche diodes) in Hanbury Brown-Twiss configuration
- Coincidence window ~10 ns
- Required count rate for meaningful statistics: > 100 coincidences per measurement
- This likely requires integration times of hours with current technology

---

## 6. Research Opportunities

### 6.1 Biophoton Emission as Non-Invasive Biomarker for MS Disease Activity

**The clinical need:** MS diagnosis currently relies on MRI (gadolinium-enhancing lesions for active inflammation) and clinical assessment. No biomarker can non-invasively assess myelin integrity in real time. Neurofilament light chain (NfL) in serum reflects axonal damage but not specifically myelin status. Myelin water imaging (MWI-MRI) provides myelin-specific information but requires expensive scanning sessions and has limited temporal resolution.

**The biophoton opportunity:** If biophoton emission from neural tissue changes measurably with demyelination (as the waveguide model predicts), then biophoton detection could provide:
- Real-time assessment of disease activity (emission intensity tracking inflammation)
- Myelin-specific information (spectral shift reflecting structural damage)
- Monitoring capability over continuous timescales (wearable detector concept)

**Development pathway:** Animal model validation -> ex vivo human tissue studies -> transcranial measurement feasibility -> clinical pilot studies.

**Key challenge:** Transcranial detection of biophotons. The skull and scalp are strong attenuators of visible light. However, near-infrared wavelengths (700-1000 nm) penetrate tissue more effectively, and the singlet oxygen emission at 1270 nm falls in the "optical window" where tissue is relatively transparent. Fiber-optic probes placed in surgical burr holes (already used for intracranial pressure monitoring in MS patients with acute attacks) could provide a nearer-term measurement route.

### 6.2 Monitoring Remyelination Therapies via Biophoton Spectral Changes

**The clinical need:** Multiple remyelination-promoting therapies are in clinical trials (clemastine, opicinumab, bexarotene, others). The primary challenge in these trials is measuring whether remyelination has actually occurred. Current methods require serial MRI with advanced sequences (magnetization transfer ratio, myelin water fraction) or postmortem histology.

**The biophoton opportunity:** If remyelinated myelin produces a distinct spectral signature (section 3.1.4) -- blueshifted relative to normal myelin but redshifted relative to demyelinated tissue -- then biophoton spectroscopy could serve as a pharmacodynamic biomarker for remyelination trials:
1. Baseline measurement at trial entry (demyelinated signature)
2. Serial measurements during treatment
3. Track spectral shift back toward normal (remyelination)
4. Detect incomplete remyelination (persistent intermediate shift due to thinner myelin)

**Advantages over existing methods:**
- Temporal resolution: potentially continuous vs. periodic MRI scans
- Specificity: spectral shift is directly tied to myelin structure, not inferred from water content or magnetization
- Cost: photon detection hardware is orders of magnitude cheaper than MRI

### 6.3 Early Detection Before Clinical Symptoms

**The clinical need:** In MS, significant axonal loss (estimated 30-60% of axons in some tracts) occurs before the first clinical relapse. In Krabbe disease and some leukodystrophies, irreversible damage occurs before diagnosis. Early detection would enable prophylactic treatment.

**The biophoton opportunity:** The oxidative stress predictions (section 3.2) suggest that biophoton emission may increase before structural demyelination occurs, as the initial immune attack or toxic insult generates ROS before myelin is visibly damaged. This "photonic prodrome" could precede clinical symptoms by days to weeks.

**Evidence from existing data:** Wang et al. (2023) demonstrated reduced biophotonic activities in Alzheimer's disease and vascular dementia models -- conditions where white matter damage precedes clinical diagnosis by years. If similar early changes occur in demyelinating disease, biophoton monitoring could provide the earliest possible warning.

### 6.4 Distinguishing Demyelination from Axonal Degeneration

**The clinical need:** Demyelination and axonal degeneration often co-occur (e.g., in progressive MS) but have different therapeutic implications. Demyelination is potentially reversible (remyelination); axonal loss is not. Currently, distinguishing them requires histopathology or indirect biomarkers (NfL for axonal damage, MWI for myelin).

**The biophoton opportunity:** The waveguide and oxidative models predict distinct signatures for each process:

| Feature | Demyelination | Axonal Degeneration |
|---------|--------------|-------------------|
| Spectral shift | Yes (blueshift per layer lost) | No (axon loss removes emitter, not waveguide) |
| Total intensity (early) | Increased (inflammation + scattering) | Decreased (fewer emitting axons) |
| Singlet O2 peaks | Prominent (lipid peroxidation of myelin) | Reduced (myelin lipid not primary target) |
| Spatial pattern | Patchy (demyelinated lesions) | Diffuse (tract-wide axon loss) |
| Response to remyelination therapy | Spectral shift reverses | No change |

This differential signature could be validated in animal models using EAE (predominantly demyelinating) vs. Wallerian degeneration (axonal + secondary myelin loss) and could eventually inform clinical decision-making.

### 6.5 Fundamental Neuroscience: Myelin as Optical Component

Beyond clinical applications, biophoton measurements in demyelinating disease address a fundamental question in neuroscience: does myelin have an optical function?

If demyelination measurably alters biophoton transmission, it would provide the strongest evidence yet that myelin serves as an optical waveguide in vivo -- not merely a passive electrical insulator. This would transform our understanding of myelin biology and potentially reveal a new dimension of neural signaling disrupted in demyelinating disease.

---

## 7. Key References

### Waveguide Models and Biophoton Propagation

1. **Zeng H, Zhang Y, Ma Y, Li S** (2022). "Electromagnetic modeling and simulation of the biophoton propagation in myelinated axon waveguide." *Applied Optics* 61(14):4013-4021.
   - Establishes the 52.3 nm/layer wavelength shift rule. Demonstrates that the myelinated axon waveguide operates in a narrow ~10 nm bandwidth. Key source for quantitative predictions of demyelination-induced spectral changes.

2. **Kumar S, Boone K, Tuszynski J, Barclay P, Simon C** (2016). "Possible existence of optical communication channels in the brain." *Scientific Reports* 6:36508.
   - Foundational FDTD modeling paper. Uses Lumerical to simulate photon propagation in myelinated axons with realistic geometry (refractive indices: myelin 1.44, axon 1.38, fluid 1.34). Shows that myelin supports guided modes at visible and near-IR wavelengths.

3. **Maghoul A, Khaleghi A, Balasingham I** (2021). "Engineering photonic transmission inside brain nerve fibers." *IEEE Access* 9:35399-35410.
   - Extended waveguide analysis including effects of nodes of Ranvier as discontinuities. Directly relevant to modeling the additional scattering discontinuities created by demyelination.

4. **Liu H, Liu R, Li S** (2022). "Simulation of nerve fiber based on anti-resonant reflecting optical waveguide." *Scientific Reports* 12:18762.
   - ARROW (anti-resonant reflecting optical waveguide) model of myelin. Demonstrates an alternative waveguiding mechanism where myelin layers act as Fabry-Perot reflectors. Important because ARROW behavior has different predictions for thin/thick myelin than total internal reflection models.

5. **Chen M, Ren QS** (2023). "Optical polarization evolution and transmission in multi-Ranvier-node axonal myelin-sheath waveguides." *bioRxiv* 2023.03.30.534951.
   - Models polarization-dependent transmission through multiple myelinated segments. Relevant to understanding how fragmentation (additional "nodes") affects total transmission.

### Quantum Optics in Myelin

6. **Liu Z, Chen X, et al.** (2024). "Entangled biphoton generation in the myelin sheath." *Physical Review E* 110:024402.
   - Demonstrates theoretically that myelin cavities can generate entangled photon pairs from C-H bond vibrations via cavity QED. Shows thickness-dependent entanglement peaking at g-ratio ~0.7-0.8. Directly predicts that demyelination should reduce entangled photon production.

### Biophoton Detection and Neural Activity

7. **Zangari A, Micheli D, Galeazzi R, Lucarini A** (2021). "Photons detected in the active nerve by photographic technique." *Scientific Reports* 11:3022.
   - Experimental detection of photon emission at nodes of Ranvier during electrically stimulated nerve activity using silver photoreduction. Key empirical evidence that myelinated nerves emit detectable photons during activity.

8. **Tang R, Dai J** (2014). "Spatiotemporal imaging of glutamate-induced biophotonic activities and transmission in neural circuits." *PLoS ONE* 9(1):e85643.
   - Demonstrates glutamate-induced biophoton emission in brain slices, with evidence for photon transmission along neural pathways. Establishes the experimental paradigm for stimulating and measuring neural biophoton emission.

9. **Chen L, Wang Z, Dai J** (2020). "Spectral blueshift of biophotonic activity and transmission in the ageing mouse brain." *Brain Research* 1749:147133.
   - Documents age-dependent spectral blueshift of brain biophoton emission. Aging involves progressive myelin thinning, making this an indirect observation consistent with the waveguide model's predictions for demyelination-induced spectral change.

10. **Wang Z, et al.** (2023). "Reduced biophotonic activities and spectral blueshift in Alzheimer's disease and vascular dementia models with cognitive impairment." *Frontiers in Aging Neuroscience* 15:1208274.
    - Shows that neurodegenerative disease models (with white matter pathology) have reduced biophoton emission and spectral blueshift. The most direct existing evidence linking neurodegeneration-associated myelin changes to altered biophoton signatures.

### Oxidative Stress and Biophoton Emission

11. **Cifra M, Pospisil P** (2014). "Ultra-weak photon emission from biological samples: definition, mechanisms, properties, detection and applications." *Journal of Photochemistry and Photobiology B: Biology* 139:2-10.
    - Comprehensive review of biophoton emission mechanisms including lipid peroxidation pathways, ROS-derived excited species, and their spectral characteristics. Essential background for the oxidative stress predictions.

12. **Yadav DK, Pospisil P** (2012). "Role of reactive oxygen species in ultra-weak photon emission in biological systems." *Journal of Photochemistry and Photobiology B: Biology* 113:78-83.
    - Details the specific ROS pathways (Russell mechanism, dioxetane decomposition) that generate photon-emitting species. Provides the spectral assignments: triplet carbonyls at 350-550 nm, singlet oxygen at 634/703/1270 nm.

13. **Prasad A, Balukova A, Pospisil P** (2022). "Imaging of lipid peroxidation-associated chemiluminescence in plants: spectral features, regulation and origin of the signal in leaves and roots." *Antioxidants* 11(7):1333.
    - Detailed spectral analysis of lipid peroxidation-derived photon emission. Although in plant tissue, the underlying photochemistry (Russell mechanism, singlet oxygen) is identical to what occurs during myelin peroxidation.

### Demyelinating Disease Models

14. **Matsushima GK, Morell P** (2001). "The neurotoxicant, cuprizone, as a model to study demyelination and remyelination in the central nervous system." *Brain Pathology* 11(1):107-116.
    - Standard reference for the cuprizone model. Details the timeline of oligodendrocyte death, demyelination, and remyelination. Essential for designing the longitudinal biophoton measurement experiments.

15. **Kipp M, Clarner T, Dang J, Copray S, Beyer C** (2009). "The cuprizone animal model: new insights into an old story." *Acta Neuropathologica* 118(6):723-736.
    - Updated review of cuprizone model mechanisms, emphasizing the role of oxidative stress (mitochondrial superoxide, reduced SOD/GSH) in oligodendrocyte death. Relevant to predicting the oxidative biophoton signature.

16. **Jeffery ND, Blakemore WF** (1995). "Remyelination of mouse spinal cord axons demyelinated by local injection of lysolecithin." *Journal of Neurocytology* 24(10):775-781.
    - Characterizes the LPC focal demyelination model with detailed spatial and temporal analysis. Essential reference for the focal demyelination experimental design.

17. **Najm FJ, Bhatt DK, et al.** (2021). "An optimized animal model of lysolecithin induced demyelination in optic nerve." *Journal of Neuroscience Methods* 352:109083.
    - Optimized protocol for LPC-induced optic nerve demyelination in mice. Directly applicable to the proposed experimental design.

18. **Constantinescu CS, Farooqi N, O'Brien K, Gran B** (2011). "Experimental autoimmune encephalomyelitis (EAE) as a model for multiple sclerosis (MS)." *British Journal of Pharmacology* 164(4):1079-1106.
    - Comprehensive review of EAE models including MOG-induced, PLP-induced, and adoptive transfer variants. Essential for selecting the appropriate model for biophoton studies.

### Remyelination Biology

19. **Duncan ID, Brower A, Kondo Y, Curlee JF, Schultz RD** (2009). "Extensive remyelination of the CNS leads to functional recovery." *Proceedings of the National Academy of Sciences* 106(16):6832-6836.
    - Demonstrates that remyelination restores function. The key finding for biophoton relevance: remyelinated sheaths remain thinner than normal, producing a permanent structural alteration detectable by waveguide-sensitive measurements.

20. **Duncan ID, Radcliff AB, Heidari M, Kidd G, August BK, Bhatt D** (2017). "Thin myelin sheaths as the hallmark of remyelination persist over time and preserve axon function." *Proceedings of the National Academy of Sciences* 114(45):E9685-E9691.
    - Demonstrates that thin remyelinated sheaths persist for over 2 years without thickening. This means the biophoton spectral signature of remyelination (intermediate blueshift) should be a permanent, detectable feature.

### MS Pathology and Biomarkers

21. **Lassmann H** (2018). "Multiple sclerosis pathology." *Cold Spring Harbor Perspectives in Medicine* 8(3):a028936.
    - Authoritative review of MS neuropathology: lesion types, shadow plaques, cortical demyelination, diffuse white matter damage. Essential context for relating biophoton predictions to actual disease pathology.

22. **Kaunzner UW, Gauthier SA** (2017). "MRI in the assessment and monitoring of multiple sclerosis: an update on best practice." *Therapeutic Advances in Neurological Disorders* 10(6):247-261.
    - Reviews current MS imaging biomarkers and their limitations, establishing the clinical need for new biomarker approaches.

### Foundational Biophoton Reviews

23. **Rahnama M, Tuszynski JA, Bokkon I, Cifra M, Sardar P, Salari V** (2011). "Emission of mitochondrial biophotons and their effect on electrical activity of membrane via microtubules." *Journal of Integrative Neuroscience* 10(1):65-88.
    - Reviews the connection between mitochondrial oxidative metabolism, biophoton generation, and neural membrane activity. Provides the theoretical basis for linking metabolic changes in demyelination to photon emission changes.

24. **Salari V, Valian H, Bassereh H, Bokkon I, Barkhordari A** (2015). "Ultraweak photon emission in the brain." *Journal of Integrative Neuroscience* 14(3):419-429.
    - Reviews evidence for biophoton emission in neural tissue and its potential functional significance. Sets the context for why demyelination-induced changes would be biologically meaningful.

---

## 8. Computational Disease Models

The following computational models implement the theoretical framework of Sections 3-4 in working Python code. All code is in `worktrees/track-06/src/` and can be run standalone.

### 8.1 Demyelination Progression Model

We implement the parametric waveguide model (Section 4.1) with three pathological parameters evolving as sigmoid functions of time:

- **Thickness factor** alpha(t): Myelin thickness remaining, modelled as logistic decay
- **Continuity factor** gamma(t): Fraction of internode with intact myelin
- **Regularity factor** rho(t): Uniformity of remaining myelin structure

These drive the waveguide observables:

```
n_eff(alpha, rho) = n_ECF + alpha * rho * (n_myelin - n_ECF)
lambda_op(alpha) = lambda_healthy - (1 - alpha) * N_layers * 52.3 nm
alpha_prop = alpha_0 / (alpha * gamma * rho) + L_junction * (1 - gamma) / l_internode
```

The coherence field Lambda is governed by the M-Phi ODE:

```
dLambda/dt = g * |Psi|^2 * Phi  -  kappa(t) * Lambda
```

where kappa(t) increases as myelin degrades (kappa scales as 1/alpha^2 reflecting the structural decoherence mechanism).

**Key finding:** Over a 20-week progressive demyelination timeline, Lambda decays from 1.0 to approximately 0.02 -- a 50-fold reduction in coherence. The initial decay is slow (weeks 0-5 while alpha is still near 1) but accelerates dramatically once myelin integrity drops below ~0.5, due to the quadratic dependence of kappa on myelin loss.

### 8.2 MS Subtype Models

Three distinct temporal patterns are modelled:

**RRMS (Relapsing-Remitting):**
Relapses are generated as a Poisson process (mean 1/year) with each relapse causing 15% loss of remaining myelin over 6 weeks, followed by 85% recovery. The net effect is a sawtooth decline: by year 20, myelin integrity reaches approximately 0.40-0.55 depending on relapse timing. The biophoton signature shows sharp emission spikes during relapses (inflammation) with spectral blueshift accumulating stepwise.

**SPMS (Secondary Progressive):**
Starting from a post-RRMS baseline of ~65% myelin integrity, the model applies 3% annual exponential decay with chronic low-grade inflammation. By year 15, myelin drops to ~0.40. The biophoton signature is characterized by a steady spectral drift without the sharp emission spikes of RRMS -- a distinguishing feature.

**PPMS (Primary Progressive):**
Starting from full myelin, 4% annual exponential decay with minimal inflammation. The biophoton signature shows gradual spectral blueshift and slowly declining coherence without inflammatory emission spikes. PPMS produces the most monotonic trajectory, making it the easiest subtype to distinguish from RRMS by temporal pattern analysis.

### 8.3 Kappa Decomposition Model

The decoherence rate kappa is decomposed into four physically motivated components:

| Component | Mechanism | Healthy Value | Dependence |
|-----------|-----------|---------------|------------|
| kappa_thermal | Thermal fluctuations at body temperature | 0.02 s^-1 | Arrhenius with E_a/k_B ~ 4000 K |
| kappa_structural | Scattering from myelin disorder | 0.01 s^-1 | 1/m^2 (diverges as myelin disappears) |
| kappa_ROS | Oxidative damage to chromophores | 0.01 s^-1 | Linear with ROS concentration |
| kappa_inflammatory | Cytokine-driven disruption | ~0 s^-1 | Hill function (K=0.3, n=2) |
| **Total (healthy)** | | **0.04 s^-1** | |

Disease-state results:

| Scenario | kappa_total (s^-1) | Lambda_ss | Fold increase in kappa |
|----------|-------------------|-----------|----------------------|
| Healthy | 0.040 | 0.0250 | 1.0x |
| Mild (early MS) | 0.208 | 0.0048 | 5.2x |
| Moderate (active MS) | 0.499 | 0.0020 | 12.5x |
| Severe (late MS) | 0.411 | 0.0024 | 10.3x |
| Acute relapse | 0.661 | 0.0015 | 16.5x |

The dominant contributor shifts with disease stage: structural disorder dominates in severe chronic disease (kappa_structural ~ 0.11 at 30% myelin integrity), while inflammatory decoherence dominates during acute relapses (kappa_inflammatory ~ 0.35 at inflammation level 0.9).

### 8.4 Biomarker Diagnostic Performance

Five candidate biomarkers were evaluated using simulated measurement distributions at five disease stages:

1. **Photon count** (total emission intensity)
2. **Spectral shift** (peak wavelength blueshift)
3. **SO2/carbonyl ratio** (singlet oxygen vs triplet carbonyl emission)
4. **g^(2)(0)** (second-order photon correlation)
5. **Combined score** (z-score composite of all four)

ROC analysis reveals a hierarchy of diagnostic sensitivity:

- **Most sensitive early:** SO2/carbonyl ratio and photon count detect preclinical changes (AUC > 0.6 at 5% myelin loss) due to inflammatory amplification.
- **Most specific:** Spectral shift provides the most direct readout of myelin structural damage, achieving AUC > 0.9 at moderate disease.
- **Least sensitive:** g^(2)(0) requires substantial demyelination (>30% loss) for reliable detection, but is the most theoretically specific marker of myelin cavity integrity.
- **Best overall:** The combined multi-parameter score achieves AUC > 0.8 at moderate disease stages, outperforming any single biomarker by leveraging complementary information.

### 8.5 Experimental Protocol Predictions

Quantitative predictions for three proposed experiments:

**EAE Model (Optic Nerve):**

| Time Point | Predicted Emission (ph/s/cm^2) | Fold Change | SNR (1h) |
|------------|-------------------------------|-------------|----------|
| Baseline | 10.0 | 1.0x | 180 |
| Pre-symptomatic (day 7) | 111.0 | 11.1x | 598 |
| Onset (day 10-12) | 515.0 | 51.5x | 1288 |
| Peak (day 14-18) | 927.5 | 92.8x | 1729 |
| Chronic (day 28+) | 172.5 | 17.3x | 746 |

The peak-to-baseline ratio of ~93x during maximal EAE inflammation should be readily detectable with standard single-photon counting equipment.

**Cuprizone Model (Corpus Callosum):**
Peak emission at week 6 (85% demyelination): 542.5 ph/s/cm^2 (54x baseline). Remyelination (week 12) reduces emission to 172.5 ph/s/cm^2 but with persistent spectral shift reflecting thinner remyelinated sheaths.

**Sample Size Requirements:**
For the primary comparison (moderate demyelination, combined score, Cohen's d ~ 1.0): n = 10 per group achieves 80% power. For early detection (d ~ 0.3): n = 90 per group is required. The cuprizone repeated-measures design needs only n = 12 per group due to within-subject pairing.

---

## 9. Testable Predictions Summary

The computational models generate the following hierarchy of predictions, ordered from most to least testable with current technology:

### Tier 1: Testable Now (ex vivo, animal models)

1. **Active demyelination increases total biophoton emission 10-100x** due to lipid peroxidation. Detectable with standard PMT/EM-CCD in ex vivo nerve preparations from EAE or cuprizone-treated animals.

2. **Emission intensity correlates with histological demyelination score.** Within the same EAE cohort, animals with higher Luxol Fast Blue scores should show lower steady-state emission and greater spectral blueshift.

3. **Cuprizone-induced demyelination produces a characteristic temporal emission profile** (rise during active demyelination, peak at week 6, partial recovery during remyelination) distinguishable from the EAE inflammatory spike pattern.

4. **Antioxidant pre-treatment (NAC) reduces the inflammatory emission component** without affecting the structural spectral shift, confirming two independent emission mechanisms.

### Tier 2: Testable with Specialized Equipment

5. **Spectral blueshift of ~52.3 nm per lost myelin layer** during demyelination, measurable with bandpass filter-equipped PMT or spectrometer. Shadow plaques (remyelinated areas) should show intermediate spectral signatures.

6. **Singlet oxygen emission peaks (634/703 nm) are elevated in autoimmune demyelination** (EAE) relative to toxic demyelination (cuprizone), reflecting MPO activity.

7. **Spatial emission mapping reveals bright spots at demyelination boundaries** in LPC-treated nerves, consistent with waveguide scattering predictions.

### Tier 3: Requires Advanced Quantum Optics

8. **g^(2)(0) > 1 (photon bunching) in healthy myelinated nerve** decreasing toward g^(2)(0) ~ 1 in demyelinated nerve, reflecting loss of entangled pair production in degraded myelin cavities.

9. **Coincidence rates in HBT measurements** correlate with myelin thickness (g-ratio) across different axon populations within the same nerve.

### Tier 4: Long-term Clinical Applications

10. **Transcranial biophoton detection** reveals MS lesion load through the skull, potentially via near-IR (1270 nm singlet oxygen) emission through the optical window.

11. **Wearable biophoton detector** provides continuous monitoring of MS disease activity, with emission spikes predicting clinical relapses days to weeks in advance.
