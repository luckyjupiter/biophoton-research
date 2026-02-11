"""
CLI entry point for biophoton demyelination simulations.

Usage:
    python -m models.simulate cuprizone --weeks 12 --detector PMT --mice 10
    python -m models.simulate spectrum --axon cns --demyelination 0.5
    python -m models.simulate compare --healthy --demyelinated --detector EMCCD
    python -m models.simulate modes --axon cns
"""

from __future__ import annotations

import argparse
import sys

import numpy as np

from . import constants as C
from .axon import AxonGeometry
from .demyelination import DemyelinationState
from .detection import Detector, compute_roc
from .emission import compute_feature_vector, waveguide_filtered_emission
from .cuprizone import CuprizoneExperiment
from .visualization import (
    plot_spectrum,
    plot_timeline,
    plot_roc,
    plot_dose_response,
    plot_waveguide_modes,
)


def _get_axon(name: str) -> AxonGeometry:
    factories = {
        "cns": AxonGeometry.typical_cns,
        "pns": AxonGeometry.typical_pns,
        "optic": AxonGeometry.optic_nerve,
    }
    if name not in factories:
        print(f"Unknown axon type '{name}'. Choose from: {', '.join(factories)}")
        sys.exit(1)
    return factories[name]()


def _get_detector(name: str) -> Detector:
    return Detector.from_name(name)


def cmd_cuprizone(args: argparse.Namespace) -> None:
    """Run a full cuprizone experiment simulation."""
    axon = _get_axon(args.axon)
    detector = _get_detector(args.detector)

    exp = CuprizoneExperiment(
        n_mice=args.mice,
        weeks=args.weeks,
        detector=detector,
        axon=axon,
        exposure_s=args.exposure,
    )
    exp.run(seed=args.seed)
    print(exp.summary())

    if not args.no_plot:
        fig = plot_timeline(exp)
        outfile = args.output or "cuprizone_experiment.png"
        fig.savefig(outfile, dpi=150)
        print(f"\nPlot saved to {outfile}")


def cmd_spectrum(args: argparse.Namespace) -> None:
    """Plot emission spectrum for healthy and/or demyelinated tissue."""
    axon = _get_axon(args.axon)

    state = None
    if args.demyelination > 0:
        state = DemyelinationState(
            alpha=args.demyelination,
            gamma=args.demyelination * 0.6,
            rho=max(0, args.demyelination - 0.3) * 0.5,
        )

    fig = plot_spectrum(axon, state)
    outfile = args.output or "spectrum.png"
    fig.savefig(outfile, dpi=150)
    print(f"Spectrum plot saved to {outfile}")

    # Print key numbers
    lam = C.DEFAULT_LAMBDA_RANGE_NM
    healthy = DemyelinationState(0, 0, 0)
    h_spec = waveguide_filtered_emission(axon, healthy, lam)
    print(f"\nHealthy: peak at {lam[np.argmax(h_spec)]:.0f} nm, "
          f"total = {np.trapezoid(h_spec, lam):.1f} photons/cm²/s")

    if state is not None:
        d_spec = waveguide_filtered_emission(axon, state, lam)
        print(f"Demyelinated: peak at {lam[np.argmax(d_spec)]:.0f} nm, "
              f"total = {np.trapezoid(d_spec, lam):.1f} photons/cm²/s")
        print(f"Enhancement ratio: {np.trapezoid(d_spec, lam) / np.trapezoid(h_spec, lam):.2f}×")


def cmd_compare(args: argparse.Namespace) -> None:
    """Compare healthy vs. demyelinated with ROC analysis."""
    axon = _get_axon(args.axon)
    detector = _get_detector(args.detector)
    rng = np.random.default_rng(args.seed)
    lam = C.DEFAULT_LAMBDA_RANGE_NM

    n_samples = args.samples
    healthy_state = DemyelinationState(0, 0, 0)
    disease_state = DemyelinationState(alpha=0.7, gamma=0.5, rho=0.3)

    print(f"Generating {n_samples} samples each for healthy and demyelinated...")

    healthy_features = []
    disease_features = []
    for _ in range(n_samples):
        healthy_features.append(compute_feature_vector(axon, healthy_state, lam, rng))
        disease_features.append(compute_feature_vector(axon, disease_state, lam, rng))

    # ROC analysis
    roc = compute_roc(healthy_features, disease_features, feature_key="total_intensity")
    print(f"\nROC AUC (total_intensity): {roc['auc']:.3f}")

    # Also check other features
    for feat in ["peak_wavelength", "coherence_degree", "polarization_ratio"]:
        roc_feat = compute_roc(healthy_features, disease_features, feature_key=feat)
        print(f"ROC AUC ({feat}): {roc_feat['auc']:.3f}")

    if not args.no_plot:
        fig = plot_roc(roc)
        outfile = args.output or "roc_curve.png"
        fig.savefig(outfile, dpi=150)
        print(f"\nROC plot saved to {outfile}")


def cmd_modes(args: argparse.Namespace) -> None:
    """Visualize waveguide mode structure."""
    axon = _get_axon(args.axon)
    print(f"Axon: {axon}")
    print(f"Cutoff wavelength: {axon.cutoff_wavelength_nm():.1f} nm")
    print(f"Modes at 400 nm: {axon.num_modes(400)}")
    print(f"Modes at 500 nm: {axon.num_modes(500)}")
    print(f"Modes at 700 nm: {axon.num_modes(700)}")

    if not args.no_plot:
        fig = plot_waveguide_modes(axon)
        outfile = args.output or "waveguide_modes.png"
        fig.savefig(outfile, dpi=150)
        print(f"\nPlot saved to {outfile}")


def cmd_dose(args: argparse.Namespace) -> None:
    """Plot Hill dose-response curves."""
    fig = plot_dose_response()
    outfile = args.output or "dose_response.png"
    fig.savefig(outfile, dpi=150)
    print(f"Dose-response plot saved to {outfile}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="biophoton-sim",
        description="Biophoton Demyelination Simulator",
    )
    subparsers = parser.add_subparsers(dest="command", help="Simulation to run")

    # --- cuprizone ---
    p_cup = subparsers.add_parser("cuprizone", help="Cuprizone experiment simulation")
    p_cup.add_argument("--weeks", type=int, default=12)
    p_cup.add_argument("--mice", type=int, default=10)
    p_cup.add_argument("--detector", default="PMT", choices=["PMT", "EMCCD", "SPAD", "SNSPD"])
    p_cup.add_argument("--axon", default="cns", choices=["cns", "pns", "optic"])
    p_cup.add_argument("--exposure", type=float, default=300.0, help="Exposure time in seconds")
    p_cup.add_argument("--seed", type=int, default=42)
    p_cup.add_argument("--no-plot", action="store_true")
    p_cup.add_argument("--output", "-o", help="Output filename for plot")

    # --- spectrum ---
    p_spec = subparsers.add_parser("spectrum", help="Plot emission spectrum")
    p_spec.add_argument("--axon", default="cns", choices=["cns", "pns", "optic"])
    p_spec.add_argument("--demyelination", "-d", type=float, default=0.0,
                        help="Demyelination alpha (0=healthy, 1=fully stripped)")
    p_spec.add_argument("--no-plot", action="store_true")
    p_spec.add_argument("--output", "-o", help="Output filename for plot")

    # --- compare ---
    p_comp = subparsers.add_parser("compare", help="ROC analysis: healthy vs. demyelinated")
    p_comp.add_argument("--axon", default="cns", choices=["cns", "pns", "optic"])
    p_comp.add_argument("--detector", default="PMT", choices=["PMT", "EMCCD", "SPAD", "SNSPD"])
    p_comp.add_argument("--samples", type=int, default=100)
    p_comp.add_argument("--seed", type=int, default=42)
    p_comp.add_argument("--no-plot", action="store_true")
    p_comp.add_argument("--output", "-o", help="Output filename for plot")

    # --- modes ---
    p_modes = subparsers.add_parser("modes", help="Waveguide mode visualization")
    p_modes.add_argument("--axon", default="cns", choices=["cns", "pns", "optic"])
    p_modes.add_argument("--no-plot", action="store_true")
    p_modes.add_argument("--output", "-o", help="Output filename for plot")

    # --- dose ---
    p_dose = subparsers.add_parser("dose", help="Hill dose-response curves")
    p_dose.add_argument("--output", "-o", help="Output filename for plot")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "cuprizone": cmd_cuprizone,
        "spectrum": cmd_spectrum,
        "compare": cmd_compare,
        "modes": cmd_modes,
        "dose": cmd_dose,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
