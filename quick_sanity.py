
# Run a tiny end-to-end demo
from exp.run_matrix import main as run_main
from exp.eval import summarize
from viz.plots import plot_bar

import os
os.system("python -m exp.run_matrix --map-types narrow --K 5 --seeds 2 --algos HeldKarp,NN2opt,GA --out results/raw")
summarize("results/raw/runs.csv", "results/summary/summary.csv")
plot_bar("results/summary/summary.csv", "figs/bar.png")
print("Done. See figs/bar.png")
