from __future__ import annotations
import argparse, time, os
from sim.grid import Grid
from sim.distance_service import DistanceService
from algos.tsp_exact import held_karp
from algos.tsp_nn_2opt import nn_2opt

def benchmark_algo(name: str, dist_fn, n: int, start: int = 0):
    t0 = time.perf_counter()
    
    if name == "HeldKarp":
        order, length, stats = held_karp(dist_fn, n, start)
    elif name == "NN2opt":
        order, length = nn_2opt(dist_fn, n, start)
    else:
        raise ValueError(f"Unknown algorithm: {name}")
        
    elapsed_ms = (time.perf_counter() - t0) * 1000
    
    return {
        'algo': name,
        'K': n-1,  # excluding depot
        'time_ms': round(elapsed_ms, 2),
        'tour_length': round(length, 3),
        'order': order
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--K", type=int, default=5)
    ap.add_argument("--algos", default="HeldKarp,NN2opt")
    ap.add_argument("--map-type", default="narrow")
    ap.add_argument("--out", default="results/module1")
    args = ap.parse_args()
    
    # Create test grid
    from exp.scenarios import make_map
    grid = make_map(args.map_type, w=20, h=20, seed=42)
    
    # Sample points
    from exp.scenarios import sample_depot_and_picks
    depot, picks = sample_depot_and_picks(grid, args.K, seed=42)
    waypoints = [depot] + picks
    
    # Initialize distance service with caching
    dist_service = DistanceService(grid, "cache/dist_cache.pkl")
    dist_fn = dist_service.pairwise_distances(waypoints, diag_allowed=True)
    
    # Run benchmarks
    print(f"Benchmarking K={args.K} on {args.map_type} map")
    print("algo\tK\ttime_ms\tlength")
    
    for algo_name in args.algos.split(","):
        result = benchmark_algo(algo_name, dist_fn, len(waypoints))
        print(f"{result['algo']}\t{result['K']}\t{result['time_ms']}\t{result['tour_length']}")

if __name__ == "__main__":
    main()