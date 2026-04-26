"""Run the rebuilt manuscript benchmark focused on corrupted bearing-only localization."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from passive_localization.benchmarks import run_single_benchmark
from passive_localization.config import MethodConfig, ScenarioConfig


METHOD_KEYS = {
    "least_squares_error": "LS",
    "robust_error": "Huber-IRLS",
    "tukey_error": "Tukey-IRLS",
    "ransac_error": "RANSAC",
    "gnc_gm_error": "GNC-GM",
    "robust_bias_trimmed_error": "Proposed",
}


def _bootstrap_ci(values: np.ndarray, stat=np.median, repeats: int = 800, seed: int = 0) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(repeats, len(values)))
    samples = values[idx]
    stats = np.array([stat(sample) for sample in samples], dtype=float)
    return {
        "estimate": float(stat(values)),
        "ci_low": float(np.percentile(stats, 2.5)),
        "ci_high": float(np.percentile(stats, 97.5)),
    }


def _summarize(values: list[float], seed: int) -> dict[str, float | dict[str, float]]:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "success_at_0_1R": float(np.mean(arr <= 1.0)),
        "catastrophic_at_0_5R": float(np.mean(arr > 5.0)),
        "median_ci": _bootstrap_ci(arr, stat=np.median, seed=seed),
        "mean_ci": _bootstrap_ci(arr, stat=np.mean, seed=seed + 17),
    }


def run_story_benchmark(output_dir: str | Path = "experiments", seeds: list[int] | None = None) -> dict:
    seeds = seeds or list(range(200))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regimes = {
        "clean": dict(),
        "outlier": dict(outlier_rate=0.28, outlier_scale=0.42),
        "mixed": dict(bias=0.04, missing_rate=0.20, outlier_rate=0.22, outlier_scale=0.45),
        "pose_uncertainty": dict(bias=0.03, outlier_rate=0.18, outlier_scale=0.35, pose_noise_std=0.35),
        "heterogeneous_bias": dict(bias=0.01, sensor_bias_std=0.05, missing_rate=0.08, outlier_rate=0.12, outlier_scale=0.30),
    }
    formations = ["circle", "random", "degenerate"]
    counts = [8]
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
                        formation_jitter=1.1 if formation == "perturbed" else 0.0,
                        target_mode="random_interior",
                        **regime_kwargs,
                    )
                    result = run_single_benchmark(scenario_cfg, method_cfg)
                    result.update(
                        {
                            "regime": regime_name,
                            "formation": formation,
                            "num_uavs": num_uavs,
                        }
                    )
                    rows.append(result)

    summary: dict[str, dict] = {"overall": {}, "by_regime": {}, "by_regime_formation": {}}
    for method_key in METHOD_KEYS:
        summary["overall"][method_key] = _summarize([row[method_key] for row in rows], seed=101)

    for regime_name in regimes:
        regime_rows = [row for row in rows if row["regime"] == regime_name]
        summary["by_regime"][regime_name] = {
            method_key: _summarize([row[method_key] for row in regime_rows], seed=11 + len(regime_rows))
            for method_key in METHOD_KEYS
        }
        for formation in formations:
            subset = [row for row in regime_rows if row["formation"] == formation]
            summary["by_regime_formation"][f"{regime_name}__{formation}"] = {
                method_key: _summarize([row[method_key] for row in subset], seed=23 + len(subset))
                for method_key in METHOD_KEYS
            }

    payload = {
        "meta": {
            "regimes": regimes,
            "formations": formations,
            "counts": counts,
            "num_runs": len(rows),
            "formation_radius": 10.0,
            "physical_radius_example_m": 100.0,
            "unit_note": "Errors are reported in the same distance unit as the scenario coordinates; thresholds 0.1R and 0.5R correspond to 1.0 and 5.0 when R=10.",
            "target_note": "Targets are randomized inside the formation footprint using the deterministic scenario seed so that each run remains reproducible while avoiding a single fixed target layout.",
            "degenerate_note": "The degenerate formation places observers on a narrow arc to stress near-singular geometry in addition to circle and random layouts.",
        },
        "methods": METHOD_KEYS,
        "runs": rows,
        "summary": summary,
    }
    out_path = output_dir / "story_benchmark_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_story_benchmark()
    print(json.dumps(payload["summary"]["by_regime"], ensure_ascii=False, indent=2))
