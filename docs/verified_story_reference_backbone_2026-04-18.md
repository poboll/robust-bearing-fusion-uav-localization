# Verified Story and Reference Backbone

Date: 2026-04-18

## 1. What the Paper Is

The current manuscript should be positioned as:

`an algorithm paper on robust inference and credibility-guided measurement management for standard bearing-only passive localization`

It is **not** a new physical sensing model, and it should **not** be sold as a full active-planning autonomy stack.

## 2. Innovation Judgment

### What is genuinely new enough

- A robust passive-localization core targeted at mixed uncertainty rather than only clean geometry.
- A credibility-guided subset-selection layer that combines geometry and residual-derived reliability.
- An honest boundary analysis showing that subset selection is conditional, not universally better than all-sensor fusion.
- A reproducible evaluation matrix that is stronger than a typical contest-style mathematical-modeling rewrite.

### What is not strong enough to claim

- A field-validated or hardware-proven system.
- A universal state-of-the-art result against every modern cooperative-localization pipeline.
- A fundamentally new bearing-only measurement model.

## 3. Evidence Pool Structure

- Full current literature pool: [docs/literature_pool_master.md](/Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization/docs/literature_pool_master.md)
- Strict SCI/SCIE core pool: [docs/sci_verified_core_pool_2016_2026.md](/Users/Apple/Developer/Pycharm/q/research/robust-bearing-fusion-uav-localization/docs/sci_verified_core_pool_2016_2026.md)
- Current manuscript backbone: `40` recent, real, DOI-backed references already cited in the MDPI draft

## 4. Story Mapping

- Problem background:
  GNSS-denied collaborative UAV sensing still needs trustworthy localization.
- Field trend:
  recent work is moving toward factor-graph fusion, distributed cooperation, observability-aware planning, and passive target localization.
- Gap:
  most papers improve geometry, motion, or system integration, but fewer papers manage heterogeneous bearing credibility inside a fixed sensing cycle.
- Our position:
  keep the standard bearing-only model, strengthen the inference layer, and explicitly decide when some bearings should not dominate fusion.

## 5. Current Submission Judgment

- `Drones`:
  realistic first target if the manuscript stays honest and the revision quality remains high.
- Harder Q1 route:
  still risky without replay-based, hardware-in-the-loop, or field validation.
- Scientific value today:
  acceptable as an algorithm-focused UAV sensing paper.

## 6. Core Verified Reference Backbone

| Key | Year | Venue | Title | DOI |
|---|---:|---|---|---|
| `avola2024uav` | 2024 | IEEE Access | UAV Geo-Localization for Navigation: A Survey | 10.1109/access.2024.3455096 |
| `liu2025survey` | 2025 | Complex & Intelligent Systems | A survey of sensors based autonomous unmanned aerial vehicle (UAV) localization techniques | 10.1007/s40747-025-01961-2 |
| `kramaric2025comprehensive` | 2025 | Drones | A Comprehensive Survey on Short-Distance Localization of UAVs | 10.3390/drones9030188 |
| `dai2022uav` | 2022 | Sensors | UAV Localization Algorithm Based on Factor Graph Optimization in Complex Scenes | 10.3390/s22155862 |
| `yang2020tightly` | 2020 | Aerospace Science and Technology | Tightly coupled integrated navigation system via factor graph for UAV indoor localization | 10.1016/j.ast.2020.106370 |
| `yang2024distributed` | 2024 | Measurement Science and Technology | A distributed factor graph model solving method for cooperative localization of UAV swarms | 10.1088/1361-6501/ad91d6 |
| `qian2025cooperative` | 2025 | IEEE Transactions on Instrumentation and Measurement | A Cooperative Localization Algorithm Based on Theory of Surveying Adjustment With Range Network for UAV Clusters | 10.1109/tim.2025.3587358 |
| `li2025tcdrl` | 2025 | IEEE Transactions on Vehicular Technology | TCDRL: Two-Stage Cooperative Dimensionality-Reduced Localization Framework for UAVs in GNSS-Poor Environments | 10.1109/tvt.2025.3649547 |
| `li2026formation` | 2026 | Sensors | Formation-Constrained Cooperative Localization for UAV Swarms in GNSS-Denied Environments | 10.3390/s26061984 |
| `liu2026high` | 2026 | Sensors | A High-Precision Cooperative Localization Method for UAVs Based on Multi-Condition Constraints | 10.3390/s26051641 |
| `ding2026set` | 2026 | IEEE Transactions on Signal and Information Processing over Networks | Set-Membership Estimation Based Distributed Cooperative Localization of Multiple UAVs | 10.1109/tsipn.2026.3663852 |
| `zhang2026multi` | 2026 | IEEE Internet of Things Journal | Multi-UAV-Assisted Cooperative Localization of Underground Sensor Nodes Using Multiobjective Reinforcement Learning | 10.1109/jiot.2026.3655176 |
| `jia2024composite` | 2024 | IEEE Transactions on Automation Science and Engineering | Composite Disturbance Filtering for Onboard UWB-Based Relative Localization of Tiny UAVs in Unknown Confined Spaces | 10.1109/tase.2024.3412068 |
| `bach2025range` | 2025 | IEEE Transactions on Industrial Electronics | Range and Bearing Estimations Using Trilateration Ultrawideband Tag for Range-Only Simultaneous Localization and Mapping | 10.1109/tie.2025.3589465 |
| `lai2025collaborative` | 2025 | Electronics Letters | Collaborative Beamforming for Multi‐Target Localization Using Passive Anchors | 10.1049/ell2.70510 |
| `gao2023scalable` | 2023 | Sensors | A Scalable Distributed Control Algorithm for Bearing-Only Passive UAV Formation Maintenance | 10.3390/s23083849 |
| `kang2024aoa` | 2024 | Drones | A New Method of UAV Swarm Formation Flight Based on AOA Azimuth-Only Passive Positioning | 10.3390/drones8060243 |
| `huang2025emcompat` | 2025 | Drones | Passive Positioning and Adjustment Strategy for UAV Swarm Considering Formation Electromagnetic Compatibility | 10.3390/drones9060426 |
| `li2025bearing` | 2025 | Drones | Bearing-Only Passive Localization and Optimized Adjustment for UAV Formations Under Electromagnetic Silence | 10.3390/drones9110767 |
| `xing2025node` | 2025 | Sensors | Node Selection and Path Optimization for Passive Target Localization via UAVs | 10.3390/s25030780 |
| `peng2024trajectory` | 2024 | Biomimetics | Trajectory Optimization to Enhance Observability for Bearing-Only Target Localization and Sensor Bias Calibration | 10.3390/biomimetics9090510 |
| `zou2024revisit` | 2024 | IEEE Sensors Journal | A Revisit to D-Criterion-Based Sensor Trajectory Planning in Bearing-Only Target Motion Analysis | 10.1109/jsen.2024.3510378 |
| `chen2025variable` | 2025 | Sensors | Variable-Speed UAV Path Optimization Based on the CRLB Criterion for Passive Target Localization | 10.3390/s25175297 |
| `wang2025bio` | 2025 | Biomimetics | Bio-Inspired Observability Enhancement Method for UAV Target Localization and Sensor Bias Estimation with Bearing-Only Measurement | 10.3390/biomimetics10050336 |
| `dogancay2024bayesian` | 2024 | Sensors | UAV Path Optimization for Angle-Only Self-Localization and Target Tracking Based on the Bayesian Fisher Information Matrix | 10.3390/s24103120 |
| `chen2025error` | 2025 | IEEE Transactions on Instrumentation and Measurement | The Error Lower Bound of Target State Estimation in Passive Localization by Bearing-Only Sensors | 10.1109/tim.2025.3551589 |
| `luo2025dynamicbearing` | 2025 | Sensors | Dynamic Bearing--Angle for Vision-Based UAV Target Motion Analysis | 10.3390/s25144396 |
| `hu2025cyclic` | 2025 | Journal of Marine Science and Engineering | Cyclic Peak Extraction from a Spatial Likelihood Map for Multi-Array Multi-Target Bearing-Only Localization | 10.3390/jmse13010109 |
| `yin2025dual` | 2025 | Digital Signal Processing | Dual-UAV cooperative bearing-only target localization based on multi-level box particle filter | 10.1016/j.dsp.2025.105572 |
| `dou2025moving` | 2025 | International Journal of Robust and Nonlinear Control | Moving‐Target Localization and Circumnavigation Control for Second‐Order Multiagent Systems With Bearing‐Only Measurements | 10.1002/rnc.70085 |
| `mei2024bearing` | 2024 | Journal of Marine Science and Engineering | Bearing-Only Multi-Target Localization Incorporating Waveguide Characteristics for Low Detection Rate Scenarios in Shallow Water | 10.3390/jmse12122300 |
| `zong2025distributed` | 2025 | IEEE Internet of Things Journal | Distributed Passive Localization of a Noncooperative Underwater Target Utilizing Broadband Acoustic Interference Structure | 10.1109/jiot.2025.3627685 |
| `yu2025passive` | 2025 | JASA Express Letters | Passive localization of dual targets in deep-ocean direct-arrival zone using a horizontal line array | 10.1121/10.0039110 |
| `wu2026bearing` | 2026 | IEEE Sensors Journal | Bearing-Only Localization for Wideband Off-Grid Sources with Distributed Sensor Array Networks | 10.1109/jsen.2026.3651323 |
| `zeng2026three` | 2026 | JASA Express Letters | Three-dimensional passive localization of near-surface targets using a deep-sea bottom mounted horizontal array | 10.1121/10.0043180 |
| `zhou2026direct` | 2026 | IEEE Transactions on Aerospace and Electronic Systems | Direct Target Localization for Distributed Hybrid Active-Passive Radars with Direct-path Interference | 10.1109/taes.2026.3679854 |
| `liu2026sensing` | 2026 | IEEE Transactions on Network Science and Engineering | Sensing With Unknown Signals: ISAC Enabled Distributed Passive Sensing for Multi-Target Detection and Localization | 10.1109/tnse.2026.3670825 |
| `liu2026dfp` | 2026 | Digital Signal Processing | DFP-MLT: A lightweight wi-Fi-based framework for device-free passive multi-target localization via feature fusion and multi-label learning | 10.1016/j.dsp.2026.106053 |
| `sui2024adaptive` | 2024 | IEEE Robotics and Automation Letters | Adaptive Bearing-Only Target Localization and Circumnavigation Under Unknown Wind Disturbance: Theory and Experiments | 10.1109/lra.2024.3487483 |
| `zhou2026target` | 2026 | Ad Hoc Networks | Target localization in UAV swarm under multi-error coupling: A cooperative utility of information optimization approach | 10.1016/j.adhoc.2026.104154 |
