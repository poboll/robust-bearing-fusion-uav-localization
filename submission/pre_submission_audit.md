# Pre-Submission Audit

Audit date: April 18, 2026

## Completed

- Core experiments had already been synchronized from the current codebase into the submission package.
- The latest figure set was synchronized into `submission/figures/`, and all manuscript figures currently used in the paper are stored as 300-DPI PNG files.
- The JSON outputs used for tables were archived under `submission/supplementary/frozen_results/`.
- `submission/mdpi_manuscript/manuscript_mdpi.tex` was rebuilt around the robust corrupted-bearing front-end story and compiled successfully.
- The method section was upgraded from qualitative prose to explicit formulas for residuals, weighted Huber refinement, bias correction, and credibility-guided subset scoring.
- `submission/tables/tables_final.md` and `submission/tables/tables_final.tex` were updated with the current regime, scaling, significance, and measurement-selection numbers.
- The graphical abstract source was upgraded to the current story and exported in both `PDF` and `PNG`.
- The cover letter was rewritten as a reusable journal-agnostic skeleton so no venue or metadata is accidentally fabricated.
- A high-seed follow-up validation (`100` seeds for the outlier and mixed regimes) was added to strengthen the robustness claim against small-sample criticism.

## Scientifically Checked

- The paper is now explicitly positioned as an `algorithmic framework`, not as a new physical model or a complete swarm-control system.
- The manuscript does not claim universal superiority over PSO or over all-sensor fusion.
- The manuscript explicitly states that validation is simulation-based.
- The main story is robust corrupted-bearing fusion under passive multi-UAV localization, not runtime advantage.
- The measurement-selection layer is described as a conditional measurement-triage tool rather than a universal rule.
- The manuscript states its strongest gains honestly: outlier-rich and mixed regimes are the main evidence-bearing settings.
- The paper includes a modest observability-oriented interpretation layer rather than overstating theoretical novelty.
- The paper now contains a higher-sample follow-up check showing that the advantage over least squares remains stable beyond the original 20-seed summaries.

## Still Pending Before Portal Submission

- Insert real author affiliations and the real corresponding-author e-mail.
- Finalize the exact target journal and portal metadata using the synchronized title, abstract, keywords, and author information.
- Perform one final advisor-level language polish if desired.
- Confirm that the graphical abstract dimensions and portal wording match the chosen journal's current guide for authors at submission time.
- Finalize the CRediT contribution statement, data-availability wording, and code-release policy.

## If You Want To Push Beyond The Current Submission Level

- Add one stronger non-heuristic baseline such as factor-graph or distributed graph optimization.
- Add a hardware-in-the-loop, replay-based, or semi-real measurement validation layer.
- Extend the current one-shot selection layer toward sequential planning or richer uncertainty quantification.

## Journal Requirement Note

The current project now has a complete MDPI-format package with a single canonical manuscript source under `submission/mdpi_manuscript/`. Portal-specific requirements should be checked one more time immediately before submission because journal guides and upload fields can change.
