"""Entry point for quick local experiments.

Recommended usage:
`/opt/homebrew/Caskroom/miniconda/base/bin/python3 run_demo.py`
or any Python environment with `numpy` installed.
"""

from passive_localization.simulate import run_demo


if __name__ == "__main__":
    result = run_demo(output_dir="experiments")
    print("Demo finished.")
    print(result)
