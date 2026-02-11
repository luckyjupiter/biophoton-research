"""
Master figure and results generation script for Track 06.

Runs all models and generates all figures and result files.

Usage:
    cd src/ && python generate_all_figures.py
"""

import os
import sys
import numpy as np

# Ensure figures and results dirs exist
os.makedirs("../figures", exist_ok=True)
os.makedirs("../results", exist_ok=True)

print("=" * 60)
print("Track 06: Demyelination & Pathology -- Generating All Output")
print("=" * 60)

# 1. Demyelination progression model
print("\n--- Demyelination Progression Model ---")
from demyelination_progression import (
    run_demyelination_progression,
    plot_demyelination_progression,
    solve_coherence_field,
    KAPPA_HEALTHY, N_LAYERS_HEALTHY, WAVELENGTH_SHIFT_PER_LAYER_NM,
    HEALTHY_OPERATING_WAVELENGTH_NM,
)
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

t = np.linspace(0, 20, 500)
results = run_demyelination_progression(t)
plot_demyelination_progression(results)

# Coherence field ODE
alpha_interp = interp1d(results["t"], results["alpha"],
                        bounds_error=False, fill_value=(1.0, 0.0))

def kappa_dynamic(t_val):
    a = float(alpha_interp(t_val))
    return KAPPA_HEALTHY / max(a**2, 0.01)

coh = solve_coherence_field(t_span=(0, 20), kappa_func=kappa_dynamic,
                            Lambda_0=1.0, t_eval=t)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(coh["t"], coh["Lambda"], "b-", linewidth=2)
ax1.set_xlabel("Time (weeks)")
ax1.set_ylabel(r"Coherence Field $\Lambda$")
ax1.set_title("Coherence Field Degradation")
ax1.grid(True, alpha=0.3)
ax2.semilogy(coh["t"], coh["kappa"], "r-", linewidth=2)
ax2.set_xlabel("Time (weeks)")
ax2.set_ylabel(r"Decoherence Rate $\kappa$ (s$^{-1}$)")
ax2.set_title("Effective Decoherence Rate")
ax2.grid(True, alpha=0.3)
fig.suptitle("Coherence Field Under Progressive Demyelination",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("../figures/coherence_field_degradation.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: ../figures/coherence_field_degradation.png")

# 2. MS subtypes
print("\n--- MS Subtype Models ---")
from ms_subtypes import plot_ms_subtypes, plot_ms_overlay
plot_ms_subtypes()
plot_ms_overlay()

# 3. Kappa decomposition
print("\n--- Kappa Decomposition ---")
from kappa_decomposition import (
    plot_kappa_decomposition, plot_kappa_sensitivity,
    scenario_healthy_vs_disease,
)
plot_kappa_decomposition()
plot_kappa_sensitivity()

scenarios = scenario_healthy_vs_disease()
print("\nKappa Decomposition Summary:")
for name, vals in scenarios.items():
    print(f"  {name}: kappa_total={vals['total']:.4f}, Lambda_ss={vals['Lambda_ss']:.6f}")

# 4. Biomarker predictions
print("\n--- Biomarker Predictions ---")
from biomarker_predictions import (
    plot_roc_curves, plot_biomarker_sensitivity,
    generate_predictions_report,
)
plot_roc_curves()
plot_biomarker_sensitivity()
report = generate_predictions_report()
with open("../results/testable_predictions.txt", "w") as f:
    f.write(report)
print("Saved: ../results/testable_predictions.txt")

# 5. Experimental protocol
print("\n--- Experimental Protocol ---")
from experimental_protocol import (
    plot_power_curves, generate_protocol_document,
)
plot_power_curves()
protocol = generate_protocol_document()
with open("../results/experimental_protocol.txt", "w") as f:
    f.write(protocol)
print("Saved: ../results/experimental_protocol.txt")

# Summary
print("\n" + "=" * 60)
print("All figures and results generated successfully.")
print("=" * 60)
print("\nFigures:")
for f in sorted(os.listdir("../figures")):
    if f.endswith(".png"):
        print(f"  figures/{f}")
print("\nResults:")
for f in sorted(os.listdir("../results")):
    print(f"  results/{f}")
