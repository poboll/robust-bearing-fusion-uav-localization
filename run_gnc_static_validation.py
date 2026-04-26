"""Run a focused static validation comparing the proposed method against GNC-GM."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np

from passive_localization.benchmarks import run_single_benchmark
from passive_localization.config import MethodConfig, ScenarioConfig


def _sign_test_p_value(wins: int, losses: int) -> float:
    total = wins + losses
    if total == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(math.comb(total, i) for i in range(0, k + 1)) / (2**total)
    return float(min(1.0, 2.0 * tail))


def _summarize(rows: list[dict], key: str) -> dict:
    vals = np.array([row[key] for row in rows], dtype=float)
    return {
        "mean": float(np.mean(vals)),
        "median": float(np.median(vals)),
        "p90": float(np.percentile(vals, 90)),
        "success_at_1_0": float(np.mean(vals <= 1.0)),
        "catastrophic_at_5_0": float(np.mean(vals > 5.0)),
    }


def _paired(rows: list[dict], left: str, right: str) -> dict:
    left_vals = np.array([row[left] for row in rows], dtype=float)
    right_vals = np.array([row[right] for row in rows], dtype=float)
    improvement = right_vals - left_vals
    wins = int(np.sum(improvement > 0.0))
    losses = int(np.sum(improvement < 0.0))
    ties = int(np.sum(np.isclose(improvement, 0.0)))
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "sign_test_p_value": _sign_test_p_value(wins, losses),
        "median_improvement": float(np.median(improvement)),
        "mean_improvement": float(np.mean(improvement)),
    }


def run_validation(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(80))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regimes = {
        "outlier": ScenarioConfig(outlier_rate=0.33, outlier_scale=0.45),
        "mixed": ScenarioConfig(bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45),
        "severe": ScenarioConfig(bias=0.05, missing_rate=0.25, outlier_rate=0.25, outlier_scale=0.50),
    }
    method = MethodConfig()

    payload = {}
    for regime_name, base in regimes.items():
        rows = []
        for seed in seeds:
            rows.append(run_single_benchmark(replace(base, seed=seed), method))
        payload[regime_name] = {
            "summary": {
                "least_squares_error": _summarize(rows, "least_squares_error"),
                "gnc_gm_error": _summarize(rows, "gnc_gm_error"),
                "robust_bias_trimmed_error": _summarize(rows, "robust_bias_trimmed_error"),
                "pso_error": _summarize(rows, "pso_error"),
            },
            "paired": {
                "robust_bt_vs_gnc_gm": _paired(rows, "robust_bias_trimmed_error", "gnc_gm_error"),
                "robust_bt_vs_ls": _paired(rows, "robust_bias_trimmed_error", "least_squares_error"),
            },
            "num_seeds": len(seeds),
        }

    out = output_dir / "gnc_static_validation.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(run_validation(), ensure_ascii=False, indent=2))
