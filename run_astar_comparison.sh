#!/bin/bash
# Run multi-depot experiment comparing AStar with other algorithms
# This script specifically tests A* algorithm's congestion handling

echo "🔍 Running A* Algorithm Comparison for Congestion Handling..."
echo ""

python3 -m exp.run_multi_depot \
    --num-depots 8 \
    --K 20 25 30 \
    --seeds 5 \
    --map-types narrow wide \
    --algos AStar,HybridNN2opt,NN2opt,GA

echo ""
echo "✅ Experiment completed!"
echo ""
echo "📊 Generating formatted results..."
python3 generate_multi_depot_results.py

echo ""
echo "📈 Generating collision plots..."
if python3 -c "import matplotlib" 2>/dev/null; then
    python3 viz/collision_plots.py --csv results/raw/multi_depot_runs.csv --outdir figs
else
    echo "⚠️  matplotlib not found. Skipping plot generation."
    echo "   To install: pip install matplotlib numpy"
    echo "   Or: pip install -r requirements.txt"
fi

echo ""
echo "✅ All done!"
echo "📊 View results:"
echo "   cat results/multi_depot_comparison.txt"
echo ""
echo "📈 View graphs:"
echo "   ls -lh figs/*.png"
