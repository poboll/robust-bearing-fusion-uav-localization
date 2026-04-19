from dataclasses import dataclass


@dataclass
class ScenarioConfig:
    num_uavs: int = 6
    formation_radius: float = 10.0
    formation_type: str = "circle"
    formation_jitter: float = 0.0
    target_x: float = 2.5
    target_y: float = -1.5
    target_mode: str = "fixed"
    target_radius_min_frac: float = 0.10
    target_radius_max_frac: float = 0.45
    target_avoid_sensor_margin_frac: float = 0.18
    degenerate_arc_width_deg: float = 42.0
    degenerate_radial_jitter_frac: float = 0.08
    noise_std: float = 0.02
    bias: float = 0.0
    sensor_bias_std: float = 0.0
    missing_rate: float = 0.0
    outlier_rate: float = 0.0
    outlier_scale: float = 0.25
    pose_noise_std: float = 0.0
    seed: int = 42


@dataclass
class MethodConfig:
    robust_loss: str = "huber"
    scheduling_mode: str = "observability"
    recovery_mode: str = "greedy"
    ls_iterations: int = 60
    learning_rate: float = 0.12
    huber_delta: float = 0.08
    pso_particles: int = 32
    pso_iterations: int = 60
    sa_iterations: int = 300
    sa_step: float = 0.8
    # Robust estimation extensions
    estimate_bias: bool = True
    trim_ratio: float = 0.15  # fraction of measurements to trim as outliers (0.0-0.5)
    reweight_iterations: int = 3  # number of iterative reweighting passes
    min_weight: float = 0.01  # minimum measurement weight during reweighting
    bias_learning_rate: float = 0.05  # step size when jointly estimating a common bias
    lm_damping: float = 1e-3
    max_step_norm: float = 3.0
    tukey_c: float = 0.18
    ransac_iterations: int = 72
    ransac_inlier_threshold: float = 0.12
    # GNC-GM baseline
    gnc_outer_iterations: int = 8
    gnc_inner_iterations: int = 15
    gnc_mu_initial: float = 12.0
    gnc_mu_decay: float = 0.55
    gnc_floor_weight: float = 1e-3
