# Abstract and Storyline v2

## 1. Recommended Abstract for the Current Evidence

Passive bearing-only localization is an important capability for collaborative unmanned aerial vehicle systems operating in GNSS-denied and electromagnetically silent environments. However, classical geometric and least-squares estimators are highly sensitive to biased bearings, missing observations, and outlier contamination, while heavier heuristic or graph-based pipelines often reduce interpretability and reproducibility. This paper presents an interpretable robust passive localization framework that preserves geometric reasoning while strengthening degraded-regime estimation through consensus-style candidate generation, trimming-aware residual suppression, and iterative reweighted refinement. Extensive synthetic experiments under biased, outlier, mixed-corruption, and multi-formation settings show that the proposed framework substantially improves stability over least-squares baselines, sharply reduces catastrophic failures in outlier-rich regimes, and remains competitive with heuristic global search. Additional sensitivity, scaling, significance, and observability-oriented analyses further clarify that the method is most effective when measurement corruption is strong and collaborative geometry is sufficiently informative. The resulting pipeline provides a reproducible robust localization core for collaborative UAV sensing and a practical foundation for future observability-guided active extensions.

## 2. Stronger Abstract for the Upgraded Version

GNSS-denied collaborative UAV sensing requires passive localization methods that remain reliable under corrupted bearings and changing swarm geometry. Existing bearing-only approaches are often either fragile under bias and outliers or system-heavy and difficult to reproduce. This paper proposes an observability-guided active robust bearing-only localization framework that couples an interpretable robust geometric estimator with decision-making that improves sensing geometry under degraded measurements. The estimator combines multi-candidate geometric initialization, trimming-aware residual control, and iterative reweighted refinement, while the active module selects informative sensing configurations using observability-oriented criteria. Experiments across corrupted-measurement regimes, formation changes, sensor-count scaling, and active trajectory decisions show that the framework improves degraded-regime stability, reduces large-error failures, and outperforms passive baselines when geometry quality would otherwise limit estimation accuracy. These results position the method as a computer-oriented and reproducible bridge between classical bearing-only geometry and modern collaborative UAV sensing systems.

## 3. Recommended Contribution List

1. An interpretable robust passive localization core that improves stability under biased, missing, and outlier-corrupted bearings.
2. A degraded-regime benchmark protocol covering severity sweeps, scaling, formation variation, significance testing, and observability interpretation.
3. A literature-grounded pathway from static robust estimation toward observability-guided active collaborative sensing.

## 4. Recommended Keywords

- passive localization
- bearing-only localization
- UAV swarm
- collaborative sensing
- robust estimation
- observability
- GNSS-denied navigation

## 5. Story in One Paragraph

The story should not be “we invented another optimizer”. The story should be “in passive collaborative UAV sensing, corrupted bearings are the real operational bottleneck; we therefore build a lightweight but robust localization core that is reproducible, interpretable, and clearly stronger than classical least squares in the corrupted regimes that matter most, while exposing a clean upgrade path toward observability-guided active sensing.”

## 6. One-Sentence Pitch for Reviewers

This manuscript contributes a reproducible and interpretable robust bearing-only localization core for collaborative UAV sensing under corrupted measurements, together with a degraded-regime evaluation protocol that clarifies where the method truly helps and where further active-sensing upgrades are needed.
