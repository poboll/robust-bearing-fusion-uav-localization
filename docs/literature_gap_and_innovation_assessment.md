# Literature Gap and Innovation Assessment

## 1. Corpus Snapshot

- Curated literature pool size: `79` real papers.
- Coverage window: `2018-2026`.
- Corpus root: `.pipeline/literature/passive-localization-2026-sci/`
- Machine-readable index: `.pipeline/literature/passive-localization-2026-sci/library_index.json`
- BibTeX export: `submission/mdpi_manuscript/references_curated.bib`

### Theme Distribution

- `22` papers: passive UAV systems
- `19` papers: cooperative / distributed localization
- `18` papers: bearing-only core methods
- `11` papers: active sensing / path planning / target motion analysis
- `6` papers: surveys and scope
- `5` papers: factor graph / graph optimization
- `3` papers: robustness / bias handling
- `2` papers: geometry / observability

## 2. What the 2024-2026 Literature Is Actually Doing

From the latest pool, the field is moving along four visible directions.

### A. Passive / Bearing-Only UAV Localization Is Still Active

Representative papers include:

- `Bearing-Only Passive Localization and Optimized Adjustment for UAV Formations Under Electromagnetic Silence` (Drones, 2025)
- `Node Selection and Path Optimization for Passive Target Localization via UAVs` (Sensors, 2025)
- `Variable-Speed UAV Path Optimization Based on the CRLB Criterion for Passive Target Localization` (Sensors, 2025)
- `Research on Precise Localization and Cooperative Control of UAV Formation Flight Based on Passive Bearing-Only Localization` (IEEE conference, 2024)

Interpretation:

- The topic is not dead.
- Passive / azimuth-only / bearing-only UAV positioning remains publishable.
- But recent papers are no longer satisfied by a plain triangulation story. They usually add path planning, observability, cooperative constraints, or system integration.

### B. Observability and Trajectory Design Are Becoming the Real Upgrade Lever

Representative papers include:

- `Trajectory Optimization to Enhance Observability for Bearing-Only Target Localization and Sensor Bias Calibration` (Biomimetics, 2024)
- `Bio-Inspired Observability Enhancement Method for UAV Target Localization and Sensor Bias Estimation with Bearing-Only Measurement` (Biomimetics, 2025)
- `Trajectory Optimization for Target Localization With Bearing-Only Measurement` (IEEE Transactions on Robotics, 2019)
- `Multi-UAV Trajectory Optimization for Bearing-Only Localization in GPS Denied Environments` (arXiv, 2026)

Interpretation:

- The frontier is not just “estimate better from the same bearings”.
- The stronger story is “actively improve the geometry / sensing / next measurement”.
- This is the clearest bridge to a more computer-oriented paper.

### C. Cooperative Multi-UAV Localization Is Getting More Systematic

Representative papers include:

- `Formation-Constrained Cooperative Localization for UAV Swarms in GNSS-Denied Environments` (Sensors, 2026)
- `A High-Precision Cooperative Localization Method for UAVs Based on Multi-Condition Constraints` (Sensors, 2026)
- `Set-Membership Estimation Based Distributed Cooperative Localization of Multiple UAVs` (IEEE TSIPN, 2026)
- `Target localization in UAV swarm under multi-error coupling: A cooperative utility of information optimization approach` (Ad Hoc Networks, 2026)

Interpretation:

- Reviewers will expect the paper to acknowledge the system-level cooperative literature.
- If we position the paper only as a single-shot estimator, it will look narrow.
- If we position it as a robust core inside a collaborative localization pipeline, it becomes easier to justify.

### D. Factor Graph and Robust System Estimation Are the Stronger Baseline Family

Representative papers include:

- `A distributed factor graph model solving method for cooperative localization of UAV swarms` (Measurement Science and Technology, 2024)
- `UAV Localization Algorithm Based on Factor Graph Optimization in Complex Scenes` (Sensors, 2022)
- `Tightly coupled integrated navigation system via factor graph for UAV indoor localization` (Aerospace Science and Technology, 2020)

Interpretation:

- These papers define the “strong systems baseline” direction.
- Our current method is lighter and more interpretable, but not stronger than the factor-graph literature in system richness.
- Therefore the manuscript should not claim to replace graph optimization. It should claim to provide an interpretable robust core and a degraded-regime benchmark.

## 3. Is the Current Direction an Innovation Point?

### Short Answer

`Yes, but only if framed honestly.`

### What Is Not Strong Enough as a Standalone Innovation

- “Trimmed + reweighted robust estimation” by itself is not a frontier-level algorithmic novelty.
- “We combine geometry with PSO / SA comparisons” is not enough for a strong SCI pitch in 2026.
- “We improve a mathematical-modeling contest solution” is not a publishable innovation statement.

### What Can Still Be Claimed as a Real Contribution

The current project can credibly claim three things:

1. `Interpretable robust passive localization core`
   A geometry-preserving estimator that is lightweight, reproducible, and materially more stable than least squares under corrupted bearings.

2. `Degraded-regime benchmark`
   A structured evaluation across bias, outliers, mixed corruption, scaling, formation variation, significance testing, and observability interpretation.

3. `Practical middle-ground positioning`
   The method sits between fragile classical geometry and heavier graph / heuristic / black-box pipelines.

### Honest Innovation Verdict

- `SCI-safe innovation`: yes
- `mid-tier SCI with clean story`: yes
- `strong Q1 / top-tier computer-oriented novelty`: not yet

## 4. Why the Current Manuscript Is Not Yet Strong Enough for a Hard Q1 Push

### Limitation 1: Method novelty is incremental

The current method is meaningful, but the step from robust initialization + trimming + reweighting to “hard Q1 novelty” is still too small.

### Limitation 2: The paper is still mostly static estimation

Recent stronger papers increasingly include:

- trajectory optimization
- observability-aware sensing
- system constraints
- cooperative decision or planning

Our current manuscript is still strongest as a static degraded-estimation study.

### Limitation 3: The strongest experimental story is robustness, not frontier intelligence

The current experiments already support:

- outlier robustness
- mixed corruption robustness
- reproducibility
- formation generalization

But they do not yet support:

- active sensing superiority
- planning intelligence
- real-time closed-loop adaptation
- graph-level collaborative inference

## 5. Recommended Upgrade Directions

## Option A. Observability-Guided Active Robust Localization

### Core idea

Use the current robust estimator as the measurement-update core, then add an active module that chooses:

- the next UAV subset,
- the next viewing geometry,
- or the next waypoint / motion primitive

to improve observability and robustness under corrupted bearings.

### Why this is the best option

- Most aligned with the newest literature.
- Most natural for a computer-oriented author.
- Reuses the current estimator instead of discarding it.
- Turns the paper from “robust estimator only” into “robust estimator + intelligent decision layer”.

### Publication effect

This is the clearest path from a publishable SCI manuscript to a possible stronger Q1 attempt.

## Option B. Robust Factor-Graph Collaborative Localization

### Core idea

Replace or wrap the current refinement as robust factors in a collaborative graph-optimization pipeline.

### Pros

- Stronger systems flavor.
- Easier to compare with modern cooperative localization papers.

### Cons

- Heavier engineering lift.
- Harder to finish cleanly from the current codebase.
- Less obviously “computer-intelligent” than active planning.

## Option C. Learning-Augmented Bearing Reliability Prediction

### Core idea

Train a light model to predict bearing trustworthiness or candidate weights before robust refinement.

### Pros

- Looks more “computer”.

### Cons

- Requires a much larger synthetic data and generalization story.
- Risky and easy to overfit.
- Harder to defend if the data are purely simulated.

## Recommendation

`Option A is the recommended main path.`

## 6. Recommended Main Story After the Upgrade

The most credible upgraded story is:

`In GNSS-denied and electromagnetically silent UAV collaboration, corrupted bearings are unavoidable and static geometry is often insufficient. We therefore build an observability-guided active robust bearing-only localization framework that couples an interpretable robust estimator with sensing/trajectory decisions that improve geometry quality under corrupted measurements.`

That story is:

- realistic,
- literature-aligned,
- computer-oriented,
- and still compatible with the current codebase.

## 7. What the Existing 2022B Local Papers Are Still Useful For

These local papers should be treated as internal design inspiration, not frontier references.

### Best use of current local B papers

- `B263`: main skeleton and solution flow
- `B174`: geometric ambiguity handling
- `B49`: localization-to-adjustment loop
- `B42`: clean baseline formulation
- `B77`: uncertainty wording

### What to borrow

- clean variable definitions
- closed-loop narrative structure
- ambiguity discussion
- adjustment / movement phrasing

### What not to borrow

- outdated optimizer-centered novelty framing
- contest-style overpacking
- unsupported real-world claims

## 8. Submission-Level Conclusion

### If we submit the current work with only polishing

Best framing:

- interpretable robust passive localization
- degraded-regime benchmark
- reproducible collaborative estimation study

Most realistic journal tier:

- `Drones`
- `Sensors`
- `Computers`
- `Electronics`

### If we complete the active observability upgrade

Best framing:

- observability-guided active robust bearing-only localization
- collaborative sensing and trajectory design under corrupted measurements

Then a stronger Q1 push becomes more credible, though still not guaranteed.

## 9. Bottom-Line Decision

The direction is worth continuing.

But the publishable center of gravity should shift from:

`a nicer robust estimator`

to:

`an interpretable robust localization core plus a modern observability-aware decision layer`.
