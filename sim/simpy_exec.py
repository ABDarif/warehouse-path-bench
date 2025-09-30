
from __future__ import annotations
import simpy
from dataclasses import dataclass
from typing import Dict, Tuple, List
from .grid import Grid, Pos
from .routing import astar

@dataclass
class CellRes:
    pos: Pos
    res: simpy.Resource

def build_cell_resources(env: simpy.Environment, grid: Grid, cap:int=1):
    return {p: CellRes(p, simpy.Resource(env, capacity=cap)) for p in grid.free_cells()}

def follow_path(env: simpy.Environment, path: List[Pos], cells: Dict[Pos, CellRes], step_time: float):
    if not path: return
    first = path[0]
    with cells[first].res.request() as req:
        yield req
        cur = first
        for nxt in path[1:]:
            with cells[nxt].res.request() as req2:
                yield req2        # wait if occupied
                yield env.timeout(step_time)
                cells[cur].res.release(cells[cur].res.users[0])
                cur = nxt

def simulate_execution(grid: Grid, leg_paths: List[List[Pos]], step_time=0.2):
    env = simpy.Environment()
    cells = build_cell_resources(env, grid, cap=1)
    def proc():
        for path in leg_paths:
            yield env.process(follow_path(env, path, cells, step_time))
    env.process(proc())
    env.run()
    return env.now  # total exec time (seconds)
