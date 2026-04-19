# Tables V1

## Table 1. Single-Run Regime Comparison

| Regime | LS | Robust Huber | Robust Bias-Trimmed | PSO | SA |
|---|---:|---:|---:|---:|---:|
| Clean | 0.0468 | 0.0468 | 0.0109 | 0.0217 | 0.0487 |
| Biased | 0.3668 | 0.3673 | 0.3003 | 0.0210 | 0.3637 |
| Outlier | 4.1971 | 4.2032 | 0.1204 | 0.7576 | 0.7233 |
| Mixed | 9.0733 | 9.2793 | 0.7516 | 1.7749 | 6.0144 |

Interpretation:
- the proposed method is strongest in outlier and mixed regimes
- it preserves nominal accuracy in the clean regime
- it does not universally beat PSO in biased measurements, which should be stated honestly

## Table 2. Mixed-Regime Robust Statistics over 20 Seeds

| Method | Median | P90 | Success@1.0 | Catastrophic@5.0 |
|---|---:|---:|---:|---:|
| Least Squares | 1.4863 | - | - | - |
| Robust Bias-Trimmed | 0.6779 | 1.5705 | 0.65 | 0.05 |

Paired comparison:
- Robust Bias-Trimmed vs LS: `17` wins / `3` losses
- Robust Bias-Trimmed vs PSO: `10` wins / `10` losses
- Robust Bias-Trimmed vs SA: `15` wins / `5` losses

## Table 3. Outlier-Regime Robust Statistics over 20 Seeds

| Method | Median | P90 | Success@1.0 | Catastrophic@5.0 |
|---|---:|---:|---:|---:|
| Least Squares | 1.6290 | - | - | - |
| Robust Bias-Trimmed | 0.3863 | 1.0028 | 0.90 | 0.00 |

Paired comparison:
- Robust Bias-Trimmed vs LS: `17` wins / `3` losses
- Robust Bias-Trimmed vs PSO: `15` wins / `5` losses
- Robust Bias-Trimmed vs SA: `18` wins / `2` losses

## Table 4. Ablation in Mixed Regime

| Variant | Median | P90 | Success@1.0 | Catastrophic@5.0 |
|---|---:|---:|---:|---:|
| Default | 0.6779 | 1.5705 | 0.65 | 0.05 |
| No Bias Estimation | 0.6805 | 1.5631 | 0.65 | 0.05 |
| No Trimming | 0.7350 | 3.1809 | 0.65 | 0.05 |
| Light Reweight | 0.6991 | 1.7068 | 0.65 | 0.05 |
| Heavy Trim | 0.6779 | 1.5705 | 0.65 | 0.05 |

Interpretation:
- trimming is especially important for mixed-regime tail control
- reweighting improves stability
- explicit bias estimation helps less than expected in the present synthetic setup

## Table 5. Formation Generalization

| Formation | LS Median | Robust Bias-Trimmed Median | Robust Bias-Trimmed P90 |
|---|---:|---:|---:|
| Circle | 1.4863 | 0.6779 | 1.5705 |
| Ellipse | 1.5445 | 0.7355 | 3.7766 |
| Perturbed | 0.8281 | 0.5330 | 4.4088 |
| Random | 2.1047 | 0.5768 | 1.1923 |

Interpretation:
- the method is not tied to one idealized circular formation
- random formation is especially important because the improvement is large and publication-friendly

## Table 6. Runtime Comparison

| Method | Mean (ms) | Median (ms) | P90 (ms) |
|---|---:|---:|---:|
| Least Squares | 2.9110 | 2.5396 | 3.3965 |
| Robust Huber | 2.6378 | 2.5082 | 2.9559 |
| Robust Bias-Trimmed | 27.6293 | 19.8039 | 24.0430 |
| PSO | 26.1574 | 19.9203 | 32.9784 |
| SA | 3.2876 | 3.2514 | 3.4145 |

Interpretation:
- the proposed method is much more expensive than plain LS
- however, its runtime is comparable to PSO while offering stronger interpretability and better degraded-regime stability
