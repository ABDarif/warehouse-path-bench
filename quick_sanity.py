<<<<<<< HEAD
# Run a tiny end-to-end demo with error handling
import os
import sys
import time

def run_sanity_check():
    print("🚀 Running quick sanity check...")
    
    # Step 1: Run experiment
    print("1. Running experiments...")
    try:
        os.system("python -m exp.run_matrix --map-types narrow --K 5 --seeds 2 --algos HeldKarp,NN2opt,GA --out results/raw")
        print("   ✅ Experiments completed")
    except Exception as e:
        print(f"   ❌ Experiments failed: {e}")
        return False
    
    # Wait a moment for file writing
    time.sleep(1)
    
    # Step 2: Check if results file exists and has data
    results_file = "results/raw/runs.csv"
    if not os.path.exists(results_file):
        print("   ❌ Results file not found")
        return False
    
    # Count lines in results file
    with open(results_file, 'r') as f:
        lines = f.readlines()
    
    if len(lines) <= 1:  # Only header or empty
        print("   ❌ Results file is empty")
        return False
    
    print(f"   ✅ Results file has {len(lines)-1} data rows")
    
    # Step 3: Summarize results
    print("2. Summarizing results...")
    try:
        from exp.eval import summarize
        summarize("results/raw/runs.csv", "results/summary/summary.csv")
        print("   ✅ Summary completed")
    except Exception as e:
        print(f"   ❌ Summary failed: {e}")
        return False
    
    # Step 4: Create plots
    print("3. Generating plots...")
    try:
        from viz.plots import plot_bar
        plot_bar("results/summary/summary.csv", "figs/bar.png")
        print("   ✅ Plot generated")
    except Exception as e:
        print(f"   ❌ Plot failed: {e}")
        # Continue anyway
    
    print("🎉 Sanity check completed!")
    print("📊 See results/raw/runs.csv for raw data")
    print("📈 See figs/bar.png for visualization")
    return True

if __name__ == "__main__":
    success = run_sanity_check()
    if not success:
        print("\n💡 Tip: Run the individual commands manually to debug:")
        print("  python -m exp.run_matrix --map-types narrow --K 5 --seeds 1 --algos NN2opt --out results/raw")
        print("  python -m exp.eval --raw results/raw --out results/summary/summary.csv")
        print("  python -m viz.plots --summary results/summary/summary.csv --outdir figs")
=======

# Run a tiny end-to-end demo
from exp.run_matrix import main as run_main
from exp.eval import summarize
from viz.plots import plot_bar

import os
os.system("python -m exp.run_matrix --map-types narrow --K 5 --seeds 2 --algos HeldKarp,NN2opt,GA --out results/raw")
summarize("results/raw/runs.csv", "results/summary/summary.csv")
plot_bar("results/summary/summary.csv", "figs/bar.png")
print("Done. See figs/bar.png")
>>>>>>> 09fc1e88cd8fbcfa8e717e118d7ebe9b1474bb02
