
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Iterable, Dict, Set
import numpy as np

Pos = Tuple[int, int]

@dataclass
class Grid:
    width: int
    height: int
    obstacles: Set[Pos]  # blocked cells
    diag: bool = False   # 4-conn by default

    @classmethod
    def empty(cls, w: int, h: int):
        return cls(w, h, set())

    def in_bounds(self, p: Pos) -> bool:
        x,y = p
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, p: Pos) -> bool:
        return p not in self.obstacles

    def neighbors(self, p: Pos) -> Iterable[Pos]:
        x,y = p
        steps4 = [(1,0),(-1,0),(0,1),(0,-1)]
        steps8 = steps4 + [(1,1),(1,-1),(-1,1),(-1,-1)]
        steps = steps8 if self.diag else steps4
        for dx,dy in steps:
            q = (x+dx, y+dy)
            if self.in_bounds(q) and self.passable(q):
                yield q

    def free_cells(self) -> List[Pos]:
        return [(x,y) for x in range(self.width) for y in range(self.height) if self.passable((x,y))]

    def add_rect_obstacle(self, x0:int, y0:int, x1:int, y1:int):
        for x in range(x0, x1+1):
            for y in range(y0, y1+1):
                if self.in_bounds((x,y)):
                    self.obstacles.add((x,y))
