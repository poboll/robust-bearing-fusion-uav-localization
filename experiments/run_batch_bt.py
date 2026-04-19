#!/usr/bin/env python3
from pathlib import Path
import json
import numpy as np
from passive_localization.config import MethodConfig, ScenarioConfig


def run_bt_batch(seeds=list(range(20))):
    outdir = Path('experiments')
    outdir.mkdir(exist_ok=True)
    results = []
    for seed in seeds:
        sc = ScenarioConfig(seed=seed, bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45)
        mc = MethodConfig()
        mc.estimate_bias = True
        mc.trim_ratio = 0.15
        mc.reweight_iterations = 3
        # reuse simulate run pattern
        from passive_localization.scenario import generate_circular_scenario
        from passive_localization.geometry import geometric_initialization
        from passive_localization.robust import robust_bias_trimmed_refine, least_squares_refine, robust_refine, pso_refine, simulated_annealing_refine
        scenario = generate_circular_scenario(sc)
        valid_sensors = [sensor for sensor, keep in zip(scenario.sensors, scenario.valid_mask) if keep]
        valid_bearings = scenario.observed_bearings[scenario.valid_mask]
        initial = geometric_initialization(valid_sensors, valid_bearings)
        ls = least_squares_refine(initial, valid_sensors, valid_bearings, mc)
        robust = robust_refine(initial, valid_sensors, valid_bearings, mc)
        robust_bt = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, mc)
        pso = pso_refine(initial, valid_sensors, valid_bearings, mc, seed=sc.seed)
        sa = simulated_annealing_refine(initial, valid_sensors, valid_bearings, mc, seed=sc.seed)
        def err(point):
            import numpy as _np
            return float(_np.linalg.norm(point.as_array() - scenario.target.as_array()))
        results.append({
            'seed': seed,
            'initial_error': err(initial),
            'least_squares_error': err(ls.point),
            'robust_error': err(robust.point),
            'robust_bias_trimmed_error': err(robust_bt.point),
            'pso_error': err(pso.point),
            'sa_error': err(sa.point),
        })
    out = outdir / 'batch_result_bt.json'
    out.write_text(json.dumps({'runs': results}, ensure_ascii=False, indent=2), encoding='utf-8')
    return results


if __name__ == '__main__':
    res = run_bt_batch(list(range(20)))
    print('done', len(res))
