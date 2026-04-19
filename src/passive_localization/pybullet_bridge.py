from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pybullet as p
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl
from gym_pybullet_drones.envs.CtrlAviary import CtrlAviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics

from .geometry import Point2D, Sensor2D, bearing_from_sensor, wrap_angle
from .replay import ReplayCase, ReplayMeasurement


@dataclass
class PyBulletReplayConfig:
    num_uavs: int = 8
    formation_type: str = "circle"
    formation_radius: float = 0.9
    target_x: float = 0.28
    target_y: float = -0.22
    position_scale: float = 14.0
    altitude_base: float = 0.95
    altitude_step: float = 0.04
    orbit_period: float = 6.0
    duration_sec: float = 8.0
    warmup_sec: float = 2.0
    sample_every: int = 3
    sim_freq_hz: int = 240
    control_freq_hz: int = 48
    physics: Physics = Physics.PYB_GND_DRAG_DW
    common_bias: float = 0.010
    bias_drift: float = 0.004
    noise_std: float = 0.010
    attitude_gain: float = 0.20
    yaw_rate_gain: float = 0.012
    delay_steps_mean: float = 1.2
    delay_steps_std: float = 0.5
    missing_rate: float = 0.04
    outlier_rate: float = 0.05
    outlier_scale: float = 0.22
    gust_force_std: float = 0.0
    gust_probability: float = 0.0
    gust_interval_steps: int = 5
    seed: int = 0


def _formation_axes(config: PyBulletReplayConfig) -> tuple[float, float]:
    if config.formation_type == "circle":
        return config.formation_radius, config.formation_radius
    if config.formation_type == "ellipse":
        return 1.28 * config.formation_radius, 0.78 * config.formation_radius
    if config.formation_type == "perturbed":
        return config.formation_radius, config.formation_radius
    raise ValueError(f"Unsupported formation type: {config.formation_type}")


def _fixed_offsets(config: PyBulletReplayConfig, rng: np.random.Generator) -> np.ndarray:
    if config.formation_type != "perturbed":
        return np.zeros((config.num_uavs, 2), dtype=float)
    return rng.normal(0.0, 0.08, size=(config.num_uavs, 2))


def _desired_positions(
    config: PyBulletReplayConfig,
    t: float,
    phases: np.ndarray,
    offsets: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    ax_x, ax_y = _formation_axes(config)
    theta = 2.0 * np.pi * t / max(config.orbit_period, 1e-6) + phases
    positions = np.zeros((config.num_uavs, 3), dtype=float)
    positions[:, 0] = ax_x * np.cos(theta) + offsets[:, 0]
    positions[:, 1] = ax_y * np.sin(theta) + offsets[:, 1]
    positions[:, 2] = config.altitude_base + config.altitude_step * ((np.arange(config.num_uavs) % 3) - 1)
    desired_yaw = wrap_angle(theta + np.pi / 2.0)
    return positions, np.asarray(desired_yaw, dtype=float)


def _apply_gusts(env: CtrlAviary, config: PyBulletReplayConfig, rng: np.random.Generator, step: int) -> None:
    if config.gust_force_std <= 0.0 or config.gust_probability <= 0.0:
        return
    if step % max(config.gust_interval_steps, 1) != 0:
        return
    client = env.getPyBulletClient()
    drone_ids = env.getDroneIds()
    for idx, drone_id in enumerate(drone_ids):
        if rng.random() >= config.gust_probability:
            continue
        lateral = rng.normal(0.0, config.gust_force_std, size=2)
        vertical = abs(rng.normal(0.0, 0.20 * config.gust_force_std))
        p.applyExternalForce(
            int(drone_id),
            4,
            forceObj=[float(lateral[0]), float(lateral[1]), float(vertical)],
            posObj=[0.0, 0.0, 0.0],
            flags=p.WORLD_FRAME,
            physicsClientId=client,
        )


def _tilt_and_speed_terms(state: np.ndarray) -> tuple[float, float]:
    roll, pitch = float(state[7]), float(state[8])
    speed = float(np.linalg.norm(state[10:12]))
    tilt = float(np.hypot(roll, pitch))
    return tilt, speed


def generate_pybullet_replay_cases(
    config: PyBulletReplayConfig,
    case_prefix: str | None = None,
) -> tuple[list[ReplayCase], dict[str, Any]]:
    rng = np.random.default_rng(config.seed)
    phases = np.linspace(0.0, 2.0 * np.pi, config.num_uavs, endpoint=False)
    offsets = _fixed_offsets(config, rng)
    initial_xyzs, initial_yaws = _desired_positions(config, 0.0, phases, offsets)
    initial_rpys = np.column_stack((np.zeros(config.num_uavs), np.zeros(config.num_uavs), initial_yaws))

    env = CtrlAviary(
        drone_model=DroneModel.CF2X,
        num_drones=config.num_uavs,
        initial_xyzs=initial_xyzs,
        initial_rpys=initial_rpys,
        physics=config.physics,
        neighbourhood_radius=10.0,
        pyb_freq=config.sim_freq_hz,
        ctrl_freq=config.control_freq_hz,
        gui=False,
        record=False,
        obstacles=False,
        user_debug_gui=False,
    )
    controllers = [DSLPIDControl(drone_model=DroneModel.CF2X) for _ in range(config.num_uavs)]

    total_steps = int(round(config.duration_sec * config.control_freq_hz))
    action = np.zeros((config.num_uavs, 4), dtype=float)
    state_history: list[np.ndarray] = []
    time_history: list[float] = []

    for step in range(total_steps):
        obs, _, _, _, _ = env.step(action)
        state_history.append(np.asarray(obs, dtype=float).copy())
        time_history.append(step / config.control_freq_hz)

        _apply_gusts(env, config, rng, step)
        desired_pos, desired_yaw = _desired_positions(config, (step + 1) / config.control_freq_hz, phases, offsets)
        for drone_idx in range(config.num_uavs):
            action[drone_idx, :], _, _ = controllers[drone_idx].computeControlFromState(
                control_timestep=env.CTRL_TIMESTEP,
                state=obs[drone_idx],
                target_pos=desired_pos[drone_idx],
                target_rpy=np.array([0.0, 0.0, desired_yaw[drone_idx]], dtype=float),
            )

    env.close()

    states = np.asarray(state_history, dtype=float)
    scaled_target = Point2D(config.position_scale * config.target_x, config.position_scale * config.target_y)
    warmup_steps = int(round(config.warmup_sec * config.control_freq_hz))
    cases: list[ReplayCase] = []

    for step in range(max(warmup_steps, 2), total_steps, max(config.sample_every, 1)):
        common_bias = config.common_bias + config.bias_drift * np.sin(
            2.0 * np.pi * time_history[step] / max(config.orbit_period, 1e-6) + 0.13 * config.seed
        )
        measurements: list[ReplayMeasurement] = []
        measurement_meta: list[dict[str, Any]] = []
        valid_count = 0

        for drone_idx in range(config.num_uavs):
            current_state = states[step, drone_idx]
            delay_steps = int(max(0, round(rng.normal(config.delay_steps_mean, config.delay_steps_std))))
            source_step = max(0, step - delay_steps)
            source_state = states[source_step, drone_idx]

            current_xy = config.position_scale * current_state[0:2]
            delayed_xy = config.position_scale * source_state[0:2]
            sensor = Sensor2D(float(current_xy[0]), float(current_xy[1]), name=f"uav_{drone_idx}")
            delayed_sensor = Sensor2D(float(delayed_xy[0]), float(delayed_xy[1]), name=f"uav_{drone_idx}_delayed")

            base_bearing = bearing_from_sensor(delayed_sensor, scaled_target)
            roll, pitch = float(source_state[7]), float(source_state[8])
            yaw_rate = float(source_state[15])
            attitude_term = config.attitude_gain * (0.65 * roll + 0.65 * pitch) + config.yaw_rate_gain * yaw_rate
            tilt, speed = _tilt_and_speed_terms(source_state)

            missing_prob = min(0.85, config.missing_rate + 0.18 * max(0.0, tilt - 0.10) + 0.05 * max(0.0, speed - 0.35))
            outlier_prob = min(0.85, config.outlier_rate + 0.20 * max(0.0, tilt - 0.12) + 0.08 * max(0.0, speed - 0.45))
            is_outlier = bool(rng.random() < outlier_prob)
            valid = bool(rng.random() >= missing_prob)
            nominal_noise = float(rng.normal(0.0, config.noise_std))
            outlier_noise = float(rng.normal(0.0, config.outlier_scale)) if is_outlier else 0.0
            measured_bearing = float(wrap_angle(base_bearing + common_bias + attitude_term + nominal_noise + outlier_noise))

            measurements.append(ReplayMeasurement(sensor=sensor, bearing=measured_bearing, valid=valid))
            measurement_meta.append(
                {
                    "name": sensor.name,
                    "step": step,
                    "delay_steps": delay_steps,
                    "roll": roll,
                    "pitch": pitch,
                    "yaw_rate": yaw_rate,
                    "tilt": tilt,
                    "speed_xy": speed,
                    "attitude_term": attitude_term,
                    "outlier": is_outlier,
                    "valid": valid,
                }
            )
            if valid:
                valid_count += 1

        if valid_count < 3:
            continue

        case_id = f"{case_prefix or 'pybullet'}_{config.formation_type}_{config.num_uavs}_{config.seed:03d}_{step:04d}"
        cases.append(
            ReplayCase(
                case_id=case_id,
                target=scaled_target,
                measurements=measurements,
                seed=config.seed,
                meta={
                    "source": "gym-pybullet-drones",
                    "formation_type": config.formation_type,
                    "num_uavs": config.num_uavs,
                    "time_s": float(time_history[step]),
                    "common_bias": float(common_bias),
                    "position_scale": config.position_scale,
                    "measurement_meta": measurement_meta,
                },
            )
        )

    trace = {
        "meta": {
            "source": "gym-pybullet-drones",
            "formation_type": config.formation_type,
            "num_uavs": config.num_uavs,
            "seed": config.seed,
            "target": {"x": float(scaled_target.x), "y": float(scaled_target.y)},
            "position_scale": config.position_scale,
        },
        "time_s": [float(value) for value in time_history],
        "drones": [
            {
                "name": f"uav_{drone_idx}",
                "x": [float(config.position_scale * value) for value in states[:, drone_idx, 0]],
                "y": [float(config.position_scale * value) for value in states[:, drone_idx, 1]],
            }
            for drone_idx in range(config.num_uavs)
        ],
    }
    return cases, trace
