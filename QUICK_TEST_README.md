# Quick Test Guide

## Fast Testing Script

The `run_quick_test.sh` script runs a minimal experiment to quickly verify that collision tracking and visualization work correctly.

### Usage

```bash
# Run quick test (takes ~1-2 minutes instead of hours)
./run_quick_test.sh

# Generate collision graphs
python3 viz/collision_plots.py
```

### What It Does

1. **Runs minimal experiment:**
   - 5 bots (instead of 15/30)
   - K=10, 15 (instead of 30-120)
   - 2 seeds (instead of 10)
   - Only "narrow" map (instead of all 3)
   - All 3 algorithms: HybridNN2opt, NN2opt, GA

2. **Generates collision graphs:**
   - `collision_comparison.png` - Bar chart comparing collision counts
   - `wait_time_comparison.png` - Bar chart comparing wait times
   - `collision_vs_makespan.png` - Scatter plot showing correlation
   - `comprehensive_collision_analysis.png` - 4-panel comparison

### Expected Output

After running `./run_quick_test.sh`, you should see:
- ✅ Quick test completed!
- Results in `results/multi_depot_comparison.txt`
- CSV data in `results/raw/multi_depot_runs.csv`

After running `python3 viz/collision_plots.py`, you should see:
- 4 PNG files in `figs/` directory
- Graphs showing HybridNN2opt's superior collision handling

### Quick Verification

```bash
# Check if results were generated
ls -lh results/multi_depot_comparison.txt

# Check if graphs were generated
ls -lh figs/*.png

# View results
cat results/multi_depot_comparison.txt | grep -A 5 "COLLISION"
```

### Full Experiments

Once you've verified everything works, run the full experiments:
- `./run_15_bots.sh` - 15 bots, 10 seeds, all maps
- `./run_30_bots.sh` - 30 bots, 10 seeds, all maps

These take much longer but provide comprehensive results.
