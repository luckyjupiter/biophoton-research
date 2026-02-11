"""CLI for unified model simulations."""

from __future__ import annotations

import argparse
import numpy as np

from .config import SimulationConfig, DemyelinationParams
from .engine import SimulationEngine
from .experiments import demyelination_sweep, cuprizone_series
from .analysis import summarize
from .inversion import invert_spectrum, synthetic_target
from .optimize import optimize_design
from models.axon import AxonGeometry
from models import constants as MC


def _print_summary(name: str, summary: dict) -> None:
    items = ", ".join(f"{k}={v:.3f}" for k, v in summary.items())
    print(f"{name}: {items}")


def cmd_demo(args: argparse.Namespace) -> None:
    cfg = SimulationConfig(
        duration_ms=args.duration_ms,
        detector_name=args.detector,
        exposure_s=args.exposure_s,
        detector_area_cm2=args.area_cm2,
        n_measurements=args.measurements,
        use_full_stack=not args.no_full_stack,
    )
    healthy = SimulationEngine(cfg).run()
    dem = SimulationConfig(
        duration_ms=args.duration_ms,
        demyelination=DemyelinationParams(thickness_loss=0.6, continuity_loss=0.4, irregularity=0.5),
        detector_name=args.detector,
        exposure_s=args.exposure_s,
        detector_area_cm2=args.area_cm2,
        n_measurements=args.measurements,
        use_full_stack=not args.no_full_stack,
    )
    dem_res = SimulationEngine(dem).run()
    _print_summary("healthy", summarize(healthy))
    _print_summary("demyelinated", summarize(dem_res))


def cmd_sweep(args: argparse.Namespace) -> None:
    cfg = SimulationConfig(
        duration_ms=args.duration_ms,
        detector_name=args.detector,
        exposure_s=args.exposure_s,
        detector_area_cm2=args.area_cm2,
        n_measurements=args.measurements,
        use_full_stack=not args.no_full_stack,
    )
    levels = [float(x) for x in args.levels.split(",")]
    results = demyelination_sweep(cfg, levels)
    for level in levels:
        _print_summary(f"loss={level:.2f}", summarize(results[level]))


def cmd_cuprizone(args: argparse.Namespace) -> None:
    cfg = SimulationConfig(
        duration_ms=args.duration_ms,
        detector_name=args.detector,
        exposure_s=args.exposure_s,
        detector_area_cm2=args.area_cm2,
        n_measurements=args.measurements,
        use_full_stack=not args.no_full_stack,
    )
    weeks = [float(x) for x in args.weeks.split(",")]
    results = cuprizone_series(cfg, weeks)
    for week in weeks:
        _print_summary(f"week={week:.1f}", summarize(results[week]))

def cmd_invert(args: argparse.Namespace) -> None:
    axon = AxonGeometry.typical_cns()
    lam = MC.DEFAULT_LAMBDA_RANGE_NM
    if args.target_npy:
        target = np.load(args.target_npy)
    else:
        target = synthetic_target(lam, axon, args.alpha, args.gamma, args.rho)
    grid = [float(x) for x in args.grid.split(",")] if args.grid else None
    result = invert_spectrum(
        lam,
        target,
        axon,
        grid=grid if grid is not None else (0.0, 0.25, 0.5, 0.75, 1.0),
        wavelength_stride=args.stride,
    )
    print(f"inversion: alpha={result.alpha:.2f}, gamma={result.gamma:.2f}, rho={result.rho:.2f}, loss={result.loss:.6f}")


def cmd_optimize(args: argparse.Namespace) -> None:
    detectors = [d.strip() for d in args.detectors.split(",")]
    exposures = [float(x) for x in args.exposures.split(",")]
    weeks = [float(x) for x in args.weeks.split(",")]
    result = optimize_design(
        detectors=detectors,
        exposures_s=exposures,
        area_cm2=args.area_cm2,
        weeks=weeks,
        n_measurements=args.measurements,
    )
    print(f"best: detector={result.detector}, exposure_s={result.exposure_s}, area_cm2={result.area_cm2}, score={result.score:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified biophoton simulation")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_demo = sub.add_parser("demo", help="Run a healthy vs demyelinated comparison")
    p_demo.add_argument("--duration-ms", type=int, default=2000)
    p_demo.add_argument("--detector", type=str, default="PMT")
    p_demo.add_argument("--exposure-s", type=float, default=10.0)
    p_demo.add_argument("--area-cm2", type=float, default=1.0)
    p_demo.add_argument("--measurements", type=int, default=10)
    p_demo.add_argument("--no-full-stack", action="store_true")
    p_demo.set_defaults(func=cmd_demo)

    p_sweep = sub.add_parser("sweep", help="Sweep demyelination levels")
    p_sweep.add_argument("--levels", type=str, default="0.0,0.3,0.6,0.9")
    p_sweep.add_argument("--duration-ms", type=int, default=2000)
    p_sweep.add_argument("--detector", type=str, default="PMT")
    p_sweep.add_argument("--exposure-s", type=float, default=10.0)
    p_sweep.add_argument("--area-cm2", type=float, default=1.0)
    p_sweep.add_argument("--measurements", type=int, default=10)
    p_sweep.add_argument("--no-full-stack", action="store_true")
    p_sweep.set_defaults(func=cmd_sweep)

    p_cup = sub.add_parser("cuprizone", help="Run cuprizone week series")
    p_cup.add_argument("--weeks", type=str, default="1,3,5,7,10")
    p_cup.add_argument("--duration-ms", type=int, default=2000)
    p_cup.add_argument("--detector", type=str, default="PMT")
    p_cup.add_argument("--exposure-s", type=float, default=10.0)
    p_cup.add_argument("--area-cm2", type=float, default=1.0)
    p_cup.add_argument("--measurements", type=int, default=10)
    p_cup.add_argument("--no-full-stack", action="store_true")
    p_cup.set_defaults(func=cmd_cuprizone)

    p_inv = sub.add_parser("invert-spectrum", help="Invert demyelination parameters from spectrum")
    p_inv.add_argument("--alpha", type=float, default=0.6)
    p_inv.add_argument("--gamma", type=float, default=0.4)
    p_inv.add_argument("--rho", type=float, default=0.5)
    p_inv.add_argument("--target-npy", type=str, default="")
    p_inv.add_argument("--grid", type=str, default="")
    p_inv.add_argument("--stride", type=int, default=6)
    p_inv.set_defaults(func=cmd_invert)

    p_opt = sub.add_parser("optimize-design", help="Optimize detector + exposure for separability")
    p_opt.add_argument("--detectors", type=str, default="PMT,EMCCD,SPAD,SNSPD")
    p_opt.add_argument("--exposures", type=str, default="1,5,10,30")
    p_opt.add_argument("--area-cm2", type=float, default=1.0)
    p_opt.add_argument("--weeks", type=str, default="1,3,5,7,10")
    p_opt.add_argument("--measurements", type=int, default=20)
    p_opt.set_defaults(func=cmd_optimize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
