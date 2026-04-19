from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np

from .geometry import Point2D, Sensor2D, weighted_observability_metrics, wrap_angle


SCREENING_WEIGHT_KEYS = ("determinant", "isotropy", "reliability", "residual")
DEFAULT_SCREENING_WEIGHTS = (0.34, 0.18, 0.24, 0.24)
DEFAULT_DETERMINANT_SCALE = 1e4
DEFAULT_RESIDUAL_SCALE = 0.25


@dataclass
class ScheduleScore:
    candidate_id: int
    observability: float
    recovery_cost: float


@dataclass
class SensorSubsetSelection:
    policy: str
    budget: int
    selected_indices: list[int]
    score: float
    observability: float
    isotropy: float
    mean_reliability: float
    mean_residual: float
    screening_triggered: bool | None = None


def score_candidate(candidate_id: int, sensors: list[Sensor2D], estimate: Point2D, residual: float) -> ScheduleScore:
    """Backward-compatible single-candidate score used by the demo script."""
    point = estimate.as_array()
    sensor_xy = np.array([[sensor.x, sensor.y] for sensor in sensors], dtype=float)
    pred = np.arctan2(point[1] - sensor_xy[:, 1], point[0] - sensor_xy[:, 0])
    spread = float(np.std(pred))
    observability = spread / (1.0 + residual)
    recovery_cost = 1.0 / (1.0 + len(sensors) * spread)
    return ScheduleScore(candidate_id=candidate_id, observability=observability, recovery_cost=recovery_cost)


def _predict_bearings(sensors: list[Sensor2D], estimate: Point2D) -> np.ndarray:
    point = estimate.as_array()
    sensor_xy = np.array([[sensor.x, sensor.y] for sensor in sensors], dtype=float)
    return np.arctan2(point[1] - sensor_xy[:, 1], point[0] - sensor_xy[:, 0])


def residual_reliability(
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    estimate: Point2D,
    huber_delta: float,
    bias: float = 0.0,
    min_weight: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    pred = _predict_bearings(sensors, estimate)
    residuals = wrap_angle(pred - bearings - bias)
    abs_res = np.abs(residuals)
    reliability = np.ones_like(abs_res)
    large = abs_res > huber_delta
    reliability[large] = huber_delta / np.maximum(abs_res[large], 1e-8)
    reliability = np.maximum(reliability, min_weight)
    return residuals, reliability


def _angle_diversity(pred_angles: np.ndarray) -> float:
    if pred_angles.size < 2:
        return 0.0
    diffs = []
    for i in range(pred_angles.size):
        for j in range(i + 1, pred_angles.size):
            diffs.append(abs(float(wrap_angle(pred_angles[i] - pred_angles[j]))))
    if not diffs:
        return 0.0
    return float(np.mean(diffs) / np.pi)


def _subset_stats(
    selected_indices: list[int],
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    estimate: Point2D,
    reliability: np.ndarray,
    residuals: np.ndarray,
) -> dict[str, float]:
    chosen = [sensors[idx] for idx in selected_indices]
    weights = reliability[selected_indices]
    metrics = weighted_observability_metrics(chosen, estimate, weights=weights)
    pred = _predict_bearings(chosen, estimate)
    diversity = _angle_diversity(pred)
    mean_rel = float(np.mean(weights)) if weights.size else 0.0
    mean_res = float(np.mean(np.abs(residuals[selected_indices]))) if selected_indices else 0.0
    return {
        "trace": metrics["trace"],
        "determinant": metrics["determinant"],
        "isotropy": metrics["isotropy"],
        "diversity": diversity,
        "mean_reliability": mean_rel,
        "mean_residual": mean_res,
    }


def _normalize_score_weights(
    score_weights: dict[str, float] | tuple[float, float, float, float] | list[float] | np.ndarray | None,
) -> np.ndarray:
    if score_weights is None:
        weights = np.asarray(DEFAULT_SCREENING_WEIGHTS, dtype=float)
    elif isinstance(score_weights, dict):
        weights = np.asarray([score_weights[key] for key in SCREENING_WEIGHT_KEYS], dtype=float)
    else:
        weights = np.asarray(score_weights, dtype=float)

    if weights.shape != (4,):
        raise ValueError("screening score weights must contain four entries")
    weights = np.maximum(weights, 1e-8)
    return weights / float(np.sum(weights))


def _combined_score(
    stats: dict[str, float],
    policy: str,
    score_weights: dict[str, float] | tuple[float, float, float, float] | list[float] | np.ndarray | None = None,
    determinant_scale: float = DEFAULT_DETERMINANT_SCALE,
    residual_scale: float = DEFAULT_RESIDUAL_SCALE,
) -> float:
    det_term = 1.0 - np.exp(-determinant_scale * max(stats["determinant"], 0.0))
    iso_term = float(np.clip(stats["isotropy"], 0.0, 1.0))
    div_term = float(np.clip(stats["diversity"], 0.0, 1.0))
    rel_term = float(np.clip(stats["mean_reliability"], 0.0, 1.0))
    res_good = 1.0 - float(np.clip(stats["mean_residual"] / residual_scale, 0.0, 1.0))

    if policy == "spread":
        return 0.75 * div_term + 0.25 * iso_term
    if policy == "crlb":
        return 0.75 * det_term + 0.25 * iso_term
    if policy == "observability_robust":
        weights = _normalize_score_weights(score_weights)
        return float(np.dot(weights, np.array([det_term, iso_term, rel_term, res_good], dtype=float)))
    raise ValueError(f"Unsupported policy: {policy}")


def _best_pair(
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    estimate: Point2D,
    reliability: np.ndarray,
    residuals: np.ndarray,
    policy: str,
    score_weights: dict[str, float] | tuple[float, float, float, float] | list[float] | np.ndarray | None = None,
    determinant_scale: float = DEFAULT_DETERMINANT_SCALE,
    residual_scale: float = DEFAULT_RESIDUAL_SCALE,
) -> tuple[list[int], float]:
    best_indices: list[int] | None = None
    best_score = float("-inf")
    for i, j in combinations(range(len(sensors)), 2):
        selected = [i, j]
        score = _combined_score(
            _subset_stats(selected, sensors, bearings, estimate, reliability, residuals),
            policy,
            score_weights=score_weights,
            determinant_scale=determinant_scale,
            residual_scale=residual_scale,
        )
        if score > best_score:
            best_score = score
            best_indices = selected
    if best_indices is None:
        return list(range(min(2, len(sensors)))), 0.0
    return best_indices, best_score


def _greedy_select(
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    estimate: Point2D,
    reliability: np.ndarray,
    residuals: np.ndarray,
    budget: int,
    policy: str,
    score_weights: dict[str, float] | tuple[float, float, float, float] | list[float] | np.ndarray | None = None,
    determinant_scale: float = DEFAULT_DETERMINANT_SCALE,
    residual_scale: float = DEFAULT_RESIDUAL_SCALE,
) -> SensorSubsetSelection:
    budget = int(max(3, min(budget, len(sensors))))
    if len(sensors) <= budget:
        stats = _subset_stats(list(range(len(sensors))), sensors, bearings, estimate, reliability, residuals)
        return SensorSubsetSelection(
            policy=policy,
            budget=budget,
            selected_indices=list(range(len(sensors))),
            score=_combined_score(
                stats,
                policy,
                score_weights=score_weights,
                determinant_scale=determinant_scale,
                residual_scale=residual_scale,
            ),
            observability=stats["determinant"],
            isotropy=stats["isotropy"],
            mean_reliability=stats["mean_reliability"],
            mean_residual=stats["mean_residual"],
            screening_triggered=True,
        )

    selected, best_score = _best_pair(
        sensors,
        bearings,
        estimate,
        reliability,
        residuals,
        policy,
        score_weights=score_weights,
        determinant_scale=determinant_scale,
        residual_scale=residual_scale,
    )
    remaining = [idx for idx in range(len(sensors)) if idx not in selected]

    while len(selected) < budget and remaining:
        candidate_choice: int | None = None
        candidate_score = float("-inf")
        for idx in remaining:
            subset = selected + [idx]
            score = _combined_score(
                _subset_stats(subset, sensors, bearings, estimate, reliability, residuals),
                policy,
                score_weights=score_weights,
                determinant_scale=determinant_scale,
                residual_scale=residual_scale,
            )
            if score > candidate_score:
                candidate_score = score
                candidate_choice = idx
        if candidate_choice is None:
            break
        selected.append(candidate_choice)
        remaining.remove(candidate_choice)
        best_score = candidate_score

    stats = _subset_stats(selected, sensors, bearings, estimate, reliability, residuals)
    return SensorSubsetSelection(
        policy=policy,
        budget=budget,
        selected_indices=selected,
        score=best_score,
        observability=stats["determinant"],
        isotropy=stats["isotropy"],
        mean_reliability=stats["mean_reliability"],
        mean_residual=stats["mean_residual"],
        screening_triggered=True,
    )


def _exhaustive_select(
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    estimate: Point2D,
    reliability: np.ndarray,
    residuals: np.ndarray,
    budget: int,
    policy: str,
    score_weights: dict[str, float] | tuple[float, float, float, float] | list[float] | np.ndarray | None = None,
    determinant_scale: float = DEFAULT_DETERMINANT_SCALE,
    residual_scale: float = DEFAULT_RESIDUAL_SCALE,
) -> SensorSubsetSelection:
    pool_order = np.argsort(-reliability)
    pool_size = min(len(sensors), max(budget + 2, 8))
    pool = sorted(pool_order[:pool_size].tolist())

    best_indices: list[int] | None = None
    best_score = float("-inf")
    for combo in combinations(pool, budget):
        selected = list(combo)
        score = _combined_score(
            _subset_stats(selected, sensors, bearings, estimate, reliability, residuals),
            policy,
            score_weights=score_weights,
            determinant_scale=determinant_scale,
            residual_scale=residual_scale,
        )
        if score > best_score:
            best_score = score
            best_indices = selected

    assert best_indices is not None
    stats = _subset_stats(best_indices, sensors, bearings, estimate, reliability, residuals)
    return SensorSubsetSelection(
        policy=policy,
        budget=budget,
        selected_indices=best_indices,
        score=best_score,
        observability=stats["determinant"],
        isotropy=stats["isotropy"],
        mean_reliability=stats["mean_reliability"],
        mean_residual=stats["mean_residual"],
        screening_triggered=True,
    )


def select_sensor_subset(
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    estimate: Point2D,
    budget: int,
    policy: str,
    seed: int = 0,
    bias: float = 0.0,
    huber_delta: float = 0.08,
    min_weight: float = 0.05,
    score_weights: dict[str, float] | tuple[float, float, float, float] | list[float] | np.ndarray | None = None,
    determinant_scale: float = DEFAULT_DETERMINANT_SCALE,
    residual_scale: float = DEFAULT_RESIDUAL_SCALE,
) -> SensorSubsetSelection:
    if len(sensors) < 3:
        raise ValueError("At least three sensors are required for subset selection")

    residuals, reliability = residual_reliability(
        sensors=sensors,
        bearings=bearings,
        estimate=estimate,
        huber_delta=huber_delta,
        bias=bias,
        min_weight=min_weight,
    )
    budget = int(max(3, min(budget, len(sensors))))

    if policy == "random":
        rng = np.random.default_rng(seed)
        selected = sorted(rng.choice(len(sensors), size=budget, replace=False).tolist())
        stats = _subset_stats(selected, sensors, bearings, estimate, reliability, residuals)
        return SensorSubsetSelection(
            policy=policy,
            budget=budget,
            selected_indices=selected,
            score=stats["mean_reliability"] + stats["diversity"],
            observability=stats["determinant"],
            isotropy=stats["isotropy"],
            mean_reliability=stats["mean_reliability"],
            mean_residual=stats["mean_residual"],
            screening_triggered=True,
        )

    if policy == "residual":
        selected = np.argsort(np.abs(residuals))[:budget].tolist()
        stats = _subset_stats(selected, sensors, bearings, estimate, reliability, residuals)
        return SensorSubsetSelection(
            policy=policy,
            budget=budget,
            selected_indices=selected,
            score=-stats["mean_residual"],
            observability=stats["determinant"],
            isotropy=stats["isotropy"],
            mean_reliability=stats["mean_reliability"],
            mean_residual=stats["mean_residual"],
            screening_triggered=True,
        )

    if policy == "reliability":
        selected = np.argsort(-reliability)[:budget].tolist()
        stats = _subset_stats(selected, sensors, bearings, estimate, reliability, residuals)
        return SensorSubsetSelection(
            policy=policy,
            budget=budget,
            selected_indices=selected,
            score=stats["mean_reliability"],
            observability=stats["determinant"],
            isotropy=stats["isotropy"],
            mean_reliability=stats["mean_reliability"],
            mean_residual=stats["mean_residual"],
            screening_triggered=True,
        )

    if policy == "adaptive":
        residual_mad = float(np.median(np.abs(residuals - np.median(residuals))))
        reliability_std = float(np.std(reliability))
        if residual_mad < 0.05 and reliability_std < 0.12:
            stats = _subset_stats(list(range(len(sensors))), sensors, bearings, estimate, reliability, residuals)
            return SensorSubsetSelection(
                policy=policy,
                budget=len(sensors),
                selected_indices=list(range(len(sensors))),
                score=_combined_score(
                    stats,
                    "observability_robust",
                    score_weights=score_weights,
                    determinant_scale=determinant_scale,
                    residual_scale=residual_scale,
                ),
                observability=stats["determinant"],
                isotropy=stats["isotropy"],
                mean_reliability=stats["mean_reliability"],
                mean_residual=stats["mean_residual"],
                screening_triggered=False,
            )
        selection = _greedy_select(
            sensors=sensors,
            bearings=bearings,
            estimate=estimate,
            reliability=reliability,
            residuals=residuals,
            budget=budget,
            policy="observability_robust",
            score_weights=score_weights,
            determinant_scale=determinant_scale,
            residual_scale=residual_scale,
        )
        selection.policy = policy
        selection.screening_triggered = True
        return selection

    if policy == "observability_robust":
        return _exhaustive_select(
            sensors=sensors,
            bearings=bearings,
            estimate=estimate,
            reliability=reliability,
            residuals=residuals,
            budget=budget,
            policy=policy,
            score_weights=score_weights,
            determinant_scale=determinant_scale,
            residual_scale=residual_scale,
        )

    if policy in {"spread", "crlb"}:
        return _greedy_select(
            sensors=sensors,
            bearings=bearings,
            estimate=estimate,
            reliability=reliability,
            residuals=residuals,
            budget=budget,
            policy=policy,
            score_weights=score_weights,
            determinant_scale=determinant_scale,
            residual_scale=residual_scale,
        )

    raise ValueError(f"Unsupported selection policy: {policy}")
