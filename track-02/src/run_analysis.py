#!/usr/bin/env python3
"""Main analysis script for Track 02: Time-Series & Fractal Analysis.

Generates all figures and numerical results for the track.
Validates DFA/MFDFA, characterizes Hurst estimator bias,
tests surrogate methods, and runs RQA analysis.

Output:
    figures/  -- All plots saved as PNG
    results/  -- Numerical results saved as text files
"""

import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from synthetic_data import (fgn_davies_harte, fbm_from_fgn, arfima,
                            poisson_homogeneous, poisson_modulated,
                            binomial_multifractal_cascade, correlated_poisson,
                            generate_test_suite)
from dfa import dfa, mfdfa, dfa_crossover
from hurst import (hurst_rs, hurst_dfa, hurst_wavelet, hurst_periodogram,
                   hurst_dma, compare_hurst_estimators, bias_characterization)
from surrogates import (shuffled_surrogate, phase_randomized_surrogate,
                        iaaft_surrogate, surrogate_test, generate_surrogates)
from rqa import full_rqa_analysis, embed_time_series, recurrence_matrix, mutual_information

# Paths
BASE = '/home/yesh/biophoton-research/worktrees/track-02'
FIG_DIR = os.path.join(BASE, 'figures')
RES_DIR = os.path.join(BASE, 'results')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# Standard style
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'figure.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.dpi': 150,
})


def fig1_dfa_validation():
    """Figure 1: DFA validation on fGn with known Hurst exponents."""
    print("Generating Figure 1: DFA validation...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    H_values = [0.3, 0.5, 0.7, 0.9]
    colors = ['#2ca02c', '#1f77b4', '#d62728', '#ff7f0e']
    
    results_text = "DFA Validation Results\n" + "="*50 + "\n"
    results_text += f"{'H_true':>8} {'alpha_DFA':>12} {'R^2':>8} {'bias':>8}\n"
    results_text += "-"*50 + "\n"
    
    for idx, (H_true, color) in enumerate(zip(H_values, colors)):
        ax = axes[idx // 2, idx % 2]
        
        x = fgn_davies_harte(4096, H_true, seed=42 + idx)
        scales, fluct, alpha, r2 = dfa(x, order=1, n_scales=40)
        
        ax.loglog(scales, fluct, 'o', color=color, markersize=4, alpha=0.7)
        
        # Fit line
        log_s = np.log(scales)
        log_f = np.log(fluct)
        fit_coeffs = np.polyfit(log_s, log_f, 1)
        fit_line = np.exp(np.polyval(fit_coeffs, log_s))
        ax.loglog(scales, fit_line, '-', color=color, linewidth=2,
                  label=f'$\\alpha$ = {alpha:.3f}')
        
        ax.set_xlabel('Scale $s$')
        ax.set_ylabel('$F(s)$')
        ax.set_title(f'fGn, $H_{{true}}$ = {H_true}')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        results_text += f"{H_true:>8.1f} {alpha:>12.4f} {r2:>8.4f} {alpha - H_true:>+8.4f}\n"
    
    fig.suptitle('DFA Validation: fGn with Known Hurst Exponents (N=4096)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig1_dfa_validation.png'))
    plt.close()
    
    with open(os.path.join(RES_DIR, 'dfa_validation.txt'), 'w') as f:
        f.write(results_text)
    
    print(f"  Saved figure and results.")
    return results_text


def fig2_mfdfa_monofractal_vs_multifractal():
    """Figure 2: MFDFA comparison -- monofractal fGn vs multifractal cascade."""
    print("Generating Figure 2: MFDFA monofractal vs multifractal...")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    # Monofractal: fGn H=0.7
    x_mono = fgn_davies_harte(4096, 0.7, seed=42)
    result_mono = mfdfa(x_mono, order=1, n_scales=40)
    
    # Multifractal: binomial cascade
    x_multi = binomial_multifractal_cascade(12, a=0.7, seed=42)
    result_multi = mfdfa(x_multi, order=1, n_scales=40)
    
    results_text = "MFDFA Comparison Results\n" + "="*60 + "\n\n"
    
    for col, (result, label, data) in enumerate([
        (result_mono, 'fGn (H=0.7, monofractal)', x_mono),
        (result_multi, 'Binomial cascade (a=0.7, multifractal)', x_multi),
    ]):
        # Row 0: F_q(s) for different q
        ax0 = axes[0, col]
        for q_idx, q in enumerate(result['q_list']):
            if q in [-5, -2, 0, 2, 5]:
                valid = result['Fq'][q_idx, :] > 0
                if np.any(valid):
                    ax0.loglog(result['scales'][valid[:len(result['scales'])]],
                              result['Fq'][q_idx, valid],
                              'o-', markersize=3, label=f'q={q:.0f}')
        ax0.set_xlabel('Scale $s$')
        ax0.set_ylabel('$F_q(s)$')
        ax0.set_title(label)
        ax0.legend(fontsize=9)
        ax0.grid(True, alpha=0.3)
        
        # Row 1: h(q) and singularity spectrum
        ax1 = axes[1, col]
        valid_q = ~np.isnan(result['hq'])
        ax1.plot(result['q_list'][valid_q], result['hq'][valid_q], 'o-', 
                color='steelblue', linewidth=2)
        ax1.set_xlabel('Moment order $q$')
        ax1.set_ylabel('$h(q)$')
        ax1.set_title(f'$h(q)$: $\\Delta h$ = {np.ptp(result["hq"][valid_q]):.3f}')
        ax1.grid(True, alpha=0.3)
        
        results_text += f"{label}:\n"
        results_text += f"  h(q=2) = {result['hq'][7]:.4f}\n"
        results_text += f"  Delta_alpha = {result['delta_alpha']:.4f}\n"
        results_text += f"  h(q) range: [{np.min(result['hq'][valid_q]):.4f}, "
        results_text += f"{np.max(result['hq'][valid_q]):.4f}]\n\n"
    
    # Singularity spectra comparison
    ax_spec = axes[0, 2]
    valid_mono = ~np.isnan(result_mono['alpha_mf']) & ~np.isnan(result_mono['f_alpha'])
    valid_multi = ~np.isnan(result_multi['alpha_mf']) & ~np.isnan(result_multi['f_alpha'])
    
    ax_spec.plot(result_mono['alpha_mf'][valid_mono],
                result_mono['f_alpha'][valid_mono],
                'o-', color='steelblue', linewidth=2, label='fGn (mono)')
    ax_spec.plot(result_multi['alpha_mf'][valid_multi],
                result_multi['f_alpha'][valid_multi],
                's-', color='firebrick', linewidth=2, label='Cascade (multi)')
    ax_spec.set_xlabel('Singularity exponent $\\alpha$')
    ax_spec.set_ylabel('$f(\\alpha)$')
    ax_spec.set_title('Singularity Spectra Comparison')
    ax_spec.legend()
    ax_spec.grid(True, alpha=0.3)
    
    # h(q) comparison
    ax_hq = axes[1, 2]
    ax_hq.plot(result_mono['q_list'], result_mono['hq'], 'o-',
              color='steelblue', linewidth=2, label='fGn (mono)')
    ax_hq.plot(result_multi['q_list'], result_multi['hq'], 's-',
              color='firebrick', linewidth=2, label='Cascade (multi)')
    ax_hq.set_xlabel('$q$')
    ax_hq.set_ylabel('$h(q)$')
    ax_hq.set_title('Generalized Hurst Exponents')
    ax_hq.legend()
    ax_hq.grid(True, alpha=0.3)
    
    fig.suptitle('MFDFA: Monofractal vs Multifractal Signals', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig2_mfdfa_comparison.png'))
    plt.close()
    
    with open(os.path.join(RES_DIR, 'mfdfa_comparison.txt'), 'w') as f:
        f.write(results_text)
    
    print(f"  Saved figure and results.")


def fig3_hurst_bias():
    """Figure 3: Hurst estimator bias characterization at short series lengths."""
    print("Generating Figure 3: Hurst estimator bias characterization...")
    print("  (Running Monte Carlo simulations -- this may take a minute...)")
    
    # Reduced parameter set for speed
    H_values = [0.3, 0.5, 0.7, 0.9]
    N_values = [256, 512, 1024, 2048, 4096]
    n_realizations = 50  # reduced for speed; use 200+ for publication
    
    bias_results = bias_characterization(
        H_values=H_values, N_values=N_values,
        n_realizations=n_realizations, seed=42
    )
    
    methods = bias_results['methods']
    n_methods = len(methods)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Bias plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    for h_idx, H_true in enumerate(H_values):
        ax = axes[h_idx // 2, h_idx % 2]
        for m_idx, (method, color) in enumerate(zip(methods, colors)):
            bias = bias_results['bias'][m_idx, h_idx, :]
            std = bias_results['std_H'][m_idx, h_idx, :]
            ax.errorbar(N_values, bias, yerr=std, fmt='o-', color=color,
                       label=method, capsize=3, markersize=5, linewidth=1.5)
        
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        ax.set_xlabel('Series length $N$')
        ax.set_ylabel('Bias (estimated $H$ - true $H$)')
        ax.set_title(f'$H_{{true}}$ = {H_true}')
        ax.set_xscale('log', base=2)
        if h_idx == 0:
            ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, alpha=0.3)
    
    fig.suptitle(f'Hurst Estimator Bias vs. Series Length ({n_realizations} realizations per point)',
                fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig3_hurst_bias.png'))
    plt.close()
    
    # RMSE plot
    fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
    
    for h_idx, H_true in enumerate(H_values):
        ax = axes2[h_idx // 2, h_idx % 2]
        for m_idx, (method, color) in enumerate(zip(methods, colors)):
            rmse = bias_results['rmse'][m_idx, h_idx, :]
            ax.plot(N_values, rmse, 'o-', color=color,
                   label=method, markersize=5, linewidth=1.5)
        
        ax.set_xlabel('Series length $N$')
        ax.set_ylabel('RMSE')
        ax.set_title(f'$H_{{true}}$ = {H_true}')
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        if h_idx == 0:
            ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    fig2.suptitle(f'Hurst Estimator RMSE vs. Series Length', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig3b_hurst_rmse.png'))
    plt.close()
    
    # Save numerical results
    results_text = "Hurst Estimator Bias Characterization\n" + "="*70 + "\n"
    results_text += f"Monte Carlo realizations per (H, N) pair: {n_realizations}\n\n"
    
    for h_idx, H_true in enumerate(H_values):
        results_text += f"\nH_true = {H_true}\n" + "-"*70 + "\n"
        header = f"{'N':>6}"
        for method in methods:
            header += f" {method + '_bias':>12} {method + '_rmse':>12}"
        results_text += header + "\n"
        
        for n_idx, N in enumerate(N_values):
            line = f"{N:>6}"
            for m_idx in range(n_methods):
                line += f" {bias_results['bias'][m_idx, h_idx, n_idx]:>+12.4f}"
                line += f" {bias_results['rmse'][m_idx, h_idx, n_idx]:>12.4f}"
            results_text += line + "\n"
    
    with open(os.path.join(RES_DIR, 'hurst_bias_characterization.txt'), 'w') as f:
        f.write(results_text)
    
    print(f"  Saved figures and results.")


def fig4_dfa_biophoton_realistic():
    """Figure 4: DFA on realistic biophoton-like data."""
    print("Generating Figure 4: DFA on biophoton-like data...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    signals = {
        'Poisson (rate=10)': poisson_homogeneous(4096, rate=10.0, seed=42),
        'Correlated Poisson (H=0.7)': correlated_poisson(4096, H=0.7, rate=10.0, seed=42),
        'Anti-persistent Poisson (H=0.3)': correlated_poisson(4096, H=0.3, rate=10.0, seed=42),
        'Modulated Poisson (T=100)': poisson_modulated(4096, base_rate=10.0,
                                                        modulation_depth=0.5,
                                                        modulation_period=100, seed=42),
    }
    
    results_text = "DFA on Biophoton-Like Signals\n" + "="*60 + "\n\n"
    
    for idx, (name, data) in enumerate(signals.items()):
        ax = axes[idx // 2, idx % 2]
        
        scales, fluct, alpha, r2 = dfa(data, order=1, n_scales=40)
        
        # Also compute Poisson reference
        pois_ref = poisson_homogeneous(4096, rate=np.mean(data), seed=999)
        s_ref, f_ref, a_ref, _ = dfa(pois_ref, order=1, n_scales=40)
        
        ax.loglog(s_ref, f_ref, 's', color='gray', markersize=3, alpha=0.4,
                  label=f'Poisson ref ($\\alpha$={a_ref:.3f})')
        ax.loglog(scales, fluct, 'o', color='steelblue', markersize=4, alpha=0.7)
        
        log_s = np.log(scales)
        log_f = np.log(fluct)
        fit_coeffs = np.polyfit(log_s, log_f, 1)
        fit_line = np.exp(np.polyval(fit_coeffs, log_s))
        ax.loglog(scales, fit_line, '-', color='steelblue', linewidth=2,
                  label=f'$\\alpha$ = {alpha:.3f} ($R^2$={r2:.3f})')
        
        ax.set_xlabel('Scale $s$')
        ax.set_ylabel('$F(s)$')
        ax.set_title(name)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        
        results_text += f"{name}:\n"
        results_text += f"  DFA alpha = {alpha:.4f}, R^2 = {r2:.4f}\n"
        results_text += f"  Mean count = {np.mean(data):.2f}, Fano = {np.var(data)/np.mean(data):.3f}\n\n"
    
    fig.suptitle('DFA on Biophoton-Like Count Time Series (N=4096)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig4_dfa_biophoton.png'))
    plt.close()
    
    with open(os.path.join(RES_DIR, 'dfa_biophoton.txt'), 'w') as f:
        f.write(results_text)
    
    print(f"  Saved figure and results.")


def fig5_surrogate_test():
    """Figure 5: Surrogate data testing -- shuffled and IAAFT."""
    print("Generating Figure 5: Surrogate data testing...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Test 1: correlated fGn should reject shuffle null
    x_corr = fgn_davies_harte(2048, 0.7, seed=42)
    
    # Test 2: Poisson should NOT reject shuffle null
    x_pois = poisson_homogeneous(2048, rate=10.0, seed=42)
    
    def dfa_alpha(series):
        _, _, a, _ = dfa(series, min_scale=16)
        return a
    
    n_surr = 99
    
    for col, (data, label) in enumerate([
        (x_corr, 'fGn H=0.7 (correlated)'),
        (x_pois, 'Poisson (uncorrelated)'),
    ]):
        # Shuffled surrogates
        result_shuf = surrogate_test(data, dfa_alpha, n_surrogates=n_surr,
                                     method='shuffle', seed=42)
        
        ax = axes[0, col]
        ax.hist(result_shuf['statistic_surrogates'], bins=20, color='lightblue',
                edgecolor='steelblue', alpha=0.7, label='Shuffled surrogates')
        ax.axvline(result_shuf['statistic_original'], color='red', linewidth=2,
                   linestyle='--', label=f'Original ($\\alpha$={result_shuf["statistic_original"]:.3f})')
        ax.set_xlabel('DFA $\\alpha$')
        ax.set_ylabel('Count')
        ax.set_title(f'{label}\nShuffle test: p={result_shuf["p_value"]:.3f}')
        ax.legend(fontsize=9)
        
        # IAAFT surrogates
        result_iaaft = surrogate_test(data, dfa_alpha, n_surrogates=n_surr,
                                      method='iaaft', seed=42)
        
        ax2 = axes[1, col]
        ax2.hist(result_iaaft['statistic_surrogates'], bins=20, color='lightyellow',
                 edgecolor='goldenrod', alpha=0.7, label='IAAFT surrogates')
        ax2.axvline(result_iaaft['statistic_original'], color='red', linewidth=2,
                    linestyle='--', label=f'Original ($\\alpha$={result_iaaft["statistic_original"]:.3f})')
        ax2.set_xlabel('DFA $\\alpha$')
        ax2.set_ylabel('Count')
        ax2.set_title(f'{label}\nIAAFT test: p={result_iaaft["p_value"]:.3f}')
        ax2.legend(fontsize=9)
    
    fig.suptitle('Surrogate Data Testing: DFA Exponent Significance', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig5_surrogate_tests.png'))
    plt.close()
    
    print(f"  Saved figure.")


def fig6_rqa_comparison():
    """Figure 6: RQA metrics across different signal types."""
    print("Generating Figure 6: RQA comparison...")
    
    signals = {
        'White noise': fgn_davies_harte(1024, 0.5, seed=42),
        'fGn H=0.7': fgn_davies_harte(1024, 0.7, seed=42),
        'fGn H=0.3': fgn_davies_harte(1024, 0.3, seed=42),
        'Poisson (r=10)': poisson_homogeneous(1024, rate=10.0, seed=42),
        'Modulated Poisson': poisson_modulated(1024, base_rate=10.0,
                                                modulation_depth=0.8,
                                                modulation_period=50, seed=42),
        'Corr. Poisson H=0.7': correlated_poisson(1024, H=0.7, rate=10.0, seed=42),
    }
    
    # Run RQA on all
    rqa_results = {}
    for name, data in signals.items():
        result = full_rqa_analysis(data, target_rr=0.05)
        rqa_results[name] = result
    
    # Bar plot of key metrics
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    metric_names = ['RR', 'DET', 'L', 'ENTR', 'LAM', 'TT']
    metric_labels = ['Recurrence Rate', 'Determinism', 'Avg Diag Length',
                     'Entropy', 'Laminarity', 'Trapping Time']
    
    names = list(signals.keys())
    x_pos = np.arange(len(names))
    
    for idx, (metric, mlabel) in enumerate(zip(metric_names, metric_labels)):
        ax = axes[idx // 3, idx % 3]
        values = [rqa_results[n][metric] for n in names]
        bars = ax.bar(x_pos, values, color=['steelblue', '#d62728', '#2ca02c',
                                             'gray', '#ff7f0e', '#9467bd'])
        ax.set_ylabel(mlabel)
        ax.set_xticks(x_pos)
        ax.set_xticklabels([n.replace(' ', '\n') for n in names], fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
    
    fig.suptitle('RQA Metrics Across Signal Types', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig6_rqa_comparison.png'))
    plt.close()
    
    # Save results
    results_text = "RQA Comparison Results\n" + "="*80 + "\n\n"
    header = f"{'Signal':>25}"
    for m in metric_names:
        header += f" {m:>10}"
    header += f" {'tau':>5} {'m':>3} {'eps':>8}"
    results_text += header + "\n" + "-"*80 + "\n"
    
    for name in names:
        r = rqa_results[name]
        line = f"{name:>25}"
        for m in metric_names:
            line += f" {r[m]:>10.4f}"
        line += f" {r['tau']:>5} {r['m']:>3} {r['epsilon']:>8.4f}"
        results_text += line + "\n"
    
    with open(os.path.join(RES_DIR, 'rqa_comparison.txt'), 'w') as f:
        f.write(results_text)
    
    print(f"  Saved figure and results.")


def fig7_recurrence_plots():
    """Figure 7: Recurrence plots for visual comparison."""
    print("Generating Figure 7: Recurrence plots...")
    
    signals = {
        'White noise (H=0.5)': fgn_davies_harte(512, 0.5, seed=42),
        'Persistent fGn (H=0.8)': fgn_davies_harte(512, 0.8, seed=42),
        'Anti-persistent fGn (H=0.3)': fgn_davies_harte(512, 0.3, seed=42),
        'Modulated Poisson': poisson_modulated(512, base_rate=10.0,
                                                modulation_depth=0.8,
                                                modulation_period=40, seed=42),
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    
    for idx, (name, data) in enumerate(signals.items()):
        ax = axes[idx // 2, idx % 2]
        
        mi, tau = mutual_information(data, max_lag=min(30, len(data)//10))
        tau = max(tau, 1)
        m = 3
        
        embedded = embed_time_series(data, m, tau)
        
        # Choose epsilon for ~5% recurrence rate
        from scipy.spatial.distance import pdist, squareform
        n_sample = min(len(embedded), 200)
        sample_idx = np.random.choice(len(embedded), n_sample, replace=False)
        sample_dists = pdist(embedded[sample_idx], metric='chebyshev')
        epsilon = np.quantile(sample_dists, 0.05)
        epsilon = max(epsilon, 1e-10)
        
        R = recurrence_matrix(embedded, epsilon, metric='chebyshev')
        
        ax.imshow(R, cmap='binary', origin='lower', aspect='equal',
                  interpolation='none')
        ax.set_xlabel('Time index $i$')
        ax.set_ylabel('Time index $j$')
        ax.set_title(f'{name}\n(m={m}, $\\tau$={tau}, $\\varepsilon$={epsilon:.2f})')
    
    fig.suptitle('Recurrence Plots', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig7_recurrence_plots.png'))
    plt.close()
    
    print(f"  Saved figure.")


def fig8_dfa_crossover_analysis():
    """Figure 8: DFA crossover analysis for biophoton-like signals."""
    print("Generating Figure 8: DFA crossover analysis...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Signal with crossover: Poisson noise at short scales, correlations at long scales
    np.random.seed(42)
    n = 4096
    # Create a signal that has Poisson noise overlaid on a correlated modulation
    corr_rate = correlated_poisson(n, H=0.8, rate=5.0, seed=42)
    
    result = dfa_crossover(corr_rate, order=1, min_scale=10, n_scales=50)
    
    ax = axes[0]
    ax.loglog(result['scales'], result['fluct'], 'o', color='steelblue',
              markersize=4, alpha=0.7)
    
    log_s = np.log(result['scales'])
    log_f = np.log(result['fluct'])
    
    # Find crossover index
    cross_idx = np.argmin(np.abs(result['scales'] - result['crossover_scale']))
    
    # Short-scale fit
    fit_short = np.polyfit(log_s[:cross_idx], log_f[:cross_idx], 1)
    s_short = result['scales'][:cross_idx]
    ax.loglog(s_short, np.exp(np.polyval(fit_short, np.log(s_short))),
              '--', color='green', linewidth=2,
              label=f'Short scales: $\\alpha$={result["alpha_short"]:.3f}')
    
    # Long-scale fit
    fit_long = np.polyfit(log_s[cross_idx:], log_f[cross_idx:], 1)
    s_long = result['scales'][cross_idx:]
    ax.loglog(s_long, np.exp(np.polyval(fit_long, np.log(s_long))),
              '--', color='red', linewidth=2,
              label=f'Long scales: $\\alpha$={result["alpha_long"]:.3f}')
    
    ax.axvline(result['crossover_scale'], color='gray', linestyle=':', linewidth=1.5,
               label=f'Crossover at s={result["crossover_scale"]}')
    ax.set_xlabel('Scale $s$')
    ax.set_ylabel('$F(s)$')
    ax.set_title('DFA Crossover: Correlated Poisson (H=0.8, rate=5)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # Ratio of data DFA to Poisson reference
    ax2 = axes[1]
    pois_ref = poisson_homogeneous(n, rate=np.mean(corr_rate), seed=999)
    s_ref, f_ref, _, _ = dfa(pois_ref, order=1, n_scales=50)
    s_data, f_data, _, _ = dfa(corr_rate, order=1, n_scales=50)
    
    # Interpolate to common scales
    from scipy.interpolate import interp1d
    f_ref_interp = interp1d(np.log(s_ref), np.log(f_ref),
                            bounds_error=False, fill_value='extrapolate')
    common_scales = s_data
    ratio = f_data / np.exp(f_ref_interp(np.log(common_scales)))
    
    ax2.semilogx(common_scales, ratio, 'o-', color='steelblue', markersize=4)
    ax2.axhline(y=1.0, color='gray', linestyle='--', linewidth=1)
    ax2.set_xlabel('Scale $s$')
    ax2.set_ylabel('$F_{data}(s) / F_{Poisson}(s)$')
    ax2.set_title('DFA Ratio: Data vs Poisson Reference')
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle('DFA Crossover Analysis for Biophoton-Like Data', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig8_dfa_crossover.png'))
    plt.close()
    
    print(f"  Saved figure.")


def fig9_hurst_method_comparison():
    """Figure 9: Direct comparison of all Hurst methods on a single fGn realization."""
    print("Generating Figure 9: Hurst method comparison (single realization)...")
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    H_true = 0.7
    x = fgn_davies_harte(4096, H_true, seed=42)
    
    # R/S
    H_rs, ws_rs, rs_rs = hurst_rs(x)
    ax = axes[0, 0]
    ax.loglog(ws_rs, rs_rs, 'o', color='steelblue', markersize=4)
    fit = np.polyfit(np.log(ws_rs), np.log(rs_rs), 1)
    ax.loglog(ws_rs, np.exp(np.polyval(fit, np.log(ws_rs))), '-', color='red', linewidth=2)
    ax.set_xlabel('Window size')
    ax.set_ylabel('R/S')
    ax.set_title(f'R/S Analysis: H = {H_rs:.4f}')
    ax.grid(True, alpha=0.3)
    
    # DFA
    from dfa import dfa as _dfa
    s_dfa, f_dfa, alpha_dfa, r2_dfa = _dfa(x, order=1, n_scales=40)
    ax = axes[0, 1]
    ax.loglog(s_dfa, f_dfa, 'o', color='steelblue', markersize=4)
    fit = np.polyfit(np.log(s_dfa), np.log(f_dfa), 1)
    ax.loglog(s_dfa, np.exp(np.polyval(fit, np.log(s_dfa))), '-', color='red', linewidth=2)
    ax.set_xlabel('Scale $s$')
    ax.set_ylabel('$F(s)$')
    ax.set_title(f'DFA: $\\alpha$ = {alpha_dfa:.4f} ($R^2$={r2_dfa:.4f})')
    ax.grid(True, alpha=0.3)
    
    # Wavelet
    H_wav, scales_wav, var_wav = hurst_wavelet(x)
    ax = axes[0, 2]
    ax.loglog(scales_wav, var_wav, 'o', color='steelblue', markersize=6)
    fit = np.polyfit(np.log(scales_wav), np.log(var_wav), 1)
    ax.loglog(scales_wav, np.exp(np.polyval(fit, np.log(scales_wav))), '-', color='red', linewidth=2)
    ax.set_xlabel('Scale (2^j)')
    ax.set_ylabel('Wavelet variance')
    ax.set_title(f'Wavelet: H = {H_wav:.4f}')
    ax.grid(True, alpha=0.3)
    
    # Periodogram
    H_per, freqs, psd = hurst_periodogram(x)
    ax = axes[1, 0]
    ax.loglog(freqs, psd, '-', color='lightblue', linewidth=0.5)
    f_low, f_high = 4.0 / len(x), 0.4
    mask = (freqs >= f_low) & (freqs <= f_high)
    fit = np.polyfit(np.log(freqs[mask]), np.log(psd[mask]), 1)
    ax.loglog(freqs[mask], np.exp(np.polyval(fit, np.log(freqs[mask]))), '-',
              color='red', linewidth=2)
    ax.set_xlabel('Frequency')
    ax.set_ylabel('PSD')
    ax.set_title(f'Periodogram: H = {H_per:.4f}')
    ax.grid(True, alpha=0.3)
    
    # DMA
    H_dma, scales_dma, fluct_dma = hurst_dma(x)
    ax = axes[1, 1]
    ax.loglog(scales_dma, fluct_dma, 'o', color='steelblue', markersize=4)
    fit = np.polyfit(np.log(scales_dma), np.log(fluct_dma), 1)
    ax.loglog(scales_dma, np.exp(np.polyval(fit, np.log(scales_dma))), '-', color='red', linewidth=2)
    ax.set_xlabel('Scale')
    ax.set_ylabel('DMA fluctuation')
    ax.set_title(f'DMA: H = {H_dma:.4f}')
    ax.grid(True, alpha=0.3)
    
    # Summary bar chart
    ax = axes[1, 2]
    methods = ['R/S', 'DFA', 'Wavelet', 'Periodogram', 'DMA']
    estimates = [H_rs, alpha_dfa, H_wav, H_per, H_dma]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    bars = ax.bar(methods, estimates, color=colors, alpha=0.8)
    ax.axhline(y=H_true, color='black', linestyle='--', linewidth=2,
               label=f'True H = {H_true}')
    ax.set_ylabel('Estimated $H$')
    ax.set_title('Method Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1)
    
    fig.suptitle(f'Hurst Exponent Estimation Methods (fGn, H={H_true}, N=4096)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'fig9_hurst_method_comparison.png'))
    plt.close()
    
    print(f"  Saved figure.")


# ======================================================================
# MAIN EXECUTION
# ======================================================================

if __name__ == '__main__':
    print("Track 02: Time-Series & Fractal Analysis")
    print("="*50)
    print("Running full analysis pipeline...\n")
    
    fig1_dfa_validation()
    fig2_mfdfa_monofractal_vs_multifractal()
    fig3_hurst_bias()
    fig4_dfa_biophoton_realistic()
    fig5_surrogate_test()
    fig6_rqa_comparison()
    fig7_recurrence_plots()
    fig8_dfa_crossover_analysis()
    fig9_hurst_method_comparison()
    
    print("\n" + "="*50)
    print("All figures and results generated.")
    print(f"Figures in: {FIG_DIR}")
    print(f"Results in: {RES_DIR}")
