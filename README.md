# Robust Bearing Fusion for Multi-UAV Passive Localization

This repository contains the canonical working tree for an SCI-oriented manuscript on corrupted bearing-only fusion in passive multi-UAV localization. The paper is written as a robust front-end paper, not as a full autonomy-stack paper: Stage 1 is the main contribution, and Stage 2 is an optional budget-aware screening extension.

## Manuscript Position

The current story is intentionally narrow and evidence-aligned:

- Stage 1: consensus-assisted robust front-end estimation under outliers, mixed corruption, pose uncertainty, and heterogeneous bias
- Stage 2: adaptive fixed-budget screening when uplink, compute, or latency limits prevent fusing every bearing
- validation chain: 3000-case Monte Carlo benchmark, 720-case pseudo-physical replay, 1103-case PyBullet multi-vehicle stress test, downstream tracking proxy, and runtime/scaling analysis

The strongest claims are in the synthetic and pseudo-physical layers. The PyBullet layer is kept as a transfer-gap stress test, where the method is broadly competitive in median replay accuracy and mainly improves tail-oriented tracking metrics rather than universally dominating every baseline.

## Canonical Assets

- `submission/mdpi_manuscript/manuscript_mdpi.tex`: canonical MDPI manuscript source
- `submission/mdpi_manuscript/manuscript_mdpi.pdf`: latest compiled manuscript proof
- `submission/mdpi_manuscript/references_curated.bib`: curated bibliography used by the paper
- `submission/figures/`: submission-ready figures in `PNG`, `PDF`, and `SVG`
- `submission/tables/`: LaTeX tables pulled into the manuscript
- `experiments/`: frozen JSON outputs and regenerated figures used by the manuscript
- `src/`: reusable localization, screening, scenario, and replay code
- `docs/`: planning, review, and restructuring notes retained for traceability

## Core Reproducibility Commands

All Python commands are intended to run in the local Conda `uu` environment.

```bash
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_story_benchmark.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_story_revision_analysis.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_active_selection.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_screening_score_ablation.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_screening_weight_sensitivity.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_selection_benefit_map.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_pseudo_physical_validation.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_pybullet_replay_validation.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_tracking_proxy.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python run_runtime.py'
conda run -n uu bash -lc 'cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization && PYTHONPATH=src python plot_results.py'
```

## Build the PDF

```bash
cd /Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization/submission/mdpi_manuscript
latexmk -pdf -interaction=nonstopmode manuscript_mdpi.tex
```

## Repository Layout

- `docs/`: review reports, restructuring plans, and archived decision trails
- `reproducibility/`: notes about reruns and packaging
- `experiments/`: machine-generated outputs only
- `submission/`: paper-facing assets only
- `external/`: simulator dependencies or external code snapshots

## Publication Workspace

- Git remote: `git@github.com:poboll/robust-bearing-fusion-uav-localization.git`
- Web URL: `https://github.com/poboll/robust-bearing-fusion-uav-localization`

## Cleanup Policy

- `submission/mdpi_manuscript/` is the only canonical paper source.
- Old stitched table drafts and transient cache files should not be treated as canonical evidence.
- Historical planning material may remain under `docs/` only when it is still useful for auditability.
