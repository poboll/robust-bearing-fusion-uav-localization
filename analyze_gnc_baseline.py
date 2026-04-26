"""Summarize Proposed vs GNC-GM from replay or benchmark result files."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
EXP = ROOT / "experiments"


def _paired(left: np.ndarray, right: np.ndarray) -> dict:
    improvement = right - left
    return {
        "wins": int(np.sum(improvement > 0.0)),
        "losses": int(np.sum(improvement < 0.0)),
        "ties": int(np.sum(np.isclose(improvement, 0.0))),
        "median_improvement": float(np.median(improvement)),
        "mean_improvement": float(np.mean(improvement)),
    }


def summarize_pybullet(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    # rerun file only has summaries, so use traces for row-level if available
    traces_path = EXP / "pybullet_replay_traces.json"
    traces = json.loads(traces_path.read_text(encoding="utf-8")) if traces_path.exists() else {}
    return {
        "summary_only": payload.get("summary", {}),
        "trace_examples": list((traces.get("examples") or {}).keys()),
    }


def main() -> None:
    result = {}
    pybullet_path = EXP / "pybullet_replay_result.json"
    if pybullet_path.exists():
        result["pybullet"] = summarize_pybullet(pybullet_path)
    out = EXP / "gnc_baseline_analysis.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
