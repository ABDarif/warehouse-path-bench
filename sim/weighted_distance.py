"""
Weighted Distance Function for HybridNN2opt
Implements the weight function: w(i,j) = α*Dij + β*Tij + γ*Cij + δ*Uij + ε*Rj
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Callable, Optional
from sim.grid import Grid
from sim.routing import astar

Pos = Tuple[int, int]


def manhattan_distance(p1: Pos, p2: Pos) -> float:
    """Manhattan distance between two points"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def turn_cost(prev: Optional[Pos], current: Pos, next_pos: Pos) -> int:
    """
    Calculate turn penalty: 0 (straight), 1 (90° turn), 2 (180° turn)
    """
    if prev is None:
        return 0
    
    # Direction vectors
    dir1 = (current[0] - prev[0], current[1] - prev[1])
    dir2 = (next_pos[0] - current[0], next_pos[1] - current[1])
    
    # Normalize (should be unit vectors for grid movement)
    if dir1 == (0, 0) or dir2 == (0, 0):
        return 0
    
    # Dot product to determine angle
    dot = dir1[0] * dir2[0] + dir1[1] * dir2[1]
    
    if dot == 0:
        return 1  # 90° turn
    elif dot < 0:
        return 2  # 180° turn (backtrack)
    else:
        return 0  # Straight or slight turn


def is_legal_direction(grid: Grid, from_pos: Pos, to_pos: Pos) -> bool:
    """
    Check if movement from from_pos to to_pos is legal (one-way aisle check)
    For now, all directions are legal (one-way aisles not fully implemented)
    """
    # TODO: Implement actual one-way aisle checking if needed
    # For now, all movements are legal
    return True


def build_weighted_distance_function(
    grid: Grid,
    waypoints: List[Pos],
    depots: List[Pos],
    traffic_map: Optional[Dict[Tuple[Pos, Pos], float]] = None,
    alpha: float = 1.0,
    beta: float = 2.0,
    gamma: float = 3.0,
    delta: float = 1000.0,
    epsilon: float = 0.5
) -> Callable[[int, int, Optional[int]], float]:
    """
    Build weighted distance function for HybridNN2opt
    
    Args:
        grid: Warehouse grid
        waypoints: List of waypoint positions (depot + packages)
        depots: List of depot positions (for dock attraction)
        traffic_map: Optional map of (from, to) -> congestion level
        alpha: Distance weight (default: 1.0)
        beta: Turn penalty weight (default: 2.0)
        gamma: Collision risk weight (default: 3.0)
        delta: One-way violation penalty (default: 1000.0)
        epsilon: Dock attraction weight (default: 0.5)
    
    Returns:
        Weighted distance function: dist(i, j, prev_idx) -> float
    """
    if traffic_map is None:
        traffic_map = {}
    
    # Cache for A* paths (for turn calculation)
    path_cache: Dict[Tuple[int, int], List[Pos]] = {}
    
    def get_path(i: int, j: int) -> List[Pos]:
        """Get A* path between waypoints, with caching"""
        if i == j:
            return [waypoints[i]]
        key = (min(i, j), max(i, j))
        if key not in path_cache:
            path, _, _ = astar(grid, waypoints[i], waypoints[j], diag_allowed=True)
            path_cache[key] = path if path else [waypoints[i], waypoints[j]]
        return path_cache[key]
    
    def weighted_dist(i: int, j: int, prev_idx: Optional[int] = None) -> float:
        """
        Calculate weighted distance between waypoints i and j
        
        Args:
            i: Source waypoint index
            j: Destination waypoint index
            prev_idx: Previous waypoint index (for turn penalty), None if first move
        
        Returns:
            Weighted distance cost
        """
        if i == j:
            return 0.0
        
        pos_i = waypoints[i]
        pos_j = waypoints[j]
        
        # 1. Distance (Manhattan)
        D = manhattan_distance(pos_i, pos_j)
        
        # 2. Turn penalty
        T = 0
        if prev_idx is not None:
            prev_pos = waypoints[prev_idx]
            # Get path to determine actual turn
            path = get_path(i, j)
            if len(path) >= 2:
                # Use first step to determine turn
                first_step = path[1] if len(path) > 1 else pos_j
                T = turn_cost(prev_pos, pos_i, first_step)
        
        # 3. Collision/congestion risk
        C = traffic_map.get((pos_i, pos_j), 0.0)
        # Also check reverse direction
        C = max(C, traffic_map.get((pos_j, pos_i), 0.0))
        
        # 4. One-way aisle violation
        U = 0 if is_legal_direction(grid, pos_i, pos_j) else 1
        
        # 5. Dock attraction (distance to nearest dock)
        R = min(manhattan_distance(pos_j, depot) for depot in depots) if depots else 0.0
        
        # Calculate weighted cost
        cost = (
            alpha * D +
            beta * T +
            gamma * C +
            delta * U +
            epsilon * R
        )
        
        return cost
    
    return weighted_dist


def build_weighted_distance_for_hybrid(
    grid: Grid,
    waypoints: List[Pos],
    depots: List[Pos],
    traffic_map: Optional[Dict[Tuple[Pos, Pos], float]] = None
) -> Callable[[int, int], float]:
    """
    Build weighted distance function compatible with TSP algorithms
    (prev_idx not needed for compatibility)
    
    For HybridNN2opt, we use a simplified version that considers:
    - Distance (A* pathfinding)
    - Dock attraction
    - Collision risk (if traffic_map provided)
    """
    if traffic_map is None:
        traffic_map = {}
    
    # Cache A* distances
    cache: Dict[Tuple[int, int], float] = {}
    
    def dist(i: int, j: int) -> float:
        if i == j:
            return 0.0
        
        key = (min(i, j), max(i, j))
        if key in cache:
            return cache[key]
        
        pos_i = waypoints[i]
        pos_j = waypoints[j]
        
        # Get A* path and distance
        path, L, _ = astar(grid, pos_i, pos_j, diag_allowed=True)
        
        # Handle unreachable case
        if path is None or len(path) == 0 or L == float('inf'):
            # Fallback to Manhattan distance if A* fails
            L = manhattan_distance(pos_i, pos_j)
        
        # Base distance cost (α = 1.0)
        D = L
        
        # Collision risk (γ = 3.0)
        C = max(
            traffic_map.get((pos_i, pos_j), 0.0),
            traffic_map.get((pos_j, pos_i), 0.0)
        )
        
        # Dock attraction (ε = 0.5)
        R = min(manhattan_distance(pos_j, depot) for depot in depots) if depots else 0.0
        
        # Weighted cost: α*D + γ*C + ε*R
        # (Turn penalty and one-way violation require path context, simplified here)
        cost = 1.0 * D + 3.0 * C + 0.5 * R
        
        cache[key] = cost
        return cost
    
    return dist
