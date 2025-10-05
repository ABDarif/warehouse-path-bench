
from __future__ import annotations
from typing import List, Tuple, Dict, Any, Callable
from .tsp_nn_2opt import nn_2opt
from .tsp_ga import ga_tsp
from .tsp_aco import aco_tsp
from .tsp_alo import alo_tsp

def hybrid_nn_2opt(dist, n, start=0, **kw):
    order, L = nn_2opt(dist, n, start=start)
    return order, L, {'base': 'NN+2opt'}

def hybrid_ga_2opt(dist, n, start=0, **kw):
    order, L = ga_tsp(dist, n, start=start, **kw)
    # optional: a quick 2-opt polish (reuse nn_2opt's two_opt if desired)
    return order, L, {'base': 'GA', 'gens': kw.get('gens', 200)}

def hybrid_aco_2opt(dist, n, start=0, **kw):
    order, L = aco_tsp(dist, n, start=start, time_budget_ms=kw.get('time_budget_ms'), **kw)
    return order, L, {'base': 'ACO', 'ants': kw.get('n_ants', 20)}

def hybrid_alo_2opt(dist, n, start=0, **kw):
    order, L = alo_tsp(dist, n, start=start, time_budget_ms=kw.get('time_budget_ms'), **kw)
    return order, L, {'base': 'ALO', 'ants': kw.get('n_ants', 30)}
