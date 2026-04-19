# Prototype Results Note

## Current Evidence Package

- `experiments/regime_comparison.json`
- `experiments/ablation_result.json`
- `experiments/ablation_summary.json`
- `experiments/batch_result_bt.json`
- `experiments/batch_bt_plot.png`

## What Changed Since the First Prototype

The project is no longer at the stage of “only a benchmark scaffold”.

The robust refinement module has now been upgraded with:
- common-bias-aware residual correction
- small-sample trimming that actually activates with 4-6 bearings
- iterative residual reweighting
- multi-candidate geometric consensus initialization

This changes the paper position materially: the method now has a defensible technical core, not only a simulation wrapper.

## Regime-Level Findings

### Clean
- `robust_bias_trimmed` reaches error `0.0109`, better than least squares (`0.0468`) and better than PSO (`0.0217`) in the current seed-0 demo regime.
- This means the upgraded method does not destroy nominal-regime accuracy.

### Biased
- `robust_bias_trimmed` reduces the error from least squares `0.3668` to about `0.3003` in the regime comparison.
- Across 20 seeds, the default robust variant beats least squares in `14/20` runs.
- Median error drops from `0.3415` to `0.3076`.

### Outlier
- This is currently the strongest evidence regime.
- In the regime comparison, least squares is about `4.1971`, while `robust_bias_trimmed` is about `0.1204`.
- Across 20 seeds, median error drops from `1.6290` to `0.3863`.
- The method beats PSO in `15/20` runs and beats SA in `18/20` runs.
- Catastrophic failure rate above `5.0` is `0.0` for the upgraded robust method in this regime.

### Mixed
- This is the most realistic and most important regime for the paper story.
- In the regime comparison, least squares is about `9.0733`, while `robust_bias_trimmed` is about `0.7516`.
- Across 20 seeds, median error drops from `1.4863` to `0.6779`.
- The method beats least squares in `17/20` runs and beats SA in `15/20` runs.
- Against PSO it is roughly balanced (`10/20` wins), which is scientifically useful:
  the paper can claim improved stability and interpretability without pretending universal dominance over stochastic global search.

## Ablation Findings

### What clearly matters
- Reweighting helps in mixed regimes:
  the default setting outperforms `light_reweight` on median and `p90`.
- Trimming helps control the mixed-regime tail:
  removing trimming raises `p90` from about `1.57` to about `3.18`.
- The robust module is consistently stronger than plain least squares in biased, outlier, and mixed regimes.

### What is less important than expected
- Explicit bias estimation currently contributes less than trimming + reweighting + consensus initialization.
- In the current synthetic setup, turning off bias estimation barely changes the biased-regime median.
- This means the present paper should not overclaim “bias estimation” as the sole key novelty.

## Best Honest Claim Right Now

The strongest current claim is:

`A geometry-preserving robust collaborative localization framework can substantially improve stability under biased, outlier-contaminated, and mixed degraded bearing-only measurements, while remaining lightweight and reproducible.`

## Claims We Should Avoid

- Do not claim the method dominates all heuristic baselines in every regime.
- Do not claim the current experiments prove full real-world UAV autonomy.
- Do not claim the main novelty is only “a new optimization algorithm”.

## Publication Implication

The paper is now strong enough to move from “idea validation” to “manuscript drafting”.

The next strengthening steps should be:
- add formation-generalization experiments
- add runtime / complexity comparison
- add observability-aware scheduling and recovery back into the closed-loop story
- align the method positioning with recent robust bearing-only / AOA / graph-optimization literature
