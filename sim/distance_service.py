from __future__ import annotations
import pickle
import os
from typing import Dict, Tuple, List, Callable
import sys
import os

# Add the parent directory to Python path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim.grid import Grid
from sim.routing import astar

class DistanceService:
    def __init__(self, grid: Grid, cache_file: str = None):
        self.grid = grid
        self.cache: Dict[Tuple[Tuple[int,int], Tuple[int,int]], float] = {}
        self.cache_file = cache_file
        self.load_cache()
        
    def load_cache(self):
        """Load cached distances from file"""
        if self.cache_file and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                print(f"Loaded {len(self.cache)} cached distances")
            except Exception as e:
                print(f"Cache load failed: {e}")
                self.cache = {}
                
    def save_cache(self):
        """Save current distances to cache file"""
        if self.cache_file:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            try:
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(self.cache, f)
                print(f"Saved {len(self.cache)} distances to cache")
            except Exception as e:
                print(f"Cache save failed: {e}")
                
    def get_distance(self, a: Tuple[int,int], b: Tuple[int,int], 
                    diag_allowed: bool = True) -> float:
        """Get distance between two points, using cache if available"""
        if a == b:
            return 0.0
            
        # Create canonical key (always store with sorted coordinates)
        key = (min(a, b), max(a, b))
        if key in self.cache:
            return self.cache[key]
            
        # Compute new distance using A*
        path, cost, _ = astar(self.grid, a, b, diag_allowed=diag_allowed)
        self.cache[key] = cost
        
        return cost
        
    def pairwise_distances(self, waypoints: List[Tuple[int,int]], 
                          diag_allowed: bool = True) -> Callable[[int,int], float]:
        """Returns a distance function for TSP algorithms"""
        n = len(waypoints)
        
        # Create distance matrix
        dist_matrix = [[0.0] * n for _ in range(n)]
        
        # Precompute all pairwise distances
        print(f"Precomputing {n}x{n} distance matrix...")
        for i in range(n):
            for j in range(i+1, n):
                dist = self.get_distance(waypoints[i], waypoints[j], diag_allowed)
                dist_matrix[i][j] = dist
                dist_matrix[j][i] = dist
                
        def dist_fn(i: int, j: int) -> float:
            return dist_matrix[i][j]
            
        return dist_fn
        
    def __del__(self):
        """Save cache when object is destroyed"""
        self.save_cache()
        
    def clear_cache(self):
        """Clear the distance cache"""
        self.cache = {}
        if self.cache_file and os.path.exists(self.cache_file):
            os.remove(self.cache_file)