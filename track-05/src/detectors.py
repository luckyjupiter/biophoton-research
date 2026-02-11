"""
Detector Simulators for Biophoton Research
===========================================
Realistic Monte Carlo models for PMT, SPAD, EMCCD, and SNSPD.
Usage: python src/detectors.py
"""
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from typing import Optional
from scipy.interpolate import interp1d

def _bialkali_qe(wl_nm):
    wl = np.array([200,250,300,350,400,420,450,500,550,600,650,700,800])
    qe = np.array([0.0,0.05,0.15,0.22,0.25,0.24,0.20,0.12,0.05,0.01,0.001,0.0,0.0])
    return np.clip(interp1d(wl,qe,kind="linear",bounds_error=False,fill_value=0.0)(wl_nm),0,1)

def _gaas_qe(wl_nm):
    wl = np.array([200,300,350,400,450,500,550,600,650,700,750,800])
    qe = np.array([0.0,0.10,0.30,0.40,0.38,0.35,0.25,0.12,0.03,0.005,0.0,0.0])
    return np.clip(interp1d(wl,qe,kind="linear",bounds_error=False,fill_value=0.0)(wl_nm),0,1)

def _si_spad_qe(wl_nm):
    wl = np.array([350,400,450,500,550,600,650,700,750,800,850,900,950])
    qe = np.array([0.30,0.45,0.55,0.65,0.70,0.68,0.60,0.50,0.35,0.20,0.10,0.04,0.01])
    return np.clip(interp1d(wl,qe,kind="linear",bounds_error=False,fill_value=0.0)(wl_nm),0,1)

def _biccd_qe(wl_nm):
    wl = np.array([300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000])
    qe = np.array([0.30,0.60,0.85,0.93,0.95,0.94,0.90,0.85,0.75,0.55,0.35,0.15,0.05,0.01,0.0])
    return np.clip(interp1d(wl,qe,kind="linear",bounds_error=False,fill_value=0.0)(wl_nm),0,1)

def _snspd_qe(wl_nm):
    wl = np.array([300,400,500,600,700,800,1000,1200,1400,1600,2000])
    qe = np.array([0.50,0.85,0.93,0.93,0.92,0.90,0.88,0.85,0.80,0.70,0.50])
    return np.clip(interp1d(wl,qe,kind="linear",bounds_error=False,fill_value=0.0)(wl_nm),0,1)

def _s20_qe(wl_nm):
    """S20 multialkali cathode (e.g., Sens-Tech DM0090C): 300-850nm range."""
    wl = np.array([200,300,350,400,450,500,550,600,650,700,750,800,850,900])
    qe = np.array([0.0,0.08,0.14,0.18,0.17,0.15,0.10,0.06,0.03,0.015,0.008,0.003,0.001,0.0])
    return np.clip(interp1d(wl,qe,kind="linear",bounds_error=False,fill_value=0.0)(wl_nm),0,1)

def _qcmos_qe(wl_nm):
    """Hamamatsu ORCA-Quest 2 qCMOS: QE~85% peak, extended UV in v2."""
    wl = np.array([300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000])
    qe = np.array([0.25,0.55,0.78,0.85,0.85,0.82,0.78,0.70,0.58,0.42,0.25,0.10,0.03,0.01,0.0])
    return np.clip(interp1d(wl,qe,kind="linear",bounds_error=False,fill_value=0.0)(wl_nm),0,1)

QE_CURVES = {"bialkali":_bialkali_qe,"s20":_s20_qe,"gaas":_gaas_qe,
             "si_spad":_si_spad_qe,"back_illuminated_ccd":_biccd_qe,
             "qcmos":_qcmos_qe,"snspd":_snspd_qe}

@dataclass
class DetectorParams:
    name: str = "Generic"
    qe_curve: str = "bialkali"
    qe_scalar: float = 0.20
    dark_count_rate: float = 30.0
    afterpulse_prob: float = 0.02
    afterpulse_tau: float = 50e-9
    dead_time: float = 20e-9
    timing_jitter: float = 1e-9
    collection_area: float = 5.0

# --- Detector presets updated Feb 2026 from manufacturer datasheets ---

# Hamamatsu R6095 bialkali, cooled -20C. Standard biophoton workhorse.
PMT_PARAMS = DetectorParams("PMT (Cooled Bialkali, R6095)","bialkali",0.20,30.0,0.02,50e-9,15e-9,0.5e-9,5.0)
# Hamamatsu GaAsP (H7421-40). QE ~40% at 500nm.
PMT_GAAS_PARAMS = DetectorParams("PMT (GaAsP, H7421-40)","gaas",0.40,50.0,0.03,60e-9,15e-9,0.3e-9,5.0)
# Sens-Tech DM0090C: S20 cathode, 22mm, 300-850nm. Dark ~1000 cps. Used in brain UPE.
PMT_SENSTECH_PARAMS = DetectorParams("PMT (Sens-Tech DM0090C)","s20",0.15,1000.0,0.02,50e-9,15e-9,0.5e-9,3.8)
# Excelitas SPCM-AQRH-14: PDE >70% @650nm, dark <250 cps, dead <25ns, jitter ~250ps.
SPAD_PARAMS = DetectorParams("SPAD (Excelitas SPCM-AQRH)","si_spad",0.70,100.0,0.03,40e-9,25e-9,100e-12,0.0003)
# Hamamatsu SPAD: ultra-low dark ~7 cps.
SPAD_HAMAMATSU_PARAMS = DetectorParams("SPAD (Hamamatsu)","si_spad",0.65,7.0,0.01,30e-9,40e-9,80e-12,0.0003)
# Andor iXon Ultra 897: QE>95%, dark 0.00017 e-/pix/s @-100C, CIC ~0.005.
EMCCD_PARAMS = DetectorParams("EM-CCD (Andor iXon 897)","back_illuminated_ccd",0.95,0.00017,0.0,0.0,0.0,0.033,0.07)
# Hamamatsu ORCA-Quest 2 qCMOS: read noise 0.27e-, dark 0.006 e-/pix/s.
QCMOS_PARAMS = DetectorParams("qCMOS (ORCA-Quest 2)","qcmos",0.85,0.006,0.0,0.0,0.0,0.033,0.002)
# ID Quantique ID281 Pro: SDE >95%, dark <1 cps, jitter <20ps.
SNSPD_PARAMS = DetectorParams("SNSPD (ID Quantique ID281)","snspd",0.95,1.0,0.0,0.0,30e-9,8e-12,0.0003)
# Single Quantum Eos: up to 24 channels, SDE >90%, jitter <15ps.
SNSPD_SQ_PARAMS = DetectorParams("SNSPD (Single Quantum Eos)","snspd",0.90,1.0,0.0,0.0,30e-9,6e-12,0.0003)
# Photon Spot: SDE ~95.5% @1550nm, dark 1-2 cps, jitter ~50ps.
SNSPD_PS_PARAMS = DetectorParams("SNSPD (Photon Spot)","snspd",0.93,2.0,0.0,0.0,10e-9,20e-12,0.0003)

ALL_DETECTORS = {
    "pmt_bialkali": PMT_PARAMS, "pmt_gaas": PMT_GAAS_PARAMS,
    "pmt_senstech": PMT_SENSTECH_PARAMS,
    "spad_excelitas": SPAD_PARAMS, "spad_hamamatsu": SPAD_HAMAMATSU_PARAMS,
    "emccd": EMCCD_PARAMS, "qcmos": QCMOS_PARAMS,
    "snspd_idq": SNSPD_PARAMS, "snspd_sq": SNSPD_SQ_PARAMS, "snspd_ps": SNSPD_PS_PARAMS,
}

def generate_photon_arrivals(rate, duration, rng=None):
    if rng is None: rng = np.random.default_rng()
    n = rng.poisson(rate * duration)
    if n == 0: return np.array([], dtype=np.float64)
    arr = rng.uniform(0, duration, size=n); arr.sort(); return arr

def apply_quantum_efficiency(arrivals, qe, rng=None):
    if rng is None: rng = np.random.default_rng()
    if len(arrivals) == 0: return arrivals
    return arrivals[rng.uniform(size=len(arrivals)) < qe]

def add_dark_counts(detections, dark_rate, duration, rng=None):
    if rng is None: rng = np.random.default_rng()
    n_dark = rng.poisson(dark_rate * duration)
    if n_dark == 0: return detections
    dark_times = rng.uniform(0, duration, size=n_dark)
    merged = np.concatenate([detections, dark_times]); merged.sort(); return merged

def add_afterpulses(detections, p_ap, tau_ap, duration, rng=None):
    if rng is None: rng = np.random.default_rng()
    if len(detections) == 0 or p_ap <= 0 or tau_ap <= 0: return detections
    mask = rng.uniform(size=len(detections)) < p_ap
    parents = detections[mask]
    if len(parents) == 0: return detections
    delays = rng.exponential(tau_ap, size=len(parents))
    ap_times = parents + delays; ap_times = ap_times[ap_times < duration]
    merged = np.concatenate([detections, ap_times]); merged.sort(); return merged

def apply_dead_time(detections, tau_dead):
    if len(detections) == 0 or tau_dead <= 0: return detections
    survived = [detections[0]]; last = detections[0]
    for t in detections[1:]:
        if t - last >= tau_dead: survived.append(t); last = t
    return np.array(survived, dtype=np.float64)

def apply_timing_jitter(detections, sigma_jitter, rng=None):
    if rng is None: rng = np.random.default_rng()
    if len(detections) == 0 or sigma_jitter <= 0: return detections
    jittered = detections + rng.normal(0, sigma_jitter, size=len(detections))
    jittered.sort(); return jittered

def simulate_detector(signal_rate, duration, params, rng=None):
    if rng is None: rng = np.random.default_rng()
    arrivals = generate_photon_arrivals(signal_rate, duration, rng)
    n_true = len(arrivals)
    detected = apply_quantum_efficiency(arrivals, params.qe_scalar, rng)
    n_det = len(detected)
    with_dark = add_dark_counts(detected, params.dark_count_rate, duration, rng)
    n_dark = len(with_dark) - n_det
    with_ap = add_afterpulses(with_dark, params.afterpulse_prob, params.afterpulse_tau, duration, rng)
    n_ap = len(with_ap) - len(with_dark)
    after_dead = apply_dead_time(with_ap, params.dead_time)
    n_dead_lost = len(with_ap) - len(after_dead)
    final = apply_timing_jitter(after_dead, params.timing_jitter, rng)
    return {"detections": final, "n_signal_true": n_true, "n_detected_signal": n_det,
            "n_dark": n_dark, "n_afterpulse": n_ap, "n_dead_time_lost": n_dead_lost,
            "n_total": len(final), "params": params}

@dataclass
class EMCCDParams:
    """Full EMCCD model for frame-level simulation (Andor iXon Ultra 897)."""
    name: str = "EM-CCD (Andor iXon Ultra 897)"
    qe: float = 0.95
    em_gain: float = 300.0
    excess_noise_factor_sq: float = 2.0
    read_noise_e: float = 50.0
    dark_current: float = 0.00017  # e-/pixel/s at -100C (Andor spec)
    cic_rate: float = 0.005
    n_pixels_x: int = 512
    n_pixels_y: int = 512
    pixel_size_um: float = 16.0
    frame_time: float = 1.0
    photon_counting_threshold: float = 5.0

@dataclass
class QCMOSParams:
    """Hamamatsu ORCA-Quest 2 qCMOS for photon-number-resolving imaging."""
    name: str = "qCMOS (Hamamatsu ORCA-Quest 2)"
    qe: float = 0.85
    read_noise_e: float = 0.27    # e- rms (ultra-quiet scan mode)
    dark_current: float = 0.006   # e-/pixel/s (water-cooled)
    n_pixels_x: int = 4096
    n_pixels_y: int = 2304
    pixel_size_um: float = 4.6
    frame_time: float = 1.0
    pnr_max: int = 200

def simulate_emccd_frame(signal_rate_per_pixel, params, rng=None):
    if rng is None: rng = np.random.default_rng()
    ny, nx = signal_rate_per_pixel.shape
    sig_pe = rng.poisson(params.qe * signal_rate_per_pixel * params.frame_time)
    dark_pe = rng.poisson(params.dark_current * params.frame_time, size=(ny, nx))
    cic_pe = rng.poisson(params.cic_rate, size=(ny, nx))
    total_pe = sig_pe + dark_pe + cic_pe
    output = np.zeros((ny, nx), dtype=np.float64)
    nz = total_pe > 0
    if np.any(nz): output[nz] = rng.gamma(shape=total_pe[nz], scale=params.em_gain)
    rn = rng.normal(0, params.read_noise_e, size=(ny, nx))
    analog = output + rn
    thresh = params.photon_counting_threshold * params.read_noise_e
    pc = (analog > thresh).astype(np.int32)
    return {"frame_analog": analog, "frame_photon_count": pc,
            "n_signal_photons": int(sig_pe.sum()), "n_dark_electrons": int(dark_pe.sum()),
            "n_cic": int(cic_pe.sum())}

def main():
    print("=" * 70)
    print("DETECTOR SIMULATION: Biophoton UPE Scenario")
    print("=" * 70)
    signal_rate = 50.0; duration = 3600.0
    rng = np.random.default_rng(42)
    print("Signal rate: %.1f photons/s, Duration: %.1f hr" % (signal_rate, duration/3600))
    for key, params in ALL_DETECTORS.items():
        if key in ("emccd", "qcmos"): continue
        r = simulate_detector(signal_rate, duration, params, rng)
        tr = r["n_total"] / duration; sr = r["n_detected_signal"] / duration
        print("\n--- %s ---" % params.name)
        print("  True: %d, Detected: %d (%.1f/s)" % (r["n_signal_true"], r["n_detected_signal"], sr))
        print("  Dark: %d (%.1f/s), AP: %d" % (r["n_dark"], r["n_dark"]/duration, r["n_afterpulse"]))
        print("  Dead-time lost: %d, Total: %d (%.1f/s)" % (r["n_dead_time_lost"], r["n_total"], tr))
        snr = sr / np.sqrt(tr) * np.sqrt(duration) if tr > 0 else 0
        print("  SNR (1hr): %.1f" % snr)
    print("\n--- EM-CCD Frame ---")
    emccd = EMCCDParams()
    sig_map = np.zeros((emccd.n_pixels_y, emccd.n_pixels_x))
    sig_map[240:272, 240:272] = 0.01
    r = simulate_emccd_frame(sig_map, emccd, rng)
    pc = r["frame_photon_count"]
    print("  Signal PE: %d, Dark: %d, CIC: %d" % (r["n_signal_photons"], r["n_dark_electrons"], r["n_cic"]))
    sr2 = pc[240:272, 240:272].sum()
    print("  PC hits: %d (signal region: %d, bg: %d)" % (pc.sum(), sr2, pc.sum()-sr2))

if __name__ == "__main__":
    main()
