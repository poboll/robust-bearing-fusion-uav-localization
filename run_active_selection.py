"""Evaluate measurement-screening policies under corrupted bearing-only localization."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import robust_bias_trimmed_refine
from passive_localization.scenario import generate_circular_scenario
from passive_localization.schedule import select_sensor_subset


POLICIES = {
    "all_sensors": "All sensors",
    "random": "Random subset",
    "spread": "Angular-spread greedy",
    "crlb": "FIM/CRLB greedy",
    "residual": "Residual-only top-k",
    "reliability": "Reliability-only top-k",
    "observability_robust": "Geom+reliability screening",
    "adaptive": "Adaptive screening",
}


def _summarize(vals: list[float]) -> dict[str, float]:
    arr = np.array(vals, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "success_at_0_5": float(np.mean(arr <= 0.5)),
        "success_at_1_0": float(np.mean(arr <= 1.0)),
        "catastrophic_at_5_0": float(np.mean(arr > 5.0)),
    }


def _wins(rows: list[dict], a: str, b: str) -> dict[str, int]:
    wins = 0
    ties = 0
    losses = 0
    for row in rows:
        delta = row[a] - row[b]
        if abs(delta) < 1e-9:
            ties += 1
        elif delta < 0:
            wins += 1
        else:
            losses += 1
    return {"wins": wins, "ties": ties, "losses": losses}


def run_active_selection(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(96))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regimes = {
        "mixed": dict(bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45),
        "severe": dict(bias=0.06, missing_rate=0.25, outlier_rate=0.3, outlier_scale=0.6),
    }
    formations = ["circle", "perturbed", "random"]
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
                    initial_all = geometric_initialization(valid_sensors, valid_bearings)
                    pilot = robust_bias_trimmed_refine(initial_all, valid_sensors, valid_bearings, method_cfg)
                    pilot_error = float(np.linalg.norm(pilot.point.as_array() - target))

                    per_policy: dict[str, dict] = {
                        "all_sensors": {
                            "error": pilot_error,
                            "num_selected": len(valid_sensors),
                            "selected_indices": list(range(len(valid_sensors))),
                            "subset_score": float("nan"),
                            "subset_isotropy": float("nan"),
                            "subset_reliability": float("nan"),
                        }
                    }

                    for policy in ["random", "spread", "crlb", "residual", "reliability", "observability_robust", "adaptive"]:
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
                        initial = geometric_initialization(chosen_sensors, chosen_bearings)
                        estimate = robust_bias_trimmed_refine(initial, chosen_sensors, chosen_bearings, method_cfg)
                        per_policy[policy] = {
                            "error": float(np.linalg.norm(estimate.point.as_array() - target)),
                            "num_selected": len(selection.selected_indices),
                            "selected_indices": selection.selected_indices,
                            "subset_score": selection.score,
                            "subset_isotropy": selection.isotropy,
                            "subset_reliability": selection.mean_reliability,
                            "subset_residual": selection.mean_residual,
                            "screening_triggered": selection.screening_triggered,
                        }

                    rows.append(
                        {
                            "regime": regime_name,
                            "formation": formation,
                            "num_uavs": num_uavs,
                            "seed": seed,
                            "num_valid_sensors": len(valid_sensors),
                            "budget": budget,
                            **{f"{policy}_error": data["error"] for policy, data in per_policy.items()},
                            **{f"{policy}_num_selected": data["num_selected"] for policy, data in per_policy.items()},
                            **{
                                f"{policy}_subset_score": data["subset_score"]
                                for policy, data in per_policy.items()
                                if policy != "all_sensors"
                            },
                            **{
                                f"{policy}_subset_isotropy": data["subset_isotropy"]
                                for policy, data in per_policy.items()
                                if policy != "all_sensors"
                            },
                            **{
                                f"{policy}_triggered": data["screening_triggered"]
                                for policy, data in per_policy.items()
                                if policy not in {"all_sensors", "random", "spread", "crlb", "residual", "reliability", "observability_robust"}
                            },
                        }
                    )

    summary = {
        "overall": {},
        "by_regime": {},
        "by_num_uavs": {},
        "paired": {},
    }
    policy_keys = list(POLICIES)
    for policy in policy_keys:
        summary["overall"][policy] = _summarize([row[f"{policy}_error"] for row in rows])

    for regime_name in regimes:
        regime_rows = [row for row in rows if row["regime"] == regime_name]
        summary["by_regime"][regime_name] = {policy: _summarize([row[f"{policy}_error"] for row in regime_rows]) for policy in policy_keys}

    for num_uavs in counts:
        count_rows = [row for row in rows if row["num_uavs"] == num_uavs]
        summary["by_num_uavs"][str(num_uavs)] = {policy: _summarize([row[f"{policy}_error"] for row in count_rows]) for policy in policy_keys}

    summary["paired"] = {
        "proposed_vs_random": _wins(rows, "observability_robust_error", "random_error"),
        "proposed_vs_spread": _wins(rows, "observability_robust_error", "spread_error"),
        "proposed_vs_crlb": _wins(rows, "observability_robust_error", "crlb_error"),
        "proposed_vs_residual": _wins(rows, "observability_robust_error", "residual_error"),
        "proposed_vs_reliability": _wins(rows, "observability_robust_error", "reliability_error"),
        "proposed_vs_all_sensors": _wins(rows, "observability_robust_error", "all_sensors_error"),
        "adaptive_vs_all_sensors": _wins(rows, "adaptive_error", "all_sensors_error"),
        "adaptive_vs_proposed": _wins(rows, "adaptive_error", "observability_robust_error"),
    }

    payload = {
        "meta": {
            "policies": POLICIES,
            "formations": formations,
            "counts": counts,
            "regimes": regimes,
            "num_runs": len(rows),
        },
        "runs": rows,
        "summary": summary,
    }
    out_path = output_dir / "active_selection_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_active_selection()
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
