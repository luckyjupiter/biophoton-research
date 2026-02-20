# Annotated Bibliography: Biophoton Research in Myelin Sheaths

> Compiled February 2026. Relevance ratings reflect importance to the specific
> research program of understanding biophotonic signaling in myelinated neural
> tissue. Research tracks referenced:
>
> - **Track 1** -- Waveguide physics of myelin
> - **Track 2** -- Biophoton sources and detection in neural tissue
> - **Track 3** -- Quantum information processing in biological substrates
> - **Track 4** -- Time-series analysis and statistical characterization of UPE
> - **Track 5** -- Functional role of biophotons in cognition and learning

---

## 1. Foundational Biophoton Science

### 1.1 Popp, F.A., Nagl, W., Li, K.H., Scholz, W., Weingartner, O., & Wolf, R. (1984). "Biophoton emission. New evidence for coherence and DNA as source." *Cell Biophysics*, 6(1), 33--52. DOI: [10.1007/BF02788579](https://doi.org/10.1007/BF02788579)

**[Essential] -- Tracks 2, 3, 4**

This is the paper that coined the term "biophoton" and established the field. Popp
and colleagues presented evidence that ultra-weak photon emission from living cells
exhibits a high degree of coherence, based on photon count statistics, spectral
distribution, and decay behavior after illumination. They proposed DNA as a
primary source, modeling it as an exciplex laser system reaching a stable state
far from thermal equilibrium. The coherence claims were influential but have been
disputed by later statistical analyses (see Cifra et al. 2015 below). This paper
remains the essential starting point for anyone entering the field, defining both the
phenomenon and the core theoretical controversy (coherent field vs. stochastic
by-product) that persists to this day.

---

### 1.2 Popp, F.A., Li, K.H., & Gu, Q. (Eds.) (1992). *Recent Advances in Biophoton Research and Its Applications*. World Scientific, Singapore. ISBN: 978-981-02-0855-4

**[Important] -- Tracks 2, 4**

This edited volume collects articles covering the historical background of biophoton
research, the physics of biophoton emission, biological phenomena showing "holistic"
character, and applications. It serves as the most comprehensive snapshot of the
field's state in the early 1990s, consolidating work that was previously scattered
across disparate journals. Popp's chapters articulate the theoretical framework of
a coherent biophoton field governing intra- and inter-cellular regulation. The
volume is now dated in its experimental methods but remains valuable for its
theoretical formulations and for understanding the intellectual genealogy of the
field.

---

### 1.3 Cifra, M. & Pospisil, P. (2014). "Ultra-weak photon emission from biological samples: Definition, mechanisms, properties, detection and applications." *Journal of Photochemistry and Photobiology B: Biology*, 139, 2--10. DOI: [10.1016/j.jphotobiol.2014.02.009](https://doi.org/10.1016/j.jphotobiol.2014.02.009)

**[Essential] -- Tracks 2, 4**

A rigorous review that defines UPE, catalogs the molecular mechanisms generating
it (ROS-mediated lipid peroxidation, protein oxidation, nucleic acid oxidation),
and surveys detection technologies. The authors establish that electronically
excited species -- triplet excited carbonyls (350--550 nm), excited pigments
(550--1000 nm), and singlet oxygen (634, 703, 1270 nm) -- are responsible for
emission across the near-UV to near-IR range at intensities of tens to thousands
of photons/s/cm^2. This paper is essential reading because it provides the
mechanistic grounding for biophoton generation that any waveguide or quantum
model must be consistent with. Its limitation is that it does not address
neural-specific emission or waveguide contexts.

---

### 1.4 Mould, R.R., Mackenzie, A.M., Sherlock-Mayston, I., Sherlock-Mayston, P., Sherlock-Mayston, J., Kalampouka, I., Sherlock-Mayston, A., Nunn, A.V.W., Thomas, E.L., Bell, J.D., & Botchway, S.W. (2024). "Ultra weak photon emission -- a brief review." *Frontiers in Physiology*, 15, 1348915. DOI: [10.3389/fphys.2024.1348915](https://doi.org/10.3389/fphys.2024.1348915)

**[Important] -- Tracks 2, 4**

An up-to-date narrative review that covers UPE definitions, ROS-based generation
mechanisms, detection technologies (PMTs, CCDs, SPAD arrays), and emerging
applications in food quality, clinical diagnostics, and aging research. The
authors note Cifra's important caveat that for UPE to serve as an information
carrier, cells must be able to generate, detect, and sense specific properties
of the emission -- for which concrete evidence remains limited. This review
is valuable as a 2024 entry point to the broader UPE literature, though it
does not focus specifically on neural tissue. It is complementary to Cifra &
Pospisil (2014) with updated references.

---

### 1.5 Cifra, M., Brouder, C., Nerudova, M., & Kucera, O. (2015). "Biophotons, coherence and photocount statistics: A critical review." *Journal of Luminescence*, 164, 38--51. DOI: [10.1016/j.jlumin.2015.03.020](https://doi.org/10.1016/j.jlumin.2015.03.020). arXiv: [1502.07316](https://arxiv.org/abs/1502.07316)

**[Essential] -- Tracks 3, 4**

This paper is the definitive critical examination of coherence claims in biophoton
research. Cifra and colleagues systematically reviewed papers claiming coherent
and squeezed states of biophotons and found that the published arguments and
data interpretations supporting these claims are incorrect or insufficient. They
identify specific statistical fallacies (e.g., sub-Poissonian statistics being
misinterpreted as evidence for coherence) and set rigorous standards for future
claims. This paper is essential because it defines what would actually constitute
evidence for quantum coherence in biophoton emission, directly informing
how any quantum model (Track 3) should be evaluated. Its limitation is that it
does not propose alternative interpretations for the non-trivial statistical
structure that has been observed.

---

### 1.6 Role of Reactive Oxygen Species in UPE Generation

**Key reference:** Pospisil, P., Prasad, A., & Rac, M. (2014). "Role of reactive oxygen species in ultra-weak photon emission in biological systems." *Journal of Photochemistry and Photobiology B: Biology*, 139, 11--23. DOI: [10.1016/j.jphotobiol.2014.02.008](https://doi.org/10.1016/j.jphotobiol.2014.02.008)

**[Important] -- Track 2**

This paper details the biochemical cascade from ROS generation (superoxide anion,
hydroxyl radical, singlet oxygen) through lipid peroxidation and protein oxidation
to the formation of electronically excited species that emit photons upon
relaxation to the ground state. The spectral signatures are mapped: triplet
carbonyls emit in near-UVA/blue-green (350--550 nm), singlet oxygen at 634 nm,
703 nm, and 1270 nm. For the myelin waveguide program, this is critical because
it constrains which wavelengths a biological source can actually produce in
neural tissue, and therefore which waveguide modes are physically relevant.
The limitation is that emission intensities in neural tissue specifically have
not been well characterized.

---

## 2. Neural Biophoton Hypothesis

### 2.1 Bokkon, I. (2008). "Phosphene phenomenon: A new concept." *BioSystems*, 92(2), 168--174. DOI: [10.1016/j.biosystems.2008.02.002](https://doi.org/10.1016/j.biosystems.2008.02.002)

**[Important] -- Tracks 2, 5**

Bokkon proposed that phosphenes (visual sensations in the absence of external
light) are caused by bioluminescent biophoton emission from cells in the visual
system, generated by ROS from mitochondrial and membrane processes. He argued
that biophotons are not mere metabolic by-products but are regulated by redox
processes and become conscious when emission exceeds a threshold. This paper
is historically important as the origin of the "visual imagery photon hypothesis"
that motivated much subsequent experimental work. Its weakness is that it is
largely speculative -- the proposed threshold mechanism and regulatory framework
lack direct experimental support, and alternative explanations for phosphenes
(retinal ganglion cell noise, cortical excitability) are well established.

---

### 2.2 Bokkon, I. (2009). "Visual perception and imagery: A new molecular hypothesis." *BioSystems*, 96(2), 178--184. DOI: [10.1016/j.biosystems.2009.01.005](https://doi.org/10.1016/j.biosystems.2009.01.005)

**[Supplementary] -- Track 5**

A refinement of Bokkon's 2008 hypothesis, proposing that retinotopic electrical
signals in V1 are converted into synchronized biophoton signals through redox
processes in cytochrome-oxidase-rich visual areas, creating "intrinsic biophysical
pictures." The paper develops quantitative estimates of biophoton numbers required
for visual perception. It remains speculative but provides testable predictions
that later experimental work (Dotta et al. 2012) attempted to address.

---

### 2.3 Dotta, B.T., Buckner, C.A., Lafrenie, R.M., & Persinger, M.A. (2012). "Increased photon emission from the head while imagining light in the dark is correlated with changes in electroencephalographic power: Support for Bokkon's biophoton hypothesis." *Neuroscience Letters*, 513(2), 151--154. DOI: [10.1016/j.neulet.2012.02.021](https://doi.org/10.1016/j.neulet.2012.02.021)

**[Important] -- Tracks 2, 5**

Using photomultiplier tubes positioned 15 cm from subjects' heads, Dotta et al.
measured a significant increase in UPE (~5 x 10^-11 W/m^2) from the right
hemisphere when 8 volunteers imagined white light in darkness, compared to
baseline or mundane thought conditions. UPE power correlated strongly (r = 0.95)
with simultaneous EEG spectral power changes. This is the most direct experimental
test of Bokkon's hypothesis and the correlation with EEG is striking. However, the
small sample size (N=8), the specificity to the right hemisphere (unexplained),
and the difficulty of replication by independent groups limit the conclusions.
The Persinger lab's broader body of work has faced methodological criticism.
Nevertheless, this paper demonstrates that task-dependent UPE from the human head
is detectable and merits further investigation with larger samples and improved
controls.

---

### 2.4 Sun, Y., Wang, C., & Dai, J. (2010). "Biophotons as neural communication signals demonstrated by in situ biophoton autography." *Photochemical & Photobiological Sciences*, 9(3), 315--322. DOI: [10.1039/b9pp00125e](https://doi.org/10.1039/b9pp00125e)

**[Essential] -- Tracks 1, 2**

Sun, Wang, and Dai developed in situ biophoton autography (IBA), a technique
using photosensitive film to detect photon emission in tissue, and applied it to
rat spinal nerve roots in vitro. They showed that light stimulation at one end
of a sensory or motor nerve root (using infrared, red, yellow, blue, green, or
white light) caused significantly increased biophotonic activity at the other end.
Crucially, this propagation was blocked by procaine (a neural conduction blocker)
and by metabolic inhibitors, indicating that the photon transmission depends on
active neural processes rather than passive light piping. This is one of the
strongest early pieces of evidence that biophotons can propagate along nerve
fibers and is directly relevant to the waveguide hypothesis. The limitation is
that the IBA technique provides spatial but not spectral information, and the
in vitro preparation may not reflect in vivo conditions.

---

### 2.5 Wang, Z., Wang, N., Li, Z., Xiao, F., & Dai, J. (2016). "Human high intelligence is involved in spectral redshift of biophotonic activities in the brain." *Proceedings of the National Academy of Sciences*, 113(31), 8753--8758. DOI: [10.1073/pnas.1604855113](https://doi.org/10.1073/pnas.1604855113)

**[Important] -- Tracks 1, 2, 5**

Using an ultraweak biophoton imaging system (UBIS) combined with a biophoton
spectral analysis device (BSAD), Wang et al. compared glutamate-induced biophotonic
emission across species (bullfrog, mouse, chicken, pig, monkey, human). They found
a systematic spectral redshift from shorter wavelengths in lower vertebrates toward
near-infrared (~865 nm) in human brain slices, and proposed this as a biophysical
basis for human high intelligence -- arguing that longer wavelengths enable more
efficient signal communication in neural tissue. The spectral data are valuable
for constraining waveguide models (Track 1), as they indicate that near-IR
wavelengths are the most relevant for human neural biophotonics. However, the
causal claim linking spectral redshift to intelligence was immediately criticized
(Salari et al. 2016 PNAS commentary noted correlation does not imply causation),
and the mechanism linking wavelength to information processing efficiency
remains unsubstantiated.

---

### 2.6 Tang, R. & Dai, J. (2014). "Spatiotemporal imaging of glutamate-induced biophotonic activities and transmission in neural circuits." *PLOS ONE*, 9(1), e85643. DOI: [10.1371/journal.pone.0085643](https://doi.org/10.1371/journal.pone.0085643)

**[Essential] -- Tracks 1, 2**

Tang and Dai developed an in vitro biophoton imaging method for mouse brain slices
and showed that glutamate application produces a gradual, significant increase in
biophotonic activity peaking at ~90 minutes and lasting over 200 minutes. This
activity was blocked by oxygen/glucose deprivation and by sodium azide (a
cytochrome c oxidase inhibitor), linking it to mitochondrial oxidative metabolism.
Most importantly, biophotonic activity detected in the corpus callosum and thalamus
in sagittal slices originated primarily from axons or axonal terminals of cortical
projection neurons, directly demonstrating biophotonic transmission along axonal
pathways. This paper provides the strongest direct evidence for biophoton
propagation through neural circuits and is essential for the waveguide program.
Its limitation is that the temporal dynamics (minutes to hours) are far slower
than neural signaling timescales (milliseconds), raising questions about
functional relevance.

---

### 2.7 Zangari, A., Micheli, D., Galeazzi, R., & Lucioli, A. (2021). "Photons detected in the active nerve by photographic technique." *Scientific Reports*, 11, 3022. DOI: [10.1038/s41598-021-82622-5](https://doi.org/10.1038/s41598-021-82622-5)

**[Essential] -- Tracks 1, 2**

Using an Ag+ photoreduction technique (analogous to photography), Zangari et al.
detected photon emission specifically at nodes of Ranvier during electrically
induced nerve activity in a dark environment. Silver deposition in tissue after
stimulation was identified under light microscopy, providing spatial localization
of photon sources. This is the first direct experimental detection of photons
at nodes of Ranvier during action potential propagation, confirming a key
prediction of the nanoantenna model (Zangari & Micheli 2018). The result is
essential for the waveguide program because it identifies nodes of Ranvier as
both photon sources and potential coupling points between internodal waveguide
segments. The limitation is that the photographic technique cannot provide
spectral, temporal, or intensity information, and the spatial resolution is
limited by the Ag deposition process.

---

## 3. Neural Waveguide Theory

### 3.1 Kumar, S., Boone, K., Tuszynski, J., Barclay, P., & Simon, C. (2016). "Possible existence of optical communication channels in the brain." *Scientific Reports*, 6, 36508. DOI: [10.1038/srep36508](https://doi.org/10.1038/srep36508)

**[Essential] -- Tracks 1, 3, 5**

This is the foundational paper for the neural waveguide hypothesis. Kumar et al.
performed detailed electromagnetic modeling of myelinated axons as optical
waveguides, incorporating realistic parameters for myelin sheath thickness,
refractive indices (myelin n ~ 1.44, axoplasm n ~ 1.38), and optical
imperfections including absorption, scattering from organelles, and bending
losses. They showed that myelinated axons could plausibly guide biophotons over
distances of millimeters to centimeters in the visible to near-IR range, with
transmission efficiencies sufficient for signaling at biologically relevant photon
rates. They proposed both in vivo and in vitro experiments and discussed
implications for quantum entanglement distribution. This paper opened an
entirely new research direction and remains the reference point for all
subsequent waveguide modeling. Its main limitation is the simplified cylindrical
geometry and the uncertainty in optical parameters of living myelin.

---

### 3.2 Kumar, S., Boone, K., Tuszynski, J., Barclay, P., & Simon, C. (2018). "Are there optical communication channels in the brain?" *Frontiers in Bioscience (Landmark Edition)*, 23(8), 1407--1421. DOI: [10.2741/4652](https://doi.org/10.2741/4652)

**[Important] -- Tracks 1, 3, 5**

This review paper expands on the 2016 Scientific Reports paper, providing a more
accessible and comprehensive discussion of the hypothesis, the waveguide modeling,
the required biophoton source rates, the detection mechanisms, and the potential
functional roles (including quantum communication). It surveys the experimental
evidence for biophoton emission in neural tissue and discusses the biological
plausibility of optical signaling. This is the best single review of the
waveguide hypothesis by its originators and is recommended as a second reading
after the 2016 paper. It acknowledges the speculative nature of the hypothesis
more explicitly than the original paper.

---

### 3.3 Zarkeshian, P., Kumar, S., Tuszynski, J., Bhatt, P., Bhatt, P., & Simon, C. (2022). "Photons guided by axons may enable backpropagation-based learning in the brain." *Scientific Reports*, 12, 20720. DOI: [10.1038/s41598-022-24871-6](https://doi.org/10.1038/s41598-022-24871-6)

**[Essential] -- Tracks 1, 3, 5**

Zarkeshian et al. propose a novel functional role for axonally guided biophotons:
enabling backpropagation-based learning. Standard backpropagation in artificial
neural networks requires backward transmission of error signals, which has been
considered biologically implausible because chemical synapses are unidirectional.
The authors argue that biophotons propagating backward through axonal waveguides
could carry error information from post-synaptic to pre-synaptic neurons. They
present updated waveguide simulations and discuss the required photon rates and
information capacity. This paper is important because it provides the first
concrete functional motivation for axonal photon waveguiding that connects to
mainstream computational neuroscience. The main limitation is that the proposed
mechanism requires photons to propagate bidirectionally in myelinated axons,
and the coupling efficiency at synaptic junctions is unknown.

---

### 3.4 Zarkeshian, P., Kumar, S., Tuszynski, J., & Simon, C. (2023). "Optical polarization evolution and transmission in multi-Ranvier-node axonal myelin-sheath waveguides." *bioRxiv* preprint. DOI: [10.1101/2023.03.30.534951](https://doi.org/10.1101/2023.03.30.534951). arXiv: [2304.00174](https://arxiv.org/abs/2304.00174)

**[Important] -- Tracks 1, 3**

This preprint addresses whether polarization-encoded information can survive
propagation through myelinated axons with multiple nodes of Ranvier -- a critical
question for both classical and quantum communication schemes. The simulations
show that optical polarization is well preserved through multiple nodes and
that transmission losses through successive nodes are approximately multiplicative
(rather than worse). These results are encouraging for quantum communication
proposals because polarization is a natural qubit encoding, and multiplicative
loss means that decoherence scales predictably with axon length. The paper
remains a preprint as of early 2026 and has not undergone full peer review.
The refractive index assumptions for the node of Ranvier region may need
refinement.

---

### 3.5 Omidi, M., Zibaii, M.I., & Granpayeh, N. (2022). "Simulation of nerve fiber based on anti-resonant reflecting optical waveguide." *Scientific Reports*, 12, 19356. DOI: [10.1038/s41598-022-23580-4](https://doi.org/10.1038/s41598-022-23580-4)

**[Important] -- Track 1**

This paper models myelinated axons as anti-resonant reflecting optical waveguides
(ARROWs), a well-studied structure in photonics where light is confined not by
total internal reflection but by anti-resonant reflection from thin layers. The
authors investigate effects of bending, myelin sheath thickness variation, and
the node of Ranvier on optical properties. The ARROW model predicts different
spectral transmission windows than the simple step-index waveguide model used
by Kumar et al. (2016), suggesting that wavelength selectivity is a key feature
of myelin waveguides. This paper is important because it introduces a more
physically realistic waveguide model, but its limitation is that the ARROW
regime requires specific relationships between myelin layer thickness and
wavelength that may not hold for all axon types.

---

### 3.6 Zeng, H., Zhang, Y., Ma, Y., & Li, S. (2022). "Electromagnetic modeling and simulation of the biophoton propagation in myelinated axon waveguide." *Applied Optics*, 61(14), 4013--4021. DOI: [10.1364/AO.457370](https://doi.org/10.1364/AO.457370)

**[Important] -- Track 1**

Zeng et al. built a multilayer electromagnetic simulation model of the myelinated
axon and found that it operates as a low-attenuation, low-dispersion waveguide
with a narrow operating bandwidth (~10 nm). They discovered a near-linear
relationship between operating wavelength and both axon diameter and number of
myelin layers, with each additional myelin layer shifting the operating wavelength
by 52.3 nm toward longer wavelengths. This result is significant because it
predicts that different axon types (varying in diameter and myelination) would
guide different wavelengths, potentially enabling wavelength-division multiplexing
in the brain. The limitation is that the model assumes idealized layer uniformity
and does not account for the Schmidt-Lanterman incisures or other structural
irregularities in real myelin.

---

### 3.7 Zangari, A. & Micheli, D. (2018). "Node of Ranvier as an array of bio-nanoantennas for infrared communication in nerve tissue." *Scientific Reports*, 8, 539. DOI: [10.1038/s41598-017-18866-x](https://doi.org/10.1038/s41598-017-18866-x)

**[Essential] -- Tracks 1, 2**

Zangari and Micheli modeled ion channel currents at the node of Ranvier as an
array of nanoantennas emitting electromagnetic radiation in the 300--2500 nm
range. Their calculations show that wavelengths below 1600 nm are most likely
to propagate through myelinated segments, and there is a broad spectral window
where both generation (by the nanoantenna array) and propagation (through the
myelin waveguide) are simultaneously possible. This paper is essential because
it provides a concrete physical model for biophoton generation at nodes of
Ranvier that is distinct from the ROS-based mechanisms, and it was experimentally
validated by the same group's 2021 photographic detection paper (Zangari et al.
2021). The main limitation is that the nanoantenna model treats ion channels
classically and does not account for the stochastic nature of channel opening.

---

### 3.8 Liu, X., Chang, Q., Bhatt, P., & Bhatt, P. (2019). "Myelin sheath as a dielectric waveguide for signal propagation in the mid-infrared to terahertz spectral range." *Advanced Functional Materials*, 29(10), 1807862. DOI: [10.1002/adfm.201807862](https://doi.org/10.1002/adfm.201807862)

**[Essential] -- Track 1**

Using synchrotron-radiation-based FTIR microspectroscopy, Liu et al. measured
the optical properties of myelin sheaths and found a ~2-fold higher refractive
index compared to both the outer medium and the inner axoplasm in the
mid-infrared to terahertz range (2.5--25 micrometers wavelength). They showed
that a myelin sheath of normal thickness (~2 micrometers) can confine infrared
field energy within the sheath and enable propagation at millimeter scales
without dramatic energy loss. This paper is essential because it provides the
first direct experimental measurement of myelin's dielectric properties in the
infrared/THz regime, demonstrating that myelin genuinely functions as a
waveguide at these wavelengths. The limitation is that the mid-IR/THz range
is distinct from the visible/near-IR biophoton emission window, so the
relevance to biophoton communication specifically requires extrapolation.

---

## 4. Quantum Models

### 4.1 Liu, Z., Chen, Y.-C., & Ao, P. (2024). "Entangled biphoton generation in the myelin sheath." *Physical Review E*, 110(2), 024402. DOI: [10.1103/PhysRevE.110.024402](https://doi.org/10.1103/PhysRevE.110.024402). arXiv: [2401.11682](https://arxiv.org/abs/2401.11682)

**[Essential] -- Tracks 1, 3**

Liu, Chen, and Ao applied cavity quantum electrodynamics to the myelin sheath,
treating it as a cylindrical optical cavity, and analyzed entangled biphoton
generation through cascade emission from C-H bond vibrations in lipid molecule
tails. They showed that the myelin cavity can enhance spontaneous photon emission
from vibrational modes and generate significant numbers of entangled photon pairs.
This is the most rigorous quantum-optical treatment of the myelin waveguide to
date, published in a mainstream physics journal (Physical Review E). Its
importance lies in providing a concrete, calculable mechanism by which myelin
could produce quantum-correlated photon pairs, potentially enabling quantum
information transfer between neurons. The key limitation is that the model
assumes idealized cavity conditions and does not address decoherence from
thermal fluctuations, water absorption, or structural disorder in real myelin.

---

### 4.2 Rahnama, M., Tuszynski, J.A., Bokkon, I., Cifra, M., Sardar, P., & Salari, V. (2011). "Emission of mitochondrial biophotons and their effect on electrical activity of membrane via microtubules." *Journal of Integrative Neuroscience*, 10(1), 65--88. DOI: [10.1142/S0219635211002622](https://doi.org/10.1142/S0219635211002622)

**[Important] -- Tracks 2, 3**

Rahnama et al. analyzed the interaction of mitochondria-generated biophotons
with microtubules from a quantum mechanical perspective, proposing that biophotons
cause transitions between coherent and incoherent states of microtubule dynamics.
They found a correspondence between the fluctuation function of microtubules and
alpha-EEG patterns, suggesting a link between biophoton-microtubule interactions
and brain rhythms. This paper bridges the Penrose-Hameroff microtubule
consciousness theory with the biophoton field and is relevant to quantum
processing models. Its main weaknesses are the highly speculative nature of
the quantum coherence claims for microtubules at biological temperatures and
the absence of direct experimental validation.

---

### 4.3 Popp, F.A., Chang, J.J., Herzog, A., Yan, Z., & Yan, Y. (2002). "Evidence of non-classical (squeezed) light in biological systems." *Physics Letters A*, 293(1--2), 98--102. DOI: [10.1016/S0375-9601(01)00832-5](https://doi.org/10.1016/S0375-9601(01)00832-5)

**[Supplementary] -- Track 3**

Popp and colleagues claimed to detect squeezed (sub-Poissonian) states of light
in biophoton emission using dual photomultiplier detection. They argued that
biological systems may exploit quantum squeezed states for regulation at ultra-weak
intensity levels where such states can exist. This paper was influential in
promoting the idea of quantum coherence in biophoton fields. However, the
squeezed light claims have been systematically refuted by Cifra et al. (2015),
who showed that the statistical analysis was flawed and the data do not support
the conclusions. This paper is included for historical completeness and as a
cautionary example -- it should not be cited uncritically as evidence for quantum
coherence in biophotons.

---

### 4.4 Davydov Soliton Theory

**Key references:**

- Davydov, A.S. (1973). "The theory of contraction of proteins under their excitation." *Journal of Theoretical Biology*, 38(3), 559--569. DOI: [10.1016/0022-5193(73)90256-7](https://doi.org/10.1016/0022-5193(73)90256-7)
- Davydov, A.S. (1977). "Solitons and energy transfer along protein molecules." *Journal of Theoretical Biology*, 66(2), 379--387. DOI: [10.1016/0022-5193(77)90178-3](https://doi.org/10.1016/0022-5193(77)90178-3)
- Davydov, A.S. (1979). "Solitons in molecular systems." *Physica Scripta*, 20(3--4), 387--394. DOI: [10.1088/0031-8949/20/3-4/013](https://doi.org/10.1088/0031-8949/20/3-4/013)
- Scott, A.C. (1992). "Davydov's soliton revisited." *Physica D*, 51(1--3), 333--342. DOI: [10.1016/0167-2789(91)90243-3](https://doi.org/10.1016/0167-2789(91)90243-3)

**[Supplementary] -- Track 3**

Davydov proposed that vibrational energy from C=O stretching (amide I) in
alpha-helical proteins could self-localize through phonon coupling, creating
a soliton that propagates along the helix without dispersion. This mechanism
for biological energy transport has been extensively studied and remains
controversial -- the main issue being the short soliton lifetime at biological
temperatures (310 K). Scott's 1992 review provides a balanced assessment.
Davydov solitons are relevant to the biophoton/myelin program as an analogy
for coherent energy transport in biological structures, and because some
authors have proposed solitonic mechanisms for biophoton generation. However,
the connection to photon emission in myelin is indirect and speculative.

---

## 5. Time-Series and Statistical Methods

### 5.1 Dlask, M., Kukal, J., Poplova, M., Sovka, P., & Cifra, M. (2019). "Short-time fractal analysis of biological autoluminescence." *PLOS ONE*, 14(7), e0214427. DOI: [10.1371/journal.pone.0214427](https://doi.org/10.1371/journal.pone.0214427)

**[Important] -- Track 4**

Dlask et al. applied the fractional Brownian bridge method to autoluminescence
time series from germinating mung beans, using rigorous statistical analysis
with advanced reference signals. They found that the detected autoluminescence
is not totally random but involves a process with negative memory (anti-persistent
behavior), distinguishing it from detector dark counts. This paper is important
for its methodological rigor -- it establishes that biophoton time series carry
genuine information content beyond Poisson noise, which is a prerequisite for
any signaling function. The limitation is that the biological system (mung beans)
is far removed from neural tissue, so the findings must be extrapolated with
caution.

---

### 5.2 Berke, J., Gulyas, I., Bognar, Z., Berke, D., Enyedi, A., Kozma-Bognar, V., Mauchart, P., Nagy, B., Varnagy, A., Kovacs, K., & Bodis, J. (2024). "Unique algorithm for the evaluation of embryo photon emission and viability." *Scientific Reports*, 14, 15066. DOI: [10.1038/s41598-024-61100-8](https://doi.org/10.1038/s41598-024-61100-8)

**[Supplementary] -- Track 4**

Berke et al. developed an entropy-weighted spectral fractal dimension algorithm
to analyze the self-similar structure of photon emission from mouse embryos. By
applying the second law of thermodynamics, they distinguished low-entropy energy
absorbed by living embryos from higher-entropy energy released. The algorithm
successfully distinguished living from degenerated embryos, and frozen from fresh
embryos. While the biological context (embryo viability) is distinct from neural
biophotonics, the analytical methodology -- particularly the entropy-weighted
spectral fractal dimension -- is directly transferable to time-series analysis
of biophoton signals in neural tissue (Track 4).

---

### 5.3 Benfatto, M., Pace, E., Curceanu, C., Scordo, A., Clozza, A., Davoli, I., Lucci, M., Francini, R., De Matteis, F., Grandi, M., Tuladhar, R., & Grigolini, P. (2021). "Biophotons and emergence of quantum coherence -- A diffusion entropy analysis." *Entropy*, 23(5), 554. DOI: [10.3390/e23050554](https://doi.org/10.3390/e23050554)

**[Important] -- Tracks 3, 4**

Using diffusion entropy analysis (DEA), a technique based on Kolmogorov complexity,
this paper analyzed biophoton emission from germinating seeds. Dark counts yielded
ordinary scaling, while the presence of seeds produced anomalous scaling. The
transition from regions dominated by non-ergodic crucial events to regions where
fractional Brownian motion dominates was interpreted as evidence for the emergence
of quantum coherence during germination. This paper introduces sophisticated
complexity measures to biophoton analysis and connects to fundamental questions
about quantum coherence in biology. Its main weakness is that the interpretation
of DEA anomalies as "quantum coherence" is model-dependent -- the same statistical
signatures could arise from classical non-equilibrium processes.

---

## 6. Reviews and Perspectives

### 6.1 Nevoit, G., Poderiene, K., Potyazhenko, M., Mintser, O., Jarusevicius, G., & Vainoras, A. (2025). "The concept of biophotonic signaling in the human body and brain: Rationale, problems and directions." *Frontiers in Systems Neuroscience*, 19, 1597329. DOI: [10.3389/fnsys.2025.1597329](https://doi.org/10.3389/fnsys.2025.1597329)

**[Important] -- Tracks 1, 2, 5**

This 2025 perspective article synthesizes the current state of the biophotonic
signaling hypothesis, covering mechanisms of cellular electromagnetic communication,
the evidence for biophoton generation and detection in neural tissue, and the
challenges facing the field. The authors identify key unsolved problems: the
low photon flux relative to thermal noise, the absence of identified biological
photon detectors, and the lack of causal evidence linking biophoton emission to
neural function. They propose directions for future research including improved
detection technologies and computational modeling. This is the most current
comprehensive perspective on the field and is valuable for its honest
assessment of both promise and limitations.

---

### 6.2 Casey, H., DiBerardino, I., Bonzanni, M., Rouleau, N., & Murugan, N.J. (2025). "Exploring ultraweak photon emissions as optical markers of brain activity." *iScience*, 28(3), 112019. DOI: [10.1016/j.isci.2025.112019](https://doi.org/10.1016/j.isci.2025.112019)

**[Essential] -- Tracks 2, 4, 5**

This 2025 study is the first to systematically track UPE from the living human
brain using paired photomultiplier tubes positioned over the left occipital and
right temporal regions. They found that brain UPE differs from background light
in both spectral and entropic properties, responds dynamically to cognitive tasks
and stimulation, and shows moderate correlation with brain rhythms. UPE exhibited
a distinctive frequency profile below 1 Hz, with slow rhythmic fluctuations.
The authors propose "photoencephalography" as a potential new brain imaging
modality. This paper is essential because it demonstrates that human brain UPE
is task-modulated and carries temporal structure, directly supporting the idea
that biophoton emission reflects neural activity. The main limitation is the
low spatial resolution (two-channel PMT) and the preliminary nature of the
task-related analyses.

---

### 6.3 Salari, V., Valian, H., Bassereh, H., Bokkon, I., & Barkhordari, A. (2015). "Ultraweak photon emission in the brain." *Journal of Integrative Neuroscience*, 14(3), 419--429. DOI: [10.1142/S0219635215300012](https://doi.org/10.1142/S0219635215300012)

**[Supplementary] -- Tracks 2, 5**

This review summarizes the evidence for UPE in neural tissue, covering the
oxidative biochemistry of biophoton generation, the experimental evidence for
neural biophotons, and the theoretical proposals for their functional roles. It
provides a useful bridge between the general UPE literature and the neural-specific
hypotheses. As a review, it does not present new results, but it usefully
organizes the literature as of 2015 and highlights the gap between theoretical
proposals and experimental evidence.

---

## 7. Key Textbooks and Background Reading

This section lists foundational texts for researchers entering the field of
biophoton research in myelinated neural tissue. The field sits at the
intersection of quantum optics, waveguide physics, neuroscience, and
biophysics, and competence in multiple areas is required.

### Quantum Optics

- **Gerry, C.C. & Knight, P.L. (2005). *Introductory Quantum Optics*. Cambridge University Press. ISBN: 978-0521527354.** The standard graduate-level introduction to quantum states of light, coherent and squeezed states, photon statistics, and cavity QED. Required background for evaluating coherence claims (Section 1) and quantum models (Section 4).

- **Mandel, L. & Wolf, E. (1995). *Optical Coherence and Quantum Optics*. Cambridge University Press. ISBN: 978-0521417112.** The definitive reference on optical coherence theory, photocount statistics, and photon correlation measurements. Essential for understanding the statistical analysis methods used to characterize biophoton emission (Cifra et al. 2015).

### Waveguide Theory and Photonics

- **Snyder, A.W. & Love, J.D. (1983). *Optical Waveguide Theory*. Chapman & Hall. ISBN: 978-0412099502.** The classic treatment of electromagnetic wave propagation in dielectric waveguides, including cylindrical waveguides. Directly relevant to modeling myelin as an optical waveguide (Section 3).

- **Saleh, B.E.A. & Teich, M.C. (2019). *Fundamentals of Photonics*, 3rd ed. Wiley. ISBN: 978-1119506874.** A comprehensive photonics textbook covering waveguides, fiber optics, optical resonators, and detection. Provides the optical engineering background needed to evaluate waveguide models and experimental designs.

### Neuroscience of Myelin

- **Bhatt, D.H., Zhang, S., & Bhatt, P. (2014). "The biology of myelin." *Nature Reviews Neuroscience*, various articles.** For primary references on myelin structure, the reader should consult current neuroscience reviews covering myelin ultrastructure (lamellae, Schmidt-Lanterman incisures, paranodal loops), its composition (70% lipid, 30% protein), and the biophysics of nodes of Ranvier.

- **Quarles, R.H., Macklin, W.B., & Morell, P. (2006). "Myelin formation, structure and biochemistry." Chapter in *Basic Neurochemistry*, 7th ed., Elsevier.** Standard reference on myelin biochemistry, particularly the lipid composition (cholesterol, galactocerebroside, phospholipids) that determines refractive index and absorption properties relevant to waveguide modeling.

- **Waxman, S.G. & Ritchie, J.M. (1993). "Molecular dissection of the myelinated axon." *Annals of Neurology*, 33(2), 121--136.** Important for understanding the electrical properties and geometry of nodes of Ranvier, which are critical for both the nanoantenna model (Section 3.7) and the ARROW model (Section 3.5).

### Biophysics and Biophotonics

- **Thar, R. & Kuhl, M. (2004). "Propagation of electromagnetic radiation in mitochondria?" *Journal of Theoretical Biology*, 230(2), 261--270.** An early theoretical treatment of electromagnetic wave propagation in biological structures, relevant as background for the waveguide hypothesis.

- **Popp, F.A. & Beloussov, L.V. (Eds.) (2003). *Integrative Biophysics: Biophotonics*. Springer. ISBN: 978-1402011399.** Edited volume collecting key papers on biophoton theory and applications, useful as a historical reference.

### Statistical Physics and Time-Series Analysis

- **Kantz, H. & Schreiber, T. (2004). *Nonlinear Time Series Analysis*, 2nd ed. Cambridge University Press. ISBN: 978-0521529020.** Standard reference for the nonlinear dynamical systems analysis methods (fractal dimension, recurrence analysis, entropy measures) applied to biophoton time series in Section 5.

- **Cover, T.M. & Thomas, J.A. (2006). *Elements of Information Theory*, 2nd ed. Wiley. ISBN: 978-0471241959.** Foundation for information-theoretic analyses of biophoton signals, including entropy measures and channel capacity calculations relevant to evaluating whether biophoton channels can carry meaningful information.

---

## Summary Table

| Paper | Year | Category | Rating | Tracks |
|:------|:----:|:--------:|:------:|:------:|
| Popp et al., Cell Biophysics | 1984 | Foundational | Essential | 2, 3, 4 |
| Popp, Li, & Gu (Eds.), World Scientific | 1992 | Foundational | Important | 2, 4 |
| Cifra & Pospisil, J. Photochem. Photobiol. B | 2014 | Foundational | Essential | 2, 4 |
| Mould et al., Frontiers Physiology | 2024 | Foundational | Important | 2, 4 |
| Cifra et al., J. Luminescence | 2015 | Foundational | Essential | 3, 4 |
| Pospisil et al., J. Photochem. Photobiol. B | 2014 | Foundational | Important | 2 |
| Bokkon, BioSystems (phosphene) | 2008 | Neural Hypothesis | Important | 2, 5 |
| Bokkon, BioSystems (imagery) | 2009 | Neural Hypothesis | Supplementary | 5 |
| Dotta et al., Neurosci. Lett. | 2012 | Neural Hypothesis | Important | 2, 5 |
| Sun, Wang, & Dai, Photochem. Photobiol. Sci. | 2010 | Neural Hypothesis | Essential | 1, 2 |
| Wang et al., PNAS | 2016 | Neural Hypothesis | Important | 1, 2, 5 |
| Tang & Dai, PLOS ONE | 2014 | Neural Hypothesis | Essential | 1, 2 |
| Zangari et al., Sci. Rep. (photons detected) | 2021 | Neural Hypothesis | Essential | 1, 2 |
| Kumar et al., Sci. Rep. | 2016 | Waveguide Theory | Essential | 1, 3, 5 |
| Kumar et al., Front. Biosci. | 2018 | Waveguide Theory | Important | 1, 3, 5 |
| Zarkeshian et al., Sci. Rep. | 2022 | Waveguide Theory | Essential | 1, 3, 5 |
| Zarkeshian et al., bioRxiv | 2023 | Waveguide Theory | Important | 1, 3 |
| Omidi et al., Sci. Rep. (ARROW) | 2022 | Waveguide Theory | Important | 1 |
| Zeng et al., Appl. Opt. | 2022 | Waveguide Theory | Important | 1 |
| Zangari & Micheli, Sci. Rep. (nanoantenna) | 2018 | Waveguide Theory | Essential | 1, 2 |
| Liu et al., Adv. Funct. Mater. | 2019 | Waveguide Theory | Essential | 1 |
| Liu, Chen, & Ao, Phys. Rev. E | 2024 | Quantum Models | Essential | 1, 3 |
| Rahnama et al., J. Integr. Neurosci. | 2011 | Quantum Models | Important | 2, 3 |
| Popp et al., Phys. Lett. A | 2002 | Quantum Models | Supplementary | 3 |
| Davydov, J. Theor. Biol. | 1973/77 | Quantum Models | Supplementary | 3 |
| Dlask et al., PLOS ONE | 2019 | Statistical Methods | Important | 4 |
| Berke et al., Sci. Rep. | 2024 | Statistical Methods | Supplementary | 4 |
| Benfatto et al., Entropy | 2021 | Statistical Methods | Important | 3, 4 |
| Nevoit et al., Front. Syst. Neurosci. | 2025 | Reviews | Important | 1, 2, 5 |
| Casey et al., iScience | 2025 | Reviews | Essential | 2, 4, 5 |
| Salari et al., J. Integr. Neurosci. | 2015 | Reviews | Supplementary | 2, 5 |

---

## New Additions (2026-02-19) — Nanoantenna Relay + Spectral Filter

| Reference | Year | Category | Relevance | Tracks |
|-----------|------|----------|-----------|--------|
| Zangari et al., Sci. Rep. 11:3022 (Ag⁺ experimental) | 2021 | Nanoantenna | Essential | 1, 6 |
| Chen, Wang & Dai, Brain Res. 1749:147133 (aging blueshift) | 2020 | Spectral Data | Essential | 6 |
| Wang et al., Front. Aging Neurosci. 15:1208274 (AD/VaD blueshift) | 2023 | Spectral Data | Essential | 6 |
| Wang et al., PNAS (species redshift, human 865nm) | 2016 | Spectral Data | Essential | 1, 6 |
| Barros & Cunha, Prog. Biophys. Mol. Biol. (biophoton review) | 2024 | Reviews | Important | 2, 6 |
| Smith & Lassmann (ROS + demyelination) | 1999 | Pathology | Important | 6 |
| Frede, Zadeh-Haghighi & Simon, IEEE JSTQE/bioRxiv (multi-node polarization) | 2023 | Waveguide Theory | Essential | 1, 3 |

**Note:** The spectral data papers (Chen 2020, Wang 2023, Wang 2016) are critical because our relay model's spectral filter prediction matches their independently measured values — particularly the AD centroid (predicted 581nm vs measured 582nm, not fitted).

*Last updated: February 19, 2026*
