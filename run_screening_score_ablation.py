"""Ablate the fixed-budget screening score terms used by the proposed selector."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import robust_bias_trimmed_refine
from passive_localization.scenario import generate_circular_scenario
from passive_localization.schedule import DEFAULT_SCREENING_WEIGHTS, select_sensor_subset


VARIANTS = {
    "all_sensors": None,
    "geometry_only": [0.72, 0.28, 0.0, 0.0],
    "geometry_plus_residual": [0.46, 0.14, 0.0, 0.40],
    "geometry_plus_reliability": [0.46, 0.14, 0.40, 0.0],
    "full_score": list(DEFAULT_SCREENING_WEIGHTS),
}


def _summary(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "success_at_0_1R": float(np.mean(arr <= 1.0)),
        "catastrophic_at_0_5R": float(np.mean(arr > 5.0)),
    }


def _wins(rows: list[dict], left: str, right: str) -> dict[str, int]:
    wins = 0
    losses = 0
    ties = 0
    for row in rows:
        delta = row[left] - row[right]
        if abs(delta) < 1e-9:
            ties += 1
        elif delta < 0.0:
            wins += 1
        else:
            losses += 1
    return {"wins": wins, "losses": losses, "ties": ties}


def run_screening_score_ablation(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    seeds = list(seeds or range(48))

    regimes = {
        "mixed": dict(bias=0.04, missing_rate=0.20, outlier_rate=0.20, outlier_scale=0.45),
        "severe": dict(bias=0.06, missing_rate=0.25, outlier_rate=0.30, outlier_scale=0.60),
    }
    formations = ["circle", "perturbed", "random", "degenerate"]
    counts = [8, 10, 12]
    method_cfg = MethodConfig()

    rows: list[dict] = []
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
                    valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
                    valid_bearings = scenario.observed_bearings[scenario.valid_mask]
                    if len(valid_sensors) < 4:
                        continue

                    target = scenario.target.as_array()
                    budget = max(4, min(len(valid_sensors) - 1, int(np.ceil(0.55 * len(valid_sensors)))))
                    initial = geometric_initialization(valid_sensors, valid_bearings)
                    pilot = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_cfg)

                    per_variant: dict[str, float] = {
                        "all_sensors": float(np.linalg.norm(pilot.point.as_array() - target)),
                    }
                    for variant_name, weights in VARIANTS.items():
                        if variant_name == "all_sensors":
                            continue
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
                            score_weights=weights,
                        )
                        chosen_sensors = [valid_sensors[idx] for idx in selection.selected_indices]
                        chosen_bearings = valid_bearings[selection.selected_indices]
                        refined = robust_bias_trimmed_refine(
                            geometric_initialization(chosen_sensors, chosen_bearings),
                            chosen_sensors,
                            chosen_bearings,
                            method_cfg,
                        )
                        per_variant[variant_name] = float(np.linalg.norm(refined.point.as_array() - target))

                    rows.append(
                        {
                            "regime": regime_name,
                            "formation": formation,
                            "num_uavs": num_uavs,
                            "seed": seed,
                            "budget": budget,
                            **{f"{name}_error": value for name, value in per_variant.items()},
                        }
                    )

    summary = {"overall": {}, "by_regime": {}, "paired": {}}
    for variant in VARIANTS:
        summary["overall"][variant] = _summary([row[f"{variant}_error"] for row in rows])
    for regime_name in regimes:
        regime_rows = [row for row in rows if row["regime"] == regime_name]
        summary["by_regime"][regime_name] = {
            variant: _summary([row[f"{variant}_error"] for row in regime_rows]) for variant in VARIANTS
        }

    summary["paired"] = {
        "full_vs_geometry_only": _wins(rows, "full_score_error", "geometry_only_error"),
        "full_vs_geometry_plus_residual": _wins(rows, "full_score_error", "geometry_plus_residual_error"),
        "full_vs_geometry_plus_reliability": _wins(rows, "full_score_error", "geometry_plus_reliability_error"),
        "full_vs_all_sensors": _wins(rows, "full_score_error", "all_sensors_error"),
    }

    payload = {
        "meta": {
            "regimes": regimes,
            "formations": formations,
            "counts": counts,
            "variants": VARIANTS,
            "num_runs": len(rows),
            "note": "The ablation isolates whether geometry alone is sufficient or whether residual/reliability terms are needed when the subset budget is fixed.",
        },
        "runs": rows,
        "summary": summary,
    }
    out_path = output_dir / "screening_score_ablation.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_screening_score_ablation()
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
