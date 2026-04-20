"""Run public real-flight trajectory replay validation using drone-tracking-datasets dataset 3."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.config import MethodConfig
from passive_localization.public_dataset_replay import (
    PublicDataset3ReplayConfig,
    PublicDatasetReplayRegime,
    generate_public_dataset3_case_grid,
    paired_report,
    summarize_public_replay_rows,
    write_public_replay_cases,
)
from passive_localization.replay import evaluate_replay_case


def run_public_dataset3_replay_validation(
    output_dir: str | Path = "experiments",
    config: PublicDataset3ReplayConfig | None = None,
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = config or PublicDataset3ReplayConfig()

    regimes = {
        "real_nominal": PublicDatasetReplayRegime(
            noise_std=0.010,
            common_bias=0.010,
            sensor_bias_std=0.008,
            outlier_rate=0.040,
            outlier_scale=0.180,
            pose_noise_std=0.350,
            extra_time_jitter=3.0,
        ),
        "real_disturbed": PublicDatasetReplayRegime(
            noise_std=0.018,
            common_bias=0.020,
            sensor_bias_std=0.015,
            outlier_rate=0.100,
            outlier_scale=0.350,
            pose_noise_std=0.700,
            extra_time_jitter=8.0,
        ),
    }

    case_grid, dataset_meta = generate_public_dataset3_case_grid(regimes=regimes, config=config)
    method_config = MethodConfig()
    rows_by_regime = {
        regime_name: [evaluate_replay_case(case, method_config) for case in cases]
        for regime_name, cases in case_grid.items()
    }
    overall_rows = [row for rows in rows_by_regime.values() for row in rows]

    summary = {
        "overall": summarize_public_replay_rows(
            overall_rows,
            ready_threshold=config.ready_threshold_m,
            extreme_threshold=config.extreme_threshold_m,
        ),
        "by_regime": {
            regime_name: summarize_public_replay_rows(
                rows,
                ready_threshold=config.ready_threshold_m,
                extreme_threshold=config.extreme_threshold_m,
            )
            for regime_name, rows in rows_by_regime.items()
        },
        "paired": {
            "overall_proposed_vs_ls": paired_report(overall_rows, "robust_bias_trimmed", "least_squares"),
            "overall_proposed_vs_gnc": paired_report(overall_rows, "robust_bias_trimmed", "gnc_gm"),
            "overall_proposed_vs_ransac": paired_report(overall_rows, "robust_bias_trimmed", "ransac"),
            "nominal_proposed_vs_ls": paired_report(rows_by_regime["real_nominal"], "robust_bias_trimmed", "least_squares"),
            "disturbed_proposed_vs_ls": paired_report(rows_by_regime["real_disturbed"], "robust_bias_trimmed", "least_squares"),
        },
    }

    payload = {
        "meta": {
            **dataset_meta,
            "thresholds_m": {
                "ready": config.ready_threshold_m,
                "extreme": config.extreme_threshold_m,
            },
            "regimes": {name: regime.__dict__ for name, regime in regimes.items()},
            "num_cases_total": len(overall_rows),
        },
        "summary": summary,
    }

    (output_dir / "public_dataset3_replay_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_public_replay_cases(output_dir / "public_dataset3_replay_cases.json", case_grid)
    return payload


if __name__ == "__main__":
    result = run_public_dataset3_replay_validation()
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
