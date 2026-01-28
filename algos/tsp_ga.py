
from __future__ import annotations
from typing import List, Tuple, Callable, Dict
import random

def ox_crossover(p1: List[int], p2: List[int]) -> List[int]:
    n = len(p1)
    # Need at least 4 elements to sample 2 from range(1, n-1)
    if n < 4:
        # For small tours, just return one of the parents
        return p1[:]
    a,b = sorted(random.sample(range(1,n-1), 2))
    child = [None]*n
    child[a:b] = p1[a:b]
    fill = [x for x in p2 if x not in child]
    j = 0
    for i in range(n):
        if child[i] is None:
            child[i] = fill[j]; j += 1
    return child

def mutate_swap(p: List[int], pm: float) -> None:
    if random.random() < pm:
        # Need at least 4 elements to swap two from middle
        if len(p) < 4:
            return  # Can't mutate small tours
        i,j = random.sample(range(1, len(p)-1), 2)
        p[i],p[j] = p[j],p[i]

def length(order: List[int], dist) -> float:
    s = 0.0
    for i in range(len(order)-1):
        s += dist(order[i], order[i+1])
    return s

def ga_tsp(dist, n, start=0, pop=48, gens=200, pc=0.9, pm=0.2, seed=0):
    rng = random.Random(seed)
    random.seed(seed)
    base = [i for i in range(n)]
    # keep start at index 0
    def mk_ind():
        mid = base[1:]
        rng.shuffle(mid)
        return [start] + mid

    P = [mk_ind() for _ in range(pop)]
    scores = [length(ind, dist) for ind in P]
    best = min(zip(scores, P))[1]

    for _ in range(gens):
        # selection: tournament
        parents = []
        for _ in range(pop):
            i,j = rng.randrange(pop), rng.randrange(pop)
            parents.append(P[i] if scores[i] < scores[j] else P[j])

        # crossover
        children = []
        for i in range(0, pop, 2):
            c1,c2 = parents[i], parents[i+1]
            if rng.random() < pc:
                c1 = ox_crossover(c1, c2)
                c2 = ox_crossover(c2, c1)
            mutate_swap(c1, pm); mutate_swap(c2, pm)
            children.extend([c1,c2])

        P = children
        scores = [length(ind, dist) for ind in P]
        cur_best = min(zip(scores, P))[1]
        if length(cur_best, dist) < length(best, dist):
            best = cur_best

    return best, length(best, dist)
