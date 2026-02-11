"""
Demyelination scenario modeling for Track 06 integration.

Parametric study of how myelin damage degrades waveguide performance:
- Partial demyelination (increased g-ratio / thinner myelin)
- Segmental demyelination (complete loss over a segment)
- Remyelination (thinner new myelin)
- Edema (altered refractive indices)

References:
    Kumar et al. (2016), Babini et al. (2022), Zeng et al. (2022)
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (AxonGeometry, N_MYELIN, N_AXOPLASM, N_ECF)
from mode_solver import find_modes, confinement_factor
from attenuation_model import total_attenuation, propagation_distance
from arrow_model import arrow_wavelengths


def gratio_sweep(r_axon_um=0.5, g_ratios=None, wavelength_nm=500.0):
    """Sweep g-ratio to model progressive demyelination.

    As g-ratio increases (myelin thins), waveguiding degrades.

    Returns dict with arrays for each metric vs g-ratio.
    """
    if g_ratios is None:
        g_ratios = np.linspace(0.5, 0.95, 20)
    results = {
        'g_ratios': g_ratios,
        'n_modes': [],
        'max_neff': [],
        'myelin_thickness_um': [],
        'n_lamellae': [],
        'confinement_myelin': [],
        'V_number': [],
        'T_node': [],
        'alpha_total': [],
        'L_max_mm': [],
    }
    for g in g_ratios:
        axon = AxonGeometry(r_axon_um=r_axon_um, g_ratio=g)
        results['myelin_thickness_um'].append(axon.myelin_thickness_um)
        results['n_lamellae'].append(axon.n_lamellae)
        V = float(axon.v_number(wavelength_nm))
        results['V_number'].append(V)
        modes = find_modes(axon, wavelength_nm, l_max=3, n_search=300)
        results['n_modes'].append(len(modes))
        if modes:
            results['max_neff'].append(modes[0]['n_eff'])
            cf = confinement_factor(modes[0], axon)
            results['confinement_myelin'].append(cf['Gamma_myelin'])
        else:
            results['max_neff'].append(np.nan)
            results['confinement_myelin'].append(0)
        att = total_attenuation(axon, wavelength_nm)
        results['T_node'].append(float(att['T_node']))
        results['alpha_total'].append(float(att['alpha_total']))
        L = propagation_distance(axon, wavelength_nm, threshold_dB=-20)
        results['L_max_mm'].append(float(L) * 10)

    for key in results:
        if key != 'g_ratios':
            results[key] = np.array(results[key])
    return results


def segmental_demyelination(axon, gap_lengths_um=None, wavelength_nm=500.0):
    """Model complete loss of myelin over a segment.

    A demyelinated gap acts as a long 'node' causing additional scattering.
    Transmission through the gap scales approximately as exp(-alpha_gap * L_gap).

    Returns dict with gap lengths and transmission values.
    """
    if gap_lengths_um is None:
        gap_lengths_um = np.array([1, 5, 10, 20, 50, 100, 200, 500])
    # In the gap, light propagates in bare axon (n_axoplasm) surrounded by ECF
    # Loss is dominated by radiation leakage and scattering
    alpha_gap = 100.0  # cm^-1 rough estimate for bare axon (very lossy)
    gap_lengths_cm = gap_lengths_um * 1e-4
    T_gap = np.exp(-alpha_gap * gap_lengths_cm)
    # Also compute total transmission including normal internode
    att_normal = total_attenuation(axon, wavelength_nm)
    T_normal = float(att_normal['T_node'])
    T_total = T_gap * T_normal  # Gap transmission * one normal node
    return {
        'gap_lengths_um': gap_lengths_um,
        'T_gap': T_gap,
        'T_total': T_total,
        'alpha_gap_per_cm': alpha_gap,
    }


def edema_model(axon, delta_n_ecf=None, wavelength_nm=500.0):
    """Model effect of edema (increased water content in periaxonal space).

    Edema changes the effective refractive indices.

    Returns dict with delta_n values and mode metrics.
    """
    if delta_n_ecf is None:
        delta_n_ecf = np.linspace(-0.03, 0.03, 15)  # Change in n_ECF
    results = {'delta_n': delta_n_ecf, 'n_modes': [], 'max_neff': [], 'V_number': []}
    for dn in delta_n_ecf:
        n_ecf_new = N_ECF + dn
        n_axo_new = N_AXOPLASM + dn * 0.5  # Axoplasm changes less
        modes = find_modes(axon, wavelength_nm, l_max=3, n_search=300,
                          use_dispersion=False)
        results['n_modes'].append(len(modes))
        if modes:
            results['max_neff'].append(modes[0]['n_eff'])
        else:
            results['max_neff'].append(np.nan)
        V = float(axon.v_number(wavelength_nm))
        results['V_number'].append(V)
    for key in results:
        if key != 'delta_n':
            results[key] = np.array(results[key])
    return results


def save_results(results, filename):
    """Save results dict to a .npz file."""
    np.savez(filename, **{k: np.array(v) for k, v in results.items()})


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("Track 03: Demyelination Scenarios")
    print("=" * 50)

    # g-ratio sweep
    print("Running g-ratio sweep...")
    gresults = gratio_sweep(r_axon_um=0.5, wavelength_nm=500.0)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    ax = axes[0, 0]
    ax.plot(gresults['g_ratios'], gresults['n_modes'], 'bo-', ms=4)
    ax.set_xlabel('g-ratio'); ax.set_ylabel('Number of modes')
    ax.set_title('Guided Modes vs g-ratio'); ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    ax.plot(gresults['g_ratios'], gresults['V_number'], 'ro-', ms=4)
    ax.set_xlabel('g-ratio'); ax.set_ylabel('V-number')
    ax.axhline(2.405, color='gray', ls='--', alpha=0.7, label='Single-mode cutoff')
    ax.set_title('V-number vs g-ratio'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    ax = axes[0, 2]
    ax.plot(gresults['g_ratios'], gresults['confinement_myelin'], 'go-', ms=4)
    ax.set_xlabel('g-ratio'); ax.set_ylabel('Gamma_myelin')
    ax.set_title('Myelin Confinement vs g-ratio'); ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    ax.plot(gresults['g_ratios'], gresults['myelin_thickness_um'], 'ko-', ms=4)
    ax.set_xlabel('g-ratio'); ax.set_ylabel('Myelin thickness [um]')
    ax.set_title('Myelin Thickness vs g-ratio'); ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    ax.plot(gresults['g_ratios'], gresults['T_node'], 'mo-', ms=4)
    ax.set_xlabel('g-ratio'); ax.set_ylabel('T_node')
    ax.set_title('Node Transmission vs g-ratio'); ax.grid(True, alpha=0.3)

    ax = axes[1, 2]
    ax.plot(gresults['g_ratios'], gresults['L_max_mm'], 'co-', ms=4)
    ax.set_xlabel('g-ratio'); ax.set_ylabel('L_max [mm]')
    ax.set_title('Max propagation distance at -20dB'); ax.grid(True, alpha=0.3)

    plt.suptitle('Demyelination: g-ratio Sweep at 500nm', fontsize=14)
    plt.tight_layout()
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                      "demyelination_gratio_sweep.png")
    plt.savefig(fp, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp)

    # Save results
    rfp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "gratio_sweep.npz")
    save_results(gresults, rfp)
    print("Results saved to", rfp)

    # Segmental demyelination
    print("Running segmental demyelination analysis...")
    axon = AxonGeometry(r_axon_um=0.5, g_ratio=0.7)
    seg = segmental_demyelination(axon, wavelength_nm=500.0)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.semilogy(seg['gap_lengths_um'], seg['T_gap'], 'ro-', ms=5, label='Gap transmission')
    ax2.semilogy(seg['gap_lengths_um'], seg['T_total'], 'bo-', ms=5, label='Total (gap + node)')
    ax2.set_xlabel('Demyelinated gap length [um]')
    ax2.set_ylabel('Transmission')
    ax2.set_title('Segmental Demyelination: Transmission vs Gap Length')
    ax2.legend(); ax2.grid(True, alpha=0.3)
    fp2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "segmental_demyelination.png")
    plt.savefig(fp2, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp2)

    # Multi-wavelength g-ratio analysis
    print("Running multi-wavelength g-ratio analysis...")
    wavelengths_test = [400, 500, 600]
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    for wl in wavelengths_test:
        gr = gratio_sweep(r_axon_um=0.5, wavelength_nm=wl,
                         g_ratios=np.linspace(0.5, 0.9, 15))
        ax3.plot(gr['g_ratios'], gr['n_modes'], 'o-', ms=4, label=f'{wl} nm')
    ax3.set_xlabel('g-ratio')
    ax3.set_ylabel('Number of guided modes')
    ax3.set_title('Modes vs g-ratio at different wavelengths')
    ax3.legend(); ax3.grid(True, alpha=0.3)
    fp3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "gratio_multiwavelength.png")
    plt.savefig(fp3, dpi=150, bbox_inches="tight"); plt.close()
    print("Saved", fp3)

    print("Done.")
