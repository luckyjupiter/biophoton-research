# Episode 1: "We Ran the Numbers"
## The Biophoton Research Podcast
### Host: Yesh (Joshua Lengfelder)
### Target length: ~22 minutes (~3900 words)

---

[INTRO — 2 min]

What if I told you that your nerves might carry light — and that we actually ran the simulations to find out?

Not a thought experiment. Not a vibe. We wrote the code, built the models, swept the parameters, and looked at what the math actually says. Eight research tracks. Thousands of lines of simulation code. Waveguide physics, quantum optics, detection theory, disease modeling. All open source, all reproducible.

And here's the thing — some of the results confirm the hypothesis beautifully. And some of them demolish claims that have been floating around the biophoton literature for years.

Welcome to the Biophoton Research Podcast. I'm Yesh. And this first episode is about what happens when you stop speculating about biophotons in myelin and start computing.

Here's the plan for today. First, the core result that held up: myelin really does have fiber-optic physics, and the waveguide predictions are specific and testable. Second, the results that didn't hold up: the quantum coherence claims that have been hyped in this field are almost certainly wrong, and we can show you why. Third, a detection result that should change how everyone in this field thinks about experiments: the standard coherence test literally cannot work. And fourth, the honest path forward — what's actually testable, what it means for diseases like MS and Guillain-Barré, and why I care about getting this right.

I want to be upfront: this episode is going to disappoint people who want biophotons to be quantum and magical. The physics is fascinating enough without the woo. Let's get into it.

---

[PART 1 — The Waveguide Physics Is Real — 5 min]

Okay, the good news first. The hypothesis that myelin works as an optical waveguide? Solid. Really solid. Multiple independent lines of evidence, confirmed by our own simulations, and the numbers are specific enough to be experimentally falsifiable. That's what you want in science.

Quick refresher for anyone new. Myelin is the fatty insulation wrapped around nerve fibers. Biology textbooks say it speeds up electrical signals. True. But myelin also has optical properties that are remarkably similar to fiber optic cable. Refractive index of about one point four four, wrapped around an axon at about one point three eight, surrounded by fluid at one point three four. High-index layer around a lower-index core in a lower-index medium. That's a waveguide.

Kumar and colleagues at Calgary showed this computationally in 2016. Babini and Bhatt at Toledo refined the model in 2022, showing it works as an ARROW waveguide — anti-resonant reflecting optical waveguide — where the myelin layers act as wavelength-selective mirrors. And Zeng's group nailed down one of the most striking numbers in this whole field: each individual layer of myelin shifts the guided wavelength by exactly fifty-two point three nanometers. Each layer.

We built our own waveguide models in Track 03 — transfer matrix methods, cylindrical mode solvers, attenuation calculations — and got consistent results. Guided modes exist across exactly the wavelength range where biological tissue emits photons. The speed advantage is a factor of two million over electrical conduction. The geometry supports wavelength-division multiplexing. Different-caliber nerve fibers, with different numbers of myelin wraps, would guide different colors of light.

And there's experimental support. Zangari detected photons at nodes of Ranvier during nerve stimulation in 2021. Tang and Bhatt captured photons from active nerves. The Dai lab has shown brain tissue biophoton emission responds to neurotransmitter stimulation, changes with age and disease, and exhibits spectral properties consistent with waveguide predictions.

So the waveguide physics? Real. Confirmed by independent groups, confirmed by our simulations, and generating specific testable predictions. That's the part of this story that holds up.

Now let me tell you what doesn't.

---

[PART 2 — The Quantum Claims Are Overhyped — 5 min]

There's a strain of biophoton research — going back decades, honestly — that really wants biophotons to be quantum. Squeezed states. Coherent emission. Sub-Poissonian statistics. The implication being that biology has somehow harnessed quantum optics at room temperature in warm, wet, noisy tissue.

We tested this. Track 01 built a complete photocount statistics simulation suite — Poisson distributions, Bose-Einstein, negative binomial, squeezed states, Cox processes. Full detector artifact chains including dark counts, dead time, afterpulsing. Bayesian model comparison. Power analysis. The works.

And the result is clear: at biophoton-level intensities, squeezed-state fits are statistically indistinguishable from classical thermal models. You can fit a squeezed-state distribution to classical data and get comparable fit quality. But when you apply proper model selection — AIC, BIC, the standard information criteria that penalize unnecessary complexity — the simpler classical models win. Every time.

Let me say that more plainly. The papers claiming to find quantum coherence signatures in biophoton statistics? They're probably fitting noise. The signal is too faint, the detector artifacts are too large, and the statistical tests lack the power to distinguish quantum from classical at these count rates.

We quantified this precisely. Detector artifacts — the stuff your PMT does that isn't real signal — attenuate sub-Poissonian signatures by ninety-seven percent. That means even if there were genuine quantum statistics in the raw photon stream, your detector would wash them out before you could see them. And it gets worse: just two percent nonstationarity in your source — a tiny drift in emission rate over the measurement period — causes a false positive rate above five percent for quantum coherence detection.

So all those papers reporting sub-Poissonian statistics or squeezed-state signatures in biophotons? They need to be revisited with proper artifact correction and model selection. Our bet, based on the simulations: the quantum signatures will disappear.

Track 04 tells the same story from the theory side. We built a full cavity QED model of the myelin sheath — Morse oscillator for C-H vibrational cascades, cylindrical shell cavity with Purcell enhancement calculations, biphoton state generation via second-order perturbation theory. The numbers are unambiguous. The coupling strength is about five times ten to the fifth radians per second. The cavity loss rate is five times ten to the thirteenth. That's a cooperativity parameter of about nine times ten to the minus four. We're deep in the weak coupling regime. The cavity Q factor is about five — compare that to the millions you need for quantum optics experiments in a lab. Vibrational dephasing happens in about one picosecond.

In plain English: the myelin sheath is a terrible quantum optical cavity. It's lossy, it's noisy, and it dephases quantum states almost instantly. The Liu paper in Physical Review E proposing entangled biphoton generation from myelin is mathematically rigorous, and I respect the work — but the parameter regime they identify is so far from anything practically detectable that it's effectively a theoretical curiosity.

And I want to be honest about why this matters. It's tempting, when you have an exciting hypothesis, to lean into the most dramatic version of it. Quantum coherence in the brain! Entangled photons in your nerves! It makes for great headlines. But if the math doesn't support it, saying so isn't pessimism. It's integrity.

The waveguide hypothesis doesn't need quantum effects to be true, interesting, or medically useful. Let me show you why.

---

[PART 3 — The Detection Problem Nobody Talks About — 3 min]

Before I get to the medical applications, there's one more result I need to share, because it changes the game for experimental design in this field.

Track 05 built what we called the Detection Engineer's toolkit. Monte Carlo detector simulators for PMTs, SPADs, EMCCDs, and SNSPDs with realistic noise models. Signal-to-noise calculators. ROC analysis. Artifact characterization. And optimal protocol design.

The headline result: measuring photon coherence via g-two correlations — the standard quantum optics test that everyone in this field assumes you'd use — is fundamentally infeasible for broadband, multi-mode ultra-weak photon emission.

The math is brutal. For broadband UPE, the excess correlation signal — g-two of zero minus one — is on the order of ten to the minus six. To measure that at ten percent precision with typical biophoton count rates, you need an integration time exceeding ten to the sixteenth years. That's a million times longer than the age of the universe.

This isn't a engineering problem. You can't fix it with better detectors or longer cables or bigger grants. It's a fundamental statistical limit. The number of coincidence counts you need to resolve a correlation that tiny, at count rates that low, requires more time than physics will give you.

So when papers propose g-two measurements as the way to test biophoton coherence — and plenty do — they're proposing something that cannot work. Full stop.

Our Track 06 simulations confirmed this from the disease-modeling side. We computed ROC curves for various biophoton biomarkers across disease severity levels. Photon count changes? AUC of one point zero — perfect discrimination. Spectral shift? AUC of one point zero with Cohen's d values above fifty. Those biomarkers are screaming-loud signals. But g-two coherence? AUC of zero point five three in preclinical disease, zero point seven four even in severe demyelination. It's the weakest biomarker by far. And that's in simulation, where you don't have detector artifacts or integration time limits.

The good news buried in this negative result: you don't need coherence measurements. The classical waveguide predictions — spectral shift, intensity changes, oxidative burst signatures — are so strong that they're detectable with existing PMT technology in seconds to minutes. A standard bialkali PMT can achieve five-sigma detection of moderate biophoton signals in about seventeen seconds. That's a real experiment you can do tomorrow.

---

[PART 4 — What's Actually Testable — 4 min]

So here's where we stand. The waveguide physics is real. The quantum claims are overhyped. The standard coherence test can't work. What can we actually do?

Track 06 built disease progression models for every major subtype of MS — relapsing-remitting, secondary progressive, primary progressive — plus acute demyelination like GBS. Each model generates specific, quantitative predictions about biophoton emission changes.

The predictions are striking. At thirty percent demyelination — about nine myelin layers lost — the spectral blueshift should be roughly four hundred seventy nanometers. That's not a subtle signal. That's the difference between deep red and deep violet. A basic spectrometer can see it.

During active inflammation — an MS relapse, an acute GBS episode — lipid peroxidation from the immune attack should produce a ten-to-hundred-fold increase in lateral photon emission, with specific spectral fingerprints. Autoimmune demyelination produces myeloperoxidase-driven chemistry with different emission spectra than toxic demyelination from something like cuprizone poisoning. The singlet oxygen signature — emission peaks at six thirty-four and seven-oh-three nanometers — should be present in autoimmune attack but absent in toxic demyelination. That's a mechanistic discriminator, not just a detection tool. It could tell you what's causing the damage, not just that damage exists.

And remyelination should be trackable too. When Schwann cells or oligodendrocytes rebuild myelin, the spectral shift should partially reverse — but not completely, because remyelinated sheaths are thinner than originals. You'd see the wavelength drift back toward red, then stabilize at an intermediate value. A pharmacodynamic biomarker for remyelination therapy, measured optically, in real time.

The experiments are straightforward. EAE mice — the standard MS model — develop optic neuritis. The optic nerve is heavily myelinated, surgically accessible. Dissect it, perfuse it, stimulate it, measure photon emission with a cooled EMCCD camera. Compare healthy versus demyelinated versus remyelinated. Look for the spectral shift, the intensity spike, the oxidative fingerprint. Cuprizone models give you controlled, reversible demyelination on a predictable schedule — perfect for tracking the remyelination signal.

The equipment exists. The animal models are standard in neuroimmunology labs worldwide. A PMT setup for the basic detection experiment costs maybe twenty thousand dollars. What's been missing is the connection between photonics and neuroimmunology — two fields that don't normally talk to each other.

And the clinical urgency is real. The CCMR-Two trial showed that clemastine plus metformin can promote myelin repair in relapsing-remitting MS patients. Remyelination is becoming a real therapeutic target. But how do you know your remyelination therapy is working? Right now, the best tool is MRI with specialized sequences like myelin water fraction imaging — expensive, slow, indirect. Biophoton spectroscopy could potentially give you continuous, myelin-specific monitoring at a fraction of the cost.

---

[THE PERSONAL PART — 3 min]

I should tell you why I care about getting this right. Not just the science — the honesty.

I had Guillain-Barré syndrome. The acute demyelinating form, AIDP, where your immune system sends macrophages to physically peel the myelin off your peripheral nerve fibers, layer by layer. Ascending paralysis. Starts in your feet, climbs. Your reflexes vanish. If it goes high enough, you stop breathing on your own.

I was fortunate. It reversed. Schwann cells are remarkably good at rebuilding myelin in the peripheral nervous system. Over weeks and months, sensation returned, strength returned.

But the rebuilt myelin is different — that's well-established neuroscience. Remyelinated fibers have thinner sheaths, shorter internodes. Electrophysiologically, that's why some GBS survivors have permanently reduced nerve conduction velocities even after clinical recovery.

In the waveguide framework, those thinner sheaths mean a different operating wavelength. If I lost ten layers and got back seven, my rebuilt nerves are tuned about a hundred and fifty-seven nanometers differently than before. I'm not just electrically repaired — if the waveguide hypothesis is correct, I'm optically retuned. Running on a different color of light.

Do I know this matters functionally? No. Nobody does. Because nobody has measured it.

And that right there is why the intellectual honesty matters so much to me. When I see biophoton research papers claiming quantum coherence effects with statistical tests that our simulations show can't possibly work — when I see g-two experiments proposed that would take longer than the age of the universe — it frustrates me. Not because the hypothesis is wrong. The waveguide hypothesis is beautiful and probably right. But because overselling the quantum angle distracts from the classical predictions that are actually testable and potentially life-changing for millions of people with demyelinating diseases.

Two point eight million people living with MS worldwide. GBS affects one to two per hundred thousand per year. Charcot-Marie-Tooth disease. Leukodystrophies. CIDP. Millions of people whose myelin has been damaged and rebuilt, carrying nervous systems that may have undergone an optical transformation we've never once measured.

I owe it to those people — and honestly, I owe it to myself — to be rigorous about what the math actually says. Not what I wish it said. Not what would make the best podcast. What the simulations show.

---

[THE PATH FORWARD — 2 min]

So here's the honest summary.

What's real: myelin is an optical waveguide. Multiple independent simulations confirm guided modes. Fifty-two point three nanometers per layer of spectral tuning. Two-million-fold speed advantage over electrical conduction. Photons have been detected in the right places. The physics works.

What's overhyped: quantum coherence claims in biophoton statistics. Squeezed-state fits don't survive proper model selection. The cavity QED parameters are deep in weak coupling. The standard g-two coherence test requires more time than the universe has existed. Previous papers claiming quantum signatures are probably wrong.

What's testable right now: classical waveguide predictions. Spectral blueshift with demyelination — huge effect sizes, detectable with existing spectrometers. Intensity spikes during active inflammation — ten to a hundred times baseline. Specific spectral fingerprints distinguishing autoimmune from toxic demyelination. Remyelination tracking via spectral recovery. All of this can be measured with PMTs and EMCCDs that exist today, using standard animal models that neuroimmunology labs already run.

What we need: someone to actually do the experiment. A neuroimmunology lab willing to put a photon detector next to their EAE mouse model. A photonics group willing to optimize collection optics for nerve tissue. The first measurement of biophoton emission from a demyelinating nerve. That's the experiment that changes everything, and it doesn't require quantum anything.

This is what we're building toward. Open science, open code, open data. Every simulation I've described is available in our repository. Eight tracks of computational work, fully reproducible. We're not asking you to take our word for it. We're asking you to run the code and check.

---

[OUTRO — 1 min]

Here's what I believe. The biophoton waveguide hypothesis is one of the most interesting ideas in neuroscience right now. Not because it's quantum — it probably isn't, at any detectable level. But because it suggests the nervous system has an entire optical communication layer we've never characterized, and because the classical physics alone generates predictions that could transform how we diagnose and monitor demyelinating diseases.

The physics is interesting enough without overselling it. Let's do the science right.

If you're a neuroscientist, a photonics researcher, a clinician working with MS or GBS, or someone who just cares about rigorous open science — I'd love to hear from you. Find us on Telegram at @biophotonresearch. That's where the research discussions happen, where the code gets shared, and where collaborators connect.

I'm Yesh. Thanks for listening.

---

*[END OF EPISODE]*

**Word count: ~3,920**

**Show notes references:**
1. Kumar et al. 2016, *Scientific Reports* — foundational waveguide simulation
2. Babini et al. 2022, *Scientific Reports* — ARROW model of myelin
3. Zeng et al. 2022, *Applied Optics* — 52.3 nm/layer spectral tuning
4. Zangari et al. 2021, *Scientific Reports* — photon detection at nodes of Ranvier
5. Liu et al. 2024, *Physical Review E* — entangled biphoton generation (theoretical)
6. Chen et al. 2020, *Brain Research* — spectral blueshift in aging
7. Wang et al. 2023, *Frontiers in Aging Neuroscience* — biophotons in neurodegeneration
8. Zarkeshian et al. 2022, *Scientific Reports* — backpropagation hypothesis
9. CCMR-Two trial, ECTRIMS 2025 — clemastine + metformin remyelination
10. Cifra et al. 2015, *J. Luminescence* — critical review

**Computational results cited (from this research program):**
- Track 01: Photocount statistics — AIC/BIC model selection, 97% artifact attenuation, 2% nonstationarity → 5% false positive rate
- Track 03: Waveguide propagation — transfer matrix, ARROW analysis, cylindrical mode solver
- Track 04: Cavity QED — g = 5.4×10⁵, κ = 5.2×10¹³, Q ≈ 5, C ≈ 9×10⁻⁴, weak coupling
- Track 05: Detection theory — g(2) requires >10¹⁶ years, PMT 5σ at 10 ph/cm²/s in 17.5s
- Track 06: Disease modeling — spectral shift AUC = 1.0, g(2) AUC = 0.53–0.74, MS subtype simulations

**Code repository:** github.com/biophoton-research (all tracks, open source)
