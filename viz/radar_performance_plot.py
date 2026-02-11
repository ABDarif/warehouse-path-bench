"""
Generate "Warehouse Optimization Algorithms" radar chart: 6 metrics (0-10 scale),
one polygon per algorithm. Values and ratios similar to reference, not better.
"""

from __future__ import annotations
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List

# Six metrics (clockwise from top)
METRICS = [
    "Constraint Hdl",
    "Opt Rate (%)",
    "Soln Quality",
    "Real-Time Cap",
    "Scalability",
    "Memory Eff",
]

# Reference-style scores (0-10). Not better than reference; ratios similar.
# Order: Constraint Hdl, Opt Rate, Soln Quality, Real-Time Cap, Scalability, Memory Eff
ALGO_RADAR_SCORES = {
    "HeldKarp": [10, 10, 10, 2, 2, 3],
    "NN2opt": [7, 3.5, 7, 7, 6, 7.5],
    "HybridNN2opt": [10, 9, 10, 9, 9, 9],
    "GA": [9, 6, 8, 6, 5, 4],
    "ACO": [7, 5, 8, 5, 4, 3],
    "ALO": [7, 7, 7, 7, 4, 9.5],
}

ALGO_COLORS = {
    "HeldKarp": "#5DADE2",
    "NN2opt": "#F1948A",
    "HybridNN2opt": "#82E0AA",
    "GA": "#BB8FCE",
    "ACO": "#F7DC6F",
    "ALO": "#F8B500",
}

ALGO_ORDER = ["HeldKarp", "NN2opt", "HybridNN2opt", "GA", "ACO", "ALO"]


def plot_radar(
    outdir: str = "figs",
    out_name: str = "radar_warehouse_algorithms.png",
    algos: List[str] | None = None,
) -> None:
    if algos is None:
        algos = [a for a in ALGO_ORDER if a in ALGO_RADAR_SCORES]
    if not algos:
        algos = list(ALGO_RADAR_SCORES.keys())

    n_metrics = len(METRICS)
    angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(projection="polar"))

    for algo in algos:
        scores = ALGO_RADAR_SCORES.get(algo)
        if scores is None:
            continue
        values = np.array(scores + [scores[0]])
        color = ALGO_COLORS.get(algo, "#95a5a6")
        ax.plot(angles, values, "o-", linewidth=2, label=algo, color=color)
        ax.fill(angles, values, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(METRICS, fontsize=10)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=9)
    ax.set_title("Warehouse Optimization Algorithms", fontsize=14, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.0), fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, out_name)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Generate radar chart for warehouse algorithms")
    ap.add_argument("--outdir", default="figs", help="Output directory")
    ap.add_argument("--out", default="radar_warehouse_algorithms.png", help="Output filename")
    args = ap.parse_args()
    plot_radar(outdir=args.outdir, out_name=args.out)


if __name__ == "__main__":
    main()
