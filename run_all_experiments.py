"""Run the full paper experiment pipeline sequentially and sync submission assets."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from plot_results import main as plot_main
from run_ablation import run_ablation
from run_formations import run_formations
from run_regimes import compare_regimes
from run_runtime import run_runtime
from run_scaling import run_scaling
from run_sensitivity import run_sensitivity
from run_significance import run_significance
from run_observability import run_observability
from run_active_selection import run_active_selection
from run_selection_benefit_map import run_selection_benefit_map
from run_story_benchmark import run_story_benchmark
from run_public_dataset3_replay_validation import run_public_dataset3_replay_validation
from run_deadline_replay_validation import run_deadline_replay_validation
from run_pybullet_replay_validation import run_pybullet_replay_validation
from summarize_results import summarize_ablation


ROOT = Path(__file__).resolve().parent
EXP = ROOT / "experiments"
SUBMISSION = ROOT / "submission"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _sync_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def run_all() -> dict:
    EXP.mkdir(parents=True, exist_ok=True)

    regime_payload = compare_regimes()
    _write_json(EXP / "regime_comparison.json", regime_payload)

    ablation_payload = run_ablation(output_dir=EXP)
    ablation_summary = summarize_ablation(EXP / "ablation_result.json", EXP / "ablation_summary.json")
    formation_payload = run_formations(output_dir=EXP)
    sensitivity_payload = run_sensitivity(output_dir=EXP)
    scaling_payload = run_scaling(output_dir=EXP)
    observability_payload = run_observability(output_dir=EXP)
    active_selection_payload = run_active_selection(output_dir=EXP)
    story_payload = run_story_benchmark(output_dir=EXP)
    selection_map_payload = run_selection_benefit_map(output_dir=EXP)
    public_replay_payload = run_public_dataset3_replay_validation(output_dir=EXP)
    deadline_replay_payload = run_deadline_replay_validation(output_dir=EXP)
    pybullet_payload = run_pybullet_replay_validation(output_dir=EXP)
    significance_payload = run_significance(EXP / "ablation_result.json", EXP)
    runtime_payload = run_runtime(output_dir=EXP, repeats=100, warmup=10)

    plot_main()

    figure_names = [
        "figure_regime_comparison.png",
        "figure_ablation_mixed.png",
        "figure_formation_generalization.png",
        "figure_runtime_comparison.png",
        "figure_sensitivity_sweep.png",
        "figure_scaling.png",
        "figure_observability.png",
        "figure_active_selection.png",
        "figure_story_regimes.png",
        "figure_selection_benefit_map.png",
        "figure_public_real_replay.png",
        "figure_deadline_replay.png",
        "figure_pybullet_replay.png",
    ]
    for figure_name in figure_names:
        src = EXP / figure_name
        if src.exists():
            _sync_file(src, SUBMISSION / "figures" / figure_name)

    frozen_dir = SUBMISSION / "supplementary" / "frozen_results"
    for json_name in [
        "regime_comparison.json",
        "ablation_result.json",
        "ablation_summary.json",
        "formation_result.json",
        "sensitivity_result.json",
        "scaling_result.json",
        "observability_result.json",
        "active_selection_result.json",
        "story_revision_analysis.json",
        "story_benchmark_result.json",
        "selection_benefit_map.json",
        "ransac_incremental_ablation.json",
        "public_dataset3_replay_result.json",
        "public_dataset3_replay_cases.json",
        "deadline_replay_result.json",
        "deadline_replay_cases.json",
        "pybullet_replay_result.json",
        "pybullet_replay_traces.json",
        "significance_result.json",
        "runtime_result.json",
    ]:
        src = EXP / json_name
        if src.exists():
            _sync_file(src, frozen_dir / json_name)

    frozen_artifacts = {
        path.stem: f"submission/supplementary/frozen_results/{path.name}"
        for path in sorted(frozen_dir.glob("*.json"))
        if path.name != "manifest.json"
    }
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "zenodo_doi": "10.5281/zenodo.19657582",
        "zenodo_record_type": "software",
        "archived_release": "v0.3.0",
        "live_repository": "https://github.com/poboll/robust-bearing-fusion-uav-localization",
        "notes": [
            "The Zenodo DOI is a GitHub-generated software/reproducibility archive, not a dataset-only deposit.",
            "The files listed here are the curated frozen JSON result-data subset used to regenerate manuscript tables and figures.",
        ],
        "runtime_repeats": 100,
        "runtime_warmup": 10,
        "artifacts": frozen_artifacts,
    }
    _write_json(frozen_dir / "manifest.json", manifest)

    return {
        "regime_comparison": regime_payload,
        "ablation_summary": ablation_summary,
        "formation_result": formation_payload,
        "sensitivity_result": sensitivity_payload,
        "scaling_result": scaling_payload,
        "observability_result": observability_payload,
        "active_selection_result": active_selection_payload,
        "story_benchmark_result": story_payload,
        "selection_benefit_map": selection_map_payload,
        "public_dataset3_replay_result": public_replay_payload,
        "deadline_replay_result": deadline_replay_payload,
        "pybullet_replay_result": pybullet_payload,
        "significance_result": significance_payload,
        "runtime_result": runtime_payload,
        "manifest": manifest,
    }


if __name__ == "__main__":
    print(json.dumps(run_all(), ensure_ascii=False, indent=2))
