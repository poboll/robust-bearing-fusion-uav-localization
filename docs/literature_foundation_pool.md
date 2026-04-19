# Literature Foundation Pool

## A. Local 2022B Core Papers

### Main Skeleton
- `B263.pdf`: best candidate for a method mother paper.
- `B174.pdf`: strongest geometric ambiguity handling.
- `B49.pdf`: most complete localization-to-adjustment loop.
- `B42.pdf`: cleanest baseline formulation.
- `B257.pdf`: concise geometric initialization candidate.

### Method Support
- `B151.pdf`: optimization and correction loop.
- `B118.pdf`: 0-1 planning / scheduling style.
- `B144.pdf`: formation adjustment wording.
- `B31.pdf`: order and movement path logic.
- `B77.pdf`: Bayesian uncertainty framing.
- `B53.pdf`: iterative recovery ordering.

### Baselines Only
- `B95.pdf`, `B87.pdf`, `B35.pdf`, `B122.pdf`, `B178.pdf`, `B190.pdf`, `B213.pdf`, `B177.pdf`, `B88.pdf`

## B. Recent Frontiers (2025-2026)

- `Efficient Multi-Target Localization Using Dynamic UAV Clusters`
- `Theoretical Guarantees for AOA-based Localization: Consistency and Asymptotic Efficiency`
- `A Recursive Total Least Squares Solution for Bearing-Only Target Motion Analysis and Circumnavigation`
- `Aerial Shepherds: Enabling Hierarchical Localization in Heterogeneous MAV Swarms`
- `Bio-Inspired Observability Enhancement Method for UAV Target Localization and Sensor Bias Estimation with Bearing-Only Measurement`
- `Communication-Efficient Cooperative Localization: A Graph Neural Network Approach`
- `Adaptive Informative Path Planning Using Deep Reinforcement Learning for UAV-based Active Sensing`
- `A survey of sensors based autonomous UAV localization techniques`
- `Cooperative Relative Localization for UAV Swarm in GNSS-Denied Environment: A Coalition Formation Game Approach`
- `Passive Positioning and Adjustment Strategy for UAV Swarm Considering Formation Electromagnetic Compatibility`
- `UAV Swarm Autonomy through Cooperative Positioning: A Unified Approach with Distributed Graph Optimization and Decentralized MPC`
- `Low-Cost Real-Time Remote Sensing and Geolocation of Moving Targets via Monocular Bearing-Only Micro UAVs`

## C. What We Borrow

- Geometric initialization
- Bias-aware or uncertainty-aware refinement
- Observability-aware scheduling
- Cooperative localization / grouping / coalition ideas
- Active sensing / path planning
- Graph-based or factor-graph style organization
- Recursive TLS / consistency-aware localization thinking
- Robust evaluation under degraded measurements rather than only nominal accuracy

## D. What We Do Not Borrow

- New metaphor-based heuristics as the main contribution
- Purely static geometry without robustness
- Single-scenario toy experiments
- Unexplained algorithm stacking
- Overclaiming deep learning when the real contribution is robust geometric estimation
