# Multi-Depot, Multi-Bot Warehouse System

## Overview

This implementation extends the warehouse pathfinding system to support **multiple docking stations with multiple bots** working in parallel. This significantly improves performance by distributing work across multiple bots, reducing the overall makespan (total completion time).

## Key Features

- **Multiple Docking Stations**: Sample multiple depots from the warehouse grid
- **Proximity-Based Assignment**: Packages are assigned to the nearest depot/bot
- **Parallel Execution**: Bots work simultaneously, reducing makespan
- **Performance Comparison**: Direct comparison between single-depot and multi-depot configurations

## Results Summary

Based on experiments with HybridNN2opt algorithm:
- **Average Makespan Improvement: 55-57% faster**
- **Best Case: ~61% faster**
- **Work Distribution**: Packages split across multiple bots, reducing individual tour lengths by ~75%

## How to Run

### Basic Usage

```bash
# Run with default settings (3 depots, K=10, 3 seeds, narrow/wide/cross maps)
python3 -m exp.run_multi_depot

# Custom configuration
python3 -m exp.run_multi_depot \
    --K 15 \
    --seeds 5 \
    --num-depots 4 \
    --map-types narrow wide \
    --algos HybridNN2opt
```

### Parameters

- `--K`: Number of packages to pick (default: [10, 15])
- `--seeds`: Number of random seeds to test (default: 3)
- `--num-depots`: Number of docking stations/bots (default: 3)
- `--map-types`: Warehouse map types: narrow, wide, cross (default: all)
- `--algos`: Algorithm to use: HybridNN2opt, NN2opt, HeldKarp, GA (default: HybridNN2opt)
- `--out`: Output directory for CSV results (default: results/raw)

### View Results

```bash
# View formatted comparison
cat results/multi_depot_comparison.txt

# Or use the viewer script
python3 view_multi_depot_results.py
```

## How It Works

### 1. Multi-Depot Sampling (`exp/multi_depot_scenarios.py`)

- Finds the largest connected component in the grid
- Samples depots from different regions (first from center, then from areas far from existing depots)
- Ensures all depots are reachable

### 2. Package Assignment (`assign_packages_to_depots`)

- For each package, finds the nearest depot using A* pathfinding
- Assigns package to that depot's bot
- Ensures each depot gets at least one package (if possible)

### 3. Parallel Execution (`exp/run_multi_depot.py`)

- Each bot plans its own TSP tour using the assigned algorithm
- Bots execute in parallel (makespan = max(bot_times))
- Results compare single-depot vs multi-depot performance

## Output Format

The system generates:
1. **CSV Results** (`results/raw/multi_depot_runs.csv`): Raw data for analysis
2. **Formatted Comparison** (`results/multi_depot_comparison.txt`): Human-readable comparison

### Key Metrics

- **Makespan**: Total time until all bots finish (main performance metric)
- **Total Distance**: Sum of all bot tour distances
- **Avg Tour Len/Bot**: Average tour length per bot
- **Planning Time**: Time to compute TSP solutions
- **Time Improvement**: Percentage reduction in makespan

## Example Output

```
📍 SITUATION: Map=NARROW, K=15, Seed=0, Algo=HybridNN2opt
⏱️  MAKESPAN (time): 88.00 → 43.00 (51.14% FASTER ⚡)
📦 Work Distribution: Packages split across 4 bots
📊 Avg Tour/Bot: 20.50 (vs 88.00 for single bot)
```

## Technical Details

### Makespan Calculation

- **Single Depot**: Makespan = tour_length (sequential execution)
- **Multi-Depot (Parallel)**: Makespan = max(bot_times) (parallel execution)
- **Multi-Depot (Sequential)**: Makespan = sum(bot_times) (if sequential mode)

### Planning Time

- **Single Depot**: Time to plan one TSP tour
- **Multi-Depot (Parallel)**: max(bot_plan_times) - bots plan simultaneously
- **Multi-Depot (Sequential)**: sum(bot_plan_times) - if sequential planning

## Integration with Existing System

The multi-depot system:
- Uses the same TSP algorithms (HybridNN2opt, NN2opt, HeldKarp, GA)
- Uses the same grid and routing infrastructure
- Maintains compatibility with existing single-depot experiments
- Can be extended to support collision avoidance and real-time simulation

## Future Enhancements

Potential improvements:
- Dynamic package reassignment during execution
- Collision avoidance between bots
- Real-time SimPy simulation with multiple bots
- Load balancing algorithms for better package distribution
- Support for different bot speeds/capabilities
