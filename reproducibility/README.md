# Reproducibility Package

This directory prepares the manuscript assets for an anonymized public release.

## Environment

- Recommended interpreter: `/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python`
- Main code root: `/Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization`
- PyBullet replay requires `pybullet` and `gym-pybullet-drones` to be installed in the same environment.

## Regenerate Core Results

```bash
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_story_benchmark.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_active_selection.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_pseudo_physical_validation.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_pybullet_replay_validation.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_story_revision_analysis.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_screening_weight_sensitivity.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_ransac_incremental_ablation.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_public_dataset3_replay_validation.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_deadline_replay_validation.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python run_tracking_proxy.py
/opt/homebrew/Caskroom/miniconda/base/envs/uu/bin/python plot_results.py
```

## Manuscript Build

```bash
cd submission/mdpi_manuscript
latexmk -pdf -interaction=nonstopmode manuscript_mdpi.tex
```

## Public-Release Contents

- `src/`: algorithm implementation
- `run_*.py`: experiment entry points
- `experiments/*.json`: frozen results used in the manuscript
- `submission/figures/`: publication figures in `PNG`, `PDF`, and `SVG`
- `submission/tables/`: LaTeX tables used by the MDPI manuscript
- `submission/mdpi_manuscript/manuscript_mdpi.tex`: camera-ready source

## Release Notes

Before uploading to GitHub, OSF, or Zenodo, remove private working notes from `docs/` if they are not intended for review.
