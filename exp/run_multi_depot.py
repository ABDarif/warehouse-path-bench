"""
Multi-Depot, Multi-Bot Experiment Runner
Compares single depot vs multiple depots with parallel bot execution
"""

from __future__ import annotations
import argparse
import time
import os
import csv
from typing import List, Tuple, Dict
from sim.grid import Grid
from sim.routing import astar
from sim.collision_tracker import simulate_multi_bot_execution, convert_tour_to_paths
from exp.scenarios import make_map, sample_depot_and_picks
from exp.multi_depot_scenarios import sample_multiple_depots, assign_packages_to_depots
from algos.hybrids import hybrid_nn_2opt
from algos.tsp_nn_2opt import nn_2opt
from algos.tsp_exact import held_karp
from algos.tsp_ga import ga_tsp


def pairwise_distance_builder(grid: Grid, waypoints: List[Tuple[int, int]]):
    """Build distance function with caching"""
    cache = {}
    def dist(i: int, j: int) -> float:
        if i == j:
            return 0.0
        key = (min(i, j), max(i, j))
        if key in cache:
            return cache[key]
        path, L, _ = astar(grid, waypoints[i], waypoints[j], diag_allowed=True)
        cache[key] = L
        return L
    return dist


def plan_sequence(name: str, dist_fn, n, start, seed=0):
    """
    Plan sequence using specified algorithm
    
    Note: This function is called independently for each depot in multi-depot scenarios.
    For Held-Karp (single-tour algorithm), it solves each depot's TSP sub-problem optimally.
    See run_multi_depot() docstring for details on the multi-depot adaptation strategy.
    """
    if name == "NN2opt":
        return nn_2opt(dist_fn, n, start)
    if name == "HeldKarp":
        order, L, _ = held_karp(dist_fn, n, start)
        return order, L
    if name == "GA":
        return ga_tsp(dist_fn, n, start, seed=seed, pop=48, gens=150)
    if name == "HybridNN2opt":
        return hybrid_nn_2opt(dist_fn, n, start)
    raise ValueError(f"Unknown algo {name}")


def run_single_depot(grid: Grid, depot: Pos, packages: List[Pos], algo_name: str, seed: int):
    """Run single depot scenario (baseline)"""
    waypoints = [depot] + packages
    dist = pairwise_distance_builder(grid, waypoints)
    
    t0 = time.perf_counter()
    order, tour_len = plan_sequence(algo_name, dist, len(waypoints), start=0, seed=seed)
    plan_time = (time.perf_counter() - t0) * 1000
    
    # Calculate execution time (simulated - sum of path distances)
    total_distance = tour_len
    
    return {
        'num_depots': 1,
        'num_bots': 1,
        'tour_len': tour_len,
        'plan_time_ms': plan_time,
        'total_distance': total_distance,
        'makespan': total_distance,  # Sequential execution
        'packages_per_bot': [len(packages)]
    }


def run_multi_depot(grid: Grid, depots: List[Pos], packages: List[Pos], 
                    algo_name: str, seed: int, parallel=True):
    """
    Run multi-depot scenario with multiple bots
    
    Multi-Depot Adaptation Strategy:
    --------------------------------
    This function adapts single-tour TSP algorithms (like Held-Karp) for multi-depot scenarios
    using a "divide-and-conquer" approach:
    
    1. Package Assignment: Packages are assigned to the nearest depot using A* pathfinding
    2. Problem Decomposition: The multi-depot problem is decomposed into multiple independent
       single-depot TSP sub-problems (one per depot)
    3. Independent Solving: Each TSP algorithm (including Held-Karp) is applied independently
       to each depot's sub-problem (depot + assigned packages)
    4. Parallel Execution: Bots execute their tours in parallel, with makespan = max(bot_times)
    
    Note: Held-Karp is a single-tour TSP algorithm. In this adaptation, it solves each
    depot's TSP instance optimally, but the overall solution is not globally optimal since
    package assignment is done heuristically (nearest depot) rather than optimally.
    
    Args:
        parallel: If True, bots work in parallel (makespan = max bot time)
                  If False, bots work sequentially (makespan = sum of bot times)
    """
    assignments = assign_packages_to_depots(grid, depots, packages, seed)
    
    bot_times = []
    bot_distances = []
    bot_tour_lens = []
    bot_plan_times = []
    packages_per_bot = []
    bot_tours = []  # Store tours for collision simulation
    bot_waypoints_list = []  # Store waypoints for each bot
    
    # Each depot has one bot
    for depot_idx, depot_pos in enumerate(depots):
        assigned_packages = assignments[depot_idx]
        
        if len(assigned_packages) == 0:
            # No packages assigned, bot stays at depot
            bot_times.append(0.0)
            bot_distances.append(0.0)
            bot_tour_lens.append(0.0)
            bot_plan_times.append(0.0)
            packages_per_bot.append(0)
            bot_tours.append([])  # Empty tour
            bot_waypoints_list.append([depot_pos])
            continue
        
        # Get package positions
        pkg_positions = [packages[i] for i in assigned_packages]
        waypoints = [depot_pos] + pkg_positions
        dist = pairwise_distance_builder(grid, waypoints)
        
        # Plan sequence for this bot
        t0 = time.perf_counter()
        order, tour_len = plan_sequence(algo_name, dist, len(waypoints), start=0, seed=seed + depot_idx)
        plan_time = (time.perf_counter() - t0) * 1000
        
        # Convert tour to paths for collision simulation
        tour_paths = convert_tour_to_paths(grid, order, waypoints)
        
        bot_tour_lens.append(tour_len)
        bot_plan_times.append(plan_time)
        bot_distances.append(tour_len)
        bot_times.append(tour_len)  # Execution time = tour length (simplified)
        packages_per_bot.append(len(assigned_packages))
        bot_tours.append(tour_paths)
        bot_waypoints_list.append(waypoints)
    
    # Calculate theoretical makespan (parallel execution = max time, sequential = sum)
    if parallel:
        theoretical_makespan = max(bot_times) if bot_times else 0.0
        # Planning time for parallel = max (bots plan simultaneously)
        total_plan_time = max(bot_plan_times) if bot_plan_times else 0.0
    else:
        theoretical_makespan = sum(bot_times)
        total_plan_time = sum(bot_plan_times)
    
    # Run collision simulation for parallel execution
    collision_makespan = theoretical_makespan
    collision_stats = None
    if parallel and len([t for t in bot_tours if t]) > 1:
        # Only simulate if we have multiple bots with tours
        try:
            # Filter out empty tours
            active_tours = [tour for tour in bot_tours if tour]
            if len(active_tours) > 1:
                collision_makespan, collision_stats = simulate_multi_bot_execution(
                    grid, active_tours, step_time=0.2
                )
        except Exception as e:
            # Fallback if simulation fails
            print(f"⚠️  Collision simulation failed: {e}, using theoretical makespan")
            collision_makespan = theoretical_makespan
            collision_stats = None
    
    total_distance = sum(bot_distances)
    avg_tour_len = sum(bot_tour_lens) / len(bot_tour_lens) if bot_tour_lens else 0.0
    
    # Collision metrics
    collision_count = collision_stats.total_collisions if collision_stats else 0
    total_wait_time = collision_stats.total_wait_time if collision_stats else 0.0
    max_wait_time = collision_stats.max_wait_time if collision_stats else 0.0
    avg_wait_time = (total_wait_time / collision_count) if collision_count > 0 else 0.0
    
    return {
        'num_depots': len(depots),
        'num_bots': len(depots),
        'tour_len': avg_tour_len,  # Average tour length per bot
        'plan_time_ms': total_plan_time,
        'total_distance': total_distance,
        'makespan': theoretical_makespan,  # Theoretical makespan (no collisions)
        'collision_makespan': collision_makespan,  # Actual makespan with collisions
        'packages_per_bot': packages_per_bot,
        'max_bot_time': max(bot_times) if bot_times else 0.0,
        'min_bot_time': min(bot_times) if bot_times else 0.0,
        'collision_count': collision_count,
        'total_wait_time': total_wait_time,
        'max_wait_time': max_wait_time,
        'avg_wait_time': avg_wait_time
    }


def run_comparison(map_type: str, K: int, seed: int, algo_name: str, 
                   num_depots: int, out_writer):
    """Run both single and multi-depot scenarios and compare"""
    grid = make_map(map_type, w=20, h=20, seed=seed)
    depot, picks = sample_depot_and_picks(grid, K, seed=seed)
    
    # Single depot (baseline) - no collisions (single bot)
    single_result = run_single_depot(grid, depot, picks, algo_name, seed)
    # Add collision fields for consistency (always 0 for single bot)
    single_result['collision_count'] = 0
    single_result['total_wait_time'] = 0.0
    single_result['max_wait_time'] = 0.0
    single_result['avg_wait_time'] = 0.0
    single_result['collision_makespan'] = single_result['makespan']
    
    # Multi-depot - with collision tracking
    depots = sample_multiple_depots(grid, num_depots, seed=seed)
    multi_result = run_multi_depot(grid, depots, picks, algo_name, seed, parallel=True)
    
    # Calculate improvement
    time_improvement = ((single_result['makespan'] - multi_result['makespan']) / 
                       max(1, single_result['makespan'])) * 100.0
    
    # Write results
    out_writer.writerow({
        "map_type": map_type,
        "K": K,
        "seed": seed,
        "algo": algo_name,
        "num_depots": 1,
        "num_bots": 1,
        "tour_len": round(single_result['tour_len'], 3),
        "plan_time_ms": round(single_result['plan_time_ms'], 2),
        "makespan": round(single_result['makespan'], 3),
        "collision_makespan": round(single_result['collision_makespan'], 3),
        "total_distance": round(single_result['total_distance'], 3),
        "packages_per_bot": str(single_result['packages_per_bot']),
        "collision_count": single_result['collision_count'],
        "total_wait_time": round(single_result['total_wait_time'], 3),
        "max_wait_time": round(single_result['max_wait_time'], 3),
        "avg_wait_time": round(single_result['avg_wait_time'], 3),
        "time_improvement_pct": "",
        "config": "single_depot"
    })
    
    out_writer.writerow({
        "map_type": map_type,
        "K": K,
        "seed": seed,
        "algo": algo_name,
        "num_depots": multi_result['num_depots'],
        "num_bots": multi_result['num_bots'],
        "tour_len": round(multi_result['tour_len'], 3),
        "plan_time_ms": round(multi_result['plan_time_ms'], 2),
        "makespan": round(multi_result['makespan'], 3),
        "collision_makespan": round(multi_result['collision_makespan'], 3),
        "total_distance": round(multi_result['total_distance'], 3),
        "packages_per_bot": str(multi_result['packages_per_bot']),
        "collision_count": multi_result['collision_count'],
        "total_wait_time": round(multi_result['total_wait_time'], 3),
        "max_wait_time": round(multi_result['max_wait_time'], 3),
        "avg_wait_time": round(multi_result['avg_wait_time'], 3),
        "time_improvement_pct": round(time_improvement, 2),
        "config": "multi_depot"
    })


def main():
    ap = argparse.ArgumentParser(description="Multi-depot, multi-bot warehouse experiment")
    ap.add_argument("--map-types", nargs="+", default=["narrow", "wide", "cross"])
    ap.add_argument("--K", nargs="+", type=int, default=[10, 15])
    ap.add_argument("--seeds", type=int, default=10, help="Number of random seeds (runs) - increased for statistical significance")
    ap.add_argument("--algos", default="HybridNN2opt,NN2opt,HeldKarp,GA")
    ap.add_argument("--num-depots", type=int, default=3, help="Number of depots/bots")
    ap.add_argument("--out", default="results/raw")
    args = ap.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "multi_depot_runs.csv")
    
    with open(out_path, "w", newline="") as f:
        fieldnames = ["map_type", "K", "seed", "algo", "num_depots", "num_bots",
                     "tour_len", "plan_time_ms", "makespan", "collision_makespan",
                     "total_distance", "packages_per_bot", "collision_count",
                     "total_wait_time", "max_wait_time", "avg_wait_time",
                     "time_improvement_pct", "config"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        
        for map_type in args.map_types:
            for K in args.K:
                for seed in range(args.seeds):
                    for algo in args.algos.split(","):
                        try:
                            run_comparison(map_type, K, seed, algo, args.num_depots, w)
                        except (ValueError, IndexError) as e:
                            print(f"⚠️  Skipping {map_type} K={K} seed={seed} algo={algo}: {type(e).__name__}: {e}")
                            import traceback
                            print(f"   Full traceback: {traceback.format_exc().split(chr(10))[-3]}")
                            continue
                        except Exception as e:
                            print(f"⚠️  Skipping {map_type} K={K} seed={seed} algo={algo}: Unexpected {type(e).__name__}: {e}")
                            import traceback
                            print(f"   Full traceback: {traceback.format_exc().split(chr(10))[-3]}")
                            continue
    
    print(f"Wrote {out_path}")
    
    # Generate formatted comparison
    try:
        from generate_multi_depot_results import generate_comparison
        generate_comparison(out_path)
    except ImportError:
        pass


if __name__ == "__main__":
    main()
