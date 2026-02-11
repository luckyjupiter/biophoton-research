"""
Observable predictions for distinguishing quantum vs classical biophoton models.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    HBAR, C_LIGHT, K_B, EV_TO_J,
    N_MYELIN, T_PHYSIOL,
    OMEGA_10, OMEGA_21, OMEGA_20,
    LAMBDA_10, LAMBDA_21,
    GAMMA_DEPH, DIPOLE_10, DIPOLE_21,
    GAMMA_10_FREE, GAMMA_21_FREE,
    AXON_RADIUS_TYPICAL, MYELIN_THICKNESS_TYPICAL, INTERNODE_LENGTH_TYPICAL,
)
from biphoton_state import (
    entanglement_vs_thickness, generate_cavity_modes,
    joint_spectral_amplitude, schmidt_decomposition,
)
from cavity_qed import (
    cavity_q_factor, mode_volume_cylindrical_shell,
    vacuum_rabi_coupling, cavity_decay_rate, purcell_factor,
)
from coherence_propagation import (
    decoherence_length, total_loss_coefficient,
    g2_correlation, entanglement_decay_vs_distance,
    coherence_length_survey,
)


def prediction_table():
    return {
        "g2_zero": {"quantum": ">2 (biphoton)", "classical": "<=2 (thermal)"},
        "spectral_correlation": {"quantum": "anti-correlated", "classical": "none"},
        "bell_inequality": {"quantum": "S>2", "classical": "S<=2"},
        "mandel_Q": {"quantum": "Q<0 possible", "classical": "Q>=0"},
    }


def compute_g2_predictions():
    tau_0 = np.array([0.0])
    kappa = 1e12
    results = {}
    for st in ["thermal", "coherent", "fock_1", "squeezed", "biphoton"]:
        g2 = g2_correlation(tau_0, st, kappa)
        results[st] = float(g2[0])
    return results


def spectral_correlation_map(a=AXON_RADIUS_TYPICAL, d=MYELIN_THICKNESS_TYPICAL,
                              L=INTERNODE_LENGTH_TYPICAL, n_modes=25):
    V = mode_volume_cylindrical_shell(a, d, L)
    g1 = vacuum_rabi_coupling(DIPOLE_21, OMEGA_21, V)
    g2 = vacuum_rabi_coupling(DIPOLE_10, OMEGA_10, V)
    Q10 = cavity_q_factor(d, OMEGA_10, 300.0)
    Q21 = cavity_q_factor(d, OMEGA_21, 300.0)
    kappa10 = cavity_decay_rate(Q10, OMEGA_10)
    kappa21 = cavity_decay_rate(Q21, OMEGA_21)
    Gamma_2 = GAMMA_21_FREE + kappa21 + GAMMA_DEPH
    Gamma_1 = GAMMA_10_FREE + kappa10 + GAMMA_DEPH
    delta = max(Gamma_1, Gamma_2) * 3
    omega1 = np.linspace(OMEGA_21 - delta, OMEGA_21 + delta, 100)
    omega2 = np.linspace(OMEGA_10 - delta, OMEGA_10 + delta, 100)
    C = joint_spectral_amplitude(omega1, omega2, g1, g2, Gamma_2, Gamma_1)
    jsi = np.abs(C)**2
    jsi_max = np.max(jsi)
    jsi_norm = jsi / jsi_max if jsi_max > 0 else jsi
    return {"omega1": omega1, "omega2": omega2, "jsi": jsi_norm,
            "Gamma_1": Gamma_1, "Gamma_2": Gamma_2}


def bell_inequality_analysis(eta_det=0.5, visibility=0.9):
    S_ideal = 2.0 * np.sqrt(2)
    S_measured = visibility * eta_det**2 * S_ideal
    violation = S_measured > 2.0
    min_eta = np.sqrt(2.0 / (visibility * S_ideal))
    return {"S_ideal": S_ideal, "S_measured": S_measured,
            "violation": violation, "min_eta": min_eta}


def demyelination_signature(d_healthy=1.0e-6, d_final=0.1e-6, n_steps=50):
    d_array = np.linspace(d_healthy, d_final, n_steps)
    ent = entanglement_vs_thickness(d_array)
    a = AXON_RADIUS_TYPICAL
    L = INTERNODE_LENGTH_TYPICAL
    Fp_array = np.zeros(n_steps)
    for i, d_val in enumerate(d_array):
        V = mode_volume_cylindrical_shell(a, d_val, L)
        Q = cavity_q_factor(d_val, OMEGA_10, 300.0)
        Fp_array[i] = purcell_factor(Q, V, LAMBDA_10)
    return {"d": d_array, "S": ent["S"], "K": ent["K"],
            "g2_0": ent["g2_0"], "Fp": Fp_array}


def parameter_regime_summary():
    return {
        "wavelength_range_um": (1.8, 4.0),
        "Q_factor_range": (3, 50),
        "coupling_regime": "weak",
        "cooperativity_range": (1e-4, 1e-2),
        "decoherence_time_ps": (0.5, 2.0),
        "coherence_length_um": (1, 10),
        "thermal_photon_number": 1e-6,
        "entanglement_type": "frequency-time",
        "optimal_thickness_um": (0.8, 1.1),
    }


if __name__ == "__main__":
    print("=== Observable Predictions ===\n")

    print("--- g^(2)(0) for different source models ---")
    g2_preds = compute_g2_predictions()
    for state, val in g2_preds.items():
        print(f"  {state:12s}: g^(2)(0) = {val:.2f}")

    print(f"\n--- Spectral Correlation Map ---")
    sc = spectral_correlation_map()
    print(f"  Linewidths: Gamma_1 = {sc['Gamma_1']:.2e}, Gamma_2 = {sc['Gamma_2']:.2e}")

    print(f"\n--- Bell Inequality Analysis ---")
    for eta in [0.3, 0.5, 0.7, 0.9]:
        bell = bell_inequality_analysis(eta)
        status = "VIOLATION" if bell["violation"] else "no violation"
        print(f"  eta={eta:.1f}: S = {bell['S_measured']:.3f} ({status})")
    print(f"  Min eta (V=0.9): {bell_inequality_analysis(0.5, 0.9)['min_eta']:.3f}")

    print(f"\n--- Demyelination Signature ---")
    demyel = demyelination_signature()
    print(f"  d={demyel['d'][0]*1e6:.2f} um: S={demyel['S'][0]:.4f}")
    print(f"  d={demyel['d'][-1]*1e6:.2f} um: S={demyel['S'][-1]:.4f}")

    print(f"\n--- Parameter Regimes ---")
    regime = parameter_regime_summary()
    for key, val in regime.items():
        print(f"  {key}: {val}")
