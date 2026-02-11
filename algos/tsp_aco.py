"""Ant Colony Optimization (ACO) for TSP"""
from __future__ import annotations
import random
from typing import List, Tuple, Callable

def aco_tsp(dist: Callable[[int, int], float], n: int, start: int = 0, 
            ants: int = 20, iterations: int = 50, alpha: float = 1.0, 
            beta: float = 2.0, rho: float = 0.1, seed: int = 0) -> Tuple[List[int], float]:
    if n <= 1:
        return [start], 0.0
    random.seed(seed)
    tau = [[1.0 for _ in range(n)] for _ in range(n)]
    eta = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                d = dist(i, j)
                eta[i][j] = 1.0 / d if d > 0 else 1.0
    best_tour = None
    best_length = float('inf')
    for iteration in range(iterations):
        tours = []
        tour_lengths = []
        for ant in range(ants):
            tour = [start]
            unvisited = set(range(n))
            unvisited.remove(start)
            current = start
            while unvisited:
                probs = []
                total = 0.0
                for j in unvisited:
                    p = (tau[current][j] ** alpha) * (eta[current][j] ** beta)
                    probs.append((j, p))
                    total += p
                if total == 0:
                    next_node = random.choice(list(unvisited))
                else:
                    r = random.uniform(0, total)
                    cumsum = 0.0
                    for j, p in probs:
                        cumsum += p
                        if cumsum >= r:
                            next_node = j
                            break
                    else:
                        next_node = probs[-1][0]
                tour.append(next_node)
                unvisited.remove(next_node)
                current = next_node
            length = 0.0
            for i in range(len(tour)):
                length += dist(tour[i], tour[(i+1) % len(tour)])
            tours.append(tour)
            tour_lengths.append(length)
            if length < best_length:
                best_length = length
                best_tour = tour[:]
        for i in range(n):
            for j in range(n):
                tau[i][j] *= (1.0 - rho)
        for tour, length in zip(tours, tour_lengths):
            if length > 0:
                pheromone = 1.0 / length
                for i in range(len(tour)):
                    j = (i + 1) % len(tour)
                    tau[tour[i]][tour[j]] += pheromone
                    tau[tour[j]][tour[i]] += pheromone
    return best_tour, best_length
