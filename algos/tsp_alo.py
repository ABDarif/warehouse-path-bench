"""
Ant Lion Optimization (ALO) for TSP
Inspired by ant lion hunting behavior - uses random walks and trapping mechanism
"""

from __future__ import annotations
from typing import List, Tuple, Callable
import random
import math


def alo_tsp(dist: Callable[[int, int], float], n: int, start: int = 0, **kw) -> Tuple[List[int], float]:
    """
    Ant Lion Optimization for TSP
    
    Algorithm:
    1. Initialize population of ant lions (solutions)
    2. Each ant performs random walk around ant lion
    3. Ant lions trap ants and update positions based on better solutions
    4. Elitism: keep best ant lion
    5. Repeat for multiple iterations
    
    Args:
        dist: Distance function
        n: Number of waypoints
        start: Starting waypoint index
        **kw: Additional parameters:
            - pop_size: Population size (default: 20)
            - iterations: Number of iterations (default: 100)
            - seed: Random seed (default: 0)
    
    Returns:
        Tuple of (best_tour_order, best_tour_length)
    """
    if n <= 1:
        return [start], 0.0
    
    # Handle very small tours (n == 2)
    if n == 2:
        other = 1 - start
        d1 = dist(start, other)
        d2 = dist(other, start)
        tour = [start, other]
        tour_len = max(d1 + d2, 0.0)  # Ensure non-negative
        return tour, tour_len
    
    # Handle n == 3 (very small, use simple greedy)
    if n == 3:
        # Simple greedy for 3 cities
        tour = [start]
        unvisited = [i for i in range(n) if i != start]
        current = start
        while unvisited:
            next_city = min(unvisited, key=lambda j: dist(current, j))
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        tour_len = sum(dist(tour[i], tour[(i + 1) % n]) for i in range(n))
        return tour, max(tour_len, 0.0)
    
    # Parameters
    pop_size = kw.get('pop_size', 20)
    iterations = kw.get('iterations', 100)
    seed = kw.get('seed', 0)
    
    rng = random.Random(seed)
    
    # Precompute distance matrix
    dist_matrix = [[dist(i, j) for j in range(n)] for i in range(n)]
    
    def tour_length(tour: List[int]) -> float:
        """Calculate tour length"""
        if len(tour) < 2:
            return 0.0
        return sum(dist_matrix[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))
    
    def random_tour() -> List[int]:
        """Generate random tour starting from 'start'"""
        tour = [start]
        remaining = [i for i in range(n) if i != start]
        rng.shuffle(remaining)
        tour.extend(remaining)
        return tour
    
    def two_opt_improve(tour: List[int], max_swaps: int = 10) -> List[int]:
        """Apply 2-opt local search"""
        improved = tour[:]
        best_len = tour_length(improved)
        
        for _ in range(max_swaps):
            improved_found = False
            for i in range(len(improved)):
                for j in range(i + 2, len(improved) + (1 if i > 0 else 0)):
                    # Try swapping edges
                    new_tour = improved[:i+1] + improved[i+1:j+1][::-1] + improved[j+1:]
                    new_len = tour_length(new_tour)
                    if new_len < best_len:
                        improved = new_tour
                        best_len = new_len
                        improved_found = True
                        break
                if improved_found:
                    break
            if not improved_found:
                break
        
        return improved
    
    # Initialize ant lion population
    ant_lions = []
    ant_lion_lengths = []
    
    for _ in range(pop_size):
        tour = random_tour()
        tour = two_opt_improve(tour, max_swaps=5)  # Light improvement
        ant_lions.append(tour)
        ant_lion_lengths.append(tour_length(tour))
    
    # Find best (elite)
    elite_idx = min(range(pop_size), key=lambda i: ant_lion_lengths[i])
    elite_tour = ant_lions[elite_idx][:]
    elite_length = ant_lion_lengths[elite_idx]
    
    # Main ALO loop
    for iteration in range(iterations):
        # Normalize iteration (0 to 1)
        I = 1.0 if iteration == 0 else 1 + 100 * (iteration / iterations)
        
        # Each ant performs random walk around an ant lion
        ants = []
        ant_lengths = []
        
        for i in range(pop_size):
            # Select ant lion (roulette wheel or random)
            if rng.random() < 0.5:
                # Use elite
                selected_lion = elite_tour[:]
            else:
                # Use random ant lion
                selected_idx = rng.randrange(pop_size)
                selected_lion = ant_lions[selected_idx][:]
            
            # Random walk: apply mutations to create ant
            ant = selected_lion[:]
            
            # Mutation operations
            if rng.random() < 0.3:
                # Swap two random cities (except start)
                if len(ant) > 2:
                    i1, i2 = rng.sample(range(1, len(ant)), 2)
                    ant[i1], ant[i2] = ant[i2], ant[i1]
            
            if rng.random() < 0.3:
                # Reverse a segment
                if len(ant) > 2:
                    i1, i2 = sorted(rng.sample(range(1, len(ant)), 2))
                    ant[i1:i2+1] = ant[i1:i2+1][::-1]
            
            # Light local search
            ant = two_opt_improve(ant, max_swaps=3)
            
            ants.append(ant)
            ant_lengths.append(tour_length(ant))
        
        # Update ant lions (if ant is better, replace ant lion)
        for i in range(pop_size):
            if ant_lengths[i] < ant_lion_lengths[i]:
                ant_lions[i] = ants[i][:]
                ant_lion_lengths[i] = ant_lengths[i]
        
        # Update elite
        current_best_idx = min(range(pop_size), key=lambda i: ant_lion_lengths[i])
        if ant_lion_lengths[current_best_idx] < elite_length:
            elite_tour = ant_lions[current_best_idx][:]
            elite_length = ant_lion_lengths[current_best_idx]
    
    # Ensure start is at beginning
    if elite_tour[0] != start:
        idx = elite_tour.index(start)
        elite_tour = elite_tour[idx:] + elite_tour[:idx]
    
    return elite_tour, elite_length
