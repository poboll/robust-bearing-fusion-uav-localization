from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import ScenarioConfig
from .geometry import Point2D, Sensor2D, bearing_from_sensor, wrap_angle


@dataclass
class ScenarioData:
    sensors: list[Sensor2D]
    true_sensors: list[Sensor2D]
    target: Point2D
    true_bearings: np.ndarray
    observed_bearings: np.ndarray
    valid_mask: np.ndarray
    sensor_biases: np.ndarray | None = None
    pose_errors: np.ndarray | None = None


def generate_circular_scenario(config: ScenarioConfig) -> ScenarioData:
    rng = np.random.default_rng(config.seed)
    angles = np.linspace(0.0, 2.0 * np.pi, config.num_uavs, endpoint=False)
    sensors: list[Sensor2D] = []
    if config.formation_type == "circle":
        coords = [(config.formation_radius * np.cos(theta), config.formation_radius * np.sin(theta)) for theta in angles]
    elif config.formation_type == "ellipse":
        coords = [(1.35 * config.formation_radius * np.cos(theta), 0.75 * config.formation_radius * np.sin(theta)) for theta in angles]
    elif config.formation_type == "perturbed":
        coords = []
        for theta in angles:
            base = np.array([config.formation_radius * np.cos(theta), config.formation_radius * np.sin(theta)], dtype=float)
            base += rng.normal(0.0, max(config.formation_jitter, 0.8), size=2)
            coords.append((float(base[0]), float(base[1])))
    elif config.formation_type == "random":
        raw = rng.normal(0.0, 1.0, size=(config.num_uavs, 2))
        norms = np.linalg.norm(raw, axis=1, keepdims=True)
        raw = raw / np.maximum(norms, 1e-6)
        radii = rng.uniform(0.6 * config.formation_radius, 1.2 * config.formation_radius, size=(config.num_uavs, 1))
        pts = raw * radii
        coords = [(float(x), float(y)) for x, y in pts]
    else:
        raise ValueError(f"Unsupported formation_type: {config.formation_type}")

    true_sensors = [
        Sensor2D(
            x=float(x),
            y=float(y),
            name=f"uav_{idx}",
        )
        for idx, (x, y) in enumerate(coords)
    ]
    pose_noise = rng.normal(0.0, config.pose_noise_std, size=(config.num_uavs, 2))
    reported_coords = np.asarray(coords, dtype=float) + pose_noise
    sensors = [
        Sensor2D(
            x=float(x),
            y=float(y),
            name=f"uav_{idx}",
        )
        for idx, (x, y) in enumerate(reported_coords)
    ]
    target = Point2D(config.target_x, config.target_y)
    true_bearings = np.array([bearing_from_sensor(sensor, target) for sensor in true_sensors], dtype=float)

    sensor_biases = rng.normal(0.0, config.sensor_bias_std, size=true_bearings.shape)
    observed = true_bearings + config.bias + sensor_biases + rng.normal(0.0, config.noise_std, size=true_bearings.shape)

    outlier_mask = rng.random(config.num_uavs) < config.outlier_rate
    observed[outlier_mask] += rng.normal(0.0, config.outlier_scale, size=outlier_mask.sum())

    valid_mask = rng.random(config.num_uavs) >= config.missing_rate
    observed = wrap_angle(observed)
    observed[~valid_mask] = np.nan

    return ScenarioData(
        sensors=sensors,
        true_sensors=true_sensors,
        target=target,
        true_bearings=true_bearings,
        observed_bearings=observed,
        valid_mask=valid_mask,
        sensor_biases=sensor_biases,
        pose_errors=np.linalg.norm(pose_noise, axis=1),
    )
