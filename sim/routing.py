from __future__ import annotations
from typing import Tuple, Dict, List, Optional, Callable
import heapq, math
from .grid import Grid, Pos

def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def octile(a: Pos, b: Pos) -> float:
    dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
    return (dx + dy) + (1.4142 - 2) * min(dx, dy)

def reconstruct_path(came_from: Dict[Pos, Pos], start: Pos, goal: Pos) -> List[Pos]:
    cur = goal
    path = [cur]
    while cur != start:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path

def dijkstra(grid: Grid, start: Pos, goal: Pos) -> Tuple[List[Pos], float, int]:
    pq = [(0, start)]
    dist = {start: 0}
    prev = {}
    nodes_expanded = 0
    
    while pq:
        d, u = heapq.heappop(pq)
        nodes_expanded += 1
        
        if u == goal:
            break
        if d != dist[u]:
            continue
            
        for v in grid.neighbors(u):
            w = 1.0 if (v[0]==u[0] or v[1]==u[1]) else 1.4142
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
                
    if goal not in dist: 
        return [], float('inf'), nodes_expanded
    return reconstruct_path(prev, start, goal), dist[goal], nodes_expanded

def astar(grid: Grid, start: Pos, goal: Pos, heuristic=None, 
          diag_allowed: bool = True) -> Tuple[List[Pos], float, int]:
    if heuristic is None:
        heuristic = octile if diag_allowed else manhattan
        
    pq = [(0 + heuristic(start, goal), 0, start)]
    dist = {start: 0}
    prev = {}
    nodes_expanded = 0
    
    while pq:
        f, g, u = heapq.heappop(pq)
        nodes_expanded += 1
        
        if u == goal: 
            break
        if g != dist[u]: 
            continue
            
        for v in grid.neighbors(u):
            w = 1.0 if (v[0]==u[0] or v[1]==u[1]) else 1.4142
            ng = g + w
            if ng < dist.get(v, float('inf')):
                dist[v] = ng
                prev[v] = u
                heapq.heappush(pq, (ng + heuristic(v, goal), ng, v))
                
    if goal not in dist: 
        return [], float('inf'), nodes_expanded
    return reconstruct_path(prev, start, goal), dist[goal], nodes_expanded