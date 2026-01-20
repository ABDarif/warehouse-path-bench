"""
Multi-Depot Scenario Generation
Generate multiple docking stations and assign packages to nearest depots
"""

from __future__ import annotations
from typing import List, Tuple, Dict
import random
from sim.grid import Grid
from sim.routing import astar

Pos = Tuple[int, int]

def sample_multiple_depots(g: Grid, num_depots: int, seed=0) -> List[Pos]:
    """Sample multiple depots (docking stations) from the grid"""
    rng = random.Random(seed)
    free = g.free_cells()
    
    # Limit num_depots to available cells
    if len(free) < num_depots:
        num_depots = len(free)
    
    if num_depots <= 0:
        return []
    
    # Find the largest connected component
    from exp.scenarios import _find_connected_component
    visited = set()
    largest_component = set()
    
    for cell in free:
        if cell not in visited:
            component = _find_connected_component(g, cell)
            visited.update(component)
            if len(component) > len(largest_component):
                largest_component = component
    
    if len(largest_component) < num_depots:
        largest_component = free
    
    # Ensure we don't try to sample more than available
    if len(largest_component) < num_depots:
        num_depots = len(largest_component)
    
    # Sample depots from different regions
    depots = []
    available = list(largest_component)
    
    for i in range(num_depots):
        if not available:
            break
        
        if i == 0:
            # First depot: prefer center area
            center_x, center_y = g.width // 2, g.height // 2
            candidates = [(abs(p[0] - center_x) + abs(p[1] - center_y), p) 
                          for p in available 
                          if len(list(g.neighbors(p))) >= 2]
            if candidates:
                candidates.sort()
                depot = candidates[0][1]
            else:
                depot = rng.choice(available)
        else:
            # Subsequent depots: prefer locations far from existing depots
            if len(depots) > 0:
                # Find point farthest from all existing depots
                max_min_dist = -1
                best_depot = None
                
                for candidate in available:
                    min_dist_to_depots = float('inf')
                    for existing_depot in depots:
                        path, dist, _ = astar(g, candidate, existing_depot, diag_allowed=True)
                        if dist < min_dist_to_depots:
                            min_dist_to_depots = dist
                    
                    if min_dist_to_depots > max_min_dist:
                        max_min_dist = min_dist_to_depots
                        best_depot = candidate
                
                depot = best_depot if best_depot else rng.choice(available)
            else:
                depot = rng.choice(available)
        
        depots.append(depot)
        available.remove(depot)
    
    return depots

def assign_packages_to_depots(g: Grid, depots: List[Pos], packages: List[Pos], seed=0) -> Dict[int, List[int]]:
    """
    Assign packages to depots based on proximity
    Returns: dict mapping depot_index -> list of package_indices
    """
    rng = random.Random(seed)
    assignments: Dict[int, List[int]] = {i: [] for i in range(len(depots))}
    
    for pkg_idx, pkg_pos in enumerate(packages):
        # Find nearest depot
        min_dist = float('inf')
        nearest_depot_idx = 0
        
        for depot_idx, depot_pos in enumerate(depots):
            path, dist, _ = astar(g, pkg_pos, depot_pos, diag_allowed=True)
            if dist < min_dist:
                min_dist = dist
                nearest_depot_idx = depot_idx
        
        assignments[nearest_depot_idx].append(pkg_idx)
    
    # Ensure each depot has at least one package (if possible)
    empty_depots = [idx for idx, pkgs in assignments.items() if len(pkgs) == 0]
    depots_with_packages = [idx for idx, pkgs in assignments.items() if len(pkgs) > 1]
    
    for empty_idx in empty_depots:
        if depots_with_packages:
            # Take one package from a depot with multiple packages
            donor_idx = rng.choice(depots_with_packages)
            if len(assignments[donor_idx]) > 1:
                pkg = assignments[donor_idx].pop()
                assignments[empty_idx].append(pkg)
                if len(assignments[donor_idx]) == 1:
                    depots_with_packages.remove(donor_idx)
    
    return assignments
