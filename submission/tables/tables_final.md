# Tables Final

## Table 1. Single-Run Regime Comparison

| Regime | LS | Robust Huber | Robust Bias-Trimmed | PSO | SA |
|---|---:|---:|---:|---:|---:|
| Clean | 0.0468 | 0.0468 | 0.0109 | 0.0217 | 0.0487 |
| Biased | 0.3668 | 0.3673 | 0.3003 | 0.0210 | 0.3637 |
| Missing | 0.0895 | 0.0895 | 0.1289 | 0.0421 | 0.1375 |
| Outlier | 4.1971 | 4.2032 | 0.1204 | 0.7576 | 0.7233 |
| Mixed | 9.0733 | 9.2793 | 0.7516 | 1.7749 | 6.0144 |

## Table 2. Mixed-Regime Statistics over 20 Seeds

| Method | Median | P90 | Success@1.0 | Catastrophic@5.0 |
|---|---:|---:|---:|---:|
| Least Squares | 1.4863 | - | - | - |
| Robust Bias-Trimmed | 0.6779 | 1.5705 | 0.65 | 0.05 |

Paired comparison:
- vs LS: 17 wins / 3 losses
- vs PSO: 10 wins / 10 losses
- vs SA: 15 wins / 5 losses

## Table 3. Outlier-Regime Statistics over 20 Seeds

| Method | Median | P90 | Success@1.0 | Catastrophic@5.0 |
|---|---:|---:|---:|---:|
| Least Squares | 1.6290 | - | - | - |
| Robust Bias-Trimmed | 0.3863 | 1.0028 | 0.90 | 0.00 |

## Table 4. Mixed-Regime Ablation

| Variant | Median | P90 | Success@1.0 | Catastrophic@5.0 |
|---|---:|---:|---:|---:|
| Default | 0.6779 | 1.5705 | 0.65 | 0.05 |
| No Bias Estimation | 0.6805 | 1.5631 | 0.65 | 0.05 |
| No Trimming | 0.7350 | 3.1809 | 0.65 | 0.05 |
| Light Reweight | 0.6991 | 1.7068 | 0.65 | 0.05 |
| Heavy Trim | 0.6779 | 1.5705 | 0.65 | 0.05 |

## Table 5. Formation Generalization

| Formation | LS Median | Robust Bias-Trimmed Median | Robust Bias-Trimmed P90 |
|---|---:|---:|---:|
| Circle | 1.4863 | 0.6779 | 1.5705 |
| Ellipse | 1.5445 | 0.7355 | 3.7766 |
| Perturbed | 0.8281 | 0.5330 | 4.4088 |
| Random | 2.1047 | 0.5768 | 1.1923 |

## Table 6. Implementation-Cost Summary

| Method | Mean (ms) | Median (ms) | P90 (ms) | Std (ms) |
|---|---:|---:|---:|---:|
| Least Squares | 2.3838 | 2.3458 | 2.5074 | 0.0978 |
| Robust Huber | 2.3842 | 2.3483 | 2.5315 | 0.1011 |
| Robust Bias-Trimmed | 19.6486 | 18.9879 | 20.0220 | 3.8435 |
| PSO | 19.5139 | 18.9073 | 21.0830 | 1.8545 |
| SA | 3.3047 | 3.2532 | 3.4737 | 0.1075 |

## Table 7. Severity-Sweep Endpoints

| Sweep | Level | LS Median | Robust Bias-Trimmed Median | PSO Median |
|---|---:|---:|---:|---:|
| Outlier Rate | 0.40 | 1.9923 | 0.9189 | 1.2859 |
| Bias | 0.08 | 1.8939 | 1.1040 | 0.9452 |
| Noise Std | 0.08 | 1.6024 | 0.9916 | 1.0212 |

## Table 8. Sensor-Count Scaling Summary

| Formation | UAV Count | LS Median | Robust Bias-Trimmed Median | PSO Median |
|---|---:|---:|---:|---:|
| Circle | 4 | 1.1880 | 1.0359 | 0.6424 |
| Circle | 8 | 1.1428 | 0.4436 | 0.2502 |
| Circle | 12 | 2.3359 | 0.4048 | 0.3348 |
| Random | 4 | 1.0345 | 0.7221 | 0.6929 |
| Random | 8 | 1.2873 | 0.4179 | 0.4714 |
| Random | 12 | 1.1249 | 0.3687 | 0.4190 |

## Table 9. Paired Sign-Test Summary

| Regime | Comparison | Wins-Losses | Sign-Test p | Median Improvement |
|---|---|---:|---:|---:|
| Outlier | Robust-BT vs LS | 17-3 | 0.0026 | 1.2691 |
| Outlier | Robust-BT vs PSO | 15-5 | 0.0414 | 0.1971 |
| Mixed | Robust-BT vs LS | 17-3 | 0.0026 | 0.2419 |
| Mixed | Robust-BT vs PSO | 10-10 | 1.0000 | 0.0037 |
| Mixed | Robust-BT vs SA | 15-5 | 0.0414 | 0.2472 |
| Biased | Robust-BT vs LS | 14-6 | 0.1153 | 0.0487 |

## Table 10. Credibility-Guided Measurement-Selection Benchmark

| Policy | Overall Median | Success@1.0 | Severe Mean | Severe Catastrophic@5.0 |
|---|---:|---:|---:|---:|
| All Sensors | 0.5510 | 0.7925 | 1.0144 | 0.0094 |
| Random Subset | 0.7491 | 0.6200 | 1.7321 | 0.0798 |
| Angular-Spread Greedy | 0.5676 | 0.7343 | 1.5745 | 0.0657 |
| FIM/CRLB Greedy | 0.5200 | 0.8298 | 1.2450 | 0.0282 |
| Observability-Robust | 0.4977 | 0.8531 | 0.9858 | 0.0188 |

Paired comparison for the proposed policy:
- vs Random: 289 wins / 120 losses
- vs Spread: 216 wins / 160 losses
- vs FIM/CRLB: 72 wins / 61 losses
- vs All-Sensor robust estimation: 200 wins / 222 losses

Interpretation:
The comparison with all-sensor robust estimation is mixed, so Table 10 should be used to support a conditional measurement-selection claim under uncertain or budgeted sensing, not a universal “subset is always better than all sensors” claim.

## Table 11. Observability Summary

| Formation | Isotropy Median | LS Error Median | Robust Bias-Trimmed Median | PSO Median |
|---|---:|---:|---:|---:|
| Circle | 0.6938 | 1.3953 | 0.4229 | 0.3685 |
| Random | 0.3358 | 1.4429 | 0.4732 | 0.4827 |
| Ellipse | 0.6596 | 1.5728 | 0.4542 | 0.3792 |

Additional correlation summary:
- inverse-condition vs LS error Spearman: `-0.0439`
- inverse-condition vs Robust-BT error Spearman: `-0.2300`
- inverse-condition vs PSO error Spearman: `-0.2614`
