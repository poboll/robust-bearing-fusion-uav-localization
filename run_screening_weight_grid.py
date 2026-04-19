"""Evaluate screening-weight stability under exact +/-20% coefficient perturbations."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import robust_bias_trimmed_refine
from passive_localization.scenario import generate_circular_scenario
from passive_localization.schedule import DEFAULT_SCREENING_WEIGHTS, select_sensor_subset


def _jaccard(left: list[int], right: list[int]) -> float:
    a = set(left)
    b = set(right)
    union = a | b
    return 1.0 if not union else float(len(a & b) / len(union))


def _evaluate_subset(
    valid_sensors,
    valid_bearings,
    pilot,
    budget: int,
    target: np.ndarray,
    method_cfg: MethodConfig,
    score_weights: list[float],
    seed: int,
) -> dict:
    selection = select_sensor_subset(
        sensors=valid_sensors,
        bearings=valid_bearings,
        estimate=pilot.point,
        budget=budget,
        policy="observability_robust",
        seed=seed,
        bias=pilot.bias,
        huber_delta=method_cfg.huber_delta,
        min_weight=method_cfg.min_weight,
        score_weights=score_weights,
    )
    chosen_sensors = [valid_sensors[idx] for idx in selection.selected_indices]
    chosen_bearings = valid_bearings[selection.selected_indices]
    refined = robust_bias_trimmed_refine(
        geometric_initialization(chosen_sensors, chosen_bearings),
        chosen_sensors,
        chosen_bearings,
        method_cfg,
    )
    return {
        "selected_indices": selection.selected_indices,
        "error": float(np.linalg.norm(refined.point.as_array() - target)),
        "score": float(selection.score),
    }


def run_screening_weight_grid(
    output_dir: str | Path = "experiments",
    seeds: list[int] | None = None,
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    seeds = list(seeds or range(24))

    method_cfg = MethodConfig()
    base_weights = np.asarray(DEFAULT_SCREENING_WEIGHTS, dtype=float)
    regimes = {
        "mixed": dict(bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45),
        "severe": dict(bias=0.06, missing_rate=0.25, outlier_rate=0.3, outlier_scale=0.6),
    }
    formations = ["circle", "perturbed", "random"]
    counts = [8, 10, 12]

    cached_cases: list[dict] = []
    for regime_name, regime_kwargs in regimes.items():
        for formation in formations:
            for num_uavs in counts:
                for seed in seeds:
                    scenario_cfg = ScenarioConfig(
                        seed=seed,
                        num_uavs=num_uavs,
                        formation_type=formation,
                        formation_jitter=1.2 if formation == "perturbed" else 0.0,
                        **regime_kwargs,
                    )
                    scenario = generate_circular_scenario(scenario_cfg)
                    valid_indices = [idx for idx, keep in enumerate(scenario.valid_mask.tolist()) if keep]
                    valid_sensors = [scenario.sensors[idx] for idx in valid_indices]
                    valid_bearings = scenario.observed_bearings[scenario.valid_mask]
                    if len(valid_sensors) < 4:
                        continue
                    target = scenario.target.as_array()
                    budget = max(4, min(len(valid_sensors) - 1, int(np.ceil(0.55 * len(valid_sensors)))))
                    pilot = robust_bias_trimmed_refine(
                        geometric_initialization(valid_sensors, valid_bearings),
                        valid_sensors,
                        valid_bearings,
                        method_cfg,
                    )
                    default_eval = _evaluate_subset(
                        valid_sensors=valid_sensors,
                        valid_bearings=valid_bearings,
                        pilot=pilot,
                        budget=budget,
                        target=target,
                        method_cfg=method_cfg,
                        score_weights=base_weights.tolist(),
                        seed=seed,
                    )
                    cached_cases.append(
                        {
                            "regime": regime_name,
                            "formation": formation,
                            "num_uavs": num_uavs,
                            "seed": seed,
                            "budget": budget,
                            "target": target,
                            "valid_sensors": valid_sensors,
                            "valid_bearings": valid_bearings,
                            "pilot": pilot,
                            "default_error": default_eval["error"],
                            "default_selected_indices": default_eval["selected_indices"],
                        }
                    )

    multiplier_grid = list(product([0.8, 1.0, 1.2], repeat=4))
    combinations_payload: list[dict] = []
    for multipliers in multiplier_grid:
        weights = base_weights * np.asarray(multipliers, dtype=float)
        weights = weights / float(np.sum(weights))
        errors = []
        overlaps = []
        deltas = []
        for case in cached_cases:
            evaluated = _evaluate_subset(
                valid_sensors=case["valid_sensors"],
                valid_bearings=case["valid_bearings"],
                pilot=case["pilot"],
                budget=case["budget"],
                target=case["target"],
                method_cfg=method_cfg,
                score_weights=weights.tolist(),
                seed=case["seed"],
            )
            errors.append(evaluated["error"])
            overlaps.append(_jaccard(evaluated["selected_indices"], case["default_selected_indices"]))
            deltas.append(evaluated["error"] - case["default_error"])

        combinations_payload.append(
            {
                "multipliers": list(map(float, multipliers)),
                "weights": weights.tolist(),
                "median_error": float(np.median(errors)),
                "p90_error": float(np.percentile(errors, 90)),
                "mean_jaccard": float(np.mean(overlaps)),
                "median_delta_vs_default": float(np.median(deltas)),
            }
        )

    payload = {
        "meta": {
            "default_weights": base_weights.tolist(),
            "multiplier_levels": [0.8, 1.0, 1.2],
            "num_cases": len(cached_cases),
            "num_combinations": len(combinations_payload),
            "note": "Each of the four score coefficients is perturbed by -20%, 0%, or +20%, then renormalized.",
        },
        "baseline": {
            "default_median_error": float(np.median([case["default_error"] for case in cached_cases])),
        },
        "combinations": combinations_payload,
        "summary": {
            "median_error": {
                "median": float(np.median([item["median_error"] for item in combinations_payload])),
                "p05": float(np.percentile([item["median_error"] for item in combinations_payload], 5)),
                "p95": float(np.percentile([item["median_error"] for item in combinations_payload], 95)),
            },
            "mean_jaccard": {
                "median": float(np.median([item["mean_jaccard"] for item in combinations_payload])),
                "p05": float(np.percentile([item["mean_jaccard"] for item in combinations_payload], 5)),
                "p95": float(np.percentile([item["mean_jaccard"] for item in combinations_payload], 95)),
            },
        },
    }
    out_path = output_dir / "screening_weight_grid_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_screening_weight_grid()
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
