# Pre-Submission Audit

Audit date: April 25, 2026

## Current Status

- Canonical manuscript: `submission/mdpi_manuscript/manuscript_mdpi.tex`
- Current PDF build: `submission/mdpi_manuscript/manuscript_mdpi.pdf`
- Current paper title: `Robust One-Shot Bearing-Only Localization Front-End for Passive Multi-UAV Sensing`
- Current page count: English `39`; Chinese companion draft `33`
- Current archival DOI: `https://doi.org/10.5281/zenodo.19657582`
- Current repository snapshot: Zenodo software archive generated from GitHub release `v0.3.0`, plus frozen JSON outputs and plotting scripts inside the submission package

## Completed in the Current Revision Round

- The manuscript was rebuilt around the `corrupted bearing fusion front-end` story instead of an inflated full-UAV-autonomy claim.
- The abstract was compressed to MDPI-compatible length and aligned with the actual evidence boundary.
- A system-placement figure and a front-end flow figure were added to clarify where the method sits in the UAV sensing stack.
- The main Monte Carlo tables were synchronized to the latest 3000-case results, including stricter threshold analysis, paired Wilcoxon statistics, and upper-tail metrics.
- RANSAC, GNC-GM, Huber, least squares, and fixed-budget subset baselines were retained in the core comparison set.
- The screening section now includes score-term ablation, coefficient-perturbation evidence, and an explicit FIM-surrogate interpretation.
- The RANSAC discussion now includes a four-case reviewer-facing failure gallery and an explicit fairness note on internal consensus seeding versus the external RANSAC baseline.
- The ablation section now includes a `no_consensus_seed` component-removal result instead of only bias/trim/reweight toggles.
- A measured-data multi-view replay surrogate based on measured multi-view trajectory data was added between the synthetic and PyBullet validation layers.
- A deadline-aware measured-data replay layer was added on top of the public replay set, retaining 227 on-time windows after cycle-level arrival, staleness, and packet-loss filtering.
- Pseudo-physical replay, PyBullet replay, cue-quality partitioning, and tracking-proxy evidence were retained to make the application boundary explicit rather than implicit.
- Data availability wording now points to the Zenodo archival DOI, the live GitHub repository, the refreshed reproducibility ZIP, and the curated frozen-result data bundle.
- The MDPI manuscript compiles successfully after the latest text, replay-layer, and table synchronization pass.

## Scientifically Checked

- The paper no longer claims universal superiority over RANSAC, PSO, or all-sensor robust fusion.
- Stage 1 is treated as the main contribution; Stage 2 is treated as an optional budget-aware extension.
- The strongest evidence-bearing regimes are outlier, mixed corruption, pose uncertainty, heterogeneous bias, and harsh pseudo-physical replay.
- Public real-flight replay is interpreted as a measured-data replay layer, not as onboard deployment proof.
- Deadline-aware replay is interpreted as a system-facing arrival filter on measured-data windows, not as SITL or HITL proof.
- PyBullet replay is interpreted as a boundary or stress layer, not as deployment proof.
- The downstream tracker section is presented as a proxy utility test whose metrics remain partly mixed.
- The manuscript states clearly that observer poses are supplied by an upstream navigation module and are not solved jointly here.
- Physical-scale mapping is explicit: the normalized thresholds are interpreted through an example 100 m formation radius.
- Runtime reporting includes hardware, operating system, Python version, and stage-level timing decomposition.

## Remaining Risks Before Submission

- The paper is still a `simulation-plus-replay` study rather than a UAV platform validation paper. This remains the main risk for `Drones` or similarly application-heavy journals.
- The screening score is more defensible than before, but it is still an engineering surrogate rather than a learned or provably optimal selector.
- The bibliography is broad, but a final manual pass should still confirm that the most foregrounded citations are journal-grade and directly comparable.
- The repository and Zenodo record are public but not anonymous. If double-anonymous review is required by the eventual venue, a separate anonymous release workflow is still needed.
- The current Zenodo DOI is a software/reproducibility archive, not a dataset-only DOI. If the target journal requires a separate dataset DOI, create a new Zenodo dataset record from `submission/supplementary/result_data_bundle.zip`.

## Still Required Before Portal Submission

- Confirm the final target journal and re-check its current guide for authors on the submission date.
- Reconfirm author affiliations, email addresses, and metadata exactly as they should appear in the portal.
- Do one final manual proofreading pass on captions, reference formatting, and float placement in the compiled PDF.
- Decide whether the current public GitHub/Zenodo archive is acceptable for the chosen venue or whether an anonymized archive is needed.
- If the portal requests a data-only upload, use `submission/supplementary/result_data_bundle.zip`; if it requests a separate data DOI, upload that bundle as a new Zenodo Dataset record.
- Prepare a stronger venue-specific cover letter rather than reusing a generic skeleton.

## If the Goal Is to Push Beyond the Current Level

- Add SITL, HITL, flight-log replay, or laboratory-scale platform data.
- Add one stronger modern baseline such as a robust factor-graph or smoothing-based method.
- Extend the downstream utility study from a Kalman proxy to task-level reacquisition, search-region overlap, or handoff acceptance metrics.

## Journal Requirement Note

The current project has a single MDPI-format source of truth under `submission/mdpi_manuscript/`. Portal-specific checks should be repeated immediately before submission because author instructions, upload forms, and editorial screening requirements can change.
