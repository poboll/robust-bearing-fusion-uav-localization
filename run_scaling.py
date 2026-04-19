"""Run sensor-count scaling experiments for the passive localization study."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from passive_localization.benchmarks import run_single_benchmark
from passive_localization.config import MethodConfig, ScenarioConfig


def _metric_summary(rows: list[dict], key: str) -> dict:
    vals = np.array([row[key] for row in rows], dtype=float)
    return {
        "mean": float(np.mean(vals)),
        "median": float(np.median(vals)),
        "p90": float(np.percentile(vals, 90)),
        "success_at_1_0": float(np.mean(vals <= 1.0)),
    }


def run_scaling(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(20))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, dict] = {}
    method_cfg = MethodConfig()
    formations = ["circle", "random"]
    uav_counts = [4, 6, 8, 10, 12]
    methods = [
        "least_squares_error",
        "robust_bias_trimmed_error",
        "pso_error",
        "sa_error",
    ]

    for formation in formations:
        formation_payload: dict[str, dict] = {}
        for num_uavs in uav_counts:
            rows = []
            for seed in seeds:
                scenario_cfg = ScenarioConfig(
                    seed=seed,
                    num_uavs=num_uavs,
                    formation_type=formation,
                    bias=0.04,
                    missing_rate=0.2,
                    outlier_rate=0.2,
                    outlier_scale=0.45,
                )
                rows.append(run_single_benchmark(scenario_cfg, method_cfg))
            formation_payload[str(num_uavs)] = {
                "runs": rows,
                "summary": {method: _metric_summary(rows, method) for method in methods},
            }
        payload[formation] = formation_payload

    out_path = output_dir / "scaling_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_scaling()
    compact = {
        formation: {
            num_uavs: values["summary"]["robust_bias_trimmed_error"]["median"]
            for num_uavs, values in counts.items()
        }
        for formation, counts in result.items()
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))
