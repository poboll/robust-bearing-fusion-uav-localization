"""Run replay-style validation from JSON, JSONL, or CSV measurement logs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from passive_localization.config import MethodConfig
from passive_localization.replay import evaluate_replay_case, load_replay_cases, summarize_replay_results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Replay file (.json, .jsonl, or .csv)")
    parser.add_argument("--output", default="experiments/replay_validation_result.json", help="Output JSON path")
    args = parser.parse_args()

    cases = load_replay_cases(args.input)
    method_config = MethodConfig()
    rows = [evaluate_replay_case(case, method_config) for case in cases]
    payload = {
        "meta": {
            "input": str(Path(args.input)),
            "num_cases": len(rows),
        },
        "cases": rows,
        "summary": summarize_replay_results(rows),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
