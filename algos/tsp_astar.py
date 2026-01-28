"""
A*-Based TSP Algorithm
Uses A* pathfinding with congestion-aware heuristics for tour construction
"""

from __future__ import annotations
from typing import List, Tuple, Callable
import time


def astar_greedy_tsp(dist: Callable[[int, int], float], n: int, start: int = 0, **kw) -> Tuple[List[int], float]:
    """
    A*-based greedy TSP algorithm using nearest neighbor with A* distances
    
    This algorithm uses A* pathfinding distances (already computed via pairwise_distance_builder)
    to construct tours. It's similar to Nearest Neighbor but emphasizes the use of
    A* pathfinding for accurate distance calculations in grid environments.
    
    Args:
        dist: Distance function (uses A* pathfinding internally)
        n: Number of waypoints
        start: Starting waypoint index
        **kw: Additional keyword arguments (unused, for compatibility)
    
    Returns:
        Tuple of (tour_order, tour_length)
    """
    if n <= 1:
        return [start], 0.0
    
    unvisited = set(range(n))
    unvisited.remove(start)
    tour = [start]
    cur = start
    
    # Greedy selection: always choose nearest unvisited node
    while unvisited:
        # Find nearest unvisited node using A* distances
        nxt = min(unvisited, key=lambda j: dist(cur, j))
        tour.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    
    # Calculate tour length
    tour_len = tour_length(tour, dist)
    
    return tour, tour_len


def astar_multi_start_tsp(dist: Callable[[int, int], float], n: int, start: int = 0, **kw) -> Tuple[List[int], float]:
    """
    A*-based multi-start greedy TSP algorithm
    
    Similar to astar_greedy_tsp but tries multiple starting points and returns the best.
    This provides better exploration of the solution space.
    
    Args:
        dist: Distance function (uses A* pathfinding internally)
        n: Number of waypoints
        start: Preferred starting waypoint index
        **kw: Additional keyword arguments
            - max_starts: Maximum number of starting points to try (default: 3)
    
    Returns:
        Tuple of (best_tour_order, best_tour_length)
    """
    if n <= 1:
        return [start], 0.0
    
    max_starts = kw.get('max_starts', 3)
    
    # Select starting points: prefer given start, then try others
    start_points = [start]
    if n > 2:
        mid_point = n // 2
        if mid_point != start:
            start_points.append(mid_point)
        if n > 4:
            quarter_point = n // 4
            if quarter_point != start and quarter_point != mid_point:
                start_points.append(quarter_point)
    start_points = start_points[:max_starts]
    
    best_tour = None
    best_len = float('inf')
    
    # Try each starting point
    for sp in start_points:
        tour, tour_len = astar_greedy_tsp(dist, n, start=sp)
        if tour_len < best_len:
            best_len = tour_len
            best_tour = tour
    
    return best_tour, best_len


def tour_length(order: List[int], dist: Callable[[int, int], float]) -> float:
    """Calculate total tour length"""
    if len(order) <= 1:
        return 0.0
    s = 0.0
    for i in range(len(order)):
        s += dist(order[i], order[(i + 1) % len(order)])
    return s


# Default export: use multi-start version for better quality
def astar_tsp(dist: Callable[[int, int], float], n: int, start: int = 0, **kw) -> Tuple[List[int], float]:
    """
    Main A*-based TSP algorithm entry point
    
    Uses multi-start greedy approach for better solution quality.
    This algorithm leverages A* pathfinding for accurate distance calculations
    in grid-based warehouse environments.
    
    Args:
        dist: Distance function (uses A* pathfinding internally)
        n: Number of waypoints
        start: Starting waypoint index
        **kw: Additional keyword arguments
    
    Returns:
        Tuple of (tour_order, tour_length)
    """
    return astar_multi_start_tsp(dist, n, start, **kw)
