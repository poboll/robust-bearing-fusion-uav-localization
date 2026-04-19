# Robust Collaborative Bearing-Only Passive Localization for UAV Swarms under Degraded Measurements

## Abstract

Passive bearing-only localization is an important capability for collaborative unmanned aerial vehicle (UAV) systems operating in GNSS-degraded or electromagnetically silent environments. However, classical geometric and least-squares estimators are highly sensitive to biased bearings, missing observations, and outlier corruption, while stochastic heuristic solvers are often difficult to interpret and reproduce. This paper proposes a geometry-preserving robust passive localization framework that combines consensus-style geometric initialization, trimming-aware residual handling, and iterative reweighted refinement for collaborative bearing-only estimation. The framework retains the transparency of classical geometry while improving degraded-regime robustness. Extensive synthetic experiments under biased, outlier, and mixed corruption regimes show that the proposed method improves stability relative to least-squares baselines, substantially reduces large-error failures, and remains competitive with heuristic global search methods. In the outlier regime, the median localization error decreases from 1.629 for least squares to 0.386, while the catastrophic failure rate above 5.0 is reduced to zero. Formation-generalization experiments across circular, elliptical, perturbed, and random swarm geometries further show that the method is not tied to a single idealized layout. Runtime measurements indicate that the proposed method has nearly the same median runtime as PSO in the current implementation while offering stronger interpretability and more stable degraded-regime behavior.

## Keywords

Passive localization; bearing-only localization; UAV swarm; robust estimation; iterative reweighting; degraded measurements

## 1. Introduction

Collaborative UAV systems are increasingly expected to operate in GNSS-denied, contested, or electromagnetically silent environments, where active positioning infrastructure may be unavailable or undesirable. In such scenarios, passive localization based on bearing-only or angle-of-arrival (AOA) sensing is especially attractive because it supports low-emission operation while preserving deployment flexibility. However, bearing-only localization is fragile: geometric ambiguity, unfavorable sensor layout, biased measurements, missing observations, and occasional outliers can all lead to large estimation errors or outright failure [1], [2].

Recent UAV localization research has evolved along several active directions. Survey work published in 2025 shows the growing role of optimization-based estimation, sensor fusion, and graph-structured inference in autonomous UAV localization [1]. In parallel, theoretical work on AOA localization has revisited consistency and asymptotic efficiency, showing that estimator quality still depends strongly on model structure and measurement handling [3]. Bearing-only tracking research has also moved toward recursive total least-squares and observability-aware estimation [4]. Meanwhile, collaborative UAV navigation increasingly incorporates distributed graph optimization and cooperative information fusion rather than purely isolated local solvers [7], [8].

Despite this progress, a practical gap remains. On one side, classical geometry and least squares are interpretable, lightweight, and easy to deploy, but they often break down under degraded measurements. On the other side, stochastic global-search heuristics can occasionally recover strong solutions, yet their behavior is harder to explain, reproduce, and integrate into collaborative autonomy pipelines. Existing passive-positioning studies in UAV formations have also often focused on specific formation adjustment strategies or application-specific optimization formulations [5], [6], leaving open the need for a more general robust estimation framework centered on corrupted bearing-only measurements.

This paper addresses that gap with a geometry-preserving robust passive localization framework. Rather than replacing geometric reasoning with a black-box estimator, the proposed method strengthens it through three complementary mechanisms: consensus-style geometric initialization, trimming-aware residual suppression, and iterative residual reweighting. The resulting framework preserves interpretability while improving stability under bias, outliers, and mixed degradation.

The main contributions are summarized as follows:

1. A robust collaborative bearing-only localization framework is developed by integrating consensus geometric initialization with trimming-aware iterative reweighted refinement.
2. A degraded-regime benchmark protocol is constructed to evaluate biased, outlier-contaminated, missing, and mixed measurement conditions rather than only nominal noise.
3. Extensive experiments show improved median accuracy and reduced catastrophic failures relative to least-squares baselines, while remaining competitive with stochastic heuristics across multiple swarm formations and comparable runtime to PSO in the current implementation.

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 formulates the collaborative bearing-only localization problem. Section 4 presents the proposed method. Section 5 reports experimental results. Section 6 discusses implications and limitations. Section 7 concludes the paper.

## 2. Related Work

### 2.1 UAV Localization and Collaborative Navigation

Recent reviews indicate that autonomous UAV localization increasingly relies on multi-sensor fusion, nonlinear optimization, and graph-structured estimation rather than isolated geometric solvers [1]. Collaborative UAV navigation has similarly shifted toward distributed information fusion and scalable cooperative localization [7], [8]. These developments suggest that purely static, idealized localization pipelines are becoming insufficient for realistic multi-UAV systems.

### 2.2 Bearing-Only and AOA Localization

Bearing-only and AOA-based localization remain important because they are compatible with passive or low-emission sensing. Han et al. investigated relative DOA estimation for UAV swarms without fixed anchors and demonstrated improved localization behavior under noisy conditions [2]. Hu et al. provided theoretical guarantees for AOA-based localization and showed that low-complexity estimators can approach maximum-likelihood behavior under suitable assumptions [3]. These studies confirm that passive directional localization remains an active research area, while also underscoring the importance of estimator stability and measurement robustness.

### 2.3 Passive Localization in UAV Swarms

Passive positioning has recently been revisited in UAV formation contexts. Kang et al. proposed an AOA azimuth-only passive-positioning method for swarm formation flight [5], and Huang et al. studied passive positioning and adjustment under electromagnetic-compatibility constraints [6]. These works demonstrate the practical relevance of passive positioning, but they do not primarily frame the problem as robust degraded-regime estimation with systematic failure analysis.

### 2.4 Robust and Structured Estimation

Robust collaborative estimation increasingly emphasizes outlier resistance, bias mitigation, and distributed inference. Li et al. proposed a recursive total least-squares approach for bearing-only analysis and circumnavigation [4], while Guo et al. studied collaborative navigation for UAV formation using factor graph optimization [7]. Compared with a full graph-optimization pipeline, the present work targets a lighter yet more robust middle ground: it preserves geometric interpretability while explicitly strengthening the refinement stage against corrupted bearings.

## 3. Problem Formulation

Consider \(N\) observing UAVs located at
\[
s_i = [x_i, y_i]^T,\quad i = 1,\dots,N,
\]
and a target position
\[
p = [x, y]^T.
\]
Each valid observing UAV provides a bearing-only measurement
\[
\theta_i = \operatorname{atan2}(y-y_i, x-x_i) + b + \epsilon_i + o_i,
\]
where \(b\) is a common angular bias, \(\epsilon_i\) is nominal noise, and \(o_i\) denotes occasional outlier corruption. Some observations may be missing due to sensing failure, communication loss, or formation constraints.

The objective is to estimate \(p\) from the available bearing set while controlling both nominal error and tail-risk behavior. Because heavy-tailed failures are central to degraded passive localization, evaluation should not rely on mean error alone; it should also include median error, upper-tail behavior, success rate, and catastrophic failure rate.

## 4. Proposed Method

### 4.1 Consensus Geometric Initialization

Classical bearing-only localization often begins with pairwise line intersections. This is transparent but fragile: one poor bearing can distort the entire intersection cloud. The proposed framework therefore constructs multiple geometric candidates from the intersections:

1. a centroid-style candidate,
2. a median-style consensus candidate,
3. an inlier-focused candidate produced by trimming distant intersections.

The later robust stage selects and refines the best candidate rather than relying on a single brittle initialization.

### 4.2 Trimming-Aware Iterative Reweighting

For each candidate point, wrapped angular residuals are computed between predicted and observed bearings. A Huber-style robust objective is used, but two additional mechanisms are introduced:

1. residual-based reweighting, which smoothly downweights large residuals,
2. explicit trimming, which deactivates the worst residuals and still activates in small-sample settings with as few as 4-6 valid bearings.

This combination prevents a few corrupted observations from dominating the final estimate.

### 4.3 Optional Bias Correction

The framework also supports a lightweight common-bias correction term through the circular weighted mean of residuals. However, current ablation results show that trimming and reweighting contribute more strongly than bias estimation alone. Accordingly, the main novelty is better characterized as robust geometry-preserving refinement rather than as bias estimation in isolation.

### 4.4 Complexity

The proposed method is more expensive than plain least squares because it evaluates multiple candidates and performs iterative refinement. Nevertheless, the current implementation has a median runtime of 19.8 ms, which is effectively comparable to PSO at 19.9 ms while offering better structure and degraded-regime stability.

## 5. Experimental Results

### 5.1 Experimental Setup

All experiments are synthetic and fully reproducible. The simulator supports common bias, missing observations, outlier corruption, mixed degradation, and multiple UAV formation layouts. The baseline family includes least squares, vanilla robust Huber refinement, PSO, simulated annealing, and the proposed robust bias-trimmed method.

To avoid misleading conclusions under heavy-tailed failures, the primary metrics are median error, 90th-percentile error, success rate at fixed thresholds, catastrophic failure rate, and paired win count against baselines.

### 5.2 Regime Comparison

Figure 1 summarizes the single-run regime comparison under clean, biased, missing, outlier, and mixed measurements. The proposed method preserves low clean-regime error while showing its strongest gains in outlier and mixed regimes. In the outlier regime, the localization error decreases from 4.197 for least squares to 0.120. In the mixed regime, the error decreases from 9.073 to 0.752. These results support the claim that the framework is especially useful when bearings are corrupted rather than merely noisy.

### 5.3 Ablation Results

Figure 2 reports the mixed-regime ablation. Removing trimming significantly worsens upper-tail behavior, increasing the mixed-regime \(p90\) from 1.57 to 3.18. Reducing reweighting also weakens stability. By contrast, removing bias estimation changes the results only slightly in the current synthetic setup. This indicates that the main performance improvement comes from the interaction of consensus initialization, trimming, and iterative reweighting.

### 5.4 Formation Generalization

Figure 3 evaluates circular, elliptical, perturbed, and random formations. The proposed method consistently improves over least squares in all four cases. The random-formation case is particularly strong: the median localization error decreases from 2.105 for least squares to 0.577 for the proposed method. This result is important because it shows that the method is not overfit to a single idealized circular layout.

### 5.5 Robust Statistics and Runtime

The 20-seed results further strengthen the degraded-regime story. In the outlier regime, the median error decreases from 1.629 for least squares to 0.386 for the proposed method, and the catastrophic failure rate above 5.0 falls to zero. In the mixed regime, the median error decreases from 1.486 to 0.678, and the proposed method wins against least squares in 17 of 20 runs while remaining approximately tied with PSO. Runtime results in Figure 4 show that the median runtime of the proposed method is 19.8 ms, nearly identical to PSO at 19.9 ms. Thus, the method improves degraded-regime robustness without exceeding the runtime of a representative heuristic global-search baseline.

## 6. Discussion

The proposed framework occupies a useful middle position between fragile classical estimation and opaque heuristic search. It clearly outperforms least squares under degraded measurements, yet it avoids relying entirely on stochastic global search. The comparison with PSO is intentionally balanced rather than exaggerated. In the mixed regime, the proposed method and PSO are approximately tied in paired wins, which supports a credible narrative: the framework does not replace all heuristic search in every case, but it provides a more structured and reproducible route to robust localization.

Several limitations should nevertheless be acknowledged. First, the current validation remains simulation-based. Second, observability-aware scheduling and cooperative recovery are not yet reintegrated as equally strong core contributions. Third, the current framework has not yet been embedded into a full collaborative factor-graph navigation stack. These limitations define the appropriate scope of the present manuscript and also point directly to future work.

## 7. Conclusion

This paper presented a geometry-preserving robust passive localization framework for collaborative UAV systems under degraded bearing-only measurements. By combining consensus geometric initialization, trimming-aware residual control, and iterative reweighted refinement, the proposed method improves median accuracy and failure robustness relative to least-squares baselines while remaining competitive with heuristic global search. The framework is lightweight, reproducible, and effective across multiple degraded regimes and swarm formations. Future work will focus on integrating observability-aware scheduling, cooperative recovery, and stronger graph-optimization structures into the same collaborative localization pipeline.
