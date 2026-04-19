# Story Reframing and MDPI Submission Plan

## 1. Recommended Story Direction

The paper should no longer be written as:

- a contest-paper extension,
- a heuristic optimizer comparison,
- or a generic “we solve UAV localization” paper.

It should be written as:

`an interpretable robust passive localization core for GNSS-denied collaborative UAV sensing, with a clear upgrade path toward observability-guided active decision-making.`

## 2. Two Submission Versions

## Version S: Safe SCI Version

### Positioning

`Interpretable robust passive localization under degraded bearing measurements`

### What we emphasize

- passive / bearing-only sensing value
- degraded measurements are the real bottleneck
- classical least squares is fragile
- the proposed robust core is reproducible and more stable
- strong benchmark protocol and honest comparison

### What we do not claim

- not a universal best solver
- not a complete autonomous swarm stack
- not a graph-optimization replacement

## Version Q: Stronger Q1-Oriented Version

### Positioning

`Observability-guided active robust bearing-only localization for collaborative UAV systems`

### What we add

- observability score or FIM/CRLB-driven next-view decision
- active sensor / trajectory / subset selection
- comparison against random, greedy, and CRLB baselines
- ablation on robust core versus active decision layer

### Why this version is stronger

- closer to 2024-2026 literature
- more clearly computer-oriented
- adds a real systems-intelligence contribution

## 3. Title Candidates

## Safe Titles

1. `Interpretable Robust Passive Localization for Collaborative UAV Systems under Degraded Bearing Measurements`
2. `Geometry-Preserving Robust Bearing-Only Localization for UAV Swarms with Biased and Outlier-Corrupted Measurements`
3. `Robust Collaborative Passive Localization under Corrupted Bearings: A Reproducible UAV Benchmark Study`

## Stronger Upgrade Titles

1. `Observability-Guided Active Robust Bearing-Only Localization for UAV Swarms in GNSS-Denied Environments`
2. `Active Robust Passive Localization for Collaborative UAV Sensing under Biased and Outlier-Corrupted Bearings`
3. `From Robust Estimation to Active Sensing: Observability-Guided Bearing-Only Localization for UAV Teams`

## 4. Recommended Abstract Logic

The abstract should use this progression:

1. Background:
   GNSS-denied and low-emission UAV collaboration needs passive bearing-only localization.
2. Gap:
   Existing approaches either remain fragile under corrupted bearings or become heavier / less interpretable.
3. Method:
   We build a geometry-preserving robust estimator with trimming-aware and reweighting-based refinement.
4. Results:
   Strongest gains appear in outlier-rich and mixed-corruption regimes; the method reduces catastrophic failures and remains competitive with heuristic search.
5. Implication:
   The method is a reproducible localization core and a foundation for observability-guided active extensions.

## 5. MDPI Journal Recommendation

## Best Immediate Fit

1. `Sensors`
   Best overall balance between sensing context, algorithmic content, and benchmark-style evidence.
2. `Drones`
   Very aligned with UAV passive localization and swarm formation scenarios.
3. `Electronics`
   Works if we strengthen the system/algorithm framing.
4. `Computers`
   Only if the paper is pushed harder toward algorithmic decision-making and software reproducibility.

## Stronger but More Demanding Outside MDPI

- `Robotics and Autonomous Systems`
- `Aerospace Science and Technology`
- `IEEE Sensors Journal`

## 6. Why MDPI Format Is Still Worth Preparing

- It forces the manuscript into a clean journal structure.
- It is fast to reuse for `Sensors` or `Drones`.
- It helps remove the remaining contest / workshop writing traces.

## 7. Official MDPI Template Status

### Local state

- User-provided directory `/Users/Apple/Downloads/学术/论文/SCI/mdpi废` is not a real template directory.
- Official template downloaded to:
  `submission/mdpi_official_template/`

### Official source

- MDPI official LaTeX page: `https://www.mdpi.com/authors/latex`
- Downloaded package: `MDPI_template_ACS.zip` dated `2026-03-13`

## 8. Required MDPI Structure for This Project

The manuscript should be reorganized as:

1. `Introduction`
2. `Related Work`
3. `Problem Formulation`
4. `Proposed Method`
5. `Experimental Setup`
6. `Results`
7. `Discussion`
8. `Conclusions`
9. `Author Contributions`
10. `Funding`
11. `Data Availability Statement`
12. `Conflicts of Interest`
13. `References`

## 9. Recommended Section Story

## Introduction

- Real scenario: GNSS-denied, emission-constrained collaborative UAV sensing.
- Why passive bearing-only remains attractive.
- Why corrupted bearings are the real challenge.
- Why the paper matters beyond a contest setting.

## Related Work

Split the literature into five blocks:

- surveys and UAV localization context
- bearing-only / AOA localization
- passive UAV formation localization
- cooperative and factor-graph localization
- observability / path planning / bias calibration

## Method

Write the current method as:

- geometric candidate generation
- robust residual trimming
- iterative reweighted refinement
- optional common-bias correction

Do not write it as an algorithm cocktail.

## Experiments

Organize by scientific question, not by script order:

1. Does the method resist corrupted bearings?
2. Which component actually matters?
3. Does the advantage persist across formations and sensor counts?
4. Is the result statistically stable?
5. How does geometry explain success and failure?

## Discussion

Must contain two honest points:

- the method is strongest in outlier-rich and mixed regimes
- the method is not yet the strongest Q1-level frontier without an active decision layer

## 10. Experimental Matrix Required Before Submission

## Already Available

- clean / biased / missing / outlier / mixed regimes
- ablation
- formation generalization
- sensitivity sweeps
- scaling with sensor count
- paired significance tests
- observability interpretation
- runtime comparison

## Still Recommended for Version Q

- active waypoint / subset / view selection experiment
- CRLB or FIM-guided baseline
- random policy baseline
- greedy observability baseline
- ablation on observability term, horizon, and robust weighting

## 11. Writing Style Rules for This Paper

- Use restrained claims.
- Never say “significantly better” without numbers.
- Avoid optimizer-centered language like “intelligent algorithm” unless we truly add a decision module.
- Use “interpretable”, “reproducible”, “degraded-regime”, and “geometry-aware” carefully and repeatedly.

## 12. Practical Plan

1. Keep the current robust estimator as the stable core.
2. Use the 79-paper pool for related work and citation grounding.
3. Convert the current manuscript to the official MDPI template.
4. Decide whether to submit Version S now or continue to Version Q.
5. If targeting stronger Q1, prioritize the observability-guided active upgrade before final submission.
