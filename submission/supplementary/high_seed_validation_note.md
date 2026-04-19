# High-Seed Validation Note

To respond to concerns that the original 20-seed summaries might be too small for a strong robustness claim, an additional follow-up validation was run with 100 seeds for the two most important degraded regimes.

Output file:

- `experiments/high_seed_validation.json`

Script:

- `run_high_seed_validation.py`

Main findings:

- Outlier regime, Robust-BT vs LS:
  `83 wins / 17 losses`, sign-test `p = 1.31e-11`, median improvement `1.6921`
- Mixed regime, Robust-BT vs LS:
  `75 wins / 25 losses`, sign-test `p = 5.64e-7`, median improvement `0.5511`

These follow-up results preserve the core interpretation of the manuscript:

- the proposed framework is reliably stronger than fragile classical estimation under degraded measurements;
- its relation to heuristic global search remains competitive and regime-dependent rather than universally dominant.
