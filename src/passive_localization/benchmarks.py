from __future__ import annotations

from dataclasses import asdict

import numpy as np

from .config import MethodConfig, ScenarioConfig
from .geometry import geometric_initialization
from .robust import (
    gnc_geman_mcclure_refine,
    least_squares_refine,
    pso_refine,
    ransac_refine,
    robust_refine,
    simulated_annealing_refine,
    tukey_refine,
)
from .scenario import generate_circular_scenario
from .robust import robust_bias_trimmed_refine


def run_single_benchmark(scenario_config: ScenarioConfig, method_config: MethodConfig) -> dict:
    scenario = generate_circular_scenario(scenario_config)
    valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
    valid_bearings = scenario.observed_bearings[scenario.valid_mask]
    target = scenario.target.as_array()

    initial = geometric_initialization(valid_sensors, valid_bearings)
    ls = least_squares_refine(initial, valid_sensors, valid_bearings, method_config)
    robust = robust_refine(initial, valid_sensors, valid_bearings, method_config)
    tukey = tukey_refine(initial, valid_sensors, valid_bearings, method_config)
    robust_bt = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_config)
    gnc = gnc_geman_mcclure_refine(initial, valid_sensors, valid_bearings, method_config)
    ransac = ransac_refine(initial, valid_sensors, valid_bearings, method_config, seed=scenario_config.seed)
    pso = pso_refine(initial, valid_sensors, valid_bearings, method_config, seed=scenario_config.seed)
    sa = simulated_annealing_refine(initial, valid_sensors, valid_bearings, method_config, seed=scenario_config.seed)

    def err(point):
        return float(np.linalg.norm(point.as_array() - target))

    return {
        "scenario": asdict(scenario_config),
        "initial_error": err(initial),
        "least_squares_error": err(ls.point),
        "robust_error": err(robust.point),
        "tukey_error": err(tukey.point),
        "robust_bias_trimmed_error": err(robust_bt.point),
        "gnc_gm_error": err(gnc.point),
        "ransac_error": err(ransac.point),
        "pso_error": err(pso.point),
        "sa_error": err(sa.point),
    }


def compare_regimes() -> dict:
    method_config = MethodConfig()
    regimes = {
        "clean": ScenarioConfig(seed=0),
        "biased": ScenarioConfig(seed=0, bias=0.04),
        "missing": ScenarioConfig(seed=0, missing_rate=0.33),
        "outlier": ScenarioConfig(seed=0, outlier_rate=0.33, outlier_scale=0.45),
        "mixed": ScenarioConfig(seed=0, bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45),
    }
    return {name: run_single_benchmark(cfg, method_config) for name, cfg in regimes.items()}
