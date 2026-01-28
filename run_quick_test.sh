#!/bin/bash
# Quick test script - runs fast to verify collision tracking works
# Uses more bots/packages to ensure collisions occur
# Much faster than full 15/30 bot experiments

python3 -m exp.run_multi_depot \
    --num-depots 8 \
    --K 20 25 \
    --seeds 3 \
    --map-types narrow \
    --algos HybridNN2opt,NN2opt,GA

echo ""
echo "✅ Quick test completed!"
echo "📊 View results:"
echo "   cat results/multi_depot_comparison.txt"
echo ""
echo "📈 Generate collision graphs:"
echo "   python3 viz/collision_plots.py"
