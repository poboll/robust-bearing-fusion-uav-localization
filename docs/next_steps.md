# Next Steps

Date: 2026-04-19

Current manuscript state:
- Main TeX: `submission/mdpi_manuscript/manuscript_mdpi.tex`
- Main PDF: `submission/mdpi_manuscript/manuscript_mdpi.pdf`
- Compile status: `passes`
- Current length: `30 pages`
- Current citation base: `41 unique references`

## What was completed in the latest revision

1. The manuscript story was kept centered on `corrupted bearing-only localization`, not on a full UAV autonomy stack.
2. Two stronger journal-style figures were added:
   - `submission/figures/figure_story_cdf.png`
   - `submission/figures/figure_screening_cases.png`
3. The results section now explains:
   - full-distribution tail suppression in outlier and mixed regimes;
   - one case where the proposed fixed-budget policy beats simpler subset heuristics;
   - one case where adaptive gating correctly avoids harmful pruning.
4. The abstract was tightened to reduce overemphasis on delay as a headline corruption type.
5. The paper still compiles cleanly to `32 pages` after all figure and text updates.

## Highest-value next actions before journal submission

1. Add one stronger validation layer beyond replay-only evidence.
   - Best options: public flight-log replay, PX4 SITL with estimator coupling, or small-scale lab logs converted to bearing-only cases.
   - This is the single biggest gap for a UAV-facing SCI submission.

2. Strengthen the selection-module methodology.
   - Add normalized score terms and weight-sensitivity analysis.
   - Preferably report whether policy ranking remains stable under coefficient perturbation.

3. Surface stronger baselines more prominently.
   - Integrate `GNC-GM` into all main narrative comparisons.
   - If feasible, add one more modern robust geometric or graph-based baseline.

4. Add one downstream utility metric.
   - Candidates: cue acceptance rate, tracker handoff success, search-region overlap, or false-cue rejection.
   - This would make the UAV-facing story much more defensible.

5. Polish the case-study figure for final submission.
   - Consider converting the current 2x2 layout into subfigures or cropping whitespace.
   - Keep the top panel as “better than simple subset heuristics” and the bottom panel as “adaptive gate keeps full-set fusion”.

## What was added in the current iteration

1. The manuscript now includes an explicit `deployment scenario -> corruption source` mapping table in the main text.
   - This makes the story less abstract and ties the estimator to concrete passive-sensing use cases.

2. The main tables were moved back toward their corresponding results subsections.
   - The previous “single input block” layout that encouraged table clustering was removed.
   - Main figures were also relaxed from rigid `[H]` placement to `[!htbp]` to improve page flow.

3. A new `screening-weight sensitivity` experiment was added.
   - Script: `run_screening_weight_sensitivity.py`
   - Output: `experiments/screening_weight_sensitivity.json`
   - Figure: `submission/figures/figure_screening_weight_sensitivity.png`
   - The experiment perturbs the four screening coefficients on a stratified 432-window slice and shows that the selected subsets remain largely stable even when the score weights are disturbed.

4. The manuscript now reports this new methodological hardening result explicitly.
   - Mild/moderate/strong perturbations increase the sampled screening median only modestly.
   - Jaccard overlap with the default selected subset remains high, which helps answer the “hand-tuned score” criticism more directly.

## Submission judgment at the current stage

- For `Drones`, the manuscript is now much better framed and less overclaimed than before, but it still reads as `a strong algorithmic paper with upgraded simulation evidence`.
- For a `stronger UAV-systems claim`, one more validation round is still needed.
- For a sensing/estimation-oriented SCI venue, the current version is closer, but another round on validation and methodological hardening is still recommended.
