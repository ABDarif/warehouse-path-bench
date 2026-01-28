"""
Ant Colony Optimization (ACO) for TSP
Inspired by ant foraging behavior - uses pheromone trails to guide tour construction
"""

from __future__ import annotations
from typing import List, Tuple, Callable
import random
import math


def aco_tsp(dist: Callable[[int, int], float], n: int, start: int = 0, **kw) -> Tuple[List[int], float]:
    """
    Ant Colony Optimization for TSP
    
    Algorithm:
    1. Initialize pheromone trails on all edges
    2. Each ant constructs a tour probabilistically based on pheromone and distance
    3. Update pheromone trails based on tour quality
    4. Repeat for multiple iterations
    5. Return best tour found
    
    Args:
        dist: Distance function
        n: Number of waypoints
        start: Starting waypoint index
        **kw: Additional parameters:
            - num_ants: Number of ants (default: 10)
            - iterations: Number of iterations (default: 50)
            - alpha: Pheromone importance (default: 1.0)
            - beta: Distance importance (default: 2.0)
            - rho: Evaporation rate (default: 0.1)
            - q: Pheromone deposit constant (default: 100.0)
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
    num_ants = kw.get('num_ants', 10)
    iterations = kw.get('iterations', 50)
    alpha = kw.get('alpha', 1.0)  # Pheromone importance
    beta = kw.get('beta', 2.0)    # Distance importance (heuristic)
    rho = kw.get('rho', 0.1)      # Evaporation rate
    q = kw.get('q', 100.0)        # Pheromone deposit constant
    seed = kw.get('seed', 0)
    
    rng = random.Random(seed)
    
    # Precompute distance matrix first to check for zero distances
    dist_matrix = [[dist(i, j) for j in range(n)] for i in range(n)]
    
    # Find a non-zero distance for initialization
    init_dist = None
    for i in range(n):
        for j in range(i + 1, n):
            if dist_matrix[i][j] > 1e-10:  # Use small threshold
                init_dist = dist_matrix[i][j]
                break
        if init_dist is not None:
            break
    
    # Ensure init_dist is safe (avoid division by zero)
    if init_dist is None or init_dist <= 0:
        init_dist = 1.0  # Default safe value
    
    # Initialize pheromone matrix (avoid division by zero)
    # Use safe initialization: if n is very small or init_dist is problematic, use default
    safe_denom = max(n * init_dist, 1e-10)
    tau0 = 1.0 / safe_denom  # Initial pheromone level
    tau = [[tau0 for _ in range(n)] for _ in range(n)]  # Pheromone matrix
    
    # Compute heuristic (1/distance) - already have dist_matrix
    # Add small epsilon to avoid division by zero
    eta = [[1.0 / (max(dist_matrix[i][j], 1e-10)) for j in range(n)] for i in range(n)]  # Heuristic (visibility)
    
    best_tour = None
    best_length = float('inf')
    
    def construct_tour(ant_start: int) -> Tuple[List[int], float]:
        """Construct a tour for one ant"""
        tour = [ant_start]
        unvisited = set(range(n))
        unvisited.remove(ant_start)
        current = ant_start
        
        while unvisited:
            # Calculate probabilities for next city
            probabilities = []
            total = 0.0
            
            for j in unvisited:
                # Probability = (pheromone^alpha) * (heuristic^beta)
                prob = (tau[current][j] ** alpha) * (eta[current][j] ** beta)
                probabilities.append((j, prob))
                total += prob
            
            # Select next city probabilistically
            if total > 0:
                r = rng.random() * total
                cumsum = 0.0
                for j, prob in probabilities:
                    cumsum += prob
                    if r <= cumsum:
                        tour.append(j)
                        unvisited.remove(j)
                        current = j
                        break
            else:
                # Fallback: choose nearest
                j = min(unvisited, key=lambda x: dist_matrix[current][x])
                tour.append(j)
                unvisited.remove(j)
                current = j
        
        # Calculate tour length
        tour_len = sum(dist_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n))
        return tour, tour_len
    
    # Main ACO loop
    for iteration in range(iterations):
        # All ants construct tours
        ant_tours = []
        ant_lengths = []
        
        for ant in range(num_ants):
            # Each ant starts from a different city (or same if only one start)
            if ant == 0:
                ant_start = start
            else:
                # Get available start points (excluding the main start)
                available_starts = [i for i in range(n) if i != start]
                if available_starts:
                    ant_start = rng.choice(available_starts)
                else:
                    ant_start = start  # Fallback if no alternatives
            tour, length = construct_tour(ant_start)
            ant_tours.append(tour)
            ant_lengths.append(length)
            
            # Update best
            if length < best_length:
                best_length = length
                best_tour = tour[:]
        
        # Evaporate pheromone
        for i in range(n):
            for j in range(n):
                tau[i][j] *= (1.0 - rho)
        
        # Deposit pheromone (only on edges of constructed tours)
        for tour, length in zip(ant_tours, ant_lengths):
            # Avoid division by zero - ensure length is positive
            safe_length = max(length, 1e-10)
            delta_tau = q / safe_length  # More pheromone for shorter tours
            for i in range(n):
                j = tour[(i + 1) % n]
                tau[tour[i]][j] += delta_tau
                tau[j][tour[i]] += delta_tau  # Symmetric
    
    # Ensure start is at beginning
    if best_tour and best_tour[0] != start:
        # Rotate tour to start at 'start'
        idx = best_tour.index(start)
        best_tour = best_tour[idx:] + best_tour[:idx]
    
    if best_tour is None:
        # Fallback: simple nearest neighbor
        best_tour = [start]
        unvisited = set(range(n))
        unvisited.remove(start)
        current = start
        while unvisited:
            next_city = min(unvisited, key=lambda j: dist_matrix[current][j])
            best_tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        best_length = sum(dist_matrix[best_tour[i]][best_tour[(i + 1) % n]] for i in range(n))
    
    return best_tour, best_length
