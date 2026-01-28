"""
High-Congestion Test Script
Forces scenarios that will generate collisions to verify collision tracking works
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sim.grid import Grid
from sim.routing import astar
from sim.collision_tracker import simulate_multi_bot_execution, convert_tour_to_paths
from exp.scenarios import make_map, sample_depot_and_picks
from exp.multi_depot_scenarios import sample_multiple_depots, assign_packages_to_depots
from algos.tsp_astar import astar_tsp


def pairwise_distance_builder(grid: Grid, waypoints: list):
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


def test_high_congestion():
    """Test with high congestion scenario"""
    print("=" * 70)
    print("HIGH-CONGESTION COLLISION TEST")
    print("=" * 70)
    print()
    
    # Create narrow map (more bottlenecks)
    grid = make_map("narrow", w=20, h=20, seed=42)
    
    # High package count
    K = 80
    depot, picks = sample_depot_and_picks(grid, K, seed=42)
    
    # Many depots (creates more bots)
    num_depots = 15
    depots = sample_multiple_depots(grid, num_depots, seed=42)
    
    print(f"Scenario Setup:")
    print(f"  Map: narrow (20×20)")
    print(f"  Total packages: {K}")
    print(f"  Number of depots/bots: {num_depots}")
    print(f"  Average packages per bot: {K / num_depots:.1f}")
    print()
    
    # Assign packages
    assignments = assign_packages_to_depots(grid, depots, picks, seed=42)
    
    # Show distribution
    packages_per_bot = [len(assignments[i]) for i in range(num_depots)]
    print(f"Packages per bot distribution:")
    print(f"  Min: {min(packages_per_bot)}")
    print(f"  Max: {max(packages_per_bot)}")
    print(f"  Avg: {sum(packages_per_bot) / len(packages_per_bot):.1f}")
    print(f"  Bots with ≤2 packages: {sum(1 for p in packages_per_bot if p <= 2)}/{num_depots}")
    print()
    
    # Plan tours for each bot using A*
    bot_tours = []
    bot_times = []
    
    for depot_idx, depot_pos in enumerate(depots):
        assigned_packages = assignments[depot_idx]
        
        if len(assigned_packages) == 0:
            bot_tours.append([])
            bot_times.append(0.0)
            continue
        
        pkg_positions = [picks[i] for i in assigned_packages]
        waypoints = [depot_pos] + pkg_positions
        dist = pairwise_distance_builder(grid, waypoints)
        
        # Plan with A*
        order, tour_len = astar_tsp(dist, len(waypoints), start=0)
        tour_paths = convert_tour_to_paths(grid, order, waypoints)
        
        bot_tours.append(tour_paths)
        bot_times.append(tour_len)
    
    # Filter active bots
    active_tours = [tour for tour in bot_tours if tour]
    active_count = len(active_tours)
    
    print(f"Active bots (with packages): {active_count}")
    print(f"Theoretical makespan (max bot time): {max(bot_times):.2f} seconds")
    print()
    
    if active_count < 2:
        print("⚠️  Not enough bots for collision testing!")
        return
    
    # Run collision simulation
    print("Running collision simulation...")
    collision_makespan, collision_stats = simulate_multi_bot_execution(
        grid, active_tours, step_time=0.2
    )
    
    print()
    print("=" * 70)
    print("COLLISION RESULTS")
    print("=" * 70)
    print(f"Total Collisions:        {collision_stats.total_collisions}")
    print(f"Total Wait Time:          {collision_stats.total_wait_time:.2f} seconds")
    print(f"Max Wait Time:            {collision_stats.max_wait_time:.2f} seconds")
    if collision_stats.total_collisions > 0:
        print(f"Avg Wait Time:            {collision_stats.total_wait_time / collision_stats.total_collisions:.2f} seconds")
    print(f"Theoretical Makespan:     {max(bot_times):.2f} seconds")
    print(f"Collision Makespan:      {collision_makespan:.2f} seconds")
    if max(bot_times) > 0:
        overhead = ((collision_makespan - max(bot_times)) / max(bot_times)) * 100
        print(f"Collision Overhead:       {overhead:+.2f}%")
    
    print()
    
    if collision_stats.total_collisions == 0:
        print("⚠️  STILL ZERO COLLISIONS!")
        print()
        print("Possible reasons:")
        print("  1. Bots finish too quickly (many have few packages)")
        print("  2. Warehouse too large for number of bots")
        print("  3. Depots too well-distributed (far apart)")
        print("  4. Paths don't overlap (good routing)")
        print()
        print("Try:")
        print("  - Increase packages: K=120, 150")
        print("  - Increase bots: num_depots=20, 25")
        print("  - Use smaller warehouse: w=15, h=15")
        print("  - Force depots closer together")
    else:
        print("✅ Collisions detected! Collision tracking is working.")
        print(f"   {collision_stats.total_collisions} collision events recorded")
        print(f"   {len(collision_stats.collision_locations)} unique collision locations")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    test_high_congestion()
