# Experiment Freeze Notes

## Freeze Date

April 18, 2026

## Execution Command

```bash
PYTHONPATH=src /opt/homebrew/Caskroom/miniconda/base/bin/python3 run_all_experiments.py
```

## What This Pipeline Does

1. Reruns regime comparison, ablation, formation-generalization, and runtime experiments sequentially.
2. Reruns severity sensitivity sweeps over outlier rate, common bias, and nominal noise.
3. Reruns sensor-count scaling experiments for circular and random formations.
4. Recomputes paired sign-test style statistical summaries for key regime comparisons.
5. Recomputes oracle observability metrics for interpretation of geometry effects.
2. Rebuilds `experiments/*.json` and `experiments/figure_*.png`.
3. Copies the latest figures into `submission/figures/`.
4. Archives the JSON outputs used in the manuscript tables into `submission/supplementary/frozen_results/`.

## Runtime Measurement Policy

- Runtime is measured after 10 untimed warmup calls per method.
- Each method is then measured over 100 timed repetitions.
- The reported metrics are mean, median, P90, and standard deviation in milliseconds.

## Seed Policy

- Core ablation, formation, and significance analyses use 20 random seeds.
- Sensitivity and scaling analyses also use 20 random seeds so that the supplementary evidence matches the main-study statistical scale.

## Frozen Result Highlights

- Outlier regime median: least squares `1.6290` vs robust bias-trimmed `0.3863`
- Mixed regime median: least squares `1.4863` vs robust bias-trimmed `0.6779`
- Random formation median: least squares `2.1047` vs robust bias-trimmed `0.5768`
- Runtime median: robust bias-trimmed `18.9879 ms` vs PSO `18.9073 ms`
- Outlier-rate sweep at `0.40`: least squares `1.9923` vs robust bias-trimmed `0.9189`
- Noise sweep at `0.08`: least squares `1.6024` vs robust bias-trimmed `0.9916`
- Circular 12-UAV scaling: least squares `2.3359` vs robust bias-trimmed `0.4048`
- Outlier paired sign test vs least squares: `17` wins, `3` losses, `p=0.0026`
- Observability isotropy median: `0.6938` for circle vs `0.3358` for random formation

## Archived Files

- `submission/supplementary/frozen_results/regime_comparison.json`
- `submission/supplementary/frozen_results/ablation_result.json`
- `submission/supplementary/frozen_results/ablation_summary.json`
- `submission/supplementary/frozen_results/formation_result.json`
- `submission/supplementary/frozen_results/sensitivity_result.json`
- `submission/supplementary/frozen_results/scaling_result.json`
- `submission/supplementary/frozen_results/significance_result.json`
- `submission/supplementary/frozen_results/observability_result.json`
- `submission/supplementary/frozen_results/runtime_result.json`
- `submission/supplementary/frozen_results/manifest.json`
