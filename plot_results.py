"""Generate publication-style plots from experiment outputs."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch, Polygon
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import to_hex, to_rgb


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

def _mix(color: str | tuple[float, float, float] | tuple[float, float, float, float], base: str = "#FFFFFF", ratio: float = 0.25) -> str:
    rgb = np.asarray(to_rgb(color), dtype=float)
    base_rgb = np.asarray(to_rgb(base), dtype=float)
    mixed = (1.0 - ratio) * rgb + ratio * base_rgb
    return to_hex(np.clip(mixed, 0.0, 1.0))


def _cw(position: float, mix: float = 0.22) -> str:
    return _mix(plt.get_cmap("coolwarm")(position), ratio=mix)


PALETTE = {
    # Hybrid editorial palette inferred from Nature-style accessibility guidance
    # plus Paul Tol categorical schemes and Crameri-style muted diverging ramps.
    "ink": "#1F2C45",
    "muted_ink": "#53627C",
    "text_soft": "#6B7891",
    "grid": "#E4EAF2",
    "panel": "#FAFBFD",
    "warm_panel": "#F6F1E7",
    "soft_center": "#F6F2EA",
    "note_fill": "#FCFDFE",
    "line_light": "#D6DEE8",
    "shadow": "#0F172A",
    "ls": "#8F949C",
    "huber": "#9FC8DB",
    "robust": "#4477AA",
    "tukey": "#72A79A",
    "ransac": "#C06C7A",
    "gnc": "#78A6D0",
    "pso": "#C9B273",
    "sa": "#9C7BA0",
    "active_all": "#999999",
    "active_random": "#E0E5EC",
    "active_spread": "#78A6D0",
    "active_crlb": "#C3D3E8",
    "active_residual": "#C7A259",
    "active_reliability": "#4FA69A",
    "active_proposed": "#4477AA",
    "active_adaptive": "#9C6C8E",
    "ready": "#7B97C6",
    "degraded": "#C8A15A",
    "extreme": "#CA7B70",
    "sensor_fill": "#E6EBF2",
    "sensor_edge": "#7B8797",
    "sensor_alert": "#E2D2AF",
    "sensor_alert_edge": "#A68457",
    "trajectory": "#9AADCB",
    "target": "#C85F5C",
}

plt.rcParams.update(
    {
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "axes.edgecolor": PALETTE["line_light"],
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "axes.titleweight": "semibold",
        "axes.labelsize": 12.2,
        "axes.titlesize": 14.0,
        "axes.labelcolor": PALETTE["ink"],
        "text.color": PALETTE["ink"],
        "legend.fontsize": 10.5,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "xtick.color": PALETTE["muted_ink"],
        "ytick.color": PALETTE["muted_ink"],
        "grid.color": PALETTE["grid"],
        "grid.linewidth": 0.62,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
    }
)

EDITORIAL_DIVERGING = LinearSegmentedColormap.from_list(
    "editorial_diverging",
    [PALETTE["extreme"], PALETTE["soft_center"], PALETTE["robust"]],
)
EDITORIAL_MULTI = LinearSegmentedColormap.from_list(
    "editorial_multi",
    [PALETTE["active_all"], PALETTE["active_spread"], PALETTE["active_reliability"], PALETTE["robust"], PALETTE["active_adaptive"]],
)


def _editorial_series(count: int, start: float = 0.14, stop: float = 0.86):
    if count <= 1:
        return [EDITORIAL_MULTI((start + stop) / 2.0)]
    return EDITORIAL_MULTI(np.linspace(start, stop, count))


def _save(fig: plt.Figure, name: str, *, tight: bool = True) -> None:
    stem = Path(name).stem
    if tight:
        fig.tight_layout(pad=0.55)
    SUBMISSION_FIG.mkdir(parents=True, exist_ok=True)
    for suffix in [".png", ".pdf", ".svg"]:
        out = EXP / f"{stem}{suffix}"
        sub_out = SUBMISSION_FIG / f"{stem}{suffix}"
        save_kwargs = {"facecolor": "white"}
        if suffix == ".png":
            save_kwargs["dpi"] = 450
        fig.savefig(out, **save_kwargs)
        fig.savefig(sub_out, **save_kwargs)
    plt.close(fig)


def _hex_to_rgb_components(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _tikz_color_block(names: list[str]) -> str:
    lines = []
    for name in names:
        r, g, b = _hex_to_rgb_components(PALETTE[name])
        lines.append(f"\\definecolor{{{name}}}{{RGB}}{{{r},{g},{b}}}")
    return "\n".join(lines)


def _render_tikz_figure(stem: str, tikz_body: str) -> None:
    color_block = _tikz_color_block(
        [
            "ink",
            "muted_ink",
            "line_light",
            "panel",
            "huber",
            "robust",
            "gnc",
            "active_adaptive",
            "active_all",
            "degraded",
            "ransac",
        ]
    )
    tex_source = textwrap.dedent(
        rf"""
        \documentclass[tikz,border=2pt]{{standalone}}
        \usepackage[T1]{{fontenc}}
        \usepackage{{mathpazo}}
        \usepackage{{tikz}}
        \usetikzlibrary{{arrows.meta,positioning,fit,calc,backgrounds,shapes.geometric}}
        {color_block}
        \begin{{document}}
        {tikz_body}
        \end{{document}}
        """
    ).strip() + "\n"

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        tex_path = tmpdir / f"{stem}.tex"
        pdf_path = tmpdir / f"{stem}.pdf"
        png_path = tmpdir / f"{stem}.png"
        tex_path.write_text(tex_source, encoding="utf-8")

        subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_path.name,
            ],
            cwd=tmpdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        subprocess.run(
            [
                "sips",
                "-s",
                "format",
                "png",
                str(pdf_path),
                "--out",
                str(png_path),
            ],
            cwd=tmpdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        subprocess.run(
            ["sips", "-Z", "2600", str(png_path)],
            cwd=tmpdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        SUBMISSION_FIG.mkdir(parents=True, exist_ok=True)
        for target_root in [EXP, SUBMISSION_FIG]:
            shutil.copy2(pdf_path, target_root / f"{stem}.pdf")
            shutil.copy2(png_path, target_root / f"{stem}.png")
            stale_svg = target_root / f"{stem}.svg"
            if stale_svg.exists():
                stale_svg.unlink()


def _style_axes(ax, *, grid_axis: str = "y") -> None:
    ax.set_facecolor("white")
    ax.tick_params(colors=PALETTE["muted_ink"])
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(PALETTE["line_light"])
        ax.spines[spine].set_linewidth(1.0)
    if grid_axis:
        ax.grid(True, axis=grid_axis, linestyle=(0, (1.0, 3.1)), linewidth=0.62, alpha=0.72, color=PALETTE["grid"])


def _light_panel(ax, color: str = PALETTE["panel"]) -> None:
    ax.set_facecolor(color)


def _style_legend(legend) -> None:
    if legend is None:
        return
    frame = legend.get_frame()
    frame.set_facecolor("white")
    frame.set_edgecolor(PALETTE["line_light"])
    frame.set_linewidth(0.8)


def _range_handles() -> list[Line2D]:
    return [
        Line2D([0], [0], color=PALETTE["muted_ink"], linewidth=2.8, label="Median to P95"),
        Line2D([0], [0], marker="o", markersize=7, markerfacecolor="white", markeredgecolor=PALETTE["ink"], linewidth=0, label="Median"),
        Line2D([0], [0], marker="o", markersize=6, markerfacecolor=PALETTE["ink"], markeredgecolor=PALETTE["ink"], linewidth=0, label="P95"),
    ]


def _box(
    ax,
    xy: tuple[float, float],
    wh: tuple[float, float],
    text: str,
    fc: str,
    ec: str = PALETTE["muted_ink"],
    lw: float = 1.2,
    fs: int = 10,
) -> FancyBboxPatch:
    shadow = FancyBboxPatch(
        (xy[0] + 0.004, xy[1] - 0.004),
        wh[0],
        wh[1],
        boxstyle="round,pad=0.015,rounding_size=0.025",
        facecolor=PALETTE["shadow"],
        edgecolor="none",
        alpha=0.05,
        zorder=0,
    )
    ax.add_patch(shadow)
    patch = FancyBboxPatch(
        xy,
        wh[0],
        wh[1],
        boxstyle="round,pad=0.015,rounding_size=0.025",
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
        color=PALETTE["ink"],
        linespacing=1.15,
    )
    return patch


def _diamond(
    ax,
    center: tuple[float, float],
    wh: tuple[float, float],
    text: str,
    fc: str,
    ec: str,
    lw: float = 1.3,
    fs: int = 9.8,
) -> Polygon:
    cx, cy = center
    w, h = wh
    shadow_pts = np.array(
        [
            (cx, cy + h / 2.0),
            (cx + w / 2.0, cy),
            (cx, cy - h / 2.0),
            (cx - w / 2.0, cy),
        ],
        dtype=float,
    )
    shadow = Polygon(shadow_pts + np.array([0.004, -0.004]), closed=True, facecolor=PALETTE["shadow"], edgecolor="none", alpha=0.05)
    ax.add_patch(shadow)
    patch = Polygon(shadow_pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=lw)
    ax.add_patch(patch)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=PALETTE["ink"], linespacing=1.12)
    return patch


def _arrow(ax, start: tuple[float, float], end: tuple[float, float], color: str = PALETTE["muted_ink"], lw: float = 1.6) -> None:
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


def _orth_connector(
    ax,
    points: list[tuple[float, float]],
    *,
    color: str = PALETTE["muted_ink"],
    lw: float = 1.8,
    arrow_end: bool = True,
) -> None:
    if len(points) < 2:
        return
    if len(points) > 2:
        xs = [p[0] for p in points[:-1]]
        ys = [p[1] for p in points[:-1]]
        ax.plot(xs, ys, color=color, linewidth=lw, solid_capstyle="round")
    start = points[-2]
    end = points[-1]
    _arrow(ax, start, end, color=color, lw=lw)


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
    tikz = r"""
\begin{tikzpicture}[
  x=1cm,y=1cm,
  >=Latex,
  font=\fontsize{10.8}{12.6}\selectfont,
  box/.style={rounded corners=7pt, draw=line_light, line width=0.9pt, align=center, text=ink, minimum height=1.85cm, inner sep=5.5pt},
  stagebox/.style={rounded corners=8pt, draw=robust, line width=1.15pt, align=center, text=ink, minimum height=1.35cm, inner sep=5.5pt},
  softarrow/.style={-Latex, draw=muted_ink, line width=1.2pt},
  auxarrow/.style={-Latex, draw=active_adaptive, line width=1.0pt},
  note/.style={text=muted_ink, font=\fontsize{10.2}{12.2}\selectfont}
]

\node[box, fill=huber!18, minimum width=3.7cm] (pose) at (0,0)
{Observer Pose Input\\GNSS / VIO / INS / SLAM\\reported with uncertainty};

\node[box, fill=robust!14, minimum width=3.85cm, right=1.0cm of pose] (bearing)
{Bearing Extraction\\EO / DF payloads\\asynchronous angle cues};

\node[stagebox, fill=robust!16, minimum width=3.8cm, right=1.05cm of bearing, yshift=0.78cm] (stageone)
{Always-on robust fusion\\(consensus + trimmed LM)};

\node[stagebox, fill=active_adaptive!14, draw=active_adaptive, minimum width=3.8cm, below=0.58cm of stageone] (stagetwo)
{Optional screening add-on\\(budget / heterogeneity only)};

\node[draw=robust!40, rounded corners=10pt, line width=1.0pt, inner xsep=0.55cm, inner ysep=0.48cm, fit=(stageone)(stagetwo)] (module) {};

\node[box, fill=degraded!18, draw=degraded!55!line_light, minimum width=3.35cm, right=1.1cm of module, yshift=0.48cm] (cue)
{Downstream Target Cue\\position estimate\\for current cycle};

\node[box, fill=ransac!15, draw=ransac!55!line_light, minimum width=3.35cm, below=0.6cm of cue] (consumer)
{Consumers\\tracker / handoff /\\formation replanning};

\draw[softarrow] (pose) -- (bearing);
\draw[softarrow] (bearing) -- ($(module.west)+(0.0,0.0)$);
\draw[softarrow] ($(module.east)+(0.0,0.0)$) -- (cue.west);
\draw[auxarrow] (cue.south) -- (consumer.north);

\node[note, below=0.7cm of module, align=center] {Engineering rule: keep all-sensor robust fusion by default; activate screening only when\\budget limits or cue heterogeneity justify pruning.};
\end{tikzpicture}
"""
    _render_tikz_figure("figure_system_pipeline", tikz)


def plot_frontend_flow() -> None:
    tikz = r"""
\begin{tikzpicture}[
  x=1cm,y=1cm,
  >=Latex,
  font=\fontsize{10.8}{12.6}\selectfont,
  box/.style={rounded corners=7pt, draw=line_light, line width=0.95pt, align=center, text=ink, minimum height=1.55cm, inner sep=5.5pt},
  gate/.style={diamond, aspect=1.55, draw=degraded!65!line_light, line width=1.0pt, align=center, text=ink, inner sep=2.4pt, minimum width=2.4cm, fill=degraded!16},
  softarrow/.style={-Latex, draw=muted_ink, line width=1.2pt},
  yesarrow/.style={-Latex, draw=active_adaptive, line width=1.0pt},
  noarrow/.style={-Latex, draw=active_all, line width=1.0pt},
  note/.style={text=muted_ink, font=\fontsize{10.0}{12.0}\selectfont}
]

\node[box, fill=huber!18, minimum width=3.35cm] (input) at (0,0)
{Current-cycle bearings\\+ reported poses};

\node[box, fill=gnc!16, draw=robust!45!line_light, minimum width=3.35cm, right=0.9cm of input] (seed)
{Pairwise intersections\\+ consensus seeding};

\node[box, fill=robust!16, draw=robust, line width=1.05pt, minimum width=3.75cm, right=0.95cm of seed] (irls)
{Trimmed IRLS / LM\\optional common-bias\\correction};

\node[gate, right=1.0cm of irls] (gate)
{Gate:\\heterogeneous or\\budget-limited\\window?};

\node[box, fill=active_adaptive!14, draw=active_adaptive, minimum width=3.0cm, above right=0.15cm and 1.05cm of gate] (screen)
{Optional\\screening};

\node[box, fill=active_all!16, draw=active_all, minimum width=3.0cm, below right=0.12cm and 1.05cm of gate] (keep)
{Keep all-sensor cue\\(default path)};

\node[box, fill=ransac!14, draw=ransac!60!line_light, minimum width=2.9cm, minimum height=2.05cm, right=1.0cm of gate] (output)
{Output cue\\for tracking /\\handoff /\\replanning};

\draw[softarrow] (input) -- (seed);
\draw[softarrow] (seed) -- (irls);
\draw[softarrow] (irls) -- (gate);
\draw[softarrow] (gate) -- (output);

\draw[yesarrow] (gate.north east) |- node[pos=0.24, right, text=active_adaptive, font=\fontsize{9.6}{10.5}\selectfont] {yes} (screen.west);
\draw[yesarrow] (screen.east) |- (output.north);

\draw[noarrow] (gate.south east) |- node[pos=0.25, right, text=active_all, font=\fontsize{9.6}{10.5}\selectfont] {no} (keep.west);
\draw[noarrow] (keep.east) |- (output.south);

\end{tikzpicture}
"""
    _render_tikz_figure("figure_frontend_flow", tikz)


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
    colors = [PALETTE["ls"], PALETTE["huber"], PALETTE["gnc"], PALETTE["ransac"], PALETTE["robust"]]
    ranking = sorted(zip(labels, [method_stats[m]["median_ms"] for m in methods], colors), key=lambda item: item[1])

    fig, axes = plt.subplots(2, 1, figsize=(10.8, 7.2), gridspec_kw={"height_ratios": [0.92, 1.15]})
    rank_labels = [item[0] for item in ranking]
    rank_vals = [item[1] for item in ranking]
    rank_colors = [item[2] for item in ranking]
    y = np.arange(len(rank_labels))
    axes[0].barh(
        y,
        rank_vals,
        height=0.56,
        color=[_mix(color, ratio=0.58) for color in rank_colors],
        edgecolor=rank_colors,
        linewidth=1.2,
    )
    for idx, val in enumerate(rank_vals):
        axes[0].text(
            val + 0.42,
            idx,
            f"{val:.2f} ms",
            va="center",
            ha="left",
            fontsize=10.1,
            color=PALETTE["ink"],
        )
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(rank_labels)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Median latency (ms)")
    axes[0].set_title("Per-cycle latency by method", loc="left", fontsize=13.2)
    axes[0].set_xlim(0.0, max(rank_vals) * 1.18)
    _light_panel(axes[0], _mix(PALETTE["panel"], ratio=0.06))
    _style_axes(axes[0], grid_axis="x")

    counts = payload["scaling"]["counts"]
    for key, label, color in [
        ("stage1_proposed", "Stage 1 robust core", PALETTE["robust"]),
        ("stage2_screening", "Stage 2 screening", PALETTE["active_spread"]),
        ("stage2_adaptive", "Adaptive gate", PALETTE["active_adaptive"]),
    ]:
        ys = [payload["scaling"][key][str(count)]["median_ms"] for count in counts if str(count) in payload["scaling"][key]]
        xs = [count for count in counts if str(count) in payload["scaling"][key]]
        axes[1].plot(xs, ys, marker="o", markersize=6.3, linewidth=2.45, color=color, label=label, alpha=0.96)
    axes[1].set_xlabel("Number of observers")
    axes[1].set_ylabel("Median runtime (ms)")
    axes[1].set_title("Stage-wise scaling vs. observer count", loc="left", fontsize=13.2)
    _light_panel(axes[1], _mix(PALETTE["panel"], ratio=0.04))
    _style_axes(axes[1], grid_axis="both")
    legend = axes[1].legend(loc="upper left", ncol=1)
    _style_legend(legend)
    hardware = payload["meta"]["hardware"]
    axes[1].text(
        0.98,
        0.02,
        f"{hardware['cpu']}\nPython {hardware['python']}",
        transform=axes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=8.8,
        color=PALETTE["muted_ink"],
        bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": PALETTE["line_light"]},
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

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.9), gridspec_kw={"width_ratios": [0.92, 1.08]})
    summary_rows = sorted(zip(labels, overall_medians, catastrophic, colors), key=lambda item: item[1])
    y = np.arange(len(summary_rows))
    axes[0].barh(y, [row[1] for row in summary_rows], color=[row[3] for row in summary_rows], height=0.68)
    for idx, (_label, median, fail, _color) in enumerate(summary_rows):
        axes[0].text(median + 0.012, idx, f"{median:.2f} | fail={fail:.02f}", va="center", ha="left", fontsize=8.8, color=PALETTE["ink"])
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([row[0] for row in summary_rows])
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Median error")
    axes[0].set_title("Budgeted screening summary", loc="left")
    _style_axes(axes[0], grid_axis="x")

    for key, label, color in zip(policy_keys, labels, colors):
        ys = [summary["by_num_uavs"][str(count)][key]["median"] for count in counts]
        axes[1].plot(counts, ys, marker="o", markersize=6.4, linewidth=2.2, label=label, color=color)
    axes[1].set_xlabel("Number of UAVs")
    axes[1].set_ylabel("Median error")
    axes[1].set_title("Observer-count scaling", loc="left")
    _style_axes(axes[1], grid_axis="both")
    legend = axes[1].legend(loc="upper right", ncol=2)
    _style_legend(legend)

    _save(fig, "figure_active_selection.png")


def plot_story_benchmark() -> None:
    payload = json.loads((EXP / "story_benchmark_result.json").read_text(encoding="utf-8"))
    regimes = ["clean", "outlier", "mixed", "pose_uncertainty", "heterogeneous_bias"]
    regime_labels = ["Clean", "Outlier", "Mixed", "Pose Noise", "Het. Bias"]
    methods = [
        ("least_squares_error", "LS", PALETTE["ls"], "o"),
        ("robust_error", "Huber", PALETTE["huber"], "s"),
        ("ransac_error", "RANSAC", PALETTE["ransac"], "^"),
        ("gnc_gm_error", "GNC-GM", PALETTE["gnc"], "D"),
        ("robust_bias_trimmed_error", "Proposed", PALETTE["robust"], "o"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(13.8, 4.9), gridspec_kw={"width_ratios": [1.06, 0.94]})
    x = np.arange(len(regimes))
    left_vals = []
    right_vals = []
    for key, label, color, marker in methods:
        medians = [payload["summary"]["by_regime"][regime][key]["median"] for regime in regimes]
        left_vals.extend(medians)
        axes[0].plot(
            x,
            medians,
            marker=marker,
            markersize=6.8,
            linewidth=2.2,
            color=color,
            label=label,
        )
        cat = [payload["summary"]["by_regime"][regime][key]["catastrophic_at_0_5R"] for regime in regimes]
        right_vals.extend(cat)
        axes[1].plot(
            x,
            cat,
            marker=marker,
            markersize=6.8,
            linewidth=2.2,
            color=color,
            label=label,
        )
    for ax in axes:
        ax.axvspan(0.5, 2.5, color=PALETTE["warm_panel"], alpha=0.56, zorder=0)
        ax.text(
            1.5,
            0.96,
            "corruption-dominant cases",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=9.3,
            color=PALETTE["muted_ink"],
        )
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(regime_labels, rotation=10)
    axes[0].set_ylabel("Median error (normalized by $R$)")
    axes[0].set_title("Localization error across corruption regimes", loc="left")
    axes[0].set_ylim(0.0, max(left_vals) * 1.12)
    _style_axes(axes[0], grid_axis="y")

    axes[1].set_xticks(x)
    axes[1].set_xticklabels(regime_labels, rotation=10)
    axes[1].set_ylim(0.0, max(right_vals) * 1.24)
    axes[1].set_ylabel("Failure rate ($>0.5R$)")
    axes[1].set_title("Failure-risk envelope", loc="left")
    _style_axes(axes[1], grid_axis="y")
    handles, labels = axes[1].get_legend_handles_labels()
    legend = axes[1].legend(
        handles,
        labels,
        loc="upper right",
        ncol=2,
        columnspacing=1.1,
        handlelength=2.0,
    )
    _style_legend(legend)
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
    titles = ["Proposed Screening vs. All-Sensor Robust Fusion", "Adaptive Screening vs. All-Sensor Robust Fusion"]

    cmap = EDITORIAL_DIVERGING
    benefit_grids = []
    for policy in policies:
        grid = np.zeros((len(outlier_rates), len(budget_fracs)), dtype=float)
        for i, outlier_rate in enumerate(outlier_rates):
            for j, budget_frac in enumerate(budget_fracs):
                key = f"outlier_{outlier_rate:.2f}__budget_{budget_frac:.2f}"
                grid[i, j] = -payload["summary"][key]["delta_vs_all"][policy]
        benefit_grids.append(grid)

    max_abs = max(float(np.max(np.abs(grid))) for grid in benefit_grids)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0.0, vmax=max_abs)
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.9), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.90, bottom=0.16, top=0.89, wspace=0.10)
    for ax, grid, title in zip(axes, benefit_grids, titles):
        _light_panel(ax, PALETTE["note_fill"])
        im = ax.imshow(grid, cmap=cmap, norm=norm, aspect="auto", origin="lower", interpolation="nearest")
        ax.set_xticks(np.arange(len(budget_fracs)))
        ax.set_xticklabels([f"{v:.2f}" for v in budget_fracs])
        ax.set_yticks(np.arange(len(outlier_rates)))
        ax.set_yticklabels([f"{v:.2f}" for v in outlier_rates])
        ax.set_xlabel("Budget Fraction")
        ax.set_title(title)
        for i in range(len(outlier_rates)):
            for j in range(len(budget_fracs)):
                ax.text(j, i, f"{grid[i, j]:+.2f}", ha="center", va="center", fontsize=8.4, color=PALETTE["ink"])
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_color(PALETTE["line_light"])
            spine.set_linewidth(1.0)
    axes[0].set_ylabel("Outlier Rate")
    cbar = fig.colorbar(im, ax=axes, fraction=0.038, pad=0.03)
    cbar.set_label("Median error difference\nvs. all-sensor fusion", color=PALETTE["ink"], labelpad=10)
    cbar.outline.set_edgecolor(PALETTE["line_light"])
    cbar.outline.set_linewidth(0.9)
    cbar.ax.tick_params(colors=PALETTE["muted_ink"])
    _save(fig, "figure_selection_benefit_map.png", tight=False)


def plot_screening_weight_sensitivity() -> None:
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
            medianprops={"color": PALETTE["ink"], "linewidth": 1.4},
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
        ax.axvline(0.2, color=PALETTE["line_light"], linestyle="--", linewidth=1.1)
        ax.axvline(0.3, color=PALETTE["active_spread"], linestyle="--", linewidth=1.1)
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
            geo_ax.plot([start[0], end[0]], [start[1], end[1]], linestyle="--", linewidth=1.0, color=PALETTE["line_light"], alpha=0.88)
            pose_error = float(sensor.get("pose_error", 0.0))
            sensor_bias = float(sensor.get("sensor_bias", 0.0))
            highlight = pose_error > 0.30 or abs(sensor_bias) > 0.05
            face = PALETTE["sensor_alert"] if highlight else PALETTE["sensor_fill"]
            edge = PALETTE["sensor_alert_edge"] if highlight else PALETTE["sensor_edge"]
            geo_ax.scatter(sensor["x"], sensor["y"], s=74, color=face, edgecolor=edge, linewidth=0.95, zorder=3)

        geo_ax.scatter(target["x"], target["y"], marker="*", s=240, color=PALETTE["target"], edgecolor="white", linewidth=0.9, zorder=5, label="True target")
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
            txt_color = PALETTE["robust"] if idx == best_idx else PALETTE["ink"]
            bar_ax.text(idx, val, f"{val:.2f}", ha="center", va="bottom", fontsize=9.2, color=txt_color)
        bar_ax.set_ylabel("Localization error")
        bar_ax.set_title("Method error on this window")
        bar_ax.grid(True, axis="y", linestyle=":", alpha=0.35)
        bar_ax.tick_params(axis="x", rotation=10)
    _save(fig, "figure_ransac_failure_case.png")


def plot_tracking_proxy() -> None:
    payload = json.loads((EXP / "tracking_proxy_result.json").read_text(encoding="utf-8"))
    methods = ["LS", "GNC-GM", "RANSAC", "Proposed"]
    overall = payload["summary"]["overall"]
    disturbed = payload["summary"]["by_regime"]["disturbed_pybullet"]
    metrics = [
        ("overall_break", "Overall sequence break rate", [overall[m]["sequence_break_rate"] for m in methods], True, "lower"),
        ("disturbed_break", "Disturbed sequence break rate", [disturbed[m]["sequence_break_rate"] for m in methods], True, "lower"),
        ("rapid_reacq", "Rapid reacquisition rate", [disturbed[m]["mean_rapid_reacquisition_rate"] for m in methods], True, "higher"),
        ("disturbed_roi", "Disturbed ROI radius (P90)", [disturbed[m]["median_roi_radius_p90"] for m in methods], False, "lower"),
    ]
    colors = [PALETTE["ls"], PALETTE["gnc"], PALETTE["ransac"], PALETTE["robust"]]

    fig, axes = plt.subplots(2, 2, figsize=(11.4, 6.9))
    for ax, (_metric_key, title, vals, as_percent, direction) in zip(axes.flat, metrics):
        ranked = sorted(
            zip(methods, vals, colors),
            key=lambda item: item[1],
            reverse=(direction == "higher"),
        )
        ranked_methods = [item[0] for item in ranked]
        ranked_vals = [item[1] for item in ranked]
        ranked_colors = [item[2] for item in ranked]
        ypos = np.arange(len(ranked_methods))
        fill_colors = [_mix(color, ratio=0.58) for color in ranked_colors]

        ax.barh(
            ypos,
            ranked_vals,
            height=0.58,
            color=fill_colors,
            edgecolor=ranked_colors,
            linewidth=1.15,
        )
        label_offset = 0.018 * max(max(ranked_vals), 1.0)
        for idx, (method, val, color) in enumerate(zip(ranked_methods, ranked_vals, ranked_colors)):
            ax.text(
                val + label_offset,
                idx,
                f"{val:.2f}",
                va="center",
                ha="left",
                fontsize=9.6,
                color=PALETTE["ink"],
            )
        ax.set_yticks(ypos)
        ax.set_yticklabels(ranked_methods)
        ax.invert_yaxis()
        ax.set_title(f"{title} {'↓' if direction == 'lower' else '↑'}", loc="left", fontsize=12.7)
        ax.set_xlim(0.0, max(ranked_vals) * 1.18 if max(ranked_vals) > 0 else 1.0)
        _light_panel(ax, _mix(PALETTE["panel"], ratio=0.05))
        _style_axes(ax, grid_axis="x")
        if as_percent:
            ax.xaxis.set_major_formatter(PercentFormatter(1.0))
            ax.set_xlabel("Rate")
        else:
            ax.set_xlabel("P90 radius")
        if title == "Disturbed break rate" and np.allclose(ranked_vals, ranked_vals[0]):
            ax.text(
                0.985,
                0.08,
                "All methods tie under disturbed replay",
                transform=ax.transAxes,
                ha="right",
                va="bottom",
                fontsize=8.6,
                color=PALETTE["muted_ink"],
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

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), gridspec_kw={"width_ratios": [1.05, 1.15]})
    policy_labels = [
        ("all_sensors", "All-sensor", PALETTE["active_all"]),
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
        target = case["target"]
        valid_sensors = case["valid_sensors"]
        valid_bearings = case["valid_bearings"]
        estimates = case["estimates"]
        row = case["row"]

        for sensor, bearing in zip(valid_sensors, valid_bearings):
            ray = np.array([np.cos(bearing), np.sin(bearing)], dtype=float)
            start = np.array([sensor.x, sensor.y], dtype=float)
            end = start + 16.0 * ray
            geo_ax.plot([start[0], end[0]], [start[1], end[1]], linestyle="--", linewidth=0.9, color=PALETTE["line_light"], alpha=0.72, zorder=1)

        geo_ax.scatter(
            [sensor.x for sensor in valid_sensors],
            [sensor.y for sensor in valid_sensors],
            s=46,
            facecolor="white",
            color=PALETTE["sensor_fill"],
            edgecolor=PALETTE["active_random"],
            linewidth=0.8,
            label="Valid sensors",
            zorder=2,
        )

        proposed_sel = estimates["observability_robust"]["selected_indices"]
        geo_ax.scatter(
            [valid_sensors[idx].x for idx in proposed_sel],
            [valid_sensors[idx].y for idx in proposed_sel],
            s=84,
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

        geo_ax.scatter(target[0], target[1], marker="*", s=220, color=PALETTE["target"], edgecolor="white", linewidth=0.8, zorder=5, label="True target")
        geo_ax.scatter(*estimates["all_sensors"]["point"], marker="X", s=90, color=PALETTE["active_all"], zorder=5, label="All-sensor estimate")
        geo_ax.scatter(*estimates["observability_robust"]["point"], marker="s", s=76, color=PALETTE["active_proposed"], zorder=5, label="Proposed estimate")
        geo_ax.scatter(*estimates["adaptive"]["point"], marker="D", s=60, color=PALETTE["active_adaptive"], zorder=5, label="Adaptive estimate")

        geo_ax.set_aspect("equal", adjustable="box")
        _style_axes(geo_ax, grid_axis="both")
        geo_ax.set_xlabel("X")
        geo_ax.set_ylabel("Y")
        geo_ax.set_title(title, loc="left")
        geo_ax.text(
            0.02,
            0.98,
            f"{row['regime'].title()}, {row['formation'].title()}, {row['num_uavs']} observers, budget={row['budget']}",
            transform=geo_ax.transAxes,
            ha="left",
            va="top",
            fontsize=9.0,
            color=PALETTE["muted_ink"],
            bbox={"boxstyle": "round,pad=0.20", "facecolor": "white", "edgecolor": PALETTE["line_light"]},
        )
        if row_idx == 0:
            legend = geo_ax.legend(loc="upper right", fontsize=8.1)
            _style_legend(legend)

        sorted_rows = sorted(
            [(key, label, estimates[key]["error"], color) for key, label, color in policy_labels],
            key=lambda item: item[2],
        )
        labels = [item[1] for item in sorted_rows]
        vals = [item[2] for item in sorted_rows]
        colors = [item[3] for item in sorted_rows]
        ypos = np.arange(len(labels))
        bar_ax.barh(ypos, vals, color=colors, edgecolor="none", height=0.68)
        bar_ax.axvline(estimates["all_sensors"]["error"], color=PALETTE["active_all"], linestyle="--", linewidth=1.2)
        best_idx = int(np.argmin(vals))
        for idx, val in enumerate(vals):
            txt_color = PALETTE["robust"] if idx == best_idx else PALETTE["ink"]
            bar_ax.text(val + max(vals) * 0.02, idx, f"{val:.2f}", va="center", ha="left", fontsize=8.9, color=txt_color)
        bar_ax.set_yticks(ypos)
        bar_ax.set_yticklabels(labels)
        bar_ax.invert_yaxis()
        bar_ax.set_xlabel("Localization error")
        bar_ax.set_title("Policy outcome on this case", loc="left")
        _style_axes(bar_ax, grid_axis="x")

        if not estimates["adaptive"]["triggered"]:
            bar_ax.text(
                0.02,
                0.06,
                "Adaptive gate kept full-set fusion",
                transform=bar_ax.transAxes,
                ha="left",
                va="bottom",
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

    trajectory_colors = _editorial_series(len(trace["drones"]), 0.10, 0.88)
    for color, drone in zip(trajectory_colors, trace["drones"]):
        axes[0].plot(drone["x"], drone["y"], linewidth=1.4, alpha=0.86, color=color)
    axes[0].scatter(
        [trace["meta"]["target"]["x"]],
        [trace["meta"]["target"]["y"]],
        marker="*",
        s=180,
        color=PALETTE["target"],
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
        axes[1].text(x[idx] - width / 2, ls_medians[idx], f"P90={value:.2f}", ha="center", va="bottom", fontsize=8, color=PALETTE["muted_ink"])
    for idx, value in enumerate(rb_p90):
        axes[1].text(x[idx] + width / 2, rb_medians[idx], f"P90={value:.2f}", ha="center", va="bottom", fontsize=8, color=PALETTE["robust"])
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
        axes[2].text(x[idx] - width / 2, ls_success[idx], f"fail={value:.2f}", ha="center", va="bottom", fontsize=8, color=PALETTE["muted_ink"])
    for idx, value in enumerate(rb_fail):
        axes[2].text(x[idx] + width / 2, rb_success[idx], f"fail={value:.2f}", ha="center", va="bottom", fontsize=8, color=PALETTE["robust"])
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

    fig, axes = plt.subplots(1, 3, figsize=(14.6, 5.2), gridspec_kw={"width_ratios": [1.0, 1.05, 1.0]})

    ax = axes[0]
    ax.plot(trajectory[:, 0], trajectory[:, 1], color=PALETTE["trajectory"], linewidth=1.7, alpha=0.9, label="RTK trajectory")
    ax.scatter(
        trajectory[0, 0],
        trajectory[0, 1],
        marker="o",
        s=56,
        color=PALETTE["robust"],
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
        color=PALETTE["extreme"],
        edgecolor="white",
        linewidth=0.6,
        zorder=5,
        label="End",
    )
    cam_colors = _editorial_series(len(camera_names), 0.14, 0.82)
    for idx, (name, color) in enumerate(zip(camera_names, cam_colors)):
        ax.scatter(
            camera_positions[idx, 0],
            camera_positions[idx, 1],
            s=80,
            color=color,
            edgecolor="white",
            linewidth=0.8,
            zorder=6,
        )
        ax.text(
            camera_positions[idx, 0] + 1.6,
            camera_positions[idx, 1] + 1.2,
            f"C{idx}",
            fontsize=8.4,
            color=PALETTE["ink"],
            bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": "none", "alpha": 0.78},
        )
    ax.set_title("Measured-data multi-view replay", loc="left")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_aspect("equal", adjustable="box")
    _style_axes(ax, grid_axis="both")
    legend = ax.legend(loc="upper left", fontsize=8.3)
    _style_legend(legend)

    ax = axes[1]
    method_order = methods
    y_positions = np.array([7, 6, 5, 4, 2.2, 1.2, 0.2, -0.8], dtype=float)
    y_labels = []
    y_values = []
    for regime_idx, regime_key in enumerate(regime_keys):
        panel = result_payload["summary"]["by_regime"][regime_key]
        for method_idx, (method_key, label, color) in enumerate(method_order):
            y = y_positions[regime_idx * len(method_order) + method_idx]
            median = panel[method_key]["median"]
            p95 = panel[method_key]["p95"]
            ax.hlines(y, median, p95, color=color, linewidth=4.4, alpha=0.95)
            ax.scatter(median, y, s=54, facecolor="white", edgecolor=color, linewidth=1.3, zorder=3)
            ax.scatter(p95, y, s=42, facecolor=color, edgecolor="white", linewidth=0.8, zorder=3)
            y_labels.append(label)
            y_values.append(y)
    ax.axhline(3.2, color=PALETTE["line_light"], linestyle="--", linewidth=1.0)
    ax.text(0.0, 7.35, "Nominal", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.text(0.0, 2.75, "Disturbed", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.set_yticks(y_values)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Replay error (m)")
    ax.set_title("Median-to-tail replay envelope", loc="left")
    _style_axes(ax, grid_axis="x")
    legend = ax.legend(handles=_range_handles(), loc="lower right")
    _style_legend(legend)

    ax = axes[2]
    cue_colors = {"ready": PALETTE["ready"], "degraded": PALETTE["degraded"], "extreme": PALETTE["extreme"]}
    y_values = []
    y_labels = []
    for regime_idx, regime_key in enumerate(regime_keys):
        panel = result_payload["summary"]["by_regime"][regime_key]
        for method_idx, (method_key, label, _color) in enumerate(method_order):
            y = y_positions[regime_idx * len(method_order) + method_idx]
            ready = panel[method_key]["ready_rate"]
            degraded = panel[method_key]["degraded_rate"]
            extreme = panel[method_key]["extreme_rate"]
            ax.barh(y, ready, color=cue_colors["ready"], height=0.68)
            ax.barh(y, degraded, left=ready, color=cue_colors["degraded"], height=0.68)
            ax.barh(y, extreme, left=ready + degraded, color=cue_colors["extreme"], height=0.68)
            y_values.append(y)
            y_labels.append(label)
    ax.axhline(3.2, color=PALETTE["line_light"], linestyle="--", linewidth=1.0)
    ax.text(0.0, 7.35, "Nominal", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.text(0.0, 2.75, "Disturbed", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.set_yticks(y_values)
    ax.set_yticklabels(y_labels)
    ax.set_xlim(0.0, 1.0)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Fraction of replay windows")
    ax.set_title(f"Cue partition ({thresholds['ready']:.0f} m / {thresholds['extreme']:.0f} m)", loc="left")
    _style_axes(ax, grid_axis="x")
    legend = ax.legend(
        handles=[Patch(color=cue_colors[key], label=label) for key, label in [("ready", "Ready"), ("degraded", "Degraded"), ("extreme", "Extreme")]],
        loc="lower right",
    )
    _style_legend(legend)

    _save(fig, "figure_public_real_replay.png")


def plot_deadline_replay() -> None:
    result_payload = json.loads((EXP / "deadline_replay_result.json").read_text(encoding="utf-8"))
    regime_keys = ["deadline_nominal", "deadline_disturbed"]
    regime_labels = ["Nominal", "Disturbed"]
    methods = [
        ("least_squares", "LS", PALETTE["ls"]),
        ("gnc_gm", "GNC-GM", PALETTE["gnc"]),
        ("ransac", "RANSAC", PALETTE["ransac"]),
        ("robust_bias_trimmed", "Proposed", PALETTE["robust"]),
    ]
    availability = result_payload["summary"]["availability"]["by_regime"]
    thresholds = result_payload["meta"]["thresholds_m"]

    fig, axes = plt.subplots(1, 3, figsize=(14.6, 5.2), gridspec_kw={"width_ratios": [1.0, 1.05, 1.0]})

    ax = axes[0]
    x = np.arange(len(regime_keys))
    mean_original = np.array([availability[key]["mean_original_valid"] for key in regime_keys], dtype=float)
    mean_on_time = np.array([availability[key]["mean_on_time"] for key in regime_keys], dtype=float)
    late_count = np.array(
        [availability[key]["mean_original_valid"] * availability[key]["mean_late_ratio"] for key in regime_keys],
        dtype=float,
    )
    drop_count = np.array(
        [availability[key]["mean_original_valid"] * availability[key]["mean_packet_drop_ratio"] for key in regime_keys],
        dtype=float,
    )
    retention = np.array([availability[key]["retention_rate"] for key in regime_keys], dtype=float)

    width = 0.56
    ax.bar(x, mean_on_time, width=width, color=PALETTE["ready"], label="On-time")
    ax.bar(x, late_count, width=width, bottom=mean_on_time, color=PALETTE["degraded"], label="Late/stale")
    ax.bar(x, drop_count, width=width, bottom=mean_on_time + late_count, color=PALETTE["extreme"], label="Packet loss")
    ax.plot(x, mean_original, color=PALETTE["ink"], marker="o", linewidth=1.3, label="Original valid")
    for idx, value in enumerate(retention):
        ax.text(
            x[idx],
            mean_original[idx] + 0.14,
            f"retain={value:.0%}",
            ha="center",
            va="bottom",
            fontsize=8.8,
            color=PALETTE["muted_ink"],
        )
    ax.set_xticks(x)
    ax.set_xticklabels(regime_labels)
    ax.set_ylabel("Bearings per current cycle")
    ax.set_title("Deadline-filtered cue availability", loc="left")
    ax.set_ylim(0.0, max(np.max(mean_original) + 0.7, 4.4))
    _style_axes(ax, grid_axis="y")
    legend = ax.legend(loc="upper right", fontsize=8.4)
    _style_legend(legend)

    ax = axes[1]
    y_positions = np.array([7, 6, 5, 4, 2.2, 1.2, 0.2, -0.8], dtype=float)
    y_labels = []
    y_values = []
    for regime_idx, regime_key in enumerate(regime_keys):
        panel = result_payload["summary"]["by_regime"][regime_key]
        for method_idx, (method_key, label, color) in enumerate(methods):
            y = y_positions[regime_idx * len(methods) + method_idx]
            median = panel[method_key]["median"]
            p95 = panel[method_key]["p95"]
            ax.hlines(y, median, p95, color=color, linewidth=4.4, alpha=0.95)
            ax.scatter(median, y, s=54, facecolor="white", edgecolor=color, linewidth=1.3, zorder=3)
            ax.scatter(p95, y, s=42, facecolor=color, edgecolor="white", linewidth=0.8, zorder=3)
            y_labels.append(label)
            y_values.append(y)
    ax.axhline(3.2, color=PALETTE["line_light"], linestyle="--", linewidth=1.0)
    ax.text(0.0, 7.35, "Nominal", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.text(0.0, 2.75, "Disturbed", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.set_yticks(y_values)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Replay error (m)")
    ax.set_title("Median-to-tail under deadline replay", loc="left")
    _style_axes(ax, grid_axis="x")
    legend = ax.legend(handles=_range_handles(), loc="lower right")
    _style_legend(legend)

    ax = axes[2]
    cue_colors = {"ready": PALETTE["ready"], "degraded": PALETTE["degraded"], "extreme": PALETTE["extreme"]}
    y_values = []
    y_labels = []
    for regime_idx, regime_key in enumerate(regime_keys):
        panel = result_payload["summary"]["by_regime"][regime_key]
        for method_idx, (method_key, label, _color) in enumerate(methods):
            y = y_positions[regime_idx * len(methods) + method_idx]
            ready = panel[method_key]["ready_rate"]
            degraded = panel[method_key]["degraded_rate"]
            extreme = panel[method_key]["extreme_rate"]
            ax.barh(y, ready, color=cue_colors["ready"], height=0.68)
            ax.barh(y, degraded, left=ready, color=cue_colors["degraded"], height=0.68)
            ax.barh(y, extreme, left=ready + degraded, color=cue_colors["extreme"], height=0.68)
            y_values.append(y)
            y_labels.append(label)
    ax.axhline(3.2, color=PALETTE["line_light"], linestyle="--", linewidth=1.0)
    ax.text(0.0, 7.35, "Nominal", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.text(0.0, 2.75, "Disturbed", ha="left", va="center", fontsize=10.1, color=PALETTE["muted_ink"])
    ax.set_yticks(y_values)
    ax.set_yticklabels(y_labels)
    ax.set_xlim(0.0, 1.0)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Fraction of retained windows")
    ax.set_title(f"Cue partition ({thresholds['ready']:.0f} m / {thresholds['extreme']:.0f} m)", loc="left")
    _style_axes(ax, grid_axis="x")
    legend = ax.legend(
        handles=[Patch(color=cue_colors[key], label=label) for key, label in [("ready", "Ready"), ("degraded", "Degraded"), ("extreme", "Extreme")]],
        loc="lower right",
    )
    _style_legend(legend)

    _save(fig, "figure_deadline_replay.png")


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
        "ready": PALETTE["ready"],
        "degraded": PALETTE["degraded"],
        "failed": PALETTE["extreme"],
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
        _style_axes(ax, grid_axis="y")

    axes[0].set_ylabel("Fraction of replay windows")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[key]) for key in ["ready", "degraded", "failed"]]
    legend = fig.legend(
        handles,
        ["Handoff-ready cue ($\\leq 1.0$)", "Degraded cue $(1.0, 5.0]$", "Unusable cue $(>5.0)$"],
        loc="upper center",
        ncol=3,
        frameon=True,
        bbox_to_anchor=(0.5, 1.05),
    )
    _style_legend(legend)
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
    if (EXP / "screening_score_ablation.json").exists():
        plot_screening_score_ablation()
    if (EXP / "active_selection_result.json").exists():
        plot_screening_case_studies()
    if (EXP / "story_revision_analysis.json").exists():
        plot_threshold_sweep()
        plot_ransac_failure_case()
    if (EXP / "public_dataset3_replay_result.json").exists():
        plot_public_real_replay()
    if (EXP / "deadline_replay_result.json").exists():
        plot_deadline_replay()
    if (EXP / "pybullet_replay_result.json").exists() and (EXP / "pybullet_replay_traces.json").exists():
        plot_pybullet_validation()
        plot_operational_utility()
    if (EXP / "tracking_proxy_result.json").exists():
        plot_tracking_proxy()


if __name__ == "__main__":
    main()
