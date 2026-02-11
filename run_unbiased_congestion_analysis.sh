#!/bin/bash
# Run unbiased congestion analysis comparing all 6 algorithms
# AStar, ACO, ALO, GA, NN2opt, HybridNN2opt

echo "🚀 Running unbiased congestion analysis..."
echo "Algorithms: AStar, ACO, ALO, GA, NN2opt, HybridNN2opt"
echo ""

python3 -m exp.run_matrix \
    --map-types narrow wide cross \
    --K 10 15 \
    --seeds 10 \
    --algos AStar,ACO,ALO,GA,NN2opt,HybridNN2opt \
    --num-bots 3 \
    --out results/raw

echo ""
echo "✅ Experiments completed!"
echo ""
echo "📊 Generating congestion analysis..."
python3 generate_single_depot_congestion.py

echo ""
echo "📈 Generating visualization graphs..."
python3 viz/single_depot_congestion_plots.py

echo ""
echo "✅ Analysis complete!"
echo ""
echo "📄 View results:"
echo "   cat results/single_depot_congestion.txt"
echo ""
echo "🖼️  View graphs:"
echo "   ls -lh figs/single_depot_congestion_*.png"
