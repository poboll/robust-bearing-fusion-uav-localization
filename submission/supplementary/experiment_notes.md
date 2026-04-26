# Experiment Freeze Notes

## Freeze Date

April 25, 2026

## Execution Commands

```bash
PYTHONPATH=src /opt/homebrew/Caskroom/miniconda/base/bin/python3 run_all_experiments.py
PYTHONPATH=src /opt/homebrew/Caskroom/miniconda/base/bin/python3 run_deadline_replay_validation.py
```

## What This Pipeline Does

1. Reruns regime comparison, ablation, formation-generalization, and runtime experiments sequentially.
2. Reruns severity sensitivity sweeps over outlier rate, common bias, and nominal noise.
3. Reruns sensor-count scaling experiments for circular and random formations.
4. Recomputes paired sign-test style statistical summaries for key regime comparisons.
5. Recomputes oracle observability metrics for interpretation of geometry effects.
6. Rebuilds the measured-data replay, pseudo-physical replay, and PyBullet-facing figures under `experiments/` and mirrors them into `submission/figures/`.
7. Runs the deadline-aware replay validation, which starts from the measured-data replay windows and applies cycle-level arrival, staleness, packet-loss, and deadline filtering before localization.
8. Archives the JSON outputs used in the manuscript tables and figures into `submission/supplementary/frozen_results/`.
9. Packages the curated result-data subset as `submission/supplementary/result_data_bundle.zip` for portals that request a dataset-style upload separate from the full software archive.

## Runtime Measurement Policy

- Runtime is measured after 10 untimed warmup calls per method.
- Each method is then measured over 100 timed repetitions.
- The reported metrics are mean, median, P90, and standard deviation in milliseconds.

## Seed Policy

- The main story benchmark uses 3000 Monte Carlo cases across five corruption regimes and three formation families.
- The fixed-budget screening benchmark uses 2285 retained cases across mixed and severe regimes.
- The RANSAC-family incremental ablation uses 717 retained mixed-corruption cases.
- The measured-data replay and deadline-aware replay layers retain 536 and 227 windows, respectively.
- The PyBullet replay layer contains 1103 replayed localization cycles.

## Frozen Result Highlights

- Outlier-regime median: least squares `1.1186` vs proposed `0.2108`
- Mixed-regime median: least squares `1.0015` vs proposed `0.4346`
- Strict `0.2R` catastrophic-failure rate: outlier `0.2933 -> 0.0400`, mixed `0.2733 -> 0.0683` for least squares vs proposed
- RANSAC-family incremental ablation: `P95 = 2.4951` for Pure RANSAC, `2.2843` for RANSAC+LM, and `2.2740` for the proposed full pipeline
- Fixed-budget screening: all-sensor robust median `0.4981`, adaptive screening median `0.5518`
- Screening-weight sensitivity: default median `0.5586`, pooled 5--95% interval `0.5479--0.5742`, median Jaccard overlap `0.9685`
- Measured-data replay: proposed `P95 = 78.8996 m` in nominal replay and `105.2853 m` in disturbed replay
- Deadline-aware replay retained windows: `227 / 536`; proposed `P95 = 82.7327 m` in nominal deadline replay and `86.0841 m` in disturbed deadline replay
- PyBullet replay: proposed overall median `2.0611`, disturbed-replay `P90 = 18.1859`
- Runtime median: proposed `23.8160 ms`, least squares `1.3987 ms`, and RANSAC `2.6141 ms`

## Archived Files

The final frozen subset contains 26 experiment JSON files plus `manifest.json`. The manifest lists every archived file path and is the authoritative inventory for `submission/supplementary/result_data_bundle.zip`.
