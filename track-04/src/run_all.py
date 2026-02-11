"""
Master simulation script for Track 04: Quantum Optics Formalism.

Generates all figures and results. Run standalone:
    python src/run_all.py

Produces:
  - figures/wigner_functions.png
  - figures/g2_correlation_curves.png
  - figures/entanglement_vs_thickness.png
  - figures/joint_spectral_intensity.png
  - figures/coherence_length_survey.png
  - figures/phi_field_properties.png
  - figures/cavity_qed_parameters.png
  - figures/demyelination_signature.png
  - results/parameter_summary.txt
  - results/observable_predictions.txt
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys
import os

# Add src directory to path
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)
base_dir = os.path.dirname(src_dir)

fig_dir = os.path.join(base_dir, "figures")
res_dir = os.path.join(base_dir, "results")
os.makedirs(fig_dir, exist_ok=True)
os.makedirs(res_dir, exist_ok=True)

from constants import *
from morse_oscillator import (
    anharmonicity_analysis, wigner_function_fock,
    wigner_function_coherent, wigner_function_squeezed,
    wigner_function_thermal, transition_dipole_harmonic,
)
from cavity_qed import (
    cavity_q_factor, purcell_factor, vacuum_rabi_coupling,
    cavity_decay_rate, mode_volume_cylindrical_shell,
    thickness_scan, cooperativity, strong_coupling_criterion,
)
from biphoton_state import (
    entanglement_vs_thickness, joint_spectral_amplitude,
    schmidt_decomposition, generate_cavity_modes,
    biphoton_density_matrix, von_neumann_entropy,
)
from coherence_propagation import (
    g1_coherence, g2_correlation, decoherence_length,
    coherence_length_survey, entanglement_decay_vs_distance,
    propagate_density_matrix, total_loss_coefficient,
)
from phi_field_quantum import (
    PhiFieldState, phi_field_vs_coherence, classify_quantum_state,
)
from observable_predictions import (
    compute_g2_predictions, spectral_correlation_map,
    bell_inequality_analysis, demyelination_signature,
    parameter_regime_summary, prediction_table,
)


def figure_wigner_functions():
    """Generate Wigner function plots for key quantum states."""
    print("  Generating Wigner functions...")
    x = np.linspace(-4, 4, 200)
    p = np.linspace(-4, 4, 200)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("Wigner Functions for Biophoton-Relevant Quantum States", fontsize=14)

    states = [
        ("Vacuum |0>", wigner_function_fock(0, x, p)),
        ("Fock |1>", wigner_function_fock(1, x, p)),
        ("Fock |2>", wigner_function_fock(2, x, p)),
        ("Coherent |alpha=1.5>", wigner_function_coherent(1.5 + 0j, x, p)),
        ("Squeezed (r=0.5)", wigner_function_squeezed(0.5, 0.0, x, p)),
        ("Thermal (n=1.0)", wigner_function_thermal(1.0, x, p)),
    ]

    for ax, (title, W) in zip(axes.flat, states):
        vmax = np.max(np.abs(W))
        im = ax.pcolormesh(x, p, W, cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                           shading="auto")
        ax.set_xlabel("x (position quadrature)")
        ax.set_ylabel("p (momentum quadrature)")
        ax.set_title(title)
        ax.set_aspect("equal")
        plt.colorbar(im, ax=ax, fraction=0.046)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "wigner_functions.png"), dpi=150, bbox_inches="tight")
    plt.close()


def figure_g2_curves():
    """Generate g^(2)(tau) curves for different source types."""
    print("  Generating g^(2) correlation curves...")
    tau = np.linspace(-5e-12, 5e-12, 500)
    kappa = 1e12

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Linear scale
    for state_type, label, color in [
        ("thermal", "Thermal", "red"),
        ("coherent", "Coherent", "blue"),
        ("fock_1", "Fock |1>", "green"),
        ("squeezed", "Squeezed", "purple"),
    ]:
        g2 = g2_correlation(tau, state_type, kappa)
        ax1.plot(tau * 1e12, g2, label=label, color=color, linewidth=2)

    ax1.axhline(y=1, color="gray", linestyle="--", alpha=0.5, label="Coherent limit")
    ax1.axhline(y=2, color="gray", linestyle=":", alpha=0.5, label="Thermal limit")
    ax1.set_xlabel("tau [ps]")
    ax1.set_ylabel("g^(2)(tau)")
    ax1.set_title("Second-Order Correlation Functions")
    ax1.legend()
    ax1.set_ylim(-0.1, 7.5)
    ax1.grid(True, alpha=0.3)

    # Biphoton (separate panel due to large scale)
    g2_bph = g2_correlation(tau, "biphoton", kappa)
    ax2.plot(tau * 1e12, g2_bph, color="darkred", linewidth=2)
    ax2.set_xlabel("tau [ps]")
    ax2.set_ylabel("g^(2)(tau)")
    ax2.set_title("Biphoton Correlation (heralded)")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "g2_correlation_curves.png"), dpi=150, bbox_inches="tight")
    plt.close()


def figure_entanglement_vs_thickness():
    """Generate entanglement entropy vs myelin thickness."""
    print("  Generating entanglement vs thickness...")
    d_array = np.linspace(0.3e-6, 2.5e-6, 80)
    ent = entanglement_vs_thickness(d_array, n_modes=25)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(ent["d"] * 1e6, ent["S"], "b-", linewidth=2)
    ax1.set_ylabel("Entanglement Entropy S [bits]")
    ax1.set_title("Biphoton Entanglement vs Myelin Thickness (Liu-Chen-Ao Model)")
    ax1.grid(True, alpha=0.3)
    ax1.axvspan(0.8, 1.1, alpha=0.15, color="green", label="Optimal range (literature)")
    ax1.legend()

    ax2.plot(ent["d"] * 1e6, ent["K"], "r-", linewidth=2)
    ax2.set_xlabel("Myelin Thickness d [um]")
    ax2.set_ylabel("Schmidt Number K")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "entanglement_vs_thickness.png"), dpi=150, bbox_inches="tight")
    plt.close()

    return ent


def figure_joint_spectral_intensity():
    """Generate joint spectral intensity map."""
    print("  Generating joint spectral intensity...")
    sc = spectral_correlation_map(n_modes=40)

    fig, ax = plt.subplots(figsize=(8, 7))

    # Convert to relative frequency (THz from line center)
    dw1 = (sc["omega1"] - OMEGA_21) / (2 * np.pi * 1e12)
    dw2 = (sc["omega2"] - OMEGA_10) / (2 * np.pi * 1e12)

    im = ax.pcolormesh(dw1, dw2, sc["jsi"].T, cmap="hot", shading="auto")
    ax.set_xlabel("delta_omega_1 / (2*pi) [THz] (from omega_21)")
    ax.set_ylabel("delta_omega_2 / (2*pi) [THz] (from omega_10)")
    ax.set_title("Joint Spectral Intensity |C(omega_1, omega_2)|^2")
    plt.colorbar(im, ax=ax, label="Normalized JSI")

    # Mark energy conservation line
    # omega_1 + omega_2 = omega_20, so delta_1 + delta_2 = 0
    ax.plot(dw1, -dw1, "w--", linewidth=1, alpha=0.7, label="Energy conservation")
    ax.legend(facecolor="gray", labelcolor="white")
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "joint_spectral_intensity.png"), dpi=150, bbox_inches="tight")
    plt.close()


def figure_coherence_length_survey():
    """Generate coherence length vs wavelength survey."""
    print("  Generating coherence length survey...")
    survey = coherence_length_survey()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.semilogy(survey["wavelength_um"], survey["alpha_abs"], "b-", label="Absorption", linewidth=2)
    ax1.semilogy(survey["wavelength_um"], survey["alpha_scat"], "g-", label="Scattering", linewidth=2)
    ax1.semilogy(survey["wavelength_um"], survey["alpha_total"], "r-", label="Total", linewidth=2)
    ax1.set_ylabel("Loss coefficient [m^-1]")
    ax1.set_title("Optical Loss in Myelin Waveguide")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Mark key wavelengths
    for lam, label in [(LAMBDA_10*1e6, "lambda_10"), (LAMBDA_21*1e6, "lambda_21")]:
        ax1.axvline(lam, color="gray", linestyle=":", alpha=0.5)
        ax1.text(lam, ax1.get_ylim()[1]*0.5, label, rotation=90, va="center", fontsize=8)

    ax2.plot(survey["wavelength_um"], survey["l_coh_um"], "k-", linewidth=2)
    ax2.set_xlabel("Wavelength [um]")
    ax2.set_ylabel("Coherence length [um]")
    ax2.set_title("Photon Coherence Length in Myelin")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 20)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "coherence_length_survey.png"), dpi=150, bbox_inches="tight")
    plt.close()


def figure_phi_field_properties():
    """Generate Phi-field quantum properties vs coherence M."""
    print("  Generating Phi-field properties...")
    M_arr = np.linspace(0, 1, 60)
    phi_props = phi_field_vs_coherence(M_arr)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Phi-Field Quantum Properties vs Neuro-Coherence M", fontsize=14)

    props = [
        ("mean_n", "<n>", "Mean Photon Number"),
        ("Q", "Mandel Q", "Mandel Q Parameter"),
        ("g2_0", "g^(2)(0)", "Second-Order Correlation"),
        ("purity", "Tr[rho^2]", "State Purity"),
        ("entropy", "S [bits]", "Von Neumann Entropy"),
    ]

    for ax, (key, ylabel, title) in zip(axes.flat, props):
        ax.plot(M_arr, phi_props[key], "b-", linewidth=2)
        ax.set_xlabel("Neuro-coherence M")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        if key == "Q":
            ax.axhline(y=0, color="red", linestyle="--", alpha=0.5, label="Q=0 (Poissonian)")
            ax.legend(fontsize=8)
        if key == "g2_0":
            ax.axhline(y=1, color="blue", linestyle="--", alpha=0.5, label="Coherent")
            ax.axhline(y=2, color="red", linestyle="--", alpha=0.5, label="Thermal")
            ax.legend(fontsize=8)

    axes[1, 2].axis("off")
    axes[1, 2].text(0.1, 0.8, "M-Phi Mapping:", fontsize=12, fontweight="bold",
                     transform=axes[1, 2].transAxes)
    axes[1, 2].text(0.1, 0.6, "M=0: thermal/vacuum (decoherent)", fontsize=10,
                     transform=axes[1, 2].transAxes)
    axes[1, 2].text(0.1, 0.45, "M=0.5: displaced squeezed thermal", fontsize=10,
                     transform=axes[1, 2].transAxes)
    axes[1, 2].text(0.1, 0.3, "M=1: displaced squeezed vacuum", fontsize=10,
                     transform=axes[1, 2].transAxes)
    axes[1, 2].text(0.1, 0.1, "Squeezing + displacement increase\nwith coherence function M", fontsize=9,
                     transform=axes[1, 2].transAxes)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "phi_field_properties.png"), dpi=150, bbox_inches="tight")
    plt.close()


def figure_cavity_qed_parameters():
    """Generate cavity QED parameter scan."""
    print("  Generating cavity QED parameters...")
    scan = thickness_scan()

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Cavity QED Parameters vs Myelin Thickness", fontsize=14)

    plots = [
        (scan["Q_10"], "Q factor (|1>->|0>)"),
        (scan["F_P_10"], "Purcell factor F_P"),
        (scan["g_10"], "Rabi coupling g [rad/s]"),
        (scan["kappa_10"], "Cavity decay kappa [rad/s]"),
        (scan["C_10"], "Cooperativity C"),
        (scan["V_mode"], "Mode volume [m^3]"),
    ]

    for ax, (data, title) in zip(axes.flat, plots):
        ax.plot(scan["d"] * 1e6, data, "b-", linewidth=2)
        ax.set_xlabel("Myelin thickness [um]")
        ax.set_ylabel(title)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        if np.max(data) / max(np.min(data[data > 0]), 1e-30) > 100:
            ax.set_yscale("log")

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "cavity_qed_parameters.png"), dpi=150, bbox_inches="tight")
    plt.close()


def figure_demyelination():
    """Generate demyelination signature plot."""
    print("  Generating demyelination signature...")
    demyel = demyelination_signature()

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    fig.suptitle("Observable Signatures of Progressive Demyelination", fontsize=14)

    ax1.plot(demyel["d"] * 1e6, demyel["S"], "b-", linewidth=2)
    ax1.set_ylabel("Entanglement Entropy S [bits]")
    ax1.set_title("Biphoton Entanglement")
    ax1.grid(True, alpha=0.3)
    ax1.axvline(0.45, color="red", linestyle="--", alpha=0.5, label="d=0.45 um threshold")
    ax1.legend()

    ax2.plot(demyel["d"] * 1e6, demyel["Fp"], "r-", linewidth=2)
    ax2.set_ylabel("Purcell Factor F_P")
    ax2.set_title("Cavity Enhancement")
    ax2.grid(True, alpha=0.3)

    ax3.plot(demyel["d"] * 1e6, demyel["g2_0"], "g-", linewidth=2)
    ax3.set_xlabel("Myelin Thickness [um]")
    ax3.set_ylabel("g^(2)(0)")
    ax3.set_title("Photon Bunching")
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "demyelination_signature.png"), dpi=150, bbox_inches="tight")
    plt.close()


def write_results():
    """Write numerical results to text files."""
    print("  Writing results...")

    # Parameter summary
    with open(os.path.join(res_dir, "parameter_summary.txt"), "w") as f:
        f.write("Track 04: Quantum Optics Parameter Summary\n")
        f.write("=" * 60 + "\n\n")

        f.write("--- Morse Oscillator (C-H bond) ---\n")
        info = anharmonicity_analysis()
        for v, e in zip(info["v"], info["E_eV"]):
            f.write(f"  E_{v} = {e:.4f} eV\n")
        f.write(f"  omega_10 = {OMEGA_10:.3e} rad/s (lambda = {LAMBDA_10*1e6:.3f} um)\n")
        f.write(f"  omega_21 = {OMEGA_21:.3e} rad/s (lambda = {LAMBDA_21*1e6:.3f} um)\n")
        f.write(f"  omega_20 = {OMEGA_20:.3e} rad/s (lambda = {LAMBDA_20*1e6:.3f} um)\n")
        f.write(f"  Morse parameter s = {info['s']:.2f}\n")
        f.write(f"  Max bound state v_max = {info['v_max']}\n\n")

        f.write("--- Thermal Photon Numbers (T = 310 K) ---\n")
        f.write(f"  n_th(omega_10) = {N_TH_10:.2e}\n")
        f.write(f"  n_th(omega_21) = {N_TH_21:.2e}\n\n")

        f.write("--- Cavity QED (d = 1.0 um, a = 1.0 um, L = 500 um) ---\n")
        d = MYELIN_THICKNESS_TYPICAL
        a = AXON_RADIUS_TYPICAL
        L = INTERNODE_LENGTH_TYPICAL
        V = mode_volume_cylindrical_shell(a, d, L)
        for label, omega, lam, dipole, gamma in [
            ("|1>->|0>", OMEGA_10, LAMBDA_10, DIPOLE_10, GAMMA_10_FREE),
            ("|2>->|1>", OMEGA_21, LAMBDA_21, DIPOLE_21, GAMMA_21_FREE),
        ]:
            Q = cavity_q_factor(d, omega, 300.0)
            Fp = purcell_factor(Q, V, lam)
            g = vacuum_rabi_coupling(dipole, omega, V)
            kappa = cavity_decay_rate(Q, omega)
            C = cooperativity(g, kappa, gamma)
            sc = strong_coupling_criterion(g, kappa, gamma)
            f.write(f"  Transition {label}:\n")
            f.write(f"    Q = {Q:.1f}\n")
            f.write(f"    F_P = {Fp:.2e}\n")
            f.write(f"    g = {g:.2e} rad/s\n")
            f.write(f"    kappa = {kappa:.2e} rad/s\n")
            f.write(f"    C = {C:.2e}\n")
            f.write(f"    Strong coupling: {'YES' if sc else 'NO'}\n")

        f.write(f"\n--- Decoherence ---\n")
        f.write(f"  T2* = {T2_STAR*1e12:.1f} ps\n")
        f.write(f"  Dephasing rate = {GAMMA_DEPH:.2e} rad/s\n")
        f.write(f"  Coherence length (3.54 um): {decoherence_length(LAMBDA_10)*1e6:.2f} um\n")
        f.write(f"  Coherence length (3.70 um): {decoherence_length(LAMBDA_21)*1e6:.2f} um\n")

    # Observable predictions
    with open(os.path.join(res_dir, "observable_predictions.txt"), "w") as f:
        f.write("Track 04: Observable Predictions\n")
        f.write("=" * 60 + "\n\n")

        f.write("--- g^(2)(0) Predictions ---\n")
        g2_preds = compute_g2_predictions()
        for state, val in g2_preds.items():
            f.write(f"  {state:12s}: g^(2)(0) = {val:.2f}\n")

        f.write(f"\n--- Bell Inequality ---\n")
        for eta in [0.3, 0.5, 0.7, 0.9, 0.95]:
            bell = bell_inequality_analysis(eta)
            f.write(f"  eta={eta:.2f}: S = {bell['S_measured']:.3f} "
                    f"({'VIOLATION' if bell['violation'] else 'no violation'})\n")

        f.write(f"\n--- Entanglement vs Thickness ---\n")
        d_arr = np.linspace(0.3e-6, 2.5e-6, 50)
        ent = entanglement_vs_thickness(d_arr, n_modes=20)
        i_max = np.argmax(ent["S"])
        f.write(f"  Peak S = {ent['S'][i_max]:.4f} bits at d = {ent['d'][i_max]*1e6:.2f} um\n")
        f.write(f"  Peak K = {ent['K'][i_max]:.2f}\n")

        f.write(f"\n--- Quantum vs Classical Discrimination ---\n")
        table = prediction_table()
        for obs, vals in table.items():
            f.write(f"  {obs}:\n")
            f.write(f"    Quantum:   {vals['quantum']}\n")
            f.write(f"    Classical: {vals['classical']}\n")

        f.write(f"\n--- Parameter Regime ---\n")
        regime = parameter_regime_summary()
        for key, val in regime.items():
            f.write(f"  {key}: {val}\n")


def main():
    """Run all simulations and generate outputs."""
    print("=== Track 04: Quantum Optics Formalism ===")
    print("Running all simulations...\n")

    figure_wigner_functions()
    figure_g2_curves()
    ent_data = figure_entanglement_vs_thickness()
    figure_joint_spectral_intensity()
    figure_coherence_length_survey()
    figure_phi_field_properties()
    figure_cavity_qed_parameters()
    figure_demyelination()
    write_results()

    print("\nAll outputs generated:")
    for d in [fig_dir, res_dir]:
        for fn in sorted(os.listdir(d)):
            fpath = os.path.join(d, fn)
            size = os.path.getsize(fpath)
            print(f"  {os.path.relpath(fpath, base_dir):45s} ({size:>8,d} bytes)")

    print("\nDone.")


if __name__ == "__main__":
    main()
