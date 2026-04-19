"""Summarize experiment outputs into compact JSON and markdown-ready snippets."""

from __future__ import annotations

import json
from pathlib import Path


def summarize_ablation(source: str | Path = "experiments/ablation_result.json", output: str | Path = "experiments/ablation_summary.json") -> dict:
    source = Path(source)
    payload = json.loads(source.read_text(encoding="utf-8"))
    summary: dict[str, dict] = {}

    for regime_name, regime_data in payload.items():
        regime_summary: dict[str, dict] = {}
        for cfg_name, cfg_payload in regime_data.items():
            bt = cfg_payload["summary"]["robust_bias_trimmed_error"]
            ls = cfg_payload["summary"]["least_squares_error"]
            regime_summary[cfg_name] = {
                "robust_bt_median": bt["median"],
                "robust_bt_p90": bt["p90"],
                "robust_bt_success_at_1_0": bt["success_at_1_0"],
                "robust_bt_catastrophic_at_5_0": bt["catastrophic_at_5_0"],
                "ls_median": ls["median"],
                "paired_robust_bt_vs_ls": cfg_payload["paired"]["robust_bt_vs_ls"],
                "paired_robust_bt_vs_pso": cfg_payload["paired"]["robust_bt_vs_pso"],
                "paired_robust_bt_vs_sa": cfg_payload["paired"]["robust_bt_vs_sa"],
            }
        summary[regime_name] = regime_summary

    output = Path(output)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = summarize_ablation()
    print(json.dumps(result, ensure_ascii=False, indent=2))
