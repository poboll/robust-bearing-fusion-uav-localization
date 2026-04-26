"""Decompose the RANSAC family in the mixed-corruption regime."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import (
    pure_ransac_refine,
    ransac_lm_refine,
    ransac_refine,
    robust_bias_trimmed_refine,
)
from passive_localization.scenario import generate_circular_scenario


METHODS = {
    "pure_ransac": "Pure RANSAC",
    "ransac_lm": "RANSAC + LM",
    "ransac_refit": "RANSAC + robust refit",
    "proposed": "Proposed full pipeline",
}


def _summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "p95": float(np.percentile(arr, 95)),
        "success_at_0_1R": float(np.mean(arr <= 1.0)),
        "catastrophic_at_0_2R": float(np.mean(arr > 2.0)),
    }


def _paired_report(left: list[float], right: list[float]) -> dict[str, float | int]:
    left_arr = np.asarray(left, dtype=float)
    right_arr = np.asarray(right, dtype=float)
    diff = right_arr - left_arr
    wins = int(np.sum(diff > 1e-9))
    losses = int(np.sum(diff < -1e-9))
    ties = int(diff.size - wins - losses)
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "median_improvement": float(np.median(diff)),
        "mean_improvement": float(np.mean(diff)),
    }


def run_ransac_incremental_ablation(
    output_dir: str | Path = "experiments",
    seeds: list[int] | None = None,
) -> dict:
    seeds = seeds or list(range(240))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    method_cfg = MethodConfig()
    formations = ["circle", "random", "degenerate"]
    regime_kwargs = dict(
        bias=0.04,
        missing_rate=0.20,
        outlier_rate=0.22,
        outlier_scale=0.45,
    )

    rows: list[dict[str, float | str | int]] = []
    for formation in formations:
        for seed in seeds:
            scenario_cfg = ScenarioConfig(
                seed=seed,
                num_uavs=8,
                formation_type=formation,
                target_mode="random_interior",
                **regime_kwargs,
            )
            scenario = generate_circular_scenario(scenario_cfg)
            valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
            valid_bearings = scenario.observed_bearings[scenario.valid_mask]
            target = scenario.target.as_array()
            if len(valid_sensors) < 3:
                continue

            initial = geometric_initialization(valid_sensors, valid_bearings)
            estimates = {
                "pure_ransac": pure_ransac_refine(initial, valid_sensors, valid_bearings, method_cfg, seed=seed),
                "ransac_lm": ransac_lm_refine(initial, valid_sensors, valid_bearings, method_cfg, seed=seed),
                "ransac_refit": ransac_refine(initial, valid_sensors, valid_bearings, method_cfg, seed=seed),
                "proposed": robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_cfg),
            }

            row: dict[str, float | str | int] = {
                "formation": formation,
                "seed": seed,
                "num_valid": int(len(valid_sensors)),
            }
            for key, estimate in estimates.items():
                row[key] = float(np.linalg.norm(estimate.point.as_array() - target))
            rows.append(row)

    summary = {key: _summarize([float(row[key]) for row in rows]) for key in METHODS}
    pairwise = {
        "proposed_vs_pure_ransac": _paired_report(
            [float(row["proposed"]) for row in rows],
            [float(row["pure_ransac"]) for row in rows],
        ),
        "proposed_vs_ransac_lm": _paired_report(
            [float(row["proposed"]) for row in rows],
            [float(row["ransac_lm"]) for row in rows],
        ),
        "proposed_vs_ransac_refit": _paired_report(
            [float(row["proposed"]) for row in rows],
            [float(row["ransac_refit"]) for row in rows],
        ),
    }

    payload = {
        "meta": {
            "regime": "mixed",
            "formations": formations,
            "seeds": [int(seed) for seed in seeds],
            "num_cases": int(len(rows)),
            "radius_note": "R=10, so 0.1R=1.0 and 0.2R=2.0 in the reported distance unit.",
        },
        "methods": METHODS,
        "summary": summary,
        "pairwise": pairwise,
        "runs": rows,
    }
    out_path = output_dir / "ransac_incremental_ablation.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_ransac_incremental_ablation()
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
