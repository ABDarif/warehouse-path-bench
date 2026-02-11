"""
Generate two side-by-side bar charts: "Narrow Maps: Collision Count" and "Wide Maps: Collision Count".
Three algorithms: GA, HybridNN2opt, NN2opt. Data from codebase (multi-bot runs only).
HybridNN2opt shows lower/zero collisions; GA and NN2opt similar and higher.
"""

from __future__ import annotations
import argparse
import os
import csv
from typing import Dict, List
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

ALGOS = ["GA", "HybridNN2opt", "NN2opt"]

# Per-algo colors; HybridNN2opt highlighted (green)
COLORS = {"GA": "#e74c3c", "HybridNN2opt": "#27ae60", "NN2opt": "#3498db"}


def safe_int(v, default=0):
    if v is None or v == "":
        return default
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return default


def load_data(csv_file: str, multi_bot_only: bool = True) -> List[Dict]:
    if not os.path.exists(csv_file):
        return []
    rows = []
    with open(csv_file, "r", newline="") as f:
        for row in csv.DictReader(f):
            if multi_bot_only:
                nb = safe_int(row.get("num_bots"), 1)
                if nb <= 1:
                    continue
            rows.append(row)
    return rows


def compute_collision_by_map(data: List[Dict]) -> tuple[Dict[str, float], Dict[str, float]]:
    """Returns (narrow_avg, wide_avg) per algo from codebase. Only multi-bot rows have non-zero collisions."""
    narrow = defaultdict(list)
    wide = defaultdict(list)
    for row in data:
        algo = row.get("algo", "").strip()
        if algo not in ALGOS:
            continue
        m = (row.get("map_type") or "").strip().lower()
        c = safe_int(row.get("collision_count"), 0)
        if m == "narrow":
            narrow[algo].append(c)
        elif m == "wide":
            wide[algo].append(c)
    narrow_avg = {a: float(np.mean(narrow[a])) if narrow[a] else 0.0 for a in ALGOS}
    wide_avg = {a: float(np.mean(wide[a])) if wide[a] else 0.0 for a in ALGOS}
    return narrow_avg, wide_avg


def plot_collision_narrow_wide(
    csv_file: str = "results/raw/runs.csv",
    outdir: str = "figs",
    out_name: str = "collision_narrow_wide.png",
) -> None:
    data = load_data(csv_file)
    narrow_avg, wide_avg = compute_collision_by_map(data)

    narrow_vals = [narrow_avg[a] for a in ALGOS]
    wide_vals = [wide_avg[a] for a in ALGOS]

    y_max = max(max(narrow_vals), max(wide_vals), 1.0) * 1.2
    y_max = max(y_max, 2.0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    x_pos = np.arange(len(ALGOS))
    width = 0.6

    for i, algo in enumerate(ALGOS):
        color = COLORS.get(algo, "#95a5a6")
        ax1.bar(x_pos[i], narrow_vals[i], width=width, color=color, alpha=0.9, edgecolor="black" if algo == "HybridNN2opt" else "none", linewidth=2 if algo == "HybridNN2opt" else 0)
        ax2.bar(x_pos[i], wide_vals[i], width=width, color=color, alpha=0.9, edgecolor="black" if algo == "HybridNN2opt" else "none", linewidth=2 if algo == "HybridNN2opt" else 0)
        if narrow_vals[i] == 0:
            ax1.text(x_pos[i], 0.05, "0", ha="center", va="bottom", fontsize=10, fontweight="bold")
        if wide_vals[i] == 0:
            ax2.text(x_pos[i], 0.05, "0", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(ALGOS, rotation=0)
    ax1.set_ylabel("Avg Collision Count", fontsize=11, fontweight="bold")
    ax1.set_title("Narrow Maps: Collision Count", fontsize=12, fontweight="bold")
    ax1.set_ylim(0, y_max)
    ax1.grid(axis="y", alpha=0.3, linestyle="--")

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(ALGOS, rotation=0)
    ax2.set_ylabel("Avg Collision Count", fontsize=11, fontweight="bold")
    ax2.set_title("Wide Maps: Collision Count", fontsize=12, fontweight="bold")
    ax2.set_ylim(0, y_max)
    ax2.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, out_name)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Generate Narrow/Wide collision count bar charts")
    ap.add_argument("--csv", default="results/raw/runs.csv", help="Runs CSV (with collision_count, map_type)")
    ap.add_argument("--outdir", default="figs", help="Output directory")
    ap.add_argument("--out", default="collision_narrow_wide.png", help="Output filename")
    args = ap.parse_args()
    plot_collision_narrow_wide(csv_file=args.csv, outdir=args.outdir, out_name=args.out)


if __name__ == "__main__":
    main()
