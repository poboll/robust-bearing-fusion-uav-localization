"""Generate publication-style plots from experiment outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parent
EXP = ROOT / "experiments"
SUBMISSION_FIG = ROOT / "submission" / "figures"
PUBLIC_DATASET_ROOT = ROOT / "data" / "public_dataset3"
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from passive_localization.config import MethodConfig, ScenarioConfig
from passive_localization.geometry import geometric_initialization
from passive_localization.robust import robust_bias_trimmed_refine
from passive_localization.scenario import generate_circular_scenario
from passive_localization.schedule import select_sensor_subset

TAB10 = list(plt.get_cmap("tab10").colors)
PALETTE = {
    "ls": TAB10[7],
    "huber": TAB10[9],
    "robust": TAB10[2],
    "tukey": TAB10[8],
    "ransac": TAB10[3],
    "gnc": TAB10[4],
    "pso": TAB10[1],
    "sa": TAB10[5],
    "active_all": TAB10[7],
    "active_random": TAB10[8],
    "active_spread": TAB10[0],
    "active_crlb": TAB10[4],
    "active_residual": TAB10[3],
    "active_reliability": TAB10[9],
    "active_proposed": TAB10[2],
    "active_adaptive": TAB10[5],
}

plt.rcParams.update(
    {
        "font.family": "STIXGeneral",
        "axes.edgecolor": "#CBD5E1",
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": "#FCFCFD",
        "figure.facecolor": "white",
        "axes.titleweight": "semibold",
        "axes.labelsize": 12.5,
        "axes.titlesize": 14.5,
        "axes.labelcolor": "#0F172A",
        "text.color": "#0F172A",
        "legend.fontsize": 10.5,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "xtick.color": "#334155",
        "ytick.color": "#334155",
        "grid.color": "#CBD5E1",
        "grid.linewidth": 0.7,
        "savefig.bbox": "tight",
    }
)


def _save(fig: plt.Figure, name: str) -> None:
    stem = Path(name).stem
    fig.tight_layout()
    SUBMISSION_FIG.mkdir(parents=True, exist_ok=True)
    for suffix in [".png", ".pdf", ".svg"]:
        out = EXP / f"{stem}{suffix}"
        sub_out = SUBMISSION_FIG / f"{stem}{suffix}"
        save_kwargs = {"facecolor": "white"}
        if suffix == ".png":
            save_kwargs["dpi"] = 400
        fig.savefig(out, **save_kwargs)
        fig.savefig(sub_out, **save_kwargs)
    plt.close(fig)


def _box(
    ax,
    xy: tuple[float, float],
    wh: tuple[float, float],
    text: str,
    fc: str,
    ec: str = "#334155",
    lw: float = 1.2,
    fs: int = 10,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        xy,
        wh[0],
        wh[1],
        boxstyle="round,pad=0.02,rounding_size=0.025",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + wh[0] / 2.0,
        xy[1] + wh[1] / 2.0,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        color="#0F172A",
        linespacing=1.15,
    )
    return patch


def _arrow(ax, start: tuple[float, float], end: tuple[float, float], color: str = "#475569", lw: float = 1.6) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=lw,
            color=color,
            shrinkA=4,
            shrinkB=4,
        )
    )


def _empirical_cdf(values: list[float] | np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    arr = np.sort(np.asarray(values, dtype=float))
    if arr.size == 0:
        return np.array([], dtype=float), np.array([], dtype=float)
    cdf = np.arange(1, arr.size + 1, dtype=float) / float(arr.size)
    return arr, cdf


def _selection_regime_kwargs(name: str) -> dict[str, float]:
    if name == "mixed":
        return dict(bias=0.04, missing_rate=0.2, outlier_rate=0.2, outlier_scale=0.45)
    if name == "severe":
        return dict(bias=0.06, missing_rate=0.25, outlier_rate=0.3, outlier_scale=0.6)
    raise ValueError(f"Unsupported selection regime: {name}")


def _replay_selection_case(row: dict) -> dict:
    scenario_cfg = ScenarioConfig(
        seed=int(row["seed"]),
        num_uavs=int(row["num_uavs"]),
        formation_type=str(row["formation"]),
        formation_jitter=1.2 if str(row["formation"]) == "perturbed" else 0.0,
        target_mode="random_interior",
        **_selection_regime_kwargs(str(row["regime"])),
    )
    scenario = generate_circular_scenario(scenario_cfg)
    valid_indices = [idx for idx, keep in enumerate(scenario.valid_mask.tolist()) if keep]
    valid_sensors = [scenario.sensors[idx] for idx in valid_indices]
    valid_bearings = scenario.observed_bearings[scenario.valid_mask]
    method_cfg = MethodConfig()
    initial = geometric_initialization(valid_sensors, valid_bearings)
    pilot = robust_bias_trimmed_refine(initial, valid_sensors, valid_bearings, method_cfg)
    target = scenario.target.as_array()
    budget = int(row["budget"])

    estimates: dict[str, dict] = {
        "all_sensors": {
            "selected_indices": list(range(len(valid_sensors))),
            "point": pilot.point.as_array(),
            "error": float(np.linalg.norm(pilot.point.as_array() - target)),
            "triggered": False,
        }
    }
    for policy in ["spread", "crlb", "residual", "reliability", "observability_robust", "adaptive"]:
        selection = select_sensor_subset(
            sensors=valid_sensors,
            bearings=valid_bearings,
            estimate=pilot.point,
            budget=budget,
            policy=policy,
            seed=int(row["seed"]),
            bias=pilot.bias,
            huber_delta=method_cfg.huber_delta,
            min_weight=method_cfg.min_weight,
        )
        chosen_sensors = [valid_sensors[idx] for idx in selection.selected_indices]
        chosen_bearings = valid_bearings[selection.selected_indices]
        initial_sel = geometric_initialization(chosen_sensors, chosen_bearings)
        refined = robust_bias_trimmed_refine(initial_sel, chosen_sensors, chosen_bearings, method_cfg)
        estimates[policy] = {
            "selected_indices": selection.selected_indices,
            "point": refined.point.as_array(),
            "error": float(np.linalg.norm(refined.point.as_array() - target)),
            "triggered": bool(selection.screening_triggered),
        }

    return {
        "scenario": scenario,
        "target": target,
        "valid_sensors": valid_sensors,
        "valid_bearings": valid_bearings,
        "budget": budget,
        "row": row,
        "estimates": estimates,
    }


def plot_system_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 4.2))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    _box(
        ax,
        (0.03, 0.30),
        (0.17, 0.40),
        "Observer Pose Input\nGNSS / VIO / INS / SLAM\nreported with uncertainty",
        "#E2E8F0",
    )
    _box(
        ax,
        (0.24, 0.30),
        (0.17, 0.40),
        "Bearing Extraction\nEO / DF payloads\nasynchronous angle cues",
        "#DBEAFE",
    )
    _box(
        ax,
        (0.45, 0.16),
        (0.28, 0.68),
        "Corruption-Aware Front End",
        "#ECFDF5",
        ec="#047857",
        lw=1.6,
        fs=12,
    )
    _box(
        ax,
        (0.48, 0.48),
        (0.22, 0.22),
        "Stage 1\nConsensus-assisted\nrobust localization",
        "#D1FAE5",
        ec="#0F766E",
        fs=10,
    )
    _box(
        ax,
        (0.48, 0.20),
        (0.22, 0.18),
        "Stage 2 (optional)\nAdaptive fixed-budget\nmeasurement screening",
        "#DCFCE7",
        ec="#166534",
        fs=10,
    )
    _box(
        ax,
        (0.78, 0.42),
        (0.18, 0.18),
        "Downstream Target Cue\nposition estimate\nfor current cycle",
        "#FEF3C7",
        ec="#B45309",
    )
    _box(
        ax,
        (0.78, 0.14),
        (0.18, 0.18),
        "Consumers\ntracker / handoff /\nformation replanning",
        "#FDE68A",
        ec="#A16207",
    )

    _arrow(ax, (0.20, 0.50), (0.24, 0.50))
    _arrow(ax, (0.41, 0.50), (0.45, 0.50))
    _arrow(ax, (0.73, 0.50), (0.78, 0.50))
    _arrow(ax, (0.87, 0.42), (0.87, 0.32), color="#A16207")

    ax.text(
        0.59,
        0.82,
        "Corruption sources handled in this paper:\nmissing bearings, shared / heterogeneous bias, outliers, pose uncertainty",
        ha="center",
        va="center",
        fontsize=10,
        color="#065F46",
    )
    ax.text(
        0.59,
        0.08,
        "Engineering gate: keep all-sensor robust fusion when credibility spread is low; screen only when budget or heterogeneity justifies pruning.",
        ha="center",
        va="center",
        fontsize=9.5,
        color="#14532D",
    )
    _save(fig, "figure_system_pipeline.png")


def plot_frontend_flow() -> None:
    fig, ax = plt.subplots(figsize=(12.6, 4.8))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    _box(ax, (0.03, 0.34), (0.14, 0.28), "Current-cycle bearings\n+ reported poses", "#E0F2FE", ec="#0369A1")
    _box(ax, (0.21, 0.34), (0.15, 0.28), "Pairwise intersections\n+ consensus seeds", "#DBEAFE", ec="#2563EB")
    _box(ax, (0.40, 0.34), (0.16, 0.28), "Trimmed IRLS\nwith LM updates\nand optional bias", "#DCFCE7", ec="#15803D")
    _box(ax, (0.60, 0.60), (0.17, 0.20), "Residual / reliability gate\nheterogeneous window?", "#FEF3C7", ec="#B45309")
    _box(ax, (0.60, 0.14), (0.17, 0.20), "Keep all-sensor robust cue\n(default path)", "#E5E7EB", ec="#6B7280")
    _box(ax, (0.81, 0.56), (0.16, 0.24), "Stage 2 optional\nbudgeted subset search\n(FIM surrogate + residuals)", "#FCE7F3", ec="#BE185D")
    _box(ax, (0.81, 0.14), (0.16, 0.22), "Output cue for\ntracking / handoff /\nreplanning", "#FDE68A", ec="#A16207")

    _arrow(ax, (0.17, 0.48), (0.21, 0.48))
    _arrow(ax, (0.36, 0.48), (0.40, 0.48))
    _arrow(ax, (0.56, 0.48), (0.60, 0.68))
    _arrow(ax, (0.56, 0.48), (0.60, 0.24))
    _arrow(ax, (0.77, 0.68), (0.81, 0.68))
    _arrow(ax, (0.77, 0.24), (0.81, 0.24))
    _arrow(ax, (0.89, 0.56), (0.89, 0.36), color="#A16207")

    ax.text(0.69, 0.86, "Stage 1 is the core contribution; Stage 2 is only activated when budget or credibility dispersion justifies pruning.", ha="center", va="center", fontsize=10.2, color="#78350F")
    ax.text(0.69, 0.05, "Outputs are current-cycle localization cues, not a full autonomy stack or distributed swarm planner.", ha="center", va="center", fontsize=10.0, color="#475569")
    _save(fig, "figure_frontend_flow.png")


def plot_regime_comparison() -> None:
    payload = json.loads((EXP / "regime_comparison.json").read_text(encoding="utf-8"))
    regimes = ["clean", "biased", "missing", "outlier", "mixed"]
    methods = [
        ("least_squares_error", "LS"),
        ("robust_error", "Huber"),
        ("gnc_gm_error", "GNC-GM"),
        ("robust_bias_trimmed_error", "Proposed"),
    ]
    x = np.arange(len(regimes))
    width = 0.20
    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = [PALETTE["ls"], PALETTE["huber"], PALETTE["gnc"], PALETTE["robust"]]

    for idx, ((key, label), color) in enumerate(zip(methods, colors)):
        vals = [payload[r][key] for r in regimes]
        ax.bar(x + (idx - 1.5) * width, vals, width=width, label=label, color=color)

    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([r.title() for r in regimes])
    ax.set_ylabel("Localization Error (log scale)")
    ax.set_title("Regime Comparison")
    ax.legend(frameon=False, ncol=4)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    _save(fig, "figure_regime_comparison.png")


def plot_ablation_mixed() -> None:
    payload = json.loads((EXP / "ablation_summary.json").read_text(encoding="utf-8"))
    mixed = payload["mixed"]
    labels = ["default", "no_consensus", "no_bias", "no_trim", "light_rw"]
    keys = ["default", "no_consensus_seed", "no_bias_estimation", "no_trimming", "light_reweight"]
    medians = [mixed[k]["robust_bt_median"] for k in keys]
    p90s = [mixed[k]["robust_bt_p90"] for k in keys]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.plot(x, medians, marker="o", linewidth=2.2, color=PALETTE["robust"], label="Median")
    ax.plot(x, p90s, marker="s", linewidth=2.2, color=PALETTE["gnc"], label="P90")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15)
    ax.set_ylabel("Error")
    ax.set_title("Mixed-Regime Ablation")
    ax.legend(frameon=False)
    ax.grid(True, linestyle=":", alpha=0.4)
    _save(fig, "figure_ablation_mixed.png")


def plot_formation_generalization() -> None:
    payload = json.loads((EXP / "formation_result.json").read_text(encoding="utf-8"))
    formations = ["circle", "ellipse", "perturbed", "random"]
    ls = [payload[f]["summary"]["least_squares_error"]["median"] for f in formations]
    proposed = [payload[f]["summary"]["robust_bias_trimmed_error"]["median"] for f in formations]
    gnc = [payload[f]["summary"]["gnc_gm_error"]["median"] for f in formations]

    x = np.arange(len(formations))
    width = 0.24
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    ax.bar(x - width, ls, width=width, label="LS", color=PALETTE["ls"])
    ax.bar(x, gnc, width=width, label="GNC-GM", color=PALETTE["gnc"])
    ax.bar(x + width, proposed, width=width, label="Proposed", color=PALETTE["robust"])
    ax.set_xticks(x)
    ax.set_xticklabels([f.title() for f in formations])
    ax.set_ylabel("Median Error")
    ax.set_title("Formation Generalization")
    ax.legend(frameon=False)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    _save(fig, "figure_formation_generalization.png")


def plot_runtime() -> None:
    payload = json.loads((EXP / "runtime_result.json").read_text(encoding="utf-8"))
    methods = ["least_squares", "robust_huber", "gnc_gm", "ransac", "robust_bias_trimmed"]
    labels = ["LS", "Huber", "GNC-GM", "RANSAC", "Proposed"]
    method_stats = payload["methods"]
    vals = [method_stats[m]["median_ms"] for m in methods]

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.6), gridspec_kw={"width_ratios": [1.0, 1.15]})
    axes[0].bar(labels, vals, color=[PALETTE["ls"], PALETTE["huber"], PALETTE["gnc"], PALETTE["ransac"], PALETTE["robust"]])
    for idx, val in enumerate(vals):
        axes[0].text(idx, val, f"{val:.1f}", ha="center", va="bottom", fontsize=9.5, color="#0F172A")
    axes[0].set_ylabel("Median runtime (ms)")
    axes[0].set_title("Method-wise runtime")
    axes[0].grid(True, axis="y", linestyle=":", alpha=0.4)

    counts = payload["scaling"]["counts"]
    for key, label, color in [
        ("stage1_proposed", "Stage 1 robust core", PALETTE["robust"]),
        ("stage2_screening", "Stage 2 screening", PALETTE["active_spread"]),
        ("stage2_adaptive", "Adaptive gate", PALETTE["active_adaptive"]),
    ]:
        ys = [payload["scaling"][key][str(count)]["median_ms"] for count in counts if str(count) in payload["scaling"][key]]
        xs = [count for count in counts if str(count) in payload["scaling"][key]]
        axes[1].plot(xs, ys, marker="o", linewidth=2.3, color=color, label=label)
    axes[1].set_xlabel("Number of observers")
    axes[1].set_ylabel("Median runtime (ms)")
    axes[1].set_title("Runtime scaling by stage")
    axes[1].grid(True, linestyle=":", alpha=0.35)
    axes[1].legend(frameon=False, loc="upper left")
    hardware = payload["meta"]["hardware"]
    axes[1].text(
        0.98,
        0.02,
        f"{hardware['cpu']}\nPython {hardware['python']}",
        transform=axes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=8.8,
        color="#334155",
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "#F8FAFC", "edgecolor": "#CBD5E1"},
    )
    _save(fig, "figure_runtime_comparison.png")


def plot_sensitivity_sweep() -> None:
    payload = json.loads((EXP / "sensitivity_result.json").read_text(encoding="utf-8"))
    sweep_order = ["outlier_rate", "bias", "noise_std"]
    method_map = [
        ("least_squares_error", "LS", PALETTE["ls"]),
        ("gnc_gm_error", "GNC-GM", PALETTE["gnc"]),
        ("robust_bias_trimmed_error", "Proposed", PALETTE["robust"]),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
    for ax, sweep_name in zip(axes, sweep_order):
        sweep = payload[sweep_name]
        xs = [float(level) for level in sweep.keys()]
        for key, label, color in method_map:
            ys = [sweep[str(level)]["summary"][key]["median"] for level in xs]
            ax.plot(xs, ys, marker="o", linewidth=2.0, label=label, color=color)
        ax.set_title(sweep_name.replace("_", " ").title())
        ax.set_xlabel("Severity Level")
        ax.grid(True, linestyle=":", alpha=0.35)
    axes[0].set_ylabel("Median Error")
    axes[-1].legend(frameon=False, loc="upper left")
    _save(fig, "figure_sensitivity_sweep.png")


def plot_scaling() -> None:
    payload = json.loads((EXP / "scaling_result.json").read_text(encoding="utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), sharey=True)
    formations = ["circle", "random"]
    method_map = [
        ("least_squares_error", "LS", PALETTE["ls"]),
        ("gnc_gm_error", "GNC-GM", PALETTE["gnc"]),
        ("robust_bias_trimmed_error", "Proposed", PALETTE["robust"]),
    ]

    for ax, formation in zip(axes, formations):
        levels = sorted(int(level) for level in payload[formation].keys())
        for key, label, color in method_map:
            ys = [payload[formation][str(level)]["summary"][key]["median"] for level in levels]
            ax.plot(levels, ys, marker="o", linewidth=2.0, label=label, color=color)
        ax.set_title(f"{formation.title()} Formation")
        ax.set_xlabel("Number of UAVs")
        ax.grid(True, linestyle=":", alpha=0.35)
    axes[0].set_ylabel("Median Error")
    axes[-1].legend(frameon=False, loc="upper right")
    _save(fig, "figure_scaling.png")


def plot_observability() -> None:
    payload = json.loads((EXP / "observability_result.json").read_text(encoding="utf-8"))
    rows = payload["runs"]
    isotropy = np.array([row["isotropy"] for row in rows], dtype=float)
    ls_err = np.array([row["least_squares_error"] for row in rows], dtype=float)
    proposed_err = np.array([row["robust_bias_trimmed_error"] for row in rows], dtype=float)
    gnc_err = np.array([row["gnc_gm_error"] for row in rows], dtype=float)

    def _binned_curve(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        bins = np.linspace(0.0, 1.0, 7)
        centers = []
        medians = []
        for left, right in zip(bins[:-1], bins[1:]):
            if right >= 1.0:
                mask = (x >= left) & (x <= right)
            else:
                mask = (x >= left) & (x < right)
            if np.any(mask):
                centers.append((left + right) / 2.0)
                medians.append(float(np.median(y[mask])))
        return np.array(centers, dtype=float), np.array(medians, dtype=float)

    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    ax.scatter(isotropy, ls_err, s=14, alpha=0.18, color=PALETTE["ls"])
    ax.scatter(isotropy, gnc_err, s=14, alpha=0.15, color=PALETTE["gnc"])
    ax.scatter(isotropy, proposed_err, s=14, alpha=0.18, color=PALETTE["robust"])

    for y, label, color in [
        (ls_err, "LS median trend", PALETTE["ls"]),
        (gnc_err, "GNC-GM median trend", PALETTE["gnc"]),
        (proposed_err, "Proposed median trend", PALETTE["robust"]),
    ]:
        cx, cy = _binned_curve(isotropy, y)
        if cx.size:
            ax.plot(cx, cy, marker="o", linewidth=2.3, color=color, label=label)

    ax.set_xlabel("Geometry Isotropy")
    ax.set_ylabel("Localization Error")
    ax.set_title("Observability vs Error")
    ax.set_yscale("log")
    ax.grid(True, linestyle=":", alpha=0.35)
    ax.legend(frameon=False, loc="upper right")
    _save(fig, "figure_observability.png")


def plot_active_selection() -> None:
    payload = json.loads((EXP / "active_selection_result.json").read_text(encoding="utf-8"))
    summary = payload["summary"]
    policy_meta = [
        ("all_sensors", "All", PALETTE["active_all"]),
        ("random", "Random", PALETTE["active_random"]),
        ("spread", "Spread", PALETTE["active_spread"]),
        ("crlb", "FIM", PALETTE["active_crlb"]),
        ("residual", "Residual", PALETTE["active_residual"]),
        ("reliability", "Reliability", PALETTE["active_reliability"]),
        ("observability_robust", "Proposed", PALETTE["active_proposed"]),
        ("adaptive", "Adaptive", PALETTE["active_adaptive"]),
    ]
    policy_meta = [item for item in policy_meta if item[0] in summary["overall"]]
    policy_keys = [item[0] for item in policy_meta]
    labels = [item[1] for item in policy_meta]
    colors = [item[2] for item in policy_meta]

    overall_medians = [summary["overall"][key]["median"] for key in policy_keys]
    catastrophic = [summary["overall"][key]["catastrophic_at_5_0"] for key in policy_keys]
    counts = sorted(int(key) for key in summary["by_num_uavs"].keys())

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.6))
    axes[0].bar(labels, overall_medians, color=colors)
    axes[0].set_ylabel("Median Error")
    axes[0].set_title("Measurement Screening Overall")
    axes[0].grid(True, axis="y", linestyle=":", alpha=0.35)
    axes[0].tick_params(axis="x", rotation=12)

    for key, label, color in zip(policy_keys, labels, colors):
        ys = [summary["by_num_uavs"][str(count)][key]["median"] for count in counts]
        axes[1].plot(counts, ys, marker="o", linewidth=2.0, label=label, color=color)
    axes[1].set_xlabel("Number of UAVs")
    axes[1].set_ylabel("Median Error")
    axes[1].set_title("Scaling Under Measurement Screening")
    axes[1].grid(True, linestyle=":", alpha=0.35)
    axes[1].legend(frameon=False, loc="upper right")

    # Add catastrophic-rate annotations to the first panel for quick paper reuse.
    for idx, rate in enumerate(catastrophic):
        axes[0].text(idx, overall_medians[idx], f"{rate:.2f}", ha="center", va="bottom", fontsize=9, color="#111827")

    _save(fig, "figure_active_selection.png")


def plot_story_benchmark() -> None:
    payload = json.loads((EXP / "story_benchmark_result.json").read_text(encoding="utf-8"))
    regimes = ["clean", "outlier", "mixed", "pose_uncertainty", "heterogeneous_bias"]
    regime_labels = ["Clean", "Outlier", "Mixed", "Pose Noise", "Het. Bias"]
    methods = [
        ("least_squares_error", "LS", PALETTE["ls"]),
        ("robust_error", "Huber", PALETTE["huber"]),
        ("tukey_error", "Tukey", PALETTE["tukey"]),
        ("ransac_error", "RANSAC", PALETTE["ransac"]),
        ("gnc_gm_error", "GNC-GM", PALETTE["gnc"]),
        ("robust_bias_trimmed_error", "Proposed", PALETTE["robust"]),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14.0, 4.8))
    x = np.arange(len(regimes))
    width = 0.13
    for idx, (key, label, color) in enumerate(methods):
        medians = [payload["summary"]["by_regime"][regime][key]["median"] for regime in regimes]
        axes[0].bar(x + (idx - 2.5) * width, medians, width=width, color=color, label=label)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(regime_labels, rotation=10)
    axes[0].set_ylabel("Median Localization Error")
    axes[0].set_title("Robust Localization Across Corruption Regimes")
    axes[0].grid(True, axis="y", linestyle=":", alpha=0.35)

    for idx, (key, label, color) in enumerate(methods):
        cat = [payload["summary"]["by_regime"][regime][key]["catastrophic_at_0_5R"] for regime in regimes]
        axes[1].plot(x, cat, marker="o", linewidth=2.0, color=color, label=label)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(regime_labels, rotation=10)
    axes[1].set_ylim(-0.01, 1.0)
    axes[1].set_ylabel("Catastrophic Failure Rate")
    axes[1].set_title("Failure-Risk Envelope")
    axes[1].grid(True, linestyle=":", alpha=0.35)
    axes[1].legend(frameon=False, ncol=2, loc="upper left")
    _save(fig, "figure_story_regimes.png")


def plot_story_cdf() -> None:
    payload = json.loads((EXP / "story_benchmark_result.json").read_text(encoding="utf-8"))
    regimes = [("outlier", "Outlier-Rich Regime"), ("mixed", "Mixed-Corruption Regime")]
    methods = [
        ("least_squares_error", "LS", PALETTE["ls"]),
        ("gnc_gm_error", "GNC-GM", PALETTE["gnc"]),
        ("ransac_error", "RANSAC", PALETTE["ransac"]),
        ("robust_bias_trimmed_error", "Proposed", PALETTE["robust"]),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.5), sharey=True)
    for ax, (regime_key, title) in zip(axes, regimes):
        regime_rows = [row for row in payload["runs"] if row["regime"] == regime_key]
        for key, label, color in methods:
            xs, ys = _empirical_cdf([row[key] for row in regime_rows])
            if xs.size == 0:
                continue
            ax.step(np.maximum(xs, 1e-4), ys, where="post", linewidth=2.1, color=color, label=label)
        ax.set_xscale("log")
        ax.set_xlabel("Localization Error")
        ax.set_title(title)
        ax.grid(True, linestyle=":", alpha=0.35)
    axes[0].set_ylabel("Empirical CDF")
    axes[0].legend(frameon=False, loc="lower right")
    _save(fig, "figure_story_cdf.png")


def plot_selection_benefit_map() -> None:
    payload = json.loads((EXP / "selection_benefit_map.json").read_text(encoding="utf-8"))
    outlier_rates = payload["meta"]["outlier_rates"]
    budget_fracs = payload["meta"]["budget_fracs"]
    policies = ["observability_robust", "adaptive"]
    titles = ["Proposed Screening vs All-Sensor", "Adaptive Screening vs All-Sensor"]

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.6), sharey=True)
    for ax, policy, title in zip(axes, policies, titles):
        grid = np.zeros((len(outlier_rates), len(budget_fracs)), dtype=float)
        for i, outlier_rate in enumerate(outlier_rates):
            for j, budget_frac in enumerate(budget_fracs):
                key = f"outlier_{outlier_rate:.2f}__budget_{budget_frac:.2f}"
                grid[i, j] = payload["summary"][key]["delta_vs_all"][policy]
        im = ax.imshow(grid, cmap="RdYlGn", aspect="auto", origin="lower")
        ax.set_xticks(np.arange(len(budget_fracs)))
        ax.set_xticklabels([f"{v:.2f}" for v in budget_fracs])
        ax.set_yticks(np.arange(len(outlier_rates)))
        ax.set_yticklabels([f"{v:.2f}" for v in outlier_rates])
        ax.set_xlabel("Budget Fraction")
        ax.set_title(title)
        for i in range(len(outlier_rates)):
            for j in range(len(budget_fracs)):
                ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center", fontsize=8, color="#111827")
    axes[0].set_ylabel("Outlier Rate")
    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.86)
    cbar.set_label("Median Error Gain Over All-Sensor")
    _save(fig, "figure_selection_benefit_map.png")


def plot_screening_weight_sensitivity() -> None:
    if not (EXP / "screening_weight_sensitivity.json").exists() and (EXP / "screening_weight_grid_result.json").exists():
        payload = json.loads((EXP / "screening_weight_grid_result.json").read_text(encoding="utf-8"))
        combos = payload["combinations"]
        baseline = payload["baseline"]["default_median_error"]
        medians = np.array([item["median_error"] for item in combos], dtype=float)
        overlaps = np.array([item["mean_jaccard"] for item in combos], dtype=float)
        stress = np.array([max(abs(mult - 1.0) for mult in item["multipliers"]) for item in combos], dtype=float)

        fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8))
        axes[0].scatter(stress * 100.0, medians, s=42, alpha=0.75, color=PALETTE["active_proposed"], edgecolor="white", linewidth=0.5)
        axes[0].axhline(baseline, color=PALETTE["active_all"], linestyle="--", linewidth=1.8, label="Default weights")
        axes[0].fill_between(
            [18, 22],
            np.percentile(medians, 5),
            np.percentile(medians, 95),
            color="#D1FAE5",
            alpha=0.8,
            label="5--95% across exact +/-20% grid",
        )
        axes[0].set_xlabel("Largest coefficient perturbation (%)")
        axes[0].set_ylabel("Median Error Across Budgeted Windows")
        axes[0].set_title("Exact +/-20% Weight Grid")
        axes[0].grid(True, axis="y", linestyle=":", alpha=0.35)
        axes[0].legend(frameon=False, loc="upper left")

        axes[1].scatter(medians, overlaps, s=48, alpha=0.78, color=PALETTE["active_spread"], edgecolor="white", linewidth=0.5)
        axes[1].axvline(baseline, color=PALETTE["active_all"], linestyle="--", linewidth=1.6)
        axes[1].set_xlabel("Median Error Across Budgeted Windows")
        axes[1].set_ylabel("Mean Jaccard Overlap vs Default Subset")
        axes[1].set_ylim(0.75, 1.01)
        axes[1].set_title("Subset Choices Stay Stable")
        axes[1].grid(True, linestyle=":", alpha=0.35)
        axes[1].text(
            0.02,
            0.05,
            f"Median overlap = {np.median(overlaps):.3f}\nMedian error inflation = {100.0 * (np.median(medians) - baseline) / baseline:.1f}%",
            transform=axes[1].transAxes,
            ha="left",
            va="bottom",
            fontsize=9,
            color="#0F172A",
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "#F8FAFC", "edgecolor": "#CBD5E1"},
        )
        _save(fig, "figure_screening_weight_sensitivity.png")
        return

    payload = json.loads((EXP / "screening_weight_sensitivity.json").read_text(encoding="utf-8"))
    levels = ["mild", "moderate", "strong"]
    labels = ["Mild", "Moderate", "Strong"]
    baseline = payload["baseline"]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.8))
    median_error_samples = [np.array([item["median_error"] for item in payload["levels"][level]["perturbations"]], dtype=float) for level in levels]
    overlap_samples = [np.array([item["mean_jaccard"] for item in payload["levels"][level]["perturbations"]], dtype=float) for level in levels]
    for ax, samples, ylabel, title in [
        (axes[0], median_error_samples, "Median Error Across Budgeted Windows", "Randomized Weight Perturbations"),
        (axes[1], overlap_samples, "Jaccard Overlap vs Default Subset", "Subset Stability Under Perturbation"),
    ]:
        box = ax.boxplot(
            samples,
            tick_labels=labels,
            patch_artist=True,
            widths=0.55,
            medianprops={"color": "#0F172A", "linewidth": 1.4},
            boxprops={"linewidth": 1.2},
            whiskerprops={"linewidth": 1.0},
            capprops={"linewidth": 1.0},
        )
        for patch, color in zip(box["boxes"], [PALETTE["active_reliability"], PALETTE["active_spread"], PALETTE["active_proposed"]]):
            patch.set_facecolor(color)
            patch.set_alpha(0.28)
            patch.set_edgecolor(color)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, axis="y", linestyle=":", alpha=0.35)
    axes[0].axhline(baseline["default_median"], color=PALETTE["active_proposed"], linestyle="-", linewidth=2.0)
    axes[0].axhline(baseline["all_sensors_median"], color=PALETTE["active_all"], linestyle="-.", linewidth=1.6)
    axes[1].set_ylim(0.75, 1.01)
    _save(fig, "figure_screening_weight_sensitivity.png")


def plot_screening_score_ablation() -> None:
    payload = json.loads((EXP / "screening_score_ablation.json").read_text(encoding="utf-8"))
    order = ["all_sensors", "geometry_only", "geometry_plus_residual", "geometry_plus_reliability", "full_score"]
    labels = ["All sensors", "Geometry", "Geom.+Residual", "Geom.+Reliability", "Full score"]
    overall = payload["summary"]["overall"]
    severe = payload["summary"]["by_regime"]["severe"]
    colors = [
        PALETTE["active_all"],
        PALETTE["active_spread"],
        PALETTE["active_residual"],
        PALETTE["active_reliability"],
        PALETTE["active_proposed"],
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.6))
    median_vals = [overall[key]["median"] for key in order]
    severe_p90 = [severe[key]["p90"] for key in order]

    axes[0].bar(labels, median_vals, color=colors)
    for idx, val in enumerate(median_vals):
        axes[0].text(idx, val, f"{val:.2f}", ha="center", va="bottom", fontsize=9)
    axes[0].set_ylabel("Overall median error")
    axes[0].set_title("Score-term ablation")
    axes[0].grid(True, axis="y", linestyle=":", alpha=0.35)
    axes[0].tick_params(axis="x", rotation=14)

    axes[1].bar(labels, severe_p90, color=colors)
    for idx, val in enumerate(severe_p90):
        axes[1].text(idx, val, f"{val:.2f}", ha="center", va="bottom", fontsize=9)
    axes[1].set_ylabel("Severe-regime P90 error")
    axes[1].set_title("Tail risk under severe corruption")
    axes[1].grid(True, axis="y", linestyle=":", alpha=0.35)
    axes[1].tick_params(axis="x", rotation=14)
    _save(fig, "figure_screening_score_ablation.png")


def plot_threshold_sweep() -> None:
    payload = json.loads((EXP / "story_revision_analysis.json").read_text(encoding="utf-8"))
    regimes = [("outlier", "Outlier-rich regime"), ("mixed", "Mixed-corruption regime")]
    methods = [
        ("LS", PALETTE["ls"]),
        ("GNC-GM", PALETTE["gnc"]),
        ("RANSAC", PALETTE["ransac"]),
        ("Proposed", PALETTE["robust"]),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6), sharey=True)
    for ax, (regime, title) in zip(axes, regimes):
        for label, color in methods:
            entries = payload["threshold_sweep"][regime][label]
            xs = [entry["threshold_r"] for entry in entries]
            ys = [entry["success_rate"] for entry in entries]
            ax.plot(xs, ys, marker="o", linewidth=2.1, color=color, label=label)
        ax.axvline(0.2, color="#CBD5E1", linestyle="--", linewidth=1.1)
        ax.axvline(0.3, color="#94A3B8", linestyle="--", linewidth=1.1)
        ax.set_title(title)
        ax.set_xlabel("Threshold (R)")
        ax.set_xlim(0.1, 0.5)
        ax.set_ylim(0.45, 1.01)
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.grid(True, linestyle=":", alpha=0.35)
    axes[0].set_ylabel("Success rate below threshold")
    axes[0].legend(frameon=False, loc="lower right")
    _save(fig, "figure_threshold_sweep.png")


def plot_ransac_failure_case() -> None:
    analysis_payload = json.loads((EXP / "story_revision_analysis.json").read_text(encoding="utf-8"))
    cases = analysis_payload.get("ransac_failure_cases") or []
    if not cases and analysis_payload.get("ransac_failure_case") is not None:
        cases = [analysis_payload["ransac_failure_case"]]

    nrows = max(1, len(cases))
    fig, axes = plt.subplots(
        nrows,
        2,
        figsize=(12.8, 4.0 * nrows),
        gridspec_kw={"width_ratios": [1.35, 0.95]},
    )
    if nrows == 1:
        axes = np.asarray([axes], dtype=object)

    for row_idx, payload in enumerate(cases):
        sensors = payload["valid_sensors"]
        target = payload["target"]
        estimates = payload["estimates"]
        geo_ax = axes[row_idx, 0]
        bar_ax = axes[row_idx, 1]

        for sensor in sensors:
            start = np.array([sensor["x"], sensor["y"]], dtype=float)
            ray = np.array([np.cos(sensor["bearing"]), np.sin(sensor["bearing"])], dtype=float)
            end = start + 16.0 * ray
            geo_ax.plot([start[0], end[0]], [start[1], end[1]], linestyle="--", linewidth=1.0, color="#CBD5E1", alpha=0.85)
            pose_error = float(sensor.get("pose_error", 0.0))
            sensor_bias = float(sensor.get("sensor_bias", 0.0))
            highlight = pose_error > 0.30 or abs(sensor_bias) > 0.05
            face = "#FDE68A" if highlight else "#E5E7EB"
            edge = "#B45309" if highlight else "#6B7280"
            geo_ax.scatter(sensor["x"], sensor["y"], s=74, color=face, edgecolor=edge, linewidth=0.95, zorder=3)

        geo_ax.scatter(target["x"], target["y"], marker="*", s=240, color="#B91C1C", edgecolor="white", linewidth=0.9, zorder=5, label="True target")
        markers = {
            "least_squares": ("o", PALETTE["ls"], "LS"),
            "ransac": ("X", PALETTE["ransac"], "RANSAC"),
            "proposed": ("s", PALETTE["robust"], "Proposed"),
        }
        for key, (marker, color, label) in markers.items():
            geo_ax.scatter(
                estimates[key]["x"],
                estimates[key]["y"],
                marker=marker,
                s=98,
                color=color,
                edgecolor="white",
                linewidth=0.95,
                zorder=6,
                label=label,
            )
        role = payload.get("case_role") or payload["regime"].replace("_", " ").title()
        geo_ax.set_title(f"{role}\n{payload['formation'].title()} formation | seed {payload['seed']}")
        geo_ax.set_xlabel("X")
        geo_ax.set_ylabel("Y")
        geo_ax.set_aspect("equal", adjustable="box")
        geo_ax.grid(True, linestyle=":", alpha=0.35)
        if row_idx == 0:
            geo_ax.legend(frameon=False, loc="upper right")

        labels = ["LS", "RANSAC", "GNC-GM", "Proposed"]
        vals = [
            estimates["least_squares"]["error"],
            estimates["ransac"]["error"],
            estimates["gnc_gm"]["error"],
            estimates["proposed"]["error"],
        ]
        colors = [PALETTE["ls"], PALETTE["ransac"], PALETTE["gnc"], PALETTE["robust"]]
        bar_ax.bar(labels, vals, color=colors)
        best_idx = int(np.argmin(vals))
        for idx, val in enumerate(vals):
            txt_color = "#065F46" if idx == best_idx else "#0F172A"
            bar_ax.text(idx, val, f"{val:.2f}", ha="center", va="bottom", fontsize=9.2, color=txt_color)
        bar_ax.set_ylabel("Localization error")
        bar_ax.set_title("Method error on this window")
        bar_ax.grid(True, axis="y", linestyle=":", alpha=0.35)
        bar_ax.tick_params(axis="x", rotation=10)
    _save(fig, "figure_ransac_failure_case.png")


def plot_tracking_proxy() -> None:
    payload = json.loads((EXP / "tracking_proxy_result.json").read_text(encoding="utf-8"))
    methods = ["LS", "RANSAC", "Proposed"]
    overall = payload["summary"]["overall"]
    disturbed = payload["summary"]["by_regime"]["disturbed_pybullet"]
    metrics = [
        ("overall_break", "Overall sequence break rate", [overall[m]["sequence_break_rate"] for m in methods], True),
        ("disturbed_break", "Disturbed sequence break rate", [disturbed[m]["sequence_break_rate"] for m in methods], True),
        ("rapid_reacq", "Rapid reacquisition rate", [disturbed[m]["mean_rapid_reacquisition_rate"] for m in methods], True),
        ("disturbed_roi", "Disturbed ROI radius P90", [disturbed[m]["median_roi_radius_p90"] for m in methods], False),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16.4, 4.6))
    for ax, (_metric_key, title, vals, as_percent) in zip(axes, metrics):
        colors = [PALETTE["ls"], PALETTE["ransac"], PALETTE["robust"]]
        ax.bar(methods, vals, color=colors)
        for idx, val in enumerate(vals):
            ax.text(idx, val, f"{val:.2f}", ha="center", va="bottom", fontsize=9, color="#0F172A")
        ax.set_title(title)
        ax.grid(True, axis="y", linestyle=":", alpha=0.35)
        if as_percent:
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))

    axes[0].set_ylabel("Proxy metric value")
    axes[-1].text(
        0.04,
        0.95,
        "Disturbed replay:\n"
        f"LS ROI$_{{P90}}$ = {disturbed['LS']['median_roi_radius_p90']:.2f}\n"
        f"RANSAC ROI$_{{P90}}$ = {disturbed['RANSAC']['median_roi_radius_p90']:.2f}\n"
        f"Proposed ROI$_{{P90}}$ = {disturbed['Proposed']['median_roi_radius_p90']:.2f}",
        transform=axes[-1].transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color="#0F172A",
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "#F8FAFC", "edgecolor": "#CBD5E1"},
    )
    _save(fig, "figure_tracking_proxy.png")


def plot_screening_case_studies() -> None:
    payload = json.loads((EXP / "active_selection_result.json").read_text(encoding="utf-8"))

    def _match(row: dict, **conds) -> bool:
        return all(row.get(key) == value for key, value in conds.items())

    best_row = next(
        (
            row
            for row in payload["runs"]
            if _match(
                row,
                regime="severe",
                formation="perturbed",
                num_uavs=10,
                budget=4,
                seed=1,
            )
        ),
        None,
    )
    if best_row is None:
        def _proposed_case_score(row: dict) -> tuple[float, float]:
            simple_best = min(
                row["spread_error"],
                row["crlb_error"],
                row["residual_error"],
                row["reliability_error"],
            )
            return (
                simple_best - row["observability_robust_error"],
                row["all_sensors_error"] - row["observability_robust_error"],
            )

        best_row = max(payload["runs"], key=_proposed_case_score)

    worst_row = next(
        (
            row
            for row in payload["runs"]
            if _match(
                row,
                regime="severe",
                formation="perturbed",
                num_uavs=12,
                budget=6,
                seed=43,
                adaptive_triggered=False,
            )
        ),
        None,
    )
    if worst_row is None:
        adaptive_safe_rows = [row for row in payload["runs"] if not row["adaptive_triggered"]]
        worst_row = max(
            adaptive_safe_rows,
            key=lambda row: row["observability_robust_error"] - row["all_sensors_error"],
        )

    cases = [
        ("Proposed screening beats simpler subset rules", _replay_selection_case(best_row)),
        ("All-sensor fusion should be kept", _replay_selection_case(worst_row)),
    ]

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(13.0, 9.0),
        gridspec_kw={"width_ratios": [1.35, 1.0]},
    )
    policy_labels = [
        ("all_sensors", "All", PALETTE["active_all"]),
        ("spread", "Spread", PALETTE["active_spread"]),
        ("crlb", "FIM", PALETTE["active_crlb"]),
        ("residual", "Residual", PALETTE["active_residual"]),
        ("reliability", "Reliability", PALETTE["active_reliability"]),
        ("observability_robust", "Proposed", PALETTE["active_proposed"]),
        ("adaptive", "Adaptive", PALETTE["active_adaptive"]),
    ]

    for row_idx, (title, case) in enumerate(cases):
        geo_ax = axes[row_idx, 0]
        bar_ax = axes[row_idx, 1]
        scenario = case["scenario"]
        target = case["target"]
        valid_sensors = case["valid_sensors"]
        valid_bearings = case["valid_bearings"]
        estimates = case["estimates"]
        row = case["row"]

        for sensor, bearing in zip(valid_sensors, valid_bearings):
            ray = np.array([np.cos(bearing), np.sin(bearing)], dtype=float)
            start = np.array([sensor.x, sensor.y], dtype=float)
            end = start + 16.0 * ray
            geo_ax.plot([start[0], end[0]], [start[1], end[1]], linestyle="--", linewidth=0.9, color="#CBD5E1", alpha=0.7, zorder=1)

        geo_ax.scatter(
            [sensor.x for sensor in valid_sensors],
            [sensor.y for sensor in valid_sensors],
            s=50,
            color="#E5E7EB",
            edgecolor="#6B7280",
            linewidth=0.8,
            label="Valid sensors",
            zorder=2,
        )

        proposed_sel = estimates["observability_robust"]["selected_indices"]
        geo_ax.scatter(
            [valid_sensors[idx].x for idx in proposed_sel],
            [valid_sensors[idx].y for idx in proposed_sel],
            s=82,
            color=PALETTE["active_proposed"],
            edgecolor="white",
            linewidth=1.1,
            label="Proposed subset",
            zorder=3,
        )

        if estimates["adaptive"]["triggered"]:
            adaptive_sel = estimates["adaptive"]["selected_indices"]
            geo_ax.scatter(
                [valid_sensors[idx].x for idx in adaptive_sel],
                [valid_sensors[idx].y for idx in adaptive_sel],
                s=96,
                facecolor="none",
                edgecolor=PALETTE["active_adaptive"],
                linewidth=1.5,
                label="Adaptive subset",
                zorder=3,
            )

        geo_ax.scatter(target[0], target[1], marker="*", s=220, color="#B91C1C", edgecolor="white", linewidth=0.8, zorder=5, label="True target")
        geo_ax.scatter(*estimates["all_sensors"]["point"], marker="X", s=90, color=PALETTE["active_all"], zorder=5, label="All-sensor estimate")
        geo_ax.scatter(*estimates["observability_robust"]["point"], marker="s", s=76, color=PALETTE["active_proposed"], zorder=5, label="Proposed estimate")
        geo_ax.scatter(*estimates["adaptive"]["point"], marker="D", s=60, color=PALETTE["active_adaptive"], zorder=5, label="Adaptive estimate")

        geo_ax.set_aspect("equal", adjustable="box")
        geo_ax.grid(True, linestyle=":", alpha=0.35)
        geo_ax.set_xlabel("X")
        geo_ax.set_ylabel("Y")
        geo_ax.set_title(
            f"{title}\n{row['regime'].title()}, {row['formation'].title()}, {row['num_uavs']} observers, budget={row['budget']}"
        )
        geo_ax.legend(frameon=False, fontsize=8, loc="upper right")

        labels = [label for _, label, _ in policy_labels]
        colors = [color for _, _, color in policy_labels]
        vals = [estimates[key]["error"] for key, _, _ in policy_labels]
        bar_ax.bar(labels, vals, color=colors)
        best_idx = int(np.argmin(vals))
        for idx, val in enumerate(vals):
            color = "#111827" if idx != best_idx else "#065F46"
            bar_ax.text(idx, val, f"{val:.2f}", ha="center", va="bottom", fontsize=8, color=color)
        bar_ax.set_ylabel("Localization Error")
        bar_ax.set_title("Policy outcome on this case")
        bar_ax.grid(True, axis="y", linestyle=":", alpha=0.35)
        bar_ax.tick_params(axis="x", rotation=12)

        if not estimates["adaptive"]["triggered"]:
            bar_ax.text(
                0.03,
                0.95,
                "Adaptive gate kept full-set fusion",
                transform=bar_ax.transAxes,
                ha="left",
                va="top",
                fontsize=9,
                color=PALETTE["active_adaptive"],
            )

    _save(fig, "figure_screening_cases.png")


def plot_pybullet_validation() -> None:
    result_payload = json.loads((EXP / "pybullet_replay_result.json").read_text(encoding="utf-8"))
    trace_payload = json.loads((EXP / "pybullet_replay_traces.json").read_text(encoding="utf-8"))
    regime_keys = ["nominal_pybullet", "disturbed_pybullet"]
    regime_labels = ["Nominal", "Disturbed"]
    trace_key = "nominal_pybullet_8"
    if trace_key not in trace_payload["examples"]:
        trace_key = next(iter(trace_payload["examples"]))
    trace = trace_payload["examples"][trace_key]

    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.6), gridspec_kw={"width_ratios": [1.35, 1.0, 1.0]})

    trajectory_colors = plt.cm.cividis(np.linspace(0.18, 0.92, len(trace["drones"])))
    for color, drone in zip(trajectory_colors, trace["drones"]):
        axes[0].plot(drone["x"], drone["y"], linewidth=1.4, alpha=0.86, color=color)
    axes[0].scatter(
        [trace["meta"]["target"]["x"]],
        [trace["meta"]["target"]["y"]],
        marker="*",
        s=180,
        color="#B91C1C",
        edgecolor="white",
        linewidth=0.8,
        zorder=5,
    )
    axes[0].set_title("PyBullet Multi-UAV Trajectories")
    axes[0].set_xlabel("X")
    axes[0].set_ylabel("Y")
    margin = 16.0
    axes[0].set_xlim(trace["meta"]["target"]["x"] - margin, trace["meta"]["target"]["x"] + margin)
    axes[0].set_ylim(trace["meta"]["target"]["y"] - margin, trace["meta"]["target"]["y"] + margin)
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].grid(True, linestyle=":", alpha=0.35)

    width = 0.34
    x = np.arange(len(regime_keys))
    ls_medians = [result_payload["summary"]["by_regime"][key]["least_squares"]["median"] for key in regime_keys]
    rb_medians = [result_payload["summary"]["by_regime"][key]["robust_bias_trimmed"]["median"] for key in regime_keys]
    ls_p90 = [result_payload["summary"]["by_regime"][key]["least_squares"]["p90"] for key in regime_keys]
    rb_p90 = [result_payload["summary"]["by_regime"][key]["robust_bias_trimmed"]["p90"] for key in regime_keys]

    axes[1].bar(x - width / 2, ls_medians, width=width, color=PALETTE["ls"], label="LS")
    axes[1].bar(x + width / 2, rb_medians, width=width, color=PALETTE["robust"], label="Proposed")
    for idx, value in enumerate(ls_p90):
        axes[1].text(x[idx] - width / 2, ls_medians[idx], f"P90={value:.2f}", ha="center", va="bottom", fontsize=8, color="#374151")
    for idx, value in enumerate(rb_p90):
        axes[1].text(x[idx] + width / 2, rb_medians[idx], f"P90={value:.2f}", ha="center", va="bottom", fontsize=8, color="#065F46")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(regime_labels)
    axes[1].set_ylabel("Median Error")
    axes[1].set_title("Replay Error Under Dynamic Flight")
    axes[1].grid(True, axis="y", linestyle=":", alpha=0.35)
    axes[1].legend(frameon=False, loc="upper left")

    ls_success = [result_payload["summary"]["by_regime"][key]["least_squares"]["success_at_1_0"] for key in regime_keys]
    rb_success = [result_payload["summary"]["by_regime"][key]["robust_bias_trimmed"]["success_at_1_0"] for key in regime_keys]
    ls_fail = [result_payload["summary"]["by_regime"][key]["least_squares"]["catastrophic_at_5_0"] for key in regime_keys]
    rb_fail = [result_payload["summary"]["by_regime"][key]["robust_bias_trimmed"]["catastrophic_at_5_0"] for key in regime_keys]

    axes[2].bar(x - width / 2, ls_success, width=width, color=PALETTE["ls"], label="LS")
    axes[2].bar(x + width / 2, rb_success, width=width, color=PALETTE["robust"], label="Proposed")
    for idx, value in enumerate(ls_fail):
        axes[2].text(x[idx] - width / 2, ls_success[idx], f"fail={value:.2f}", ha="center", va="bottom", fontsize=8, color="#374151")
    for idx, value in enumerate(rb_fail):
        axes[2].text(x[idx] + width / 2, rb_success[idx], f"fail={value:.2f}", ha="center", va="bottom", fontsize=8, color="#065F46")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(regime_labels)
    axes[2].set_ylim(0.0, 1.05)
    axes[2].set_ylabel("Success Rate @ 1.0")
    axes[2].set_title("Reliability Under Replay Stress")
    axes[2].grid(True, axis="y", linestyle=":", alpha=0.35)

    _save(fig, "figure_pybullet_replay.png")


def plot_public_real_replay() -> None:
    result_payload = json.loads((EXP / "public_dataset3_replay_result.json").read_text(encoding="utf-8"))
    trajectory = np.loadtxt(PUBLIC_DATASET_ROOT / "rtk.txt", dtype=float)
    camera_positions = np.loadtxt(PUBLIC_DATASET_ROOT / "campos.txt", dtype=float)
    camera_names = result_payload["meta"]["camera_names"]
    thresholds = result_payload["meta"]["thresholds_m"]
    regime_keys = ["real_nominal", "real_disturbed"]
    regime_labels = ["Nominal", "Disturbed"]
    methods = [
        ("least_squares", "LS", PALETTE["ls"]),
        ("gnc_gm", "GNC-GM", PALETTE["gnc"]),
        ("ransac", "RANSAC", PALETTE["ransac"]),
        ("robust_bias_trimmed", "Proposed", PALETTE["robust"]),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.9), gridspec_kw={"width_ratios": [1.15, 1.0, 1.0]})

    ax = axes[0]
    ax.plot(trajectory[:, 0], trajectory[:, 1], color="#94A3B8", linewidth=1.8, alpha=0.95, label="RTK trajectory")
    ax.scatter(
        trajectory[0, 0],
        trajectory[0, 1],
        marker="o",
        s=52,
        color="#0F766E",
        edgecolor="white",
        linewidth=0.6,
        zorder=5,
        label="Start",
    )
    ax.scatter(
        trajectory[-1, 0],
        trajectory[-1, 1],
        marker="X",
        s=70,
        color="#B91C1C",
        edgecolor="white",
        linewidth=0.6,
        zorder=5,
        label="End",
    )
    cam_colors = plt.cm.viridis(np.linspace(0.16, 0.86, len(camera_names)))
    for idx, (name, color) in enumerate(zip(camera_names, cam_colors)):
        ax.scatter(
            camera_positions[idx, 0],
            camera_positions[idx, 1],
            s=82,
            color=color,
            edgecolor="white",
            linewidth=0.8,
            zorder=6,
        )
        ax.text(
            camera_positions[idx, 0] + 1.6,
            camera_positions[idx, 1] + 1.2,
            f"C{idx}",
            fontsize=8.5,
            color="#0F172A",
        )
    ax.set_title("Public Flight Trajectory Replay")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle=":", alpha=0.35)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)

    positions: list[float] = []
    xticklabels: list[str] = []
    p95_values: list[float] = []
    median_values: list[float] = []
    bar_colors: list[str] = []
    for regime_idx, regime_key in enumerate(regime_keys):
        base = regime_idx * (len(methods) + 1)
        panel = result_payload["summary"]["by_regime"][regime_key]
        for method_idx, (method_key, label, color) in enumerate(methods):
            positions.append(base + method_idx)
            xticklabels.append(label)
            p95_values.append(panel[method_key]["p95"])
            median_values.append(panel[method_key]["median"])
            bar_colors.append(color)

    ax = axes[1]
    ax.bar(positions, p95_values, color=bar_colors, alpha=0.88)
    ax.scatter(
        positions,
        median_values,
        s=48,
        facecolor="white",
        edgecolor="#0F172A",
        linewidth=1.0,
        zorder=5,
        label="Median",
    )
    y_top = max(p95_values) * 1.15
    for regime_idx, regime_label in enumerate(regime_labels):
        base = regime_idx * (len(methods) + 1)
        ax.text(base + 1.5, y_top * 0.98, regime_label, ha="center", va="top", fontsize=10.5, color="#334155")
    ax.axvline(len(methods) - 0.4, color="#CBD5E1", linestyle="--", linewidth=1.0)
    ax.set_xticks(positions)
    ax.set_xticklabels(xticklabels, rotation=0)
    ax.set_ylabel("Error (m)")
    ax.set_title("Replay Tail Error (bars = P95, dots = median)")
    ax.set_ylim(0.0, y_top)
    ax.grid(True, axis="y", linestyle=":", alpha=0.35)
    ax.legend(frameon=False, loc="upper right")

    cue_colors = {
        "ready": "#047857",
        "degraded": "#D97706",
        "extreme": "#B91C1C",
    }
    ready_values: list[float] = []
    degraded_values: list[float] = []
    extreme_values: list[float] = []
    for regime_key in regime_keys:
        panel = result_payload["summary"]["by_regime"][regime_key]
        for method_key, _label, _color in methods:
            ready_values.append(panel[method_key]["ready_rate"])
            degraded_values.append(panel[method_key]["degraded_rate"])
            extreme_values.append(panel[method_key]["extreme_rate"])

    ax = axes[2]
    ax.bar(positions, ready_values, color=cue_colors["ready"])
    ax.bar(positions, degraded_values, bottom=ready_values, color=cue_colors["degraded"])
    ax.bar(
        positions,
        extreme_values,
        bottom=np.asarray(ready_values, dtype=float) + np.asarray(degraded_values, dtype=float),
        color=cue_colors["extreme"],
    )
    for regime_idx, regime_label in enumerate(regime_labels):
        base = regime_idx * (len(methods) + 1)
        ax.text(base + 1.5, 1.03, regime_label, ha="center", va="bottom", fontsize=10.5, color="#334155")
    ax.axvline(len(methods) - 0.4, color="#CBD5E1", linestyle="--", linewidth=1.0)
    ax.set_xticks(positions)
    ax.set_xticklabels(xticklabels, rotation=0)
    ax.set_ylim(0.0, 1.08)
    ax.set_ylabel("Fraction of windows")
    ax.set_title(f"Cue Partition ({thresholds['ready']:.0f} m / {thresholds['extreme']:.0f} m)")
    ax.grid(True, axis="y", linestyle=":", alpha=0.35)
    handles = [plt.Rectangle((0, 0), 1, 1, color=cue_colors[key]) for key in ["ready", "degraded", "extreme"]]
    ax.legend(handles, ["Ready", "Degraded", "Extreme"], frameon=False, loc="upper right")

    _save(fig, "figure_public_real_replay.png")


def plot_operational_utility() -> None:
    result_payload = json.loads((EXP / "pybullet_replay_result.json").read_text(encoding="utf-8"))
    panels = [
        ("Overall replay", result_payload["summary"]["overall"]),
        ("Disturbed replay", result_payload["summary"]["by_regime"]["disturbed_pybullet"]),
    ]
    methods = [
        ("least_squares", "LS"),
        ("gnc_gm", "GNC-GM"),
        ("robust_huber", "Huber"),
        ("robust_bias_trimmed", "Proposed"),
    ]
    colors = {
        "ready": "#047857",
        "degraded": "#D97706",
        "failed": "#B91C1C",
    }

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.6), sharey=True)
    for ax, (title, panel) in zip(axes, panels):
        labels = [label for _, label in methods]
        ready = np.array([panel[key]["success_at_1_0"] for key, _ in methods], dtype=float)
        failed = np.array([panel[key]["catastrophic_at_5_0"] for key, _ in methods], dtype=float)
        degraded = np.clip(1.0 - ready - failed, 0.0, 1.0)
        x = np.arange(len(labels))

        ax.bar(x, ready, color=colors["ready"])
        ax.bar(x, degraded, bottom=ready, color=colors["degraded"])
        ax.bar(x, failed, bottom=ready + degraded, color=colors["failed"])
        for idx, value in enumerate(ready):
            ax.text(idx, value / 2.0, f"{value:.2f}", ha="center", va="center", fontsize=8, color="white")

        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0.0, 1.05)
        ax.set_title(title)
        ax.grid(True, axis="y", linestyle=":", alpha=0.35)

    axes[0].set_ylabel("Fraction of replay windows")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[key]) for key in ["ready", "degraded", "failed"]]
    fig.legend(
        handles,
        ["Handoff-ready cue ($\\leq 1.0$)", "Degraded cue $(1.0, 5.0]$", "Unusable cue $(>5.0)$"],
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 1.05),
    )
    _save(fig, "figure_operational_utility.png")


def main() -> None:
    plot_system_pipeline()
    plot_frontend_flow()
    plot_regime_comparison()
    plot_ablation_mixed()
    plot_formation_generalization()
    plot_runtime()
    if (EXP / "sensitivity_result.json").exists():
        plot_sensitivity_sweep()
    if (EXP / "scaling_result.json").exists():
        plot_scaling()
    if (EXP / "observability_result.json").exists():
        plot_observability()
    if (EXP / "active_selection_result.json").exists():
        plot_active_selection()
    if (EXP / "story_benchmark_result.json").exists():
        plot_story_benchmark()
        plot_story_cdf()
    if (EXP / "selection_benefit_map.json").exists():
        plot_selection_benefit_map()
    if (EXP / "screening_weight_sensitivity.json").exists():
        plot_screening_weight_sensitivity()
    elif (EXP / "screening_weight_grid_result.json").exists():
        plot_screening_weight_sensitivity()
    if (EXP / "screening_score_ablation.json").exists():
        plot_screening_score_ablation()
    if (EXP / "active_selection_result.json").exists():
        plot_screening_case_studies()
    if (EXP / "story_revision_analysis.json").exists():
        plot_threshold_sweep()
        plot_ransac_failure_case()
    if (EXP / "public_dataset3_replay_result.json").exists():
        plot_public_real_replay()
    if (EXP / "pybullet_replay_result.json").exists() and (EXP / "pybullet_replay_traces.json").exists():
        plot_pybullet_validation()
        plot_operational_utility()
    if (EXP / "tracking_proxy_result.json").exists():
        plot_tracking_proxy()


if __name__ == "__main__":
    main()
