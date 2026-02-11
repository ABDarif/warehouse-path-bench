"""Ant Lion Optimization (ALO) for TSP"""
from __future__ import annotations
import random
from typing import List, Tuple, Callable

def alo_tsp(dist: Callable[[int, int], float], n: int, start: int = 0,
            ants: int = 30, iterations: int = 50, seed: int = 0) -> Tuple[List[int], float]:
    if n <= 1:
        return [start], 0.0
    random.seed(seed)
    ant_lions = []
    ant_lion_fitness = []
    for _ in range(ants):
        tour = list(range(n))
        random.shuffle(tour)
        if tour[0] != start:
            tour.remove(start)
            tour.insert(0, start)
        length = 0.0
        for i in range(len(tour)):
            length += dist(tour[i], tour[(i+1) % len(tour)])
        ant_lions.append(tour)
        ant_lion_fitness.append(length)
    elite_idx = min(range(len(ant_lion_fitness)), key=lambda i: ant_lion_fitness[i])
    elite_tour = ant_lions[elite_idx][:]
    elite_fitness = ant_lion_fitness[elite_idx]
    best_tour = elite_tour[:]
    best_length = elite_fitness
    for iteration in range(iterations):
        for ant_idx in range(ants):
            total_fitness = sum(ant_lion_fitness)
            if total_fitness == 0:
                selected_idx = random.randint(0, ants - 1)
            else:
                r = random.uniform(0, total_fitness)
                cumsum = 0.0
                selected_idx = 0
                for i in range(ants):
                    cumsum += ant_lion_fitness[i]
                    if cumsum >= r:
                        selected_idx = i
                        break
            selected_tour = ant_lions[selected_idx][:]
            new_tour = selected_tour[:]
            if len(new_tour) > 3:
                i, j = random.sample(range(1, len(new_tour)), 2)
                new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
            length = 0.0
            for i in range(len(new_tour)):
                length += dist(new_tour[i], new_tour[(i+1) % len(new_tour)])
            if length < ant_lion_fitness[ant_idx]:
                ant_lions[ant_idx] = new_tour
                ant_lion_fitness[ant_idx] = length
                if length < elite_fitness:
                    elite_tour = new_tour[:]
                    elite_fitness = length
                    if length < best_length:
                        best_tour = new_tour[:]
                        best_length = length
            else:
                if random.random() < 0.1:
                    ant_lions[ant_idx] = new_tour
                    ant_lion_fitness[ant_idx] = length
    return best_tour, best_length
