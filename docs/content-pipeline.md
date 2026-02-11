# Biophoton Research Content Pipeline

## Overview

When simulations produce notable results, they flow through this pipeline:

1. **Discovery** → Finding logged in `FINDINGS_LOG.md`
2. **Commit** → Code + results committed to repo
3. **Report** → Summary posted to Telegram group + Agent Mail
4. **Content** → Finding formatted as podcast segment draft

## Findings Log Format

Each entry in `/home/yesh/biophoton-research/FINDINGS_LOG.md`:

```markdown
## [DATE] [TRACK] Finding Title

**What:** One-sentence summary of the finding.
**Numbers:** Key quantitative result(s).
**Why it matters:** One sentence on significance.
**Files:** List of new/changed files.
**Podcast potential:** [high/medium/low] — brief note on narrative angle.
```

## Podcast Episode Mapping

| Episode | Focus | Status | Key Findings |
|---------|-------|--------|--------------|
| Ep 01 | Demyelination & the Light | Script complete | Track 06 predictions |
| Ep 02 | Can We Actually Measure This? | Planned | Track 05 feasibility, Track 01 statistics |
| Ep 03 | The Quantum Question | Planned | Track 04 cavity QED, entanglement bounds |
| Ep 04 | Building the Simulator | Planned | models/ package, cuprizone results |
| Ep 05 | Mind-Matter & the Phi Field | Planned | Track 08 MMI bridge, QTrainerAI connection |
| Ep 06 | Multi-Scale: Molecules to Networks | Planned | Track 07 unified model |

## OpenClaw Agents Format

For the OpenClaw Agents Podcast, each episode segment is:

```markdown
### Segment: [Title]
**Agent perspective:** Which track agent is "speaking"
**Discovery:** What was found
**The math:** Key equation or number (made accessible)
**The implication:** Why a listener should care
**The honest caveat:** What we don't know yet
**Duration:** ~3-5 minutes per segment
```

## Automation Hooks

When running simulations, append to FINDINGS_LOG.md if any of these trigger:
- New AUC > 0.9 for a biomarker
- First N-sigma detection at a new timepoint
- Cross-track consistency check passes or fails
- New experimental prediction generated
- Parameter regime boundary discovered

## Content Generation Command

```bash
# After a finding is logged:
python3 -m models.simulate cuprizone --weeks 12 --detector SNSPD --output figures/latest_cuprizone.png
# Then generate podcast segment from FINDINGS_LOG.md entry
```
