# Submission Package

## Current Packaging Direction

- Canonical formatted manuscript: `mdpi_manuscript/`
- Recommended current story: robust one-shot bearing-only localization front-end for corrupted passive multi-UAV sensing
- Supporting submission assets: `figures/`, `tables/`, `graphical_abstract/`, and `supplementary/`

## Recommended Journal Order

This package is currently best aligned with sensing / UAV / localization journals rather than broad soft-computing journals.

1. `Sensors` or a closely matched MDPI special issue if the emphasis is robust corrupted-bearing fusion and reproducible algorithmic validation.
2. `Drones` if the UAV mission background is foregrounded more strongly and the replay-style validation is supplemented with a stronger flight-log, SITL, or hardware-facing layer.
3. `Scientific Reports` only as a stretch target after adding materially stronger validation or a broader systems angle.

## Package Contents

- `mdpi_manuscript/`: main MDPI-format manuscript package
- `graphical_abstract/`: graphical abstract assets
- `figures/`: 300-DPI figure files prepared for submission
- `tables/`: final table sources
- `cover_letter/`: editable cover-letter skeleton
- `supplementary/`: reproducibility, data availability, highlights, frozen results, and the data-only result bundle
- `pre_submission_audit.md`: current package audit and remaining action items
- `next_stage_science_upgrade.md`: what to add if aiming for a materially stronger SCI story

## Current Status

This package is assembled from the latest validated project materials and is intended to serve as the final staging area before journal submission formatting and author metadata completion.

As of April 25, 2026, the submission package contains the synchronized Monte Carlo benchmark, score ablations, formation generalization, sensitivity sweeps, scaling, significance/effect-size summaries, observability interpretation, threshold sweeps, RANSAC-family incremental ablation, tracking-proxy analysis, the fixed-budget screening benchmark, the measured-data multi-view replay surrogate, the deadline-aware replay layer, pseudo-physical replay, and the PyBullet replay study. The resulting figures and frozen JSON outputs are archived under `submission/`.

The English and Chinese MDPI manuscripts compile successfully from the current sources and build to 39-page and 32-page PDFs, respectively. The fixed archival software snapshot is available at `https://doi.org/10.5281/zenodo.19805203`, and the live project mirror is `https://github.com/poboll/robust-bearing-fusion-uav-localization`. Because the Zenodo DOI was minted from the GitHub release, it is a software/reproducibility archive rather than a dataset-only deposit. The curated data subset is kept in `supplementary/frozen_results/` and bundled as `supplementary/result_data_bundle.zip` for portals that request a data-style upload. The remaining non-technical items are author metadata, final portal-specific wording, and any last advisor-level polish.
