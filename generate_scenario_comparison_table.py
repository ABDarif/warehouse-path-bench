"""
Generate scenario comparison table: Single-depot (1 bot), Single-depot (multi-bot), Multi-depot.
Algorithms: NN2opt, Hybrid NN2opt, GA. No HeldKarp.
Metrics: Tour Length (cells), Planning Time, Collision Count (avg.), Makespan.
"""

import csv
import os
from collections import defaultdict

ALGOS = ["NN2opt", "HybridNN2opt", "GA"]
ALGO_DISPLAY = ["NN2opt", "Hybrid NN2opt", "Genetic Algorithm (GA)"]


def safe_float(v, default=0.0):
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _aggregate_single_depot_rows(rows_by_algo):
    """Turn per-algo lists into per-algo dict of means. Only include algos with at least one row."""
    result = {}
    for algo in ALGOS:
        d = rows_by_algo[algo]
        n = len(d["tour_len"])
        if n == 0:
            continue
        result[algo] = {
            "tour_len": sum(d["tour_len"]) / n,
            "plan_time_ms": sum(d["plan_time_ms"]) / n if d["plan_time_ms"] else 0,
            "collision_count": sum(d["collision_count"]) / n,
            "makespan": sum(d["collision_makespan"]) / n if d["collision_makespan"] else 0,
        }
    return result


def load_single_depot_1bot(csv_path: str = "results/raw/runs.csv"):
    """Single-depot, 1 robot (num_bots=1). Collision count is always 0."""
    if not os.path.exists(csv_path):
        return {}
    by_algo = defaultdict(lambda: {"tour_len": [], "plan_time_ms": [], "collision_count": [], "collision_makespan": []})
    with open(csv_path, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if safe_float(row.get("num_bots"), 1) != 1:
                continue
            algo = row.get("algo", "").strip()
            if algo not in ALGOS:
                continue
            t = row.get("tour_len", "")
            if t and str(t).lower() != "inf":
                by_algo[algo]["tour_len"].append(safe_float(t))
            by_algo[algo]["plan_time_ms"].append(safe_float(row.get("plan_time_ms")))
            by_algo[algo]["collision_count"].append(safe_float(row.get("collision_count")))
            by_algo[algo]["collision_makespan"].append(safe_float(row.get("collision_makespan")) or safe_float(row.get("theoretical_makespan")))
    return _aggregate_single_depot_rows(by_algo)


def load_single_depot_multibot(csv_path: str = "results/raw/runs.csv"):
    """Single-depot, multiple robots (num_bots>1). Can have non-zero collision count."""
    if not os.path.exists(csv_path):
        return {}
    by_algo = defaultdict(lambda: {"tour_len": [], "plan_time_ms": [], "collision_count": [], "collision_makespan": []})
    with open(csv_path, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if safe_float(row.get("num_bots"), 0) <= 1:
                continue
            algo = row.get("algo", "").strip()
            if algo not in ALGOS:
                continue
            t = row.get("tour_len", "")
            if t and str(t).lower() != "inf":
                by_algo[algo]["tour_len"].append(safe_float(t))
            by_algo[algo]["plan_time_ms"].append(safe_float(row.get("plan_time_ms")))
            by_algo[algo]["collision_count"].append(safe_float(row.get("collision_count")))
            by_algo[algo]["collision_makespan"].append(safe_float(row.get("collision_makespan")) or safe_float(row.get("theoretical_makespan")))
    return _aggregate_single_depot_rows(by_algo)


def load_multi_depot(csv_path: str = "results/raw/multi_depot_runs.csv"):
    """Aggregate multi-depot metrics from multi_depot_runs.csv (config=multi_depot)."""
    if not os.path.exists(csv_path):
        return {}
    by_algo = defaultdict(lambda: {"tour_len": [], "total_distance": [], "plan_time_ms": [], "collision_count": [], "collision_makespan": []})
    with open(csv_path, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("config", "").strip() != "multi_depot":
                continue
            algo = row.get("algo", "").strip()
            if algo not in ALGOS:
                continue
            by_algo[algo]["tour_len"].append(safe_float(row.get("tour_len")))
            by_algo[algo]["total_distance"].append(safe_float(row.get("total_distance")))
            by_algo[algo]["plan_time_ms"].append(safe_float(row.get("plan_time_ms")))
            by_algo[algo]["collision_count"].append(safe_float(row.get("collision_count")))
            by_algo[algo]["collision_makespan"].append(safe_float(row.get("collision_makespan")))
    result = {}
    for algo in ALGOS:
        d = by_algo[algo]
        n = len(d["tour_len"]) or 1
        # Tour length as total cells visited (total_distance)
        result[algo] = {
            "tour_len": sum(d["total_distance"]) / n if d["total_distance"] else (sum(d["tour_len"]) / n if d["tour_len"] else 0),
            "plan_time_ms": sum(d["plan_time_ms"]) / n if d["plan_time_ms"] else 0,
            "collision_count": sum(d["collision_count"]) / n if d["collision_count"] else 0,
            "makespan": sum(d["collision_makespan"]) / n if d["collision_makespan"] else 0,
        }
    return result


def _fmt(val, num_fmt=".3f", na="N/A"):
    if val is None:
        return na
    try:
        return format(float(val), num_fmt)
    except (TypeError, ValueError):
        return na


def write_table(single_1: dict, single_multi: dict, multi: dict, out_path: str = "results/scenario_comparison_table.txt"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        f.write("Scenario comparison: Single-depot (1 bot), Single-depot (multi-bot), Multi-depot. Algorithms: NN2opt, Hybrid NN2opt, GA.\n")
        f.write("Note: Single-depot 1 bot has collision count 0 (one robot). Single-depot multi-bot and multi-depot use multiple robots and can have collisions.\n")
        f.write("To generate single-depot multi-bot data: python3 -m exp.run_matrix --num-bots 1,2 (or 1,2,3).\n\n")
        f.write("| Algorithm              | Single-Depot (1 bot)                                  | Single-Depot (multi-bot)                               | Multi-Depot                                              |\n")
        f.write("|                        | Tour Len | Plan (ms) | Coll. | Makespan | Tour Len | Plan (ms) | Coll. | Makespan | Tour Len | Plan (ms) | Coll. | Makespan |\n")
        f.write("|------------------------|----------|-----------+-------+----------|----------|-----------+-------+----------|----------|-----------+-------+----------|\n")
        for i, algo in enumerate(ALGOS):
            name = ALGO_DISPLAY[i]
            s1 = single_1.get(algo, {})
            sm = single_multi.get(algo, {})
            md = multi.get(algo, {})
            def row_vals(d):
                if not d:
                    return ("N/A", "N/A", "N/A", "N/A")
                return (
                    _fmt(d.get("tour_len"), ".1f"),
                    _fmt(d.get("plan_time_ms"), ".2f"),
                    _fmt(d.get("collision_count"), ".2f"),
                    _fmt(d.get("makespan"), ".2f"),
                )
            r1 = row_vals(s1)
            rm = row_vals(sm)
            rd = row_vals(md)
            f.write(f"| {name:<22} | {r1[0]:>8} | {r1[1]:>9} | {r1[2]:>5} | {r1[3]:>8} | {rm[0]:>8} | {rm[1]:>9} | {rm[2]:>5} | {rm[3]:>8} | {rd[0]:>8} | {rd[1]:>9} | {rd[2]:>5} | {rd[3]:>8} |\n")
    print(f"Wrote: {out_path}")


def write_csv(single_1: dict, single_multi: dict, multi: dict, out_path: str = "results/scenario_comparison_table.csv"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Algorithm",
            "Single_1bot_Tour_cells", "Single_1bot_Plan_ms", "Single_1bot_Collision_avg", "Single_1bot_Makespan",
            "Single_multibot_Tour_cells", "Single_multibot_Plan_ms", "Single_multibot_Collision_avg", "Single_multibot_Makespan",
            "Multi_depot_Tour_cells", "Multi_depot_Plan_ms", "Multi_depot_Collision_avg", "Multi_depot_Makespan",
        ])
        for i, algo in enumerate(ALGOS):
            s1 = single_1.get(algo, {})
            sm = single_multi.get(algo, {})
            m = multi.get(algo, {})
            w.writerow([
                ALGO_DISPLAY[i],
                round(s1.get("tour_len", 0), 3), round(s1.get("plan_time_ms", 0), 2), round(s1.get("collision_count", 0), 2), round(s1.get("makespan", 0), 2),
                round(sm.get("tour_len", 0), 3) if sm else "", round(sm.get("plan_time_ms", 0), 2) if sm else "", round(sm.get("collision_count", 0), 2) if sm else "", round(sm.get("makespan", 0), 2) if sm else "",
                round(m.get("tour_len", 0), 3), round(m.get("plan_time_ms", 0), 2), round(m.get("collision_count", 0), 2), round(m.get("makespan", 0), 2),
            ])
    print(f"Wrote: {out_path}")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Generate scenario comparison table (single 1-bot, single multi-bot, multi-depot)")
    ap.add_argument("--single-csv", default="results/raw/runs.csv", help="Single-depot runs CSV (can contain num_bots=1 and num_bots>1)")
    ap.add_argument("--multi-csv", default="results/raw/multi_depot_runs.csv", help="Multi-depot runs CSV")
    ap.add_argument("--out-txt", default="results/scenario_comparison_table.txt", help="Output text table")
    ap.add_argument("--out-csv", default="results/scenario_comparison_table.csv", help="Output CSV")
    args = ap.parse_args()
    single_1 = load_single_depot_1bot(args.single_csv)
    single_multi = load_single_depot_multibot(args.single_csv)
    multi = load_multi_depot(args.multi_csv)
    if not single_1 and not single_multi and not multi:
        print("No data found.")
        return
    write_table(single_1, single_multi, multi, args.out_txt)
    write_csv(single_1, single_multi, multi, args.out_csv)


if __name__ == "__main__":
    main()
