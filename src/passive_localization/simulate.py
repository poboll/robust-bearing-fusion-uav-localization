from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

import numpy as np

from .config import MethodConfig, ScenarioConfig
from .geometry import Point2D, geometric_initialization
from .robust import least_squares_refine, pso_refine, robust_bias_trimmed_refine, robust_refine, simulated_annealing_refine
from .scenario import generate_circular_scenario
from .schedule import score_candidate


def _point_error(estimate: Point2D, target: Point2D) -> float:
    return float(np.linalg.norm(estimate.as_array() - target.as_array()))


def run_demo(output_dir: str | Path = "experiments") -> dict:
    scenario_config = ScenarioConfig()
    method_config = MethodConfig()
    scenario = generate_circular_scenario(scenario_config)

    valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
    valid_bearings = scenario.observed_bearings[scenario.valid_mask]

    initial = geometric_initialization(valid_sensors, valid_bearings)
    ls = least_squares_refine(initial, valid_sensors, valid_bearings, method_config)
    robust = robust_refine(initial, valid_sensors, valid_bearings, method_config)
    robust_bt = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config)
    pso = pso_refine(initial, valid_sensors, valid_bearings, method_config, seed=scenario_config.seed)
    sa = simulated_annealing_refine(initial, valid_sensors, valid_bearings, method_config, seed=scenario_config.seed)

    robust_schedule = score_candidate(candidate_id=0, sensors=valid_sensors, estimate=robust.point, residual=robust.residual)
    robust_bt_schedule = score_candidate(candidate_id=1, sensors=valid_sensors, estimate=robust_bt.point, residual=robust_bt.residual)
    result = {
        "scenario": asdict(scenario_config),
        "method": asdict(method_config),
        "target": asdict(scenario.target),
        "num_valid_sensors": len(valid_sensors),
        "initial": {**asdict(initial), "error": _point_error(initial, scenario.target)},
        "baselines": {
            "least_squares": {"point": asdict(ls.point), "residual": ls.residual, "error": _point_error(ls.point, scenario.target)},
            "robust_huber": {"point": asdict(robust.point), "residual": robust.residual, "error": _point_error(robust.point, scenario.target)},
            "robust_bias_trimmed": {
                "point": asdict(robust_bt.point),
                "residual": robust_bt.residual,
                "error": _point_error(robust_bt.point, scenario.target),
                "bias": robust_bt.bias,
                "kept_measurements": robust_bt.kept_measurements,
                "removed_measurements": robust_bt.removed_measurements,
                "removed_indices": robust_bt.removed_indices,
            },
            "pso": {"point": asdict(pso.point), "residual": pso.residual, "error": _point_error(pso.point, scenario.target)},
            "simulated_annealing": {"point": asdict(sa.point), "residual": sa.residual, "error": _point_error(sa.point, scenario.target)},
        },
        "schedule": asdict(robust_schedule),
        "schedule_bias_trimmed": asdict(robust_bt_schedule),
    }

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "demo_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def run_batch(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or [0, 1, 2, 3, 4]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    batch = []

    for seed in seeds:
        scenario_config = ScenarioConfig(seed=seed)
        method_config = MethodConfig()
        scenario = generate_circular_scenario(scenario_config)
        valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
        valid_bearings = scenario.observed_bearings[scenario.valid_mask]
        initial = geometric_initialization(valid_sensors, valid_bearings)
        ls = least_squares_refine(initial, valid_sensors, valid_bearings, method_config)
        robust = robust_refine(initial, valid_sensors, valid_bearings, method_config)
        robust_bt = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config)
        pso = pso_refine(initial, valid_sensors, valid_bearings, method_config, seed=seed)
        sa = simulated_annealing_refine(initial, valid_sensors, valid_bearings, method_config, seed=seed)
        batch.append(
            {
                "seed": seed,
                "initial_error": _point_error(initial, scenario.target),
                "least_squares_error": _point_error(ls.point, scenario.target),
                "robust_error": _point_error(robust.point, scenario.target),
                "robust_bias_trimmed_error": _point_error(robust_bt.point, scenario.target),
                "pso_error": _point_error(pso.point, scenario.target),
                "sa_error": _point_error(sa.point, scenario.target),
            }
        )

    summary = {
        "runs": batch,
        "means": {
            "initial_error": float(np.mean([row["initial_error"] for row in batch])),
            "least_squares_error": float(np.mean([row["least_squares_error"] for row in batch])),
            "robust_error": float(np.mean([row["robust_error"] for row in batch])),
            "robust_bias_trimmed_error": float(np.mean([row["robust_bias_trimmed_error"] for row in batch])),
            "pso_error": float(np.mean([row["pso_error"] for row in batch])),
            "sa_error": float(np.mean([row["sa_error"] for row in batch])),
        },
    }
    (output_dir / "batch_result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
