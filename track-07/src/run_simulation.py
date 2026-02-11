#!/usr/bin/env python3
"""Standalone entry point for the unified multi-scale biophoton model.

Usage:
    python -m src.run_simulation
    python -m src.run_simulation --sweep coupling_K --min 0.001 --max 0.1 --steps 20
"""

import argparse
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .multiscale_simulator import run_multiscale, parameter_sweep
from .coherence_solver import solve_coherence_1d, bifurcation_analysis


def run_default():
    """Run default multiscale simulation and print summary."""
    print("=" * 60)
    print("Unified Multi-Scale Biophoton Model")
    print("=" * 60)

    result = run_multiscale()
    s = result["summary"]

    print(f"\n--- Scale 1: Molecular Generation ---")
    print(f"  Photon generation rate: {s['photon_generation_rate']:.2e} photons/s per axon")

    print(f"\n--- Scale 2: Waveguide Transport ---")
    print(f"  Waveguide transmission: {s['waveguide_transmission']:.2e}")
    print(f"  Delivered photon rate:  {s['delivered_photons']:.2e} photons/s")
    mode = result["scale2"]["mode_info"]
    v_str = "single-mode" if mode["single_mode"] else f"{mode['n_modes']} modes"
    print(f"  V-number: {mode['V_number']:.3f} ({v_str})")

    print(f"\n--- Scale 3: Network Coherence ---")
    print(f"  Network sync (r):      {s['network_sync_r']:.4f}")
    print(f"  Coherence Lambda:      {s['coherence_Lambda']:.6f}")
    print(f"  Neuro-coherence M:     {s['neurocoherence_M']:.6f}")

    return result


def run_sweep(param_name, param_min, param_max, steps):
    """Run parameter sweep and generate plot."""
    print(f"Sweeping {param_name} from {param_min} to {param_max} ({steps} steps)")

    values = np.linspace(param_min, param_max, steps)
    results = parameter_sweep(param_name, values)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"Parameter Sweep: {param_name}", fontsize=14)

    axes[0, 0].plot(values, results["photon_rate"])
    axes[0, 0].set_ylabel("Photon Rate (photons/s)")
    axes[0, 0].set_xlabel(param_name)
    axes[0, 0].set_yscale("log")

    axes[0, 1].plot(values, results["transmission"])
    axes[0, 1].set_ylabel("Waveguide Transmission")
    axes[0, 1].set_xlabel(param_name)

    axes[1, 0].plot(values, results["sync_r"])
    axes[1, 0].set_ylabel("Network Sync (r)")
    axes[1, 0].set_xlabel(param_name)

    axes[1, 1].plot(values, results["M"])
    axes[1, 1].set_ylabel("Neuro-coherence M")
    axes[1, 1].set_xlabel(param_name)

    plt.tight_layout()
    outpath = f"figures/sweep_{param_name}.png"
    plt.savefig(outpath, dpi=150)
    print(f"Saved: {outpath}")


def run_coherence_demo():
    """Run 1D coherence solver demo and plot."""
    print("\n--- 1D Coherence Evolution Demo ---")

    result = solve_coherence_1d(
        length=1e-3, n_points=100, t_span=(0, 50)
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Spatiotemporal evolution
    im = ax1.pcolormesh(result["t"], result["x"] * 1e3, result["Lambda"],
                        shading="auto", cmap="inferno")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Position (mm)")
    ax1.set_title("Coherence Field Lambda(x, t)")
    plt.colorbar(im, ax=ax1, label="Lambda")

    # Final profile vs steady state
    ax2.plot(result["x"] * 1e3, result["Lambda"][:, -1], "b-", label="Final Lambda")
    ax2.plot(result["x"] * 1e3, result["steady_state"], "r--", label="Steady state")
    ax2.set_xlabel("Position (mm)")
    ax2.set_ylabel("Lambda")
    ax2.set_title("Final vs Steady-State Profile")
    ax2.legend()

    plt.tight_layout()
    plt.savefig("figures/coherence_1d_demo.png", dpi=150)
    print("Saved: figures/coherence_1d_demo.png")


def main():
    parser = argparse.ArgumentParser(description="Unified Multi-Scale Biophoton Model")
    parser.add_argument("--sweep", type=str, help="Parameter to sweep")
    parser.add_argument("--min", type=float, default=0.001)
    parser.add_argument("--max", type=float, default=0.1)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--coherence-demo", action="store_true",
                        help="Run 1D coherence solver demo")
    args = parser.parse_args()

    result = run_default()

    if args.sweep:
        run_sweep(args.sweep, args.min, args.max, args.steps)

    if args.coherence_demo:
        run_coherence_demo()

    # Bifurcation analysis
    print("\n--- Bifurcation Analysis ---")
    bif = bifurcation_analysis()
    print(f"  Critical g (Lambda_ss = 1): {bif['critical_g']:.4f}")

    return result


if __name__ == "__main__":
    main()
