Dear Editors of [Target Journal],

Please consider our manuscript entitled “Uncertainty-Aware Bearing-Only Passive Localization with Credibility-Guided Measurement Selection for Collaborative UAV Sensing” for publication in your journal.

This manuscript studies a practical passive-localization problem arising in collaborative UAV sensing under GNSS-denied or electromagnetically silent conditions. Classical geometric and least-squares methods are lightweight and interpretable, but they are highly vulnerable to biased, missing, and outlier-corrupted bearings. Recent literature increasingly emphasizes system-level cooperative inference and observability-aware planning, yet a lighter algorithmic need remains: during a single passive sensing cycle, not every bearing is equally trustworthy, and indiscriminate fusion can destabilize the estimate. To address that gap, the manuscript proposes an uncertainty-aware framework that combines a geometry-preserving robust estimator with a credibility-guided measurement-selection layer.

The work is supported by a reproducible synthetic benchmark including degraded-regime comparison, ablation analysis, formation generalization, sensitivity sweeps, sensor-count scaling, paired significance testing, and an observability-oriented interpretation analysis. The robust core markedly improves over least-squares estimation in outlier-rich and mixed regimes. In the fixed-budget selection benchmark, the proposed policy reduces the overall median error to 0.4977, compared with 0.7491 for random subset selection and 0.5200 for FIM/CRLB-greedy selection. Importantly, the manuscript states the scope of this result conservatively: measurement selection is most useful when part of the bearing set is unreliable, rather than being presented as a universal replacement for all-sensor fusion.

We believe the manuscript is a good fit for journals interested in sensing, localization, intelligent estimation, and uncertainty-aware algorithms because it addresses a real operational problem with a reproducible and carefully bounded solution. The contribution is not another metaphor-based optimizer. Instead, it lies in the integration of robust geometric reasoning, credibility-aware measurement triage, and a benchmark that clarifies when lightweight passive localization remains scientifically and practically useful.

The manuscript has not been submitted elsewhere, and all authors approve its submission. Real author affiliations, contribution statements, and corresponding-author contact details will be inserted consistently in the final portal submission package.

Sincerely,
Zengye Su, Yudan Nie, and Zilu Zhou
