#!/bin/bash
# Quick congestion comparison test
# Fast execution for back-to-back testing
# Compares: HybridNN2opt, NN2opt, GA, AStar, ACO, ALO

set -e

echo "======================================================================"
echo "⚡ QUICK CONGESTION COMPARISON TEST"
echo "======================================================================"
echo ""
echo "Algorithms: HybridNN2opt, NN2opt, GA, AStar, ACO, ALO"
echo "Parameters: Small, fast execution"
echo ""

# Quick test parameters (small for fast execution)
NUM_DEPOTS=5
K_VALUES="10 15"
SEEDS=3
MAP_TYPES="narrow"

echo "Test Parameters:"
echo "  Depots/Bots: $NUM_DEPOTS"
echo "  Packages (K): $K_VALUES"
echo "  Seeds: $SEEDS"
echo "  Map Types: $MAP_TYPES"
echo ""
echo "This will run quickly for back-to-back testing..."
echo ""

# Run experiments
echo "Running quick experiments..."
python3 -m exp.run_multi_depot \
    --num-depots "$NUM_DEPOTS" \
    --K $K_VALUES \
    --seeds "$SEEDS" \
    --map-types $MAP_TYPES \
    --algos HybridNN2opt,NN2opt,GA,AStar,ACO,ALO \
    --out results/raw 2>&1 | grep -v "Skipping" || true

echo ""
echo "Generating congestion comparison..."
python3 generate_congestion_comparison.py \
    --csv results/raw/multi_depot_runs.csv \
    --out results/congestion_comparison.txt

echo ""
echo "======================================================================"
echo "✅ Quick test complete!"
echo "======================================================================"
echo ""
echo "Results:"
echo "  📊 results/raw/multi_depot_runs.csv"
echo "  📈 results/congestion_comparison.txt"
echo ""
echo "View comparison:"
echo "  cat results/congestion_comparison.txt"
echo ""
