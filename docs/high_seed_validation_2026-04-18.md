# High-Seed Validation Note

Date: 2026-04-18

Purpose:

- respond to the criticism that the original 20-seed summaries were too small to support a strong robustness claim.

## Setup

- script: `run_high_seed_validation.py`
- output: `experiments/high_seed_validation.json`
- seed count: `100`
- regimes: `outlier`, `mixed`
- method configuration: default `MethodConfig()`

## Main Results

### Outlier regime

- Robust-BT median error: `0.4123`
- LS median error: `2.1377`
- PSO median error: `0.5798`
- Robust-BT vs LS:
  `83 wins / 17 losses`, `p = 1.31e-11`
- median improvement over LS:
  `1.6921`, bootstrap 95% CI `[1.1023, 2.1663]`

Interpretation:

- the strong advantage over fragile classical estimation survives at 100 seeds;
- the advantage over PSO is weaker and should not be overstated.

### Mixed regime

- Robust-BT median error: `0.6529`
- LS median error: `1.5501`
- PSO median error: `0.5351`
- Robust-BT vs LS:
  `75 wins / 25 losses`, `p = 5.64e-7`
- median improvement over LS:
  `0.5511`, bootstrap 95% CI `[0.1310, 1.2295]`

Interpretation:

- the advantage over LS remains statistically stable;
- PSO remains competitive and can be stronger in part of the mixed regime.

## Use In Manuscript

The correct narrative supported by this follow-up test is:

- the proposed framework is reliably better than fragile classical estimation under degraded measurements;
- its relation to heuristic global search is competitive and regime-dependent;
- therefore the paper should not claim universal superiority, but it can claim statistically stable robustness gains over least squares.
