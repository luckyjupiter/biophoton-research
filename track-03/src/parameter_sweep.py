"""
Comprehensive parameter sweep for myelinated axon waveguide.

Sweeps across axon diameters, g-ratios, and wavelengths to map the full
parameter space of biophoton waveguiding performance.

Generates results for Track 03 and feeds into Track 06 (pathology).
"""

import numpy as np
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import AxonGeometry, N_MYELIN, N_AXOPLASM, N_ECF
from mode_solver import find_modes, confinement_factor
from attenuation_model import total_attenuation, propagation_distance
from arrow_model import arrow_wavelengths


def parameter_sweep():
    """Run full parameter sweep."""
    # Parameter ranges
    axon_radii = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]  # um
    g_ratios = [0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
    wavelengths = [400, 450, 500, 550, 600, 650, 700]  # nm

    results = []
    total = len(axon_radii) * len(g_ratios) * len(wavelengths)
    count = 0
    for r_ax in axon_radii:
        for g in g_ratios:
            axon = AxonGeometry(r_axon_um=r_ax, g_ratio=g)
            for wl in wavelengths:
                count += 1
                if count % 20 == 0:
                    print(f"  Progress: {count}/{total}")
                modes = find_modes(axon, wl, l_max=3, n_search=300)
                n_modes = len(modes)
                if modes:
                    max_neff = modes[0]['n_eff']
                    cf = confinement_factor(modes[0], axon)
                    gamma_myelin = cf['Gamma_myelin']
                else:
                    max_neff = 0
                    gamma_myelin = 0
                att = total_attenuation(axon, wl)
                V = float(axon.v_number(wl))
                aw = arrow_wavelengths(axon.myelin_thickness_um)
                # Find nearest AR wavelength
                ar_wls = aw['anti_resonant']
                if len(ar_wls) > 0:
                    nearest_ar = ar_wls[np.argmin(np.abs(ar_wls - wl))]
                else:
                    nearest_ar = 0
                results.append({
                    'r_axon_um': r_ax,
                    'g_ratio': g,
                    'wavelength_nm': wl,
                    'r_outer_um': axon.r_outer_um,
                    'myelin_thickness_um': axon.myelin_thickness_um,
                    'n_lamellae': axon.n_lamellae,
                    'V_number': V,
                    'n_modes': n_modes,
                    'max_neff': max_neff,
                    'Gamma_myelin': gamma_myelin,
                    'alpha_total_per_cm': float(att['alpha_total']),
                    'loss_dB_per_cm': float(att['loss_dB_per_cm']),
                    'T_node': float(att['T_node']),
                    'nearest_AR_nm': float(nearest_ar),
                })
    return results


def find_optimal_configurations(results, min_modes=1, max_loss_dB=30):
    """Find parameter configurations that support waveguiding."""
    guided = [r for r in results if r['n_modes'] >= min_modes and r['loss_dB_per_cm'] <= max_loss_dB]
    guided.sort(key=lambda x: x['loss_dB_per_cm'])
    return guided


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("Track 03: Parameter Sweep")
    print("=" * 50)

    print("Running parameter sweep...")
    results = parameter_sweep()

    # Save raw results
    rfp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "parameter_sweep.json")
    with open(rfp, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} data points to {rfp}")

    # Find optimal configs
    optimal = find_optimal_configurations(results)
    print(f"Found {len(optimal)} guided configurations (out of {len(results)})")
    if optimal:
        print("Top 5 lowest-loss configurations:")
        for r in optimal[:5]:
            print(f"  r={r['r_axon_um']}um g={r['g_ratio']} wl={r['wavelength_nm']}nm "
                  f"modes={r['n_modes']} loss={r['loss_dB_per_cm']:.1f}dB/cm")

    # Create summary plots
    # 1. Mode count heatmap (g-ratio vs wavelength) for r=0.5um
    r_target = 0.5
    g_vals = sorted(set(r['g_ratio'] for r in results))
    wl_vals = sorted(set(r['wavelength_nm'] for r in results))
    mode_map = np.zeros((len(g_vals), len(wl_vals)))
    for r in results:
        if r['r_axon_um'] == r_target:
            gi = g_vals.index(r['g_ratio'])
            wi = wl_vals.index(r['wavelength_nm'])
            mode_map[gi, wi] = r['n_modes']

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mode_map, aspect='auto', origin='lower',
                   extent=[wl_vals[0], wl_vals[-1], g_vals[0], g_vals[-1]],
                   cmap='YlOrRd')
    ax.set_xlabel('Wavelength [nm]')
    ax.set_ylabel('g-ratio')
    ax.set_title(f'Number of Guided Modes (r_axon={r_target} um)')
    plt.colorbar(im, ax=ax, label='N modes')
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                      "parameter_sweep_modes.png")
    plt.savefig(fp, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp)

    # 2. Loss heatmap
    loss_map = np.zeros((len(g_vals), len(wl_vals)))
    for r in results:
        if r['r_axon_um'] == r_target:
            gi = g_vals.index(r['g_ratio'])
            wi = wl_vals.index(r['wavelength_nm'])
            loss_map[gi, wi] = r['loss_dB_per_cm']

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    im2 = ax2.imshow(loss_map, aspect='auto', origin='lower',
                    extent=[wl_vals[0], wl_vals[-1], g_vals[0], g_vals[-1]],
                    cmap='RdYlGn_r', vmin=0, vmax=80)
    ax2.set_xlabel('Wavelength [nm]')
    ax2.set_ylabel('g-ratio')
    ax2.set_title(f'Total Loss [dB/cm] (r_axon={r_target} um)')
    plt.colorbar(im2, ax=ax2, label='dB/cm')
    fp2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "parameter_sweep_loss.png")
    plt.savefig(fp2, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp2)

    # 3. Modes vs axon radius
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    for wl in [400, 500, 600]:
        radii = sorted(set(r['r_axon_um'] for r in results))
        modes_vs_r = []
        for rad in radii:
            matching = [r for r in results if r['r_axon_um'] == rad
                       and r['wavelength_nm'] == wl and r['g_ratio'] == 0.7]
            if matching:
                modes_vs_r.append(matching[0]['n_modes'])
            else:
                modes_vs_r.append(0)
        ax3.plot(radii, modes_vs_r, 'o-', ms=5, label=f'{wl} nm')
    ax3.set_xlabel('Axon radius [um]')
    ax3.set_ylabel('Number of guided modes')
    ax3.set_title('Guided Modes vs Axon Size (g=0.7)')
    ax3.legend(); ax3.grid(True, alpha=0.3)
    fp3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "modes_vs_radius.png")
    plt.savefig(fp3, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp3)

    print("Parameter sweep complete.")
