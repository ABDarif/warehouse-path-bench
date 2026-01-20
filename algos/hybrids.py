
from __future__ import annotations
from typing import List, Tuple, Dict, Any, Callable
from .tsp_nn_2opt import nearest_neighbor, two_opt, tour_length
from .tsp_ga import ga_tsp

def hybrid_nn_2opt(dist, n, start=0, **kw):
    """
    Hybrid-NN2opt: True hybrid algorithm that runs multiple NN starts + extended 2-opt
    
    Strategy:
    1. Run Nearest Neighbor from multiple starting points (exploration)
    2. Select best initial solution
    3. Apply extended 2-opt with more iterations (exploitation)
    
    This takes MORE time than NN2opt but provides:
    - Better solution quality (lower tour length)
    - More consistent results across runs
    - Better convergence (larger improvement from initial)
    """
    max_nn_starts = kw.get('max_nn_starts', 3)  # Try multiple starting points
    max_swaps = kw.get('max_swaps', 3000)  # More swaps than regular NN2opt (1000)
    max_time = kw.get('max_time', 3.0)  # More time than regular NN2opt (1.0)
    
    # Step 1: Run NN from multiple starting points
    best_nn_tour = None
    best_nn_len = float('inf')
    
    # Try different starting points (including the given start)
    start_points = [start]
    if n > 2:
        # Add a couple more starting points for diversity
        mid_point = n // 2
        if mid_point != start:
            start_points.append(mid_point)
        if n > 4:
            quarter_point = n // 4
            if quarter_point != start and quarter_point != mid_point:
                start_points.append(quarter_point)
    
    # Limit to max_nn_starts
    start_points = start_points[:max_nn_starts]
    
    for sp in start_points:
        nn_tour = nearest_neighbor(dist, n, start=sp)
        nn_len = tour_length(nn_tour, dist)
        if nn_len < best_nn_len:
            best_nn_len = nn_len
            best_nn_tour = nn_tour
    
    # Step 2: Apply extended 2-opt with more iterations
    if best_nn_tour is None:
        best_nn_tour = nearest_neighbor(dist, n, start=start)
        best_nn_len = tour_length(best_nn_tour, dist)
    
    # Extended 2-opt with more swaps and time
    improved_tour = two_opt(best_nn_tour, dist, max_swaps=max_swaps, max_time=max_time)
    improved_len = tour_length(improved_tour, dist)
    
    return improved_tour, improved_len

def hybrid_ga_2opt(dist, n, start=0, **kw):
    order, L = ga_tsp(dist, n, start=start, **kw)
    # optional: a quick 2-opt polish (reuse nn_2opt's two_opt if desired)
    return order, L, {'base': 'GA', 'gens': kw.get('gens', 200)}
