from __future__ import annotations
import argparse, time, os, csv, itertools, random
from typing import List, Tuple, Dict, Callable
from tqdm import tqdm
from sim.grid import Grid
from sim.routing import astar, dijkstra
from sim.collision_tracker import simulate_multi_bot_execution, convert_tour_to_paths
from exp.scenarios import make_map, sample_depot_and_picks
from algos.tsp_exact import held_karp
from algos.tsp_nn_2opt import nn_2opt
from algos.tsp_ga import ga_tsp
from algos.hybrids import hybrid_nn_2opt, hybrid_ga_2opt
from algos.tsp_aco import aco_tsp
from algos.tsp_alo import alo_tsp
from algos.tsp_astar import astar_tsp

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
    if name == "AStar":
        return astar_tsp(dist_fn, n, start)
    if name == "ACO":
        return aco_tsp(dist_fn, n, start, seed=seed, ants=20, iterations=50)
    if name == "ALO":
        return alo_tsp(dist_fn, n, start, seed=seed, ants=30, iterations=50)
    raise ValueError(f"Unknown algo {name}")

def assign_packages_to_bots(grid: Grid, depot: Tuple[int, int], packages: List[Tuple[int, int]], 
                            num_bots: int, seed: int) -> Dict[int, List[int]]:
    """
    Assign packages to multiple bots from the same depot based on proximity
    Returns: dict mapping bot_index -> list of package_indices
    """
    rng = random.Random(seed)
    assignments: Dict[int, List[int]] = {i: [] for i in range(num_bots)}
    
    if num_bots == 1:
        # Single bot: assign all packages
        assignments[0] = list(range(len(packages)))
        return assignments
    
    # For multiple bots, assign packages to nearest bot (using depot as reference)
    # We'll use a simple round-robin with distance-based optimization
    for pkg_idx, pkg_pos in enumerate(packages):
        # Find nearest bot (all bots start from same depot, so we use package-to-depot distance)
        # For simplicity, we'll use round-robin, but could optimize based on current bot load
        bot_idx = pkg_idx % num_bots
        assignments[bot_idx].append(pkg_idx)
    
    # Balance assignments: ensure each bot has roughly equal packages
    total_packages = len(packages)
    target_per_bot = total_packages // num_bots
    extra = total_packages % num_bots
    
    # Rebalance if needed
    for bot_idx in range(num_bots):
        if len(assignments[bot_idx]) == 0:
            # Empty bot: take from bot with most packages
            max_bot = max(range(num_bots), key=lambda i: len(assignments[i]))
            if len(assignments[max_bot]) > 1:
                pkg = assignments[max_bot].pop()
                assignments[bot_idx].append(pkg)
    
    return assignments


def run_once(map_type: str, K: int, seed: int, algo_name: str, num_bots: int, out_writer):
    g = make_map(map_type, w=20, h=20, seed=seed)
    depot, picks = sample_depot_and_picks(g, K, seed=seed)
    
    # If single bot, use original logic
    if num_bots == 1:
        waypoints = [depot] + picks  # index 0 is depot
        dist = pairwise_distance_builder(g, waypoints)

        t0 = time.perf_counter()
        order, L = plan_sequence(algo_name, dist, len(waypoints), start=0, seed=seed)
        plan_ms = (time.perf_counter() - t0) * 1000

        # Calculate additional metrics for hybrid algorithms
        initial_quality = None
        improvement_pct = None
        is_hybrid = 1 if algo_name == "HybridNN2opt" else 0
        
        # For hybrid and NN2opt, calculate improvement metrics
        if algo_name in ["HybridNN2opt", "NN2opt"]:
            # Get initial NN solution quality (before 2-opt)
            from algos.tsp_nn_2opt import nearest_neighbor, tour_length
            nn_tour = nearest_neighbor(dist, len(waypoints), start=0)
            initial_quality = tour_length(nn_tour, dist)
            if initial_quality > 0:
                improvement_pct = ((initial_quality - L) / initial_quality) * 100.0

        # Collision metrics (always 0 for single bot)
        collision_count = 0
        total_wait_time = 0.0
        max_wait_time = 0.0
        avg_wait_time = 0.0
        collision_makespan = L
        theoretical_makespan = L
        
        out_writer.writerow({
            "map_type": map_type, "K": K, "seed": seed, "algo": algo_name,
            "num_bots": num_bots, "is_hybrid": is_hybrid, 
            "tour_len": round(L,3), "plan_time_ms": round(plan_ms,2),
            "initial_quality": round(initial_quality, 3) if initial_quality else "",
            "improvement_pct": round(improvement_pct, 2) if improvement_pct else "",
            "theoretical_makespan": round(theoretical_makespan, 3),
            "collision_makespan": round(collision_makespan, 3),
            "collision_count": collision_count,
            "total_wait_time": round(total_wait_time, 3),
            "max_wait_time": round(max_wait_time, 3),
            "avg_wait_time": round(avg_wait_time, 3),
            "exec_time_s": "", "waits_s": "", "replan_count": "", "success": 1
        })
    else:
        # Multiple bots from same depot
        assignments = assign_packages_to_bots(g, depot, picks, num_bots, seed)
        
        bot_times = []
        bot_distances = []
        bot_tour_lens = []
        bot_plan_times = []
        packages_per_bot = []
        bot_tours = []  # Store tours for collision simulation
        
        total_plan_time = 0.0
        
        # Plan sequence for each bot
        for bot_idx in range(num_bots):
            assigned_packages = assignments[bot_idx]
            
            if len(assigned_packages) == 0:
                # No packages assigned, bot stays at depot
                bot_times.append(0.0)
                bot_distances.append(0.0)
                bot_tour_lens.append(0.0)
                bot_plan_times.append(0.0)
                packages_per_bot.append(0)
                bot_tours.append([])  # Empty tour
                continue
            
            # Get package positions
            pkg_positions = [picks[i] for i in assigned_packages]
            waypoints = [depot] + pkg_positions
            dist = pairwise_distance_builder(g, waypoints)
            
            # Plan sequence for this bot
            t0 = time.perf_counter()
            order, tour_len = plan_sequence(algo_name, dist, len(waypoints), start=0, seed=seed + bot_idx)
            plan_time = (time.perf_counter() - t0) * 1000
            
            # Convert tour to paths for collision simulation
            tour_paths = convert_tour_to_paths(g, order, waypoints)
            
            bot_tour_lens.append(tour_len)
            bot_plan_times.append(plan_time)
            bot_distances.append(tour_len)
            bot_times.append(tour_len)
            packages_per_bot.append(len(assigned_packages))
            bot_tours.append(tour_paths)
            total_plan_time += plan_time
        
        # Calculate theoretical makespan (parallel execution = max time)
        theoretical_makespan = max(bot_times) if bot_times else 0.0
        # Planning time for parallel = max (bots plan simultaneously)
        plan_ms = max(bot_plan_times) if bot_plan_times else 0.0
        
        # Run collision simulation for parallel execution
        collision_makespan = theoretical_makespan
        collision_count = 0
        total_wait_time = 0.0
        max_wait_time = 0.0
        avg_wait_time = 0.0
        
        try:
            collision_makespan, collision_stats = simulate_multi_bot_execution(
                g, bot_tours, step_time=0.2
            )
            collision_count = collision_stats.total_collisions
            total_wait_time = collision_stats.total_wait_time
            max_wait_time = collision_stats.max_wait_time
            avg_wait_time = (total_wait_time / collision_count) if collision_count > 0 else 0.0
        except Exception as e:
            print(f"⚠️  Collision simulation failed: {e}, using theoretical makespan")
            collision_makespan = theoretical_makespan
        
        # Calculate total tour length (sum of all bot tours)
        total_tour_len = sum(bot_tour_lens)
        
        # Calculate improvement metrics (for first bot as representative)
        initial_quality = None
        improvement_pct = None
        is_hybrid = 1 if algo_name == "HybridNN2opt" else 0
        
        if bot_tour_lens and algo_name in ["HybridNN2opt", "NN2opt"]:
            # Calculate improvement for first bot as representative
            first_bot_packages = assignments[0]
            if first_bot_packages:
                first_pkg_positions = [picks[i] for i in first_bot_packages]
                first_waypoints = [depot] + first_pkg_positions
                first_dist = pairwise_distance_builder(g, first_waypoints)
                from algos.tsp_nn_2opt import nearest_neighbor, tour_length
                nn_tour = nearest_neighbor(first_dist, len(first_waypoints), start=0)
                initial_quality = tour_length(nn_tour, first_dist)
                if initial_quality > 0 and bot_tour_lens[0] > 0:
                    improvement_pct = ((initial_quality - bot_tour_lens[0]) / initial_quality) * 100.0
        
        out_writer.writerow({
            "map_type": map_type, "K": K, "seed": seed, "algo": algo_name,
            "num_bots": num_bots, "is_hybrid": is_hybrid,
            "tour_len": round(total_tour_len, 3), "plan_time_ms": round(plan_ms, 2),
            "initial_quality": round(initial_quality, 3) if initial_quality else "",
            "improvement_pct": round(improvement_pct, 2) if improvement_pct else "",
            "theoretical_makespan": round(theoretical_makespan, 3),
            "collision_makespan": round(collision_makespan, 3),
            "collision_count": collision_count,
            "total_wait_time": round(total_wait_time, 3),
            "max_wait_time": round(max_wait_time, 3),
            "avg_wait_time": round(avg_wait_time, 3),
            "exec_time_s": "", "waits_s": "", "replan_count": "", "success": 1
        })

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map-types", nargs="+", default=["narrow","wide","cross"])
    ap.add_argument("--K", nargs="+", type=int, default=[5,10])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--algos", default="HybridNN2opt,NN2opt,HeldKarp,GA")
    ap.add_argument("--num-bots", default="1", help="Comma-separated bot counts for single-depot (e.g. 1,2,3). Default: 1.")
    ap.add_argument("--out", default="results/raw")
    args = ap.parse_args()

    num_bots_list = [int(x.strip()) for x in args.num_bots.split(",") if x.strip()]
    if not num_bots_list:
        num_bots_list = [1]

    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "runs.csv")
    with open(out_path, "w", newline="") as f:
        fieldnames = ["map_type","K","seed","algo","num_bots","is_hybrid","tour_len","plan_time_ms",
                      "initial_quality","improvement_pct",
                      "theoretical_makespan","collision_makespan",
                      "collision_count","total_wait_time","max_wait_time","avg_wait_time",
                      "exec_time_s","waits_s","replan_count","success"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for map_type in args.map_types:
            for K in args.K:
                for seed in range(args.seeds):
                    for algo in args.algos.split(","):
                        for num_bots in num_bots_list:
                            run_once(map_type, K, seed, algo, num_bots, w)
    print(f"Wrote {out_path}")
    
    # Generate formatted output
    try:
        from format_results import format_results
        formatted_path = os.path.join(os.path.dirname(args.out), "formatted_results.txt")
        format_results(out_path, output_file=formatted_path)
    except ImportError:
        pass  # Optional feature

if __name__ == "__main__":
    main()