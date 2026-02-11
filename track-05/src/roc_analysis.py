"""
ROC Analysis for Biophoton Detection
Usage: python src/roc_analysis.py
"""
from __future__ import annotations
import numpy as np
from scipy.stats import poisson, norm
from dataclasses import dataclass

def compute_roc_poisson(b, s, n_points=200):
    mu0, mu1 = b, s + b
    if mu0 > 100:  # Gaussian approx for large counts
        z_vals = np.linspace(-4, 8, n_points)
        thresholds = mu0 + z_vals * np.sqrt(max(mu0, 1))
        fpr = norm.sf(z_vals)
        z1_vals = (thresholds - mu1) / np.sqrt(max(mu1, 1))
        tpr = norm.sf(z1_vals)
    else:
        n_max = int(mu1 + 10*np.sqrt(max(mu1,1)) + 20)
        thresholds = np.arange(n_max+1)
        fpr = poisson.sf(thresholds - 1, mu0)
        tpr = poisson.sf(thresholds - 1, mu1)
    return fpr, tpr, thresholds

def compute_auc_poisson(b, s):
    fpr,tpr,_ = compute_roc_poisson(b,s)
    idx = np.argsort(fpr)
    return float(np.trapezoid(tpr[idx], fpr[idx]))

def roc_operating_point(b, s, alpha=0.05):
    if b > 100:  # Gaussian approx
        z_a = norm.ppf(1 - alpha)
        n_thresh = b + z_a * np.sqrt(b)
        fpr_val = norm.sf((n_thresh - b) / np.sqrt(max(b, 1)))
        tpr_val = norm.sf((n_thresh - (s+b)) / np.sqrt(max(s+b, 1)))
        return int(n_thresh), float(fpr_val), float(tpr_val)
    n_start = max(0, int(b + norm.ppf(1-alpha)*np.sqrt(max(b,1)) - 3))
    for n_thresh in range(n_start, int(s+b+10*np.sqrt(max(s+b,1))+20)):
        fpr_val = poisson.sf(n_thresh-1, b)
        if fpr_val <= alpha:
            tpr_val = poisson.sf(n_thresh-1, s+b)
            return n_thresh, float(fpr_val), float(tpr_val)
    return 0, 0.0, 0.0

def required_counts_for_power(b_rate, s_rate, qe, alpha=0.05, power=0.80):
    s_det = qe * s_rate
    if s_det <= 0: return np.inf
    t_low, t_high = 0.1, 1e7
    for _ in range(80):
        t_mid = (t_low+t_high)/2
        b = b_rate*t_mid; s = s_det*t_mid
        _,_,tpr = roc_operating_point(b,s,alpha)
        if tpr >= power: t_high = t_mid
        else: t_low = t_mid
    return t_high

def sample_size_for_rate_difference(b_rate,r1,r2,qe,alpha=0.05,power=0.80):
    dr = qe*abs(r2-r1)
    if dr<=0: return np.inf
    z_a = norm.ppf(1-alpha); z_b = norm.ppf(power)
    var_per_t = qe*(r1+r2)+2*b_rate
    return (z_a+z_b)**2 * var_per_t / dr**2

@dataclass
class ROCScenario:
    name: str
    signal_rate: float
    background_rate: float
    qe: float
    collection_area: float
    integration_time: float

SCENARIOS = [
    ROCScenario("PMT bright 10m",100,30,0.20,5.0,600),
    ROCScenario("PMT moderate 1h",10,30,0.20,5.0,3600),
    ROCScenario("PMT faint 1h",1,30,0.20,5.0,3600),
    ROCScenario("SPAD moderate 1h",10,50,0.65,0.002,3600),
    ROCScenario("EMCCD moderate 1h",10,0.1,0.92,0.002,3600),
    ROCScenario("SNSPD faint 1h",1,0.1,0.93,0.0003,3600),
    ROCScenario("SNSPD moderate 1h",10,0.1,0.93,0.0003,3600),
]

def analyze_scenario(sc):
    s = sc.qe*sc.signal_rate*sc.collection_area*sc.integration_time
    b = sc.background_rate*sc.integration_time
    fpr,tpr,thresh = compute_roc_poisson(b,s)
    auc = compute_auc_poisson(b,s)
    _,f5,t5 = roc_operating_point(b,s,0.05)
    _,f1,t1 = roc_operating_point(b,s,0.01)
    return {"scenario":sc,"expected_signal":s,"expected_background":b,
            "auc":auc,"tpr_at_5pct_fpr":t5,"tpr_at_1pct_fpr":t1,
            "fpr":fpr,"tpr":tpr,"thresholds":thresh}

def main():
    print("=" * 80)
    print("ROC ANALYSIS: Biophoton Detection Scenarios")
    print("=" * 80)
    print()
    print("%40s  %8s  %8s  %6s  %10s  %10s" % (
        "Scenario","E[sig]","E[bkg]","AUC","TPR@5%FPR","TPR@1%FPR"))
    print("-" * 100)
    for sc in SCENARIOS:
        r = analyze_scenario(sc)
        print("%40s  %8.1f  %8.1f  %6.4f  %10.4f  %10.4f" % (
            sc.name,r["expected_signal"],r["expected_background"],
            r["auc"],r["tpr_at_5pct_fpr"],r["tpr_at_1pct_fpr"]))
    print()
    print("--- Rate Difference Detection (PMT bialkali, dark=30/s) ---")
    print("%12s  %12s  %12s  %15s" % ("R_high","R_low","Delta_R","T_needed"))
    for r2,r1 in [(50,45),(50,40),(50,30),(10,5),(10,8)]:
        t = sample_size_for_rate_difference(30.0,float(r1),float(r2),0.20)
        if t<60: ts="%.1f s"%t
        elif t<3600: ts="%.1f min"%(t/60)
        else: ts="%.1f hr"%(t/3600)
        print("%9.0f /s  %9.0f /s  %9.0f /s  %15s"%(r2,r1,r2-r1,ts))

if __name__ == "__main__":
    main()
