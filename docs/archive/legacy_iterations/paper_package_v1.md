# Paper Package V1

## Recommended Main Title

Robust Collaborative Bearing-Only Passive Localization for UAV Swarms under Degraded Measurements

## Alternative Titles

- Geometry-Preserving Robust Passive Localization for Collaborative UAV Systems with Biased and Outlier-Corrupted Bearings
- Robust Bearing-Only Localization for UAV Swarms via Consensus Initialization and Trimming-Aware Refinement
- A Reproducible Robust Passive Localization Framework for Collaborative UAV Systems under Degraded Bearing Measurements

## Best Current Abstract

Passive bearing-only localization is a critical capability for collaborative UAV systems operating in GNSS-degraded or electromagnetically silent environments. However, classical geometric and least-squares estimators are highly sensitive to biased bearings, missing observations, and outlier contamination, while stochastic heuristic solvers are often difficult to interpret and reproduce. This paper proposes a geometry-preserving robust passive localization framework that combines consensus-style geometric initialization, trimming-aware residual filtering, and iterative reweighted refinement for collaborative bearing-only estimation. The method is designed to retain the transparency of classical geometry while improving degraded-regime robustness. Extensive synthetic experiments under biased, outlier, and mixed corruption regimes show that the proposed framework consistently improves stability relative to least-squares baselines, substantially reduces large-error failures, and remains competitive with heuristic global search methods. Additional formation-generalization experiments across circular, elliptical, perturbed, and random swarm geometries further demonstrate that the proposed method is not tied to a single idealized layout. The resulting pipeline is lightweight, reproducible, and suitable as a computer-oriented foundation for collaborative localization and recovery in UAV swarms.

## Introduction First-Page Draft

### Opening Paragraph

Collaborative UAV systems are increasingly expected to operate in GNSS-denied, contested, or electromagnetically silent environments, where active positioning infrastructure may be unavailable or undesirable. In such settings, passive localization based on bearing-only measurements becomes especially attractive because it supports low-emission operation while preserving deployment flexibility. However, bearing-only localization is also notoriously fragile: geometric ambiguity, poor sensor layout, biased measurements, missing observations, and occasional outliers can all produce large estimation errors or outright failure.

### Gap Paragraph

Existing approaches typically fall into two unsatisfactory extremes. On one side, classical geometric and least-squares pipelines are interpretable and lightweight but often break down under degraded measurements. On the other side, stochastic global-search heuristics can occasionally recover strong solutions, yet their behavior is harder to explain, reproduce, and integrate into collaborative autonomy pipelines. This leaves a practical gap for a method that preserves geometric transparency while remaining robust to the kinds of corruption that appear in degraded collaborative sensing.

### Method Paragraph

To address this gap, this paper proposes a geometry-preserving robust passive localization framework for collaborative UAV systems. The method combines consensus-style geometric initialization, trimming-aware residual filtering, and iterative reweighted refinement, with an optional common-bias correction term. Rather than replacing geometric reasoning with a black-box solver, the proposed approach strengthens it so that a small number of corrupted bearings no longer dominate the final estimate.

### Contributions Paragraph

The contributions of this work are threefold. First, a robust collaborative bearing-only localization framework is developed that integrates consensus initialization with trimming-aware reweighted refinement. Second, a degraded-regime evaluation protocol is constructed to systematically test biased, outlier, missing, and mixed bearing corruption. Third, extensive experiments show improved median accuracy and reduced catastrophic failure relative to least-squares baselines, while remaining competitive with stochastic heuristics across multiple swarm formations.

## Main Contribution Claims

### Contribution 1
A geometry-preserving robust bearing-only localization framework based on consensus initialization and trimming-aware iterative refinement.

### Contribution 2
A degraded-regime benchmark protocol that evaluates localization behavior under bias, outliers, missing data, and mixed corruption rather than only nominal noise.

### Contribution 3
A formation-generalization study showing that the method remains effective across circular, elliptical, perturbed, and random UAV layouts.

## Experimental Highlights To Mention

### Biased Regime
- robust method median error about `0.308` versus least squares about `0.342`
- robust method beats least squares in `14/20` runs

### Outlier Regime
- robust method median error about `0.386` versus least squares about `1.629`
- robust method beats PSO in `15/20` runs
- catastrophic failure rate above `5.0` is `0.0`

### Mixed Regime
- robust method median error about `0.678` versus least squares about `1.486`
- robust method beats least squares in `17/20` runs
- robust method is roughly tied with PSO, which supports an honest and credible comparison

### Formation Generalization
- random formation median error drops from about `2.105` with least squares to about `0.577`
- ellipse and perturbed formations also preserve robust advantages in median error

### Runtime
- `robust_bias_trimmed` median runtime is about `19.8 ms`
- `PSO` median runtime is about `19.9 ms`
- this supports a strong practical claim:
  the proposed method achieves stronger degraded-regime stability without costing more than a representative heuristic global search baseline in the current implementation

## Suggested Target Journals

### Better-Fit Computer / Intelligent Systems Direction
- `Engineering Applications of Artificial Intelligence`
- `Applied Soft Computing`
- `Expert Systems with Applications`
- `IEEE Sensors Journal`
- `IEEE Access`
- `Sensors`

### More UAV / Robotics / Sensing Oriented
- `Drones`
- `Unmanned Systems`
- `Aerospace Science and Technology`
- `Robotics and Autonomous Systems`

## Honest Submission Strategy

### If We Stop Now
- good foundation for a solid Q2 or crossover Q1/Q2 venue depending on writing and reviewer fit
- still weaker for a very demanding top-tier一区 because scheduling/recovery/runtime evidence is not fully closed yet

### If We Add One More Round
- add runtime tables
- add boxplots / ECDF plots
- reintroduce observability-aware scheduling or recovery with meaningful evidence
- strengthen related work against recent graph-optimization and recursive-TLS literature

Then a stronger Q1 attempt becomes much more realistic.

## Best Story To Tell

Do not tell this story:
`We invent a brand-new optimization trick and beat everything everywhere.`

Tell this story:
`We build an interpretable robust collaborative localization framework that closes the gap between fragile classical geometry and unstable heuristic search under degraded bearing-only measurements.`
