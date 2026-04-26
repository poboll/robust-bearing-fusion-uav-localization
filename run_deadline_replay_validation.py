"""Run deadline-aware measured-data replay validation on public dataset 3."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.config import MethodConfig
from passive_localization.deadline_replay import (
    DeadlineReplayRegime,
    generate_deadline_public_case_grid,
    write_deadline_replay_cases,
)
from passive_localization.public_dataset_replay import (
    PublicDataset3ReplayConfig,
    PublicDatasetReplayRegime,
    paired_report,
    summarize_public_replay_rows,
)
from passive_localization.replay import evaluate_replay_case


def run_deadline_replay_validation(
    output_dir: str | Path = "experiments",
    config: PublicDataset3ReplayConfig | None = None,
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = config or PublicDataset3ReplayConfig()

    regimes = {
        "deadline_nominal": DeadlineReplayRegime(
            base_regime=PublicDatasetReplayRegime(
                noise_std=0.010,
                common_bias=0.010,
                sensor_bias_std=0.008,
                outlier_rate=0.040,
                outlier_scale=0.180,
                pose_noise_std=0.350,
                extra_time_jitter=3.0,
            ),
            front_end_deadline_ms=170.0,
            processing_guard_ms=28.0,
            network_latency_mean_ms=16.0,
            network_latency_std_ms=5.0,
            queue_burst_ms=7.0,
            packet_drop_rate=0.020,
            max_measurement_age_ms=125.0,
            age_jitter_ms=3.0,
            frame_rate_hz=30.0,
        ),
        "deadline_disturbed": DeadlineReplayRegime(
            base_regime=PublicDatasetReplayRegime(
                noise_std=0.018,
                common_bias=0.020,
                sensor_bias_std=0.015,
                outlier_rate=0.100,
                outlier_scale=0.350,
                pose_noise_std=0.700,
                extra_time_jitter=8.0,
            ),
            front_end_deadline_ms=300.0,
            processing_guard_ms=40.0,
            network_latency_mean_ms=28.0,
            network_latency_std_ms=10.0,
            queue_burst_ms=14.0,
            packet_drop_rate=0.055,
            max_measurement_age_ms=240.0,
            age_jitter_ms=6.0,
            frame_rate_hz=30.0,
        ),
    }

    case_grid, dataset_meta = generate_deadline_public_case_grid(regimes=regimes, config=config)
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
            "nominal_proposed_vs_ls": paired_report(rows_by_regime["deadline_nominal"], "robust_bias_trimmed", "least_squares"),
            "disturbed_proposed_vs_ls": paired_report(rows_by_regime["deadline_disturbed"], "robust_bias_trimmed", "least_squares"),
        },
        "availability": dataset_meta["deadline_summary"],
    }

    payload = {
        "meta": {
            **dataset_meta,
            "thresholds_m": {
                "ready": config.ready_threshold_m,
                "extreme": config.extreme_threshold_m,
            },
            "num_cases_total": len(overall_rows),
        },
        "summary": summary,
    }

    (output_dir / "deadline_replay_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_deadline_replay_cases(output_dir / "deadline_replay_cases.json", case_grid)
    return payload


if __name__ == "__main__":
    result = run_deadline_replay_validation()
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
