Dear Editors of Drones,

Please consider our manuscript entitled “Robust One-Shot Bearing-Only Localization Front-End for Passive Multi-UAV Sensing” for publication in your journal.

This manuscript studies a practical front-end localization problem in passive multi-UAV sensing. Classical geometric and least-squares fusion remains lightweight and interpretable, but it is highly vulnerable when a few bearings are missing, biased, or grossly corrupted. Recent literature increasingly emphasizes system-level cooperation, distributed inference, and geometry-aware planning, yet a narrower engineering gap remains at the current sensing cycle: once a fixed set of bearings has already been produced, indiscriminate fusion can destabilize the cue passed to downstream tracking or replanning modules. To address that gap, the manuscript proposes a robust one-shot bearing-fusion front end with consensus-style initialization, trimmed iteratively reweighted refinement, conditional common-bias correction, and an optional fixed-budget screening add-on.

The study is supported by a reproducible validation chain that combines expanded Monte Carlo experiments, fixed-budget screening analysis, measured-data multi-view replay, a deadline-aware replay layer with cycle-level arrival filtering, pseudo-physical replay, and PyBullet multi-vehicle replay. The main result is not a claim of universal superiority in median accuracy. Instead, the evidence shows that the proposed front end suppresses tail risk and catastrophic failures more consistently than least squares and remains comparable to strong robust baselines under mixed corruption, heterogeneous bias, pose uncertainty, disturbed replay, and on-time bearing loss.

We believe the manuscript fits journals interested in sensing, localization, and robust estimation because it addresses a concrete operational bottleneck with a bounded and reproducible solution. The contribution is the integration of a robust corrupted-bearing front end and a validation chain that clarifies where the method helps, where it does not, and how it should be used in a passive sensing stack.

The manuscript has not been submitted elsewhere, and all authors approve its submission. The corresponding author is Zengye Su, School of Information Technology and Engineering, Guangzhou College of Commerce, Guangzhou 511363, China.

Sincerely,
Zengye Su, Yudan Nie, and Zilu Zhou
