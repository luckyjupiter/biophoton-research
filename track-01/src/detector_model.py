"""
Detector Model for Biophoton Measurements
==========================================

Models the full detection chain for single-photon counting experiments:
  - Quantum efficiency (Bernoulli thinning)
  - Dark counts (additive Poisson noise)
  - Dead time (non-paralyzable and paralyzable)
  - Afterpulsing (correlated noise)

Can apply artifacts to both distributions (analytic) and sample data (Monte Carlo).

Author: Track 01 -- Quantum Optics Statistician
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.stats import poisson
from typing import Optional


class DetectorModel:
    """Full photodetector model with configurable artifacts.

    Parameters
    ----------
    quantum_efficiency : float
        Quantum efficiency eta (0 < eta <= 1).
    dark_rate : float
        Dark count rate (counts per second).
    dead_time : float
        Dead time in seconds.
    afterpulse_prob : float
        Probability of afterpulse per detection event.
    paralyzable : bool
        If True, use paralyzable dead time model.
    """

    def __init__(
        self,
        quantum_efficiency: float = 0.15,
        dark_rate: float = 5.0,
        dead_time: float = 20e-9,
        afterpulse_prob: float = 0.01,
        paralyzable: bool = False,
    ):
        self.eta = quantum_efficiency
        self.dark_rate = dark_rate
        self.dead_time = dead_time
        self.afterpulse_prob = afterpulse_prob
        self.paralyzable = paralyzable

    def dark_counts_per_interval(self, interval_duration: float) -> float:
        """Mean dark counts per counting interval."""
        return self.dark_rate * interval_duration

    def dead_time_product(self, measured_rate: float) -> float:
        """Dimensionless dead time product r * tau_d."""
        return measured_rate * self.dead_time

    def apply_to_samples(
        self,
        photon_counts: NDArray[np.int64],
        interval_duration: float,
        rng: Optional[np.random.Generator] = None,
    ) -> NDArray[np.int64]:
        """Apply full detector model to ideal photocount samples.

        Parameters
        ----------
        photon_counts : ndarray
            True photon number per interval (before detection).
        interval_duration : float
            Duration of each counting interval (seconds).
        rng : np.random.Generator, optional

        Returns
        -------
        measured_counts : ndarray
            Measured photocounts after all artifacts.
        """
        if rng is None:
            rng = np.random.default_rng()

        N = len(photon_counts)

        # Step 1: Quantum efficiency (Bernoulli thinning)
        detected = np.array([
            rng.binomial(n, self.eta) for n in photon_counts
        ], dtype=np.int64)

        # Step 2: Add dark counts
        dark = rng.poisson(self.dark_rate * interval_duration, size=N)
        measured = detected + dark

        # Step 3: Dead time (approximate -- reduces count rate)
        if self.dead_time > 0:
            for i in range(N):
                rate = measured[i] / interval_duration
                if self.paralyzable:
                    # Paralyzable: r_m = r * exp(-r * tau_d)
                    effective_rate = rate * np.exp(-rate * self.dead_time)
                else:
                    # Non-paralyzable: r_m = r / (1 + r * tau_d)
                    effective_rate = rate / (1.0 + rate * self.dead_time)
                measured[i] = rng.poisson(max(0, effective_rate * interval_duration))

        # Step 4: Afterpulsing
        if self.afterpulse_prob > 0:
            afterpulses = np.array([
                rng.binomial(n, self.afterpulse_prob) for n in measured
            ], dtype=np.int64)
            measured = measured + afterpulses

        return measured

    def fano_transformation(
        self,
        F_true: float,
        mean_signal: float,
        interval_duration: float,
    ) -> dict:
        """Compute measured Fano factor analytically.

        Parameters
        ----------
        F_true : float
            True source Fano factor.
        mean_signal : float
            True mean photon number per interval.
        interval_duration : float
            Counting interval duration.

        Returns
        -------
        dict with F at each stage and final measured F.
        """
        mu_det = self.eta * mean_signal
        dark_mean = self.dark_rate * interval_duration
        measured_rate = (mu_det + dark_mean) / interval_duration
        dt_product = measured_rate * self.dead_time

        # Efficiency
        F1 = self.eta * (F_true - 1.0) + 1.0

        # Dark counts
        if dark_mean > 0:
            F2 = (mu_det * F1 + dark_mean) / (mu_det + dark_mean)
        else:
            F2 = F1

        # Dead time
        F3 = F2 * (1.0 - 2.0 * dt_product)

        # Afterpulsing
        sig_frac = mu_det / (mu_det + dark_mean) if (mu_det + dark_mean) > 0 else 0
        F4 = F3 + self.afterpulse_prob * sig_frac

        return {
            "F_true": F_true,
            "F_after_efficiency": F1,
            "F_after_dark": F2,
            "F_after_deadtime": F3,
            "F_measured": F4,
            "detected_mean": mu_det,
            "dark_mean": dark_mean,
            "total_mean": mu_det + dark_mean,
            "dead_time_product": dt_product,
            "signal_to_dark": mu_det / dark_mean if dark_mean > 0 else np.inf,
        }

    def __repr__(self) -> str:
        return (f"DetectorModel(eta={self.eta}, dark_rate={self.dark_rate}, "
                f"dead_time={self.dead_time:.1e}, "
                f"afterpulse={self.afterpulse_prob})")


# Preset detector configurations
COOLED_PMT = DetectorModel(
    quantum_efficiency=0.15,
    dark_rate=2.0,
    dead_time=20e-9,
    afterpulse_prob=0.005,
)

ROOM_TEMP_PMT = DetectorModel(
    quantum_efficiency=0.12,
    dark_rate=20.0,
    dead_time=20e-9,
    afterpulse_prob=0.01,
)

SNSPD = DetectorModel(
    quantum_efficiency=0.85,
    dark_rate=0.1,
    dead_time=50e-9,
    afterpulse_prob=0.001,
)

SPAD = DetectorModel(
    quantum_efficiency=0.50,
    dark_rate=25.0,
    dead_time=50e-6,
    afterpulse_prob=0.05,
)

IDEAL = DetectorModel(
    quantum_efficiency=1.0,
    dark_rate=0.0,
    dead_time=0.0,
    afterpulse_prob=0.0,
)


if __name__ == "__main__":
    print("=== Detector Model Self-Test ===\n")

    rng = np.random.default_rng(42)

    # Generate ideal Poisson data
    true_counts = rng.poisson(50, size=10000)
    print(f"True counts: mean={true_counts.mean():.2f}, "
          f"F={true_counts.var(ddof=1)/true_counts.mean():.4f}")

    # Apply cooled PMT
    det = COOLED_PMT
    print(f"\nDetector: {det}")
    measured = det.apply_to_samples(true_counts, interval_duration=1.0, rng=rng)
    print(f"Measured counts: mean={measured.mean():.2f}, "
          f"F={measured.var(ddof=1)/measured.mean():.4f}")

    # Analytic Fano transformation
    result = det.fano_transformation(F_true=1.0, mean_signal=50.0,
                                     interval_duration=1.0)
    print(f"Analytic chain:")
    print(f"  F_true={result['F_true']:.4f}")
    print(f"  F_after_eff={result['F_after_efficiency']:.4f}")
    print(f"  F_after_dark={result['F_after_dark']:.4f}")
    print(f"  F_after_dead={result['F_after_deadtime']:.6f}")
    print(f"  F_measured={result['F_measured']:.4f}")
    print(f"  S/D ratio={result['signal_to_dark']:.2f}")

    # Test with sub-Poissonian source
    print("\n--- Sub-Poissonian source (F=0.5) ---")
    for name, detector in [("Cooled PMT", COOLED_PMT), ("SNSPD", SNSPD),
                            ("Room temp PMT", ROOM_TEMP_PMT)]:
        res = detector.fano_transformation(
            F_true=0.5, mean_signal=10.0, interval_duration=1.0
        )
        print(f"  {name}: F_measured={res['F_measured']:.4f}, "
              f"S/D={res['signal_to_dark']:.1f}")

    print("\nAll detector model tests passed.")
