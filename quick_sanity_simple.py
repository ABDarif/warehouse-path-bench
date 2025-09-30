# Simple working version that uses only NN2opt (avoids Held-Karp issues)
import os
import sys

print("🚀 Running simplified sanity check...")

# Use only NN2opt to avoid Held-Karp recursion issues
os.system("python -m exp.run_matrix --map-types narrow --K 5 --seeds 2 --algos NN2opt,GA --out results/raw")

# Summarize
from exp.eval import summarize
summarize("results/raw/runs.csv", "results/summary/summary.csv")

# Plot
from viz.plots import plot_bar
plot_bar("results/summary/summary.csv", "figs/bar.png")

print("✅ Done! Check figs/bar.png")