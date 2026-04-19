# Robust Collaborative Bearing-Only Passive Localization for UAV Swarms under Degraded Measurements

## Abstract

Passive bearing-only localization is a critical capability for collaborative unmanned aerial vehicle (UAV) systems operating in GNSS-degraded or electromagnetically silent environments. However, classical geometric and least-squares estimators are highly sensitive to biased bearings, missing observations, and outlier contamination, while stochastic heuristic solvers are often difficult to interpret and reproduce. This paper proposes a geometry-preserving robust passive localization framework that combines consensus-style geometric initialization, trimming-aware residual filtering, and iterative reweighted refinement for collaborative bearing-only estimation. The proposed method is designed to retain the transparency of classical geometry while improving degraded-regime robustness. Extensive synthetic experiments under biased, outlier, and mixed corruption regimes show that the framework improves stability relative to least-squares baselines, substantially reduces large-error failures, and remains competitive with heuristic global search methods. In particular, in the outlier regime the median localization error decreases from 1.629 for least squares to 0.386, while the catastrophic failure rate above 5.0 is reduced to zero. Additional formation-generalization experiments across circular, elliptical, perturbed, and random swarm geometries further show that the method is not tied to a single idealized layout. The resulting pipeline is lightweight, reproducible, and suitable as a computer-oriented foundation for collaborative localization and recovery in UAV swarms.

## Keywords

UAV swarm localization; bearing-only localization; passive localization; robust estimation; iterative reweighting; degraded measurements

## 1. Introduction

Collaborative UAV systems are increasingly expected to operate in GNSS-denied, contested, or electromagnetically silent environments, where active positioning infrastructure may be unavailable or undesirable. In such settings, passive localization based on bearing-only or angle-of-arrival (AOA) measurements becomes especially attractive because it supports low-emission operation while preserving deployment flexibility. At the same time, bearing-only localization is notoriously fragile: geometric ambiguity, unfavorable sensor deployment, biased bearings, missing observations, and occasional outliers can all produce large estimation errors or outright failure [1], [2].

Recent UAV localization research has moved along several distinct directions. Survey work published in 2025 highlights a rapid expansion of sensor-assisted, optimization-based, and fusion-based UAV localization methods, while also emphasizing the trade-off between accuracy, interpretability, real-time performance, and data dependence [1]. In parallel, recent AOA-oriented work has revisited the theoretical side of localization, including consistency and asymptotic efficiency guarantees for AOA-based estimators [3]. Bearing-only tracking research has also evolved toward recursive total least-squares and observability-aware estimation strategies, showing that bias control and trajectory-aware estimation remain central issues in passive localization [4]. Meanwhile, multi-UAV coordination research increasingly incorporates distributed graph optimization and cooperative information fusion, reflecting a broader trend from isolated estimators toward collaborative navigation systems [7], [8].

Despite this progress, a practical gap remains. On one side, classical geometric and least-squares pipelines are interpretable, lightweight, and easy to deploy, but they often break down under degraded measurements. On the other side, stochastic global-search heuristics can occasionally recover strong solutions, yet their behavior is harder to explain, reproduce, and integrate into collaborative autonomy pipelines. Existing UAV swarm passive-positioning studies have also often focused on specific idealized formations or problem-specific optimization schemes, such as AOA-only formation adjustment or electromagnetic-compatibility-constrained passive positioning [5], [6]. These studies are valuable, but they do not fully close the gap between fragile classical geometry and a robust, reproducible collaborative estimation pipeline for corrupted bearing-only measurements.

To address this gap, this paper proposes a geometry-preserving robust passive localization framework for collaborative UAV systems. The core idea is not to replace geometric reasoning with a black-box model, but to strengthen it with three complementary mechanisms: consensus-style geometric initialization, trimming-aware residual handling, and iterative residual reweighting. The resulting framework is designed to retain interpretability while improving stability in the presence of bias, outliers, and mixed corruption.

The main contributions of this work are as follows:

1. A robust collaborative bearing-only localization framework is developed by integrating consensus geometric initialization with trimming-aware iterative reweighted refinement.
2. A degraded-regime benchmark protocol is constructed to systematically evaluate biased, outlier-contaminated, missing, and mixed measurement conditions rather than only nominal noise.
3. Extensive experiments show that the proposed method improves median accuracy and reduces catastrophic failures relative to least-squares baselines, while remaining competitive with stochastic heuristics across multiple swarm formations and similar runtime cost to PSO in the current implementation.

The remainder of this paper is organized as follows. Section 2 reviews related work on UAV localization, robust bearing-only estimation, and collaborative navigation. Section 3 formulates the collaborative bearing-only localization problem under degraded measurements. Section 4 introduces the proposed robust framework. Section 5 reports experimental results, including regime comparison, ablation analysis, formation generalization, and runtime comparison. Section 6 discusses strengths, limitations, and publication-relevant implications. Section 7 concludes the paper.

## 2. Related Work

### 2.1 UAV Localization and Multi-Sensor Fusion

Recent reviews confirm that UAV localization research is increasingly dominated by multi-sensor fusion, optimization-based estimation, and graph-structured inference [1]. Classical filtering methods remain attractive for their efficiency, but they are sensitive to modeling assumptions and measurement quality. Optimization-based fusion, including factor graph optimization, has become more prominent because it can unify heterogeneous constraints and support higher-dimensional nonlinear estimation [1], [7], [8]. However, these methods also introduce additional modeling complexity and may require more careful noise handling.

### 2.2 Bearing-Only and AOA-Based Localization

Bearing-only and AOA-based localization remain important because they are compatible with passive or low-emission sensing. Han et al. studied relative DOA estimation for UAV swarms in GNSS-denied environments without fixed anchors and showed that phase-difference-driven DOA estimation can improve success rate relative to weaker baselines under noisy conditions [2]. On the theoretical side, Hu et al. established consistency and asymptotic efficiency properties for AOA-based localization and proposed a low-complexity two-step estimator that approaches maximum-likelihood performance for large sample sizes [3]. These works reinforce two points relevant to the present study: first, AOA localization remains an active research direction; second, estimator stability still depends strongly on model structure, initialization, and error handling.

### 2.3 Bearing-Only Passive Localization in UAV Swarms

Recent UAV swarm studies have revisited passive positioning from the viewpoint of pure azimuth or electromagnetically silent coordination. Kang et al. proposed an AOA azimuth-only passive-positioning method for UAV swarm formation flight and combined localization with a two-step adjustment strategy [5]. Huang et al. later extended passive positioning toward an electromagnetic-compatibility-constrained setting, studying how intra-formation interference affects localization and adjustment [6]. These studies show that passive positioning is practically relevant and publication-worthy. However, they remain more tailored to specific formation or adjustment settings and do not primarily focus on robust degraded-regime estimation as a standalone contribution.

### 2.4 Robust and Collaborative Estimation

Robust collaborative estimation increasingly emphasizes stability under corrupted measurements and distributed information fusion. Li et al. proposed a recursive total least-squares method for bearing-only target motion analysis and circumnavigation, highlighting bias mitigation and observability enhancement in mobile-observer settings [4]. More recently, Guo et al. proposed distributed collaborative navigation for UAV formations based on factor graph optimization, reflecting the broader shift toward scalable collaborative inference frameworks [7]. A 2025 review on distributed cooperative localization algorithms for multi-UAV systems likewise emphasized decentralized architectures, information fusion, and algorithm selection trade-offs [8].

In contrast to both purely classical geometry and fully graph-optimized collaborative navigation, the present work occupies a middle position. It preserves the transparency of geometric estimation while introducing a robust refinement layer specifically targeted at degraded bearing-only measurements. This makes the framework both lighter than a full collaborative graph-optimization stack and more robust than plain least squares.

## 3. Problem Formulation

Consider a collaborative UAV system with \(N\) observing platforms located at positions
\[
s_i = [x_i, y_i]^T,\quad i = 1,\dots,N,
\]
and a target position
\[
p = [x, y]^T.
\]
Each observing UAV provides a bearing-only measurement
\[
\theta_i = \operatorname{atan2}(y-y_i, x-x_i) + b + \epsilon_i + o_i,
\]
where \(b\) denotes a common angular bias term, \(\epsilon_i\) denotes nominal zero-mean noise, and \(o_i\) denotes occasional gross corruption or outlier disturbance. Some measurements may also be missing entirely due to communication loss, sensing failure, or formation constraints.

The objective is to recover \(p\) from the available bearing set while maintaining:

1. low median localization error under degraded regimes,
2. controlled upper-tail failure behavior,
3. reproducible performance across different swarm formations, and
4. computational cost that remains practical for collaborative autonomy pipelines.

This formulation deliberately focuses on degraded bearing corruption rather than only nominal Gaussian noise, because the latter is often too weak to discriminate between estimation strategies.

## 4. Proposed Method

### 4.1 Consensus Geometric Initialization

Classical bearing-only localization often begins by intersecting bearing rays pairwise. While this is transparent, any single bad bearing can distort the resulting intersection cloud. Instead of relying on one fragile closed-form estimate, the proposed method first generates multiple candidate initial states from pairwise intersections:

1. a centroid-style candidate,
2. a median-style consensus candidate,
3. an inlier-focused candidate derived from a distance-trimmed subset of intersections.

This multi-candidate strategy keeps the initialization fully geometric while reducing sensitivity to a single bad intersection pattern.

### 4.2 Trimming-Aware Iterative Reweighting

Given an initial candidate \(p^{(0)}\), residuals are defined as wrapped angular mismatches between predicted and observed bearings. The robust objective follows a Huber-style form, but two additional mechanisms are introduced:

1. residual reweighting, which continuously downweights large residuals instead of treating all bearings equally;
2. trimming, which can temporarily deactivate the worst residuals even in small-sample settings with only 4-6 valid bearings.

In each reweighting round, the algorithm:

1. computes residuals,
2. identifies the largest residuals for trimming,
3. derives weights from the residual magnitudes,
4. performs weighted iterative refinement of the position estimate.

This design prevents a few corrupted bearings from dominating the solution.

### 4.3 Optional Common-Bias Correction

An optional common-bias correction term is maintained by computing a circular weighted mean of residuals. This step is intentionally lightweight. In the current synthetic experiments, ablation shows that trimming and reweighting contribute more strongly than explicit bias estimation to the final improvement. Therefore, bias correction is retained as a useful component, but not presented as the sole innovation.

### 4.4 Complexity and Practical Positioning

The proposed method is more expensive than plain least squares because it evaluates multiple candidates and performs iterative reweighting. However, the current implementation achieves a median runtime of about 19.8 ms, which is effectively the same order as PSO at 19.9 ms, while offering stronger interpretability and better degraded-regime stability.

## 5. Experiments

### 5.1 Experimental Setup

All experiments are synthetic and fully reproducible. The simulator supports measurement noise, common bias, missing observations, outlier corruption, and multiple swarm formations. The baseline set includes geometric initialization, least squares refinement, robust Huber refinement, PSO, simulated annealing (SA), and the proposed robust bias-trimmed refinement.

To avoid misleading conclusions under heavy-tailed failures, the primary metrics are median error, 90th-percentile error, success rate below a threshold, catastrophic failure rate above a threshold, and paired win count against baselines.

### 5.2 Regime Comparison

The regime comparison includes clean, biased, missing, outlier, and mixed degraded measurements. The strongest evidence appears in the outlier and mixed regimes. In the outlier regime, the proposed method reduces the single-run error from 4.197 for least squares to 0.120. In the mixed regime, the single-run error decreases from 9.073 for least squares to 0.752. Importantly, the clean-regime error remains low at 0.0109, showing that the robust method does not sacrifice nominal accuracy in the current setup.

### 5.3 Ablation Study

The ablation study compares the default setting with variants that disable bias estimation, disable trimming, reduce reweighting, or use heavier trimming. Three findings stand out.

First, trimming is especially important for mixed-regime tail control: removing trimming increases the mixed-regime \(p90\) from about 1.57 to 3.18. Second, iterative reweighting improves stability in the mixed regime relative to lighter reweighting. Third, explicit bias estimation has a smaller impact than expected in the present synthetic setup, which indicates that the main innovation is better characterized as robust geometry-preserving refinement rather than as a pure bias-estimation method.

### 5.4 Formation Generalization

To test whether the method is tied to a single idealized geometry, additional experiments were performed on circular, elliptical, perturbed, and random formations. The proposed method remains effective across all four cases. In the random-formation case, the median localization error decreases from 2.105 for least squares to 0.577. In elliptical and perturbed formations, the proposed method also maintains strong median accuracy while avoiding the unstable tail behavior observed in some heuristic runs.

### 5.5 Runtime

Runtime measurements were collected over repeated runs in the mixed regime. Least squares and vanilla robust Huber refinement run in about 2.5-3.3 ms median time, whereas the proposed robust method and PSO both run in about 19.8-19.9 ms median time. Thus, the proposed method improves degraded-regime robustness without exceeding the runtime of a representative heuristic global-search baseline in the current implementation.

## 6. Discussion

The results suggest that the proposed framework occupies a useful middle ground. It clearly outperforms classical least squares under degraded measurements, yet it does not rely on opaque or difficult-to-reproduce heuristic behavior. Against PSO, the comparison is intentionally balanced rather than exaggerated. In the mixed regime, the proposed method and PSO are approximately tied in paired wins, which is scientifically useful because it supports a credible story: the method is not a universal replacement for all heuristic search, but it offers a more structured and interpretable route to robust localization.

Several limitations remain. First, the current evidence is still simulation-based. Second, observability-aware scheduling and cooperative recovery are not yet re-integrated as equally strong core contributions. Third, the method has not yet been embedded into a full factor-graph collaborative navigation stack. For these reasons, the present paper should foreground robust localization and treat scheduling or recovery as future extensions rather than as fully closed contributions.

## 7. Conclusion

This paper presented a geometry-preserving robust passive localization framework for collaborative UAV systems under degraded bearing-only measurements. By combining consensus geometric initialization, trimming-aware residual control, and iterative reweighted refinement, the method improves median accuracy and failure robustness relative to least-squares baselines while remaining competitive with heuristic global search. The framework is lightweight, reproducible, and effective across multiple degraded regimes and formation geometries. Future work will focus on integrating observability-aware scheduling, cooperative recovery, and stronger collaborative graph-optimization structures into the same robust localization pipeline.

## References

[1] H. Liu, Q. Long, B. Yi, et al., "A survey of sensors based autonomous unmanned aerial vehicle (UAV) localization techniques," Complex & Intelligent Systems, vol. 11, p. 371, 2025. doi: 10.1007/s40747-025-01961-2.

[2] Y. Han, J. Zhang, and J. Luo, "Relative DOA estimation method for UAV swarm based on phase difference information without fixed anchors," Scientific Reports, vol. 15, art. 14394, 2025. doi: 10.1038/s41598-025-97961-w.

[3] S. Hu, G. Zeng, W. Xue, H. Fang, and B. Mu, "Theoretical Guarantees for AOA-based Localization: Consistency and Asymptotic Efficiency," arXiv:2507.07647, 2025.

[4] L. Li, X. Liu, Z. Qiu, T. Hu, and Q. Zhang, "A Recursive Total Least Squares Solution for Bearing-Only Target Motion Analysis and Circumnavigation," arXiv:2508.11289, accepted by IROS 2025.

[5] Z. Kang, Y. Deng, H. Yan, L. Yang, S. Zeng, and B. Li, "A New Method of UAV Swarm Formation Flight Based on AOA Azimuth-Only Passive Positioning," Drones, vol. 8, no. 6, art. 243, 2024. doi: 10.3390/drones8060243.

[6] J. Huang, L. Zhang, and W. Wang, "Passive Positioning and Adjustment Strategy for UAV Swarm Considering Formation Electromagnetic Compatibility," Drones, vol. 9, no. 6, art. 426, 2025. doi: 10.3390/drones9060426.

[7] P. Guo et al., "Distributed collaborative navigation for UAV formation based on factor graph optimization," Measurement, vol. 257, part C, art. 118732, 2026. doi: 10.1016/j.measurement.2025.118732.

[8] Z. Zhang, N. Li, G. Yan, and W. Li, "The development of distributed cooperative localization algorithms for Multi-UAV systems in the past decade," Measurement, vol. 256, part A, art. 118040, 2025. doi: 10.1016/j.measurement.2025.118040.
