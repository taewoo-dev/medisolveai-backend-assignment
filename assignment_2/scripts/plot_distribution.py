"""n=100에서 `get_random`의 분포를 시각화하는 스크립트."""

from __future__ import annotations

import collections
import pathlib
import sys

import matplotlib
import matplotlib.pyplot as plt

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from random_generator import get_random


def parse_args() -> tuple[int, int]:
    import argparse

    parser = argparse.ArgumentParser(description="Plot distribution of get_random(n).")
    parser.add_argument("--samples", type=int, default=200_000, help="샘플 개수")
    parser.add_argument("--n", type=int, default=100, help="get_random의 최대 값")

    args = parser.parse_args()
    return args.samples, args.n

matplotlib.use("Agg")


def main(sample_size: int = 200_000, n: int = 100) -> None:
    counts = collections.Counter(get_random(n) for _ in range(sample_size))
    values = list(range(n + 1))
    frequencies = [counts[v] for v in values]

    artifacts_dir = pathlib.Path(__file__).resolve().parent.parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    output_path = artifacts_dir / f"distribution_n{n}_samples{sample_size}.png"

    plt.figure(figsize=(16, 6))
    plt.bar(values, frequencies, color="#1f77b4", width=0.8)
    plt.title(f"Distribution of get_random({n}) over {sample_size:,} samples")
    plt.xlabel("Result value")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    samples, upper_bound = parse_args()
    main(sample_size=samples, n=upper_bound)

