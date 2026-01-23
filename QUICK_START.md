# Quick Start Guide - How to Run the Code

## Step 1: Install Dependencies (if not already installed)

```bash
cd /home/abdarif/Downloads/warehouse-path-bench
pip install -r requirements.txt
```

## Step 2: Run Experiments

### Option A: Single-Depot Experiments (Compare Algorithms)

```bash
# Quick run with defaults (all algorithms, all map types, 5 seeds)
python3 -m exp.run_matrix

# Or with custom settings
python3 -m exp.run_matrix \
    --algos HybridNN2opt,NN2opt,HeldKarp,GA \
    --K 10 15 \
    --map-types narrow wide cross \
    --seeds 5 \
    --out results/raw
```

**View Results:**
```bash
# Option 1: View formatted output in terminal
python3 format_results.py results/raw/runs.csv

# Option 2: Generate formatted text file and view
python3 generate_formatted_results.py results/raw/runs.csv results/formatted_results.txt
cat results/formatted_results.txt

# Option 3: View raw CSV
python3 -m utils.view_results results/raw/runs.csv
```

### Option B: Multi-Depot Experiments (Single vs Multi-Depot Comparison)

```bash
# Run multi-depot comparison (10 seeds by default for statistical significance)
python3 -m exp.run_multi_depot \
    --K 10 15 \
    --seeds 10 \
    --num-depots 3 \
    --map-types narrow wide cross \
    --algos HybridNN2opt,NN2opt,HeldKarp,GA
```

**View Results:**
```bash
# View the formatted comparison
cat results/multi_depot_comparison.txt

# Or view raw CSV
python3 -m utils.view_results results/raw/multi_depot_runs.csv
```

## Step 3: Understanding the Output

### Single-Depot Results (`formatted_results.txt` or terminal output)
- Shows algorithm comparison for each situation (map type, K, seed)
- Highlights winners: 🏆 (best tour length), ⚡ (fastest), 📈 (best improvement)
- Overall statistics and performance by map type
- HybridNN2opt advantages section

### Multi-Depot Results (`multi_depot_comparison.txt`)
- Compares single-depot vs multi-depot makespan
- Shows improvement percentage (typically 55-60% faster)
- Average tour length per bot
- Highlights which algorithm benefits most from multi-depot

## Quick Test Run (Small Example)

If you want to test quickly with fewer runs:

```bash
# Single-depot quick test
python3 -m exp.run_matrix --K 5 --seeds 2 --map-types narrow
python3 format_results.py results/raw/runs.csv

# Multi-depot quick test
python3 -m exp.run_multi_depot --K 5 --seeds 2 --num-depots 2 --map-types narrow
cat results/multi_depot_comparison.txt
```

## Common Issues

1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Results directory not found**: It will be created automatically
3. **Import errors**: Make sure you're in the project root directory

## Full Command Reference

### Single-Depot (`exp.run_matrix`)
- `--algos`: Comma-separated list (default: "HeldKarp,NN2opt,GA")
- `--K`: Package counts, space-separated (default: [5, 10])
- `--map-types`: Map types, space-separated (default: ["narrow", "wide", "cross"])
- `--seeds`: Number of random seeds (default: 5)
- `--out`: Output directory (default: "results/raw")

### Multi-Depot (`exp.run_multi_depot`)
- `--algos`: Comma-separated list (default: "HybridNN2opt,NN2opt,HeldKarp,GA")
- `--K`: Package counts, space-separated (default: [10, 15])
- `--map-types`: Map types, space-separated (default: ["narrow", "wide", "cross"])
- `--seeds`: Number of random seeds (default: 10)
- `--num-depots`: Number of depots/bots (default: 3)
- `--out`: Output directory (default: "results/raw")
