#!/bin/bash
# Quick test script for single-depot experiments
# Runs fast to verify single depot analysis works

python3 -m exp.run_matrix \
    --map-types narrow \
    --K 10 15 \
    --seeds 3 \
    --algos HybridNN2opt,NN2opt,GA,HeldKarp

echo ""
echo "✅ Single-depot experiment completed!"
echo "📊 Generate formatted results:"
echo "   python3 generate_single_depot_results.py"
echo ""
echo "📈 Generate graphs:"
echo "   python3 viz/single_depot_plots.py"
