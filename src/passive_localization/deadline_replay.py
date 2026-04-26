from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .public_dataset_replay import (
    PublicDataset3ReplayConfig,
    PublicDatasetReplayRegime,
    generate_public_dataset3_case_grid,
    serialize_case_grid,
)
from .replay import ReplayCase, ReplayMeasurement


@dataclass(frozen=True)
class DeadlineReplayRegime:
    base_regime: PublicDatasetReplayRegime
    front_end_deadline_ms: float
    processing_guard_ms: float
    network_latency_mean_ms: float
    network_latency_std_ms: float
    queue_burst_ms: float
    packet_drop_rate: float
    max_measurement_age_ms: float
    age_jitter_ms: float = 0.0
    frame_rate_hz: float = 30.0


def _deadline_case_from_public_case(
    case: ReplayCase,
    regime_name: str,
    regime: DeadlineReplayRegime,
    rng: np.random.Generator,
) -> tuple[ReplayCase | None, dict[str, Any]]:
    original_meta = dict(case.meta or {})
    original_measurement_meta = list(original_meta.get("measurement_meta", []))

    deadline_measurement_meta: list[dict[str, Any]] = []
    new_measurements: list[ReplayMeasurement] = []
    valid_original = 0
    on_time = 0
    late = 0
    packet_dropped = 0
    arrival_ms_values: list[float] = []
    age_ms_values: list[float] = []
    usable_budget_ms = max(regime.front_end_deadline_ms - regime.processing_guard_ms, 0.0)

    for measurement, measurement_meta in zip(case.measurements, original_measurement_meta):
        sync_alpha = float(measurement_meta.get("sync_alpha", 1.0))
        sync_beta = float(measurement_meta.get("sync_beta", 0.0))
        reference_frame = float(measurement_meta.get("reference_frame", 0.0))
        mapped_frame = float(measurement_meta.get("mapped_frame", reference_frame))
        ideal_frame = sync_alpha * reference_frame + sync_beta
        sync_age_ms = 1000.0 * abs(mapped_frame - ideal_frame) / max(regime.frame_rate_hz, 1e-6)
        sync_age_ms += abs(float(rng.normal(0.0, regime.age_jitter_ms)))

        network_latency_ms = max(0.0, float(rng.normal(regime.network_latency_mean_ms, regime.network_latency_std_ms)))
        if regime.queue_burst_ms > 0.0:
            network_latency_ms += float(rng.exponential(regime.queue_burst_ms))
        arrival_ms = sync_age_ms + network_latency_ms

        original_valid = bool(measurement.valid)
        packet_loss = bool(original_valid and (rng.random() < regime.packet_drop_rate))
        stale = bool(original_valid and (sync_age_ms > regime.max_measurement_age_ms))
        misses_deadline = bool(original_valid and (arrival_ms > usable_budget_ms))
        on_time_valid = bool(original_valid and not packet_loss and not stale and not misses_deadline)

        valid_original += int(original_valid)
        on_time += int(on_time_valid)
        late += int(original_valid and not packet_loss and (stale or misses_deadline))
        packet_dropped += int(packet_loss)
        if original_valid:
            arrival_ms_values.append(arrival_ms)
            age_ms_values.append(sync_age_ms)

        new_measurements.append(
            ReplayMeasurement(
                sensor=measurement.sensor,
                bearing=measurement.bearing,
                valid=on_time_valid,
            )
        )
        deadline_measurement_meta.append(
            {
                "camera_id": measurement_meta.get("camera_id"),
                "camera_name": measurement_meta.get("camera_name", measurement.sensor.name),
                "original_valid": original_valid,
                "packet_loss": packet_loss,
                "stale": stale,
                "misses_deadline": misses_deadline,
                "on_time_valid": on_time_valid,
                "sync_age_ms": round(sync_age_ms, 3),
                "network_latency_ms": round(network_latency_ms, 3),
                "arrival_ms": round(arrival_ms, 3),
            }
        )

    case_stats = {
        "case_id": case.case_id,
        "regime": regime_name,
        "num_original_valid": valid_original,
        "num_on_time": on_time,
        "num_late": late,
        "num_packet_dropped": packet_dropped,
        "retained": bool(on_time >= 3),
        "mean_arrival_ms": float(np.mean(arrival_ms_values)) if arrival_ms_values else 0.0,
        "mean_sync_age_ms": float(np.mean(age_ms_values)) if age_ms_values else 0.0,
        "usable_budget_ms": usable_budget_ms,
    }

    if on_time < 3:
        return None, case_stats

    deadline_meta = {
        "source": "public_dataset3_deadline_replay",
        "deadline_regime": regime_name,
        "deadline_parameters": asdict(regime),
        "num_original_valid": valid_original,
        "num_on_time": on_time,
        "num_late": late,
        "num_packet_dropped": packet_dropped,
        "mean_arrival_ms": case_stats["mean_arrival_ms"],
        "mean_sync_age_ms": case_stats["mean_sync_age_ms"],
        "usable_budget_ms": usable_budget_ms,
        "measurement_meta": deadline_measurement_meta,
    }
    merged_meta = dict(original_meta)
    merged_meta.update(deadline_meta)

    return (
        ReplayCase(
            case_id=case.case_id,
            target=case.target,
            measurements=new_measurements,
            seed=case.seed,
            meta=merged_meta,
        ),
        case_stats,
    )


def summarize_deadline_stats(case_stats: list[dict[str, Any]]) -> dict[str, Any]:
    if not case_stats:
        return {
            "total_cases": 0,
            "retained_cases": 0,
            "retention_rate": 0.0,
            "mean_original_valid": 0.0,
            "mean_on_time": 0.0,
            "mean_on_time_ratio": 0.0,
            "mean_late_ratio": 0.0,
            "mean_packet_drop_ratio": 0.0,
            "mean_arrival_ms": 0.0,
            "mean_sync_age_ms": 0.0,
            "usable_budget_ms": 0.0,
        }

    original_valid = np.asarray([item["num_original_valid"] for item in case_stats], dtype=float)
    on_time = np.asarray([item["num_on_time"] for item in case_stats], dtype=float)
    late = np.asarray([item["num_late"] for item in case_stats], dtype=float)
    packet_dropped = np.asarray([item["num_packet_dropped"] for item in case_stats], dtype=float)
    arrival_ms = np.asarray([item["mean_arrival_ms"] for item in case_stats], dtype=float)
    sync_age_ms = np.asarray([item["mean_sync_age_ms"] for item in case_stats], dtype=float)
    retained = np.asarray([1.0 if item["retained"] else 0.0 for item in case_stats], dtype=float)
    denom = np.maximum(original_valid, 1.0)

    return {
        "total_cases": int(len(case_stats)),
        "retained_cases": int(np.sum(retained)),
        "retention_rate": float(np.mean(retained)),
        "mean_original_valid": float(np.mean(original_valid)),
        "mean_on_time": float(np.mean(on_time)),
        "mean_on_time_ratio": float(np.mean(on_time / denom)),
        "mean_late_ratio": float(np.mean(late / denom)),
        "mean_packet_drop_ratio": float(np.mean(packet_dropped / denom)),
        "mean_arrival_ms": float(np.mean(arrival_ms)),
        "mean_sync_age_ms": float(np.mean(sync_age_ms)),
        "usable_budget_ms": float(case_stats[0]["usable_budget_ms"]),
    }


def generate_deadline_public_case_grid(
    regimes: dict[str, DeadlineReplayRegime],
    config: PublicDataset3ReplayConfig | None = None,
) -> tuple[dict[str, list[ReplayCase]], dict[str, Any]]:
    config = config or PublicDataset3ReplayConfig()
    base_regimes = {name: regime.base_regime for name, regime in regimes.items()}
    public_case_grid, dataset_meta = generate_public_dataset3_case_grid(base_regimes, config=config)

    case_grid: dict[str, list[ReplayCase]] = {}
    case_stats_by_regime: dict[str, list[dict[str, Any]]] = {}
    retained_case_counts: dict[str, int] = {}

    for regime_index, (regime_name, regime) in enumerate(regimes.items()):
        rng = np.random.default_rng(config.seed + 101 * (regime_index + 1))
        retained_cases: list[ReplayCase] = []
        regime_case_stats: list[dict[str, Any]] = []
        for case in public_case_grid[regime_name]:
            filtered_case, case_stats = _deadline_case_from_public_case(case, regime_name, regime, rng)
            regime_case_stats.append(case_stats)
            if filtered_case is not None:
                retained_cases.append(filtered_case)
        case_grid[regime_name] = retained_cases
        case_stats_by_regime[regime_name] = regime_case_stats
        retained_case_counts[regime_name] = len(retained_cases)

    summary_by_regime = {
        regime_name: summarize_deadline_stats(stats)
        for regime_name, stats in case_stats_by_regime.items()
    }
    overall_summary = summarize_deadline_stats(
        [item for stats in case_stats_by_regime.values() for item in stats]
    )

    dataset_meta = {
        **dataset_meta,
        "source": "CenekAlbl/drone-tracking-datasets dataset3 deadline replay",
        "retained_case_counts": retained_case_counts,
        "deadline_regimes": {name: asdict(regime) for name, regime in regimes.items()},
        "deadline_summary": {
            "overall": overall_summary,
            "by_regime": summary_by_regime,
        },
        "bearing_generation_note": (
            "Bearings are first replayed from surveyed observer positions, the public RTK target trajectory, "
            "and measured multi-camera visibility and synchronization. A second deadline-replay filter then "
            "drops bearings that become stale, miss the front-end deadline, or are lost by simulated link drop."
        ),
    }
    return case_grid, dataset_meta


def write_deadline_replay_cases(path: str | Path, case_grid: dict[str, list[ReplayCase]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serialize_case_grid(case_grid), ensure_ascii=False, indent=2), encoding="utf-8")
