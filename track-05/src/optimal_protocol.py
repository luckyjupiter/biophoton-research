"""
Optimal Protocol Design for Biophoton Measurements
===================================================
Given realistic detector parameters, designs measurement protocols that
maximize information about quantum coherence. Includes time-gating,
coincidence detection, and adaptive measurement strategies.

Usage: python src/optimal_protocol.py
"""
from __future__ import annotations
import numpy as np
from scipy.stats import norm, poisson
from scipy.optimize import minimize_scalar


def optimal_on_off_ratio(signal_rate, background_rate, qe, total_time):
    """Optimal ratio of on-source to off-source time."""
    s = qe * signal_rate
    b = background_rate
    # Optimal tau = t_off/t_on = sqrt(b/(s+b))
    tau_opt = np.sqrt(b / max(s + b, 1e-20))
    t_on = total_time / (1 + tau_opt)
    t_off = total_time - t_on
    return {"tau_opt": tau_opt, "t_on": t_on, "t_off": t_off}


def time_gating_improvement(signal_rate, background_rate, gate_width, duty_cycle):
    """SNR improvement from time-gating if signal is pulsed."""
    # Gating reduces background by duty_cycle factor
    # Signal is preserved if gate is synchronized
    b_gated = background_rate * duty_cycle
    snr_ungated = signal_rate / np.sqrt(signal_rate + background_rate)
    snr_gated = signal_rate / np.sqrt(signal_rate + b_gated)
    return {"snr_improvement": snr_gated / max(snr_ungated, 1e-20),
            "bg_reduction": duty_cycle,
            "b_gated": b_gated}


def coincidence_window_optimization(rate1, rate2, pair_rate, dark1, dark2):
    """Optimize coincidence window for pair detection."""
    windows = np.logspace(-10, -5, 100)  # 0.1 ns to 10 us
    results = []
    for tau in windows:
        accidental = 2 * tau * (rate1 + dark1) * (rate2 + dark2)
        true_coin = pair_rate * min(1.0, tau / 1e-9)  # capture efficiency
        snr = true_coin / np.sqrt(max(true_coin + accidental, 1e-20))
        results.append({"tau": tau, "accidental": accidental,
                        "true": true_coin, "snr": snr})
    best = max(results, key=lambda r: r["snr"])
    return best, results


def spectral_binning_optimization(total_rate, background_rate, qe, n_bins_range,
                                   integration_time, target_sigma=5.0):
    """Find optimal spectral binning for UPE spectrum acquisition."""
    results = []
    for n_bins in n_bins_range:
        rate_per_bin = total_rate / n_bins
        s_per_bin = qe * rate_per_bin * integration_time
        b_per_bin = background_rate * integration_time
        snr = s_per_bin / np.sqrt(s_per_bin + b_per_bin) if s_per_bin + b_per_bin > 0 else 0
        spectral_info = n_bins * max(0, snr - target_sigma)  # excess info above threshold
        results.append({"n_bins": n_bins, "rate_per_bin": rate_per_bin,
                        "snr_per_bin": snr, "spectral_info": spectral_info})
    return results


def adaptive_integration_strategy(signal_rate_estimate, background_rate, qe,
                                   check_interval=60, max_time=86400,
                                   target_sigma=5.0):
    """Simulate adaptive integration: stop early if significance reached."""
    rng = np.random.default_rng(42)
    s = qe * signal_rate_estimate
    b = background_rate
    n_checks = int(max_time / check_interval)
    results = []
    for trial in range(100):
        cumulative = 0
        bg_estimate = 0
        stopped = False
        for i in range(1, n_checks + 1):
            t = i * check_interval
            n_on = rng.poisson((s + b) * check_interval)
            n_off = rng.poisson(b * check_interval)
            cumulative += n_on
            bg_estimate += n_off
            sig_hat = cumulative / t - bg_estimate / t
            if t * b > 10:  # enough for Gaussian
                z = sig_hat * t / np.sqrt(cumulative + bg_estimate) if cumulative + bg_estimate > 0 else 0
                if z >= target_sigma:
                    results.append({"trial": trial, "stopped_at": t, "detected": True})
                    stopped = True
                    break
        if not stopped:
            results.append({"trial": trial, "stopped_at": max_time, "detected": False})
    n_detected = sum(1 for r in results if r["detected"])
    stop_times = [r["stopped_at"] for r in results if r["detected"]]
    return {"power": n_detected / len(results),
            "median_stop_time": np.median(stop_times) if stop_times else max_time,
            "mean_stop_time": np.mean(stop_times) if stop_times else max_time}


def coherence_time_estimation_requirements(count_rate, target_precision=0.01):
    """Integration time needed to measure g(2)(tau) to given precision."""
    # sigma[g2] ~ 1/sqrt(R^2 * delta_tau * T)
    # For delta_tau = 1 ns (typical HBT bin):
    delta_tau = 1e-9
    T_needed = 1.0 / (target_precision**2 * count_rate**2 * delta_tau)
    return {"integration_time_s": T_needed,
            "integration_time_hr": T_needed / 3600,
            "count_rate": count_rate,
            "target_precision": target_precision,
            "bin_width_ns": delta_tau * 1e9}


def main():
    print("=" * 80)
    print("OPTIMAL PROTOCOL DESIGN")
    print("=" * 80)
    print()
    # On/off optimization
    print("--- Optimal On/Off Time Ratio ---")
    for sr in [1, 5, 10, 50, 100]:
        r = optimal_on_off_ratio(sr, 30.0, 0.20, 3600)
        print("  Signal %4d ph/s: tau_opt=%.3f, t_on=%.0fs, t_off=%.0fs" % (
            sr, r["tau_opt"], r["t_on"], r["t_off"]))
    print()
    # Time gating
    print("--- Time-Gating Improvement (if signal is pulsed) ---")
    for dc in [1.0, 0.5, 0.1, 0.01, 0.001]:
        r = time_gating_improvement(10, 30, 1e-3, dc)
        print("  Duty cycle %.3f: SNR improvement = %.2fx, bg -> %.3f/s" % (
            dc, r["snr_improvement"], r["b_gated"]))
    print()
    # Coincidence optimization
    print("--- Coincidence Window Optimization ---")
    best, _ = coincidence_window_optimization(50, 50, 0.01, 30, 30)
    print("  Best window: %.1f ns" % (best["tau"] * 1e9))
    print("  Accidental rate: %.2e /s" % best["accidental"])
    print("  True coincidence rate: %.2e /s" % best["true"])
    print()
    # Spectral binning
    print("--- Spectral Binning Optimization (50 ph/s total, PMT, 1hr) ---")
    results = spectral_binning_optimization(50, 30, 0.20, [1,2,5,10,20,50,100,500], 3600)
    print("%8s  %12s  %8s  %12s" % ("N_bins", "Rate/bin", "SNR/bin", "Info_score"))
    for r in results:
        print("%8d  %9.2f /s  %8.1f  %12.1f" % (
            r["n_bins"], r["rate_per_bin"], r["snr_per_bin"], r["spectral_info"]))
    print()
    # g(2) measurement requirements
    print("--- g(2)(tau) Measurement Requirements ---")
    print("%12s  %12s  %12s" % ("Count rate", "Precision", "T_needed"))
    for rate in [10, 50, 100, 500]:
        for prec in [0.1, 0.01, 0.001]:
            r = coherence_time_estimation_requirements(rate, prec)
            t = r["integration_time_s"]
            if t < 3600: ts = "%.1f s" % t
            elif t < 86400: ts = "%.1f hr" % (t/3600)
            elif t < 86400*365: ts = "%.1f day" % (t/86400)
            else: ts = "%.1f yr" % (t/86400/365)
            print("%9d /s  %12.3f  %12s" % (rate, prec, ts))


if __name__ == "__main__":
    main()
