#!/bin/bash
# Quick test script for multi-bot single-depot experiments with collision tracking

echo "🚀 Running Multi-Bot Single-Depot Test..."
echo "   This will test collision tracking with 3 bots from a single depot"
echo ""

# Run experiments with 3 bots
python3 -m exp.run_matrix \
    --num-bots 3 \
    --map-types narrow wide \
    --K 15 20 \
    --seeds 3 \
    --algos HybridNN2opt,NN2opt,GA

echo ""
echo "✅ Experiments completed!"
echo ""
echo "📊 Generate collision analysis:"
echo "   python3 generate_single_depot_congestion.py"
echo ""
echo "📈 Generate collision graphs:"
echo "   python3 viz/single_depot_congestion_plots.py"
echo ""
echo "📄 View results:"
echo "   cat results/single_depot_congestion.txt | grep -A 20 'COLLISION ANALYSIS'"
echo ""
echo "🔍 Check collision data in CSV:"
echo "   awk -F',' 'NR>1 && \$13>0 {print \$1, \$4, \$13, \$14}' results/raw/runs.csv | head -10"
