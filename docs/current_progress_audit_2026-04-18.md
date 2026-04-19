# Current Progress Audit

## Completed in This Iteration

### Literature and citation foundation

- Built a refreshed literature corpus with `79` real papers under:
  `.pipeline/literature/passive-localization-2026-sci/`
- Generated the readable master pool:
  `docs/literature_pool_master.md`
- Exported a usable BibTeX file:
  `submission/manuscript/references_curated.bib`
- Separated a strict `37`-paper `SCI/SCIE` core pool into:
  `docs/sci_verified_core_pool_2016_2026.md`
- Rechecked the manuscript backbone against official journal pages / DOI landing pages and corrected several cited metadata fields that were too loose in the earlier pool.

### Story and submission planning

- Wrote a literature-grounded innovation diagnosis:
  `docs/literature_gap_and_innovation_assessment.md`
- Reframed the story and MDPI submission route:
  `docs/story_reframing_mdpi.md`
- Produced updated abstract/storyline text:
  `docs/abstract_storyline_v2.md`
- Added an Oh-My-Paper-style strong-version execution document:
  `docs/ohmypaper_strong_version_pipeline.md`
- Added a concrete strong-version method design file:
  `docs/plans/2026-04-18-observability-robust-active-selection-design.md`

### Strong-version method upgrade

- Added an observability-guided active sensor-subset scheduling layer.
- Implemented the strong-version benchmark script:
  `run_active_selection.py`
- Expanded geometry utilities and scheduling logic to support weighted observability / FIM-style scoring.
- Re-ran the full experiment pipeline in `conda uu`.
- Added and synchronized a new `300 DPI` figure:
  `submission/figures/figure_active_selection.png`
- Added the active-selection result artifact:
  `experiments/active_selection_result.json`

### Formatting and figure quality

- Downloaded the official MDPI LaTeX package from the official MDPI page into:
  `submission/mdpi_official_template/`
- Upgraded figure export to `300 DPI`
- Re-rendered and synchronized the figure set into:
  `submission/figures/`

### MDPI manuscript conversion

- Created a new MDPI manuscript source:
  `submission/mdpi_manuscript/manuscript_mdpi.tex`
- Copied the official `Definitions/` folder into the MDPI manuscript workspace
- Successfully compiled:
  `submission/mdpi_manuscript/manuscript_mdpi.pdf`
- Updated the MDPI manuscript to the strong-version story and recompiled successfully.
- Updated the Elsevier-style backup manuscript and recompiled successfully:
  `submission/manuscript/manuscript_final.pdf`

## What Is Now Scientifically Strong

- The paper has a real passive-localization application story.
- The benchmark is no longer shallow; it already includes corruption regimes, ablation, scaling, observability interpretation, and significance testing.
- The literature base is now large enough to support a serious related-work section.
- The manuscript can now be discussed in a real MDPI journal format instead of an Elsevier placeholder.
- The project now also has a real decision-layer upgrade rather than only a static robust estimator.
- The active-selection benchmark shows the proposed policy is stronger than `Random`, stronger than `Angular-Spread`, and modestly stronger than `FIM/CRLB` greedy selection overall.

## What Is Still Missing Before a Strong Submission

### For a safe SCI submission

- replace placeholder author information
- polish the MDPI manuscript text section by section
- tighten citations inside the new MDPI draft
- align journal choice with the final story (`Sensors` or `Drones` are the current best fits)
- add one compact table and one short subsection in the manuscript body specifically summarizing the active-selection result in reviewer-friendly prose

### For a stronger Q1 attempt

- extend the current one-shot active subset-selection module toward sequential waypoint / trajectory planning
- add ablation for the new decision layer
- add semi-real or replay-style validation if available

## Honest Status Judgment

### If we stop here and polish

- `SCI-ready direction`: yes
- `mid-tier publishable story`: yes
- `hard Q1 certainty`: no

### After the reconstruction and source-verification pass

- `current story quality`: strong enough for a serious `Sensors` / `Drones` submission if kept honest
- `best current framing`: uncertainty-aware passive bearing-only localization with credibility-guided measurement selection
- `remaining gap to harder一区`: semi-real / hardware-grounded validation, plus at least one stronger modern baseline

## Immediate Next Recommended Action

The best next move is no longer inventing a more aggressive title or story. The best next move is to:

1. finish the manuscript with verified citations and complete author metadata for a clean `Sensors` / `Drones` submission; or
2. spend one more cycle adding semi-real validation and one stronger baseline before making a harder venue attempt.
