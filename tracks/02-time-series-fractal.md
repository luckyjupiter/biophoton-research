# Track 02: Time-Series and Fractal Analysis of Biophoton Emissions

## 1. Overview

Ultra-weak photon emission (UPE) from biological tissue is not merely a stochastic byproduct of oxidative metabolism. Growing evidence indicates that the *temporal structure* of biophoton streams encodes information about the dynamical state of the emitting system -- its metabolic coordination, degree of coherence, and capacity for self-organization. If myelin sheaths function as optical waveguides (Track 03), then the temporal statistics of photons entering, propagating through, and exiting these structures carry signatures of waveguide coupling efficiency, coherence length, and biological integrity.

This track develops the mathematical and computational framework for extracting temporal structure from biophoton count time series, with particular emphasis on:

- **Memory and correlation structure**: Do successive photon counts carry information about each other, or is the stream memoryless (Poisson)?
- **Scale-free dynamics**: Does the emission exhibit fractal or multifractal scaling, and what does this imply about the generating mechanism?
- **Complexity and entropy**: How does the informational complexity of the emission stream relate to tissue viability and health?
- **Coherence signatures**: Can temporal analysis distinguish coherent (quantum-correlated) emission from classical stochastic emission?
- **Waveguide coupling**: Does the temporal correlation structure change when photons propagate through myelinated versus unmyelinated tissue?

The central hypothesis is that biophoton time series from myelinated neural tissue should exhibit richer temporal structure than emission from unmyelinated tissue or from tissue in which the myelin has been damaged, because the waveguide imposes spectral and modal filtering that reshapes temporal correlations.

---

## 2. Background Theory

### 2.1 Autocorrelation Functions and Emission Memory

The normalized autocorrelation function (ACF) of a discrete photon count time series $\{x_i\}_{i=1}^{N}$ at lag $k$ is:

$$C(k) = \frac{\sum_{i=1}^{N-k}(x_i - \bar{x})(x_{i+k} - \bar{x})}{\sum_{i=1}^{N}(x_i - \bar{x})^2}$$

For a purely Poissonian (memoryless) emission process, $C(k) = 0$ for all $k > 0$. Deviations from this null indicate temporal structure:

- **$C(k) > 0$ (positive memory)**: Photon counts tend to cluster -- high-count bins follow high-count bins. This is characteristic of bunched (super-Poissonian) light, metabolic bursts, or slow modulation of the emission rate.
- **$C(k) < 0$ (negative memory / anti-correlation)**: High-count bins tend to be followed by low-count bins and vice versa. This is the signature found by Dlask et al. (2019) in mung bean autoluminescence using fractional Brownian bridge analysis, suggesting a regulatory feedback mechanism that actively suppresses fluctuations.
- **Power-law decay $C(k) \sim k^{-\gamma}$**: Long-range dependence, characteristic of critical or self-organized systems.
- **Exponential decay $C(k) \sim e^{-k/\tau}$**: Short-range (Markovian) memory with a characteristic correlation time $\tau$.

**Practical considerations for biophoton data**: At ultra-low count rates (1--100 photons/s), the ACF is dominated by shot noise. The Fano factor $F = \sigma^2 / \bar{x}$ provides a complementary measure: $F = 1$ for Poisson, $F < 1$ for sub-Poissonian (antibunched) light, $F > 1$ for super-Poissonian (bunched) light. The relationship between $F$ and $C(k)$ over a counting window $T$ containing $M$ bins is:

$$F = 1 + 2\sum_{k=1}^{M-1}\left(1 - \frac{k}{M}\right)C(k)\bar{x}$$

This shows that positive autocorrelations inflate $F$ above 1 and negative autocorrelations suppress it below 1.

### 2.2 Power Spectral Density and 1/f^alpha Noise Classification

The power spectral density (PSD) $S(f)$ is the Fourier transform of the autocorrelation function:

$$S(f) = \sum_{k=-\infty}^{\infty} C(k) e^{-2\pi i f k}$$

For many biological and physical systems, the PSD follows a power law:

$$S(f) \propto \frac{1}{f^{\alpha}}$$

The spectral exponent $\alpha$ classifies the noise type:

| $\alpha$ | Noise type | Interpretation |
|----------|------------|----------------|
| 0 | White noise | No correlations; Poisson process gives $\alpha = 0$ |
| 1 | Pink / flicker noise | Equal energy per octave; ubiquitous in biological systems |
| 2 | Brown(ian) noise | Random walk; integrated white noise |
| $0 < \alpha < 1$ | Stationary long-memory process | Anti-persistent to weakly correlated |
| $1 < \alpha < 2$ | Non-stationary long-memory process | Persistent fluctuations |

**Estimation methods**: For short, noisy biophoton time series, the Welch periodogram with overlapping Hann-windowed segments is preferred over raw periodograms. The Lomb-Scargle periodogram may be necessary if the data have gaps (e.g., from dead-time corrections in photomultiplier data). The spectral exponent is estimated from a linear fit to $\log S(f)$ vs. $\log f$, excluding the lowest frequencies (affected by nonstationarity) and the highest (affected by detector artifacts).

**Relationship to Hurst exponent**: For stationary processes, $\alpha = 2H - 1$ where $H$ is the Hurst exponent. For nonstationary processes (where a DFA exponent $\alpha_{\text{DFA}}$ is more appropriate), $\alpha = 2\alpha_{\text{DFA}} - 1$.

### 2.3 Fractal Dimension Estimation

The fractal dimension $D$ quantifies the complexity or irregularity of a time series. For a one-dimensional signal embedded in two dimensions, $1 \leq D \leq 2$, where $D = 1$ is a smooth curve and $D = 2$ fills the plane.

#### 2.3.1 Box-Counting Dimension

Overlay a grid of box size $\epsilon$ on the time series graph and count the number $N(\epsilon)$ of boxes that contain at least one data point:

$$D_{\text{box}} = \lim_{\epsilon \to 0} \frac{\log N(\epsilon)}{\log(1/\epsilon)}$$

In practice, compute $N(\epsilon)$ for a range of box sizes and take the slope of $\log N(\epsilon)$ vs. $\log(1/\epsilon)$. The method is straightforward but sensitive to data length and requires careful selection of the scaling region.

#### 2.3.2 Higuchi Fractal Dimension

The Higuchi method (1988) operates directly in the time domain without phase-space reconstruction. Given a time series $x(1), x(2), \ldots, x(N)$, construct new time series:

$$x_m^k = \{x(m), x(m+k), x(m+2k), \ldots, x(m+\lfloor(N-m)/k\rfloor \cdot k)\}$$

for $m = 1, 2, \ldots, k$, where $k$ is the interval length and $m$ is the initial time. The length of each curve $x_m^k$ is:

$$L_m(k) = \frac{1}{k}\left[\left(\sum_{i=1}^{\lfloor(N-m)/k\rfloor} |x(m+ik) - x(m+(i-1)k)|\right) \cdot \frac{N-1}{\lfloor(N-m)/k\rfloor \cdot k}\right]$$

The average length over all $m$ values is $\langle L(k) \rangle$. The Higuchi dimension is:

$$D_H = -\frac{d \log \langle L(k) \rangle}{d \log k}$$

estimated from the slope of $\log \langle L(k) \rangle$ vs. $\log k$ for $k = 1, 2, \ldots, k_{\max}$.

**Advantages for biophoton data**: Higuchi's method is computationally efficient, works well on short time series ($N \sim 100$--$1000$), and does not require embedding.

#### 2.3.3 Katz Fractal Dimension

The Katz method (1988) computes the fractal dimension directly from the waveform:

$$D_K = \frac{\log_{10}(n)}{\log_{10}(n) + \log_{10}(d/L)}$$

where $n$ is the number of steps in the time series, $L$ is the total path length:

$$L = \sum_{i=1}^{n} \sqrt{(t_{i+1}-t_i)^2 + (x_{i+1}-x_i)^2}$$

and $d$ is the maximum distance between the first point and any subsequent point:

$$d = \max_i \sqrt{(t_i - t_1)^2 + (x_i - x_1)^2}$$

The Katz dimension is fast to compute but less robust than Higuchi for short or noisy series.

### 2.4 Detrended Fluctuation Analysis (DFA) and Scaling Exponents

DFA, introduced by Peng et al. (1994), is the workhorse method for detecting long-range correlations in nonstationary time series. It is particularly important for biophoton data because emission rates can drift due to metabolic changes, temperature fluctuations, or dark-adaptation.

**Algorithm** (detailed for implementation):

**Step 1 -- Integration**. Given a time series $\{x_i\}_{i=1}^{N}$ with mean $\bar{x}$, compute the cumulative deviation (profile):

$$Y(k) = \sum_{i=1}^{k}(x_i - \bar{x}), \quad k = 1, 2, \ldots, N$$

**Step 2 -- Segmentation**. Divide $Y(k)$ into $N_s = \lfloor N/s \rfloor$ non-overlapping segments of length $s$. Since $N$ is generally not a multiple of $s$, repeat the procedure starting from the end of the series, yielding $2N_s$ segments total.

**Step 3 -- Local detrending**. In each segment $\nu$ ($\nu = 1, \ldots, 2N_s$), fit a polynomial of order $n$ (typically $n = 1$ for DFA-1, $n = 2$ for DFA-2, etc.) by least squares. Denote the fit as $\hat{Y}_\nu(k)$.

**Step 4 -- Variance computation**. For each segment $\nu$, compute the variance of the residuals:

$$F^2(\nu, s) = \frac{1}{s}\sum_{k=1}^{s}\left[Y((\nu-1)s + k) - \hat{Y}_\nu(k)\right]^2$$

For segments $\nu = N_s + 1, \ldots, 2N_s$ (from the end):

$$F^2(\nu, s) = \frac{1}{s}\sum_{k=1}^{s}\left[Y(N - (\nu - N_s)s + k) - \hat{Y}_\nu(k)\right]^2$$

**Step 5 -- Fluctuation function**. Average over all segments:

$$F(s) = \left[\frac{1}{2N_s}\sum_{\nu=1}^{2N_s}F^2(\nu, s)\right]^{1/2}$$

**Step 6 -- Scaling**. Repeat for a range of scales $s$ (typically $s_{\min} = 10$ to $s_{\max} = N/4$). The DFA exponent $\alpha$ is the slope of $\log F(s)$ vs. $\log s$:

$$F(s) \propto s^{\alpha}$$

**Interpretation of $\alpha$**:

| $\alpha$ | Process type |
|----------|-------------|
| 0.5 | White noise (uncorrelated) |
| $0 < \alpha < 0.5$ | Anti-correlated (anti-persistent) |
| $0.5 < \alpha < 1.0$ | Long-range correlated (persistent) |
| 1.0 | $1/f$ noise |
| 1.5 | Brownian motion (integrated white noise) |
| $\alpha > 1.0$ | Nonstationary, strongly persistent |

**Relationship to Hurst exponent**: For stationary signals ($\alpha < 1$), $H = \alpha$. For nonstationary signals ($\alpha > 1$), $H = \alpha - 1$.

**Biophoton-specific considerations**: At ultra-low count rates, many bins may contain zero counts. This creates a "floor" in the fluctuation function at small scales where $F(s)$ is dominated by Poisson noise rather than correlations. The crossover scale $s^*$ where correlations emerge above the Poisson background must be identified. One approach is to compute $F(s)$ for both the data and a Poisson surrogate with the same mean rate, and analyze only scales where $F_{\text{data}}(s) / F_{\text{Poisson}}(s)$ significantly exceeds 1.

### 2.5 Hurst Exponent Estimation and Long-Range Dependence

The Hurst exponent $H$ characterizes the tendency of a time series to either regress to the mean ($H < 0.5$), behave as a random walk ($H = 0.5$), or trend ($H > 0.5$). It is intimately connected to the autocorrelation decay and spectral exponent.

**Rescaled range (R/S) analysis** (the classical Hurst method):

For a time series of length $N$, divide into subseries of length $n$. For each subseries:

1. Compute mean $\bar{x}_n$ and standard deviation $S_n$.
2. Compute cumulative deviations $Y_k = \sum_{i=1}^{k}(x_i - \bar{x}_n)$.
3. Compute range $R_n = \max_k Y_k - \min_k Y_k$.
4. The rescaled range is $R_n / S_n$.

The Hurst exponent satisfies:

$$\mathbb{E}\left[\frac{R_n}{S_n}\right] \propto n^H$$

**Detrended moving average (DMA)**: An alternative that generalizes R/S analysis by replacing the global mean with a moving average, making it more robust to trends. The DMA fluctuation function is:

$$F_{\text{DMA}}^2(s) = \frac{1}{N-s}\sum_{k=s}^{N}\left[Y(k) - \tilde{Y}_s(k)\right]^2$$

where $\tilde{Y}_s(k) = \frac{1}{s}\sum_{j=0}^{s-1}Y(k-j)$ is the backward moving average.

**Fractional Brownian motion (fBm) model**: The Dlask et al. (2019) study used a fractional Brownian bridge model to analyze short biophoton time series. An fBm $B_H(t)$ with Hurst exponent $H$ has the covariance:

$$\text{Cov}[B_H(t), B_H(s)] = \frac{1}{2}\left(|t|^{2H} + |s|^{2H} - |t-s|^{2H}\right)$$

The fractional Brownian bridge constrains the process to return to zero at the endpoint, which is appropriate for analyzing autocorrelation within finite windows of biophoton data. Their finding of $H < 0.5$ (anti-correlated / negative memory) in mung bean autoluminescence suggests an active regulatory mechanism governing photon emission.

### 2.6 Multifractal Analysis (MFDFA)

Many biological signals exhibit *multifractal* behavior, meaning different statistical moments scale with different exponents. This is captured by the multifractal detrended fluctuation analysis (MFDFA), introduced by Kantelhardt et al. (2002).

**MFDFA Algorithm**:

Steps 1--3 are identical to standard DFA. Then:

**Step 4 -- Generalized variance**. For each segment $\nu$ and scale $s$:

$$F^2(\nu, s) = \frac{1}{s}\sum_{k=1}^{s}\left[Y((\nu-1)s+k) - \hat{Y}_\nu(k)\right]^2$$

**Step 5 -- Generalized fluctuation function**. For moment order $q$ (where $q$ can be any real number):

$$F_q(s) = \left[\frac{1}{2N_s}\sum_{\nu=1}^{2N_s}\left[F^2(\nu,s)\right]^{q/2}\right]^{1/q}$$

For $q = 0$, use the logarithmic average:

$$F_0(s) = \exp\left[\frac{1}{4N_s}\sum_{\nu=1}^{2N_s}\ln F^2(\nu,s)\right]$$

**Step 6 -- Generalized scaling exponent**. The generalized Hurst exponent $h(q)$ satisfies:

$$F_q(s) \propto s^{h(q)}$$

For a monofractal signal, $h(q) = \text{const}$ for all $q$. For a multifractal signal, $h(q)$ varies with $q$: positive $q$ emphasize large fluctuations, negative $q$ emphasize small fluctuations.

**Multifractal spectrum** (Legendre transform):

$$\tau(q) = qh(q) - 1$$

$$\alpha_H = \frac{d\tau}{dq} = h(q) + qh'(q)$$

$$f(\alpha_H) = q\alpha_H - \tau(q) = q[\alpha_H - h(q)] + 1$$

where $\alpha_H$ is the Holder (singularity) exponent and $f(\alpha_H)$ is the singularity spectrum. The width of the spectrum:

$$\Delta\alpha_H = \alpha_{H,\max} - \alpha_{H,\min}$$

quantifies the degree of multifractality. Broader spectra indicate richer, more heterogeneous scaling behavior.

**Application to biophotons**: Scholkmann et al. (2011) showed that multifractal parameters of UPE from germinating wheat seedlings could differentiate between control and potassium-dichromate-treated samples, even when linear statistical measures (mean, variance) showed no significant difference. The width $\Delta\alpha_H$ was the most discriminating parameter, suggesting that multifractal analysis captures information about biological state that is invisible to conventional statistics.

### 2.7 Entropy Measures

Entropy quantifies the complexity, irregularity, or information content of a time series. Several entropy measures are relevant to biophoton analysis.

#### 2.7.1 Shannon Entropy

For a discrete random variable $X$ with probability mass function $p(x_i)$:

$$H_S = -\sum_{i=1}^{n} p(x_i) \log_2 p(x_i)$$

Applied to binned photon counts, this measures the diversity of count values. A Poisson process with mean $\lambda$ has Shannon entropy:

$$H_{\text{Poisson}} = -\sum_{k=0}^{\infty} \frac{e^{-\lambda}\lambda^k}{k!}\log_2\left(\frac{e^{-\lambda}\lambda^k}{k!}\right)$$

Deviations from $H_{\text{Poisson}}$ at the same mean rate indicate non-Poissonian structure.

#### 2.7.2 Renyi Entropy

The Renyi entropy of order $q$ ($q \geq 0$, $q \neq 1$) generalizes Shannon entropy:

$$H_q^R = \frac{1}{1-q}\log_2\left(\sum_{i=1}^{n}p(x_i)^q\right)$$

As $q \to 1$, $H_q^R \to H_S$. For $q = 0$, $H_0^R = \log_2 n$ (Hartley entropy, depends only on the number of possible states). For $q = 2$, $H_2^R = -\log_2\left(\sum_i p_i^2\right)$ (collision entropy). The Renyi entropy spectrum $H_q^R$ as a function of $q$ provides a multiscale characterization of the probability distribution, analogous to the multifractal spectrum for fluctuations.

#### 2.7.3 Sample Entropy (SampEn)

Sample entropy (Richman & Moorman, 2000) quantifies the regularity of a time series by measuring the probability that sequences that are similar for $m$ consecutive points remain similar when extended to $m+1$ points:

$$\text{SampEn}(m, r, N) = -\ln\frac{A}{B}$$

where:
- $B$ = number of template matches of length $m$ within tolerance $r$ (i.e., pairs $(i,j)$ with $\max_{k=0,\ldots,m-1}|x_{i+k} - x_{j+k}| < r$, excluding self-matches)
- $A$ = number of template matches of length $m+1$ within the same tolerance $r$

Standard parameter choices: $m = 2$, $r = 0.15\sigma$ to $0.25\sigma$ where $\sigma$ is the standard deviation of the series.

**Interpretation**: Lower SampEn indicates more regularity/predictability; higher SampEn indicates more complexity/randomness. A Poisson process has relatively high SampEn, so values exceeding the Poisson expectation suggest additional randomness (possibly from measurement artifacts), while values below it suggest deterministic structure.

#### 2.7.4 Approximate Entropy (ApEn)

Approximate entropy (Pincus, 1991) is a precursor to SampEn that includes self-matches:

$$\text{ApEn}(m, r, N) = \Phi^m(r) - \Phi^{m+1}(r)$$

where $\Phi^m(r) = \frac{1}{N-m+1}\sum_{i=1}^{N-m+1}\ln C_i^m(r)$ and $C_i^m(r)$ is the fraction of sequences within distance $r$ of the $i$-th template of length $m$. ApEn is biased low for short series due to self-matching; SampEn is generally preferred.

#### 2.7.5 Distribution Entropy (DistEn)

Distribution entropy, used by Benfatto et al. (2025) in their multi-method biophoton analysis, estimates the Shannon entropy of the distance distribution from the distance matrix used in SampEn computation. Rather than counting threshold crossings, it constructs a histogram of all pairwise distances between embedded vectors and computes:

$$\text{DistEn}(m, B, N) = -\sum_{b=1}^{B}p_b\ln p_b$$

where $p_b$ is the proportion of distances falling in the $b$-th histogram bin ($B$ bins total). This avoids the threshold parameter $r$ and is more robust for short time series.

### 2.8 Diffusion Entropy Analysis (DEA)

DEA, developed by Scafetta and Grigolini (2002), measures the scaling of the probability density of the diffusion process generated by the time series, rather than its moments. This makes it robust to "strong anomalous diffusion" where different moments scale differently.

**Algorithm**:

1. Generate a diffusion trajectory from the data: $W(t) = \sum_{i=1}^{t}(x_i - \bar{x})$ (identical to the DFA profile).

2. For each time window $s$, compute the displacement $\Delta W_s = W(t+s) - W(t)$.

3. Estimate the probability density $p(\Delta W_s, s)$ of displacements at scale $s$ using a histogram or kernel density estimator.

4. Compute the Shannon entropy of the displacement distribution:

$$S(s) = -\int p(\Delta W, s) \ln p(\Delta W, s) \, d(\Delta W)$$

5. The scaling exponent $\delta$ is determined from:

$$S(s) = A + \delta \ln s$$

**Interpretation**: For standard diffusion (Brownian motion), $\delta = 0.5$. For subdiffusion, $\delta < 0.5$. For superdiffusion, $\delta > 0.5$. Unlike DFA, DEA correctly identifies the scaling exponent even when the scaling arises from fat-tailed waiting-time distributions (Levy processes) rather than long-range correlations.

**Crucial vs. non-crucial events**: The updated version of DEA used by Mahmoodi, Grigolini et al. (2021) in their biophoton study distinguishes between:
- **Crucial events**: Non-ergodic renewal events with power-law waiting times $\psi(t) \sim t^{-\mu}$ ($2 < \mu < 3$), generating complexity with a non-stationary correlation function. The DEA exponent is $\delta = 1/(\mu - 1)$.
- **Non-crucial events (FBM-type)**: Stationary but non-integrable correlation functions characteristic of fractional Brownian motion, where $\delta = H$ (the Hurst exponent).

Their finding that biophoton emission during seed germination transitions from a regime dominated by crucial events to one dominated by FBM-type correlations suggests a shift from event-driven (possibly quantum coherent) dynamics to continuous (classical) correlation dynamics as biological organization increases.

---

## 3. Current State of the Field

### 3.1 Dlask et al. (2019): Short-Time Fractal Analysis of Biological Autoluminescence

**Reference**: Dlask M, Kukal J, Poplova M, Sovka P, Cifra M. "Short-time fractal analysis of biological autoluminescence." *PLOS ONE* 14(7): e0214427 (2019).

**Key contributions**:

- Developed a rigorous methodology based on the **fractional Brownian bridge** (fBB) model to test whether short biophoton time series carry intrinsic temporal correlations.
- Applied the method to autoluminescence from **germinating mung beans** (*Vigna radiata*), measuring photon counts in bins of 10 ms.
- Introduced proper **reference signals** including Poisson surrogates and fractional Gaussian noise with known Hurst exponents, enabling calibration of the estimator for short sample lengths.
- **Main finding**: The autoluminescence signal exhibited **negative memory** ($H < 0.5$, anti-correlated), meaning that higher-than-average photon counts tend to be followed by lower-than-average counts and vice versa. This is *not* consistent with a purely random (Poisson) emission process.
- The anti-correlation was robust across multiple seeds and measurement runs, suggesting it reflects a genuine biological regulatory mechanism rather than instrumental artifact.

**Significance for myelin research**: The finding of anti-correlated emission challenges the assumption that biophoton streams are simply Poisson shot noise. If myelin waveguides filter or reshape the temporal statistics of propagating photons, the Hurst exponent of emission collected at the output of a myelinated axon should differ systematically from emission at the point of generation.

**Methodological note**: The fractional Brownian bridge approach is particularly well-suited for biophoton analysis because it (a) works with short time series ($N \sim 50$--$500$), (b) does not assume stationarity within the analysis window, and (c) provides a maximum likelihood estimator for $H$ with quantified uncertainty.

### 3.2 Berke et al. (2024): Entropy-Weighted Spectral Fractal Dimension for Embryo Viability

**Reference**: Berke J, Gulyas I, Bognar Z, Berke D, Enyedi A. "Unique algorithm for the evaluation of embryo photon emission and viability." *Scientific Reports* 14: 15066 (2024).

**Key contributions**:

- Developed the **entropy-weighted spectral fractal dimension (EWSFD)**, a novel composite metric that combines the information content (Shannon entropy) with the self-similar spectral structure (spectral fractal dimension) of UPE time series.
- Applied this to spontaneous photon emission from **mouse embryos** measured with a Hamamatsu photon-counting camera.
- Demonstrated that the EWSFD can distinguish between:
  - **Living vs. degenerated** embryos
  - **Fresh vs. frozen-thawed** embryos
  - **Embryos vs. background** (empty chamber)
- The spectral fractal dimension alone was less discriminating than the entropy-weighted version, indicating that both the complexity and the self-similarity of the emission carry independent biological information.

**Significance for myelin research**: The EWSFD approach demonstrates that fractal analysis of UPE has practical diagnostic value for assessing tissue viability. The same methodology could be applied to distinguish healthy myelinated tissue from demyelinated tissue (Track 06), with the hypothesis that myelin integrity is reflected in the spectral fractal structure of emission.

### 3.3 Mahmoodi, Grigolini et al. (2021): Diffusion Entropy Analysis for Quantum Coherence

**Reference**: Mahmoodi K, West BJ, Grigolini P. "Biophotons and Emergence of Quantum Coherence -- A Diffusion Entropy Analysis." *Entropy* 23(5): 554 (2021).

**Key contributions**:

- Applied an updated version of **diffusion entropy analysis** (DEA) to photon emission during lentil seed germination, using a sensitive PMT-based detection system.
- Distinguished between two fundamentally different sources of complexity: (a) **crucial events** -- intermittent, non-ergodic renewal events with power-law waiting-time distributions, and (b) **FBM-type** correlations -- stationary, long-memory processes.
- **Dark count control**: Showed that the dark count signal (no seeds present) yields ordinary scaling ($\delta = 0.5$), confirming that the method detects genuine biological signal rather than instrumental artifacts.
- **Phase transition interpretation**: During germination, the photon emission transitions from a regime with **crucial events** (interpreted as signatures of quantum coherence during early metabolic activation) to a regime dominated by **FBM correlations** (interpreted as classical statistical coordination). The transition is accompanied by changes in the DEA scaling exponent.
- Argued that crucial events correspond to the spontaneous breaking of temporal symmetry, which can be associated with quantum coherent emission processes.

**Significance for myelin research**: If myelin waveguides support coherent photon propagation, the DEA approach could detect coherence through the presence of crucial events in the output photon stream. The transition between crucial-event and FBM regimes might serve as a marker for the degree of coherent coupling in the waveguide.

### 3.4 Popp's Delayed Luminescence: Hyperbolic Decay as Coherence Signature

**References**:
- Popp FA, Li KH. "Hyperbolic relaxation as a sufficient condition of a fully coherent ergodic field." *Int. J. Theor. Phys.* 32: 1573--1583 (1993).
- Popp FA. "About the coherence of biophotons." In: *Macroscopic Quantum Coherence*, World Scientific (1999).
- Bajpai RP. "Quantum coherence of biophotons and living systems." *Indian J. Exp. Biol.* 41: 514--527 (2003).

**Theoretical framework**: When a biological system is illuminated briefly and then the light source is removed, the subsequent afterglow is called **delayed luminescence** (DL). The temporal decay of DL intensity carries information about the coherence of the emitting system:

**Coherent (ergodic) decay**:

$$I(t) = \frac{I_0}{(1 + \lambda t)^2}$$

or more generally $I(t) \propto t^{-\beta}$ with $\beta \approx 2$, which is the hallmark of a system where many oscillators are coherently coupled and share energy. The hyperbolic decay arises because the probability of photon emission from a coherent state $|\alpha\rangle$ with decaying amplitude $\alpha(t) = \alpha_0/(1+\lambda t)$ gives $|\alpha(t)|^2 \propto 1/(1+\lambda t)^2$.

**Incoherent (exponential) decay**:

$$I(t) = I_0 e^{-t/\tau}$$

characteristic of independent emitters with a single relaxation time $\tau$. Multiple independent pools give multi-exponential decay $I(t) = \sum_j A_j e^{-t/\tau_j}$.

**Fitting protocol**: Given a DL time series $I(t_i)$, fit both models and compare using information criteria (AIC/BIC):

- Hyperbolic: $I(t) = A(1+\lambda t)^{-\beta}$, parameters $\{A, \lambda, \beta\}$
- Multi-exponential: $I(t) = \sum_{j=1}^{K}A_j e^{-t/\tau_j}$, parameters $\{A_j, \tau_j\}$

The parameter $\beta$ in the hyperbolic fit is informative: $\beta = 2$ corresponds to a fully coherent field; deviations from 2 indicate partial coherence or a mixture of coherent and incoherent contributions.

**Stretched exponential alternative**: A Kohlrausch-Williams-Watts (KWW) stretched exponential $I(t) = A \exp[-(t/\tau)^{\beta_{\text{KWW}}}]$ with $0 < \beta_{\text{KWW}} < 1$ can sometimes fit DL data comparably well and represents a distribution of relaxation times without requiring coherence. Model selection must be principled.

**Critical assessment**: The coherence interpretation of hyperbolic DL remains debated. The critical review by Cifra and Pospisil (2014) noted that indirect evidence for coherence is suggestive but not conclusive, and that hyperbolic-like decay can arise from non-coherent mechanisms including distributions of exponential relaxation rates. Nevertheless, the decay curve shape remains a valuable phenomenological tool for characterizing biological state.

### 3.5 Benfatto et al. (2025): Multi-Method Analysis Pipeline

**Reference**: Benfatto M, De Paolis G, Tonello L, Grigolini P. "Advanced Data Analysis of Spontaneous Biophoton Emission: A Multi-Method Approach." *arXiv:2511.11080* (2025).

**Key contributions**:

- Established a comprehensive, benchmarked **multi-method analysis pipeline** for biophoton photon-count time series, combining:
  - Distribution entropy analysis (DistEn)
  - Renyi entropy
  - Detrended fluctuation analysis (DFA)
  - Multifractal DFA (MFDFA)
  - Tail-statistics characterization
- Validated the pipeline against **surrogate signals**: Poisson processes, fractional Gaussian noise (FGN), and renewal processes with power-law waiting times, demonstrating sensitivity and specificity for memory, intermittency, and multifractality.
- Showed that across all methods, a **coherent hierarchy of dynamical regimes** is recovered, providing internal methodological consistency -- i.e., the different methods agree on the classification of dynamical behavior, increasing confidence in results obtained from any single method.

**Significance**: This paper provides the closest thing to a turnkey analysis protocol for biophoton time series and should serve as a reference implementation for the methodology proposed in this track.

### 3.6 Scholkmann et al. (2011): Multifractal Differentiation of Toxicological States

**Reference**: Scholkmann F, Cifra M, Moraes TA, de Mello Gallep C. "Using multifractal analysis of ultra-weak photon emission from germinating wheat seedlings to differentiate between two grades of intoxication with potassium dichromate." *J. Phys. Conf. Ser.* 329: 012020 (2011).

**Key contributions**:

- Applied MFDFA to UPE from germinating wheat seedlings (*Triticum aestivum*) treated with two concentrations of potassium dichromate (25 ppm and 150 ppm).
- The **multifractal spectrum width** $\Delta\alpha_H$ was the most discriminating parameter, with statistically significant differences ($p < 0.05$) between control, low-dose, and high-dose groups.
- Linear statistical measures (mean intensity, variance) showed no significant difference between groups, demonstrating that multifractal analysis captures hidden information about biological state.

**Significance**: This is direct evidence that the multifractal structure of UPE is biologically meaningful and can serve as a sensitive biomarker. The approach can be directly transferred to the question of whether myelin damage alters the multifractal properties of neural biophoton emission.

### 3.7 Belksma (2024): RQA Applied to Human UPE

**Reference**: Belksma R. "Temporal Variability in Ultra-weak Photon Emission." Master's thesis, Utrecht University (2024).

**Key contributions**:

- Applied **recurrence quantification analysis** (RQA) to ultra-weak photon emission measured from human palms and forearms.
- Used time-delay embedding with mutual information (for delay $\tau$) and false nearest neighbors (for embedding dimension $m$).
- Computed RQA metrics: recurrence rate (RR), determinism (DET), laminarity (LAM), and trapping time (TT).
- Found intermittent short-lived deterministic structures in palm emission, suggesting transient physiological regulation reflected in UPE temporal patterns.

---

## 4. Mathematical Framework

### 4.1 Full DFA Formulation for Photon Count Time Series

For a photon count time series $\{n_i\}_{i=1}^{N}$ where $n_i \in \{0, 1, 2, \ldots\}$ is the number of photons detected in the $i$-th time bin of width $\Delta t$, we must address several issues specific to ultra-low count data.

**Preprocessing**:

1. **Mean subtraction vs. centering**: Compute $\bar{n} = \frac{1}{N}\sum_{i=1}^{N}n_i$ and form the profile $Y(k) = \sum_{i=1}^{k}(n_i - \bar{n})$. For very low count rates ($\bar{n} \ll 1$), most $n_i = 0$, and the profile is a nearly monotone decreasing function punctuated by upward jumps at photon arrivals. This is mathematically valid for DFA but can create artifacts at small scales.

2. **Bin aggregation**: If the raw time resolution is $\Delta t$ (e.g., 10 ms for a PMT), consider aggregating into coarser bins of width $M\Delta t$ before DFA. The optimal aggregation level balances temporal resolution against the need for sufficient counts per bin. A rule of thumb: $M$ should be chosen so that $\bar{n}_M = M\bar{n} \gtrsim 0.5$, ensuring that at least half the bins are non-zero.

3. **Nonstationarity removal**: Slow drifts in emission rate (e.g., from metabolic trends over minutes) can create spurious long-range correlations. DFA handles polynomial trends via the detrending step, but it is still advisable to check for and remove gross trends (e.g., a monotone increase in emission during wound healing) before analysis.

**Scale selection**: Choose the range of scales $s$ as:

$$s \in \{s_1, s_2, \ldots, s_K\}$$

where $s_k$ are logarithmically spaced between $s_{\min}$ and $s_{\max}$:

$$s_k = s_{\min} \cdot \left(\frac{s_{\max}}{s_{\min}}\right)^{(k-1)/(K-1)}, \quad k = 1, \ldots, K$$

with $s_{\min} \geq 4n_{\text{poly}}$ (where $n_{\text{poly}}$ is the detrending polynomial order + 1) and $s_{\max} \leq N/4$. Using $K = 30$--$50$ logarithmically spaced scales provides sufficient resolution for the log-log fit.

**Poisson floor**: The expected DFA fluctuation function for a Poisson process with rate $\lambda$ is:

$$F_{\text{Poisson}}(s) = \sqrt{\lambda \cdot s \cdot \Delta t} \cdot s^{-1/2} \cdot C_{\text{end}} \approx \sqrt{\lambda \Delta t} \cdot C_{\text{end}}$$

Wait -- more precisely, for a Poisson process, the integrated profile $Y(k)$ has variance:

$$\text{Var}[Y(k)] = k \cdot \text{Var}[n_i] = k \cdot \lambda\Delta t$$

After linear detrending within a window of size $s$, the residual variance scales as $F^2(s) \propto s \cdot \lambda\Delta t / 12$, giving:

$$F_{\text{Poisson}}(s) \propto \sqrt{\lambda\Delta t} \cdot s^{1/2}$$

Hence $\alpha_{\text{Poisson}} = 0.5$, as expected. In practice, for ultra-low-rate data, finite-size and discreteness effects can cause deviations from the theoretical $\alpha = 0.5$ at small scales. Always compare data DFA against Poisson surrogates generated with the same mean rate.

### 4.2 Multifractal Spectrum Width as Biological State Indicator

The multifractal spectrum $f(\alpha_H)$ can be parameterized by its key features:

- **$\alpha_0$**: The singularity exponent at which $f(\alpha_H)$ is maximum. This corresponds to the most prevalent scaling behavior.
- **$\Delta\alpha_H = \alpha_{\max} - \alpha_{\min}$**: The spectrum width, measuring the degree of multifractality.
- **Asymmetry** $A = (\alpha_0 - \alpha_{\min})/(\alpha_{\max} - \alpha_0)$: Left-skewed ($A > 1$) spectra indicate dominance of large fluctuations; right-skewed ($A < 1$) spectra indicate dominance of small fluctuations.
- **$f(\alpha_{\min})$ and $f(\alpha_{\max})$**: The fractal dimensions of the subsets where the strongest and weakest singularities reside.

**Biological state mapping** (proposed):

| State | Expected $\alpha_0$ | Expected $\Delta\alpha_H$ | Rationale |
|-------|---------------------|---------------------------|-----------|
| Healthy myelinated tissue | $\sim 0.5$--$0.7$ | Wide ($> 0.3$) | Rich multiscale regulation; waveguide filtering introduces scale-dependent correlations |
| Demyelinated tissue | $\sim 0.5$ | Narrow ($< 0.2$) | Loss of waveguide structure reduces modal filtering; emission approaches Poisson |
| Metabolically stressed | $> 0.7$ | Wide ($> 0.4$) | Bursting dynamics from ROS cascades |
| Dead/fixed tissue | $\sim 0.5$ | Near zero | Chemiluminescent afterglow is exponentially decaying, monofractal |

These are hypotheses to be tested, not established results.

### 4.3 Wavelet Transform Modulus Maxima (WTMM) Method

WTMM provides an alternative to MFDFA for multifractal analysis that is better suited for detecting isolated singularities and handling nonstationarities.

**Algorithm**:

1. Compute the continuous wavelet transform (CWT) of the signal $x(t)$ using an analyzing wavelet $\psi(t)$:

$$W_\psi[x](a, b) = \frac{1}{a}\int_{-\infty}^{\infty}x(t)\psi^*\left(\frac{t-b}{a}\right)dt$$

where $a > 0$ is the scale and $b$ is the translation. The wavelet is typically chosen as the $n$-th derivative of a Gaussian: $\psi^{(n)}(t) = \frac{d^n}{dt^n}e^{-t^2/2}$ (the choice of $n$ determines how many polynomial trends are removed).

2. At each scale $a$, identify the **local maxima** of $|W_\psi[x](a, b)|$ with respect to $b$. These maxima form curves ("maxima lines") in the $(a, b)$ plane.

3. Follow the maxima lines from fine to coarse scales. The partition function is:

$$Z(q, a) = \sum_{\ell \in \mathcal{L}(a)} \left|\sup_{(a', b') \in \ell, a' \leq a} W_\psi[x](a', b')\right|^q$$

where $\mathcal{L}(a)$ is the set of all maxima lines passing through scale $a$.

4. The scaling exponent $\tau(q)$ is obtained from:

$$Z(q, a) \propto a^{\tau(q)}$$

5. The singularity spectrum is obtained via Legendre transform as in Section 2.6.

**Advantages over MFDFA**: WTMM naturally handles nonstationarities, provides better localization of singularities in time, and is theoretically more principled for multifractal analysis. **Disadvantages**: Computationally more expensive, requires careful selection of the analyzing wavelet, and the maxima-line tracking can be unstable for noisy data.

**Recommended wavelet for biophoton data**: The Mexican hat wavelet ($n = 2$ Gaussian derivative) provides a good compromise between time and frequency localization. For data where linear trends are common, use $n = 3$ (third derivative) to ensure trend removal.

### 4.4 Recurrence Quantification Analysis (RQA) for Nonlinear Dynamics

RQA characterizes the recurrence structure of a dynamical system by constructing and analyzing a recurrence plot.

**Phase space reconstruction**: Given the scalar time series $\{x_i\}$, construct delay vectors:

$$\mathbf{x}_i = (x_i, x_{i+\tau}, x_{i+2\tau}, \ldots, x_{i+(m-1)\tau})$$

where:
- **Embedding dimension** $m$ is determined by the false nearest neighbors (FNN) algorithm: systematically increase $m$ until the fraction of false neighbors drops below a threshold (typically 1--5%).
- **Time delay** $\tau$ is determined by the first minimum of the mutual information function $I(\tau)$, which measures nonlinear statistical dependence between $x_i$ and $x_{i+\tau}$.

**Recurrence matrix**:

$$R_{ij}(\varepsilon) = \Theta(\varepsilon - \|\mathbf{x}_i - \mathbf{x}_j\|)$$

where $\Theta$ is the Heaviside step function and $\varepsilon$ is the recurrence threshold. Typical choice: $\varepsilon = 0.1\sigma$ to $0.3\sigma$ where $\sigma$ is the standard deviation of the embedded vectors.

**RQA metrics**:

- **Recurrence rate** (RR): Density of recurrence points.

$$\text{RR} = \frac{1}{N_r^2}\sum_{i,j=1}^{N_r}R_{ij}$$

- **Determinism** (DET): Fraction of recurrence points forming diagonal lines of length $\geq l_{\min}$ (typically $l_{\min} = 2$).

$$\text{DET} = \frac{\sum_{l=l_{\min}}^{N_r}l \cdot P(l)}{\sum_{i,j}R_{ij}}$$

  where $P(l)$ is the histogram of diagonal line lengths. Higher DET indicates more deterministic (less random) dynamics.

- **Average diagonal line length** ($L$): Mean length of diagonal lines.

$$L = \frac{\sum_{l=l_{\min}}^{N_r}l \cdot P(l)}{\sum_{l=l_{\min}}^{N_r}P(l)}$$

  Related to the prediction horizon of the system.

- **Entropy of diagonal lines** ($\text{ENTR}$): Shannon entropy of the distribution of diagonal line lengths, measuring the complexity of the deterministic structure.

- **Laminarity** (LAM): Fraction of recurrence points forming vertical lines of length $\geq v_{\min}$.

$$\text{LAM} = \frac{\sum_{v=v_{\min}}^{N_r}v \cdot P(v)}{\sum_{i,j}R_{ij}}$$

  Higher LAM indicates more intermittent behavior (the system gets "trapped" in certain states).

- **Trapping time** (TT): Average length of vertical structures.

$$\text{TT} = \frac{\sum_{v=v_{\min}}^{N_r}v \cdot P(v)}{\sum_{v=v_{\min}}^{N_r}P(v)}$$

**Biophoton-specific adaptations**: For ultra-low count data, the embedding must account for the discrete (integer) nature of photon counts. The Euclidean norm may not be the best distance metric; consider the Chebyshev (maximum) norm. The recurrence threshold $\varepsilon$ should be set relative to the data range (not just $\sigma$), and its sensitivity should be tested.

### 4.5 Transfer Entropy for Directional Information Flow

Transfer entropy (Schreiber, 2000) quantifies the directed information flow from a source time series $X$ to a target time series $Y$:

$$T_{X \to Y} = \sum p(y_{t+1}, y_t^{(k)}, x_t^{(l)}) \log_2 \frac{p(y_{t+1} | y_t^{(k)}, x_t^{(l)})}{p(y_{t+1} | y_t^{(k)})}$$

where $y_t^{(k)} = (y_t, y_{t-1}, \ldots, y_{t-k+1})$ and $x_t^{(l)} = (x_t, x_{t-1}, \ldots, x_{t-l+1})$ are the past histories of length $k$ and $l$ respectively.

**Interpretation**: $T_{X \to Y} > 0$ means that knowing the past of $X$ improves prediction of $Y$ beyond what the past of $Y$ alone provides. This is a model-free measure of Granger causality.

**Application to multi-site biophoton recording**: If photon emission is measured simultaneously at multiple points along a myelinated nerve (or at different nodes of Ranvier), transfer entropy can reveal:

- **Directional propagation**: Is information flowing preferentially in one direction along the nerve?
- **Waveguide coupling**: Is the photon emission at downstream sites influenced by emission at upstream sites, with a lag consistent with waveguide propagation speed?
- **Feedback loops**: Are there recurrent information flows suggesting resonant cavity effects within myelin internodes?

**Practical estimation for low-count data**: Transfer entropy estimation is notoriously data-hungry. For biophoton data with low count rates, use:
- Symbolic transfer entropy (discretize the time series into symbols based on rank ordering)
- Bayesian estimation (e.g., the NSB estimator) to correct for finite-sample bias
- Kraskov-Stogbauer-Grassberger (KSG) $k$-nearest-neighbor estimator for continuous embedding

### 4.6 Adaptations for Ultra-Low Count Rate Time Series

Biophoton emission from single cells or small tissue samples typically yields count rates of 1--100 photons per second, far below the rates encountered in most time-series analysis applications. This creates specific challenges:

#### 4.6.1 Zero-Inflation

At fine temporal resolution (e.g., 1 ms bins), most bins contain zero counts. This is not pathological -- it is the expected behavior of a low-rate Poisson process. However, it means:

- **Autocorrelation estimates** are dominated by $(0 - \bar{n})(0 - \bar{n}) = \bar{n}^2$ pairs, with rare $(k - \bar{n})(0 - \bar{n})$ terms. The ACF estimate has very large variance.
- **Fractal dimension methods** that assume continuous-valued signals (Higuchi, Katz) may produce artifacts when applied directly to binary-like (0 or 1) count data.
- **Entropy measures** have limited dynamic range: the entropy of a binary (0/1) distribution is at most 1 bit.

**Mitigation strategies**:

1. **Bin aggregation**: Increase bin width until $\bar{n}_{\text{bin}} \geq 3$--$5$. For a 10 photon/s source, this means bins of 300--500 ms. This sacrifices temporal resolution below the bin width.

2. **Inter-photon interval (IPI) analysis**: Instead of analyzing the count time series, analyze the sequence of time intervals between consecutive photon detections. For a Poisson process, IPIs are exponentially distributed: $p(\Delta t) = \lambda e^{-\lambda \Delta t}$. Deviations indicate temporal structure. Apply DFA, MFDFA, or entropy measures to the IPI sequence. *Advantage*: no zero-count problem; every data point is a genuine photon event. *Disadvantage*: unevenly sampled in calendar time.

3. **Point process methods**: Treat the photon arrivals as a point process $\{t_1, t_2, \ldots, t_n\}$ and use methods designed for point processes:
   - **Conditional intensity function**: $\lambda(t | \mathcal{H}_t) = \lim_{\Delta t \to 0}\frac{P(\text{event in }[t, t+\Delta t) | \mathcal{H}_t)}{\Delta t}$
   - **Allan variance**: $\sigma_A^2(\tau) = \frac{1}{2}\langle(n_{k+1} - n_k)^2\rangle$ for non-overlapping bins of width $\tau$. The scaling $\sigma_A^2(\tau) \propto \tau^{\beta}$ reveals: $\beta = -1$ (white noise), $\beta = 0$ (flicker/1/f noise), $\beta = 1$ (random walk).

4. **Wavelet leaders for discrete data**: The wavelet leader multifractal formalism (Jaffard, 2004) can be adapted for integer-valued data and is more robust than MFDFA for short, noisy series.

#### 4.6.2 Dark Count Subtraction

PMT dark counts (typically 1--50 counts/s for cooled PMTs) can constitute a significant fraction of the total count rate. Simple subtraction of the mean dark rate is insufficient because dark counts add their own (Poisson) temporal structure. Proper treatment:

1. Measure the dark count time series $\{d_i\}$ in a separate run with no sample.
2. Compute the DFA/MFDFA of both the sample+dark signal $\{n_i\}$ and the dark-only signal $\{d_i\}$.
3. Compare scaling exponents. If $\alpha_{\text{sample}} \neq \alpha_{\text{dark}}$, the difference is attributable to the biological signal.
4. For a more rigorous treatment, use the variance subtraction: $F^2_{\text{bio}}(s) = F^2_{\text{total}}(s) - F^2_{\text{dark}}(s)$, valid when the biological signal and dark counts are independent.

#### 4.6.3 Detector Dead Time and Afterpulsing

- **Dead time** ($\tau_d \sim 10$--$100$ ns for PMTs): After detecting a photon, the detector is insensitive for a period $\tau_d$. This creates artificial anti-correlation at time scales near $\tau_d$. At the bin widths typically used for biophoton analysis ($\geq 1$ ms), this is negligible for low count rates ($\lambda \tau_d \ll 1$).
- **Afterpulsing**: False secondary pulses occurring 0.1--10 microseconds after a genuine detection. This creates artificial positive correlation at short time scales. Correct by identifying and removing afterpulse clusters, or restrict analysis to time scales $\gg$ the afterpulsing time constant.

---

## 5. Research Opportunities

### 5.1 Fractal Scaling Exponents as Discriminators of Myelinated vs. Unmyelinated Tissue

**Hypothesis**: If myelin sheaths function as optical waveguides, they impose mode-selective filtering on propagating photons. This filtering should reshape the temporal statistics of the output photon stream, producing distinctive scaling exponents compared to unmyelinated tissue where photons propagate diffusively.

**Specific predictions**:

- **DFA exponent**: Myelinated tissue emission should show $\alpha > 0.5$ (positive long-range correlations) due to the resonant modal structure of the waveguide, which creates temporal coherence. Unmyelinated tissue should show $\alpha \approx 0.5$ (Poisson-like) or $\alpha < 0.5$ (anti-correlated, if regulatory mechanisms dominate).
- **Multifractal spectrum width**: Myelinated tissue should show broader $\Delta\alpha_H$ because the waveguide supports multiple modes with different propagation characteristics, each contributing a different scaling behavior.
- **Hurst exponent**: The waveguide's finite propagation time (estimated at $\sim 10^8$ m/s for visible light in myelin with $n \approx 1.44$, giving $\sim 10$ ns transit time per internode) introduces a characteristic correlation time that should appear as a crossover in the DFA fluctuation function.

**Experimental design**:

1. *Ex vivo* comparison: Measure UPE from excised sciatic nerve (heavily myelinated) vs. vagus nerve (mixed myelinated/unmyelinated C-fibers) vs. dorsal root (cell bodies, unmyelinated) under identical metabolic conditions. Compare DFA exponents, multifractal spectra, and entropy measures.
2. *Demyelination perturbation*: Treat myelinated nerve samples with lysolecithin or cuprizone to induce demyelination. Track changes in fractal scaling exponents over time.

### 5.2 Temporal Correlation Structure as Probe of Waveguide Coupling

The temporal autocorrelation function of photons exiting a dielectric waveguide depends on the input photon statistics, the waveguide geometry, and the coupling efficiency. For a multimode waveguide with $M$ guided modes:

$$C_{\text{out}}(k) = \sum_{m=1}^{M}\eta_m^2 C_{\text{in}}(k - \Delta t_m) + \text{cross terms}$$

where $\eta_m$ is the coupling efficiency into mode $m$ and $\Delta t_m$ is the group delay of mode $m$. The spread in group delays $\{\Delta t_m\}$ creates temporal broadening (modal dispersion) that appears as positive autocorrelation at lags corresponding to the intermodal delay spread.

**Observable signature**: If the intermodal delay spread is $\Delta T_{\text{modal}}$, the autocorrelation function should show a characteristic feature (bump or broadening) at lags $\sim \Delta T_{\text{modal}}$. For a myelin internode of length $L \sim 1$ mm with refractive index difference $\Delta n \sim 0.02$ between the fundamental and first higher-order mode, the delay spread is:

$$\Delta T_{\text{modal}} \sim \frac{L \Delta n}{c} \sim \frac{10^{-3} \times 0.02}{3 \times 10^8} \sim 0.07 \text{ ps}$$

This is far below the temporal resolution of any photon counter ($\sim$ ns), so modal dispersion per se is not directly observable. However, coherent interference between modes (beating) at longer time scales *could* produce modulation of the emission rate at detectable frequencies.

### 5.3 Multi-Site Recording: Cross-Correlation Between Emission Sites

**Concept**: Record biophoton emission simultaneously from two or more positions along a myelinated nerve. If the myelin waveguide transports photons, then emission at a downstream site should be correlated with -- and temporally lagged relative to -- emission at an upstream site.

**Cross-correlation function**:

$$C_{XY}(\tau) = \frac{\langle(X(t) - \bar{X})(Y(t+\tau) - \bar{Y})\rangle}{\sigma_X \sigma_Y}$$

A peak in $C_{XY}(\tau)$ at $\tau = \tau^* > 0$ indicates that $X$ leads $Y$ by time $\tau^*$, consistent with photon propagation from $X$ to $Y$.

**Challenges**: At ultra-low count rates, the signal-to-noise ratio of the cross-correlation is:

$$\text{SNR}_{C_{XY}} \approx \sqrt{N_{\text{pairs}}} \cdot |C_{XY}|$$

where $N_{\text{pairs}}$ is the number of coincident-bin pairs. For $|C_{XY}| \sim 0.01$ and $10^5$ bins, $\text{SNR} \sim 3$: marginal but potentially detectable.

**Transfer entropy enhancement**: Transfer entropy (Section 4.5) is more sensitive than cross-correlation for detecting nonlinear, directional coupling and can work even when the coupling is intermittent or state-dependent.

### 5.4 Real-Time Fractal Dimension as Biomarker for Myelin Integrity

**Vision**: Develop a sliding-window analysis that continuously computes the Higuchi fractal dimension (or DFA exponent) of the photon count stream, providing a real-time readout of tissue state.

**Implementation**:

1. Use a sliding window of width $W$ (e.g., $W = 1000$ bins = 10 s at 100 ms binning).
2. At each time step, compute $D_H$ or $\alpha_{\text{DFA}}$ within the window.
3. Track the temporal evolution of the fractal exponent: $D_H(t)$, $\alpha(t)$.
4. Define alarm thresholds based on baseline measurements from healthy tissue.

**Potential applications**:

- Intraoperative monitoring during neurosurgery (detecting inadvertent nerve damage).
- Longitudinal monitoring of demyelination progression in animal models of MS.
- Drug screening: testing remyelination therapies by monitoring recovery of fractal scaling.

**Computational requirements**: Higuchi's algorithm on a 1000-point window requires $O(k_{\max} \cdot N)$ operations, which is easily real-time even on modest hardware.

---

## 6. Proposed Methodology

### 6.1 Optimal Binning Strategies for Ultra-Low-Rate Photon Streams

The choice of bin width $\Delta t$ determines the trade-off between temporal resolution and count statistics:

| Bin width | Mean count ($\bar{n}$) at 10 ph/s | Fraction zero bins | Suitable methods |
|-----------|----------------------------------|--------------------|-----------------|
| 1 ms | 0.01 | 99% | IPI analysis only |
| 10 ms | 0.1 | 90% | IPI analysis, point process |
| 100 ms | 1.0 | 37% | DFA, entropy (marginal) |
| 500 ms | 5.0 | 0.7% | All methods |
| 1 s | 10.0 | $<0.01$% | All methods, good statistics |
| 10 s | 100.0 | $\approx 0$ | All methods, excellent statistics, poor temporal resolution |

**Recommended strategy**: Perform analysis at multiple bin widths and check for consistency of scaling exponents across scales. The *true* scaling behavior should be independent of binning above the correlation time of the process.

**Multi-resolution approach**:

1. Start with the finest available temporal resolution.
2. Compute the Allan variance $\sigma_A^2(\tau)$ as a function of bin width $\tau$.
3. Identify the regime where $\sigma_A^2(\tau)$ transitions from Poisson-dominated ($\sigma_A^2 \approx \bar{n}$) to correlation-dominated behavior.
4. Set the minimum bin width for DFA/MFDFA analysis at this crossover scale.

### 6.2 Surrogate Data Testing

Surrogate data testing is essential for determining whether observed temporal structure is statistically significant or could arise from trivial processes.

#### 6.2.1 Null Hypotheses and Surrogate Types

| Null hypothesis | Surrogate type | Construction | What it preserves |
|----------------|---------------|--------------|-------------------|
| H0: Independent Poisson process | **Shuffled surrogates** | Randomly permute the time series | Amplitude distribution, mean, variance |
| H0: Linear stochastic process (correlated Gaussian) | **Phase-randomized (FT) surrogates** | Take FFT, randomize phases uniformly on $[0, 2\pi)$, inverse FFT | Power spectrum, amplitude distribution (approximately) |
| H0: Linear stochastic process with exact amplitude distribution | **IAAFT surrogates** | Iteratively adjust amplitude distribution and power spectrum | Power spectrum AND amplitude distribution (both exactly) |
| H0: Poisson process with time-varying rate | **Rate-matched Poisson surrogates** | Estimate local rate $\lambda(t)$ by smoothing, generate Poisson draws with rate $\lambda(t)$ | Mean rate trajectory |

#### 6.2.2 IAAFT Algorithm (Iterative Amplitude Adjusted Fourier Transform)

The IAAFT algorithm (Schreiber & Schmitz, 1996) proceeds as follows:

1. Sort the original data $\{x_i\}$ to get the sorted amplitudes $\{x_{\text{sorted}}\}$.
2. Compute the Fourier amplitudes $|X(f)|$ of the original data.
3. **Initialize**: Create a random shuffle of $\{x_i\}$; call it $\{s_i^{(0)}\}$.
4. **Iterate**:
   a. Compute FFT of $\{s_i^{(n)}\}$; replace the Fourier amplitudes with $|X(f)|$ while keeping the phases; inverse FFT to get $\{r_i^{(n)}\}$.
   b. Rank-order $\{r_i^{(n)}\}$ and replace values with the corresponding rank-ordered original values: $s_i^{(n+1)} = x_{\text{sorted}}[\text{rank}(r_i^{(n)})]$.
5. **Converge**: Repeat until the power spectrum of the surrogate matches the original to within tolerance.

**For integer-valued photon count data**: The standard IAAFT assumes continuous-valued data. For discrete photon counts, use the **randomized rank** variant: when multiple data points have the same value (which is frequent for $n = 0, 1, 2$ counts), randomly break ties in the ranking step.

#### 6.2.3 Testing Protocol

1. Generate $N_s = 99$ surrogates (for a two-tailed test at $p = 0.02$) or $N_s = 999$ (for $p = 0.002$).
2. Compute the test statistic $T$ (e.g., DFA exponent $\alpha$, multifractal width $\Delta\alpha_H$, or sample entropy) for the original data and all surrogates.
3. Rank the original among the surrogates. The p-value is:

$$p = \frac{2 \min(r, N_s + 1 - r)}{N_s + 1}$$

where $r$ is the rank of the original statistic.

4. If $p < 0.05$, reject the null hypothesis: the observed temporal structure is not consistent with the surrogate-generating process.

### 6.3 Analysis Pipeline

The following pipeline implements the multi-method approach of Benfatto et al. (2025), adapted for biophoton emission from neural tissue.

#### Stage 1: Data Acquisition and Preprocessing

```
Input: Raw photon timestamps {t_1, t_2, ..., t_n}
    or binned counts {n_1, n_2, ..., n_N} with bin width Delta_t

1. Quality control:
   - Remove first 30 min of recording (dark adaptation)
   - Flag and remove intervals with anomalous count rates
     (>5 sigma from local mean, likely cosmic ray events)
   - Check for afterpulsing: compute IPI histogram, look for
     excess at tau < 10 microseconds

2. Binning:
   - Generate count time series at multiple bin widths:
     Delta_t in {10 ms, 50 ms, 100 ms, 500 ms, 1 s}
   - For each: compute mean rate, Fano factor, fraction of zero bins

3. Dark count characterization:
   - Compute DFA of dark-count-only recording
   - Verify alpha_dark = 0.50 +/- 0.02
```

#### Stage 2: Linear Analysis

```
For each bin width:

4. Autocorrelation function:
   - Compute C(k) for k = 1, ..., N/4
   - Test significance: |C(k)| > 1.96/sqrt(N) for 95% confidence
   - Fit decay model: exponential, power-law, or oscillatory

5. Power spectral density:
   - Welch periodogram (segment length = N/8, 50% overlap, Hann window)
   - Fit spectral exponent alpha in log-log space
   - Report frequency range of power-law scaling

6. Fano factor:
   - Compute F(T) for window sizes T from Delta_t to total duration
   - Plot F(T) vs T on log-log axes
   - Compare against Poisson expectation F(T) = 1 for all T
```

#### Stage 3: Fractal and Scaling Analysis

```
7. DFA:
   - Polynomial orders: n = 1 (DFA-1) and n = 2 (DFA-2)
   - Scale range: s_min = 16 to s_max = N/4
   - Estimate alpha from log-log regression
   - Report R^2 of the fit (quality of scaling)
   - Compare against Poisson surrogate DFA

8. MFDFA:
   - Moment orders: q in {-5, -4, ..., 0, ..., 4, 5}
   - For each q: estimate h(q)
   - Compute tau(q), singularity spectrum f(alpha_H)
   - Report: alpha_0, Delta_alpha_H, asymmetry A
   - Shuffle test: compare Delta_alpha_H against shuffled surrogates
     to distinguish true multifractality from fat-tailed distributions

9. Hurst exponent:
   - R/S analysis
   - DFA (use alpha from step 7)
   - DMA (backward moving average)
   - Report consensus H with uncertainty from method spread

10. Fractal dimension:
    - Higuchi (k_max = N/10)
    - Katz
    - Report D_H, D_K with 95% CI from bootstrap
```

#### Stage 4: Complexity and Entropy

```
11. Shannon entropy of count distribution
12. Renyi entropy spectrum: q in {0, 0.5, 1, 2, 3, 5}
13. Sample entropy: m = 2, r = 0.2*sigma
14. Distribution entropy: m = 2, B = 512 bins
15. Diffusion entropy analysis:
    - Compute S(s) for s in range
    - Fit delta
    - Apply crucial event / FBM decomposition
```

#### Stage 5: Nonlinear Dynamics

```
16. RQA:
    - Determine tau (mutual information first minimum)
    - Determine m (FNN algorithm)
    - Compute: RR, DET, LAM, TT, L, ENTR
    - Compare against shuffled surrogates

17. Delayed luminescence analysis (if DL protocol used):
    - Fit hyperbolic: I(t) = A(1 + lambda*t)^(-beta)
    - Fit stretched exponential: I(t) = A*exp(-(t/tau)^beta_KWW)
    - Fit multi-exponential (K = 1, 2, 3)
    - Model selection by BIC
```

#### Stage 6: Surrogate Testing and Significance

```
18. Generate 999 surrogates of each type:
    - Shuffled
    - Phase-randomized
    - IAAFT
    - Rate-matched Poisson

19. For each surrogate type, compute all statistics from Stages 2-5

20. Report p-values for each statistic against each null hypothesis
```

### 6.4 Recommended Software and Libraries

| Task | Python | R | MATLAB | Julia |
|------|--------|---|--------|-------|
| DFA | `nolds`, `neurokit2` | `fractal`, `nonlinearTseries` | `mfDFA` (Ihlen) | `FractalDimensions.jl` |
| MFDFA | `MFDFA` (LRydin) | `MFDFA` | `mfDFA` (Ihlen) | `MFDFA.jl` |
| Higuchi FD | `antropy`, `neurokit2` | `pracma::hurstexp` | Built-in (`wfdb`) | Custom |
| Entropy (SampEn, ApEn, DistEn) | `antropy`, `neurokit2`, `EntropyHub` | `pracma`, `TSEntropies` | `EntropyHub` | `ComplexityMeasures.jl` |
| RQA | `pyrqa` | `crqa` | CRP Toolbox (Marwan) | `RecurrenceAnalysis.jl` |
| Wavelet WTMM | `PyWavelets`, custom | `wmtsa` | MATLAB Wavelet Toolbox (`wtmm`) | `ContinuousWavelets.jl` |
| Surrogates | `nolitsa`, custom | `surrogate` | Custom | `TimeseriesSurrogates.jl` |
| Transfer entropy | `PyInform`, `IDTxl` | `RTransferEntropy` | TRENTOOL | `TransferEntropy.jl` |
| Point process | `elephant`, `spiketools` | `spatstat` | Custom | `PointProcesses.jl` |
| DEA | Custom (follow Grigolini group code) | Custom | Custom | Custom |

**Recommended primary platform**: Python with `neurokit2` + `MFDFA` + `antropy` covers most needs. For RQA, the Julia `RecurrenceAnalysis.jl` package is the most performant for large datasets.

---

## 7. Key References

### Foundational Methods

1. **Peng CK, Buldyrev SV, Havlin S, Simons M, Stanley HE, Goldberger AL.** "Mosaic organization of DNA nucleotide sequences." *Physical Review E* 49(2): 1685 (1994).
   -- *Original DFA paper. Essential reference for the algorithm and its interpretation.*

2. **Kantelhardt JW, Zschiegner SA, Koscielny-Bunde E, Havlin S, Bunde A, Stanley HE.** "Multifractal detrended fluctuation analysis of nonstationary time series." *Physica A* 316(1-4): 87--114 (2002).
   -- *MFDFA formulation. Extends DFA to arbitrary moment orders q, enabling multifractal spectrum estimation.*

3. **Higuchi T.** "Approach to an irregular time series on the basis of the fractal theory." *Physica D* 31(2): 277--283 (1988).
   -- *Higuchi fractal dimension method. Computationally efficient, works directly in time domain.*

4. **Richman JS, Moorman JR.** "Physiological time-series analysis using approximate entropy and sample entropy." *American Journal of Physiology-Heart and Circulatory Physiology* 278(6): H2039--H2049 (2000).
   -- *Sample entropy. More robust than ApEn for short, noisy biological signals.*

5. **Schreiber T, Schmitz A.** "Improved surrogate data for nonlinearity tests." *Physical Review Letters* 77(4): 635 (1996).
   -- *IAAFT surrogate method. Essential for significance testing of nonlinear structure.*

6. **Schreiber T.** "Measuring information transfer." *Physical Review Letters* 85(2): 461 (2000).
   -- *Transfer entropy. Model-free measure of directed information flow between time series.*

7. **Scafetta N, Grigolini P.** "Scaling detection in time series: Diffusion entropy analysis." *Physical Review E* 66(3): 036130 (2002).
   -- *DEA formulation. Superior to DFA for detecting anomalous diffusion from Levy processes.*

### Biophoton Time-Series Analysis

8. **Dlask M, Kukal J, Poplova M, Sovka P, Cifra M.** "Short-time fractal analysis of biological autoluminescence." *PLOS ONE* 14(7): e0214427 (2019).
   -- *Fractional Brownian bridge analysis of mung bean biophotons. First rigorous demonstration of negative memory (H < 0.5) in UPE time series, with proper surrogate controls.*

9. **Berke J, Gulyas I, Bognar Z, Berke D, Enyedi A.** "Unique algorithm for the evaluation of embryo photon emission and viability." *Scientific Reports* 14: 15066 (2024).
   -- *Entropy-weighted spectral fractal dimension (EWSFD) applied to mouse embryo UPE. Demonstrates fractal analysis can discriminate living from degenerated biological tissue.*

10. **Mahmoodi K, West BJ, Grigolini P.** "Biophotons and Emergence of Quantum Coherence -- A Diffusion Entropy Analysis." *Entropy* 23(5): 554 (2021).
    -- *DEA applied to lentil seed biophotons. Identifies transition from crucial events (quantum coherence signature) to FBM correlations during germination. Critical dark-count control.*

11. **Scholkmann F, Cifra M, Moraes TA, de Mello Gallep C.** "Using multifractal analysis of ultra-weak photon emission from germinating wheat seedlings to differentiate between two grades of intoxication with potassium dichromate." *J. Phys. Conf. Ser.* 329: 012020 (2011).
    -- *MFDFA applied to wheat UPE under toxicological stress. Multifractal width Delta_alpha is most discriminating parameter, sensitive when linear measures are not.*

12. **Benfatto M, De Paolis G, Tonello L, Grigolini P.** "Advanced Data Analysis of Spontaneous Biophoton Emission: A Multi-Method Approach." *arXiv:2511.11080* (2025).
    -- *Comprehensive benchmarked pipeline: DistEn + Renyi + DFA + MFDFA + tail statistics. Validated against Poisson, FGN, and renewal process surrogates. Reference implementation for multi-method biophoton analysis.*

13. **Belksma R.** "Temporal Variability in Ultra-weak Photon Emission." Master's thesis, Utrecht University (2024).
    -- *RQA applied to human UPE. Finds intermittent deterministic structures in palm emission. Good methodological template for nonlinear dynamics analysis of UPE.*

### Biophoton Coherence and Delayed Luminescence

14. **Popp FA, Li KH.** "Hyperbolic relaxation as a sufficient condition of a fully coherent ergodic field." *International Journal of Theoretical Physics* 32: 1573--1583 (1993).
    -- *Theoretical foundation for the hyperbolic (1/t^2) decay of delayed luminescence as a coherence signature. Derives the decay law from the properties of coherent states.*

15. **Bajpai RP.** "Quantum coherence of biophotons and living systems." *Indian Journal of Experimental Biology* 41: 514--527 (2003).
    -- *Squeezed state model of biophoton emission from Parmelia tinctorum. Influential but contentious claims about quantum state of biological light.*

16. **Cifra M, Pospisil P.** "Ultra-weak photon emission from biological samples: definition, mechanisms, properties, detection and applications." *Journal of Photochemistry and Photobiology B: Biology* 139: 2--10 (2014).
    -- *Comprehensive review including critical assessment of coherence claims. Essential reading for balanced perspective.*

### Myelin and Neural Biophotons

17. **Kumar S, Boone K, Tuszynski J, Barclay P, Simon C.** "Possible existence of optical communication channels in the brain." *Scientific Reports* 6: 36508 (2016).
    -- *Theoretical analysis of myelinated axons as optical waveguides. Calculates attenuation, dispersion, and modal properties.*

18. **Zangari A, Micheli D, Galeazzi R, Lucioli A.** "Node of Ranvier as an array of bio-nanoantennas for infrared communication in nerve tissue." *Scientific Reports* 8: 539 (2018).
    -- *Proposes nodes of Ranvier as photon sources. Provides electromagnetic modeling of photon generation at nodes.*

19. **Tang R, Dai J.** "Biophoton signal transmission and processing in the brain." *Journal of Photochemistry and Photobiology B: Biology* 139: 71--75 (2014).
    -- *Evidence for biophoton transmission through neural tissue. Discusses implications for brain information processing.*

20. **Shi L, Galvez EJ, Bhatt DK, Morgan A.** "Entangled biphoton generation in myelin sheath." *arXiv:2401.11682* (2024).
    -- *Theoretical model for entangled photon pair generation in myelin via spontaneous parametric down-conversion. Provides framework connecting quantum optics to myelin biophysics (see Track 04).*

---

## Appendix A: Quick Reference -- Relationships Between Scaling Exponents

The various scaling exponents used in time-series analysis are interrelated:

| Exponent | Symbol | Relationship |
|----------|--------|-------------|
| DFA exponent | $\alpha$ | Directly estimated from DFA |
| Hurst exponent | $H$ | $H = \alpha$ (for $0 < \alpha < 1$); $H = \alpha - 1$ (for $1 < \alpha < 2$) |
| Spectral exponent | $\beta$ | $\beta = 2\alpha - 1$ (for stationary processes) |
| Fractal dimension | $D$ | $D = 2 - H$ (for self-affine traces) |
| Autocorrelation exponent | $\gamma$ | $\gamma = 2 - 2H = 2 - \beta - 1$ (for $C(k) \sim k^{-\gamma}$) |

**Warning**: These relationships hold for monofractal, self-affine processes. For multifractal signals, each moment order $q$ has its own scaling exponent $h(q)$, and the above relationships apply only to the specific $q$ value ($q = 2$ for DFA).

## Appendix B: Minimum Data Requirements

| Method | Minimum $N$ | Recommended $N$ | Notes |
|--------|-------------|-----------------|-------|
| DFA | 256 | $> 2000$ | Need $\geq 2$ decades of scaling |
| MFDFA | 1024 | $> 4000$ | Negative $q$ moments need more data |
| Higuchi FD | 100 | $> 500$ | Robust for short series |
| Katz FD | 50 | $> 200$ | Least data-hungry |
| SampEn | 200 | $> 1000$ | Template matching needs sufficient statistics |
| DistEn | 100 | $> 500$ | More robust than SampEn for short series |
| RQA | 500 | $> 2000$ | Embedding requires adequate phase space filling |
| DEA | 1000 | $> 5000$ | Probability density estimation needs many samples |
| Transfer entropy | 5000 | $> 20000$ | Very data-hungry; consider symbolic TE for less |
| WTMM | 512 | $> 2048$ | CWT computation scales as $O(N \log N)$ |

For a photon source at 10 counts/s with 100 ms bins, $N = 2000$ corresponds to a 200-second recording. Most methods are feasible with recordings of 5--30 minutes, which is typical for biophoton experiments.
