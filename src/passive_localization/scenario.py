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


def _generate_target(config: ScenarioConfig, rng: np.random.Generator, coords: list[tuple[float, float]]) -> Point2D:
    if config.target_mode == "fixed":
        return Point2D(config.target_x, config.target_y)
    if config.target_mode != "random_interior":
        raise ValueError(f"Unsupported target_mode: {config.target_mode}")

    radius = float(config.formation_radius)
    min_r = max(0.0, config.target_radius_min_frac * radius)
    max_r = max(min_r + 1e-6, config.target_radius_max_frac * radius)
    sensor_xy = np.asarray(coords, dtype=float)
    min_sensor_gap = max(0.5, config.target_avoid_sensor_margin_frac * radius)

    for _ in range(256):
        theta = float(rng.uniform(-np.pi, np.pi))
        sampled_r = float(rng.uniform(min_r, max_r))
        candidate = np.array([sampled_r * np.cos(theta), sampled_r * np.sin(theta)], dtype=float)
        if sensor_xy.size == 0:
            return Point2D(float(candidate[0]), float(candidate[1]))
        dists = np.linalg.norm(sensor_xy - candidate[None, :], axis=1)
        if float(np.min(dists)) >= min_sensor_gap:
            return Point2D(float(candidate[0]), float(candidate[1]))

    fallback = np.array([config.target_x, config.target_y], dtype=float)
    return Point2D(float(fallback[0]), float(fallback[1]))


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
    elif config.formation_type == "degenerate":
        center_angle = float(rng.uniform(-np.pi, np.pi))
        half_width = 0.5 * np.deg2rad(config.degenerate_arc_width_deg)
        arc = np.linspace(-half_width, half_width, config.num_uavs)
        coords = []
        for delta in arc:
            theta = center_angle + float(delta) + float(rng.normal(0.0, 0.03))
            radius = config.formation_radius * (
                1.0 + float(rng.normal(0.0, max(config.degenerate_radial_jitter_frac, 1e-3)))
            )
            coords.append((float(radius * np.cos(theta)), float(radius * np.sin(theta))))
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
    target = _generate_target(config, rng, coords)
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
