"""Run a small regime comparison for paper-story sanity checks."""

import json
from pathlib import Path

from passive_localization.benchmarks import compare_regimes


if __name__ == "__main__":
    results = compare_regimes()
    out = Path("experiments")
    out.mkdir(parents=True, exist_ok=True)
    (out / "regime_comparison.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
