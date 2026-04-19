# Review and Reframing Notes

## 1. What This Paper Actually Is

This work is best described as an `algorithmic framework`, not a new physical model and not a full swarm system.

- Core component: a geometry-preserving robust passive bearing-only localization algorithm.
- Decision component: a one-shot active measurement-selection layer that ranks candidate bearing subsets by observability and residual credibility.
- Validation scope: simulation-based robustness benchmarking under uncertain measurements.

Practical wording for the manuscript:

`This paper studies uncertainty-aware passive bearing localization for collaborative UAV sensing, with emphasis on corrupted, missing, and reliability-varying bearings.`

## 2. The Real Problem Worth Publishing

The paper should not be sold as “another localization optimizer”.

The real pain point is:

- In GNSS-denied or electromagnetically silent operations, UAV teams may only have passive bearing observations.
- In that setting, not every received bearing is equally trustworthy.
- Small bias, partial occlusion, emitter uncertainty, or gross corruption can make all-measurement fusion unstable.
- Operators need a lightweight method that still works when observations are incomplete, biased, or partially wrong.

So the publishable problem is not just `where is the target?`

It is:

`How can a collaborative UAV team obtain a stable passive location estimate when the available bearings are uncertain, partially corrupted, and not all worth trusting equally?`

## 3. Why the Current Draft Feels “虚”

The previous version had several expression-level issues even though experiments already existed.

### 3.1 Title and abstract were algorithm-name first

- The old title foregrounded `observability-guided active robust...` before clearly stating the application problem.
- The abstract framed the work as a strong upgrade, but did not explain why measurement selection matters in a real passive sensing workflow.

### 3.2 Introduction did not fully anchor the pain point

- It mentioned GNSS denial and electromagnetic silence, but did not explicitly say that `using all bearings can be harmful when some bearings are corrupted`.
- The “why now” paragraph mixed too many research directions together without stating the exact gap.

### 3.3 The active layer was slightly overclaimed

- The active-selection benchmark is real and useful.
- But it does **not** dominate all-sensor robust estimation in paired comparisons.
- Therefore, the correct claim is:
  `selection is helpful under uncertain measurement credibility or budgeted sensing`,
  not
  `selection is universally better than using all available measurements`.

### 3.4 Runtime had too much visibility

- Runtime data can be kept for completeness.
- But it should not be part of the main sales pitch.
- The paper is about robustness under uncertainty, not latency reduction.

## 4. Recent Literature and the Right Gap

The current topic is still active, but the frontier has shifted.

### 4.1 What recent papers are doing

1. `Trajectory / observability optimization`
   - Peng et al., 2024, *Biomimetics*, DOI: `10.3390/biomimetics9090510`
   - Wang et al., 2025, *Biomimetics*, DOI: `10.3390/biomimetics10050336`
   - These papers optimize motion or observability for better bearing-only localization, often assuming a controllable trajectory-planning loop.

2. `Passive localization in electromagnetically silent UAV formations`
   - Li et al., 2025, *Drones*, DOI: `10.3390/drones9110767`
   - This line confirms that pure bearing-only passive localization is still relevant in UAV scenarios with electromagnetic silence.

3. `System-level cooperative localization with stronger fusion`
   - Yang et al., 2024, *Measurement Science and Technology*, DOI: `10.1088/1361-6501/ad91d6`
   - Li et al., 2026, *Sensors*, DOI: `10.3390/s26061984`
   - These papers move toward distributed graph optimization or formation-constrained cooperative localization.

4. `Information-driven / optimization-oriented swarm localization`
   - Zhou et al., 2026, *Ad Hoc Networks*, DOI: `10.1016/j.adhoc.2026.104154`
   - This suggests the frontier increasingly values information utility and system-level decision design, not only closed-form estimation.

### 4.2 Where this paper can still stand

This paper should occupy a narrower, honest, and still useful slot:

- not full trajectory planning,
- not factor-graph cooperative inference,
- not reinforcement-learning swarm control,
- but a reproducible `robust passive localization + measurement triage` framework for uncertain bearings.

That gap is still defensible because the recent papers above mostly emphasize:

- trajectory optimization,
- formation priors,
- graph/distributed fusion,
- or system-level cooperative optimization,

whereas the present work focuses on:

- corrupted bearing handling,
- explicit failure control,
- and one-shot measurement credibility selection inside a lightweight passive pipeline.

## 5. Is There Real Increment Over Existing Work?

Yes, but the increment is `moderate and practical`, not `revolutionary`.

### What is genuinely new enough here

- A robust geometric localization core that behaves much better than least squares under outliers and mixed corruption.
- A residual-aware measurement-selection layer that is more realistic than pure geometry-only subset choice.
- A benchmark centered on uncertainty regimes rather than nominal-noise-only evaluation.

### What is not new enough to claim

- Not a new observability theory.
- Not a full active-sensing or trajectory-planning framework.
- Not a universal improvement over graph-based or full-information systems.

## 6. How the Story Should Be Told

Recommended story order:

1. `Application need`
   - GNSS-denied, low-emission, uncertainty-heavy collaborative sensing.

2. `Failure mode`
   - Bearing-only passive localization is attractive, but fragile when some bearings are biased, missing, or unreliable.

3. `Literature gap`
   - Existing works either optimize trajectories / graph fusion at a higher system level, or study passive localization without focusing on corrupted-measurement triage.

4. `Our response`
   - Build a lightweight algorithmic framework that first stabilizes estimation, then actively selects more credible and informative bearings.

5. `What the experiments actually prove`
   - Strong gains over least squares in outlier-rich and mixed settings.
   - Useful but not universal gains from measurement selection.

6. `Boundary`
   - Simulation only, 2D only, one-shot selection only, no sequential planning or field data.

## 7. Recommended Manuscript Positioning

### Best concise title direction

`Uncertainty-Aware Bearing-Only Passive Localization with Credibility-Guided Measurement Selection for Collaborative UAV Sensing`

### Best one-sentence positioning

`A simulation-validated algorithmic framework for robust passive bearing localization under uncertain measurements, with a lightweight measurement-selection module for cases where not all bearings should be trusted equally.`

## 8. SCI Readiness Judgment

### Current scientific level

- `Enough for SCI direction`: yes, after rewriting and tightening claims.
- `Enough for a safe Q1 promise`: no.
- `Enough for a serious mid-tier SCI submission`: yes.

### Why it can still be submitted

- Recent relevant literature exists and is active.
- The task is application-grounded.
- The experiments are broader than a contest extension.
- The paper has a clear algorithmic contribution if written honestly.

### What still limits a stronger venue

- no real-data or hardware validation,
- no sequential planning,
- no full cooperative state-estimation stack,
- and no learned component or stronger uncertainty quantification yet.

## 9. Concrete Revision Rules Applied to the Main Draft

The manuscript should be revised to satisfy the following rules:

1. Put `uncertain measurements` before `algorithm branding`.
2. Explicitly state that some bearings should be down-weighted or discarded.
3. Treat the active layer as `measurement triage`, not a universal victory over all-sensor fusion.
4. Downplay runtime.
5. Use restrained conclusions and clear limitations.
6. Add author information and journal-style section transitions.

## 10. Source Notes

Key source pages checked in this revision:

- Li et al., 2025, *Drones*: https://www.mdpi.com/2504-446X/9/11/767
- Peng et al., 2024, *Biomimetics*: https://www.mdpi.com/2313-7673/9/9/510
- Wang et al., 2025, *Biomimetics* (PMC full text): https://pmc.ncbi.nlm.nih.gov/articles/PMC12109225/
- Li et al., 2026, *Sensors*: https://www.mdpi.com/1424-8220/26/6/1984
- Yang et al., 2024, *Measurement Science and Technology*: https://iopscience.iop.org/article/10.1088/1361-6501/ad91d6

These sources were used to confirm that:

- passive UAV localization under electromagnetic silence remains current,
- observability/trajectory optimization is a frontier direction,
- cooperative graph-based or formation-constrained localization is also active,
- and therefore this paper must position itself as a lighter uncertainty-aware algorithmic contribution rather than a full system-level breakthrough.
