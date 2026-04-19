# SCI Strong Iteration Plan

Date: 2026-04-18

## 1. Current Status

### Already completed

- MDPI manuscript switched to the `Drones` configuration and recompiled successfully.
- Abstract reduced to `199` words.
- Body citation backbone expanded to `40` recent real references.
- Story reframed around:
  `robust inference + credibility-guided measurement management`
- Replay-validation interface added:
  [run_replay_validation.py](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/run_replay_validation.py)
- Example replay case added:
  [replay_case_example.json](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/experiments/examples/replay_case_example.json)

### Evidence already strong enough to use in the manuscript

- High-seed outlier validation:
  median error reduced from `2.1377` to `0.4123`; catastrophic failure rate reduced from `0.29` to `0.04`; sign test `83/17`, `p=1.31e-11`.
- High-seed mixed validation:
  median error reduced from `1.5501` to `0.6529`; catastrophic failure rate reduced from `0.23` to `0.04`; sign test `75/25`, `p=5.64e-07`.
- Fixed-budget subset benchmark:
  proposed median `0.4977`, all sensors `0.5510`, CRLB `0.5200`, spread `0.5676`, random `0.7491`.
- Fixed-budget success rate at error `<= 1.0`:
  proposed `0.8531`, CRLB `0.8298`, all sensors `0.7925`, spread `0.7343`, random `0.6200`.

## 2. Scientific Positioning

- `This is an algorithm, not a new model.`
- The standard bearing-only geometry is unchanged.
- The paper's novelty comes from:
  robust estimation under heterogeneous bearing quality,
  credibility-guided subset decision,
  and a cleaner operational boundary than "add another optimizer".

## 3. Journal Decision

### Best current order

1. `Drones`
2. `Sensors`

### Honest judgment

- A real SCI-direction submission is already defensible.
- A safer mid/high-tier result is realistic now.
- A harder Q1 outcome is still risky until replay or semi-real validation is added.

## 4. Next Execution Order

### Round 1: Finish the writing package

- Freeze the revised `Drones` manuscript as the new master version.
- Remove remaining low-signal wording in Results and Discussion.
- Finalize author metadata and confirm the CRediT statement with the authors.
- Sync the backup manuscript only after the MDPI version is stable.

### Round 2: Strengthen the evidence

- Use the new replay interface on real or semi-real logs.
- Minimum acceptable replay format:
  one target, at least three valid sensors, known sensor coordinates, known bearings, known target ground truth.
- Preferred first replay sources:
  real UAV logs converted to bearing-only measurements,
  vision/radio angle outputs with synchronized platform poses,
  or teacher-provided scenario records.
- Add one stronger modern comparison path if feasible:
  factor-graph or distributed cooperative baseline on the same replay cases.

### Round 3: Submission hardening

- Re-export figures at `600 dpi` for the final MDPI upload package.
- Finalize public repository or private-share statement.
- Update cover letter to match the `Drones` framing.
- Do one final human polish pass for language naturalness.

## 5. What Must Not Be Overclaimed

- Do not say the method universally beats all-sensor estimation.
- Do not say the paper already solves full swarm intelligence or full mission planning.
- Do not sell PSO/SA comparisons as the main frontier claim.
- Do not present synthetic validation as equivalent to field deployment.

## 6. Immediate Command for Replay Validation

```bash
conda run -n uu python run_replay_validation.py \
  experiments/examples/replay_case_example.json \
  --output experiments/replay_validation_result.json
```

This path has already been tested successfully in the current workspace.
