from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .geometry import Point2D, Sensor2D, bearing_from_sensor, wrap_angle
from .replay import ReplayCase, ReplayMeasurement


@dataclass
class PseudoPhysicalConfig:
    num_uavs: int = 8
    formation_radius: float = 10.0
    formation_type: str = "circle"
    formation_jitter: float = 0.0
    target_x: float = 2.5
    target_y: float = -1.5
    speed: float = 1.8
    noise_std: float = 0.012
    common_bias: float = 0.015
    sensor_bias_std: float = 0.01
    attitude_jitter_std: float = 0.02
    delay_mean: float = 0.18
    delay_jitter: float = 0.07
    missing_rate: float = 0.08
    outlier_rate: float = 0.08
    outlier_scale: float = 0.35
    seed: int = 0


def _formation_coords(config: PseudoPhysicalConfig, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    angles = np.linspace(0.0, 2.0 * np.pi, config.num_uavs, endpoint=False)
    if config.formation_type == "circle":
        coords = np.column_stack(
            (
                config.formation_radius * np.cos(angles),
                config.formation_radius * np.sin(angles),
            )
        )
    elif config.formation_type == "ellipse":
        coords = np.column_stack(
            (
                1.35 * config.formation_radius * np.cos(angles),
                0.75 * config.formation_radius * np.sin(angles),
            )
        )
    elif config.formation_type == "perturbed":
        coords = np.column_stack(
            (
                config.formation_radius * np.cos(angles),
                config.formation_radius * np.sin(angles),
            )
        )
        coords += rng.normal(0.0, max(config.formation_jitter, 0.8), size=coords.shape)
    elif config.formation_type == "random":
        raw = rng.normal(0.0, 1.0, size=(config.num_uavs, 2))
        norms = np.linalg.norm(raw, axis=1, keepdims=True)
        raw = raw / np.maximum(norms, 1e-6)
        radii = rng.uniform(0.6 * config.formation_radius, 1.25 * config.formation_radius, size=(config.num_uavs, 1))
        coords = raw * radii
        angles = np.arctan2(coords[:, 1], coords[:, 0])
    else:
        raise ValueError(f"Unsupported formation type: {config.formation_type}")
    return coords.astype(float), angles.astype(float)


def generate_pseudo_physical_case(config: PseudoPhysicalConfig, case_id: str | None = None) -> ReplayCase:
    rng = np.random.default_rng(config.seed)
    coords, angles = _formation_coords(config, rng)
    target = Point2D(config.target_x, config.target_y)

    tangential = np.column_stack((-np.sin(angles), np.cos(angles)))
    tangential += rng.normal(0.0, 0.08, size=tangential.shape)
    tangential /= np.maximum(np.linalg.norm(tangential, axis=1, keepdims=True), 1e-6)
    velocities = config.speed * tangential

    delays = np.maximum(0.0, rng.normal(config.delay_mean, config.delay_jitter, size=config.num_uavs))
    measurement_positions = coords - velocities * delays[:, None]
    common_bias = config.common_bias + rng.normal(0.0, 0.003)
    sensor_bias = rng.normal(0.0, config.sensor_bias_std, size=config.num_uavs)
    attitude_jitter = rng.normal(0.0, config.attitude_jitter_std, size=config.num_uavs)
    nominal_noise = rng.normal(0.0, config.noise_std, size=config.num_uavs)
    outlier_mask = rng.random(config.num_uavs) < config.outlier_rate
    outlier_noise = np.zeros(config.num_uavs, dtype=float)
    outlier_noise[outlier_mask] = rng.normal(0.0, config.outlier_scale, size=int(np.sum(outlier_mask)))
    valid_mask = rng.random(config.num_uavs) >= config.missing_rate

    measurements: list[ReplayMeasurement] = []
    meta_measurements: list[dict[str, float | bool | str]] = []
    for idx in range(config.num_uavs):
        sensor = Sensor2D(float(coords[idx, 0]), float(coords[idx, 1]), name=f"uav_{idx}")
        delayed_sensor = Sensor2D(float(measurement_positions[idx, 0]), float(measurement_positions[idx, 1]), name=f"uav_{idx}_delayed")
        bearing = bearing_from_sensor(delayed_sensor, target)
        observed = float(
            wrap_angle(
                bearing
                + common_bias
                + sensor_bias[idx]
                + attitude_jitter[idx]
                + nominal_noise[idx]
                + outlier_noise[idx]
            )
        )
        measurements.append(ReplayMeasurement(sensor=sensor, bearing=observed, valid=bool(valid_mask[idx])))
        meta_measurements.append(
            {
                "name": sensor.name,
                "delay_s": float(delays[idx]),
                "velocity_x": float(velocities[idx, 0]),
                "velocity_y": float(velocities[idx, 1]),
                "sensor_bias": float(sensor_bias[idx]),
                "attitude_jitter": float(attitude_jitter[idx]),
                "is_outlier": bool(outlier_mask[idx]),
                "valid": bool(valid_mask[idx]),
            }
        )

    return ReplayCase(
        case_id=case_id or f"pseudo_{config.seed:04d}",
        target=target,
        measurements=measurements,
        seed=config.seed,
        meta={
            "formation_type": config.formation_type,
            "formation_radius": config.formation_radius,
            "speed": config.speed,
            "common_bias": float(common_bias),
            "noise_std": config.noise_std,
            "sensor_bias_std": config.sensor_bias_std,
            "attitude_jitter_std": config.attitude_jitter_std,
            "delay_mean": config.delay_mean,
            "delay_jitter": config.delay_jitter,
            "missing_rate": config.missing_rate,
            "outlier_rate": config.outlier_rate,
            "outlier_scale": config.outlier_scale,
            "measurements": meta_measurements,
        },
    )


def generate_case_grid(
    seeds: list[int],
    regimes: dict[str, dict],
    formations: list[str],
    counts: list[int],
) -> dict[str, list[ReplayCase]]:
    payload: dict[str, list[ReplayCase]] = {}
    for regime_name, regime_kwargs in regimes.items():
        rows: list[ReplayCase] = []
        for formation in formations:
            for count in counts:
                for seed in seeds:
                    cfg = PseudoPhysicalConfig(
                        seed=seed,
                        num_uavs=count,
                        formation_type=formation,
                        formation_jitter=1.1 if formation == "perturbed" else 0.0,
                        **regime_kwargs,
                    )
                    rows.append(generate_pseudo_physical_case(cfg, case_id=f"{regime_name}_{formation}_{count}_{seed:03d}"))
        payload[regime_name] = rows
    return payload
