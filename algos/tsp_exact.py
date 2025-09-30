from __future__ import annotations
from typing import List, Tuple
from functools import lru_cache
import time

def held_karp(dist, n, start=0, time_limit: float = 30.0):
    start_time = time.time()
    memo_stats = {'calls': 0, 'hits': 0}
    
    @lru_cache(maxsize=None)
    def dp(mask, i):
        memo_stats['calls'] += 1
        if mask == (1<<start) | (1<<i):
            return dist(start, i), start
            
        best = (float('inf'), -1)
        prev_mask = mask & ~(1<<i)
        
        for j in range(n):
            if prev_mask & (1<<j):
                cost, _ = dp(prev_mask, j)
                cand = cost + dist(j, i)
                if cand < best[0]:
                    best = (cand, j)
                    
                # Time limit check
                if time.time() - start_time > time_limit:
                    return best
                    
        return best

    full = (1<<n) - 1
    best_cost = float('inf')
    end = -1
    
    for i in range(n):
        if i == start: 
            continue
        cost, _ = dp(full, i)
        if cost < best_cost:
            best_cost, end = cost, i
            
        if time.time() - start_time > time_limit:
            break

    # Reconstruct path if we found a solution
    if best_cost < float('inf'):
        order = [end]
        mask = full
        i = end
        while i != start:
            _, j = dp(mask, i)
            order.append(j)
            mask &= ~(1<<i)
            i = j
        order.reverse()
    else:
        order = list(range(n))  # fallback
        best_cost = tour_length(order, dist)
        
    return order, best_cost, memo_stats

def tour_length(order: List[int], dist) -> float:
    s = 0.0
    for i in range(len(order)-1):
        s += dist(order[i], order[i+1])
    return s