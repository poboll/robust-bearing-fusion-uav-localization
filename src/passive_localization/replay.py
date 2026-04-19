from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .config import MethodConfig
from .geometry import Point2D, Sensor2D, geometric_initialization
from .robust import (
    gnc_geman_mcclure_refine,
    least_squares_refine,
    ransac_refine,
    robust_bias_trimmed_refine,
    robust_refine,
    tukey_refine,
)


@dataclass
class ReplayMeasurement:
    sensor: Sensor2D
    bearing: float
    valid: bool = True


@dataclass
class ReplayCase:
    case_id: str
    target: Point2D
    measurements: list[ReplayMeasurement]
    seed: int = 0
    meta: dict[str, Any] | None = None


def _as_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    return default


def _measurement_from_dict(row: dict[str, Any], index: int) -> ReplayMeasurement:
    return ReplayMeasurement(
        sensor=Sensor2D(
            x=float(row["x"]),
            y=float(row["y"]),
            name=str(row.get("name") or f"sensor_{index}"),
        ),
        bearing=float(row["bearing"]),
        valid=_as_bool(row.get("valid"), default=True),
    )


def _case_from_dict(payload: dict[str, Any], index: int) -> ReplayCase:
    target = payload.get("target", {})
    measurements = payload.get("measurements", [])
    return ReplayCase(
        case_id=str(payload.get("case_id") or f"case_{index:04d}"),
        target=Point2D(float(target["x"]), float(target["y"])),
        measurements=[_measurement_from_dict(row, idx) for idx, row in enumerate(measurements)],
        seed=int(payload.get("seed", 0)),
        meta={k: v for k, v in payload.items() if k not in {"case_id", "target", "measurements", "seed"}},
    )


def _load_json_cases(path: Path) -> list[ReplayCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        cases = payload.get("cases", [])
    elif isinstance(payload, list):
        cases = payload
    else:
        raise ValueError("JSON replay data must be a list of cases or a dict with a 'cases' field")
    return [_case_from_dict(case, idx) for idx, case in enumerate(cases)]


def _load_jsonl_cases(path: Path) -> list[ReplayCase]:
    cases: list[ReplayCase] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        cases.append(_case_from_dict(json.loads(line), idx))
    return cases


def _load_csv_cases(path: Path) -> list[ReplayCase]:
    grouped: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"case_id", "target_x", "target_y", "sensor_x", "sensor_y", "bearing"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV replay data is missing required columns: {sorted(missing)}")

        for idx, row in enumerate(reader):
            case_id = str(row["case_id"])
            record = grouped.setdefault(
                case_id,
                {
                    "case_id": case_id,
                    "target": {"x": float(row["target_x"]), "y": float(row["target_y"])},
                    "seed": int(row.get("seed") or 0),
                    "measurements": [],
                },
            )
            record["measurements"].append(
                {
                    "name": row.get("sensor_name") or row.get("name") or f"sensor_{idx}",
                    "x": float(row["sensor_x"]),
                    "y": float(row["sensor_y"]),
                    "bearing": float(row["bearing"]),
                    "valid": _as_bool(row.get("valid"), default=True),
                }
            )
    return [_case_from_dict(case, idx) for idx, case in enumerate(grouped.values())]


def load_replay_cases(path: str | Path) -> list[ReplayCase]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".json":
        return _load_json_cases(path)
    if path.suffix.lower() == ".jsonl":
        return _load_jsonl_cases(path)
    if path.suffix.lower() == ".csv":
        return _load_csv_cases(path)
    raise ValueError(f"Unsupported replay file type: {path.suffix}")


def evaluate_replay_case(case: ReplayCase, method_config: MethodConfig | None = None) -> dict[str, Any]:
    method_config = method_config or MethodConfig()
    valid_measurements = [measurement for measurement in case.measurements if measurement.valid]
    if len(valid_measurements) < 3:
        raise ValueError(f"Replay case '{case.case_id}' has fewer than three valid measurements")

    sensors = [measurement.sensor for measurement in valid_measurements]
    bearings = np.array([measurement.bearing for measurement in valid_measurements], dtype=float)
    target = case.target.as_array()

    initial = geometric_initialization(sensors, bearings)
    ls = least_squares_refine(initial, sensors, bearings, method_config)
    robust = robust_refine(initial, sensors, bearings, method_config)
    tukey = tukey_refine(initial, sensors, bearings, method_config)
    robust_bt = robust_bias_trimmed_refine(initial, sensors, bearings, method_config)
    gnc = gnc_geman_mcclure_refine(initial, sensors, bearings, method_config)
    ransac = ransac_refine(initial, sensors, bearings, method_config, seed=case.seed)

    def _result(name: str, estimate_point: Point2D, residual: float, bias: float | None = None) -> dict[str, Any]:
        point = estimate_point.as_array()
        result = {
            "method": name,
            "x": float(point[0]),
            "y": float(point[1]),
            "residual": float(residual),
            "error": float(np.linalg.norm(point - target)),
        }
        if bias is not None:
            result["bias"] = float(bias)
        return result

    return {
        "case_id": case.case_id,
        "num_measurements": len(case.measurements),
        "num_valid_measurements": len(valid_measurements),
        "target": {"x": case.target.x, "y": case.target.y},
        "results": {
            "initial": _result("initial", initial, residual=float("nan")),
            "least_squares": _result("least_squares", ls.point, ls.residual),
            "robust_huber": _result("robust_huber", robust.point, robust.residual),
            "tukey_irls": _result("tukey_irls", tukey.point, tukey.residual),
            "gnc_gm": _result("gnc_gm", gnc.point, gnc.residual),
            "ransac": _result("ransac", ransac.point, ransac.residual),
            "robust_bias_trimmed": _result("robust_bias_trimmed", robust_bt.point, robust_bt.residual, bias=robust_bt.bias),
        },
        "meta": case.meta or {},
    }


def summarize_replay_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    methods = list(rows[0]["results"].keys()) if rows else []
    summary: dict[str, Any] = {}
    for method in methods:
        errors = np.array([row["results"][method]["error"] for row in rows], dtype=float)
        summary[method] = {
            "mean": float(np.mean(errors)),
            "median": float(np.median(errors)),
            "p90": float(np.percentile(errors, 90)),
            "success_at_1_0": float(np.mean(errors <= 1.0)),
            "catastrophic_at_5_0": float(np.mean(errors > 5.0)),
        }
    return summary
