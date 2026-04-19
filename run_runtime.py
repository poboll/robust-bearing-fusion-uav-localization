"""Measure runtime, stage decomposition, and scaling for the passive-localization front end."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
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
from passive_localization.schedule import select_sensor_subset


def _cpu_name() -> str:
    try:
        if sys.platform == "darwin":
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    except Exception:
        pass
    return platform.processor() or platform.machine() or "Unknown CPU"


def _time_callable(fn, repeats: int, warmup: int) -> dict[str, float]:
    for _ in range(max(0, warmup)):
        fn()
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    arr = np.asarray(times, dtype=float) * 1000.0
    return {
        "mean_ms": float(np.mean(arr)),
        "median_ms": float(np.median(arr)),
        "p90_ms": float(np.percentile(arr, 90)),
        "std_ms": float(np.std(arr)),
    }


def _mixed_runtime_case(num_uavs: int, seed: int = 0) -> tuple[list, np.ndarray, np.ndarray, MethodConfig, object]:
    scenario = generate_circular_scenario(
        ScenarioConfig(
            seed=seed,
            num_uavs=num_uavs,
            formation_type="random" if seed % 2 else "degenerate",
            target_mode="random_interior",
            bias=0.04,
            sensor_bias_std=0.03,
            missing_rate=0.18,
            outlier_rate=0.20,
            outlier_scale=0.45,
            pose_noise_std=0.25,
        )
    )
    method_config = MethodConfig()
    valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
    valid_bearings = scenario.observed_bearings[scenario.valid_mask]
    initial = geometric_initialization(valid_sensors, valid_bearings)
    return valid_sensors, valid_bearings, initial, method_config, scenario


def run_runtime(output_dir: str | Path = "experiments", repeats: int = 50, warmup: int = 10) -> dict:
    valid_sensors, valid_bearings, initial, method_config, scenario = _mixed_runtime_case(num_uavs=8, seed=7)

    methods = {
        "least_squares": lambda: least_squares_refine(initial, valid_sensors, valid_bearings, method_config),
        "robust_huber": lambda: robust_refine(initial, valid_sensors, valid_bearings, method_config),
        "robust_bias_trimmed": lambda: robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config),
        "pso": lambda: pso_refine(initial, valid_sensors, valid_bearings, method_config, seed=0),
        "sa": lambda: simulated_annealing_refine(initial, valid_sensors, valid_bearings, method_config, seed=0),
    }

    method_payload = {name: _time_callable(fn, repeats=repeats, warmup=warmup) for name, fn in methods.items()}

    pilot = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config)
    budget = max(4, min(len(valid_sensors) - 1, int(np.ceil(0.55 * len(valid_sensors)))))
    stage_payload = {
        "stage1_proposed": _time_callable(
            lambda: robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config),
            repeats=repeats,
            warmup=warmup,
        ),
        "stage2_screening": _time_callable(
            lambda: select_sensor_subset(
                sensors=valid_sensors,
                bearings=valid_bearings,
                estimate=pilot.point,
                budget=budget,
                policy="observability_robust",
                seed=7,
                bias=pilot.bias,
                huber_delta=method_config.huber_delta,
                min_weight=method_config.min_weight,
            ),
            repeats=repeats,
            warmup=warmup,
        ),
        "stage2_adaptive": _time_callable(
            lambda: select_sensor_subset(
                sensors=valid_sensors,
                bearings=valid_bearings,
                estimate=pilot.point,
                budget=budget,
                policy="adaptive",
                seed=7,
                bias=pilot.bias,
                huber_delta=method_config.huber_delta,
                min_weight=method_config.min_weight,
            ),
            repeats=repeats,
            warmup=warmup,
        ),
    }

    counts = [4, 6, 8, 10, 12, 14]
    scaling = {"counts": counts, "stage1_proposed": {}, "stage2_screening": {}, "stage2_adaptive": {}}
    for count in counts:
        sensors_n, bearings_n, initial_n, _cfg_n, scenario_n = _mixed_runtime_case(num_uavs=count, seed=11 + count)
        if len(sensors_n) < 4:
            continue
        pilot_n = robust_bias_trimmed_refine(initial_n, sensors_n, bearings_n, method_config)
        budget_n = max(4, min(len(sensors_n) - 1, int(np.ceil(0.55 * len(sensors_n)))))
        scaling["stage1_proposed"][str(count)] = _time_callable(
            lambda: robust_bias_trimmed_refine(initial_n, sensors_n, bearings_n, method_config),
            repeats=repeats,
            warmup=warmup,
        )
        scaling["stage2_screening"][str(count)] = _time_callable(
            lambda: select_sensor_subset(
                sensors=sensors_n,
                bearings=bearings_n,
                estimate=pilot_n.point,
                budget=budget_n,
                policy="observability_robust",
                seed=11 + count,
                bias=pilot_n.bias,
                huber_delta=method_config.huber_delta,
                min_weight=method_config.min_weight,
            ),
            repeats=repeats,
            warmup=warmup,
        )
        scaling["stage2_adaptive"][str(count)] = _time_callable(
            lambda: select_sensor_subset(
                sensors=sensors_n,
                bearings=bearings_n,
                estimate=pilot_n.point,
                budget=budget_n,
                policy="adaptive",
                seed=11 + count,
                bias=pilot_n.bias,
                huber_delta=method_config.huber_delta,
                min_weight=method_config.min_weight,
            ),
            repeats=repeats,
            warmup=warmup,
        )

    payload = {
        "meta": {
            "hardware": {
                "cpu": _cpu_name(),
                "logical_cores": os.cpu_count(),
                "platform": platform.platform(),
                "python": sys.version.split()[0],
                "threading": "single-process sequential timing",
            },
            "benchmark_case": {
                "formation_radius_R": 10.0,
                "physical_example_radius_m": 100.0,
                "num_valid_sensors": len(valid_sensors),
                "formation_type": "random/degenerate mixed runtime case",
                "target_note": "Targets are drawn with target_mode=random_interior.",
                "budget": budget,
            },
            "timing_note": "Median runtimes are reported in milliseconds over repeated single-thread calls. Screening timings exclude the final refit so that stage costs can be interpreted separately.",
        },
        "methods": method_payload,
        "stages": stage_payload,
        "scaling": scaling,
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
