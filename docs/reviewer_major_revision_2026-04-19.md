# Reviewer-Style Major Revision Report

Date: 2026-04-19

Target manuscript:
- `submission/mdpi_manuscript/manuscript_mdpi.tex`

Current judgment:
- `Not ready for a strong SCI/Q1 submission in its current form.`
- `Possible but risky for Drones if submitted now.`
- `Safer for a sensing/estimation-oriented venue after one more validation round.`

## 1. Bottom-line editorial judgment

From a reviewer's perspective, the manuscript is no longer a loose contest-style rewrite. It has a coherent problem framing, a reproducible code package, multiple experiment layers, and a more restrained claim than earlier drafts. However, the present version still looks like an `algorithm paper with upgraded simulation evidence`, not yet like a `platform-grounded UAV study`.

That distinction matters for `Drones`. The journal's official scope clearly accepts navigation, positioning, GNSS-outage, signal-processing, and sensor-fusion papers for unmanned platforms, but it also explicitly expects manuscripts to directly address unmanned platforms and, for theoretical/numerical work, recommends validation with experimental unmanned-platform data at least on a laboratory scale. The current paper does not yet satisfy that stronger expectation.

## 2. Critical findings

### C1. The validation chain still stops short of platform-grounded evidence

Severity:
- `Critical`

Why this is dangerous:
- The paper repeatedly frames itself as a UAV sensing contribution, yet the evidence remains synthetic Monte Carlo, pseudo-physical disturbance replay, and PyBullet-derived replay.
- This is stronger than pure static simulation, but it is still not equivalent to real flight logs, HIL, SITL with autopilot coupling, or laboratory-scale platform experiments.

Where it appears:
- `submission/mdpi_manuscript/manuscript_mdpi.tex:213`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:231`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:233`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:325`
- `src/passive_localization/pybullet_bridge.py:110`

Reviewer concern:
- The dynamic replay cases are generated from closed-loop quadrotor trajectories, but the localization itself is still evaluated on converted horizontal bearing cases rather than on a full onboard perception and control loop.
- A reviewer can therefore argue that the manuscript has not demonstrated robustness under realistic sensing latency, pose-estimation drift, synchronization errors, communication jitter, autopilot update timing, or actual sensor extraction noise.

Required revision:
- Add at least one stronger layer:
- `PX4 SITL/Gazebo` or equivalent autopilot-coupled loop.
- Real replay from flight logs, Vicon/UWB lab logs, or public multi-UAV datasets converted into bearing-only cases.
- Hardware-in-the-loop or small-scale laboratory validation on an unmanned platform.

Editorial consequence if not fixed:
- Likely `major revision` or `reject and encourage resubmission` for a UAV-application journal.

### C2. The method section still contains hand-tuned engineering heuristics that are not sufficiently justified

Severity:
- `Critical`

Why this is dangerous:
- The manuscript exposes a fixed composite selection score with hand-set coefficients, but does not present a principled calibration procedure, cross-validation protocol, or sensitivity analysis for those weights.
- This makes the selection layer look partly engineered around the current benchmark family.

Where it appears:
- `submission/mdpi_manuscript/manuscript_mdpi.tex:176`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:179`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:187`
- `src/passive_localization/schedule.py:102`
- `src/passive_localization/schedule.py:115`

Reviewer concern:
- A reviewer can fairly ask whether the observed gains come from a reusable credibility principle or from benchmark-specific coefficient tuning.
- The sentence "frozen engineering weights" is honest, but it also openly advertises a methodological weakness.

Required revision:
- Normalize each score term explicitly.
- Add weight-sensitivity analysis or cross-validated weight selection.
- Report whether the ordering of subset policies remains stable under perturbations of the weights.
- Move any tuned coefficient table to supplement and state how it was chosen.

### C3. The baseline family is still weaker than what strong reviewers will expect

Severity:
- `Critical`

Why this is dangerous:
- The paper mainly compares against least squares, Huber, PSO, SA, and geometry-only subset policies.
- This is enough to show robustness against fragile classical estimators, but not enough to defend the paper as a modern high-level contribution.

Where it appears:
- `submission/mdpi_manuscript/manuscript_mdpi.tex:221`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:252`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:325`
- `src/passive_localization/benchmarks.py:21`
- `src/passive_localization/replay.py:146`

Reviewer concern:
- PSO and SA look dated as headline competitors.
- A stronger reviewer will ask for at least one modern robust optimization baseline or one stronger cooperative-inference baseline on the same replay cases.
- The code already contains a `gnc_gm` baseline, but it is not integrated into the manuscript tables, discussion, or claims.

Required revision:
- Integrate `GNC + Geman-McClure` results into the main results tables and discussion.
- Add one modern system-level comparison if feasible:
- Robust factor-graph baseline.
- Sequential particle-filter / smoothing baseline.
- M-estimation or graduated-nonconvex robust geometric solver from the recent literature.

### C4. The manuscript claim is still stronger than the deployment evidence

Severity:
- `Critical`

Why this is dangerous:
- The manuscript often speaks in mission-level terms such as cueing, handoff, follow-up maneuvering, and action gating.
- Those are good storytelling devices, but they are not yet backed by a decision-loop experiment that measures downstream mission benefit.

Where it appears:
- `submission/mdpi_manuscript/manuscript_mdpi.tex:33`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:43`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:97`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:205`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:333`

Reviewer concern:
- The current experiments validate localization error reduction, not actual downstream cue acceptance, tracker recovery, handoff success, or mission utility.
- This creates a potential mismatch between narrative scope and measured evidence.

Required revision:
- Either reduce the operational language, or add a downstream task metric such as:
- cue acceptance rate,
- downstream search-region overlap,
- tracker reacquisition probability,
- false handoff rate,
- decision-trigger precision/recall.

## 3. Major findings

### M1. The algorithmic novelty is moderate, not yet obviously Q1-level by itself

Severity:
- `Major`

Where it appears:
- `submission/mdpi_manuscript/manuscript_mdpi.tex:131`
- `submission/mdpi_manuscript/manuscript_mdpi.tex:159`
- `src/passive_localization/robust.py:176`
- `src/passive_localization/robust.py:281`

Reviewer concern:
- Multi-candidate initialization + trimming + iterative reweighting + optional bias correction is a sensible integration, but each component is individually familiar.
- The novelty therefore depends on the `problem framing`, the `credibility-guided triage interpretation`, and the `validation design`, not on a fundamentally new estimator class.

What this means:
- For a stronger journal, the paper must win on `clarity + evidence + deployment relevance`, not on raw algorithmic novelty alone.

### M2. The implementation still looks prototype-like in places

Severity:
- `Major`

Where it appears:
- `src/passive_localization/robust.py:63`
- `src/passive_localization/robust.py:73`
- `src/passive_localization/robust.py:196`
- `src/passive_localization/config.py:25`
- `src/passive_localization/config.py:34`

Reviewer concern:
- Finite-difference gradients, fixed learning rates, and heuristic trim ratios are acceptable for a reproducible prototype, but they weaken the perception of mathematical and numerical maturity.
- A reviewer may ask whether improvements come from the robust principle or from favorable hyperparameter settings.

Required revision:
- Add hyperparameter robustness analysis.
- State default settings and rationale in a compact table.
- If possible, replace finite-difference updates with an explicit analytical or autodiff-based gradient for the core objective.

### M3. Statistical reporting is improved but still incomplete for a journal-grade results section

Severity:
- `Major`

Where it appears:
- `submission/tables/tables_final.tex:20`
- `submission/tables/tables_final.tex:38`
- `submission/tables/tables_final.tex:170`
- `submission/tables/tables_final.tex:188`

Reviewer concern:
- Some tables report only medians without confidence intervals.
- The paper uses sign tests, but not a consistent paired nonparametric test family across all main comparisons.
- Sample sizes vary across sections and are not always emphasized visually in the tables.

Required revision:
- Add bootstrap confidence intervals for all key medians.
- Add paired Wilcoxon signed-rank tests or explain why sign tests are preferred.
- Report effect sizes, not just p-values.

### M4. The literature base is broad, but not all entries are equally strong or equally safe to foreground

Severity:
- `Major`

Where it appears:
- `submission/mdpi_manuscript/references_curated.bib:93`
- `submission/mdpi_manuscript/references_curated.bib:147`
- `submission/mdpi_manuscript/references_curated.bib:303`
- `submission/mdpi_manuscript/references_curated.bib:321`
- `submission/mdpi_manuscript/references_curated.bib:330`
- `submission/mdpi_manuscript/references_curated.bib:339`
- `submission/mdpi_manuscript/references_curated.bib:402`

Reviewer concern:
- The bibliography contains a large number of `Unknown venue`, conference, repository, arXiv, and TechRxiv-style entries.
- These are useful for frontier scouting, but they weaken a Q1-oriented manuscript if they dominate the core argument.

Required revision:
- Keep frontier references for context, but anchor the main argument in peer-reviewed journal literature.
- Recheck whether each reference cited as state of the art is journal-grade and truly comparable.
- Remove unresolved or low-confidence entries from the main narrative if they are not essential.

## 4. Moderate findings

### N1. Some tables still look like internal benchmark summaries rather than polished journal tables

Severity:
- `Moderate`

Where it appears:
- `submission/tables/tables_final.tex:3`
- `submission/tables/tables_final.tex:20`
- `submission/tables/tables_final.tex:83`
- `submission/tables/tables_final.tex:188`

Reviewer concern:
- Table titles are functional but not yet publication-sharp.
- Several tables still mix different reporting philosophies.
- The most important takeaway is sometimes hidden in the paragraph below the table instead of built into the table itself.

Required revision:
- Rebuild the main tables around scientific questions rather than internal script outputs.
- Reduce the number of small summary tables and consolidate headline evidence into fewer stronger tables.

### N2. The figures are high-resolution but not yet visually competitive with polished journal graphics

Severity:
- `Moderate`

Evidence:
- Current PNG figures are exported at `300 DPI`, which satisfies the user's internal baseline.

Reviewer concern:
- Resolution alone is not enough.
- The current figure set is readable, but still resembles well-made benchmark outputs rather than intentionally designed journal graphics.
- The visual hierarchy, palette discipline, annotation style, and panel storytelling can still be improved.

Required revision:
- Redesign the main figures around one message per panel.
- Use a unified palette and stronger annotation of deltas and failure regions.
- If targeting `Drones`, rerender final upload assets at the journal's preferred figure standard.

### N3. Data-availability language is weaker than it should be

Severity:
- `Moderate`

Where it appears:
- `submission/mdpi_manuscript/manuscript_mdpi.tex:343`

Reviewer concern:
- "available upon reasonable request" is weaker than a public release for a reproducibility-centered algorithm paper.

Required revision:
- Prepare a public or frozen release package, or at minimum a supplement ZIP with scripts, environment file, and frozen outputs.

## 5. What is already working

These points should be preserved during revision:

- The paper now has a coherent narrow story: `credibility-guided front-end stabilization of unreliable bearings`.
- The manuscript no longer overclaims universal dominance.
- The pseudo-physical and PyBullet layers are valuable intermediate evidence.
- The 100-seed follow-up validation is a real strength.
- The paper explicitly acknowledges its own boundary against all-sensor robust fusion.

## 6. Practical recommendation on Drones

Current answer:
- `Can it be submitted to Drones now?` Technically yes.
- `Should it be submitted now if the goal is a strong SCI/Q1 outcome?` No.

Reason:
- The paper fits the official `Drones` scope.
- The paper does not yet fit the stronger reviewer expectation for a platform-grounded UAV study.
- In its current state, it is more naturally read as a `sensing/estimation manuscript with UAV motivation`.

Safer strategy:
- If no stronger validation can be added soon, prefer a sensing/signal-processing-oriented venue.
- If `Drones` remains the target, add one more validation layer before submission.

## 7. Immediate revision priority list

Priority 1:
- Add one stronger validation tier beyond replay-only simulation.

Priority 2:
- Integrate the modern `gnc_gm` baseline into the manuscript and add at least one more serious comparison family.

Priority 3:
- Replace or justify the hand-tuned selection score with normalization and sensitivity analysis.

Priority 4:
- Tighten the story so that every operational claim is matched by a measured quantity.

Priority 5:
- Rebuild the main tables and figures to look like publication figures rather than internal benchmark outputs.

## 8. Submission decision if forced today

If forced to decide today:
- `Drones`: risky major-revision candidate, not a confident acceptance candidate.
- `Sensors`: better fit than Drones in the current evidence state.
- `Harder Q1`: not recommended yet.
