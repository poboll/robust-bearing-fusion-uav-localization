# Reconstruction From Teacher Review

Date: 2026-04-18

This document is the executable reconstruction plan derived from the two external review files:

- `/Users/Apple/Downloads/针对《基于可信度引导测量选择的无源测向定位协同无人机感知》的深度学术审查与返修重构报告.md`
- `/Users/Apple/Downloads/deep-research-thinking-20260418-201100.md`

It converts their criticisms into concrete manuscript, experiment, and submission actions.

## 1. Bottom-Line Judgment

The external review is directionally correct, but not every criticism should be adopted literally.

### Fully valid criticisms

- the method section was too qualitative and needed explicit formulas;
- the selection score was under-defined in the paper even though code already existed;
- the manuscript needed a clearer boundary between robust estimation and measurement selection;
- the 20-seed statistics were too thin for a strong robustness claim;
- the submission strategy should not rely on an inflated Q1 promise.

### Valid but should be treated in a restrained way

- `simulation-only` is a real weakness, but it does not automatically make the paper unpublishable if the scope is clearly kept algorithmic;
- `modern baselines are missing` is true, but heavier system-level baselines such as factor graphs or trajectory planners are not one-to-one replacements for the current algorithmic question;
- `Sensors may reject pure simulation papers` is a useful warning, not a guaranteed verdict.

### Overstated or too harsh points

- calling the current package almost certainly desk-rejectable is stronger than the evidence supports;
- framing `Sensors` as a near-top-tier venue is inaccurate for 2026 positioning;
- treating every 2026 citation as suspicious is not justified as long as the cited paper is real and traceable.

## 2. Latest Literature Recheck

The current direction remains scientifically live.

Representative official-source papers/pages rechecked:

- `Trajectory Optimization to Enhance Observability for Bearing-Only Target Localization and Sensor Bias Calibration`, Biomimetics 2024:
  https://www.mdpi.com/2313-7673/9/9/510
- `Bearing-Only Passive Localization and Optimized Adjustment for UAV Formations Under Electromagnetic Silence`, Drones 2025:
  https://www.mdpi.com/2504-446X/9/11/767
- `Node Selection and Path Optimization for Passive Target Localization via UAVs`, Sensors 2025:
  https://www.mdpi.com/1424-8220/25/3/780
- `Formation-Constrained Cooperative Localization for UAV Swarms in GNSS-Denied Environments`, Sensors 2026:
  https://www.mdpi.com/1424-8220/26/6/1984
- `Scientific Reports` journal scope page:
  https://www.nature.com/srep/about
- `Sensors` scope page:
  https://www.mdpi.com/journal/sensors/about
- `Drones` scope and instructions:
  https://www.mdpi.com/journal/drones/about
  https://www.mdpi.com/journal/drones/instructions

Interpretation:

- the field has indeed moved toward trajectory optimization, node selection, observability enhancement, and stronger cooperative inference;
- our paper can still stand if positioned as a lighter uncertainty-aware algorithmic framework;
- the most natural first-submit journals remain `Sensors` and `Drones`, not `Scientific Reports`.

## 3. What Has Already Been Reconstructed

### 3.1 Story and journal route

- The paper is now explicitly positioned as an `algorithmic framework`.
- The central problem is now `uncertain passive measurements`, not `another optimizer`.
- The recommended journal order is now:
  1. `Sensors`
  2. `Drones`
  3. `Scientific Reports` as a stretch target

### 3.2 Method section

The manuscript has now been upgraded from qualitative prose to explicit definitions aligned with the implementation:

- residual definition under common bias;
- pairwise-ray geometric initialization;
- weighted Huber objective;
- trimming rule and reweighting rule;
- circular weighted mean for bias correction;
- weighted Fisher-style matrix for subset scoring;
- isotropy, diversity, and proposed combined subset score;
- algorithm summary list.

This is the single most important theoretical repair.

### 3.3 Statistical evidence

A higher-sample validation was added for the two most important regimes using 100 seeds:

- output file:
  `experiments/high_seed_validation.json`
- script:
  `run_high_seed_validation.py`

Key findings:

- outlier regime, Robust-BT vs LS:
  `83 wins / 17 losses`, `p = 1.31e-11`, median improvement `1.6921`
- mixed regime, Robust-BT vs LS:
  `75 wins / 25 losses`, `p = 5.64e-7`, median improvement `0.5511`
- against PSO:
  outlier advantage is only marginal, mixed regime remains unfavorable

This is valuable because it strengthens the claim against fragile classical estimators while preserving an honest boundary against heuristic global search.

### 3.4 Primary-source citation recheck

A late-pass primary-source audit was performed against official journal pages and DOI landing pages.

Important corrections made in this round:

- `Node Selection and Path Optimization for Passive Target Localization via UAVs` was confirmed as a real `Sensors 2025` paper, but it is a `Chan-TDOA + CRLB node-selection/path-optimization` study, not a bearing-only paper;
- the manuscript wording was tightened so this paper is used as a broader passive-localization and sensing-allocation reference rather than a same-problem baseline;
- multiple bibliographic fields were corrected against publisher pages, including author names for `xing2025node`, `li2025bearing`, `chen2025variable`, `yang2024distributed`, and `li2026formation`;
- the manuscript no longer relies on the weaker `arXiv/Open MIND` trajectory-optimization citation in its main positioning paragraphs when a peer-reviewed `Sensors 2025` path-planning paper can serve the same role more cleanly.

## 4. Remaining Gaps

These are real remaining weaknesses, not cosmetic ones.

### Gap A: no semi-real or hardware-grounded validation

Current status:

- still unresolved

Impact:

- the paper remains a simulation-validated algorithmic study, not a systems paper

### Gap B: missing stronger system-level baseline

Current status:

- still unresolved

Best next additions:

- factor graph optimization
- distributed cooperative localization

### Gap C: no platform-level sensing dynamics

Current status:

- still unresolved

Best next upgrade:

- ROS/Gazebo or replay-based validation with attitude perturbation and realistic sensing gaps

### Gap D: incomplete author metadata

Current status:

- still unresolved for the first and second authors

Impact:

- the package is scientifically coherent but not portal-ready until affiliation and corresponding e-mail fields are confirmed by the authors

## 5. Exact Section-Level Revision Guidance

### Title and abstract

Keep the current title direction.

Do not revert to:

- `observability-guided active robust...`
- `geometry-preserving robust...`

The current title is more publishable because it foregrounds the actual problem.

### Introduction

The first three paragraphs should continue to follow this logic:

1. passive sensing remains useful in GNSS-denied / low-emission missions;
2. not all bearings are equally trustworthy;
3. the paper solves uncertainty-aware measurement handling, not full-system active control.

### Related work

Split the literature into:

- passive bearing-only localization,
- observability / trajectory / node selection,
- heavier cooperative inference.

This prevents the paper from looking outdated.

### Methods

The paper should now explicitly claim:

- the score is implementation-grounded and reproducible,
- the proposed selector is a fixed-budget greedy triage policy,
- the method is transparent even though the current implementation uses finite-difference gradients.

### Results

The paper should continue to present three layers of evidence:

1. robustness against LS;
2. competitive rather than dominant relation to PSO;
3. conditional value of measurement selection.

### Discussion

Do not hide the mixed comparison against all-sensor fusion.

That mixed result is not just a weakness; it is part of the real story:

`selection helps when credibility varies, not as a universal law`.

## 6. Concrete Next-Step Execution Order

### Immediate

1. keep the new method formulas and high-seed validation in the manuscript;
2. finalize author affiliations and corresponding e-mail;
3. choose `Sensors` or `Drones` as first target;
4. do one final English polish pass.

### Stronger-version upgrade

1. add a semi-real or ROS/Gazebo validation layer;
2. add one stronger non-heuristic baseline;
3. if aiming higher, extend subset selection toward sequential planning.

## 7. Final Strategic Conclusion

The correct response to the teacher review is not to throw away the project, and not to oversell it either.

The correct response is:

- accept the critique on theory presentation and statistical evidence;
- partially accept the critique on modern baselines and simulation scope;
- reject exaggerated conclusions about immediate hopelessness;
- reposition the paper as a careful SCI-direction algorithmic study;
- strengthen it with formulas, higher-sample statistics, and a clearer journal route.

That reconstruction path is now already underway in the current workspace.
