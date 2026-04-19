"""Create a publication-style graphical abstract for the submission package."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission" / "graphical_abstract"


def _box(ax, xy, width, height, title, body, facecolor, edgecolor="#1f2937"):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=1.5,
        facecolor=facecolor,
        edgecolor=edgecolor,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height - 0.08, title, ha="center", va="top", fontsize=14, weight="bold")
    ax.text(x + 0.04, y + height - 0.16, body, ha="left", va="top", fontsize=11, linespacing=1.35)


def build_graphical_abstract() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 5.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#fffdf8")

    ax.text(
        0.5,
        0.95,
        "Uncertainty-Aware Passive Localization with Credibility-Guided Selection",
        ha="center",
        va="top",
        fontsize=18,
        weight="bold",
        color="#0f172a",
    )

    _box(
        ax,
        (0.04, 0.18),
        0.25,
        0.58,
        "Why it matters",
        "Passive bearing sets can be\n"
        "biased, incomplete, or partly\n"
        "corrupted in GNSS-denied\n"
        "missions.\n\n"
        "Using every bearing is not\n"
        "always helpful when some are\n"
        "not trustworthy.",
        "#fef2f2",
    )
    _box(
        ax,
        (0.375, 0.18),
        0.25,
        0.58,
        "Framework",
        "1. Multi-candidate geometric\n   initialization\n"
        "2. Trimming-aware robust\n   refinement\n"
        "3. Optional bias correction\n"
        "4. Residual-aware subset\n   selection\n\n"
        "Goal: stable estimates with\n"
        "explicit geometric logic",
        "#ecfdf5",
    )
    _box(
        ax,
        (0.71, 0.18),
        0.25,
        0.58,
        "Observed outcomes",
        "Outlier median:\n"
        "1.6290 -> 0.3863\n\n"
        "Mixed median:\n"
        "1.4863 -> 0.6779\n\n"
        "Selection median:\n"
        "0.7491 -> 0.4977 vs random\n\n"
        "Selection beats FIM-only:\n"
        "0.5200 -> 0.4977",
        "#eff6ff",
    )

    for start, end in [((0.30, 0.47), (0.37, 0.47)), ((0.635, 0.47), (0.705, 0.47))]:
        arrow = FancyArrowPatch(start, end, arrowstyle="simple", mutation_scale=20, color="#475569")
        ax.add_patch(arrow)

    ax.text(
        0.5,
        0.08,
        "Story: robust passive localization is most valuable when bearing credibility is uneven",
        ha="center",
        va="center",
        fontsize=12,
        color="#334155",
    )

    png_path = OUT / "graphical_abstract.png"
    pdf_path = OUT / "graphical_abstract.pdf"
    fig.tight_layout()
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    build_graphical_abstract()
