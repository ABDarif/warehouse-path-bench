# A* Algorithm for Congestion Handling

## Overview

The A* algorithm has been integrated into the warehouse path-bench project to measure congestion handling metrics alongside other algorithms (GA, NN2opt, HybridNN2opt).

## What is A* in This Context?

The **A* TSP Algorithm** (`algos/tsp_astar.py`) uses A* pathfinding distances to construct tours using a greedy multi-start approach:

1. **Distance Calculation**: Uses A* pathfinding (already computed via `pairwise_distance_builder`) to get accurate grid-based distances
2. **Tour Construction**: Uses a greedy nearest-neighbor approach with multiple starting points
3. **Multi-Start**: Tries 3 different starting points and returns the best tour

## Key Features

- **A* Pathfinding**: Leverages A* for accurate distance calculations in grid environments
- **Multi-Start Greedy**: Tries multiple starting points for better exploration
- **Congestion Metrics**: Tracks the same metrics as other algorithms:
  - Collision count
  - Wait time (total, max, average)
  - Collision makespan
  - Tour length
  - Planning time

## How to Run

### Quick Test with A*
```bash
./run_astar_comparison.sh
```

This script runs:
- 8 bots
- 20-25-30 packages
- 5 random seeds
- Narrow and wide maps
- Algorithms: **AStar, HybridNN2opt, NN2opt, GA**

### Include A* in Other Experiments

Add `AStar` to the `--algos` parameter:

```bash
python3 -m exp.run_multi_depot \
    --num-depots 15 \
    --K 30 45 60 \
    --seeds 10 \
    --map-types narrow wide cross \
    --algos AStar,HybridNN2opt,NN2opt,GA
```

### View Results

After running experiments, view formatted results:
```bash
cat results/multi_depot_comparison.txt
```

Generate collision plots (includes A*):
```bash
python3 viz/collision_plots.py --csv results/raw/multi_depot_runs.csv --outdir figs
```

## Algorithm Comparison

A* will be compared against:

1. **HybridNN2opt**: Hybrid algorithm with multiple NN starts + extended 2-opt
2. **NN2opt**: Nearest Neighbor + 2-opt local search
3. **GA**: Genetic Algorithm with population-based search
4. **HeldKarp**: Exact algorithm (optimal but slow)

## Expected Performance

A* (multi-start greedy) is expected to:
- **Similar to NN2opt** in solution quality (both are greedy)
- **Faster than GA** (no population evolution)
- **Faster than HybridNN2opt** (no extended 2-opt)
- **Better than basic NN** (multi-start exploration)

## Files Modified/Created

1. **`algos/tsp_astar.py`** (NEW): A* TSP algorithm implementation
2. **`exp/run_multi_depot.py`**: Added AStar to `plan_sequence()`
3. **`viz/collision_plots.py`**: Added AStar color/marker support
4. **`run_astar_comparison.sh`** (NEW): Dedicated script for A* comparison

## Technical Details

### Algorithm Implementation

```python
def astar_tsp(dist, n, start=0, **kw):
    """
    A*-based multi-start greedy TSP
    
    - Uses A* distances (already computed)
    - Tries 3 starting points
    - Greedy nearest-neighbor construction
    - Returns best tour
    """
```

### Integration Point

The A* algorithm is integrated at the same level as other TSP algorithms:
- Called via `plan_sequence('AStar', dist_fn, n, start, seed)`
- Receives the same distance function (A* pathfinding-based)
- Returns `(tour_order, tour_length)` like other algorithms
- Subject to same collision tracking and metrics collection

## Notes

- A* pathfinding is already used by **all algorithms** for distance calculation
- The A* TSP algorithm is a **tour construction method**, not a pathfinding method
- The name "AStar" refers to using A* distances in a greedy TSP construction
- For congestion handling, A* will show how a simple greedy approach compares to more sophisticated methods
