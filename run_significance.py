"""Compute paired significance-style statistics for core experiment results."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


def _sign_test_p_value(wins: int, losses: int) -> float:
    total = wins + losses
    if total == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(math.comb(total, i) for i in range(0, k + 1)) / (2**total)
    return float(min(1.0, 2.0 * tail))


def _bootstrap_ci(values: np.ndarray, n_boot: int = 4000, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    boots = []
    n = len(values)
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
        "improvement_median": float(np.median(diff)),
        "improvement_mean": float(np.mean(diff)),
        "improvement_bootstrap": _bootstrap_ci(diff),
    }


def run_significance(
    ablation_path: str | Path = "experiments/ablation_result.json",
    output_dir: str | Path = "experiments",
) -> dict:
    ablation_path = Path(ablation_path)
    payload = json.loads(ablation_path.read_text(encoding="utf-8"))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regimes = ["outlier", "mixed", "biased"]
    result: dict[str, dict] = {}
    for regime in regimes:
        rows = payload[regime]["default"]["runs"]
        result[regime] = {
            "robust_bt_vs_ls": _paired_report(rows, "robust_bias_trimmed_error", "least_squares_error"),
            "robust_bt_vs_pso": _paired_report(rows, "robust_bias_trimmed_error", "pso_error"),
            "robust_bt_vs_sa": _paired_report(rows, "robust_bias_trimmed_error", "sa_error"),
        }

    out_path = output_dir / "significance_result.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_significance()
    print(json.dumps(result, ensure_ascii=False, indent=2))
