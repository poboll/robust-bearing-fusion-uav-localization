"""Measure rough runtime per method for the current passive localization prototype."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import (
    least_squares_refine,
    pso_refine,
    robust_bias_trimmed_refine,
    robust_refine,
    simulated_annealing_refine,
)
from passive_localization.scenario import generate_circular_scenario


def run_runtime(output_dir: str | Path = "experiments", repeats: int = 50, warmup: int = 10) -> dict:
    scenario = generate_circular_scenario(
        ScenarioConfig(
            seed=0,
            bias=0.04,
            missing_rate=0.2,
            outlier_rate=0.2,
            outlier_scale=0.45,
            formation_type="circle",
        )
    )
    method_config = MethodConfig()
    valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
    valid_bearings = scenario.observed_bearings[scenario.valid_mask]
    initial = geometric_initialization(valid_sensors, valid_bearings)

    methods = {
        "least_squares": lambda: least_squares_refine(initial, valid_sensors, valid_bearings, method_config),
        "robust_huber": lambda: robust_refine(initial, valid_sensors, valid_bearings, method_config),
        "robust_bias_trimmed": lambda: robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config),
        "pso": lambda: pso_refine(initial, valid_sensors, valid_bearings, method_config, seed=0),
        "sa": lambda: simulated_annealing_refine(initial, valid_sensors, valid_bearings, method_config, seed=0),
    }

    payload = {}
    for name, fn in methods.items():
        for _ in range(max(0, warmup)):
            fn()
        times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            fn()
            times.append(time.perf_counter() - t0)
        payload[name] = {
            "mean_ms": float(np.mean(times) * 1000.0),
            "median_ms": float(np.median(times) * 1000.0),
            "p90_ms": float(np.percentile(times, 90) * 1000.0),
            "std_ms": float(np.std(times) * 1000.0),
        }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "runtime_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="experiments", help="Directory for runtime_result.json")
    parser.add_argument("--repeats", type=int, default=50, help="Number of timed repetitions per method")
    parser.add_argument("--warmup", type=int, default=10, help="Number of untimed warmup calls per method")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    print(
        json.dumps(
            run_runtime(output_dir=args.output_dir, repeats=args.repeats, warmup=args.warmup),
            ensure_ascii=False,
            indent=2,
        )
    )
