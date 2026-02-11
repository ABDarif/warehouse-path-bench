"""
A* based greedy TSP solver
Uses A* pathfinding for distance calculation and greedy nearest-neighbor approach
"""

from __future__ import annotations
from typing import List, Tuple, Callable
from .tsp_nn_2opt import nearest_neighbor, tour_length

def astar_tsp(dist: Callable[[int, int], float], n: int, start: int = 0, **kw) -> Tuple[List[int], float]:
    """
    A* based TSP solver - uses greedy nearest neighbor with A* distances
    
    This is essentially a nearest neighbor approach where distances
    are calculated using A* pathfinding (which is already done in dist function)
    
    Args:
        dist: Distance function (uses A* internally)
        n: Number of nodes
        start: Starting node index
    
    Returns:
        (tour, tour_length)
    """
    if n <= 1:
        return [start], 0.0
    
    # Use nearest neighbor (distances already use A*)
    tour = nearest_neighbor(dist, n, start=start)
    length = tour_length(tour, dist)
    
    return tour, length
