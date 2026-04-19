"""Compute stricter threshold, paired-statistics, and RANSAC failure-case analyses."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.benchmarks import run_single_benchmark
from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import (
    gnc_geman_mcclure_refine,
    least_squares_refine,
    pso_refine,
    ransac_refine,
    robust_bias_trimmed_refine,
)
from passive_localization.scenario import generate_circular_scenario


RADIUS = 10.0
KEY_REGIMES = ["outlier", "mixed", "pose_uncertainty", "heterogeneous_bias"]
THRESHOLDS_R = [round(value, 2) for value in np.arange(0.10, 0.51, 0.05)]
METHODS = {
    "least_squares_error": "LS",
    "ransac_error": "RANSAC",
    "gnc_gm_error": "GNC-GM",
    "pso_error": "PSO",
    "robust_bias_trimmed_error": "Proposed",
}


def _paired_report(rows: list[dict], left: str, right: str) -> dict[str, float | int]:
    left_vals = np.asarray([row[left] for row in rows], dtype=float)
    right_vals = np.asarray([row[right] for row in rows], dtype=float)
    diff = right_vals - left_vals
    wins = int(np.sum(diff > 1e-9))
    losses = int(np.sum(diff < -1e-9))
    ties = int(diff.size - wins - losses)
    try:
        _, p_value = wilcoxon(diff, alternative="greater", zero_method="wilcox", method="auto")
    except ValueError:
        p_value = 1.0

    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "wilcoxon_p_value": float(p_value),
        "median_improvement": float(np.median(diff)),
        "mean_improvement": float(np.mean(diff)),
        "proposed_median": float(np.median(left_vals)),
        "baseline_median": float(np.median(right_vals)),
        "proposed_p95": float(np.percentile(left_vals, 95)),
        "baseline_p95": float(np.percentile(right_vals, 95)),
        "proposed_p99": float(np.percentile(left_vals, 99)),
        "baseline_p99": float(np.percentile(right_vals, 99)),
    }


def _reconstruct_case(row: dict, method_config: MethodConfig) -> dict:
    scenario_cfg = ScenarioConfig(**row["scenario"])
    scenario = generate_circular_scenario(scenario_cfg)
    valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask.tolist()) if keep]
    valid_bearings = scenario.observed_bearings[scenario.valid_mask]
    target = scenario.target.as_array()

    initial = geometric_initialization(valid_sensors, valid_bearings)
    ls = least_squares_refine(initial, valid_sensors, valid_bearings, method_config)
    ransac = ransac_refine(initial, valid_sensors, valid_bearings, method_config, seed=scenario_cfg.seed)
    proposed = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config)
    gnc = gnc_geman_mcclure_refine(initial, valid_sensors, valid_bearings, method_config)
    pso = pso_refine(initial, valid_sensors, valid_bearings, method_config, seed=scenario_cfg.seed)

    sensor_payload = []
    for idx, sensor in enumerate(valid_sensors):
        sensor_payload.append(
            {
                "name": sensor.name,
                "x": float(sensor.x),
                "y": float(sensor.y),
                "bearing": float(valid_bearings[idx]),
                "sensor_bias": float(scenario.sensor_biases[idx]) if scenario.sensor_biases is not None else 0.0,
                "pose_error": float(scenario.pose_errors[idx]) if scenario.pose_errors is not None else 0.0,
            }
        )

    return {
        "regime": row["regime"],
        "formation": row["formation"],
        "seed": int(row["scenario"]["seed"]),
        "target": {"x": float(target[0]), "y": float(target[1])},
        "scenario": row["scenario"],
        "valid_sensors": sensor_payload,
        "estimates": {
            "least_squares": {"x": float(ls.point.x), "y": float(ls.point.y), "error": float(row["least_squares_error"])},
            "gnc_gm": {"x": float(gnc.point.x), "y": float(gnc.point.y), "error": float(row["gnc_gm_error"])},
            "ransac": {
                "x": float(ransac.point.x),
                "y": float(ransac.point.y),
                "error": float(row["ransac_error"]),
                "removed_indices": ransac.removed_indices or [],
            },
            "pso": {"x": float(pso.point.x), "y": float(pso.point.y), "error": float(row["pso_error"])},
            "proposed": {
                "x": float(proposed.point.x),
                "y": float(proposed.point.y),
                "error": float(row["robust_bias_trimmed_error"]),
                "removed_indices": proposed.removed_indices or [],
                "bias": float(proposed.bias),
            },
        },
    }


def run_story_revision_analysis(
    story_path: str | Path = "experiments/story_benchmark_result.json",
    output_dir: str | Path = "experiments",
) -> dict:
    story_path = Path(story_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = json.loads(story_path.read_text(encoding="utf-8"))
    rows = payload["runs"]

    threshold_sweep: dict[str, dict[str, list[dict[str, float]]]] = {}
    strict_thresholds: dict[str, dict[str, dict[str, float]]] = {}
    for regime in KEY_REGIMES:
        regime_rows = [row for row in rows if row["regime"] == regime]
        threshold_sweep[regime] = {}
        strict_thresholds[regime] = {}
        for method_key, label in METHODS.items():
            errors = np.asarray([row[method_key] for row in regime_rows], dtype=float)
            threshold_sweep[regime][label] = [
                {
                    "threshold_r": float(threshold_r),
                    "threshold_abs": float(threshold_r * RADIUS),
                    "success_rate": float(np.mean(errors <= threshold_r * RADIUS)),
                    "failure_rate": float(np.mean(errors > threshold_r * RADIUS)),
                }
                for threshold_r in THRESHOLDS_R
            ]
            strict_thresholds[regime][label] = {
                "catastrophic_at_0_2R": float(np.mean(errors > 0.2 * RADIUS)),
                "catastrophic_at_0_3R": float(np.mean(errors > 0.3 * RADIUS)),
                "catastrophic_at_0_5R": float(np.mean(errors > 0.5 * RADIUS)),
            }

    paired_stats: dict[str, dict[str, dict[str, float | int]]] = {}
    for regime in KEY_REGIMES:
        regime_rows = [row for row in rows if row["regime"] == regime]
        paired_stats[regime] = {
            "proposed_vs_ls": _paired_report(regime_rows, "robust_bias_trimmed_error", "least_squares_error"),
            "proposed_vs_ransac": _paired_report(regime_rows, "robust_bias_trimmed_error", "ransac_error"),
            "proposed_vs_gnc": _paired_report(regime_rows, "robust_bias_trimmed_error", "gnc_gm_error"),
            "proposed_vs_pso": _paired_report(regime_rows, "robust_bias_trimmed_error", "pso_error"),
        }

    candidate_rows = [row for row in rows if row["regime"] in {"pose_uncertainty", "heterogeneous_bias"}]
    selected_case = max(
        candidate_rows,
        key=lambda row: (
            row["ransac_error"] - row["robust_bias_trimmed_error"],
            row["least_squares_error"] - row["robust_bias_trimmed_error"],
            row["pso_error"] - row["robust_bias_trimmed_error"],
        ),
    )
    failure_case = _reconstruct_case(selected_case, MethodConfig())

    result = {
        "meta": {
            "formation_radius": RADIUS,
            "thresholds_r": THRESHOLDS_R,
            "threshold_note": "Thresholds are reported in normalized units of R and absolute units with R=10.",
        },
        "strict_thresholds": strict_thresholds,
        "threshold_sweep": threshold_sweep,
        "paired_stats": paired_stats,
        "ransac_failure_case": failure_case,
    }
    out_path = output_dir / "story_revision_analysis.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    payload = run_story_revision_analysis()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
