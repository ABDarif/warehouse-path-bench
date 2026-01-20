from __future__ import annotations
import argparse, time, os, csv, itertools, random
from typing import List, Tuple, Dict, Callable
from tqdm import tqdm
from sim.grid import Grid
from sim.routing import astar, dijkstra
from exp.scenarios import make_map, sample_depot_and_picks
from algos.tsp_exact import held_karp
from algos.tsp_nn_2opt import nn_2opt
from algos.tsp_ga import ga_tsp
from algos.hybrids import hybrid_nn_2opt, hybrid_ga_2opt

AlgoFn = Callable[[Callable[[int,int], float], int, int], Tuple[List[int], float]]

def pairwise_distance_builder(grid: Grid, waypoints: List[Tuple[int,int]]):
    # cache routes between waypoint indices using A*
    cache = {}
    def dist(i: int, j: int) -> float:
        if i == j: return 0.0
        key = (min(i,j), max(i,j))
        if key in cache: return cache[key]
        # FIX: A* now returns 3 values, but we only need path and length
        path, L, _ = astar(grid, waypoints[i], waypoints[j])
        cache[key] = L
        return L
    return dist

def plan_sequence(name: str, dist_fn, n, start, seed=0):
    if name == "NN2opt":
        return nn_2opt(dist_fn, n, start)
    if name == "HeldKarp":
        # FIX: held_karp now returns 3 values, but we only need order and length
        order, L, _ = held_karp(dist_fn, n, start)
        return order, L
    if name == "GA":
        return ga_tsp(dist_fn, n, start, seed=seed, pop=48, gens=150)
    if name == "HybridNN2opt":
        return hybrid_nn_2opt(dist_fn, n, start)
    raise ValueError(f"Unknown algo {name}")

def run_once(map_type: str, K: int, seed: int, algo_name: str, out_writer):
    g = make_map(map_type, w=20, h=20, seed=seed)
    depot, picks = sample_depot_and_picks(g, K, seed=seed)
    waypoints = [depot] + picks  # index 0 is depot
    dist = pairwise_distance_builder(g, waypoints)

    t0 = time.perf_counter()
    order, L = plan_sequence(algo_name, dist, len(waypoints), start=0, seed=seed)
    plan_ms = (time.perf_counter() - t0) * 1000

    # Calculate additional metrics for hybrid algorithms
    initial_quality = None
    improvement_pct = None
    is_hybrid = 1 if algo_name == "HybridNN2opt" else 0
    
    # For hybrid, calculate improvement metrics
    if algo_name == "HybridNN2opt":
        # Get initial NN solution quality (before 2-opt)
        from algos.tsp_nn_2opt import nearest_neighbor, tour_length
        nn_tour = nearest_neighbor(dist, len(waypoints), start=0)
        initial_quality = tour_length(nn_tour, dist)
        if initial_quality > 0:
            improvement_pct = ((initial_quality - L) / initial_quality) * 100.0
    elif algo_name == "NN2opt":
        # For comparison, also get initial NN quality
        from algos.tsp_nn_2opt import nearest_neighbor, tour_length
        nn_tour = nearest_neighbor(dist, len(waypoints), start=0)
        initial_quality = tour_length(nn_tour, dist)
        if initial_quality > 0:
            improvement_pct = ((initial_quality - L) / initial_quality) * 100.0

    # convert sequence into leg endpoints (cells)
    # here we just sum distances; SimPy exec is separate
    out_writer.writerow({
        "map_type": map_type, "K": K, "seed": seed, "algo": algo_name,
        "is_hybrid": is_hybrid, "tour_len": round(L,3), "plan_time_ms": round(plan_ms,2),
        "initial_quality": round(initial_quality, 3) if initial_quality else "",
        "improvement_pct": round(improvement_pct, 2) if improvement_pct else "",
        "exec_time_s": "", "waits_s": "", "replan_count": "", "success": 1
    })

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map-types", nargs="+", default=["narrow","wide","cross"])
    ap.add_argument("--K", nargs="+", type=int, default=[5,10])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--algos", default="HeldKarp,NN2opt,GA")
    ap.add_argument("--out", default="results/raw")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "runs.csv")
    with open(out_path, "w", newline="") as f:
        fieldnames = ["map_type","K","seed","algo","is_hybrid","tour_len","plan_time_ms",
                      "initial_quality","improvement_pct",
                      "exec_time_s","waits_s","replan_count","success"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for map_type in args.map_types:
            for K in args.K:
                for seed in range(args.seeds):
                    for algo in args.algos.split(","):
                        run_once(map_type, K, seed, algo, w)
    print(f"Wrote {out_path}")
    
    # Generate formatted output
    try:
        from generate_formatted_results import generate_formatted_output
        formatted_path = os.path.join(os.path.dirname(args.out), "formatted_results.txt")
        generate_formatted_output(out_path, formatted_path)
    except ImportError:
        pass  # Optional feature

if __name__ == "__main__":
    main()