"""Stress-test the screening score under coefficient perturbations."""

from __future__ import annotations

import json
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


def _jaccard(a: list[int], b: list[int]) -> float:
    left = set(a)
    right = set(b)
    union = left | right
    if not union:
        return 1.0
    return float(len(left & right) / len(union))


def _summarize_distribution(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "median": float(np.median(arr)),
        "mean": float(np.mean(arr)),
        "p05": float(np.percentile(arr, 5)),
        "p95": float(np.percentile(arr, 95)),
    }


def _sample_weights(rng: np.random.Generator, base_weights: np.ndarray, scale: float) -> list[float]:
    noisy = np.maximum(base_weights + rng.normal(0.0, scale, size=base_weights.size), 1e-5)
    noisy = noisy / float(np.sum(noisy))
    return noisy.tolist()


def _evaluate_subset(
    valid_sensors,
    valid_bearings,
    pilot,
    budget: int,
    target: np.ndarray,
    method_cfg: MethodConfig,
    policy: str = "observability_robust",
    score_weights: list[float] | None = None,
    seed: int = 0,
) -> dict:
    selection = select_sensor_subset(
        sensors=valid_sensors,
        bearings=valid_bearings,
        estimate=pilot.point,
        budget=budget,
        policy=policy,
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


def run_screening_weight_sensitivity(
    output_dir: str | Path = "experiments",
    seeds: list[int] | None = None,
    draws_per_level: int = 16,
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
    formations = ["circle", "perturbed", "random", "degenerate"]
    counts = [8, 10, 12]
    levels = {
        "mild": 0.03,
        "moderate": 0.08,
        "strong": 0.16,
    }

    cases: list[dict] = []
    for regime_name, regime_kwargs in regimes.items():
        for formation in formations:
            for num_uavs in counts:
                for seed in seeds:
                    scenario_cfg = ScenarioConfig(
                        seed=seed,
                        num_uavs=num_uavs,
                        formation_type=formation,
                        formation_jitter=1.2 if formation == "perturbed" else 0.0,
                        target_mode="random_interior",
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
                    baseline = {
                        "all_sensors_error": float(np.linalg.norm(pilot.point.as_array() - target)),
                        "residual": _evaluate_subset(
                            valid_sensors,
                            valid_bearings,
                            pilot,
                            budget,
                            target,
                            method_cfg,
                            policy="residual",
                            seed=seed,
                        ),
                        "reliability": _evaluate_subset(
                            valid_sensors,
                            valid_bearings,
                            pilot,
                            budget,
                            target,
                            method_cfg,
                            policy="reliability",
                            seed=seed,
                        ),
                        "default": _evaluate_subset(
                            valid_sensors,
                            valid_bearings,
                            pilot,
                            budget,
                            target,
                            method_cfg,
                            policy="observability_robust",
                            score_weights=base_weights.tolist(),
                            seed=seed,
                        ),
                    }
                    cases.append(
                        {
                            "regime": regime_name,
                            "formation": formation,
                            "num_uavs": num_uavs,
                            "seed": seed,
                            "budget": budget,
                            "all_sensors_error": baseline["all_sensors_error"],
                            "residual_error": baseline["residual"]["error"],
                            "reliability_error": baseline["reliability"]["error"],
                            "default_error": baseline["default"]["error"],
                            "default_selected_indices": baseline["default"]["selected_indices"],
                            "valid_sensors": valid_sensors,
                            "valid_bearings": valid_bearings,
                            "pilot": pilot,
                            "target": target,
                        }
                    )

    payload = {
        "meta": {
            "levels": levels,
            "draws_per_level": draws_per_level,
            "default_weights": base_weights.tolist(),
            "num_cases": len(cases),
            "num_seeds": len(seeds),
        },
        "baseline": {
            "all_sensors_median": float(np.median([case["all_sensors_error"] for case in cases])),
            "residual_median": float(np.median([case["residual_error"] for case in cases])),
            "reliability_median": float(np.median([case["reliability_error"] for case in cases])),
            "default_median": float(np.median([case["default_error"] for case in cases])),
        },
        "levels": {},
    }

    for level_name, scale in levels.items():
        rng = np.random.default_rng(700 + int(scale * 1000))
        perturbations: list[dict] = []
        for draw_idx in range(draws_per_level):
            weights = _sample_weights(rng, base_weights, scale)
            errors = []
            delta_vs_default = []
            beat_residual = []
            beat_reliability = []
            overlaps = []
            for case in cases:
                evaluated = _evaluate_subset(
                    case["valid_sensors"],
                    case["valid_bearings"],
                    case["pilot"],
                    case["budget"],
                    case["target"],
                    method_cfg,
                    policy="observability_robust",
                    score_weights=weights,
                    seed=case["seed"],
                )
                errors.append(evaluated["error"])
                delta_vs_default.append(case["default_error"] - evaluated["error"])
                beat_residual.append(1.0 if evaluated["error"] < case["residual_error"] else 0.0)
                beat_reliability.append(1.0 if evaluated["error"] < case["reliability_error"] else 0.0)
                overlaps.append(_jaccard(evaluated["selected_indices"], case["default_selected_indices"]))

            perturbations.append(
                {
                    "id": f"{level_name}_{draw_idx:02d}",
                    "weights": weights,
                    "median_error": float(np.median(errors)),
                    "p90_error": float(np.percentile(errors, 90)),
                    "beat_residual_rate": float(np.mean(beat_residual)),
                    "beat_reliability_rate": float(np.mean(beat_reliability)),
                    "mean_jaccard": float(np.mean(overlaps)),
                    "median_delta_vs_default": float(np.median(delta_vs_default)),
                }
            )

        payload["levels"][level_name] = {
            "perturbations": perturbations,
            "summary": {
                "median_error": _summarize_distribution([item["median_error"] for item in perturbations]),
                "p90_error": _summarize_distribution([item["p90_error"] for item in perturbations]),
                "beat_residual_rate": _summarize_distribution([item["beat_residual_rate"] for item in perturbations]),
                "beat_reliability_rate": _summarize_distribution([item["beat_reliability_rate"] for item in perturbations]),
                "mean_jaccard": _summarize_distribution([item["mean_jaccard"] for item in perturbations]),
                "median_delta_vs_default": _summarize_distribution([item["median_delta_vs_default"] for item in perturbations]),
            },
        }

    out_path = output_dir / "screening_weight_sensitivity.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_screening_weight_sensitivity()
    print(json.dumps(result["levels"], ensure_ascii=False, indent=2))
