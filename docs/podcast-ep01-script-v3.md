# Episode 1: "We Ran the Numbers"
## The Biophoton Research Podcast
### Host: Yesh (Joshua Lengfelder)
### Target length: ~22 minutes (~3950 words)

---

[INTRO — 2 min]

What if I told you that your nerves might carry light — and that we actually ran the simulations to find out?

Not a thought experiment. Not a vibe. We wrote the code, built the models, swept the parameters, and looked at what the math actually says. Eight research tracks. Thousands of lines of simulation code. Waveguide physics, quantum optics, detection theory, disease modeling. All open source, all reproducible.

And here's the thing — some of the results confirm the hypothesis beautifully. And some of them demolish claims that have been floating around the biophoton literature for years. With specific numbers. Not hand-wavy "our models suggest" — actual numbers you can check.

Welcome to the Biophoton Research Podcast. I'm Yesh. And this first episode is about what happens when you stop speculating about biophotons in myelin and start computing.

Here's the plan. First, the core result that held up: myelin really does have fiber-optic physics, and the waveguide predictions are specific and testable. Second, the results that didn't hold up: the quantum coherence claims that have been hyped in this field are almost certainly wrong, and I'll give you the exact numbers that killed them. Third, a detection result that should change how everyone in this field designs experiments — the standard coherence test literally cannot work, but the classical tests are shockingly powerful. And fourth, the honest path forward — what's actually testable, what it means for diseases like MS and Guillain-Barré, and why I care about getting this right.

I want to be upfront: this episode is going to disappoint people who want biophotons to be quantum and magical. The physics is fascinating enough without the woo. Let's get into it.

---

[PART 1 — The Waveguide Physics Is Real — 5 min]

Okay, the good news first. The hypothesis that myelin works as an optical waveguide? Solid. Really solid. Multiple independent lines of evidence, confirmed by our own simulations, and the numbers are specific enough to be experimentally falsifiable. That's what you want in science.

Quick refresher for anyone new. Myelin is the fatty insulation wrapped around nerve fibers. Biology textbooks say it speeds up electrical signals. True. But myelin also has optical properties that are remarkably similar to fiber optic cable. Refractive index of about one point four four, wrapped around an axon at about one point three eight, surrounded by fluid at one point three four. High-index layer around a lower-index core in a lower-index medium. That's a waveguide.

Kumar and colleagues at Calgary showed this computationally in 2016. Babini and Bhatt at Toledo refined the model in 2022, showing it works as an ARROW waveguide — anti-resonant reflecting optical waveguide — where the myelin layers act as wavelength-selective mirrors. And Zeng's group nailed down one of the most striking numbers in this whole field: each individual layer of myelin shifts the guided wavelength by exactly fifty-two point three nanometers. Each layer. That number is going to come back when we talk about disease detection.

We built our own waveguide models in Track 03 — transfer matrix methods, cylindrical mode solvers, attenuation calculations — and got consistent results. Guided modes exist across the wavelength range of one point eight to four microns, which is exactly where our Morse oscillator model puts the C-H vibrational emission. The fundamental C-H stretch transition — that's the v-one to v-zero drop — emits at three point five four microns. The first overtone, v-two to v-one, lands at three point seven microns. And the second harmonic, v-two to v-zero, hits one point eight one microns. All of these fall squarely in the waveguide's operating band.

The speed advantage is a factor of two million over electrical conduction. The geometry supports wavelength-division multiplexing. Different-caliber nerve fibers, with different numbers of myelin wraps, would guide different colors of light.

And there's experimental support. Zangari detected photons at nodes of Ranvier during nerve stimulation in 2021. Tang and Bhatt captured photons from active nerves. The Dai lab has shown brain tissue biophoton emission responds to neurotransmitter stimulation, changes with age and disease, and exhibits spectral properties consistent with waveguide predictions.

So the waveguide physics? Real. Confirmed by independent groups, confirmed by our simulations, generating specific testable predictions with actual wavelengths attached. That's the part of this story that holds up.

Now let me tell you what doesn't.

---

[PART 2 — The Quantum Claims Are Dead. Here Are the Numbers That Killed Them — 6 min]

There's a strain of biophoton research — going back decades, honestly — that really wants biophotons to be quantum. Squeezed states. Coherent emission. Sub-Poissonian statistics. The implication being that biology has somehow harnessed quantum optics at room temperature in warm, wet, noisy tissue.

We tested this. Rigorously. Track 01 built a complete photocount statistics simulation suite — Poisson, Bose-Einstein, negative binomial, squeezed states, Cox processes. Full detector artifact chains. Bayesian model comparison. Power analysis. And the result is clear: at biophoton-level intensities, squeezed-state fits are statistically indistinguishable from classical thermal models.

But let me give you the specific numbers that make this undeniable, because the numbers are the story.

First, the indistinguishability problem. Biophoton emission is broadband — bandwidth around ten-to-the-fourteen hertz. That means the number of thermal modes is around ten-to-the-thirteen. The Fano factor departure from Poisson for M-mode thermal light is mu divided by M — about ten-to-the-minus-twelve. To detect a departure that small, you'd need more data than any feasible experiment can collect. The minimum detectable departure with ten-to-the-seventh counting intervals is about plus-or-minus zero point zero zero one. You're off by nine orders of magnitude. Photocount statistics literally cannot distinguish coherent from broadband thermal light at biophoton intensities.

Second, the detector artifact budget. This one's brutal. Say you have a genuinely sub-Poissonian source with a true Fano factor of zero point five — that's strong squeezing, way beyond anything anyone claims for biophotons. What does your detector actually see? With a cooled PMT — quantum efficiency fifteen percent, dark rate two per second — you measure a Fano factor of zero point nine seven. You've lost ninety-seven percent of the sub-Poissonian signature to detector artifacts alone. With a room-temperature PMT, it's even worse: measured Fano factor of zero point nine nine seven. Only three-tenths of a percent of the quantum signature survives. Even the best detector on the planet — a superconducting nanowire single-photon detector, eighty-five percent quantum efficiency, dark rate zero point one per second — only preserves a Fano factor of zero point five eight. And SNSPDs cost a hundred to five hundred thousand dollars with a collection area of zero point zero zero zero three square centimeters.

Third — and this is the nail in the coffin for every paper claiming sub-Poissonian biophoton statistics — nonstationarity. Biological sources don't emit at a perfectly constant rate. Our simulations show that a mere two point one percent sinusoidal modulation in emission rate causes the Fano factor test to reject the Poisson null at above five percent. Two percent drift. Any living tissue varies more than that just from metabolic fluctuations. Every "sub-Poissonian" result in the biophoton literature that didn't meticulously control for rate drift is suspect.

And we checked the original papers. We did a computational reanalysis of the Popp and Chang 2002 and Bajpai 2005 data — the canonical papers claiming quantum coherence in biophoton emission. When you apply proper model selection — AIC, BIC — the simpler classical models win. The squeezed-state fits have more free parameters and don't earn their keep. Four-parameter squeezed fits match classical negative binomial data comparably well. They're fitting noise.

Track 04 tells the same story from the theory side. We built a full cavity QED model of the myelin sheath — Morse oscillator for C-H vibrational cascades, cylindrical shell cavity with Purcell enhancement. Let me just read you the numbers.

Coupling strength g: five point four one times ten-to-the-fifth radians per second. Cavity loss rate kappa: five point two zero times ten-to-the-thirteen radians per second. That gives a cooperativity C of eight point eight times ten-to-the-minus-four. The cavity Q factor? Five point one. Five. In a quantum optics lab, you're working with Q factors in the millions to billions. We have five.

Strong coupling? No. Not even close. The cooperativity is zero point zero zero zero nine. That's weak coupling, full stop. You need C much greater than one for anything quantum-optically interesting. We're nearly four orders of magnitude below that threshold.

Vibrational dephasing time T-two-star: one picosecond. Coherence length in the waveguide: about four microns. That's how far any quantum coherence propagates before the environment destroys it. Four microns. A nerve fiber is centimeters to meters long.

Bell inequality violation? We swept detector efficiency from thirty to ninety-five percent. At thirty percent efficiency — roughly what a good PMT gives you — the Bell parameter S equals zero point two three. You need S greater than two for a violation. At fifty percent, S equals zero point six four. At seventy percent, still only one point two five. You don't cross the Bell limit until you hit ninety percent efficiency, where S barely scrapes two point zero six. So you need at minimum eighty-nine percent detector efficiency to even see a Bell violation, which rules out everything except SNSPDs — and those have the collection area problem I already mentioned.

The entanglement itself, even in theory, is minuscule. Peak entanglement entropy is zero point zero six bits at an optimal myelin thickness of two point five microns. The Schmidt number peaks at one point zero one — barely above the separable state value of one point zero. There is essentially no entanglement to detect.

The Liu paper in Physical Review E proposing entangled biphoton generation from myelin is mathematically rigorous, and I respect the work — but the parameter regime is so far from anything detectable that it's a theoretical curiosity, not a testable prediction.

---

[PART 3 — The Detection Paradox: One Test Is Impossible, the Other Is Trivial — 4 min]

Here's where it gets interesting. Because Track 05 and Track 06 together reveal this beautiful paradox: the quantum measurement everyone assumes you'd do cannot work, but the classical measurements are almost embarrassingly easy.

The g-two correlation measurement — the standard quantum optics test — requires resolving a correlation excess of about ten-to-the-minus-six for broadband multi-mode biophoton emission. At typical count rates, the integration time exceeds ten-to-the-sixteenth years. Ten to the sixteenth. The universe is about one point four times ten-to-the-tenth years old. You'd need to run your experiment for a million times longer than everything has existed.

And there's another g-two problem nobody mentions: afterpulsing. A PMT with a two percent afterpulse probability — completely standard — creates a g-two excess of about three thousand at one nanosecond delay. Three thousand. Your artifact is six orders of magnitude larger than the signal you're looking for. Correlation measurements below a hundred nanoseconds are completely dominated by afterpulsing.

So g-two coherence measurement for biophotons is dead. Not difficult. Not expensive. Dead.

But now look at the classical predictions from Track 06, and the contrast is almost funny.

We modeled biophoton biomarkers across five stages of demyelination — preclinical, early clinical, moderate, severe, and active relapse — and computed AUC and Cohen's d for each.

The spectral shift biomarker? AUC of one point zero at every single disease stage. Even preclinical — the earliest stage, before symptoms appear — AUC of one point zero with a Cohen's d of eighteen point seven. At moderate demyelination, Cohen's d hits one hundred and fifteen. At severe, one hundred and eighty. These are preposterous effect sizes by any standard in biomedical research. A Cohen's d of zero point eight is considered "large." We're getting a hundred and eighty.

Photon count changes? Also AUC of one point zero across the board, with Cohen's d ranging from three point three to three point nine. Still excellent.

The singlet oxygen to carbonyl ratio — the mechanistic discriminator between autoimmune and toxic demyelination — hits AUC of zero point nine at preclinical and climbs to one point zero during active relapse, with Cohen's d up to three point three.

Now compare: g-two coherence. AUC of zero point five three in preclinical disease. That's barely above coin flip. Even at severe demyelination, only zero point seven four. Cohen's d of zero point zero nine at preclinical, zero point nine one at severe. The weakest biomarker by a mile — and that's in perfect simulation conditions without detector artifacts or time constraints.

The classical biomarkers aren't just better. They're in a different universe of detectability.

And the detection hardware confirms it. Track 05 computed integration times for five-sigma detection across five detector types and nine signal levels. A standard bialkali PMT — the workhorse of photon counting, costs a few thousand dollars — can detect a moderate biophoton signal of ten photons per square centimeter per second in seventeen point five seconds. Seconds. A GaAsP PMT does it in seven point five seconds. Even at one photon per square centimeter per second — faint emission — a bialkali PMT gets there in twenty-five minutes. Still a perfectly reasonable experiment.

With one hour of integration, a bialkali PMT can detect signals down to zero point two three photons per square centimeter per second. That's well within the range of reported biophoton emission from neural tissue.

For spectral measurement specifically — which is what you need for the spectral shift biomarker — an EMCCD camera with ten-by-ten pixel binning can achieve ten-nanometer spectral resolution in about ten hours. That's the first high-resolution biophoton spectrum from neural tissue. One overnight run.

---

[PART 4 — What Demyelination Actually Looks Like in Photons — 3 min]

So here's what the disease model predicts, in concrete terms.

At thirty percent demyelination — about nine myelin layers lost — the spectral blueshift should be roughly four hundred seventy nanometers. That's not a subtle signal. That's the difference between deep infrared and visible light. A basic spectrometer can see it.

During active inflammation — an MS relapse, an acute GBS episode — lipid peroxidation from the immune attack should produce a ten-to-hundred-fold increase in lateral photon emission, with specific spectral fingerprints from reactive oxygen species. The singlet oxygen peaks at six thirty-four and seven-oh-three nanometers should light up during autoimmune attack but stay quiet during toxic demyelination. That distinction matters: it's the difference between MS and chemical exposure. A mechanistic discriminator, not just a yes-or-no test.

And remyelination should be trackable. When oligodendrocytes or Schwann cells rebuild myelin sheaths, the spectral shift should partially reverse — but not completely, because remyelinated sheaths are thinner than originals. You'd see the emission wavelength drift back toward longer wavelengths, then stabilize at an intermediate value. A real-time pharmacodynamic biomarker for remyelination therapy.

The experiments are straightforward. EAE mice — the standard MS model — develop optic neuritis. The optic nerve is heavily myelinated, surgically accessible. Dissect, perfuse, stimulate, measure. Compare healthy versus demyelinated versus remyelinated. Cuprizone models give you controlled, reversible demyelination on a predictable schedule — perfect for tracking the remyelination signal.

The equipment exists. A PMT setup costs maybe twenty thousand dollars. The animal models are standard in neuroimmunology labs worldwide. What's been missing is the connection between photonics and neuroimmunology — two fields that don't normally talk to each other.

And the clinical urgency is real. The CCMR-Two trial showed that clemastine plus metformin can promote myelin repair in relapsing-remitting MS patients. Remyelination is becoming a real therapeutic target. But how do you know your drug is working? Right now, the best tool is MRI with specialized sequences like myelin water fraction imaging — expensive, slow, indirect. Biophoton spectroscopy could potentially give you continuous, myelin-specific monitoring at a fraction of the cost. And our simulations say the signal is screaming loud.

---

[THE PERSONAL PART — 2.5 min]

I should tell you why I care about getting this right. Not just the science — the honesty.

I had Guillain-Barré syndrome. The acute demyelinating form — AIDP — where your immune system sends macrophages to physically peel the myelin off your peripheral nerve fibers, layer by layer. Ascending paralysis. Starts in your feet, climbs. Your reflexes vanish. If it goes high enough, you stop breathing on your own.

I was fortunate. It reversed. Schwann cells are remarkably good at rebuilding myelin in the peripheral nervous system. Over weeks and months, sensation returned, strength returned.

But the rebuilt myelin is different — that's well-established neuroscience. Remyelinated fibers have thinner sheaths, shorter internodes. In the waveguide framework, those thinner sheaths mean a different operating wavelength. If I lost ten layers and got back seven, my rebuilt nerves are tuned about one hundred fifty-seven nanometers differently than before — that's ten times fifty-two point three minus seven times fifty-two point three. I'm not just electrically repaired — if the waveguide hypothesis is correct, I'm optically retuned. Running on a different color of light.

Do I know this matters functionally? No. Nobody does. Because nobody has measured it.

And that's why the intellectual honesty matters. When I see papers claiming quantum coherence with statistical tests that our simulations show have ninety-seven percent of their signal eaten by detector artifacts — when I see g-two experiments proposed that would take ten-to-the-sixteenth years — it frustrates me. Not because the hypothesis is wrong. The waveguide hypothesis is beautiful and probably right. But because overselling the quantum angle distracts from the classical predictions that are actually testable and potentially life-changing for millions of people.

Two point eight million people living with MS worldwide. GBS affects one to two per hundred thousand per year. Charcot-Marie-Tooth disease. Leukodystrophies. CIDP. Millions of people whose myelin has been damaged and rebuilt, carrying nervous systems that may have undergone an optical transformation we've never once measured.

---

[THE HONEST SUMMARY — 2 min]

Here's what we know.

What's real: myelin is an optical waveguide. Guided modes from one point eight to four microns. Fifty-two point three nanometers per layer of spectral tuning. C-H vibrational emission at three point five four and three point seven microns falls right in the operating band. The Morse oscillator model gives us twenty-four bound states with a maximum quantum number of twenty-three. Photons have been detected in the right places. The physics works.

What's dead: quantum coherence claims. Cavity Q of five. Cooperativity of zero point zero zero zero nine. Dephasing in one picosecond. Coherence length of four microns. Bell violation requires eighty-nine percent detector efficiency minimum. Peak entanglement of zero point zero six bits. Ninety-seven percent of sub-Poissonian signatures lost to detector artifacts. G-two measurement needs ten-to-the-sixteenth years. Two percent source drift causes five percent false positive rate on coherence tests. The squeezed-state papers don't survive model selection. It's over.

What's screaming to be measured: spectral shift biomarker — AUC of one point zero, Cohen's d of eighteen to one hundred eighty across disease stages. Photon count changes — AUC of one point zero, Cohen's d above three. Singlet oxygen mechanistic discriminator — AUC zero point nine to one point zero. A bialkali PMT gets five-sigma detection in seventeen point five seconds at moderate signal levels. An EMCCD gets you a spectrum overnight.

What we need: someone to actually do the experiment. A neuroimmunology lab willing to put a photon detector next to their EAE mouse model. A photonics group willing to optimize collection optics for nerve tissue. The first measurement of biophoton emission from a demyelinating nerve.

Every simulation is in the repository. Eight tracks. Fully reproducible. We're not asking you to take our word for it. We're asking you to run the code.

---

[OUTRO — 30 sec]

The biophoton waveguide hypothesis is one of the most interesting ideas in neuroscience right now. Not because it's quantum — it probably isn't, at any detectable level. But because the classical physics alone generates predictions that could transform how we diagnose and monitor demyelinating diseases. Predictions with AUC of one point zero. Predictions measurable in seconds.

The physics is interesting enough without overselling it. Let's do the science right.

Find us on Telegram at @biophotonresearch. That's where the research happens, where the code gets shared, and where collaborators connect.

I'm Yesh. Thanks for listening.

---

*[END OF EPISODE]*

**Word count: ~3,950**

**Show notes references:**
1. Kumar et al. 2016, *Scientific Reports* — foundational waveguide simulation
2. Babini et al. 2022, *Scientific Reports* — ARROW model of myelin
3. Zeng et al. 2022, *Applied Optics* — 52.3 nm/layer spectral tuning
4. Zangari et al. 2021, *Scientific Reports* — photon detection at nodes of Ranvier
5. Liu et al. 2024, *Physical Review E* — entangled biphoton generation (theoretical)
6. Popp & Chang 2002 — sub-Poissonian biophoton claims (critiqued)
7. Bajpai 2005 — squeezed-state biophoton claims (reanalyzed)
8. Cifra et al. 2015, *J. Luminescence* — critical review
9. CCMR-Two trial, ECTRIMS 2025 — clemastine + metformin remyelination

**Computational results cited (all from this research program):**
- Track 01: Photocount statistics — 97% artifact attenuation of sub-Poissonian signal, 2.1% nonstationarity → >5% FPR, squeezed fits lose on AIC/BIC, Fano departure ~10⁻¹² for broadband thermal, min detectable |F-1| > 0.001
- Track 03: Waveguide propagation — guided modes 1.8–4.0 μm, transfer matrix & ARROW analysis
- Track 04: Cavity QED — g = 5.41×10⁵ rad/s, κ = 5.20×10¹³ rad/s, Q = 5.1, C = 8.8×10⁻⁴, T₂* = 1 ps, coherence length ~4 μm, Bell S = 0.23 at η=0.30 rising to 2.06 at η=0.90, peak entanglement 0.06 bits, Schmidt K = 1.01
- Track 05: Detection theory — PMT 5σ at 10 ph/cm²/s in 17.5 s, g(2) requires >10¹⁶ yr, afterpulse g(2) excess ~3000 at 1 ns, EMCCD 10 nm spectrum in ~10 hr, min detectable 0.23 ph/cm²/s in 1 hr (bialkali PMT)
- Track 06: Disease modeling — spectral shift AUC = 1.0 / Cohen's d = 18.7–179.8 across stages, photon count AUC = 1.0 / d = 3.3–3.9, SO₂/carbonyl AUC = 0.90–1.0, g(2) AUC = 0.53–0.74, 52.3 nm blueshift per lost layer, ~470 nm shift at 30% demyelination

**Code repository:** github.com/biophoton-research (all tracks, open source)
