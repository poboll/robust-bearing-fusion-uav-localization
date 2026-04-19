# Figure Captions V1

## Figure 1

**Regime comparison under clean, biased, missing, outlier, and mixed measurements.**
The proposed robust bias-trimmed method preserves low nominal error in the clean regime and shows its strongest advantage under outlier and mixed degradation. The plot is shown on a log scale to make both nominal and degraded behavior visible in one figure.

File:
- `experiments/figure_regime_comparison.png`

## Figure 2

**Mixed-regime ablation of the proposed robust framework.**
The figure compares the default configuration with variants that remove bias estimation, remove trimming, reduce reweighting, or increase trimming. The results show that trimming is especially important for controlling the upper tail of the error distribution.

File:
- `experiments/figure_ablation_mixed.png`

## Figure 3

**Formation generalization across circular, elliptical, perturbed, and random swarm layouts.**
The proposed method consistently improves over least squares across all tested formations. The random-formation case is particularly important because it shows that the method is not tied to one idealized circular geometry.

File:
- `experiments/figure_formation_generalization.png`

## Figure 4

**Median runtime comparison among deterministic, heuristic, and proposed robust estimators.**
Although the proposed method is more expensive than least squares, it has nearly the same median runtime as PSO in the current implementation, supporting its practical value as a structured alternative to heuristic global search.

File:
- `experiments/figure_runtime_comparison.png`
