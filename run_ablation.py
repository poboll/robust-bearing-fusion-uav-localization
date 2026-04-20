"""Run ablation studies for the robust passive localization prototype.

Recommended usage:
`PYTHONPATH=src /opt/homebrew/Caskroom/miniconda/base/bin/python3 run_ablation.py`
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from passive_localization.benchmarks import run_single_benchmark
from passive_localization.config import MethodConfig, ScenarioConfig


def _summarize(rows: list[dict], key: str) -> dict:
    vals = np.array([row[key] for row in rows], dtype=float)
    return {
        "mean": float(np.mean(vals)),
        "median": float(np.median(vals)),
        "p90": float(np.percentile(vals, 90)),
        "success_at_0_5": float(np.mean(vals <= 0.5)),
        "success_at_1_0": float(np.mean(vals <= 1.0)),
        "catastrophic_at_5_0": float(np.mean(vals > 5.0)),
    }


def _paired_wins(rows: list[dict], a: str, b: str) -> dict:
    wins = sum(1 for row in rows if row[a] < row[b])
    ties = sum(1 for row in rows if abs(row[a] - row[b]) < 1e-9)
    return {"wins": wins, "ties": ties, "losses": len(rows) - wins - ties}


def run_ablation(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(20))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regimes = {
        "biased": ScenarioConfig(bias=0.04),
        "outlier": ScenarioConfig(outlier_rate=0.33, outlier_scale=0.45),
        "mixed": ScenarioConfig(bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45),
    }
    configs = {
        "default": MethodConfig(),
        "no_consensus_seed": replace(MethodConfig(), use_consensus_seed=False),
        "no_bias_estimation": replace(MethodConfig(), estimate_bias=False),
        "no_trimming": replace(MethodConfig(), trim_ratio=0.0),
        "light_reweight": replace(MethodConfig(), reweight_iterations=1),
        "heavy_trim": replace(MethodConfig(), trim_ratio=0.33),
    }

    all_results: dict[str, dict] = {}
    for regime_name, base_scenario in regimes.items():
        regime_payload: dict[str, dict] = {}
        for cfg_name, method_cfg in configs.items():
            rows = []
            for seed in seeds:
                scenario_cfg = replace(base_scenario, seed=seed)
                rows.append(run_single_benchmark(scenario_cfg, method_cfg))

            regime_payload[cfg_name] = {
                "config": asdict(method_cfg),
                "runs": rows,
                "summary": {
                    key: _summarize(rows, key)
                    for key in [
                        "least_squares_error",
                        "robust_error",
                        "robust_bias_trimmed_error",
                        "pso_error",
                        "sa_error",
                    ]
                },
                "paired": {
                    "robust_bt_vs_ls": _paired_wins(rows, "robust_bias_trimmed_error", "least_squares_error"),
                    "robust_bt_vs_robust": _paired_wins(rows, "robust_bias_trimmed_error", "robust_error"),
                    "robust_bt_vs_pso": _paired_wins(rows, "robust_bias_trimmed_error", "pso_error"),
                    "robust_bt_vs_sa": _paired_wins(rows, "robust_bias_trimmed_error", "sa_error"),
                },
            }
        all_results[regime_name] = regime_payload

    out_path = output_dir / "ablation_result.json"
    out_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    return all_results


if __name__ == "__main__":
    payload = run_ablation()
    print(json.dumps({k: list(v.keys()) for k, v in payload.items()}, ensure_ascii=False, indent=2))
