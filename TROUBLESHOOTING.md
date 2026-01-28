# Troubleshooting Guide

## "Skipping..." Messages

When you see messages like:
```
⚠️  Skipping narrow K=60 seed=0 algo=HeldKarp: ...
```

This means that specific run failed and was skipped. The experiment continues with other runs.

### Common Causes:

#### 1. **GA Algorithm with Small Tours (Fixed)**
- **Problem**: GA's crossover/mutation requires at least 4 waypoints (depot + 3 packages)
- **When it happened**: Bots with 0-2 packages (total waypoints < 4) caused `random.sample()` to fail
- **Status**: ✅ **FIXED** - Now handles small tours gracefully

#### 2. **Held-Karp Timeout**
- **Problem**: Held-Karp has exponential complexity O(2^n × n²) and a 30-second time limit
- **When it happens**: With large K values (K ≥ 30), Held-Karp may timeout or fail
- **Solution**: 
  - Use smaller K values for Held-Karp (K ≤ 15)
  - Or exclude Held-Karp from large experiments: `--algos HybridNN2opt,NN2opt,GA`

#### 2. **Insufficient Free Cells**
- **Problem**: Not enough free cells in the grid for depots + packages
- **When it happens**: Very large `--num-depots` + large `--K` values
- **Solution**: Reduce `--num-depots` or `--K` values

#### 3. **Memory Issues**
- **Problem**: Held-Karp uses significant memory for large problems
- **When it happens**: K ≥ 25-30
- **Solution**: Use heuristic algorithms (NN2opt, GA, HybridNN2opt) for large problems

### Recommended Configurations:

#### For 15 Bots:
```bash
# Option 1: Exclude Held-Karp (recommended for large K)
python3 -m exp.run_multi_depot \
    --num-depots 15 \
    --K 30 45 60 \
    --seeds 10 \
    --map-types narrow wide cross \
    --algos HybridNN2opt,NN2opt,GA

# Option 2: Use smaller K for Held-Karp
python3 -m exp.run_multi_depot \
    --num-depots 15 \
    --K 10 15 20 \
    --seeds 10 \
    --map-types narrow wide cross \
    --algos HybridNN2opt,NN2opt,HeldKarp,GA
```

#### For 30 Bots:
```bash
# Recommended: Exclude Held-Karp
python3 -m exp.run_multi_depot \
    --num-depots 30 \
    --K 60 90 120 \
    --seeds 10 \
    --map-types narrow wide cross \
    --algos HybridNN2opt,NN2opt,GA
```

### Understanding the Results:

- **Skipped runs are not included** in the final statistics
- The experiment continues with successful runs
- You'll still get valid comparisons for algorithms that completed
- Check the CSV file to see which runs succeeded/failed

### Checking What Failed:

```bash
# View the raw CSV to see which runs completed
python3 -m utils.view_results results/raw/multi_depot_runs.csv

# Or check the formatted results
cat results/multi_depot_comparison.txt
```
