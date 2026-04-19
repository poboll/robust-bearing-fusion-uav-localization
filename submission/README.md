# Submission Package

## Current Packaging Direction

- Canonical formatted manuscript: `mdpi_manuscript/`
- Recommended current story: robust front-end estimation for corrupted bearing fusion in passive multi-UAV localization
- Supporting submission assets: `figures/`, `tables/`, `graphical_abstract/`, and `supplementary/`

## Recommended Journal Order

This package is currently best aligned with sensing / UAV / localization journals rather than broad soft-computing journals.

1. `Sensors` or a closely matched MDPI special issue if the emphasis is uncertainty-aware sensing and reproducible algorithmic validation.
2. `Drones` if the UAV mission background is foregrounded more strongly than the generic sensing contribution.
3. `Scientific Reports` only as a stretch target after adding materially stronger validation or a broader systems angle.

## Package Contents

- `mdpi_manuscript/`: main MDPI-format manuscript package
- `graphical_abstract/`: graphical abstract assets
- `figures/`: 300-DPI figure files prepared for submission
- `tables/`: final table sources
- `cover_letter/`: editable cover-letter skeleton
- `supplementary/`: reproducibility, data availability, highlights, and frozen results
- `pre_submission_audit.md`: current package audit and remaining action items
- `next_stage_science_upgrade.md`: what to add if aiming for a materially stronger SCI story

## Current Status

This package is assembled from the latest validated project materials and is intended to serve as the final staging area before journal submission formatting and author metadata completion.

On April 18-19, 2026, the experiment suite available in this workspace had already been synchronized into the submission package, including regime comparison, ablation, formation generalization, sensitivity sweeps, scaling, significance summaries, observability interpretation, threshold sweeps, tracking-proxy analysis, and the measurement-selection benchmark. The resulting figures and frozen JSON outputs are archived under `submission/`.

The MDPI manuscript compiles successfully from the current sources. The remaining non-technical items are author metadata, final portal-specific wording, and any last advisor-level polish.
