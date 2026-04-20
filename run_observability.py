"""Analyze the relationship between geometry quality and localization error."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization, observability_metrics
from passive_localization.robust import (
    gnc_geman_mcclure_refine,
    least_squares_refine,
    pso_refine,
    robust_bias_trimmed_refine,
)
from passive_localization.scenario import generate_circular_scenario


def _rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(len(values), dtype=float)
    unique_vals, inverse, counts = np.unique(values, return_inverse=True, return_counts=True)
    for idx, count in enumerate(counts):
        if count > 1:
            mask = inverse == idx
            ranks[mask] = float(np.mean(ranks[mask]))
    return ranks


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def run_observability(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(20))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    method_cfg = MethodConfig()
    formations = ["circle", "random", "ellipse"]
    counts = [4, 6, 8, 10, 12]

    for formation in formations:
        for num_uavs in counts:
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
                scenario = generate_circular_scenario(scenario_cfg)
                valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
                valid_bearings = scenario.observed_bearings[scenario.valid_mask]
                initial = geometric_initialization(valid_sensors, valid_bearings)
                ls = least_squares_refine(initial, valid_sensors, valid_bearings, method_cfg)
                gnc = gnc_geman_mcclure_refine(initial, valid_sensors, valid_bearings, method_cfg)
                bt = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_cfg)
                pso = pso_refine(initial, valid_sensors, valid_bearings, method_cfg, seed=seed)

                metrics = observability_metrics(valid_sensors, scenario.target)
                target = scenario.target.as_array()
                rows.append(
                    {
                        "formation": formation,
                        "num_uavs": num_uavs,
                        "seed": seed,
                        "num_valid_sensors": len(valid_sensors),
                        **metrics,
                        "least_squares_error": float(np.linalg.norm(ls.point.as_array() - target)),
                        "gnc_gm_error": float(np.linalg.norm(gnc.point.as_array() - target)),
                        "robust_bias_trimmed_error": float(np.linalg.norm(bt.point.as_array() - target)),
                        "pso_error": float(np.linalg.norm(pso.point.as_array() - target)),
                    }
                )

    isotropy = np.array([row["isotropy"] for row in rows], dtype=float)
    inv_condition = 1.0 / np.maximum(np.array([row["condition_number"] for row in rows], dtype=float), 1.0)
    ls_err = np.array([row["least_squares_error"] for row in rows], dtype=float)
    gnc_err = np.array([row["gnc_gm_error"] for row in rows], dtype=float)
    bt_err = np.array([row["robust_bias_trimmed_error"] for row in rows], dtype=float)
    pso_err = np.array([row["pso_error"] for row in rows], dtype=float)

    summary = {
        "correlation": {
            "isotropy_vs_ls_error_pearson": _corr(isotropy, ls_err),
            "isotropy_vs_gnc_error_pearson": _corr(isotropy, gnc_err),
            "isotropy_vs_bt_error_pearson": _corr(isotropy, bt_err),
            "isotropy_vs_pso_error_pearson": _corr(isotropy, pso_err),
            "inverse_condition_vs_ls_error_spearman": _corr(_rankdata(inv_condition), _rankdata(ls_err)),
            "inverse_condition_vs_gnc_error_spearman": _corr(_rankdata(inv_condition), _rankdata(gnc_err)),
            "inverse_condition_vs_bt_error_spearman": _corr(_rankdata(inv_condition), _rankdata(bt_err)),
            "inverse_condition_vs_pso_error_spearman": _corr(_rankdata(inv_condition), _rankdata(pso_err)),
        },
        "by_formation": {},
    }

    for formation in formations:
        formation_rows = [row for row in rows if row["formation"] == formation]
        summary["by_formation"][formation] = {
            "isotropy_median": float(np.median([row["isotropy"] for row in formation_rows])),
            "ls_error_median": float(np.median([row["least_squares_error"] for row in formation_rows])),
            "gnc_error_median": float(np.median([row["gnc_gm_error"] for row in formation_rows])),
            "bt_error_median": float(np.median([row["robust_bias_trimmed_error"] for row in formation_rows])),
            "pso_error_median": float(np.median([row["pso_error"] for row in formation_rows])),
        }

    payload = {"runs": rows, "summary": summary}
    out_path = output_dir / "observability_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_observability()
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
