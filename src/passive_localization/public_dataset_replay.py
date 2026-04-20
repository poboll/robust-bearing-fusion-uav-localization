from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .geometry import Point2D, Sensor2D, bearing_from_sensor, wrap_angle
from .replay import ReplayCase, ReplayMeasurement


@dataclass(frozen=True)
class PublicDatasetReplayRegime:
    noise_std: float
    common_bias: float
    sensor_bias_std: float
    outlier_rate: float
    outlier_scale: float
    pose_noise_std: float
    extra_time_jitter: float


@dataclass
class PublicDataset3ReplayConfig:
    dataset_root: str | Path = "data/public_dataset3"
    reference_camera: int = 0
    sample_count: int = 450
    seed: int = 0
    ready_threshold_m: float = 20.0
    extreme_threshold_m: float = 80.0


def _load_sync_table(readme_lines: list[str], title: str) -> np.ndarray:
    idx = next(i for i, line in enumerate(readme_lines) if line.strip() == title)
    rows: list[list[float]] = []
    for line in readme_lines[idx + 3 : idx + 9]:
        parts = [part.strip() for part in line.split("|")][1:7]
        rows.append([float(value) for value in parts])
    return np.asarray(rows, dtype=float)


def _load_detection(path: Path) -> np.ndarray:
    return np.loadtxt(path, skiprows=1)


def load_public_dataset3_assets(dataset_root: str | Path) -> dict[str, Any]:
    dataset_root = Path(dataset_root)
    readme_lines = (dataset_root / "README.md").read_text(encoding="utf-8").splitlines()
    cameras = [line.split("-", 1)[1].strip() for line in (dataset_root / "cameras.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
    camera_positions = np.loadtxt(dataset_root / "campos.txt", dtype=float)
    trajectory = np.loadtxt(dataset_root / "rtk.txt", dtype=float)
    detections = {cam_idx: _load_detection(dataset_root / f"cam{cam_idx}.txt") for cam_idx in range(len(cameras))}
    alpha = _load_sync_table(readme_lines, "### Time scale (alpha)")
    beta = _load_sync_table(readme_lines, "### Time shift (beta)")
    visibility_rates = {
        f"cam{cam_idx}": float(
            np.mean(
                np.logical_not(
                    np.logical_and(
                        np.isclose(detections[cam_idx][:, 1], 0.0),
                        np.isclose(detections[cam_idx][:, 2], 0.0),
                    )
                )
            )
        )
        for cam_idx in detections
    }
    return {
        "dataset_root": str(dataset_root),
        "camera_names": cameras,
        "camera_positions": camera_positions,
        "trajectory": trajectory,
        "detections": detections,
        "alpha": alpha,
        "beta": beta,
        "visibility_rates": visibility_rates,
    }


def _serialize_case(case: ReplayCase) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "seed": case.seed,
        "target": {"x": case.target.x, "y": case.target.y},
        "meta": case.meta or {},
        "measurements": [
            {
                "name": measurement.sensor.name,
                "x": measurement.sensor.x,
                "y": measurement.sensor.y,
                "bearing": measurement.bearing,
                "valid": measurement.valid,
            }
            for measurement in case.measurements
        ],
    }


def serialize_case_grid(case_grid: dict[str, list[ReplayCase]]) -> dict[str, Any]:
    return {
        regime_name: [_serialize_case(case) for case in cases]
        for regime_name, cases in case_grid.items()
    }


def generate_public_dataset3_case_grid(
    regimes: dict[str, PublicDatasetReplayRegime],
    config: PublicDataset3ReplayConfig | None = None,
) -> tuple[dict[str, list[ReplayCase]], dict[str, Any]]:
    config = config or PublicDataset3ReplayConfig()
    assets = load_public_dataset3_assets(config.dataset_root)
    rng = np.random.default_rng(config.seed)

    detections = assets["detections"]
    trajectory = assets["trajectory"]
    camera_positions = assets["camera_positions"]
    alpha = assets["alpha"]
    beta = assets["beta"]
    reference_camera = int(config.reference_camera)
    reference_detection = detections[reference_camera]
    sample_positions = np.unique(np.linspace(0, len(reference_detection) - 1, config.sample_count, dtype=int))

    case_grid: dict[str, list[ReplayCase]] = {}
    case_counts: dict[str, int] = {}
    for regime_name, regime in regimes.items():
        cases: list[ReplayCase] = []
        for sample_order, ref_pos_idx in enumerate(sample_positions):
            ref_frame = int(reference_detection[ref_pos_idx, 0])
            ref_t = ref_pos_idx / max(len(reference_detection) - 1, 1)
            target_ref = trajectory[int(round(ref_t * (len(trajectory) - 1))), :2]
            common_bias = regime.common_bias + rng.normal(0.0, 0.002)
            per_sensor_bias = rng.normal(0.0, regime.sensor_bias_std, size=len(detections))
            measurements: list[ReplayMeasurement] = []
            measurement_meta: list[dict[str, Any]] = []
            valid_count = 0

            for cam_idx in range(len(detections)):
                mapped_frame = int(
                    round(
                        alpha[reference_camera, cam_idx] * ref_frame
                        + beta[reference_camera, cam_idx]
                        + rng.normal(0.0, regime.extra_time_jitter)
                    )
                )
                detection_visible = False
                image_x: float | None = None
                image_y: float | None = None
                target_cam_xy = target_ref
                if 1 <= mapped_frame <= len(detections[cam_idx]):
                    mapped_row = detections[cam_idx][mapped_frame - 1]
                    image_x = float(mapped_row[1])
                    image_y = float(mapped_row[2])
                    detection_visible = not (math.isclose(image_x, 0.0) and math.isclose(image_y, 0.0))
                    cam_t = (mapped_frame - 1) / max(len(detections[cam_idx]) - 1, 1)
                    target_cam_xy = trajectory[int(round(cam_t * (len(trajectory) - 1))), :2]

                noisy_sensor_xy = camera_positions[cam_idx, :2] + rng.normal(0.0, regime.pose_noise_std, size=2)
                sensor = Sensor2D(float(noisy_sensor_xy[0]), float(noisy_sensor_xy[1]), name=f"cam{cam_idx}")
                target_cam = Point2D(float(target_cam_xy[0]), float(target_cam_xy[1]))
                observed_bearing = (
                    bearing_from_sensor(sensor, target_cam)
                    + common_bias
                    + per_sensor_bias[cam_idx]
                    + rng.normal(0.0, regime.noise_std)
                )
                is_outlier = bool(detection_visible and (rng.random() < regime.outlier_rate))
                if is_outlier:
                    observed_bearing += rng.normal(0.0, regime.outlier_scale)
                observed_bearing = float(wrap_angle(observed_bearing))

                measurements.append(
                    ReplayMeasurement(
                        sensor=sensor,
                        bearing=observed_bearing,
                        valid=bool(detection_visible),
                    )
                )
                measurement_meta.append(
                    {
                        "camera_id": cam_idx,
                        "camera_name": assets["camera_names"][cam_idx],
                        "reference_frame": ref_frame,
                        "mapped_frame": mapped_frame,
                        "sync_alpha": float(alpha[reference_camera, cam_idx]),
                        "sync_beta": float(beta[reference_camera, cam_idx]),
                        "image_x": image_x,
                        "image_y": image_y,
                        "visible": bool(detection_visible),
                        "is_outlier": is_outlier,
                        "target_async_x": float(target_cam.x),
                        "target_async_y": float(target_cam.y),
                        "sensor_reported_x": float(sensor.x),
                        "sensor_reported_y": float(sensor.y),
                    }
                )
                valid_count += int(detection_visible)

            if valid_count < 3:
                continue

            cases.append(
                ReplayCase(
                    case_id=f"{regime_name}_{sample_order:04d}",
                    target=Point2D(float(target_ref[0]), float(target_ref[1])),
                    measurements=measurements,
                    seed=sample_order,
                    meta={
                        "source": "public_dataset3",
                        "regime": regime_name,
                        "reference_camera": reference_camera,
                        "reference_frame": ref_frame,
                        "reference_time_norm": float(ref_t),
                        "num_valid_measurements": valid_count,
                        "common_bias": float(common_bias),
                        "regime_parameters": asdict(regime),
                        "measurement_meta": measurement_meta,
                    },
                )
            )

        case_grid[regime_name] = cases
        case_counts[regime_name] = len(cases)

    dataset_meta = {
        "source": "CenekAlbl/drone-tracking-datasets dataset3",
        "reference_camera": reference_camera,
        "sample_count_requested": int(config.sample_count),
        "camera_names": assets["camera_names"],
        "camera_positions_xy": [[float(row[0]), float(row[1])] for row in camera_positions[:, :2]],
        "trajectory_length": int(len(trajectory)),
        "trajectory_xy_bounds": {
            "min": [float(np.min(trajectory[:, 0])), float(np.min(trajectory[:, 1]))],
            "max": [float(np.max(trajectory[:, 0])), float(np.max(trajectory[:, 1]))],
        },
        "visibility_rates": assets["visibility_rates"],
        "retained_case_counts": case_counts,
        "bearing_generation_note": (
            "Bearings are replayed from surveyed observer positions and the public RTK target trajectory, "
            "while visibility masks and synchronization offsets come from the real multi-camera dataset; "
            "additional pose noise, bias, and outliers are injected to emulate passive-bearing front-end corruption."
        ),
    }
    return case_grid, dataset_meta


def summarize_public_replay_rows(
    rows: list[dict[str, Any]],
    ready_threshold: float,
    extreme_threshold: float,
) -> dict[str, Any]:
    if not rows:
        return {}

    methods = list(rows[0]["results"].keys())
    summary: dict[str, Any] = {}
    for method in methods:
        errors = np.asarray([row["results"][method]["error"] for row in rows], dtype=float)
        ready_rate = float(np.mean(errors <= ready_threshold))
        extreme_rate = float(np.mean(errors > extreme_threshold))
        summary[method] = {
            "mean": float(np.mean(errors)),
            "median": float(np.median(errors)),
            "p90": float(np.percentile(errors, 90)),
            "p95": float(np.percentile(errors, 95)),
            "ready_rate": ready_rate,
            "degraded_rate": float(np.clip(1.0 - ready_rate - extreme_rate, 0.0, 1.0)),
            "extreme_rate": extreme_rate,
        }
    return summary


def _sign_test_p_value(wins: int, losses: int) -> float:
    total = wins + losses
    if total == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(math.comb(total, idx) for idx in range(0, k + 1)) / (2**total)
    return float(min(1.0, 2.0 * tail))


def paired_report(rows: list[dict[str, Any]], left: str, right: str) -> dict[str, Any]:
    left_errors = np.asarray([row["results"][left]["error"] for row in rows], dtype=float)
    right_errors = np.asarray([row["results"][right]["error"] for row in rows], dtype=float)
    improvement = right_errors - left_errors
    wins = int(np.sum(improvement > 0.0))
    losses = int(np.sum(improvement < 0.0))
    ties = int(np.sum(np.isclose(improvement, 0.0)))
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "median_improvement": float(np.median(improvement)),
        "mean_improvement": float(np.mean(improvement)),
        "sign_test_p_value": _sign_test_p_value(wins, losses),
    }


def write_public_replay_cases(path: str | Path, case_grid: dict[str, list[ReplayCase]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serialize_case_grid(case_grid), ensure_ascii=False, indent=2), encoding="utf-8")
