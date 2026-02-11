"""
SNR Calculators for Biophoton Detection
========================================
Computes Signal-to-Noise Ratio, minimum detectable signals, integration
times, Poisson confidence intervals, Feldman-Cousins intervals, and
Li-Ma significance for on/off measurements.

Usage: python src/snr_calculator.py
"""
from __future__ import annotations
import numpy as np
from scipy.stats import norm, chi2, poisson
from scipy.optimize import brentq
from dataclasses import dataclass
from typing import Tuple, List


def snr_photon_counting(signal_rate, background_rate, qe, integration_time,
                        excess_noise_factor_sq=1.0):
    """SNR = eta*S*T / sqrt(F^2 * eta*S*T + B*T)."""
    S = qe * signal_rate * integration_time
    B = background_rate * integration_time
    if S + B <= 0: return 0.0
    return S / np.sqrt(excess_noise_factor_sq * S + B)


def snr_background_subtracted(signal_rate, background_rate, qe, t_on, t_off,
                               excess_noise_factor_sq=1.0):
    """SNR for on/off background-subtracted measurement."""
    S = qe * signal_rate
    B = background_rate
    num = S * t_on
    var = excess_noise_factor_sq * S * t_on + B * t_on + B * t_on**2 / t_off
    if var <= 0: return 0.0
    return num / np.sqrt(var)


def li_ma_significance(n_on, n_off, tau):
    """Li-Ma significance for on/off counting. tau = t_off/t_on."""
    if n_on + n_off == 0 or n_on == 0 or n_off == 0: return 0.0
    t1 = n_on * np.log((1 + tau) / tau * n_on / (n_on + n_off))
    t2 = n_off * np.log((1 + tau) * n_off / (n_on + n_off))
    arg = 2.0 * (t1 + t2)
    return np.sqrt(arg) if arg > 0 else 0.0


def cowan_discovery_significance(s, b):
    """Z_0 = sqrt(2*[(s+b)*ln(1+s/b) - s]). Exact for Poisson."""
    if s <= 0 or b <= 0: return 0.0
    arg = 2.0 * ((s + b) * np.log(1 + s / b) - s)
    return np.sqrt(arg) if arg > 0 else 0.0


def min_detectable_signal_gaussian(background_rate, qe, integration_time,
                                    alpha=0.05, beta=0.20):
    """Gaussian-approximation minimum detectable signal (photons/s at detector)."""
    z_a = norm.ppf(1 - alpha)
    z_b = norm.ppf(1 - beta)
    s_min = (z_a + z_b) * np.sqrt(background_rate / integration_time) + \
            z_a**2 / (2 * integration_time)
    return s_min / qe


def min_detectable_signal_poisson(background_rate, qe, integration_time,
                                   alpha=0.05, power=0.80):
    """Exact Poisson minimum detectable signal (photons/s at detector)."""
    b = background_rate * integration_time
    # Start near Gaussian approx to avoid slow iteration for large b
    n_start = max(0, int(b + norm.ppf(1 - alpha) * np.sqrt(max(b, 1)) - 1))
    n_crit = n_start
    while poisson.sf(n_crit - 1, b) > alpha:
        n_crit += 1
    def pfunc(s_total):
        return poisson.sf(n_crit - 1, s_total) - power
    try:
        s_total = brentq(pfunc, b, b + 100 * np.sqrt(max(b, 1)) + 100)
    except ValueError:
        return np.inf
    return (s_total - b) / integration_time / qe


def integration_time_for_significance(signal_rate, background_rate, qe, z_sigma=5.0):
    """T = z^2 * (eta*S + 2*B) / (eta*S)^2. Gaussian approximation."""
    s = qe * signal_rate
    if s <= 0: return np.inf
    return z_sigma**2 * (s + 2 * background_rate) / s**2


def poisson_upper_limit(n_observed, cl=0.90):
    """Garwood exact upper limit."""
    return 0.5 * chi2.ppf(cl, 2 * n_observed + 2)


def poisson_confidence_interval(n_observed, cl=0.90):
    """Exact Poisson confidence interval (Garwood 1936)."""
    alpha = 1 - cl
    lower = 0.0 if n_observed == 0 else 0.5 * chi2.ppf(alpha / 2, 2 * n_observed)
    upper = 0.5 * chi2.ppf(1 - alpha / 2, 2 * n_observed + 2)
    return (lower, upper)


def feldman_cousins_interval(n_observed, b, cl=0.90, s_max=50.0, s_step=0.1):
    """Feldman-Cousins unified confidence interval for signal s."""
    s_values = np.arange(0, s_max + s_step, s_step)
    in_interval = []
    for s in s_values:
        mu = s + b
        n_scan = int(mu + 8 * np.sqrt(max(mu, 1)) + 15)
        ns = np.arange(0, n_scan + 1)
        p_sb = poisson.pmf(ns, mu)
        s_best = np.maximum(0, ns - b)
        mu_best = s_best + b
        p_best = poisson.pmf(ns, mu_best)
        with np.errstate(divide="ignore", invalid="ignore"):
            R = np.where(p_best > 0, p_sb / p_best, 0.0)
        order = np.argsort(-R)
        cumprob = 0.0
        accepted = set()
        for idx in order:
            accepted.add(ns[idx])
            cumprob += p_sb[idx]
            if cumprob >= cl: break
        if n_observed in accepted:
            in_interval.append(s)
    if len(in_interval) == 0: return (0.0, 0.0)
    return (min(in_interval), max(in_interval))


@dataclass
class DetectorSNRConfig:
    name: str
    qe: float
    dark_rate: float
    excess_noise_sq: float = 1.0
    collection_area: float = 1.0

DETECTOR_CONFIGS = {
    "PMT (bialkali)": DetectorSNRConfig("PMT (bialkali)", 0.20, 30.0, 1.0, 5.0),
    "PMT (GaAsP)": DetectorSNRConfig("PMT (GaAsP)", 0.40, 50.0, 1.0, 5.0),
    "SPAD": DetectorSNRConfig("SPAD", 0.65, 50.0, 1.0, 0.002),
    "EMCCD (10x10 bin)": DetectorSNRConfig("EMCCD (10x10 bin)", 0.92, 0.1, 2.0, 0.002),
    "SNSPD": DetectorSNRConfig("SNSPD", 0.93, 0.1, 1.0, 0.0003),
}


def compute_snr_map(signal_rates, integration_times, config):
    """2D SNR map over signal rate and integration time."""
    snr_map = np.zeros((len(signal_rates), len(integration_times)))
    for i, sr in enumerate(signal_rates):
        for j, t in enumerate(integration_times):
            pr = sr * config.collection_area
            snr_map[i, j] = snr_photon_counting(pr, config.dark_rate, config.qe, t, config.excess_noise_sq)
    return snr_map


def compute_feasibility_table(signal_rates, detector_configs, z_target=5.0):
    """Integration times for z_target detection across detectors."""
    table = {}
    for det_name, config in detector_configs.items():
        times = []
        for sr in signal_rates:
            pr = sr * config.collection_area
            t = integration_time_for_significance(pr, config.dark_rate, config.qe, z_target)
            times.append(t)
        table[det_name] = times
    return table


def main():
    print("=" * 80)
    print("SNR ANALYSIS: Biophoton Detection Feasibility")
    print("=" * 80)

    srs = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]
    print()
    print("--- Integration Time for 5-sigma Detection ---")
    header = "%20s" % "Signal (ph/cm2/s)"
    for dn in DETECTOR_CONFIGS:
        header += "  %20s" % dn
    print(header)

    table = compute_feasibility_table(srs, DETECTOR_CONFIGS)
    for i, sr in enumerate(srs):
        row = "%20.1f" % sr
        for dn in DETECTOR_CONFIGS:
            t = table[dn][i]
            if t < 60: row += "  %17.1f s " % t
            elif t < 3600: row += "  %16.1f min" % (t/60)
            elif t < 86400: row += "  %16.1f hr " % (t/3600)
            elif t < 86400*365: row += "  %15.1f day " % (t/86400)
            else: row += "  %15.1f yr  " % (t/86400/365)
        print(row)

    print()
    print("--- Min Detectable Signal (1hr, 95%% CL, 80%% power) ---")
    print("%25s  %18s  %18s  %12s" % ("Detector", "s_min(Gauss)", "s_min(Poiss)", "ph/cm2/s"))
    for dn, cfg in DETECTOR_CONFIGS.items():
        sg = min_detectable_signal_gaussian(cfg.dark_rate, cfg.qe, 3600.0)
        sp = min_detectable_signal_poisson(cfg.dark_rate, cfg.qe, 3600.0)
        phys = sg / cfg.collection_area if cfg.collection_area > 0 else np.inf
        print("%25s  %15.4f /s   %15.4f /s   %9.3f" % (dn, sg, sp, phys))

    print()
    print("--- Poisson Confidence Intervals (90%% CL) ---")
    print("%8s  %10s  %10s  %10s" % ("n_obs", "Lower", "Upper", "Width"))
    for n in [0,1,2,3,5,10,20,50,100]:
        lo, hi = poisson_confidence_interval(n, 0.90)
        print("%8d  %10.3f  %10.3f  %10.3f" % (n, lo, hi, hi-lo))

    print()
    print("--- Feldman-Cousins Intervals (90%% CL, b=3.0) ---")
    print("%8s  %10s  %10s" % ("n_obs", "s_lower", "s_upper"))
    for n in [0,1,2,3,5,7,10,15]:
        lo, hi = feldman_cousins_interval(n, 3.0, cl=0.90, s_max=25.0, s_step=0.1)
        print("%8d  %10.2f  %10.2f" % (n, lo, hi))

    print()
    print("--- Cowan Discovery Significance ---")
    print("%8s  %8s  %8s" % ("s", "b", "Z_0"))
    for s, b in [(1,3),(2,3),(5,3),(10,3),(5,30),(10,30),(50,30)]:
        z = cowan_discovery_significance(s, b)
        print("%8.1f  %8.1f  %8.2f" % (s, b, z))


if __name__ == "__main__":
    main()
