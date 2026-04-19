# Uncertainty-Aware Bearing-Only Passive Localization with Credibility-Guided Measurement Selection for Collaborative UAV Sensing

Authors:
- Zengye Su (first author, corresponding author; affiliation and e-mail pending author confirmation)
- Yudan Nie (affiliation to be confirmed before submission)
- Zilu Zhou (Guangzhou College of Commerce, Guangzhou 511363, China)

## Abstract

Passive bearing-only localization remains attractive for collaborative unmanned aerial vehicle (UAV) sensing in GNSS-denied or electromagnetically silent missions, but its practical usefulness is limited by uncertain measurements. In realistic deployments, some bearings can be biased, missing, or grossly corrupted, so fusing every available observation may destabilize the estimate instead of improving it. This paper presents an uncertainty-aware algorithmic framework for passive bearing localization that couples a geometry-preserving robust estimator with a credibility-guided measurement-selection layer. The robust core combines multi-candidate geometric initialization, trimming-aware residual suppression, iterative reweighting, and optional common-bias correction. A subsequent selection stage ranks measurement subsets using observability quality, angular diversity, geometry isotropy, and residual-derived reliability, then re-estimates the target from the chosen subset. Synthetic experiments under biased, outlier, mixed-corruption, multi-formation, and sensor-scaling settings show that the robust core markedly improves over least squares in the regimes that matter most for passive sensing. In the fixed-budget selection benchmark, the proposed policy reduces the overall median error to `0.4977`, compared with `0.7491` for random subsets, `0.5676` for angular-spread greedy selection, and `0.5200` for FIM/CRLB-greedy selection, while achieving the best success rate at the 1.0-error threshold among the tested subset policies. The comparison with all-sensor estimation is mixed, indicating that measurement selection is most useful when part of the bearing set is unreliable rather than universally preferable. The resulting study is best understood as a reproducible passive-localization framework for uncertain observations and a practical bridge toward stronger active sensing.

## 1. Introduction

Collaborative UAV systems are increasingly expected to operate in GNSS-denied, low-emission, or electromagnetically silent environments. In such settings, passive bearing-only or angle-of-arrival sensing remains attractive because it supports target search, emergency observation, and low-detectability surveillance without requiring active emission. The practical difficulty is not simply geometric triangulation itself, but the fact that real bearings are unreliable: some observations can be biased, intermittently missing, or contaminated by large errors, and a small number of bad bearings can trigger large localization failures.

Recent literature shows two strong development trends. One line pushes toward system-level cooperative localization through formation constraints, distributed estimation, and factor-graph inference. Another line improves sensing geometry through observability-aware trajectory design, CRLB-driven path optimization, sensor-bias calibration, or passive node selection. These directions are important, but they do not remove a lighter-weight practical need: in a single passive localization cycle, how should a UAV team localize robustly when the available bearings are uncertain and not all of them deserve equal trust?

This manuscript targets that problem. It presents an uncertainty-aware bearing-only passive localization framework that keeps geometric reasoning explicit while improving robustness under degraded measurements. The method first stabilizes estimation through multi-candidate initialization, trimming-aware residual handling, and iterative reweighting, then performs credibility-guided measurement selection based on observability quality and residual reliability. The paper does not claim to replace graph-based cooperative inference or long-horizon trajectory planning. Instead, it shows that a lightweight algorithmic framework can materially improve passive localization under uncertain observations and can produce a reusable baseline for stronger active-sensing extensions.

The main contributions are fourfold:

1. An interpretable robust bearing-only passive localization framework for collaborative UAV sensing under biased, missing, and outlier-corrupted measurements.
2. A credibility-guided measurement-selection strategy that explicitly treats some bearings as more informative and trustworthy than others, instead of assuming that every available observation should always be fused.
3. A degraded-regime benchmark protocol covering regime comparison, ablation, formation generalization, sensitivity sweeps, sensor-count scaling, paired significance testing, and observability-oriented interpretation.
4. A restrained literature-grounded positioning of the method as a simulation-validated algorithmic framework for uncertain passive sensing rather than a universal replacement for heavier system-level localization pipelines.

## 2. Related Work

Recent surveys confirm that UAV localization remains an active topic under GNSS degradation, heterogeneous sensing, and cooperative mission constraints. Within this broader area, passive localization remains especially relevant in low-emission or electromagnetically silent scenarios, including recent UAV formation studies on azimuth-only positioning and system-level node selection for passive target localization. Recent UAV formation papers therefore still study azimuth-only passive positioning, showing that the application background is contemporary rather than outdated.

Another active thread in the literature seeks better geometry or better decisions. Observability-aware path design, sensor-bias calibration, active trajectory optimization, and CRLB-driven path optimization have been studied to improve bearing-only localization quality or broader passive-target-localization performance. These papers show that informative geometry matters, but they typically emphasize motion planning, path design, or system-level sensing allocation rather than the reliability triage of a fixed bearing set.

At the same time, cooperative localization research is becoming more system-oriented. Representative examples include formation-constrained localization, distributed estimation, and factor-graph inference for UAV teams. Those directions are stronger at the system level, but they also impose a heavier modeling and integration burden than a lightweight passive estimator. Compared with them, the present work focuses on a narrower question: how far a geometry-preserving robust estimator can go when it explicitly accounts for corrupted bearings and is equipped with a lightweight measurement-selection layer.

## 3. Problem Formulation

We consider a single passive localization cycle for a collaborative UAV team. Let `N` observing UAVs be located at positions `s_i = [x_i, y_i]^T`, and let the target position be `p = [x, y]^T`. Each valid observer provides a bearing-only measurement

```math
\theta_i = \operatorname{atan2}(y-y_i, x-x_i) + b + \epsilon_i + o_i
```

where `b` is a common angular bias term, `epsilon_i` denotes nominal noise, and `o_i` models occasional gross corruption. Some measurements may be unavailable because of missed detections, occlusion, or communication loss.

For a candidate target position `p`, the predicted bearing from observer `i` is

```math
\hat{\theta}_i(p)=\operatorname{atan2}(y-y_i, x-x_i),
```

and the wrapped residual under common bias `b` is

```math
r_i(p,b)=\operatorname{wrap}\!\left(\hat{\theta}_i(p)-\theta_i-b\right),
```

where `wrap(·)` maps an angle to `(-\pi,\pi]`.

The objective is to recover the target under uncertain measurements while controlling failure risk. Two features are important in this paper. First, the estimator should remain stable when some bearings are unreliable. Second, when only a subset of measurements should be retained, the selection rule should prefer bearings that are both informative and credible. The manuscript studies five representative regimes: clean, biased, missing, outlier, and mixed.

## 4. Proposed Method

### 4.1 Consensus Geometric Initialization

Instead of relying on a single closed-form estimate, the method generates several geometric candidates from pairwise bearing intersections and simple aggregation rules. For observer `i`, the bearing ray is

```math
\ell_i(\tau_i)=s_i+\tau_i
\begin{bmatrix}
\cos\theta_i\\
\sin\theta_i
\end{bmatrix},
```

and pairwise intersection candidates are aggregated into centroid, coordinate-wise median, and trimmed-centroid seeds. This preserves interpretability while reducing dependence on any one fragile initialization.

### 4.2 Trimming-Aware Robust Refinement

For each candidate, wrapped angular residuals are computed between predicted and observed bearings. The refinement stage minimizes a weighted Huber objective

```math
J(p,b;w)=\frac{\sum_{i=1}^{N} w_i \,\rho_{\delta}(r_i(p,b))}{\sum_{i=1}^{N} w_i},
```

with

```math
\rho_{\delta}(r)=
\begin{cases}
\frac{1}{2}r^2, & |r|\le \delta,\\
\delta\left(|r|-\frac{1}{2}\delta\right), & |r|>\delta.
\end{cases}
```

At each outer iteration, the largest residuals are trimmed according to a trim ratio `alpha`, and the remaining observations are reweighted by

```math
w_i \leftarrow \max\!\left(w_{\min}, \min\left(1,\frac{\delta}{|r_i(p,b)|+\varepsilon}\right)\right),
```

with trimmed observations forced to zero weight. This stage acts as the uncertainty-handling core of the framework.

### 4.3 Optional Common-Bias Correction

The framework also includes a lightweight circular residual-mean correction term for shared angular bias:

```math
b \leftarrow \angle \left(\sum_{i=1}^{N} w_i \exp\!\left(j\tilde{r}_i\right)\right),
```

where `\tilde{r}_i = wrap(\hat{\theta}_i(p)-\theta_i)`. Ablation results show that trimming and robust weighting contribute more strongly than bias correction alone, but the bias term remains useful when corruption is moderate rather than extreme.

### 4.4 Credibility-Guided Measurement Selection

The second stage adds a one-shot measurement-selection layer after the pilot robust estimate. Starting from all currently valid bearings, the method first computes a pilot estimate and its residual pattern. It then scores candidate subsets using four ingredients: weighted observability quality, geometry isotropy, angular diversity, and residual-derived reliability. For a subset `S`, the weighted Fisher-style geometry matrix is

```math
\mathbf{F}_{\mathcal{S}}=\sum_{i\in\mathcal{S}} w_i\,\mathbf{J}_i^\top \mathbf{J}_i,
```

and isotropy is measured as

```math
\eta_{\mathcal{S}}=\frac{\lambda_{\min}(\mathbf{F}_{\mathcal{S}})}{\lambda_{\max}(\mathbf{F}_{\mathcal{S}})}.
```

Angular diversity is estimated by

```math
\nu_{\mathcal{S}}=\frac{2}{|\mathcal{S}|(|\mathcal{S}|-1)\pi}\sum_{i<j,\, i,j\in\mathcal{S}}
\left|\operatorname{wrap}\!\left(\hat{\theta}_i-\hat{\theta}_j\right)\right|.
```

The proposed combined score is

```math
\begin{aligned}
\operatorname{Score}_{\text{prop}}(\mathcal{S}) ={}& 0.95 \log\!\left(1+10^{4}\det(\mathbf{F}_{\mathcal{S}})\right)
+ 0.40 \eta_{\mathcal{S}}
+ 0.25 \nu_{\mathcal{S}} \\
&+ 0.75 \bar{w}_{\mathcal{S}}
+ 0.08 \log\!\left(1+50 \operatorname{tr}(\mathbf{F}_{\mathcal{S}})\right)
- 0.80 \min\!\left(\frac{\bar{r}_{\mathcal{S}}}{0.2}, 2\right).
\end{aligned}
```

The chosen subset is finally passed back into the same robust refinement module.

This stage should be interpreted as measurement triage rather than universal sensor pruning. Its role is to help in conditions where some available bearings are less trustworthy than others, or where a fixed sensing budget prevents using every observation.

## 5. Experimental Setup

All experiments are synthetic and fully reproducible. The benchmark includes common bias, missing observations, outlier corruption, mixed degradation, multiple formation layouts, and scaling in sensor count. Baselines include least squares, robust Huber refinement, particle swarm optimization (`PSO`), simulated annealing (`SA`), and the proposed robust bias-trimmed estimator. The fixed-budget selection benchmark additionally compares the proposed measurement-selection policy against random subset selection, angular-spread greedy selection, and FIM/CRLB-guided greedy selection.

The evaluation is organized around five scientific questions:

1. Does the method improve robustness under corrupted bearings?
2. Which components actually matter?
3. Does the advantage persist across formation layouts and sensor counts?
4. Are the differences statistically stable?
5. How does geometry quality help explain performance variation?

## 6. Results

The strongest gains appear in outlier-rich and mixed regimes. In the outlier setting, the proposed method reduces median error from `1.6290` to `0.3863` and eliminates catastrophic failures above `5.0` in the reported 20-seed summary. In the mixed regime, the median error drops from `1.4863` to `0.6779`, while paired sign testing against least squares yields `17` wins and `3` losses with `p = 0.0026`. Against `PSO`, the comparison is more balanced, which is exactly the honest interpretation this manuscript adopts: the method is a robust and reproducible alternative to fragile classical estimators rather than a universal winner against every heuristic baseline.

The severity sweeps further refine the claim. At outlier rate `0.40`, least squares reaches a median error of `1.9923`, while the proposed method remains at `0.9189`. At nominal noise `sigma = 0.08`, the proposed method remains slightly better than `PSO` and clearly better than least squares. In contrast, under pure high-bias stress, `PSO` can still be stronger, indicating that the main advantage of the proposed framework lies in robust corruption handling rather than bias-only compensation.

Formation-generalization and scaling experiments show that the method is not tied to a single idealized geometry. Under random formation, the mixed-regime median error decreases from `2.1047` to `0.5768`. In scaling experiments, richer collaborative geometry makes the robust core increasingly competitive: for a 12-UAV circular formation, the proposed method achieves `0.4048` median error versus `2.3359` for least squares and `0.3348` for `PSO`. Under random formations, the robust method outperforms `PSO` for the 8-, 10-, and 12-UAV settings.

To reduce the risk that the 20-seed summaries are merely small-sample artifacts, a higher-sample follow-up validation was also run for the two most important degraded regimes using 100 seeds. The same qualitative pattern remains. In the outlier regime, Robust-BT versus least squares yields `83` wins and `17` losses with sign-test `p = 1.31e-11`, and the median improvement is `1.6921` with a bootstrap 95% interval of approximately `[1.1023, 2.1663]`. In the mixed regime, Robust-BT versus least squares yields `75` wins and `25` losses with `p = 5.64e-7` and a median improvement of `0.5511` with a bootstrap 95% interval of approximately `[0.1310, 1.2295]`. Against `PSO`, the outlier advantage becomes only marginal and the mixed-regime comparison remains unfavorable, which supports the restrained claim of this paper: the framework is strongly preferable to fragile classical estimation, while its relationship to heuristic global search is competitive and regime-dependent rather than universally dominant.

The measurement-selection experiment is the key extension result, but it should be interpreted carefully. Aggregated over mixed and severe regimes, three formation families, and 8/10/12-UAV settings, the proposed policy achieves an overall median error of `0.4977`, compared with `0.7491` for random subset selection, `0.5676` for angular-spread greedy selection, and `0.5200` for FIM/CRLB-greedy selection. It also attains the best success rate at the 1.0-error threshold among the tested subset policies (`0.8531` versus `0.8298` for FIM/CRLB and `0.6200` for random selection). In the severe-regime slice, the proposed policy improves the mean error from `1.2450` to `0.9858` relative to FIM/CRLB selection while reducing the catastrophic-failure rate from `0.0282` to `0.0188`.

At the same time, the comparison with all-sensor robust estimation is mixed: the proposed policy yields a lower aggregate median error (`0.4977` versus `0.5510`), but the paired count is `200` wins versus `222` losses. This is an important boundary rather than a weakness to hide. It indicates that measurement selection is not a universal replacement for using every available bearing. Instead, it is most useful when measurement credibility varies or when the sensing process is budgeted and a smaller, cleaner subset is preferable to indiscriminate fusion.

An additional observability-oriented analysis was performed for interpretation only. Circular formations have higher median isotropy than random ones, and stronger estimators benefit more consistently from informative geometry than least squares. Runtime results are retained only as an implementation-cost reference and are not part of the main scientific claim.

## 7. Discussion

The paper's most defensible claim is that an interpretable robust passive-localization core is already worthwhile for uncertain measurement conditions. The framework clearly improves over least squares in the degraded regimes that matter most for passive sensing, especially outlier-rich and mixed settings. It also remains competitive with representative heuristic global search without relying entirely on opaque optimization behavior.

The measurement-selection layer further clarifies the practical story. When only a subset of bearings should be trusted or retained, residual-aware selection can outperform random, geometry-only, and FIM-only subset policies. However, the mixed paired comparison against all-sensor estimation also shows that selection should be viewed as a conditional tool, not a universal law. This honesty is important for journal quality because it ties the contribution to a real operational question: not all passive observations are equally useful, and a lighter system may benefit from selecting the most credible ones.

The literature review also shows where stronger future work lies. Recent papers increasingly incorporate observability-aware trajectory design, CRLB-driven path planning, passive node selection, or heavier collaborative inference. The present study is therefore best positioned as an intermediate but meaningful step: a lightweight uncertainty-aware algorithmic framework, not yet a full system-level active-planning stack.

## 8. Conclusion

This paper presented an uncertainty-aware bearing-only passive localization framework for collaborative UAV sensing under degraded measurements. By combining multi-candidate geometric initialization, trimming-aware residual suppression, iterative reweighted refinement, and a credibility-guided measurement-selection layer, the method improves degraded-regime stability relative to least-squares baselines and outperforms simpler fixed-budget subset policies in the new benchmark. The experiments clarify that the strongest gains occur in outlier-rich and mixed regimes, where the risk of fusing unreliable bearings is highest, and that richer sensing geometry further amplifies those gains.

The work is best understood as a simulation-validated algorithmic framework rather than a complete active-sensing system. Its immediate value is to provide a reusable passive-localization baseline for uncertain observations, together with an honest benchmark that distinguishes robust estimation from measurement selection. Future work should extend the current one-shot selection stage toward sequential planning, richer uncertainty quantification, and hardware or replay-based validation.

## Figures and Tables

1. Figure 1. Regime comparison under clean, biased, missing, outlier, and mixed measurements. File: `submission/figures/figure_regime_comparison.png`
2. Figure 2. Mixed-regime ablation of the proposed robust framework. File: `submission/figures/figure_ablation_mixed.png`
3. Figure 3. Formation generalization across circular, elliptical, perturbed, and random swarm layouts. File: `submission/figures/figure_formation_generalization.png`
4. Figure 4. Implementation-cost comparison reported for completeness rather than as a primary claim. File: `submission/figures/figure_runtime_comparison.png`
5. Figure 5. Sensitivity sweeps over outlier rate, common bias, and nominal noise. File: `submission/figures/figure_sensitivity_sweep.png`
6. Figure 6. Sensor-count scaling under circular and random formations. File: `submission/figures/figure_scaling.png`
7. Figure 7. Observability versus error using oracle geometry isotropy for interpretation. File: `submission/figures/figure_observability.png`
8. Figure 8. Credibility-guided measurement-selection benchmark comparing all-sensor estimation, random subsets, angular-spread greedy selection, FIM/CRLB-greedy selection, and the proposed residual-aware observability policy. File: `submission/figures/figure_active_selection.png`

Tables are maintained in `submission/tables/tables_final.md` and `submission/tables/tables_final.tex`.
