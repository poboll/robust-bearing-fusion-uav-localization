# Robust Bearing Fusion for Multi-UAV Passive Localization

This repository is the cleaned working tree for an SCI-style manuscript on robust front-end estimation under corrupted bearing-only measurements in passive multi-UAV localization. The project is organized around one canonical MDPI manuscript, one reproducible experiment pipeline, and one synchronized submission package.

## Repository Layout

- `docs/`: research story, outline, method, experiment plan
- `lit/`: literature assets and notes
- `notes/`: working notes
- `src/`: code scaffold
- `experiments/`: generated outputs
- `submission/`: canonical manuscript, figures, tables, and supplementary submission assets

## Current Research Position

The current manuscript is organized around three concrete contributions:

- consensus-assisted robust bearing fusion under outliers, mixed corruption, pose uncertainty, and heterogeneous bias
- adaptive fixed-budget screening when only a subset of bearings can be fused or transmitted
- a validation chain spanning static Monte Carlo, pseudo-physical replay, and PyBullet multi-vehicle replay

Canonical current documents:

- `docs/review_reframe_2026-04-18.md`
- `docs/submission_execution_plan_2026-04-18.md`
- `submission/pre_submission_audit.md`
- `reproducibility/README.md`

Superseded planning drafts are archived under `docs/archive/` so that the root documentation stays focused on the current submission path.

## Reproducibility Commands

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

## Canonical Submission Assets

- `submission/mdpi_manuscript/manuscript_mdpi.tex`: main MDPI-format manuscript source
- `submission/mdpi_manuscript/manuscript_mdpi.pdf`: compiled MDPI manuscript proof
- `submission/pre_submission_audit.md`: current completion and remaining-item audit
- `submission/figures/`: submission-ready 300-DPI figure set in `PNG`, `PDF`, and `SVG`
- `submission/tables/`: LaTeX table sources used by the manuscript
- `submission/supplementary/`: highlights, frozen outputs, and data-availability notes

## Publication Workspace

- GitHub repository: `git@github.com:poboll/robust-bearing-fusion-uav-localization.git`
- Web URL: `https://github.com/poboll/robust-bearing-fusion-uav-localization`
- Current MDPI PDF: `submission/mdpi_manuscript/manuscript_mdpi.pdf`

## Rebuild the PDF

```bash
cd submission/mdpi_manuscript
latexmk -pdf -interaction=nonstopmode manuscript_mdpi.tex
```

## Cleanup Policy

- The MDPI manuscript under `submission/mdpi_manuscript/` is the only canonical paper source.
- LaTeX auxiliary files, Python cache files, and archived draft branches are intentionally excluded from the main working tree.
- Historical planning material is retained only in `docs/archive/` when it is still useful for traceability.
