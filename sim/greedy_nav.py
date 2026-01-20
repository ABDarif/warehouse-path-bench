"""
Greedy Nearest-Neighbor Navigation System
Based on try3/try3GA dynamic package picking approach
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Set, Optional
from .grid import Grid, Pos
from .routing import astar

class GreedyNavigator:
    """Greedy nearest-neighbor navigation for package picking"""
    
    def __init__(self, grid: Grid, depot: Pos, packages: List[Pos]):
        self.grid = grid
        self.depot = depot
        self.packages = packages
        self.visited = set()
        self.current_pos = depot
        self.total_distance = 0.0
        self.path_history: List[Pos] = [depot]
        self.steps = 0
        
    def get_distance(self, a: Pos, b: Pos) -> float:
        """Get distance between two positions using A*"""
        if a == b:
            return 0.0
        path, cost, _ = astar(self.grid, a, b, diag_allowed=True)
        return cost if path else float('inf')
    
    def find_nearest_package(self, current_pos: Pos, available_packages: List[int]) -> Optional[int]:
        """Find nearest unvisited package using greedy nearest-neighbor"""
        if not available_packages:
            return None
        
        min_distance = float('inf')
        nearest_idx = None
        
        for pkg_idx in available_packages:
            if pkg_idx in self.visited:
                continue
            pkg_pos = self.packages[pkg_idx]
            distance = self.get_distance(current_pos, pkg_pos)
            
            if distance < min_distance:
                min_distance = distance
                nearest_idx = pkg_idx
        
        return nearest_idx
    
    def navigate_greedy(self) -> Tuple[List[int], float, int]:
        """
        Navigate using greedy nearest-neighbor approach
        Returns: (visit_order, total_distance, total_steps)
        """
        visit_order: List[int] = []
        unvisited = set(range(len(self.packages)))
        self.current_pos = self.depot
        self.visited = set()
        self.total_distance = 0.0
        self.steps = 0
        
        while unvisited:
            # Find nearest unvisited package
            available = list(unvisited)
            nearest_idx = self.find_nearest_package(self.current_pos, available)
            
            if nearest_idx is None:
                break
            
            # Move to package
            pkg_pos = self.packages[nearest_idx]
            path, distance, _ = astar(self.grid, self.current_pos, pkg_pos, diag_allowed=True)
            
            if distance == float('inf') or not path:
                break
            
            self.total_distance += distance
            # Count steps in path (excluding starting position)
            if len(path) > 1:
                self.steps += len(path) - 1
            self.current_pos = pkg_pos
            self.visited.add(nearest_idx)
            unvisited.remove(nearest_idx)
            visit_order.append(nearest_idx)
        
        # Return to depot
        if self.current_pos != self.depot:
            path, return_distance, _ = astar(self.grid, self.current_pos, self.depot, diag_allowed=True)
            if path and return_distance < float('inf'):
                self.total_distance += return_distance
                if len(path) > 1:
                    self.steps += len(path) - 1
        
        return visit_order, self.total_distance, self.steps


def greedy_package_picking(grid: Grid, depot: Pos, packages: List[Pos]) -> Tuple[List[int], float, int]:
    """
    Greedy nearest-neighbor package picking algorithm
    Similar to try3/try3GA approach
    
    Returns: (visit_order, total_distance, total_steps)
    """
    navigator = GreedyNavigator(grid, depot, packages)
    return navigator.navigate_greedy()
