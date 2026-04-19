# B Passive Localization SCI Workspace

This subproject is the working area for turning the 2022B passive localization topic into an SCI manuscript centered on a robust front-end for corrupted bearing fusion in passive multi-UAV localization.

## Structure

- `docs/`: research story, outline, method, experiment plan
- `lit/`: literature assets and notes
- `notes/`: working notes
- `src/`: code scaffold
- `experiments/`: generated outputs
- `submission/`: synchronized manuscript, figures, tables, references, and supplementary package

## Current Research Position

The current manuscript is organized around three concrete contributions:

- consensus-assisted robust bearing fusion under outliers, mixed corruption, pose uncertainty, and heterogeneous bias
- adaptive fixed-budget screening when only a subset of bearings can be fused or transmitted
- a validation chain spanning static Monte Carlo, pseudo-physical replay, and PyBullet multi-vehicle replay

Canonical current docs:

- `docs/review_reframe_2026-04-18.md`
- `docs/submission_execution_plan_2026-04-18.md`
- `submission/pre_submission_audit.md`
- `reproducibility/README.md`

Older planning notes remain in `docs/` as archive material and may reflect superseded wording.

## Run

```bash
conda run -n uu bash -lc 'PYTHONPATH=src python run_demo.py'
conda run -n uu bash -lc 'PYTHONPATH=src python run_batch.py'
conda run -n uu bash -lc 'PYTHONPATH=src python run_regimes.py'
conda run -n uu bash -lc 'PYTHONPATH=src python run_ablation.py'
conda run -n uu bash -lc 'PYTHONPATH=src python run_formations.py'
conda run -n uu bash -lc 'PYTHONPATH=src python run_runtime.py --repeats 100 --warmup 10'
conda run -n uu bash -lc 'PYTHONPATH=src python run_active_selection.py'
conda run -n uu bash -lc 'PYTHONPATH=src python run_all_experiments.py'
conda run -n uu python run_story_revision_analysis.py
conda run -n uu python run_screening_weight_grid.py
conda run -n uu python run_tracking_proxy.py
conda run -n uu python plot_results.py
conda run -n uu python create_graphical_abstract.py
```

## Current Submission State

- `submission/mdpi_manuscript/manuscript_mdpi.tex`: main MDPI-format manuscript source
- `submission/mdpi_manuscript/manuscript_mdpi.pdf`: compiled MDPI manuscript proof
- `submission/manuscript/manuscript_final.md`: human-readable final draft
- `submission/manuscript/manuscript_final.tex`: synchronized backup manuscript source
- `submission/manuscript/manuscript_final.pdf`: compiled PDF proof
- `submission/pre_submission_audit.md`: current completion and remaining-item audit
