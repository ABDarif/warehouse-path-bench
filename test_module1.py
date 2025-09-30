from __future__ import annotations
import unittest
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sim.grid import Grid
from sim.routing import astar, dijkstra
from algos.tsp_nn_2opt import nn_2opt, nearest_neighbor, tour_length
from algos.tsp_exact import held_karp

class TestModule1(unittest.TestCase):
    
    def setUp(self):
        """Create 7x7 test grid with obstacles"""
        self.grid = Grid(7, 7, set())
        # Add some obstacles to create interesting paths
        self.grid.obstacles = {(1,1), (1,2), (2,1), (3,3), (4,4)}
        
    def test_astar_vs_dijkstra(self):
        """Test that A* and Dijkstra give same path costs"""
        start, goal = (0,0), (6,6)
        
        path_astar, cost_astar, _ = astar(self.grid, start, goal, diag_allowed=False)
        path_dijk, cost_dijk, _ = dijkstra(self.grid, start, goal)
        
        self.assertAlmostEqual(cost_astar, cost_dijk, delta=1e-6,
                             msg="A* and Dijkstra should find same cost paths")
        self.assertTrue(len(path_astar) > 0, "A* should find a path")
        self.assertTrue(len(path_dijk) > 0, "Dijkstra should find a path")
        
    def test_nn2opt_improvement(self):
        """Test that 2-opt never makes solution worse than plain NN"""
        # Simple 4-point Euclidean test
        def dist(i, j):
            points = [(0,0), (1,2), (3,1), (2,3)]
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            return (dx*dx + dy*dy) ** 0.5
            
        nn_tour = nearest_neighbor(dist, 4, 0)
        nn_len = tour_length(nn_tour, dist)
        
        opt_tour, opt_len = nn_2opt(dist, 4, 0)
        
        self.assertLessEqual(opt_len, nn_len + 1e-6,
                           msg="2-opt should not make solution worse than NN")
        
    def test_held_karp_optimality(self):
        """Test that Held-Karp finds optimal solution for small cases"""
        # Small test case where HK should be optimal
        def dist(i, j):
            d = [
                [0, 1, 2, 3],
                [1, 0, 1, 2],
                [2, 1, 0, 1],
                [3, 2, 1, 0]
            ]
            return d[i][j]
            
        hk_order, hk_len, stats = held_karp(dist, 4, 0)
        nn_order, nn_len = nn_2opt(dist, 4, 0)
        
        self.assertLessEqual(hk_len, nn_len + 1e-6,
                           msg="Held-Karp should be at least as good as NN+2opt")

def run_micro_benchmark():
    """CLI micro-benchmark: print (algo, K, ms)"""
    import time
    
    def create_test_dist(n):
        """Create a simple Euclidean distance matrix for testing"""
        import math
        # Create points along a line for simple testing
        points = [(i * 10, i * 5) for i in range(n)]
        
        def dist(i, j):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            return math.sqrt(dx*dx + dy*dy)
        return dist
    
    print("algo\tK\ttime_ms")
    print("-" * 20)
    
    # Test different problem sizes
    for K in [4, 6, 8, 10, 12]:
        n = K + 1  # including depot
        dist_fn = create_test_dist(n)
        
        # Test NN+2opt
        t0 = time.time()
        nn_2opt(dist_fn, n, 0)
        nn_time = (time.time() - t0) * 1000
        
        # Test Held-Karp (only for small K due to exponential complexity)
        if K <= 10:
            t0 = time.time()
            held_karp(dist_fn, n, 0, time_limit=10.0)
            hk_time = (time.time() - t0) * 1000
            print(f"HK\t{K}\t{hk_time:.1f}")
            
        print(f"NN2opt\t{K}\t{nn_time:.1f}")

if __name__ == "__main__":
    print("Running Module 1 Tests...")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run micro-benchmark
    print("\n" + "=" * 50)
    print("MICRO-BENCHMARK RESULTS:")
    print("=" * 50)
    run_micro_benchmark()