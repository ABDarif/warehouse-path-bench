"""
Collision Tracking and Simulation for Multi-Bot Warehouse Execution
Tracks collisions, wait times, and makespan when multiple bots operate in parallel
"""

from __future__ import annotations
import simpy
from dataclasses import dataclass, field
from typing import Dict, Tuple, List
from collections import defaultdict
from .grid import Grid, Pos
from .routing import astar


@dataclass
class CollisionStats:
    """Statistics about collisions during multi-bot execution"""
    total_collisions: int = 0
    total_wait_time: float = 0.0
    max_wait_time: float = 0.0
    wait_events: List[float] = field(default_factory=list)
    collision_locations: List[Pos] = field(default_factory=list)
    bot_wait_times: Dict[int, float] = field(default_factory=lambda: defaultdict(float))
    makespan: float = 0.0


@dataclass
class CellRes:
    """Resource representing a cell that can be occupied by one bot"""
    pos: Pos
    res: simpy.Resource


def build_cell_resources(env: simpy.Environment, grid: Grid, cap: int = 1):
    """Build resource pool for each free cell in the grid"""
    return {p: CellRes(p, simpy.Resource(env, capacity=cap)) for p in grid.free_cells()}


def follow_path_with_tracking(env: simpy.Environment, bot_id: int, path: List[Pos], 
                              cells: Dict[Pos, CellRes], step_time: float,
                              stats: CollisionStats):
    """
    Follow a path and track collisions/wait times
    
    Args:
        env: SimPy environment
        bot_id: ID of the bot
        path: List of positions to follow
        cells: Dictionary of cell resources
        step_time: Time to move one step
        stats: CollisionStats object to update
    """
    if not path:
        return
    
    # Enter first cell
    first = path[0]
    if first not in cells:
        return  # Invalid cell
    
    req = cells[first].res.request()
    wait_start = env.now
    yield req  # Wait if cell is occupied (collision!)
    wait_duration = env.now - wait_start
    
    if wait_duration > 0:
        stats.total_collisions += 1
        stats.total_wait_time += wait_duration
        stats.wait_events.append(wait_duration)
        stats.bot_wait_times[bot_id] += wait_duration
        stats.collision_locations.append(first)
        if wait_duration > stats.max_wait_time:
            stats.max_wait_time = wait_duration
    
    cur = first
    
    # Move through remaining path
    for nxt in path[1:]:
        if nxt not in cells:
            continue
        
        # Move to next cell (takes time)
        yield env.timeout(step_time)
        
        # Release current cell
        cells[cur].res.release(req)
        
        # Request next cell
        req = cells[nxt].res.request()
        wait_start = env.now
        yield req  # Wait if next cell is occupied
        wait_duration = env.now - wait_start
        
        if wait_duration > 0:
            stats.total_collisions += 1
            stats.total_wait_time += wait_duration
            stats.wait_events.append(wait_duration)
            stats.bot_wait_times[bot_id] += wait_duration
            stats.collision_locations.append(nxt)
            if wait_duration > stats.max_wait_time:
                stats.max_wait_time = wait_duration
        
        cur = nxt
    
    # Release final cell when bot finishes
    if cur in cells:
        cells[cur].res.release(req)


def convert_tour_to_paths(grid: Grid, order: List[int], waypoints: List[Pos]) -> List[List[Pos]]:
    """
    Convert a TSP tour order to a list of paths between waypoints
    
    Args:
        grid: Warehouse grid
        order: TSP tour order (list of waypoint indices)
        waypoints: List of waypoint positions
    
    Returns:
        List of paths, where each path is a list of positions from one waypoint to the next
    """
    paths = []
    for i in range(len(order)):
        start_idx = order[i]
        end_idx = order[(i + 1) % len(order)]
        
        start_pos = waypoints[start_idx]
        end_pos = waypoints[end_idx]
        
        # Get A* path between waypoints
        path, _, _ = astar(grid, start_pos, end_pos, diag_allowed=True)
        if path:
            paths.append(path)
    
    return paths


def simulate_multi_bot_execution(grid: Grid, bot_tours: List[List[List[Pos]]], 
                                 step_time: float = 0.2) -> Tuple[float, CollisionStats]:
    """
    Simulate multiple bots executing their tours in parallel with collision tracking
    
    Args:
        grid: Warehouse grid
        bot_tours: List of tours, where each tour is a list of paths (one per bot)
        step_time: Time to move one step (default 0.2 seconds)
    
    Returns:
        Tuple of (makespan, CollisionStats)
    """
    env = simpy.Environment()
    cells = build_cell_resources(env, grid, cap=1)
    stats = CollisionStats()
    
    def bot_process(bot_id: int, tour_paths: List[List[Pos]]):
        """Process for a single bot executing its tour"""
        for path in tour_paths:
            yield env.process(follow_path_with_tracking(
                env, bot_id, path, cells, step_time, stats
            ))
    
    # Start all bots simultaneously
    for bot_id, tour_paths in enumerate(bot_tours):
        if tour_paths:  # Only start bots with actual tours
            env.process(bot_process(bot_id, tour_paths))
    
    # Run simulation
    env.run()
    
    stats.makespan = env.now
    return stats.makespan, stats
