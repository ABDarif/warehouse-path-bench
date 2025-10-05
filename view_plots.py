#!/usr/bin/env python3
"""
Simple Plot Viewer - Displays information about generated plots
"""

import os
import matplotlib.pyplot as plt
from PIL import Image
import sys

def show_plot_info():
    """Show information about generated plots."""
    
    figs_dir = "figs"
    if not os.path.exists(figs_dir):
        print("No figs directory found. Run experiments first!")
        return
    
    plot_files = [f for f in os.listdir(figs_dir) if f.endswith('.png')]
    
    if not plot_files:
        print("No plot files found in figs directory.")
        return
    
    print("Generated Performance Analysis Plots")
    print("=" * 50)
    
    # Show the main plots (according to feedback)
    main_plots = {
        "optimization_rate.png": "Optimization Rate Comparison (with values)",
        "planning_time_vs_opt.png": "Planning Time vs Optimization Rate (with legends)",
        "planning_time_vs_success_rate.png": "Planning Time vs Success Rate (with proper legends)",
        "full_planning_time_vs_opt.png": "Full Planning Time Including Replanning"
    }
    
    print("\nMain Analysis Plots (per Research Assistant feedback):")
    for filename, description in main_plots.items():
        filepath = os.path.join(figs_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  [OK] {filename}")
            print(f"     Description: {description}")
            print(f"     Size: {size:,} bytes")
        else:
            print(f"  [MISSING] {filename} - Not found")
    
    print(f"\nAll plot files in {figs_dir}:")
    for i, filename in enumerate(plot_files, 1):
        filepath = os.path.join(figs_dir, filename)
        size = os.path.getsize(filepath)
        print(f"  {i}. {filename} ({size:,} bytes)")
    
    print(f"\nTo view plots:")
    print(f"  1. Open Windows Explorer: explorer {os.path.abspath(figs_dir)}")
    print(f"  2. Or open files directly with your default image viewer")
    print(f"  3. Or use any image viewer application")

def display_plot_matplotlib(filename):
    """Display a plot using matplotlib (if possible)."""
    try:
        filepath = os.path.join("figs", filename)
        if os.path.exists(filepath):
            img = plt.imread(filepath)
            plt.figure(figsize=(10, 6))
            plt.imshow(img)
            plt.axis('off')
            plt.title(f"Plot: {filename}")
            plt.tight_layout()
            plt.show()
            return True
        else:
            print(f"File {filename} not found")
            return False
    except Exception as e:
        print(f"Error displaying {filename}: {e}")
        return False

def main():
    show_plot_info()
    
    if len(sys.argv) > 1:
        # Try to display specific plot
        filename = sys.argv[1]
        print(f"\nAttempting to display {filename}...")
        display_plot_matplotlib(filename)

if __name__ == "__main__":
    main()
