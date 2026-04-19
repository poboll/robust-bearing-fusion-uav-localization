"""Run higher-sample validation for the most important degraded regimes."""

from __future__ import annotations

import json
import math
from dataclasses import replace
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
        "success_at_1_0": float(np.mean(vals <= 1.0)),
        "catastrophic_at_5_0": float(np.mean(vals > 5.0)),
    }


def _sign_test_p_value(wins: int, losses: int) -> float:
    total = wins + losses
    if total == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(math.comb(total, i) for i in range(0, k + 1)) / (2**total)
    return float(min(1.0, 2.0 * tail))


def _bootstrap_ci(values: np.ndarray, n_boot: int = 4000, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    n = len(values)
    boots = []
    for _ in range(n_boot):
        sample = values[rng.integers(0, n, size=n)]
        boots.append(float(np.median(sample)))
    boots_arr = np.array(boots, dtype=float)
    return {
        "median": float(np.median(values)),
        "ci_low": float(np.percentile(boots_arr, 2.5)),
        "ci_high": float(np.percentile(boots_arr, 97.5)),
    }


def _paired_report(rows: list[dict], left: str, right: str) -> dict:
    left_vals = np.array([row[left] for row in rows], dtype=float)
    right_vals = np.array([row[right] for row in rows], dtype=float)
    diff = right_vals - left_vals
    wins = int(np.sum(diff > 0))
    losses = int(np.sum(diff < 0))
    ties = int(np.sum(np.isclose(diff, 0.0)))
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "sign_test_p_value": _sign_test_p_value(wins, losses),
        "median_improvement": float(np.median(diff)),
        "mean_improvement": float(np.mean(diff)),
        "bootstrap_median_improvement": _bootstrap_ci(diff),
    }


def run_high_seed_validation(
    output_dir: str | Path = "experiments",
    seeds: list[int] | None = None,
) -> dict:
    seeds = seeds or list(range(100))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regimes = {
        "outlier": ScenarioConfig(outlier_rate=0.33, outlier_scale=0.45),
        "mixed": ScenarioConfig(bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45),
    }

    payload: dict[str, dict] = {}
    for regime_name, base_scenario in regimes.items():
        rows = []
        for seed in seeds:
            rows.append(run_single_benchmark(replace(base_scenario, seed=seed), MethodConfig()))

        payload[regime_name] = {
            "num_seeds": len(seeds),
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
                "robust_bt_vs_ls": _paired_report(rows, "robust_bias_trimmed_error", "least_squares_error"),
                "robust_bt_vs_pso": _paired_report(rows, "robust_bias_trimmed_error", "pso_error"),
                "robust_bt_vs_sa": _paired_report(rows, "robust_bias_trimmed_error", "sa_error"),
            },
        }

    out_path = output_dir / "high_seed_validation.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_high_seed_validation()
    print(json.dumps(result, ensure_ascii=False, indent=2))
