import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim.grid import Grid
from sim.distance_service import DistanceService
from exp.scenarios import make_map, sample_depot_and_picks

def simple_demo():
    """Simple demo that should work without import issues"""
    print("Module 1 Demo: Classical Methods")
    print("=" * 40)
    
    # 1. Create warehouse
    grid = make_map("narrow", w=10, h=10, seed=42)
    print(f"Created {grid.width}x{grid.height} grid with {len(grid.obstacles)} obstacles")
    
    # 2. Sample points
    depot, picks = sample_depot_and_picks(grid, K=3, seed=42)
    waypoints = [depot] + picks
    print(f"Depot: {depot}, Picks: {picks}")
    
    # 3. Create distance service
    dist_service = DistanceService(grid, "cache/demo_cache.pkl")
    
    # 4. Get distance function
    dist_fn = dist_service.pairwise_distances(waypoints, diag_allowed=True)
    
    # 5. Test some distances
    print("\nDistance Matrix:")
    n = len(waypoints)
    for i in range(n):
        for j in range(n):
            if i <= j:
                dist_ij = dist_fn(i, j)
                print(f"  {i}->{j}: {dist_ij:.2f}")
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    simple_demo()
