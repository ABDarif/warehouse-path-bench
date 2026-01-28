#!/bin/bash
# Run congestion comparison experiments
# Compares HybridNN2opt (weighted) vs A*, ACO, ALO

set -e

echo "======================================================================"
echo "🏆 CONGESTION HANDLING COMPARISON EXPERIMENTS"
echo "======================================================================"
echo ""
echo "This will run experiments comparing:"
echo "  • HybridNN2opt (with weighted distance function)"
echo "  • AStar (multi-start greedy)"
echo "  • ACO (Ant Colony Optimization)"
echo "  • ALO (Ant Lion Optimization)"
echo ""
echo "The weighted function for HybridNN2opt includes:"
echo "  • Distance cost (α=1.0)"
echo "  • Turn penalty (β=2.0)"
echo "  • Collision risk (γ=3.0)"
echo "  • One-way violation penalty (δ=1000)"
echo "  • Dock attraction (ε=0.5)"
echo ""

# Default parameters
NUM_DEPOTS=${1:-15}
K_VALUES=${2:-"30 45 60"}
SEEDS=${3:-10}
MAP_TYPES=${4:-"narrow wide cross"}

echo "Parameters:"
echo "  Depots/Bots: $NUM_DEPOTS"
echo "  Packages (K): $K_VALUES"
echo "  Seeds: $SEEDS"
echo "  Map Types: $MAP_TYPES"
echo ""

# Run experiments
echo "Running experiments..."
python3 -m exp.run_multi_depot \
    --num-depots "$NUM_DEPOTS" \
    --K $K_VALUES \
    --seeds "$SEEDS" \
    --map-types $MAP_TYPES \
    --algos HybridNN2opt,AStar,ACO,ALO \
    --out results/raw

echo ""
echo "Generating congestion comparison..."
python3 generate_congestion_comparison.py \
    --csv results/raw/multi_depot_runs.csv \
    --out results/congestion_comparison.txt

echo ""
echo "======================================================================"
echo "✅ Experiments complete!"
echo "======================================================================"
echo ""
echo "Results saved to:"
echo "  📊 results/raw/multi_depot_runs.csv"
echo "  📈 results/congestion_comparison.txt"
echo ""
echo "View the comparison:"
echo "  cat results/congestion_comparison.txt"
echo ""
