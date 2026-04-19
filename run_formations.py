"""Evaluate method robustness under different UAV formations."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from passive_localization.benchmarks import run_single_benchmark
from passive_localization.config import MethodConfig, ScenarioConfig


def run_formations(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(20))
    formations = {
        "circle": {"formation_type": "circle", "formation_jitter": 0.0},
        "ellipse": {"formation_type": "ellipse", "formation_jitter": 0.0},
        "perturbed": {"formation_type": "perturbed", "formation_jitter": 1.2},
        "random": {"formation_type": "random", "formation_jitter": 0.0},
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, dict] = {}
    for formation_name, formation_kwargs in formations.items():
        rows = []
        for seed in seeds:
            scenario = ScenarioConfig(
                seed=seed,
                bias=0.04,
                missing_rate=0.2,
                outlier_rate=0.2,
                outlier_scale=0.45,
                **formation_kwargs,
            )
            rows.append(run_single_benchmark(scenario, MethodConfig()))

        payload[formation_name] = {
            "runs": rows,
            "summary": {
                key: {
                    "mean": float(np.mean([row[key] for row in rows])),
                    "median": float(np.median([row[key] for row in rows])),
                    "p90": float(np.percentile([row[key] for row in rows], 90)),
                }
                for key in [
                    "least_squares_error",
                    "robust_error",
                    "robust_bias_trimmed_error",
                    "pso_error",
                    "sa_error",
                ]
            },
        }

    out_path = output_dir / "formation_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    data = run_formations()
    print(json.dumps({k: list(v["summary"].keys()) for k, v in data.items()}, ensure_ascii=False, indent=2))
