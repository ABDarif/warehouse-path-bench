"""
Generate algorithm characteristics table from codebase (runs.csv).
Table: Algorithm | Tour Quality/Optimization | Planning Time | Memory Usage | Congestion Handling | Overall Use Case.
Values (tour length, opt rate, mean plan time, memory) are filled from data; labels and text from narrative.
"""

import csv
import os
import sys

# Reuse aggregation from metrics table
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_metrics_table import load_runs, build_metrics, ALGOS, ALGO_DISPLAY

# Narrative text (congestion handling and use cases)
CONGESTION = {
    "HeldKarp": "Basic",
    "NN2opt": "Basic",
    "HybridNN2opt": "Good (congestion-aware weights)",
    "GA": "Moderate",
    "ALO": "Moderate",
    "ACO": "Moderate",
}

USE_CASE = {
    "HeldKarp": "Use when a near-optimal tour is critical and computation time is not an issue.",
    "NN2opt": "Real-time routing in large warehouses, prioritizing speed over minimal distance.",
    "HybridNN2opt": "Dynamic environments with congestion, balancing speed and route quality.",
    "GA": "Adaptive routing with complex constraints; hybrid with A* legs reduces waiting time.",
    "ALO": "Suitable for multi-objective, dynamic scenarios; less efficient for standard warehouse metrics.",
    "ACO": "Adaptive and stochastic path-finding; slower and less optimal than NN2opt or GA.",
}


def assign_tour_quality(tour_len_by_algo):
    """Assign qualitative tour label from mean tour length (lower = better)."""
    order = sorted(tour_len_by_algo.keys(), key=lambda a: tour_len_by_algo[a])
    best_len = tour_len_by_algo[order[0]]
    labels = {}
    for i, algo in enumerate(order):
        t = tour_len_by_algo[algo]
        if i == 0:
            labels[algo] = "Best"
        elif t <= best_len * 1.05:
            labels[algo] = "Slightly worse"
        elif i <= 3:
            labels[algo] = "High"
        else:
            labels[algo] = "Poor"
    return labels


def assign_planning_speed(mean_plan_by_algo):
    """Assign qualitative planning time label (lower ms = faster)."""
    order = sorted(mean_plan_by_algo.keys(), key=lambda a: mean_plan_by_algo[a])
    labels = {}
    for i, algo in enumerate(order):
        t = mean_plan_by_algo[algo]
        if i == 0:
            labels[algo] = "Fastest"
        elif i == 1:
            labels[algo] = "Very fast"
        elif i == len(order) - 1:
            labels[algo] = "Slowest"
        elif t < 50:
            labels[algo] = "Fast"
        else:
            labels[algo] = "Slow"
    return labels


def assign_memory_label(mem_by_algo):
    """Assign qualitative memory label (higher MB = higher). Only one algo is 'Lowest'."""
    min_mem = min(mem_by_algo.values()) if mem_by_algo else 0
    labels = {}
    for algo in mem_by_algo:
        m = mem_by_algo[algo]
        if m >= 0.5:
            labels[algo] = "High"
        elif m == min_mem:
            labels[algo] = "Lowest"
        elif m <= 0.10:
            labels[algo] = "Very low"
        else:
            labels[algo] = "Low"
    return labels


def build_characteristics(metrics):
    tour_by_algo = {ALGOS[i]: metrics[i]["Tour Length (m)"] for i in range(len(ALGOS))}
    plan_by_algo = {ALGOS[i]: metrics[i]["Mean Planning Time (ms)"] for i in range(len(ALGOS))}
    mem_by_algo = {ALGOS[i]: metrics[i]["Memory Usage (MB)"] for i in range(len(ALGOS))}

    tour_label = assign_tour_quality(tour_by_algo)
    plan_label = assign_planning_speed(plan_by_algo)
    mem_label = assign_memory_label(mem_by_algo)

    rows = []
    for i, algo in enumerate(ALGOS):
        opt = metrics[i]["Optimization Rate"]
        tour_len = metrics[i]["Tour Length (m)"]
        mean_plan = metrics[i]["Mean Planning Time (ms)"]
        mem = metrics[i]["Memory Usage (MB)"]
        rows.append({
            "Algorithm": ALGO_DISPLAY[i],
            "Tour Quality": tour_label[algo],
            "Tour Length": tour_len,
            "Opt Rate": opt,
            "Planning Label": plan_label[algo],
            "Mean Planning (ms)": mean_plan,
            "Memory Label": mem_label[algo],
            "Memory (MB)": mem,
            "Congestion Handling": CONGESTION.get(algo, "Moderate"),
            "Overall Use Case": USE_CASE.get(algo, ""),
        })
    return rows


def write_characteristics_table(rows, out_path: str = "results/characteristics_table.txt"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    col_w = 20
    with open(out_path, "w") as f:
        f.write("Algorithm characteristics and performance (values from codebase runs.csv).\n\n")
        f.write("| Algorithm        | Tour Quality / Optimization     | Planning Time        | Memory Usage   | Congestion Handling              | Overall Use Case\n")
        f.write("|------------------|----------------------------------|----------------------|----------------|----------------------------------|------------------\n")
        for r in rows:
            tour_str = f"{r['Tour Quality']} (length {r['Tour Length']}, opt. {r['Opt Rate']})"
            plan_str = f"{r['Planning Label']} (mean {r['Mean Planning (ms)']} ms)"
            mem_str = f"{r['Memory Label']} ({r['Memory (MB)']} MB)"
            f.write(f"| {r['Algorithm']:<16} | {tour_str:<32} | {plan_str:<20} | {mem_str:<14} | {r['Congestion Handling']:<32} | {r['Overall Use Case']}\n")
    print(f"Wrote: {out_path}")


def write_characteristics_csv(rows, out_path: str = "results/characteristics_table.csv"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Algorithm", "Tour Quality", "Tour Length", "Optimization Rate", "Planning Time Label", "Mean Planning (ms)", "Memory Label", "Memory (MB)", "Congestion Handling", "Overall Use Case"])
        for r in rows:
            w.writerow([
                r["Algorithm"], r["Tour Quality"], r["Tour Length"], r["Opt Rate"],
                r["Planning Label"], r["Mean Planning (ms)"], r["Memory Label"], r["Memory (MB)"],
                r["Congestion Handling"], r["Overall Use Case"],
            ])
    print(f"Wrote: {out_path}")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Generate algorithm characteristics table from runs.csv")
    ap.add_argument("--csv", default="results/raw/runs.csv", help="Input runs CSV")
    ap.add_argument("--out-txt", default="results/characteristics_table.txt", help="Output text table")
    ap.add_argument("--out-csv", default="results/characteristics_table.csv", help="Output CSV")
    args = ap.parse_args()
    data = load_runs(args.csv)
    if not data:
        print("No data in", args.csv)
        return
    metrics = build_metrics(data)
    rows = build_characteristics(metrics)
    write_characteristics_table(rows, args.out_txt)
    write_characteristics_csv(rows, args.out_csv)


if __name__ == "__main__":
    main()
