"""Map when screening helps relative to all-sensor robust fusion."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import robust_bias_trimmed_refine
from passive_localization.scenario import generate_circular_scenario
from passive_localization.schedule import select_sensor_subset


POLICIES = ["all_sensors", "residual", "reliability", "observability_robust", "adaptive"]


def _summary(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "success_at_0_1R": float(np.mean(arr <= 1.0)),
        "catastrophic_at_0_5R": float(np.mean(arr > 5.0)),
    }


def run_selection_benefit_map(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(80))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    method_cfg = MethodConfig()
    outlier_rates = [0.05, 0.12, 0.20, 0.28, 0.36]
    budget_fracs = [0.45, 0.55, 0.70, 0.85]

    rows: list[dict] = []
    for outlier_rate in outlier_rates:
        for budget_frac in budget_fracs:
            for seed in seeds:
                scenario_cfg = ScenarioConfig(
                    seed=seed,
                    num_uavs=10,
                    formation_type="degenerate" if seed % 5 == 4 else ("random" if seed % 2 else "circle"),
                    target_mode="random_interior",
                    bias=0.03,
                    sensor_bias_std=0.03,
                    pose_noise_std=0.20,
                    missing_rate=0.12,
                    outlier_rate=outlier_rate,
                    outlier_scale=0.42,
                )
                scenario = generate_circular_scenario(scenario_cfg)
                valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
                valid_bearings = scenario.observed_bearings[scenario.valid_mask]
                if len(valid_sensors) < 4:
                    continue

                target = scenario.target.as_array()
                budget = max(4, min(len(valid_sensors) - 1, int(np.ceil(budget_frac * len(valid_sensors)))))
                initial = geometric_initialization(valid_sensors, valid_bearings)
                pilot = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_cfg)
                baseline_error = float(np.linalg.norm(pilot.point.as_array() - target))

                per_policy = {"all_sensors": baseline_error}
                for policy in [p for p in POLICIES if p != "all_sensors"]:
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
                    )
                    chosen_sensors = [valid_sensors[idx] for idx in selection.selected_indices]
                    chosen_bearings = valid_bearings[selection.selected_indices]
                    estimate = robust_bias_trimmed_refine(
                        geometric_initialization(chosen_sensors, chosen_bearings),
                        chosen_sensors,
                        chosen_bearings,
                        method_cfg,
                    )
                    per_policy[policy] = float(np.linalg.norm(estimate.point.as_array() - target))

                rows.append(
                    {
                        "seed": seed,
                        "outlier_rate": outlier_rate,
                        "budget_fraction": budget_frac,
                        **{f"{policy}_error": value for policy, value in per_policy.items()},
                    }
                )

    summary: dict[str, dict] = {}
    for outlier_rate in outlier_rates:
        for budget_frac in budget_fracs:
            key = f"outlier_{outlier_rate:.2f}__budget_{budget_frac:.2f}"
            subset = [row for row in rows if row["outlier_rate"] == outlier_rate and row["budget_fraction"] == budget_frac]
            summary[key] = {
                policy: _summary([row[f"{policy}_error"] for row in subset])
                for policy in POLICIES
            }
            summary[key]["delta_vs_all"] = {
                policy: float(np.median([row["all_sensors_error"] - row[f"{policy}_error"] for row in subset]))
                for policy in POLICIES
                if policy != "all_sensors"
            }

    payload = {
        "meta": {
            "outlier_rates": outlier_rates,
            "budget_fracs": budget_fracs,
            "num_runs": len(rows),
        },
        "runs": rows,
        "summary": summary,
    }
    out_path = output_dir / "selection_benefit_map.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_selection_benefit_map()
    print(json.dumps(payload["meta"], ensure_ascii=False, indent=2))
