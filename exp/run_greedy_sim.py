"""
Warehouse Package Picking Simulation with Greedy Navigation
Based on try3/try3GA approach - outputs terminal performance summary
"""

from __future__ import annotations
import argparse
import time
from sim.grid import Grid
from sim.greedy_nav import greedy_package_picking
from exp.scenarios import make_map, sample_depot_and_picks


def run_simulation(map_type: str, K: int, seed: int, algo_name: str = "GreedyNN"):
    """Run a single simulation using greedy nearest-neighbor navigation"""
    
    # Create warehouse
    grid = make_map(map_type, w=20, h=20, seed=seed)
    depot, picks = sample_depot_and_picks(grid, K, seed=seed)
    
    # Run greedy navigation
    start_time = time.perf_counter()
    visit_order, total_distance, total_steps = greedy_package_picking(grid, depot, picks)
    exec_time = time.perf_counter() - start_time
    
    # Calculate performance metrics
    packages_completed = len(visit_order)
    success_rate = 100.0 * packages_completed / max(1, K)
    
    if total_steps > 0:
        steps_per_package = total_steps / max(1, packages_completed)
    else:
        steps_per_package = 0.0
    
    return {
        'map_type': map_type,
        'K': K,
        'seed': seed,
        'algo': algo_name,
        'total_time_ticks': total_steps,
        'exec_time_s': exec_time,
        'total_distance': total_distance,
        'packages_completed': packages_completed,
        'total_packages': K,
        'success_rate': success_rate,
        'steps_per_package': steps_per_package,
        'visit_order': visit_order
    }


def print_summary(results: dict):
    """Print performance summary similar to try3 output"""
    print("\n" + "="*60)
    print("SIMULATION COMPLETE - SUMMARY")
    print("="*60)
    print(f"Algorithm: {results['algo']}")
    print(f"Map Type: {results['map_type']}")
    print(f"Total time (ticks): {results['total_time_ticks']}")
    print(f"Execution time: {results['exec_time_s']:.3f} seconds")
    print(f"Total distance: {results['total_distance']:.2f}")
    print(f"Packages: {results['packages_completed']}/{results['total_packages']}")
    print(f"Success rate: {results['success_rate']:.1f}%")
    print(f"Steps per package: {results['steps_per_package']:.2f}")
    print("="*60)


def main():
    ap = argparse.ArgumentParser(description="Greedy warehouse package picking simulation")
    ap.add_argument("--map-type", default="narrow", choices=["narrow", "wide", "cross"],
                    help="Warehouse map type")
    ap.add_argument("--K", type=int, default=10, help="Number of packages")
    ap.add_argument("--seeds", type=int, default=1, help="Number of random seeds to run")
    ap.add_argument("--algo", default="GreedyNN", help="Algorithm name")
    args = ap.parse_args()
    
    print("="*60)
    print("WAREHOUSE PACKAGE PICKING SIMULATION (Greedy Navigation)")
    print("="*60)
    print(f"Map Type: {args.map_type}")
    print(f"Packages (K): {args.K}")
    print(f"Seeds: {args.seeds}")
    print(f"Algorithm: {args.algo}")
    print("="*60)
    
    all_results = []
    
    for seed in range(args.seeds):
        print(f"\nRunning seed {seed}...")
        results = run_simulation(args.map_type, args.K, seed, args.algo)
        all_results.append(results)
        print_summary(results)
    
    # Aggregate statistics if multiple seeds
    if args.seeds > 1:
        print("\n" + "="*60)
        print("AGGREGATE STATISTICS (across all seeds)")
        print("="*60)
        avg_time = sum(r['total_time_ticks'] for r in all_results) / len(all_results)
        avg_distance = sum(r['total_distance'] for r in all_results) / len(all_results)
        avg_success = sum(r['success_rate'] for r in all_results) / len(all_results)
        avg_steps_per_pkg = sum(r['steps_per_package'] for r in all_results) / len(all_results)
        
        print(f"Average total time (ticks): {avg_time:.1f}")
        print(f"Average total distance: {avg_distance:.2f}")
        print(f"Average success rate: {avg_success:.1f}%")
        print(f"Average steps per package: {avg_steps_per_pkg:.2f}")
        print("="*60)


if __name__ == "__main__":
    main()
