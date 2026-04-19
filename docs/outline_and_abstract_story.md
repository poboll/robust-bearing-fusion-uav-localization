# Outline and Abstract Story

## Recommended Title Direction

### Safer SCI Title
Robust Collaborative Bearing-Only Passive Localization for UAV Swarms under Degraded Measurements

### Slightly Stronger Title
Geometry-Preserving Robust Passive Localization for Collaborative UAV Systems under Bias, Outliers, and Missing Bearings

### If Later We Reintegrate Recovery/Scheduling
Robust Collaborative Passive Localization and Formation Recovery for UAV Swarms under Degraded Bearing-Only Measurements

## Why This Title Direction Works

- It foregrounds `robust`, which is now supported by evidence.
- It stays in a computer/intelligent-systems style framing.
- It avoids outdated heuristic branding.
- It does not overclaim deep learning or real-world deployment that we have not yet validated.

## Updated Abstract Story Line

1. Passive bearing-only localization is important for UAV collaboration in GNSS-denied or electromagnetically silent scenarios.
2. Classical geometric and least-squares methods are vulnerable to bias, missing observations, and outliers.
3. Pure stochastic heuristics can sometimes recover good solutions, but their behavior is harder to interpret and reproduce.
4. We therefore propose a geometry-preserving robust collaborative localization framework built on consensus geometric initialization, trimming-aware refinement, and iterative residual reweighting.
5. Experiments across biased, outlier, and mixed degraded regimes show improved median accuracy, reduced catastrophic failures, and competitive performance against heuristic baselines.

## Abstract Draft

Passive bearing-only localization is a critical capability for collaborative UAV systems operating in GNSS-degraded or electromagnetically silent environments. However, classical geometric and least-squares estimators are highly sensitive to biased bearings, missing observations, and outlier contamination, while stochastic heuristic solvers are often difficult to interpret and reproduce. This paper proposes a geometry-preserving robust passive localization framework that combines consensus-style geometric initialization, trimming-aware residual filtering, and iterative reweighted refinement for collaborative bearing-only estimation. The method is designed to retain the transparency of classical geometry while improving degraded-regime robustness. Extensive synthetic experiments under biased, outlier, and mixed corruption regimes show that the proposed framework consistently improves stability relative to least-squares baselines, substantially reduces large-error failures, and remains competitive with heuristic global search methods. The resulting pipeline is lightweight, reproducible, and suitable as a computer-oriented foundation for collaborative localization and recovery in UAV swarms.

## Paper Outline

### 1. Introduction
- GNSS-denied / low-emission UAV collaboration as the application background.
- Bearing-only passive localization as the technical problem.
- Why classical geometry alone is insufficient in degraded measurement regimes.
- Contribution list:
  1. a geometry-preserving robust localization framework
  2. a degraded-regime evaluation protocol for biased / outlier / mixed measurements
  3. a reproducible comparison against least squares and stochastic heuristics

### 2. Related Work
- Bearing-only and AOA localization
- Robust estimation under bias / outlier corruption
- Cooperative UAV localization
- Graph-optimization and factor-graph flavored collaborative positioning
- Why we do not choose a purely black-box learning route as the main method

### 3. Problem Formulation
- UAV sensor geometry and target state
- Bearing-only observation model
- Common bias, random noise, missing observation, and outlier perturbation model
- Objective and evaluation criteria

### 4. Proposed Method
- 4.1 Consensus geometric initialization
- 4.2 Trimming-aware and reweighting-based robust refinement
- 4.3 Optional common-bias correction term
- 4.4 Extension path toward observability-aware scheduling and recovery

### 5. Experiments
- 5.1 Degraded-regime benchmark
- 5.2 Baseline comparison
- 5.3 Ablation on bias estimation, trimming, and reweighting
- 5.4 Formation-generalization experiment
- 5.5 Runtime / complexity discussion

### 6. Discussion
- Why the robust framework helps in mixed regimes
- Why heuristic solvers still matter
- Limits of the current evidence
- How this connects to newer graph-optimization / recursive-TLS directions

### 7. Conclusion
- summarize contribution
- note reproducibility
- discuss next steps toward closed-loop swarm recovery and real simulation integration
