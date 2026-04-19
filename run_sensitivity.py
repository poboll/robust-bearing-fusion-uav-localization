"""Run severity sensitivity sweeps for the passive localization study."""

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
        "catastrophic_at_5_0": float(np.mean(vals > 5.0)),
    }


def run_sensitivity(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(20))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sweeps = {
        "outlier_rate": {
            "levels": [0.0, 0.1, 0.2, 0.3, 0.4],
            "base": dict(bias=0.04, missing_rate=0.2, outlier_scale=0.45, noise_std=0.02),
        },
        "bias": {
            "levels": [0.0, 0.02, 0.04, 0.06, 0.08],
            "base": dict(missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45, noise_std=0.02),
        },
        "noise_std": {
            "levels": [0.01, 0.02, 0.04, 0.06, 0.08],
            "base": dict(bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45),
        },
    }

    payload: dict[str, dict] = {}
    method_cfg = MethodConfig()
    methods = [
        "least_squares_error",
        "robust_error",
        "robust_bias_trimmed_error",
        "pso_error",
        "sa_error",
    ]

    for sweep_name, sweep_cfg in sweeps.items():
        sweep_payload: dict[str, dict] = {}
        for level in sweep_cfg["levels"]:
            rows = []
            for seed in seeds:
                kwargs = dict(sweep_cfg["base"])
                kwargs[sweep_name] = level
                scenario_cfg = ScenarioConfig(seed=seed, **kwargs)
                rows.append(run_single_benchmark(scenario_cfg, method_cfg))

            sweep_payload[str(level)] = {
                "runs": rows,
                "summary": {method: _metric_summary(rows, method) for method in methods},
            }
        payload[sweep_name] = sweep_payload

    out_path = output_dir / "sensitivity_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_sensitivity()
    compact = {
        sweep: {
            level: values["summary"]["robust_bias_trimmed_error"]["median"]
            for level, values in levels.items()
        }
        for sweep, levels in result.items()
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))
