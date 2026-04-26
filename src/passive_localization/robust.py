from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import MethodConfig
from .geometry import Point2D, Sensor2D, bearing_jacobian, pairwise_intersections, wrap_angle


@dataclass
class RefinedEstimate:
    point: Point2D
    residual: float
    method: str
    bias: float = 0.0
    kept_measurements: int | None = None
    removed_measurements: int | None = None
    removed_indices: list[int] | None = None


def _bearing_residual(point: np.ndarray, sensors: list[Sensor2D], bearings: np.ndarray) -> np.ndarray:
    sensor_xy = np.array([[sensor.x, sensor.y] for sensor in sensors], dtype=float)
    pred = np.arctan2(point[1] - sensor_xy[:, 1], point[0] - sensor_xy[:, 0])
    return wrap_angle(pred - bearings)


def _bearing_residual_with_bias(point: np.ndarray, bias: float, sensors: list[Sensor2D], bearings: np.ndarray) -> np.ndarray:
    return wrap_angle(_bearing_residual(point, sensors, bearings) - bias)


def _mean_abs_residual(point: np.ndarray, sensors: list[Sensor2D], bearings: np.ndarray, bias: float = 0.0) -> float:
    return float(np.mean(np.abs(_bearing_residual_with_bias(point, bias, sensors, bearings))))


def _absolute_residual_stats(residuals: np.ndarray) -> tuple[float, float, float, float]:
    abs_res = np.abs(residuals)
    median = float(np.median(abs_res))
    mad = float(np.median(np.abs(abs_res - median)))
    p90 = float(np.percentile(abs_res, 90))
    return median, mad, p90, float(np.mean(abs_res))


def _trim_indices(residuals: np.ndarray, trim_ratio: float) -> np.ndarray:
    if trim_ratio <= 0.0:
        return np.array([], dtype=int)
    n_trim = int(np.floor(trim_ratio * residuals.size))
    if n_trim == 0 and residuals.size >= 4:
        n_trim = 1
    n_trim = min(n_trim, max(0, residuals.size - 3))
    if n_trim <= 0:
        return np.array([], dtype=int)
    idx = np.argsort(np.abs(residuals))
    return idx[-n_trim:]


def _reweight_from_residuals(residuals: np.ndarray, huber_delta: float, min_weight: float) -> np.ndarray:
    abs_res = np.abs(residuals)
    weights = np.ones_like(abs_res)
    large = abs_res > huber_delta
    weights[large] = huber_delta / np.maximum(abs_res[large], 1e-8)
    return np.maximum(weights, min_weight)


def _tukey_weights(residuals: np.ndarray, c: float, min_weight: float) -> np.ndarray:
    abs_res = np.abs(residuals)
    scaled = abs_res / max(c, 1e-8)
    weights = np.zeros_like(abs_res)
    active = scaled < 1.0
    weights[active] = (1.0 - scaled[active] ** 2) ** 2
    return np.maximum(weights, min_weight * (weights > 0.0))


def _circular_weighted_mean(residuals: np.ndarray, weights: np.ndarray) -> float:
    if residuals.size == 0:
        return 0.0
    comp = np.sum(weights * np.exp(1j * residuals))
    if abs(comp) < 1e-12:
        return 0.0
    return float(np.angle(comp))


def _gauss_newton_step(
    point: np.ndarray,
    bias: float,
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    weights: np.ndarray,
    config: MethodConfig,
    estimate_bias: bool,
) -> tuple[np.ndarray, float]:
    residuals = _bearing_residual_with_bias(point, bias, sensors, bearings)
    active = weights > 0.0
    if int(np.sum(active)) < 2:
        return np.zeros(2, dtype=float), 0.0

    rows = []
    rhs = []
    point_obj = Point2D(float(point[0]), float(point[1]))
    for idx, sensor in enumerate(sensors):
        if not active[idx]:
            continue
        jac = bearing_jacobian(sensor, point_obj)
        if not np.isfinite(jac).all():
            continue
        sqrt_w = float(np.sqrt(max(weights[idx], 1e-12)))
        if estimate_bias:
            rows.append(sqrt_w * np.array([jac[0], jac[1], -1.0], dtype=float))
        else:
            rows.append(sqrt_w * np.array([jac[0], jac[1]], dtype=float))
        rhs.append(sqrt_w * float(residuals[idx]))

    if not rows:
        return np.zeros(2, dtype=float), 0.0

    mat = np.vstack(rows)
    vec = np.array(rhs, dtype=float)
    damping = config.lm_damping * np.eye(mat.shape[1], dtype=float)
    delta = -np.linalg.solve(mat.T @ mat + damping, mat.T @ vec)

    if estimate_bias:
        step_point = delta[:2]
        step_bias = float(delta[2])
    else:
        step_point = delta[:2]
        step_bias = 0.0

    norm = float(np.linalg.norm(step_point))
    if norm > config.max_step_norm:
        step_point = step_point * (config.max_step_norm / max(norm, 1e-12))

    return step_point, step_bias


def _candidate_points(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray) -> list[np.ndarray]:
    candidates = [initial.as_array().copy()]
    intersections = pairwise_intersections(sensors, bearings)
    if intersections:
        inter_stack = np.vstack(intersections)
        candidates.append(np.median(inter_stack, axis=0))
        if len(intersections) >= 3:
            center = np.mean(inter_stack, axis=0)
            dists = np.linalg.norm(inter_stack - center, axis=1)
            keep = dists <= np.percentile(dists, 60)
            if np.any(keep):
                candidates.append(np.mean(inter_stack[keep], axis=0))

    uniq: list[np.ndarray] = []
    for cand in candidates:
        if not any(np.linalg.norm(cand - prev) < 1e-6 for prev in uniq):
            uniq.append(np.asarray(cand, dtype=float))
    return uniq


def _ransac_inlier_hypothesis(
    sensors: list[Sensor2D],
    bearings: np.ndarray,
    config: MethodConfig,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray] | None:
    rng = np.random.default_rng(seed)
    intersections = pairwise_intersections(sensors, bearings)
    if not intersections:
        return None

    best_inliers: np.ndarray | None = None
    best_candidate: np.ndarray | None = None
    best_score: tuple[int, float] | None = None
    threshold = config.ransac_inlier_threshold

    for _ in range(max(config.ransac_iterations, len(intersections))):
        candidate = np.asarray(intersections[rng.integers(0, len(intersections))], dtype=float)
        residuals = np.abs(_bearing_residual(candidate, sensors, bearings))
        inliers = residuals <= threshold
        score = (int(np.sum(inliers)), -float(np.mean(residuals[inliers])) if np.any(inliers) else float("inf"))
        if best_score is None or score > best_score:
            best_score = score
            best_inliers = inliers
            best_candidate = candidate

    assert best_candidate is not None
    assert best_inliers is not None
    if int(np.sum(best_inliers)) < 3:
        residuals = np.abs(_bearing_residual(best_candidate, sensors, bearings))
        chosen = np.argsort(residuals)[: min(3, len(sensors))]
        best_inliers = np.zeros(len(sensors), dtype=bool)
        best_inliers[chosen] = True
    return best_candidate, best_inliers


def least_squares_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig) -> RefinedEstimate:
    point = initial.as_array().copy()
    weights = np.ones(len(bearings), dtype=float)
    for _ in range(config.ls_iterations):
        step_point, _ = _gauss_newton_step(point, 0.0, sensors, bearings, weights, config, estimate_bias=False)
        point += step_point
        if float(np.linalg.norm(step_point)) < 1e-6:
            break
    residual = _mean_abs_residual(point, sensors, bearings)
    return RefinedEstimate(point=Point2D(float(point[0]), float(point[1])), residual=residual, method="least_squares")


def robust_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig) -> RefinedEstimate:
    point = initial.as_array().copy()
    weights = np.ones(len(bearings), dtype=float)
    for _ in range(config.ls_iterations):
        residuals = _bearing_residual(point, sensors, bearings)
        weights = _reweight_from_residuals(residuals, config.huber_delta, config.min_weight)
        step_point, _ = _gauss_newton_step(point, 0.0, sensors, bearings, weights, config, estimate_bias=False)
        point += step_point
        if float(np.linalg.norm(step_point)) < 1e-6:
            break
    residual = _mean_abs_residual(point, sensors, bearings)
    return RefinedEstimate(point=Point2D(float(point[0]), float(point[1])), residual=residual, method="robust_huber")


def tukey_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig) -> RefinedEstimate:
    point = initial.as_array().copy()
    weights = np.ones(len(bearings), dtype=float)
    for _ in range(config.ls_iterations):
        residuals = _bearing_residual(point, sensors, bearings)
        weights = _tukey_weights(residuals, config.tukey_c, config.min_weight)
        step_point, _ = _gauss_newton_step(point, 0.0, sensors, bearings, weights, config, estimate_bias=False)
        point += step_point
        if float(np.linalg.norm(step_point)) < 1e-6:
            break
    residual = _mean_abs_residual(point, sensors, bearings)
    return RefinedEstimate(point=Point2D(float(point[0]), float(point[1])), residual=residual, method="tukey_irls")


def pure_ransac_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig, seed: int = 0) -> RefinedEstimate:
    hypothesis = _ransac_inlier_hypothesis(sensors, bearings, config, seed=seed)
    if hypothesis is None:
        return least_squares_refine(initial, sensors, bearings, config)
    best_candidate, best_inliers = hypothesis
    residual = _mean_abs_residual(best_candidate, sensors, bearings)
    return RefinedEstimate(
        point=Point2D(float(best_candidate[0]), float(best_candidate[1])),
        residual=residual,
        method="pure_ransac",
        kept_measurements=int(np.sum(best_inliers)),
        removed_measurements=int(len(sensors) - np.sum(best_inliers)),
        removed_indices=[idx for idx, keep in enumerate(best_inliers.tolist()) if not keep],
    )


def ransac_lm_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig, seed: int = 0) -> RefinedEstimate:
    hypothesis = _ransac_inlier_hypothesis(sensors, bearings, config, seed=seed)
    if hypothesis is None:
        return least_squares_refine(initial, sensors, bearings, config)
    best_candidate, best_inliers = hypothesis
    inlier_sensors = [sensor for sensor, keep in zip(sensors, best_inliers) if keep]
    inlier_bearings = bearings[best_inliers]
    refined = least_squares_refine(Point2D(float(best_candidate[0]), float(best_candidate[1])), inlier_sensors, inlier_bearings, config)
    residual = _mean_abs_residual(refined.point.as_array(), sensors, bearings)
    return RefinedEstimate(
        point=refined.point,
        residual=residual,
        method="ransac_lm",
        kept_measurements=int(np.sum(best_inliers)),
        removed_measurements=int(len(sensors) - np.sum(best_inliers)),
        removed_indices=[idx for idx, keep in enumerate(best_inliers.tolist()) if not keep],
    )


def robust_bias_trimmed_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig) -> RefinedEstimate:
    best_estimate: RefinedEstimate | None = None
    ls_estimate = least_squares_refine(initial, sensors, bearings, config)
    gnc_estimate = gnc_geman_mcclure_refine(initial, sensors, bearings, config)
    ls_residuals = _bearing_residual(ls_estimate.point.as_array(), sensors, bearings)
    ls_med, ls_mad, ls_p90, ls_mean = _absolute_residual_stats(ls_residuals)

    candidate_states: list[tuple[np.ndarray, list[int] | None]] = [(cand, None) for cand in _candidate_points(initial, sensors, bearings)]
    consensus_estimate: RefinedEstimate | None = None
    if config.use_consensus_seed and len(sensors) >= 4:
        consensus_estimate = ransac_refine(initial, sensors, bearings, config, seed=0)
        candidate_states.append((consensus_estimate.point.as_array(), consensus_estimate.removed_indices))
    smooth_candidates = [ls_estimate, gnc_estimate]
    if consensus_estimate is not None:
        smooth_candidates.append(consensus_estimate)
    smooth_choice = min(smooth_candidates, key=lambda estimate: estimate.residual)

    coherent_window = (
        ls_med <= 0.58 * config.huber_delta
        and ls_mad <= 0.32 * config.huber_delta
        and ls_p90 <= 1.65 * config.huber_delta
        and ls_mean <= 0.95 * config.huber_delta
    )
    if coherent_window:
        return RefinedEstimate(
            point=smooth_choice.point,
            residual=smooth_choice.residual,
            method="robust_bias_trimmed",
            bias=0.0,
            kept_measurements=smooth_choice.kept_measurements,
            removed_measurements=smooth_choice.removed_measurements,
            removed_indices=smooth_choice.removed_indices,
        )

    for start_point, removed_hint in candidate_states:
        point = start_point.copy()
        bias = 0.0
        weights = np.ones(len(bearings), dtype=float)
        removed_indices: list[int] = list(removed_hint or [])
        if removed_indices:
            weights[np.array(removed_indices, dtype=int)] = 0.0

        for _ in range(max(1, config.reweight_iterations)):
            raw_residuals = _bearing_residual(point, sensors, bearings)
            if config.estimate_bias:
                active_raw = raw_residuals[weights > 0]
                if active_raw.size >= 3 and float(np.std(active_raw)) <= 1.8 * config.huber_delta:
                    bias = _circular_weighted_mean(raw_residuals, weights)
                else:
                    bias = 0.0
            residuals = _bearing_residual_with_bias(point, bias, sensors, bearings)
            trim_idx = _trim_indices(residuals, config.trim_ratio)
            severe_idx = np.where(np.abs(residuals) > max(1.75 * config.huber_delta, np.percentile(np.abs(residuals), 78)))[0]
            if severe_idx.size:
                trim_idx = np.unique(np.concatenate((trim_idx, severe_idx)))
                if trim_idx.size > len(residuals) - 3:
                    order = np.argsort(np.abs(residuals))
                    trim_idx = np.sort(order[-(len(residuals) - 3) :])
            current_weights = _tukey_weights(residuals, max(config.tukey_c, 2.0 * config.huber_delta), config.min_weight)
            if trim_idx.size:
                current_weights[trim_idx] = 0.0
                removed_indices = sorted(set(removed_indices).union(int(i) for i in trim_idx.tolist()))

            for _inner in range(max(1, config.ls_iterations // 4)):
                step_point, step_bias = _gauss_newton_step(
                    point,
                    bias,
                    sensors,
                    bearings,
                    current_weights,
                    config,
                    estimate_bias=config.estimate_bias,
                )
                point += step_point
                if config.estimate_bias:
                    bias = float(wrap_angle(np.array([bias + step_bias]))[0])
                else:
                    bias = 0.0
                if float(np.linalg.norm(step_point)) < 1e-6 and abs(step_bias) < 1e-6:
                    break

            weights = current_weights

        final_residuals = _bearing_residual_with_bias(point, bias, sensors, bearings)
        active = weights > 0
        if np.any(active):
            residual = float(np.mean(np.abs(final_residuals[active])))
        else:
            residual = float(np.mean(np.abs(final_residuals)))
        kept = int(np.sum(active))
        removed = int(len(bearings) - kept)
        estimate = RefinedEstimate(
            point=Point2D(float(point[0]), float(point[1])),
            residual=residual,
            method="robust_bias_trimmed",
            bias=float(bias),
            kept_measurements=kept,
            removed_measurements=removed,
            removed_indices=removed_indices or None,
        )
        if best_estimate is None or estimate.residual < best_estimate.residual:
            best_estimate = estimate

    assert best_estimate is not None
    if consensus_estimate is not None:
        best_residuals = np.abs(_bearing_residual(best_estimate.point.as_array(), sensors, bearings))
        severe_fraction = float(np.mean(best_residuals > 1.75 * config.huber_delta))
        point_gap = float(
            np.linalg.norm(best_estimate.point.as_array() - consensus_estimate.point.as_array())
        )
        residual_gap_small = consensus_estimate.residual <= best_estimate.residual + 0.03
        heavy_pruning = (best_estimate.removed_measurements or 0) >= max(2, int(0.25 * len(sensors)))
        suspicious_bias = abs(best_estimate.bias) >= 0.08
        if severe_fraction >= 0.12 or (best_estimate.removed_measurements or 0) >= max(1, int(0.2 * len(sensors))):
            return RefinedEstimate(
                point=consensus_estimate.point,
                residual=consensus_estimate.residual,
                method="robust_bias_trimmed",
                bias=0.0,
                kept_measurements=consensus_estimate.kept_measurements,
                removed_measurements=consensus_estimate.removed_measurements,
                removed_indices=consensus_estimate.removed_indices,
            )
        if point_gap > 1.0 and residual_gap_small and (heavy_pruning or suspicious_bias):
            return RefinedEstimate(
                point=consensus_estimate.point,
                residual=consensus_estimate.residual,
                method="robust_bias_trimmed",
                bias=0.0,
                kept_measurements=consensus_estimate.kept_measurements,
                removed_measurements=consensus_estimate.removed_measurements,
                removed_indices=consensus_estimate.removed_indices,
            )
    point_gap_to_smooth = float(np.linalg.norm(best_estimate.point.as_array() - smooth_choice.point.as_array()))
    light_residual_advantage = best_estimate.residual <= smooth_choice.residual + 0.010
    aggressive_pruning = (best_estimate.removed_measurements or 0) >= max(2, int(0.22 * len(sensors)))
    if aggressive_pruning and point_gap_to_smooth > 0.65 and not light_residual_advantage:
        return RefinedEstimate(
            point=smooth_choice.point,
            residual=smooth_choice.residual,
            method="robust_bias_trimmed",
            bias=0.0,
            kept_measurements=smooth_choice.kept_measurements,
            removed_measurements=smooth_choice.removed_measurements,
            removed_indices=smooth_choice.removed_indices,
        )
    if best_estimate.residual + 0.015 >= smooth_choice.residual:
        return RefinedEstimate(
            point=smooth_choice.point,
            residual=smooth_choice.residual,
            method="robust_bias_trimmed",
            bias=0.0,
            kept_measurements=smooth_choice.kept_measurements,
            removed_measurements=smooth_choice.removed_measurements,
            removed_indices=smooth_choice.removed_indices,
        )
    if smooth_choice.residual + 0.008 < best_estimate.residual:
        return RefinedEstimate(
            point=smooth_choice.point,
            residual=smooth_choice.residual,
            method="robust_bias_trimmed",
            bias=0.0,
            kept_measurements=smooth_choice.kept_measurements,
            removed_measurements=smooth_choice.removed_measurements,
            removed_indices=smooth_choice.removed_indices,
        )
    if consensus_estimate is not None and consensus_estimate.residual + 1e-6 < best_estimate.residual:
        return RefinedEstimate(
            point=consensus_estimate.point,
            residual=consensus_estimate.residual,
            method="robust_bias_trimmed",
            bias=0.0,
            kept_measurements=consensus_estimate.kept_measurements,
            removed_measurements=consensus_estimate.removed_measurements,
            removed_indices=consensus_estimate.removed_indices,
        )
    return best_estimate


def ransac_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig, seed: int = 0) -> RefinedEstimate:
    hypothesis = _ransac_inlier_hypothesis(sensors, bearings, config, seed=seed)
    if hypothesis is None:
        return robust_refine(initial, sensors, bearings, config)
    best_candidate, best_inliers = hypothesis

    inlier_sensors = [sensor for sensor, keep in zip(sensors, best_inliers) if keep]
    inlier_bearings = bearings[best_inliers]
    refined = robust_refine(Point2D(float(best_candidate[0]), float(best_candidate[1])), inlier_sensors, inlier_bearings, config)
    residual = _mean_abs_residual(refined.point.as_array(), sensors, bearings)
    return RefinedEstimate(
        point=refined.point,
        residual=residual,
        method="ransac",
        kept_measurements=int(np.sum(best_inliers)),
        removed_measurements=int(len(sensors) - np.sum(best_inliers)),
        removed_indices=[idx for idx, keep in enumerate(best_inliers.tolist()) if not keep],
    )


def pso_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig, seed: int = 0) -> RefinedEstimate:
    rng = np.random.default_rng(seed)
    center = initial.as_array()
    particles = center + rng.normal(0.0, 2.0, size=(config.pso_particles, 2))
    velocities = rng.normal(0.0, 0.3, size=(config.pso_particles, 2))
    personal_best = particles.copy()
    personal_scores = np.array([_mean_abs_residual(p, sensors, bearings) for p in particles])
    global_idx = int(np.argmin(personal_scores))
    global_best = personal_best[global_idx].copy()

    for _ in range(config.pso_iterations):
        r1 = rng.random(size=particles.shape)
        r2 = rng.random(size=particles.shape)
        velocities = 0.6 * velocities + 1.2 * r1 * (personal_best - particles) + 1.2 * r2 * (global_best - particles)
        particles = particles + velocities
        scores = np.array([_mean_abs_residual(p, sensors, bearings) for p in particles])
        improved = scores < personal_scores
        personal_best[improved] = particles[improved]
        personal_scores[improved] = scores[improved]
        global_idx = int(np.argmin(personal_scores))
        global_best = personal_best[global_idx].copy()

    residual = _mean_abs_residual(global_best, sensors, bearings)
    return RefinedEstimate(point=Point2D(float(global_best[0]), float(global_best[1])), residual=residual, method="pso")


def simulated_annealing_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig, seed: int = 0) -> RefinedEstimate:
    rng = np.random.default_rng(seed)
    current = initial.as_array().copy()
    current_score = _mean_abs_residual(current, sensors, bearings)
    best = current.copy()
    best_score = current_score

    for step_idx in range(config.sa_iterations):
        temp = max(1e-3, 1.0 - step_idx / max(1, config.sa_iterations))
        proposal = current + rng.normal(0.0, config.sa_step * temp, size=2)
        score = _mean_abs_residual(proposal, sensors, bearings)
        delta = score - current_score
        if delta < 0.0 or rng.random() < np.exp(-delta / max(temp, 1e-4)):
            current = proposal
            current_score = score
            if score < best_score:
                best = proposal
                best_score = score

    residual = _mean_abs_residual(best, sensors, bearings)
    return RefinedEstimate(point=Point2D(float(best[0]), float(best[1])), residual=residual, method="simulated_annealing")


def gnc_geman_mcclure_refine(initial: Point2D, sensors: list[Sensor2D], bearings: np.ndarray, config: MethodConfig) -> RefinedEstimate:
    point = initial.as_array().copy()
    mu = config.gnc_mu_initial
    for _outer in range(max(1, config.gnc_outer_iterations)):
        for _inner in range(max(1, config.gnc_inner_iterations)):
            residuals = _bearing_residual(point, sensors, bearings)
            abs_r = np.abs(residuals)
            w = 1.0 / (1.0 + (abs_r / max(mu, 1e-12)) ** 2)
            w = np.maximum(w, config.gnc_floor_weight)
            step_point, _ = _gauss_newton_step(point, 0.0, sensors, bearings, w, config, estimate_bias=False)
            point += step_point
            if float(np.linalg.norm(step_point)) < 1e-6:
                break
        mu = max(1e-3, mu * config.gnc_mu_decay)
    residual = _mean_abs_residual(point, sensors, bearings)
    return RefinedEstimate(point=Point2D(float(point[0]), float(point[1])), residual=residual, method="gnc_gm")
