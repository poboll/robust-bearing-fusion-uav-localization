"""Generate pseudo-physical replay cases with delay and attitude jitter, then evaluate them."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.config import MethodConfig
from passive_localization.pseudo_physical import generate_case_grid
from passive_localization.replay import evaluate_replay_case, summarize_replay_results


def _group_summary(rows: list[dict]) -> dict:
    return summarize_replay_results(rows)


def run_pseudo_physical_validation(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(40))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regimes = {
        "mild_dynamic": {
            "speed": 1.6,
            "noise_std": 0.01,
            "common_bias": 0.012,
            "sensor_bias_std": 0.008,
            "attitude_jitter_std": 0.015,
            "delay_mean": 0.12,
            "delay_jitter": 0.05,
            "missing_rate": 0.05,
            "outlier_rate": 0.05,
            "outlier_scale": 0.25,
        },
        "harsh_dynamic": {
            "speed": 2.1,
            "noise_std": 0.015,
            "common_bias": 0.02,
            "sensor_bias_std": 0.012,
            "attitude_jitter_std": 0.03,
            "delay_mean": 0.25,
            "delay_jitter": 0.09,
            "missing_rate": 0.12,
            "outlier_rate": 0.12,
            "outlier_scale": 0.4,
        },
    }
    formations = ["circle", "perturbed", "random"]
    counts = [8, 10, 12]
    case_grid = generate_case_grid(seeds=seeds, regimes=regimes, formations=formations, counts=counts)
    method_config = MethodConfig()

    regime_rows: dict[str, list[dict]] = {}
    serializable_cases: dict[str, list[dict]] = {}
    for regime_name, cases in case_grid.items():
        rows = [evaluate_replay_case(case, method_config) for case in cases]
        regime_rows[regime_name] = rows
        serializable_cases[regime_name] = [
            {
                "case_id": case.case_id,
                "target": {"x": case.target.x, "y": case.target.y},
                "seed": case.seed,
                "meta": case.meta,
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
            for case in cases
        ]

    summary = {
        "overall": _group_summary([row for rows in regime_rows.values() for row in rows]),
        "by_regime": {regime_name: _group_summary(rows) for regime_name, rows in regime_rows.items()},
    }

    payload = {
        "meta": {
            "num_seeds": len(seeds),
            "formations": formations,
            "counts": counts,
            "regimes": regimes,
        },
        "summary": summary,
    }
    (output_dir / "pseudo_physical_result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "pseudo_physical_cases.json").write_text(json.dumps(serializable_cases, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_pseudo_physical_validation()
    print(json.dumps(result, ensure_ascii=False, indent=2))
