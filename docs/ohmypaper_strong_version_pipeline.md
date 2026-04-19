# Oh My Paper Strong-Version Pipeline

## 1. What This Document Means

This project is now being advanced with the same stage logic emphasized by `Oh My Paper`:

`Survey -> Ideation -> Experiment -> Publication -> Promotion`

Important practical note:

- The `Oh My Paper` repository is a Claude Code plugin workflow, not a native Codex CLI skill in the current session.
- So in this project we are following the **same pipeline standard manually inside the repo**, rather than pretending the slash commands are directly available here.

## 2. Stage Audit

## Stage A. Survey

### Done

- Built a traceable `79`-paper literature bank.
- Exported a curated BibTeX file.
- Re-screened the pool and separated a `37`-paper `SCI/SCIE` core pool.
- Wrote the literature-gap and innovation assessment.
- Re-checked disputed venue status, especially `Sensors`, `Drones`, `Biomimetics`, and `Computers`.

### Not Done

- We still do not have sentence-level notes for every core paper.
- The strongest `10-15` references for the final introduction / related-work section are not yet converted into one-paper-one-note cards.

### Next Tasks

1. Build one-page structured notes for the top `15` core papers.
2. Extract the most reusable experimental patterns from the active-sensing and cooperative-localization papers.
3. Freeze the final citation backbone for the first manuscript version.

### Acceptance Standard

- The introduction and related-work section can be written without returning to broad web search.
- Every major claim in the paper can point to at least one core-paper citation.

## Stage B. Ideation

### Done

- Rejected the old contest-style story and the outdated optimizer-comparison story.
- Confirmed that the safe story is `interpretable robust passive localization`.
- Confirmed that the strong story is `observability-guided active robust bearing-only localization`.
- Diagnosed that plain `trim + reweight + bias correction` is publishable but not a convincing hard-`Q1` novelty by itself.

### Not Done

- The method story has not yet been fully rewritten section by section into the MDPI manuscript.
- The exact naming of the proposed strong-version method is still flexible.

### Next Tasks

1. Freeze the strong-version name and acronym.
2. Rewrite the abstract, introduction, and contributions around the active-scheduling layer.
3. Tighten the realism story:
   `GNSS-denied`, `emission-constrained`, `corrupted bearings`, `adaptive scheduling`.

### Acceptance Standard

- The story answers four questions cleanly:
  - Why this problem matters now.
  - Why the existing static estimator story is not enough.
  - What the new decision layer adds.
  - Why the work is still reproducible and not over-claimed.

## Stage C. Experiment

### Done

- Existing benchmark line is complete for the robust core:
  - regime comparison
  - ablation
  - formation generalization
  - sensitivity sweeps
  - scaling
  - observability analysis
  - significance testing
  - runtime
- Added the strong-version module:
  `observability-guided active sensor subset scheduling`
- Added new strong-version experiment:
  `run_active_selection.py`
- Re-ran the full experiment pipeline in `conda uu`.
- Generated new `300 DPI` figure:
  `submission/figures/figure_active_selection.png`

### Current Strong-Version Result Signal

- Against `Random` and `Spread` subset baselines, the proposed policy is clearly better.
- Against `FIM/CRLB` greedy selection, the proposed policy is modestly but consistently stronger overall.
- On the aggregated active-selection benchmark:
  - proposed median error: `0.4977`
  - `FIM/CRLB` median error: `0.5200`
  - all-sensor robust median error: `0.5510`
- The proposed policy is especially useful as the paper's bridge from `robust estimation` to `active decision-making`.

### Not Done

- No real-world dataset or hardware experiment yet.
- No multi-step trajectory planning yet; current strong version is active **subset scheduling**, not full path planning.
- No reviewer-facing table has yet been written for the new active experiment.

### Next Tasks

1. Write a compact active-selection results table for the manuscript.
2. Add one ablation on the proposed policy:
   `reliability term removed` vs `FIM-only` vs `full score`.
3. Decide whether to stop at subset scheduling or continue to a waypoint-planning extension.

### Acceptance Standard

- The strong-version section contains at least:
  - one method figure
  - one active experiment figure
  - one summary table
  - one honest paragraph on limits

## Stage D. Publication

### Done

- Official MDPI template downloaded from the official MDPI LaTeX page.
- New MDPI manuscript workspace created and compiled successfully.
- Figures upgraded to `300 DPI`.
- Core story documents already exist:
  - story reframing
  - abstract storyline
  - innovation assessment
  - submission strategy

### Not Done

- The MDPI manuscript has not yet been rewritten to fully absorb the new active-selection strong version.
- The paper still needs final author info, acknowledgments, and a submission-specific cover letter.
- Related work needs to explicitly separate core SCI evidence from supplement references.

### Next Tasks

1. Update manuscript title, abstract, contributions, and method section for the strong version.
2. Add the new active-selection figure and results paragraph to the MDPI draft.
3. Rewrite related work using `docs/sci_verified_core_pool_2016_2026.md` as the only backbone.
4. Prepare two journal variants:
   - safe version: `Sensors` / `Drones`
   - stronger version: `IEEE Sensors Journal` or similar

### Acceptance Standard

- The manuscript compiles cleanly.
- Every major result in the PDF corresponds to an existing artifact in `submission/`.
- The submission package can survive reviewer questions about novelty, work volume, and reproducibility.

## Stage E. Promotion

### Current Status

- Not started.

### Deferred Deliverables

- graphical abstract refinement
- journal-specific highlights
- slide deck / defense deck
- project one-page summary

## 3. Strong-Version Positioning Decision

The current best publication framing is:

`observability-guided active robust bearing-only localization for collaborative UAV systems under degraded measurements`

Why this framing is currently the best:

- It keeps the already working robust estimator instead of discarding existing progress.
- It aligns with the 2024-2026 literature shift toward observability, scheduling, and active sensing.
- It makes the work more computer-oriented than a plain triangulation or optimizer-comparison paper.

## 4. What Still Blocks a Harder Q1 Push

Three things are still missing if we want a more aggressive `Q1/一区` attempt:

1. A stronger decision layer than one-shot subset scheduling.
2. A more systems-style experiment story, ideally with sequential planning or online adaptation.
3. A cleaner reviewer-facing narrative that shows why this is not just a contest-paper cleanup.

## 5. Immediate Execution Order

1. Freeze the `SCI/SCIE` citation backbone.
2. Rewrite the abstract and introduction for the active strong version.
3. Add the new active experiment into the MDPI manuscript.
4. Produce one new table for the active-selection benchmark.
5. Decide whether to submit the strong subset-scheduling version now or continue to trajectory planning.

## 6. Honest Final Status

- `SCI-ready`: yes
- `High-quality strong-version prototype`: yes
- `Hard-Q1 guaranteed`: no
- `Much stronger than the old static-estimator-only version`: yes
