# Simulation Basis and Story Deepening Note

Date: 2026-04-18

## 1. What the Current Story Should Solve

This paper is not about inventing a new bearing-only model. It is about solving a failure mode in collaborative passive sensing:

- a UAV team already has one round of passive angular observations;
- those observations are not equally trustworthy;
- blindly fusing all of them can break localization;
- a lightweight inference layer is therefore needed before higher-level planning or consensus.

The real pain point is:

`bearing credibility is heterogeneous, but many pipelines still treat every available bearing as equally usable`

That is the story to keep pushing.

## 2. What the Current Simulation Actually Is

### Existing main benchmark

The current published benchmark is a **Monte Carlo single-cycle 2D passive-localization simulation**:

- one target position per run
- one bearing measurement per valid UAV
- formations: `circle`, `ellipse`, `perturbed`, `random`
- corruption types:
  common bias, nominal Gaussian noise, missing observations, gross outliers

### Core generation logic

Main source file:
- [scenario.py](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/src/passive_localization/scenario.py)

Main formula in code:

- true bearing from sensor to target
- observed bearing =
  true bearing + common bias + Gaussian noise + optional outlier
- invalid measurements are dropped by Bernoulli masking

This is a **controlled uncertainty-isolation benchmark**, not a flight-dynamics simulator.

## 3. Why This Simulation Is Still Useful

It is useful for an algorithm paper because it isolates exactly the variables the method is supposed to handle:

- corrupted bearings
- partial measurement loss
- poor geometry
- subset-selection decisions under a fixed sensing budget

It is *not* enough for a hard Q1 systems claim because it does not yet model:

- 6-DOF vehicle dynamics
- real camera or RF front-end physics
- communication topology and packet delay
- onboard time synchronization errors
- hardware runtime under real flight software stacks

## 4. What Has Been Added This Round

### Replay validation interface

Files:
- [replay.py](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/src/passive_localization/replay.py)
- [run_replay_validation.py](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/run_replay_validation.py)

Purpose:

- accept `.json`, `.jsonl`, or `.csv` bearing logs
- evaluate the current localization methods on real or semi-real cases
- save a unified result file for manuscript use

### Pseudo-physical dynamic extension

Files:
- [pseudo_physical.py](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/src/passive_localization/pseudo_physical.py)
- [run_pseudo_physical_validation.py](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/run_pseudo_physical_validation.py)

Purpose:

- inject tangential platform motion
- generate measurements from delayed positions
- inject per-sensor bias
- inject attitude-jitter-like angular disturbance
- retain missing observations and outliers

This is still synthetic, but it is a stronger intermediate step than static geometry-only Monte Carlo.

## 5. New Dynamic Validation Results

Output:
- [pseudo_physical_result.json](/Users/Apple/Developer/Pycharm/q/research/2026-04-17-b-passive-localization-sci/experiments/pseudo_physical_result.json)

Key outcomes:

- Mild dynamic regime:
  LS median `0.3050`, Robust-BT median `0.1485`
- Harsh dynamic regime:
  LS median `1.0411`, Robust-BT median `0.3862`
- Harsh dynamic success at error `<= 1.0`:
  LS `0.4889`, Robust-BT `0.9694`
- Harsh dynamic catastrophic failure:
  LS `0.1000`, Robust-BT `0.0000`

Interpretation:

- the current method is not only surviving a clean static intersection toy case;
- it also remains effective when timing and attitude disturbances are folded into the measurement stream.

## 6. Story Background and Application Scenario

The right application framing is:

- emission-controlled target localization
- low-signature collaborative observation
- edge-side fusion for one sensing cycle before a maneuver decision
- passive cue generation for larger autonomy pipelines

The wrong application framing is:

- full UAV swarm autonomy
- complete communication-aware distributed consensus
- field-proven autonomous flight stack

## 7. Skill and Software Status

### Installed and already used from the paper pipeline repo

- `literature-engineer`
- `citation-verifier`
- `manuscript-ingest`
- `paper-notes`
- `novelty-matrix`
- `front-matter-writer`
- `draft-polisher`
- `survey-visuals`
- `latex-compile-qa`
- `research-pipeline-runner`

### About the other skill repo

The `Awesome-Scientific-Skills` repository is not an installable skill package in the same sense; it is mainly a curated collection, so it was reviewed but not installed as an executable local skill bundle.

### Current simulation software availability

Checked locally on this machine:

- `gazebo`: not installed
- `gz`: not installed
- `ros2`: not installed

So at this moment I can honestly claim:

- manuscript-level simulation and replay validation: yes
- pseudo-physical dynamic validation: yes
- ROS/Gazebo high-fidelity physics: not yet

## 8. Recommended Next Simulation Step

Best next move:

1. obtain real or semi-real bearing logs from your teacher or your own sensors
2. convert them into the replay schema already supported
3. run:

```bash
conda run -n uu python run_replay_validation.py <your_file>.json
```

If no real data arrives immediately, the next-best move is:

1. install a UAV-oriented simulator stack
2. generate pose and timing traces there
3. convert those traces into replay cases for the current estimator

## 9. Honest Submission Judgment

After this round, the manuscript is stronger in three concrete ways:

- the story is more operational and less template-like
- the simulation basis is now explicit instead of vague
- there is already a dynamic pseudo-physical bridge toward stronger validation

But the honest ceiling remains:

- `Drones` / `Sensors`: realistic if polished well
- harder Q1: still depends on replay, MIL/HIL, or field evidence
