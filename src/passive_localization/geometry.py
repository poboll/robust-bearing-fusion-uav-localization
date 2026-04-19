from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass
class Point2D:
    x: float
    y: float

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)


@dataclass
class Sensor2D:
    x: float
    y: float
    name: str = ""

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)


def wrap_angle(angle: np.ndarray | float) -> np.ndarray | float:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def bearing_from_sensor(sensor: Sensor2D, target: Point2D) -> float:
    delta = target.as_array() - sensor.as_array()
    return float(np.arctan2(delta[1], delta[0]))


def line_from_bearing(sensor: Sensor2D, bearing: float) -> tuple[np.ndarray, np.ndarray]:
    origin = sensor.as_array()
    direction = np.array([np.cos(bearing), np.sin(bearing)], dtype=float)
    return origin, direction


def _pairwise_intersection(sensor_a: Sensor2D, bearing_a: float, sensor_b: Sensor2D, bearing_b: float) -> np.ndarray | None:
    origin_a, dir_a = line_from_bearing(sensor_a, bearing_a)
    origin_b, dir_b = line_from_bearing(sensor_b, bearing_b)
    mat = np.column_stack((dir_a, -dir_b))
    det = np.linalg.det(mat)
    if abs(det) < 1e-8:
        return None
    rhs = origin_b - origin_a
    params = np.linalg.solve(mat, rhs)
    return origin_a + params[0] * dir_a


def pairwise_intersections(sensors: Iterable[Sensor2D], bearings: Iterable[float]) -> list[np.ndarray]:
    sensors = list(sensors)
    bearings = list(bearings)
    intersections: list[np.ndarray] = []

    for i in range(len(sensors)):
        for j in range(i + 1, len(sensors)):
            inter = _pairwise_intersection(sensors[i], bearings[i], sensors[j], bearings[j])
            if inter is not None and np.isfinite(inter).all():
                intersections.append(inter)

    return intersections


def geometric_initialization(sensors: Iterable[Sensor2D], bearings: Iterable[float]) -> Point2D:
    """Estimate target position from pairwise line intersections.

    This gives a transparent closed-form style initializer suitable as the
    first stage of a passive bearing-only localization pipeline.
    """
    sensors = list(sensors)
    bearings = list(bearings)
    intersections = pairwise_intersections(sensors, bearings)

    if not intersections:
        if sensors:
            center = np.mean(np.array([sensor.as_array() for sensor in sensors]), axis=0)
            return Point2D(float(center[0]), float(center[1]))
        return Point2D(0.0, 0.0)

    centroid = np.mean(np.vstack(intersections), axis=0)
    return Point2D(float(centroid[0]), float(centroid[1]))


def bearing_jacobian(sensor: Sensor2D, point: Point2D) -> np.ndarray:
    """Jacobian of a 2D bearing measurement with respect to target position."""
    delta = point.as_array() - sensor.as_array()
    r2 = float(np.dot(delta, delta))
    if r2 < 1e-10:
        return np.zeros(2, dtype=float)
    return np.array([-delta[1] / r2, delta[0] / r2], dtype=float)


def fim_matrix(sensors: Iterable[Sensor2D], point: Point2D, weights: Iterable[float] | None = None) -> np.ndarray:
    """Build a Fisher-information-style geometry matrix for bearing measurements."""
    sensors = list(sensors)
    if not sensors:
        return np.zeros((2, 2), dtype=float)

    jac = np.vstack([bearing_jacobian(sensor, point) for sensor in sensors])
    if weights is None:
        return jac.T @ jac

    weights = np.asarray(list(weights), dtype=float)
    if weights.size != len(sensors):
        raise ValueError("weights must match the number of sensors")
    return jac.T @ (weights[:, None] * jac)


def observability_metrics(sensors: Iterable[Sensor2D], point: Point2D) -> dict[str, float]:
    """Simple geometry-quality diagnostics for bearing-only localization.

    These metrics are intended for analysis and interpretation, not for
    replacing the estimation method itself.
    """
    return weighted_observability_metrics(sensors, point)


def weighted_observability_metrics(
    sensors: Iterable[Sensor2D],
    point: Point2D,
    weights: Iterable[float] | None = None,
) -> dict[str, float]:
    """Geometry-quality diagnostics with optional per-sensor reliability weights."""
    sensors = list(sensors)
    if len(sensors) < 2:
        return {
            "trace": 0.0,
            "determinant": 0.0,
            "condition_number": float("inf"),
            "min_eigenvalue": 0.0,
            "max_eigenvalue": 0.0,
            "isotropy": 0.0,
        }

    fim = fim_matrix(sensors, point, weights=weights)
    eigvals = np.linalg.eigvalsh(fim)
    eigvals = np.maximum(eigvals, 0.0)
    min_eig = float(eigvals[0])
    max_eig = float(eigvals[-1])
    cond = float(max_eig / max(min_eig, 1e-12)) if max_eig > 0 else float("inf")
    isotropy = float(min_eig / max(max_eig, 1e-12))
    return {
        "trace": float(np.trace(fim)),
        "determinant": float(np.linalg.det(fim)),
        "condition_number": cond,
        "min_eigenvalue": min_eig,
        "max_eigenvalue": max_eig,
        "isotropy": isotropy,
    }
