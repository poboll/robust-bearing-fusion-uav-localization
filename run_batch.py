"""Batch experiment runner.

Recommended usage:
`PYTHONPATH=src /opt/homebrew/Caskroom/miniconda/base/bin/python3 run_batch.py`
"""

from passive_localization.simulate import run_batch


if __name__ == "__main__":
    result = run_batch(output_dir="experiments", seeds=list(range(20)))
    print("Batch finished.")
    print(result)
