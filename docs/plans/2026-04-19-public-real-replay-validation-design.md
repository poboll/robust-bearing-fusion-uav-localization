# 2026-04-19 Public Real Replay Validation Design

## Goal

Add one stronger validation layer that sits between synthetic replay and full SITL/HIL:

- public real-flight geometry
- measured multi-view visibility
- measured cross-camera asynchrony
- reproducible replay runner that fits the current manuscript pipeline

The chosen source is `drone-tracking-datasets` dataset 3. It is the most practical immediate option because it provides:

- surveyed observer locations
- manual detections per camera
- RTK trajectory
- synchronization parameters between camera streams

## Why This Layer

This is not a full onboard UAV field test and should not be described as one. The value is narrower and still important:

- it is stronger than purely synthetic or PyBullet-only evidence
- it uses real target motion and real observer geometry
- it introduces real visibility loss and measured cross-view timing mismatch
- it helps bound the paper honestly if the method is not universally dominant

## Technical Plan

1. Add `src/passive_localization/public_dataset_replay.py`.
2. Parse dataset metadata:
   - `campos.txt`
   - `rtk.txt`
   - `cam0.txt` to `cam5.txt`
   - synchronization tables from `README.md`
3. Build replay cases by:
   - sampling reference windows from camera 0
   - mapping each observer to asynchronous frames using `alpha` and `beta`
   - using zero detections as visibility dropouts
   - generating bearings from surveyed observer pose to asynchronous target location
   - injecting pose noise, common bias, per-sensor bias, nominal noise, and optional outliers
4. Add `run_public_dataset3_replay_validation.py`.
5. Save JSON outputs for results and serialized cases.
6. Add one publication figure and one LaTeX table.
7. Insert the layer into the MDPI manuscript before the PyBullet stress test.

## Expected Story

This layer should be written as:

"public real-flight trajectory replay with measured asynchrony and visibility masks"

It should not be written as:

- full field validation
- onboard UAV passive-bearing logs
- SITL or HIL
- proof of deployment readiness

The anticipated value is that the real replay will clarify whether the method suppresses extreme failures under a more realistic timing and visibility structure, even if another robust baseline remains stronger on central error.
