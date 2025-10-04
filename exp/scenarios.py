
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

def sample_depot_and_picks(g: Grid, K: int, seed=0) -> Tuple[Pos, List[Pos]]:
    rng = random.Random(seed)
    free = g.free_cells()
    depot = (0,0)
    if depot not in free:
        depot = free[0]
    picks = rng.sample([p for p in free if p != depot], K)
    return depot, picks
