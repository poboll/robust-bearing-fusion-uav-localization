# Submission Execution Plan

Date: 2026-04-18

## 1. Current Position

The project is now best positioned as:

`a simulation-validated algorithmic framework for uncertainty-aware passive bearing-only localization, with credibility-guided measurement selection for cases where not all bearings should be trusted equally`

This is the correct level of claim for the current evidence.

It is:

- stronger than a contest-style mathematical-modeling rewrite,
- more honest than claiming a full active-planning or swarm-control system,
- publishable if the scope is kept restrained,
- not yet a safe "hard Q1 breakthrough" story.

## 2. What Is Already Done

- MDPI main manuscript has been rebuilt and compiled.
- Backup manuscript has been synchronized to the same title, abstract, and conclusions.
- Tables, figure captions, highlights, data-availability statement, and cover letter have been updated to the same story.
- The project already contains the following experiment families:
  - degraded-regime comparison,
  - multi-seed outlier and mixed summaries,
  - ablation,
  - formation generalization,
  - sensitivity sweeps,
  - sensor-count scaling,
  - paired significance tests,
  - observability-oriented interpretation,
  - fixed-budget measurement-selection benchmark.
- Submission figures are stored as 300-DPI PNG files.

## 3. Core Scientific Story

The paper should be told in this order:

1. Passive bearing-only sensing remains useful in GNSS-denied or electromagnetically silent UAV missions.
2. The real practical problem is not just localization itself, but unreliable bearings.
3. Some bearings can be biased, missing, or badly corrupted, so fusing every observation may be harmful.
4. A lightweight and interpretable algorithmic framework is therefore valuable.
5. The robust core stabilizes localization under corrupted measurements.
6. The measurement-selection layer helps when credibility varies or sensing is budgeted.
7. The method is not a universal replacement for all-sensor fusion, graph optimization, or trajectory planning.

## 4. What Must Not Be Overclaimed

- Do not say the paper is a new physical model.
- Do not say the paper universally outperforms all-sensor estimation.
- Do not make runtime a headline selling point.
- Do not present the work as a full system-level active-sensing framework.
- Do not promise top-Q1 novelty without stronger validation.

## 5. Recommended Journal Route

Current best-fit order:

1. `Sensors`
   - Best match if the paper is framed as uncertainty-aware sensing and reproducible algorithmic validation.
2. `Drones`
   - Best match if the UAV mission context is made more prominent.
3. `Scientific Reports`
   - Only if a broader systems story or stronger validation is added.

Practical judgment:

- `Sensors` / `Drones`: realistic with the current evidence if written carefully.
- `Scientific Reports`: possible only after another strengthening round; not the safest first shot right now.

## 6. Remaining Required Actions Before First Submission

1. Fill in missing author affiliations and the real corresponding-author e-mail.
2. Finalize author contributions using CRediT taxonomy.
3. Decide whether the first submission emphasizes `sensing` or `UAV application`.
4. Recheck the target journal's latest portal requirements before upload.
5. Do one final human language polish pass.

Formatting reminder:

- the current package figures are already exported at 300 DPI;
- if the first target is `Drones`, rerender all figures and the graphical abstract at 600 DPI before the final portal upload because the current MDPI author instructions prefer figures at no less than 600 dpi.

## 7. Optional Upgrades Before a Stronger Submission

Highest-value upgrades:

- add replay-based, semi-real, or hardware-in-the-loop validation;
- add one stronger non-heuristic baseline such as factor graph optimization;
- extend one-shot measurement selection toward sequential planning;
- add richer uncertainty quantification.

Lower-value upgrades:

- adding another swarm-intelligence optimizer,
- adding more plots without changing the evidence level,
- making the title more aggressive than the experiments justify.

## 8. Immediate Working Order

From this point, the practical order should be:

1. freeze the manuscript story,
2. fill author metadata,
3. choose the first target journal,
4. adapt the cover letter and front matter to that journal only,
5. do a final submission-format pass,
6. upload.

## 9. Final Readiness Judgment

Current readiness:

- `scientific coherence`: yes
- `experimental completeness for a simulation paper`: yes
- `honest SCI submission readiness`: yes
- `safe high-end Q1 readiness`: no

The package is now good enough to move forward as a real SCI-direction submission package, provided we stay with the current restrained story.
