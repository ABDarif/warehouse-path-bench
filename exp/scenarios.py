
from __future__ import annotations
from typing import List, Tuple, Dict
import random
from sim.grid import Grid

Pos = Tuple[int,int]

def make_map(map_type: str, w=20, h=20, seed=0) -> Grid:
    rng = random.Random(seed)
    g = Grid.empty(w,h)
    # simple aisle patterns
    if map_type == 'narrow':
        for x in range(2, w-2, 3):
            for y in range(0,h):
                if y % 6 != 0:  # leave cross aisles
                    g.obstacles.add((x,y))
    elif map_type == 'wide':
        for x in range(3, w-3, 5):
            for y in range(0,h):
                if y % 8 != 0:
                    g.obstacles.add((x,y))
    elif map_type == 'cross':
        for y in range(2, h-2, 4):
            for x in range(0,w):
                g.obstacles.add((x,y))
        for x in range(3, w-3, 6):
            for y in range(0,h):
                g.obstacles.add((x,y))
        # carve main crossings
        for x in range(0,w,6):
            for y in range(0,h,4):
                for dx in range(-1,2):
                    for dy in range(-1,2):
                        g.obstacles.discard((x+dx,y+dy))
    else:
        pass
    return g

def _find_connected_component(g: Grid, start: Pos) -> set:
    """Find all cells reachable from start using BFS"""
    from collections import deque
    component = set()
    queue = deque([start])
    component.add(start)
    
    while queue:
        current = queue.popleft()
        for neighbor in g.neighbors(current):
            if neighbor not in component:
                component.add(neighbor)
                queue.append(neighbor)
    
    return component

def sample_depot_and_picks(g: Grid, K: int, seed=0) -> Tuple[Pos, List[Pos]]:
    rng = random.Random(seed)
    free = g.free_cells()
    
    # Find the largest connected component to ensure all waypoints are reachable
    visited = set()
    largest_component = set()
    
    for cell in free:
        if cell not in visited:
            component = _find_connected_component(g, cell)
            visited.update(component)
            if len(component) > len(largest_component):
                largest_component = component
    
    # If no large component found, use all free cells
    if len(largest_component) < K + 1:
        largest_component = free
    
    # Sample depot from center area of the component
    if largest_component:
        center_x, center_y = g.width // 2, g.height // 2
        candidates = [(abs(p[0] - center_x) + abs(p[1] - center_y), p) 
                      for p in largest_component 
                      if len(list(g.neighbors(p))) >= 2]
        if candidates:
            candidates.sort()
            depot = candidates[0][1]
        else:
            depot = list(largest_component)[0]
    else:
        depot = free[0] if free else (0,0)
    
    # Sample picks from the same component
    available_picks = [p for p in largest_component if p != depot]
    if len(available_picks) < K:
        # Not enough picks in component, use what we have
        picks = available_picks
    else:
        picks = rng.sample(available_picks, K)
    
    return depot, picks
