"""Evaluate a simple downstream tracking proxy on PyBullet replay sequences."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.config import MethodConfig
from passive_localization.pybullet_bridge import PyBulletReplayConfig, generate_pybullet_replay_cases
from passive_localization.replay import evaluate_replay_case


REGIMES = {
    "nominal_pybullet": {
        "target_x": 0.0,
        "target_y": 0.0,
        "position_scale": 10.0,
        "duration_sec": 7.0,
        "warmup_sec": 2.0,
        "sample_every": 3,
        "common_bias": 0.004,
        "bias_drift": 0.0015,
        "noise_std": 0.0035,
        "attitude_gain": 0.014,
        "yaw_rate_gain": 0.0012,
        "delay_steps_mean": 0.25,
        "delay_steps_std": 0.15,
        "missing_rate": 0.004,
        "outlier_rate": 0.004,
        "outlier_scale": 0.04,
        "gust_force_std": 0.11,
        "gust_probability": 0.20,
        "gust_interval_steps": 6,
    },
    "disturbed_pybullet": {
        "target_x": 0.0,
        "target_y": 0.0,
        "position_scale": 10.0,
        "duration_sec": 7.5,
        "warmup_sec": 2.0,
        "sample_every": 3,
        "common_bias": 0.005,
        "bias_drift": 0.002,
        "noise_std": 0.004,
        "attitude_gain": 0.016,
        "yaw_rate_gain": 0.0015,
        "delay_steps_mean": 0.30,
        "delay_steps_std": 0.20,
        "missing_rate": 0.005,
        "outlier_rate": 0.005,
        "outlier_scale": 0.05,
        "gust_force_std": 0.12,
        "gust_probability": 0.22,
        "gust_interval_steps": 6,
    },
}
FORMATIONS = ["circle", "ellipse"]
COUNTS = [8, 10]
SEEDS = [0, 1, 2]
METHODS = {
    "least_squares": "LS",
    "ransac": "RANSAC",
    "robust_bias_trimmed": "Proposed",
}


def _run_tracker(rows: list[dict], method_key: str) -> dict[str, float | int | list[int]]:
    rows = sorted(rows, key=lambda row: float(row["meta"]["time_s"]))
    state: np.ndarray | None = None
    covariance: np.ndarray | None = None
    last_t: float | None = None
    target = np.array([rows[0]["target"]["x"], rows[0]["target"]["y"]], dtype=float)

    accepted = 0
    rejected = 0
    miss_count = 0
    break_count = 0
    sequence_broken = False
    reacq_delays: list[int] = []
    tracked_errors: list[float] = []
    gating_values: list[float] = []

    for row in rows:
        t = float(row["meta"]["time_s"])
        measurement = np.array(
            [
                row["results"][method_key]["x"],
                row["results"][method_key]["y"],
            ],
            dtype=float,
        )
        if state is None:
            state = np.array([measurement[0], measurement[1], 0.0, 0.0], dtype=float)
            covariance = np.diag([4.0, 4.0, 1.0, 1.0]).astype(float)
            accepted += 1
            last_t = t
            tracked_errors.append(float(np.linalg.norm(state[:2] - target)))
            continue

        dt = max(t - float(last_t or t), 1.0 / 16.0)
        last_t = t
        transition = np.array(
            [
                [1.0, 0.0, dt, 0.0],
                [0.0, 1.0, 0.0, dt],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=float,
        )
        process_noise = np.diag([0.06, 0.06, 0.35, 0.35]).astype(float)
        observe = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], dtype=float)
        measure_noise = np.diag([0.80, 0.80]).astype(float)

        assert covariance is not None
        state = transition @ state
        covariance = transition @ covariance @ transition.T + process_noise
        innovation = measurement - observe @ state
        innovation_cov = observe @ covariance @ observe.T + measure_noise
        gate_value = float(innovation.T @ np.linalg.solve(innovation_cov, innovation))
        gating_values.append(gate_value)

        if gate_value <= 9.21:
            kalman_gain = covariance @ observe.T @ np.linalg.inv(innovation_cov)
            state = state + kalman_gain @ innovation
            covariance = (np.eye(4) - kalman_gain @ observe) @ covariance
            accepted += 1
            if miss_count >= 3:
                reacq_delays.append(miss_count)
            miss_count = 0
        else:
            rejected += 1
            miss_count += 1
            if miss_count == 3:
                break_count += 1
                sequence_broken = True
                state = np.array([measurement[0], measurement[1], 0.0, 0.0], dtype=float)
                covariance = np.diag([6.0, 6.0, 1.6, 1.6]).astype(float)

        tracked_errors.append(float(np.linalg.norm(state[:2] - target)))

    total = max(len(rows), 1)
    return {
        "num_windows": len(rows),
        "accepted_update_rate": float(accepted / total),
        "rejected_update_rate": float(rejected / total),
        "break_count": break_count,
        "sequence_break": int(sequence_broken),
        "breaks_per_100_windows": float(100.0 * break_count / total),
        "median_reacquisition_steps": float(np.median(reacq_delays)) if reacq_delays else 0.0,
        "rmse": float(np.sqrt(np.mean(np.square(tracked_errors)))),
        "p90_tracking_error": float(np.percentile(tracked_errors, 90)),
        "median_gate_value": float(np.median(gating_values)) if gating_values else 0.0,
        "reacquisition_delays": reacq_delays,
    }


def _summarize_sequence_metrics(sequence_metrics: list[dict]) -> dict[str, float]:
    if not sequence_metrics:
        return {
            "sequence_break_rate": 0.0,
            "mean_breaks_per_100_windows": 0.0,
            "mean_accepted_update_rate": 0.0,
            "median_reacquisition_steps": 0.0,
            "median_tracking_rmse": 0.0,
            "p90_tracking_rmse": 0.0,
        }
    return {
        "sequence_break_rate": float(np.mean([item["sequence_break"] for item in sequence_metrics])),
        "mean_breaks_per_100_windows": float(np.mean([item["breaks_per_100_windows"] for item in sequence_metrics])),
        "mean_accepted_update_rate": float(np.mean([item["accepted_update_rate"] for item in sequence_metrics])),
        "median_reacquisition_steps": float(
            np.median([item["median_reacquisition_steps"] for item in sequence_metrics if item["break_count"] > 0])
        )
        if any(item["break_count"] > 0 for item in sequence_metrics)
        else 0.0,
        "median_tracking_rmse": float(np.median([item["rmse"] for item in sequence_metrics])),
        "p90_tracking_rmse": float(np.percentile([item["rmse"] for item in sequence_metrics], 90)),
    }


def run_tracking_proxy(output_dir: str | Path = "experiments") -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    method_config = MethodConfig()
    per_sequence: list[dict] = []
    serializable_examples: dict[str, list[dict]] = {}

    for regime_name, regime_kwargs in REGIMES.items():
        for formation in FORMATIONS:
            for count in COUNTS:
                for seed in SEEDS:
                    cfg = PyBulletReplayConfig(
                        seed=seed,
                        num_uavs=count,
                        formation_type=formation,
                        **regime_kwargs,
                    )
                    cases, _trace = generate_pybullet_replay_cases(cfg, case_prefix=regime_name)
                    rows = [evaluate_replay_case(case, method_config) for case in cases]
                    series_key = f"{regime_name}__{formation}__{count}__seed{seed}"
                    serializable_examples[series_key] = [
                        {
                            "case_id": row["case_id"],
                            "time_s": float(row["meta"]["time_s"]),
                            "target": row["target"],
                            "least_squares": row["results"]["least_squares"],
                            "ransac": row["results"]["ransac"],
                            "robust_bias_trimmed": row["results"]["robust_bias_trimmed"],
                        }
                        for row in rows
                    ]
                    for method_key, label in METHODS.items():
                        metrics = _run_tracker(rows, method_key)
                        per_sequence.append(
                            {
                                "series": series_key,
                                "regime": regime_name,
                                "formation": formation,
                                "num_uavs": count,
                                "seed": seed,
                                "method": label,
                                **metrics,
                            }
                        )

    summary = {"overall": {}, "by_regime": {}}
    for label in METHODS.values():
        label_rows = [row for row in per_sequence if row["method"] == label]
        summary["overall"][label] = _summarize_sequence_metrics(label_rows)
    for regime_name in REGIMES:
        summary["by_regime"][regime_name] = {}
        for label in METHODS.values():
            label_rows = [row for row in per_sequence if row["method"] == label and row["regime"] == regime_name]
            summary["by_regime"][regime_name][label] = _summarize_sequence_metrics(label_rows)

    payload = {
        "meta": {
            "regimes": REGIMES,
            "formations": FORMATIONS,
            "counts": COUNTS,
            "seeds": SEEDS,
            "methods": METHODS,
            "tracker_note": "A constant-velocity Kalman filter with chi-square gating is used as a downstream utility proxy.",
        },
        "summary": summary,
        "per_sequence": per_sequence,
        "examples": serializable_examples,
    }
    out_path = output_dir / "tracking_proxy_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_tracking_proxy()
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
