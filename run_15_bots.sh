#!/bin/bash
# Run multi-depot experiment with 15 bots
# Note: Held-Karp excluded for large K values (it's too slow for K>=30)
# If you want Held-Karp, use smaller K values (--K 10 15 20)

python3 -m exp.run_multi_depot \
    --num-depots 3 \
    --K 30 45 60 \
    --seeds 10 \
    --map-types narrow wide cross \
    --algos HybridNN2opt,NN2opt,GA

echo ""
echo "✅ Experiment completed!"
echo "📊 View results:"
echo "   cat results/multi_depot_comparison.txt"
