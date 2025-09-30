from __future__ import annotations
from typing import List, Tuple, Callable
import math, random, time

def nearest_neighbor(dist, n, start=0):
    unvisited = set(range(n)); unvisited.remove(start)
    tour = [start]
    cur = start
    while unvisited:
        nxt = min(unvisited, key=lambda j: dist(cur, j))
        tour.append(nxt); unvisited.remove(nxt); cur = nxt
    return tour

def two_opt(tour: List[int], dist, max_swaps: int = 1000, max_time: float = 1.0) -> List[int]:
    best = tour[:]
    best_len = tour_length(best, dist)
    improved = True
    swaps = 0
    start_time = time.time()
    
    while improved and swaps < max_swaps and (time.time() - start_time) < max_time:
        improved = False
        for i in range(1, len(best)-2):
            for j in range(i+1, len(best)-1):
                # Check if swap would improve
                old_segment = dist(best[i-1], best[i]) + dist(best[j], best[j+1])
                new_segment = dist(best[i-1], best[j]) + dist(best[i], best[j+1])
                
                if new_segment < old_segment:
                    best[i:j+1] = reversed(best[i:j+1])
                    best_len += new_segment - old_segment
                    improved = True
                    swaps += 1
                    break
            if improved:
                break
    return best

def tour_length(order: List[int], dist) -> float:
    s = 0.0
    for i in range(len(order)-1):
        s += dist(order[i], order[i+1])
    return s

def nn_2opt(dist, n, start=0, max_swaps: int = 1000, max_time: float = 1.0):
    nn = nearest_neighbor(dist, n, start=start)
    nn_len = tour_length(nn, dist)
    improved = two_opt(nn, dist, max_swaps=max_swaps, max_time=max_time)
    improved_len = tour_length(improved, dist)
    
    # Assertion: 2-opt never worse than NN
    assert improved_len <= nn_len + 1e-6, f"2-opt made it worse: {improved_len} > {nn_len}"
    
    return improved, improved_len