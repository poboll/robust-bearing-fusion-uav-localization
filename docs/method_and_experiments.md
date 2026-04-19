# Method and Experiments

## Method Framework

### Stage 1: Consensus Geometric Initialization

Instead of relying on a single fragile closed-form estimate, the current method uses multiple pairwise-bearing intersections to construct several candidate initial states:
- centroid-style initialization
- median-style consensus initialization
- trimmed / inlier-focused initialization

This keeps the method interpretable and makes the later robust stage less sensitive to a single bad intersection pattern.

### Stage 2: Trimming-Aware Robust Refinement

Starting from the geometric candidates, the method performs iterative refinement with:
- Huber-style robust residual modeling
- residual-based reweighting
- small-sample trimming that still activates when only a few bearings are available
- optional common-bias correction

The key design principle is:
preserve the geometry, but prevent a small number of corrupted bearings from dominating the solution.

### Stage 3: Extension Slot for Observability-Aware Scheduling

The current codebase already keeps room for an observability-aware scheduling module.
This stage is not yet the strongest evidence-bearing contribution, so in the current paper it should be treated as:
- an extension path
- a closed-loop collaboration hook
- optional extra experiment if time permits

### Stage 4: Extension Slot for Cooperative Recovery

Formation recovery should remain in the paper roadmap, but only be elevated to a main contribution after stronger experiments are added.

## Baselines

The current baseline family is:
- geometric initialization only
- least squares refinement
- vanilla robust Huber refinement
- PSO
- simulated annealing
- upgraded robust bias-trimmed refinement

This is already a better baseline design than many contest-style rewrites, because it compares:
- classical geometry
- deterministic local refinement
- stochastic global search
- the proposed robust hybrid method

## Evaluation Regimes

### Core Regimes
- clean
- biased
- missing
- outlier
- mixed

### Additional Formation Generalization
- circle
- ellipse
- perturbed
- random

These formation tests are important because otherwise the paper could look too tailored to one idealized geometry.

## Metrics

The paper should not rely on mean error alone.

Recommended primary metrics:
- median localization error
- `p90` localization error
- success rate at thresholds such as `1.0`
- catastrophic failure rate above thresholds such as `5.0`
- paired win count against least squares / PSO / SA

Recommended secondary metrics:
- mean error
- runtime
- iteration count

## Current Strong Evidence

### Biased Regime
- the proposed robust method improves median accuracy over least squares
- it beats least squares in most seeds

### Outlier Regime
- this is the strongest regime for the proposed method
- it substantially reduces error relative to least squares
- it also beats PSO and SA in most seeds

### Mixed Regime
- this is the most publication-relevant regime
- the proposed method clearly improves over least squares and SA
- it is competitive with PSO, which supports a balanced and credible story

## Current Ablation Lessons

- trimming matters for controlling the mixed-regime tail
- iterative reweighting matters for stability
- explicit bias estimation is currently a weaker contributor than robust reweighting and consensus initialization

This is valuable for the manuscript because it helps define the real innovation:
not a single bias parameter trick, but a robust geometry-preserving refinement strategy.

## Recommended Experimental Table Set

### Table 1
Single-regime comparison on clean / biased / missing / outlier / mixed.

### Table 2
20-seed robust statistics:
- median
- p90
- success@1.0
- catastrophic@5.0

### Table 3
Ablation:
- default
- no bias estimation
- no trimming
- light reweight
- heavy trim

### Table 4
Formation generalization:
- circle
- ellipse
- perturbed
- random

### Figure Set
- error distribution plot across seeds
- log-scale comparison plot
- optional boxplot / violin plot by method and regime

## What To Avoid

- do not present PSO only as a weak strawman, because it is actually competitive in some regimes
- do not use only average error as the headline metric
- do not claim recovery / scheduling as a finished core contribution unless we add stronger closed-loop experiments
