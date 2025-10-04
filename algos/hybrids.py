
from __future__ import annotations
from typing import List, Tuple, Dict, Any, Callable
from .tsp_nn_2opt import nn_2opt
from .tsp_ga import ga_tsp

def hybrid_nn_2opt(dist, n, start=0, **kw):
    order, L = nn_2opt(dist, n, start=start)
    return order, L, {'base': 'NN+2opt'}

def hybrid_ga_2opt(dist, n, start=0, **kw):
    order, L = ga_tsp(dist, n, start=start, **kw)
    # optional: a quick 2-opt polish (reuse nn_2opt's two_opt if desired)
    return order, L, {'base': 'GA', 'gens': kw.get('gens', 200)}
