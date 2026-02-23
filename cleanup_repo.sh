#!/bin/bash

# Clean up biophoton research repository
# Remove all non-biophoton content

echo "=== Cleaning up biophoton-research repository ==="
echo "Removing podcast, quantum tracks, and unrelated content..."

# Remove track directories (old quantum stuff)
git rm -r track-*/ 2>/dev/null || true
git rm -r worktrees/ 2>/dev/null || true
git rm -r tracks/ 2>/dev/null || true
git rm -r kg/ 2>/dev/null || true
git rm -r src/ 2>/dev/null || true
git rm -r unified_model/ 2>/dev/null || true

# Remove podcast files
git rm docs/podcast-*.mp3 2>/dev/null || true
git rm docs/podcast-*.md 2>/dev/null || true

# Remove unrelated PDFs
git rm "docs/Physical Basis of Coherence_112325.pdf" 2>/dev/null || true
git rm "docs/Quantum Cognition AI System_111925.pdf" 2>/dev/null || true

# Remove other unrelated docs
git rm docs/content-pipeline.md 2>/dev/null || true
git rm docs/master-predictions.md 2>/dev/null || true
git rm docs/research-update-2026.md 2>/dev/null || true
git rm docs/bibliography.md 2>/dev/null || true

# Remove old/unrelated root files
git rm discord_relay_darpa_go_research.md 2>/dev/null || true
git rm README_original.md 2>/dev/null || true
git rm CLAUDE.md 2>/dev/null || true
git rm FINDINGS_LOG.md 2>/dev/null || true
git rm SIMULATIONS_TODO.md 2>/dev/null || true

# Remove loose image files from root (they should be in figures/)
git rm cuprizone_experiment.png 2>/dev/null || true
git rm dose_response.png 2>/dev/null || true
git rm roc_curve.png 2>/dev/null || true
git rm spectrum.png 2>/dev/null || true
git rm spectrum_test.png 2>/dev/null || true
git rm waveguide_modes.png 2>/dev/null || true

# Keep these - they ARE biophoton-related
echo -e "\n=== Keeping biophoton-related docs ==="
echo "✓ docs/experimental-proposal.md - Dai collaboration proposal"
echo "✓ docs/liu_cavity_qed_analysis.md - Analysis of quantum claims" 
echo "✓ docs/relay-model-paper.md - Core theoretical paper"

# Commit the cleanup
echo -e "\n=== Ready to commit cleanup ==="
echo "Run: git commit -m 'Clean repository: Remove quantum tracks, podcasts, and unrelated content'"
echo "Then: git push origin main"