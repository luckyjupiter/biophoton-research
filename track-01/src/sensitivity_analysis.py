"""
Sensitivity Analysis for Biophoton Photocount Statistics
========================================================

Parameter sweeps and power calculations for the central question:
At what count rates, integration times, and detector configurations can
we distinguish coherent from thermal sources at biophoton intensities?

Produces results tables and data for plotting.

Author: Track 01 -- Quantum Optics Statistician
"""

from __future__ import annotations

import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from statistical_tests import (
    power_analysis_fano,
    fano_factor_detectable,
    measured_fano_with_artifacts,
    estimate_fano_factor,
    likelihood_ratio_test,
)
from detector_model import DetectorModel, COOLED_PMT, SNSPD, ROOM_TEMP_PMT


def power_vs_count_rate(
    signal_rates: np.ndarray,
    dark_rate: float = 5.0,
    eta: float = 0.15,
    interval_duration: float = 1.0,
    n_intervals: int = 10000,
    F_true: float = 1.5,
    alpha: float = 0.05,
) -> dict:
    """Compute statistical power for detecting super-Poissonian stats
    as a function of signal count rate.

    Parameters
    ----------
    signal_rates : ndarray
        Array of signal rates (photons/s at source).
    dark_rate : float
        Dark count rate (counts/s).
    eta : float
        Detector efficiency.
    interval_duration : float
        Counting interval (s).
    n_intervals : int
        Number of intervals.
    F_true : float
        True source Fano factor.
    alpha : float
        Significance level.

    Returns
    -------
    dict with signal_rates, F_measured, delta_detectable, can_detect (bool array)
    """
    F_measured = np.zeros_like(signal_rates, dtype=float)
    delta_detectable = fano_factor_detectable(n_intervals, alpha)

    for i, r_s in enumerate(signal_rates):
        mean_signal = r_s * interval_duration
        dark_mean = dark_rate * interval_duration
        F_measured[i] = measured_fano_with_artifacts(
            F_true, mean_signal, eta, dark_mean
        )

    departure = np.abs(F_measured - 1.0)
    can_detect = departure > delta_detectable

    return {
        "signal_rates": signal_rates,
        "F_measured": F_measured,
        "delta_detectable": delta_detectable,
        "can_detect": can_detect,
        "F_true": F_true,
    }


def required_intervals_map(
    signal_rates: np.ndarray,
    dark_rates: np.ndarray,
    eta: float = 0.15,
    F_true: float = 1.5,
    alpha: float = 0.05,
    power: float = 0.80,
) -> np.ndarray:
    """Map of required counting intervals to detect F != 1.

    Parameters
    ----------
    signal_rates, dark_rates : ndarray
        1D arrays defining the parameter grid.
    eta : float
        Detector efficiency.
    F_true : float
        True Fano factor.
    alpha, power : float
        Test parameters.

    Returns
    -------
    N_required : 2D ndarray, shape (len(dark_rates), len(signal_rates))
        Required intervals. np.inf where detection is impossible.
    """
    N_required = np.full((len(dark_rates), len(signal_rates)), np.inf)

    for i, d_r in enumerate(dark_rates):
        for j, s_r in enumerate(signal_rates):
            F_m = measured_fano_with_artifacts(
                F_true, s_r, eta, d_r
            )
            delta = abs(F_m - 1.0)
            if delta > 1e-8:
                N_required[i, j] = power_analysis_fano(delta, alpha, power)

    return N_required


def multimode_thermal_distinguishability(
    mean_count: float,
    mode_numbers: np.ndarray,
    n_intervals_values: np.ndarray,
    alpha: float = 0.05,
) -> np.ndarray:
    """Can we distinguish M-mode thermal from Poisson?

    For M-mode thermal light, Q = mu/M. The minimum detectable Q
    depends on N (number of intervals).

    Parameters
    ----------
    mean_count : float
        Mean detected counts per interval.
    mode_numbers : ndarray
        Array of mode numbers M to test.
    n_intervals_values : ndarray
        Array of sample sizes to test.
    alpha : float
        Significance level.

    Returns
    -------
    detectable : 2D bool array, shape (len(mode_numbers), len(n_intervals_values))
        True where the departure Q = mu/M is detectable.
    """
    detectable = np.zeros((len(mode_numbers), len(n_intervals_values)), dtype=bool)

    for i, M in enumerate(mode_numbers):
        Q_true = mean_count / M
        F_true = 1.0 + Q_true

        for j, N in enumerate(n_intervals_values):
            delta_min = fano_factor_detectable(int(N), alpha)
            detectable[i, j] = Q_true > delta_min

    return detectable


def squeezed_detection_threshold(
    squeeze_rs: np.ndarray,
    alpha_sq: float = 10.0,
    eta: float = 0.15,
    dark_rate: float = 5.0,
    interval_duration: float = 1.0,
    alpha_test: float = 0.05,
    power: float = 0.80,
) -> dict:
    """Determine minimum measurement time to detect squeezing.

    Parameters
    ----------
    squeeze_rs : ndarray
        Array of squeeze parameters r.
    alpha_sq : float
        |alpha|^2 of coherent component.
    eta : float
        Detector efficiency.
    dark_rate : float
        Dark count rate.
    interval_duration : float
        Counting interval.
    alpha_test : float
        Significance level.
    power : float
        Desired power.

    Returns
    -------
    dict with squeeze_r, F_source, F_measured, N_required, time_hours
    """
    from photocount_distributions import squeezed_state_moments

    F_source = np.zeros_like(squeeze_rs, dtype=float)
    F_measured = np.zeros_like(squeeze_rs, dtype=float)
    N_required = np.full_like(squeeze_rs, np.inf, dtype=float)

    dark_mean = dark_rate * interval_duration

    for i, r in enumerate(squeeze_rs):
        alpha_val = np.sqrt(alpha_sq) + 0j
        moments = squeezed_state_moments(alpha_val, r, 0.0)
        F_source[i] = moments["fano_factor"]

        mean_signal = moments["mean"]
        F_measured[i] = measured_fano_with_artifacts(
            F_source[i], mean_signal, eta, dark_mean
        )

        delta = abs(F_measured[i] - 1.0)
        if delta > 1e-8 and F_measured[i] < 1.0:
            N_required[i] = power_analysis_fano(delta, alpha_test, power)

    time_hours = N_required * interval_duration / 3600.0

    return {
        "squeeze_r": squeeze_rs,
        "F_source": F_source,
        "F_measured": F_measured,
        "N_required": N_required,
        "time_hours": time_hours,
    }


def nonstationarity_false_positive_rate(
    n_intervals: int,
    mean_rate: float,
    modulation_depths: np.ndarray,
    modulation_period: float,
    interval_duration: float = 1.0,
    n_mc: int = 1000,
    alpha: float = 0.05,
    rng=None,
) -> np.ndarray:
    """False positive rate for Fano test under nonstationary Poisson process.

    A sinusoidally modulated Poisson rate produces super-Poissonian
    statistics even though each instant is Poissonian.

    Parameters
    ----------
    n_intervals : int
        Number of counting intervals per experiment.
    mean_rate : float
        Mean count rate.
    modulation_depths : ndarray
        Fractional modulation depths (0 = stationary, 1 = 100% modulation).
    modulation_period : float
        Period of rate modulation (in units of interval_duration).
    interval_duration : float
        Counting interval duration.
    n_mc : int
        Monte Carlo repetitions per modulation depth.
    alpha : float
        Significance level.
    rng : optional

    Returns
    -------
    false_positive_rate : ndarray, same shape as modulation_depths
    """
    if rng is None:
        rng = np.random.default_rng()

    fpr = np.zeros_like(modulation_depths, dtype=float)

    for k, depth in enumerate(modulation_depths):
        rejects = 0
        for _ in range(n_mc):
            # Time of each interval center
            t = np.arange(n_intervals) * interval_duration
            rates = mean_rate * (1.0 + depth * np.sin(2 * np.pi * t / modulation_period))
            rates = np.maximum(rates, 0)
            counts = rng.poisson(rates * interval_duration)

            result = estimate_fano_factor(counts)
            if result["p_value_super"] < alpha:
                rejects += 1

        fpr[k] = rejects / n_mc

    return fpr


def dark_count_masking_analysis(
    signal_rates: np.ndarray,
    dark_rates: np.ndarray,
    F_true: float,
    eta: float = 0.15,
    interval_duration: float = 1.0,
) -> np.ndarray:
    """How much do dark counts mask non-Poissonian statistics?

    Parameters
    ----------
    signal_rates, dark_rates : ndarray
        Grid axes.
    F_true : float
        True source Fano factor.
    eta : float
        Detector efficiency.
    interval_duration : float
        Counting interval.

    Returns
    -------
    F_measured : 2D ndarray, shape (len(dark_rates), len(signal_rates))
    """
    F_measured = np.zeros((len(dark_rates), len(signal_rates)))

    for i, d_r in enumerate(dark_rates):
        for j, s_r in enumerate(signal_rates):
            dark_mean = d_r * interval_duration
            mean_signal = s_r * interval_duration
            F_measured[i, j] = measured_fano_with_artifacts(
                F_true, mean_signal, eta, dark_mean
            )

    return F_measured


def run_full_sensitivity_analysis(output_dir: str) -> dict:
    """Run the complete sensitivity analysis and save results.

    Parameters
    ----------
    output_dir : str
        Directory to save results.

    Returns
    -------
    dict of all computed results.
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    print("Running sensitivity analysis...")

    # 1. Power vs count rate
    print("  [1/6] Power vs count rate...")
    signal_rates = np.logspace(0, 3, 50)  # 1 to 1000 photons/s
    pvr = power_vs_count_rate(signal_rates, dark_rate=5.0, eta=0.15,
                              n_intervals=10000, F_true=1.5)
    results["power_vs_rate"] = pvr
    np.savez(os.path.join(output_dir, "power_vs_count_rate.npz"),
             signal_rates=pvr["signal_rates"],
             F_measured=pvr["F_measured"],
             delta_detectable=pvr["delta_detectable"])

    # 2. Required intervals heatmap
    print("  [2/6] Required intervals map...")
    sr = np.logspace(0, 2.5, 30)  # 1-300 photons/s
    dr = np.array([1, 2, 5, 10, 20, 50])
    N_req = required_intervals_map(sr, dr, eta=0.15, F_true=1.5)
    results["required_intervals"] = {"signal_rates": sr, "dark_rates": dr,
                                      "N_required": N_req}
    np.savez(os.path.join(output_dir, "required_intervals.npz"),
             signal_rates=sr, dark_rates=dr, N_required=N_req)

    # 3. Multimode thermal distinguishability
    print("  [3/6] Multimode thermal distinguishability...")
    mode_nums = np.logspace(0, 15, 50)
    n_intervals_vals = np.logspace(2, 6, 40)
    detect_map = multimode_thermal_distinguishability(
        mean_count=10.0, mode_numbers=mode_nums,
        n_intervals_values=n_intervals_vals)
    results["multimode_detect"] = {
        "mode_numbers": mode_nums,
        "n_intervals": n_intervals_vals,
        "detectable": detect_map,
    }
    np.savez(os.path.join(output_dir, "multimode_distinguishability.npz"),
             mode_numbers=mode_nums, n_intervals=n_intervals_vals,
             detectable=detect_map)

    # 4. Squeezed detection threshold
    print("  [4/6] Squeezed state detection threshold...")
    rs = np.linspace(0.01, 1.5, 50)
    for detector_name, det_eta, det_dark in [
        ("cooled_pmt", 0.15, 2.0),
        ("snspd", 0.85, 0.1),
        ("room_pmt", 0.12, 20.0),
    ]:
        sq_res = squeezed_detection_threshold(
            rs, alpha_sq=10.0, eta=det_eta, dark_rate=det_dark)
        results[f"squeezed_{detector_name}"] = sq_res
        np.savez(os.path.join(output_dir, f"squeezed_threshold_{detector_name}.npz"),
                 squeeze_r=rs, F_source=sq_res["F_source"],
                 F_measured=sq_res["F_measured"],
                 N_required=sq_res["N_required"],
                 time_hours=sq_res["time_hours"])

    # 5. Nonstationarity false positives
    print("  [5/6] Nonstationarity false positives...")
    depths = np.linspace(0, 0.3, 15)
    fpr = nonstationarity_false_positive_rate(
        n_intervals=5000, mean_rate=10.0, modulation_depths=depths,
        modulation_period=100.0, n_mc=500, rng=np.random.default_rng(42))
    results["nonstationarity"] = {"depths": depths, "fpr": fpr}
    np.savez(os.path.join(output_dir, "nonstationarity_fpr.npz"),
             depths=depths, fpr=fpr)

    # 6. Dark count masking
    print("  [6/6] Dark count masking...")
    sr2 = np.logspace(0, 2, 30)
    dr2 = np.logspace(-0.3, 1.7, 30)
    # Super-Poissonian case
    F_map_super = dark_count_masking_analysis(sr2, dr2, F_true=2.0, eta=0.15)
    # Sub-Poissonian case
    F_map_sub = dark_count_masking_analysis(sr2, dr2, F_true=0.5, eta=0.15)
    results["dark_masking"] = {
        "signal_rates": sr2, "dark_rates": dr2,
        "F_map_super": F_map_super, "F_map_sub": F_map_sub,
    }
    np.savez(os.path.join(output_dir, "dark_count_masking.npz"),
             signal_rates=sr2, dark_rates=dr2,
             F_map_super=F_map_super, F_map_sub=F_map_sub)

    print("Sensitivity analysis complete.")
    return results


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "..", "results")
    results = run_full_sensitivity_analysis(output_dir)

    # Print summary
    print("\n=== Summary ===")

    pvr = results["power_vs_rate"]
    detect_idx = np.where(pvr["can_detect"])[0]
    if len(detect_idx) > 0:
        min_rate = pvr["signal_rates"][detect_idx[0]]
        print(f"\nMinimum signal rate to detect F=1.5 (N=10000, dark=5/s): "
              f"{min_rate:.1f} photons/s")
    else:
        print("\nCannot detect F=1.5 at any rate with N=10000")

    print(f"Detectable Fano departure with N=10000: "
          f"|F-1| > {pvr['delta_detectable']:.4f}")

    # Multimode boundary
    md = results["multimode_detect"]
    for j, N in enumerate(md["n_intervals"]):
        row = md["detectable"][:, j]
        if np.any(row):
            max_M = md["mode_numbers"][np.where(row)[0][-1]]
            if N > 9999 and N < 100001:
                print(f"With N={N:.0f} intervals, can distinguish M-mode "
                      f"thermal up to M={max_M:.0e} (mu=10)")

    # Squeeze detection
    for key in ["squeezed_cooled_pmt", "squeezed_snspd"]:
        sq = results[key]
        finite_mask = np.isfinite(sq["N_required"])
        if np.any(finite_mask):
            min_time = np.min(sq["time_hours"][finite_mask])
            r_at_min = sq["squeeze_r"][finite_mask][np.argmin(sq["time_hours"][finite_mask])]
            name = key.replace("squeezed_", "").upper()
            print(f"\n{name}: min detection time for squeezing = "
                  f"{min_time:.1f} hours (at r={r_at_min:.2f})")
        else:
            name = key.replace("squeezed_", "").upper()
            print(f"\n{name}: squeezing undetectable at these parameters")

    # Nonstationarity
    ns = results["nonstationarity"]
    idx_5pct = np.argmax(ns["fpr"] > 0.05) if np.any(ns["fpr"] > 0.05) else -1
    if idx_5pct >= 0:
        print(f"\nNonstationarity: {ns['depths'][idx_5pct]*100:.1f}% rate modulation "
              f"causes >5% false positive rate")
