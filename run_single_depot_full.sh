#!/bin/bash
# Full single-depot experiment with all map types (narrow, wide, cross)
# This provides complete congestion analysis

python3 -m exp.run_matrix \
    --map-types narrow wide cross \
    --K 10 15 \
    --seeds 5 \
    --algos HybridNN2opt,NN2opt,GA,HeldKarp

echo ""
echo "✅ Full single-depot experiment completed!"
echo "📊 Generate formatted results:"
echo "   python3 generate_single_depot_results.py"
echo "   python3 generate_single_depot_congestion.py"
echo ""
echo "📈 Generate graphs:"
echo "   python3 viz/single_depot_plots.py"
echo "   python3 viz/single_depot_congestion_plots.py"
