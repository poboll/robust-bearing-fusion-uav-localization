# Observability-Robust Active Selection Design

## Goal

Upgrade the existing paper from a static robust estimator to a stronger computer-oriented version by adding an active decision layer that chooses which sensors should be trusted and scheduled.

## Recommended Design

Use a two-stage pipeline:

1. `Pilot robust estimate`
   Run the existing geometry initialization plus robust bias-trimmed refinement on all currently valid bearings.
2. `Active subset scheduling`
   Score candidate subsets using:
   - weighted observability / FIM quality
   - geometry isotropy
   - angular diversity
   - residual-derived reliability from the pilot estimate
3. `Final robust refinement`
   Re-run the robust estimator on the selected subset.

This gives us a method that remains interpretable and reproducible, while adding a clear active-sensing flavor.

## Why This Design

- It reuses the existing strongest module instead of replacing it.
- It matches the latest literature direction: observability, node selection, path planning, and active sensing.
- It is a realistic amount of engineering for the current codebase.

## Baselines

- `All sensors`
- `Random subset`
- `Angular-spread greedy`
- `FIM/CRLB greedy`
- `Observability-robust` proposed policy

## Experiment Matrix

- Regimes:
  - `mixed`
  - `severe`
- Formations:
  - `circle`
  - `perturbed`
  - `random`
- Sensor counts:
  - `8`
  - `10`
  - `12`
- Seeds:
  - `24`

## Acceptance Criteria

- Proposed policy clearly beats `Random` and `Spread`.
- Proposed policy is at least competitive with `FIM/CRLB`.
- The result gives the manuscript a real decision-layer contribution.

## Risks

- If the pilot estimate is very poor, active scheduling can amplify error.
- A one-shot subset scheduler is stronger than the old version, but still weaker than full trajectory planning.

## Next Upgrade After This

If we continue past the current strong version, the next step should be:

`observability-guided waypoint / trajectory planning`

That would be the cleanest bridge toward a harder `Q1` attempt.
