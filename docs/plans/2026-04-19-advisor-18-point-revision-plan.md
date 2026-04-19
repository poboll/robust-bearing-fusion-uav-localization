# Advisor 18-Point Revision Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Revise the manuscript, experiments, figures, references, and submission assets so the draft addresses the advisor's 18-point checklist with one canonical MDPI manuscript and a rebuilt PDF.

**Architecture:** The revision is executed in four layers: front-matter and compliance cleanup, method-and-experiment reinforcement, figure/table and system-story upgrade, and final packaging plus reproducibility updates. The canonical source remains `submission/mdpi_manuscript/manuscript_mdpi.tex`; all experiments regenerate JSON artifacts first, then figures/tables, then the final PDF.

**Tech Stack:** Python 3 in Conda `uu`, NumPy/SciPy/Matplotlib, LaTeX/latexmk, Git/GitHub CLI.

---

### Task 1: Clean front matter and compliance language

**Files:**
- Modify: `submission/mdpi_manuscript/manuscript_mdpi.tex`
- Modify: `submission/pre_submission_audit.md`
- Modify: `README.md`

**Steps:**
1. Replace the title with the bearing-only version and tighten the abstract to a five-sentence structure.
2. Rewrite contribution bullets so Stage 1 is the core contribution and Stage 2 is an optional engineering extension.
3. Remove reviewer-facing or self-defensive phrases from the manuscript body.
4. Replace the acknowledgments with a standard academic acknowledgment and add an AI-language-polishing disclosure.
5. Rewrite `\dataavailability{}` so it points to a concrete reproducibility package or review repository.

### Task 2: Repair references and scope anchors

**Files:**
- Modify: `submission/mdpi_manuscript/references_curated.bib`
- Modify: `submission/mdpi_manuscript/manuscript_mdpi.tex`

**Steps:**
1. Add canonical robust-estimation references for Huber, Tukey, RANSAC, LM, and GNC.
2. Add or strengthen recent 2023--2026 bearing-only / passive UAV references from Drones, IEEE, and related primary venues.
3. Rewire method paragraphs and related work so the new citations are used where claims are made.

### Task 3: Strengthen Stage 1 and Stage 2 explanation

**Files:**
- Modify: `submission/mdpi_manuscript/manuscript_mdpi.tex`
- Modify: `submission/tables/table_screening.tex`
- Create/Modify: new tables or figures as needed under `submission/tables/` and `submission/figures/`

**Steps:**
1. Add an algorithm box for the robust front-end pipeline and adaptive screening.
2. Remove unsupported “confidence estimate” language from the system placement description and figure.
3. Move screening sensitivity analysis into the main body.
4. Add a score-term ablation comparing geometry-only, geometry+residual, and full score.
5. Add a concrete budget story for 10 UAVs and 5--6 transmitted measurements.

### Task 4: Upgrade the synthetic benchmark and statistics

**Files:**
- Modify: `src/passive_localization/config.py`
- Modify: `src/passive_localization/scenario.py`
- Modify: `run_story_benchmark.py`
- Modify: `run_story_revision_analysis.py`
- Modify: related figure/table generators

**Steps:**
1. Replace the fixed target with randomized targets and multiple range layers.
2. Add near-degenerate geometry cases to the main benchmark.
3. Keep paired Wilcoxon testing and extend reporting to the revised benchmark outputs.
4. Recompute main tables and tail-risk figures from the new benchmark.

### Task 5: Upgrade downstream utility and replay realism

**Files:**
- Modify: `run_tracking_proxy.py`
- Modify: `src/passive_localization/pybullet_bridge.py`
- Modify: `submission/tables/table_pybullet_parameters.tex`
- Modify: `submission/tables/table_tracking_proxy.tex`
- Modify: `submission/mdpi_manuscript/manuscript_mdpi.tex`

**Steps:**
1. Add reacquisition success and search-ROI proxy metrics to the tracking analysis.
2. Make the PyBullet bearing-generation description explicit: delayed pose, attitude perturbation, visibility or validity logic, and timing noise.
3. Update the replay parameter table and manuscript discussion accordingly.

### Task 6: Improve figure quality and runtime reporting

**Files:**
- Modify: `plot_results.py`
- Modify: `run_runtime.py`
- Modify: `submission/mdpi_manuscript/manuscript_mdpi.tex`

**Steps:**
1. Switch figure colors to a colorblind-safe palette and enlarge labels/line widths.
2. Add empirical runtime-scaling reporting with hardware metadata.
3. Rebuild all manuscript figures in `experiments/` and `submission/figures/`.

### Task 7: Rebuild package and verify

**Files:**
- Modify: `reproducibility/README.md`
- Modify: `submission/README.md`
- Modify: `submission/supplementary/data_availability.md`
- Modify: `submission/mdpi_manuscript/manuscript_mdpi.tex`

**Steps:**
1. Prepare or refresh the public reproducibility package description.
2. Rebuild the manuscript with `latexmk`.
3. Check references, page count, and remaining warnings.
4. Commit with a `fix:` message and push.
