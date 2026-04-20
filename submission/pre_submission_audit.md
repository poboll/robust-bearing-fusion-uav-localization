# Pre-Submission Audit

Audit date: April 19, 2026

## Current Status

- Canonical manuscript: `submission/mdpi_manuscript/manuscript_mdpi.tex`
- Current PDF build: `submission/mdpi_manuscript/manuscript_mdpi.pdf`
- Current paper title: `Corruption-Aware Bearing-Only Localization for Passive Multi-UAV Sensing`
- Current page count: `36`
- Current repository snapshot: public GitHub mirror plus frozen JSON outputs and plotting scripts inside the submission package

## Completed in the Current Revision Round

- The manuscript was rebuilt around the `corrupted bearing fusion front-end` story instead of an inflated full-UAV-autonomy claim.
- The abstract was compressed to MDPI-compatible length and aligned with the actual evidence boundary.
- A system-placement figure and a front-end flow figure were added to clarify where the method sits in the UAV sensing stack.
- The main Monte Carlo tables were synchronized to the latest 3000-case results, including stricter threshold analysis, paired Wilcoxon statistics, and upper-tail metrics.
- RANSAC, GNC-GM, Huber, least squares, and fixed-budget subset baselines were retained in the core comparison set.
- The screening section now includes score-term ablation, coefficient-perturbation evidence, and an explicit FIM-surrogate interpretation.
- The RANSAC discussion now includes a four-case reviewer-facing failure gallery and an explicit fairness note on internal consensus seeding versus the external RANSAC baseline.
- The ablation section now includes a `no_consensus_seed` component-removal result instead of only bias/trim/reweight toggles.
- A public real-flight replay layer based on measured multi-view trajectory data was added between the synthetic and PyBullet validation layers.
- Pseudo-physical replay, PyBullet replay, cue-quality partitioning, and tracking-proxy evidence were retained to make the application boundary explicit rather than implicit.
- Data availability wording now points directly to the repository containing code, figure scripts, MDPI sources, and frozen outputs.
- The MDPI manuscript compiles successfully after the latest text and table synchronization pass.

## Scientifically Checked

- The paper no longer claims universal superiority over RANSAC, PSO, or all-sensor robust fusion.
- Stage 1 is treated as the main contribution; Stage 2 is treated as an optional budget-aware extension.
- The strongest evidence-bearing regimes are outlier, mixed corruption, pose uncertainty, heterogeneous bias, and harsh pseudo-physical replay.
- Public real-flight replay is interpreted as a measured-data replay layer, not as onboard deployment proof.
- PyBullet replay is interpreted as a boundary or stress layer, not as deployment proof.
- The downstream tracker section is presented as a proxy utility test whose metrics remain partly mixed.
- The manuscript states clearly that observer poses are supplied by an upstream navigation module and are not solved jointly here.
- Physical-scale mapping is explicit: the normalized thresholds are interpreted through an example 100 m formation radius.
- Runtime reporting includes hardware, operating system, Python version, and stage-level timing decomposition.

## Remaining Risks Before Submission

- The paper is still a `simulation-plus-replay` study rather than a UAV platform validation paper. This remains the main risk for `Drones` or similarly application-heavy journals.
- The screening score is more defensible than before, but it is still an engineering surrogate rather than a learned or provably optimal selector.
- The bibliography is broad, but a final manual pass should still confirm that the most foregrounded citations are journal-grade and directly comparable.
- The repository is public but not anonymous. If double-anonymous review is required by the eventual venue, a separate anonymous release workflow is still needed.

## Still Required Before Portal Submission

- Confirm the final target journal and re-check its current guide for authors on the submission date.
- Reconfirm author affiliations, email addresses, and metadata exactly as they should appear in the portal.
- Do one final manual proofreading pass on captions, reference formatting, and float placement in the compiled PDF.
- Decide whether the current public GitHub repository is acceptable for the chosen venue or whether an anonymized archive is needed.
- Prepare a stronger venue-specific cover letter rather than reusing a generic skeleton.

## If the Goal Is to Push Beyond the Current Level

- Add SITL, HITL, flight-log replay, or laboratory-scale platform data.
- Add one stronger modern baseline such as a robust factor-graph or smoothing-based method.
- Extend the downstream utility study from a Kalman proxy to task-level reacquisition, search-region overlap, or handoff acceptance metrics.

## Journal Requirement Note

The current project has a single MDPI-format source of truth under `submission/mdpi_manuscript/`. Portal-specific checks should be repeated immediately before submission because author instructions, upload forms, and editorial screening requirements can change.
