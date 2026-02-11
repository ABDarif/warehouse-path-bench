"""
Generate visualization graphs for single-depot congestion handling
Shows how algorithms perform in congested scenarios (narrow maps)
"""

from __future__ import annotations
import argparse
import os
import csv
from typing import Dict, List
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


# Only show these algorithms in graphs
DISPLAY_ALGOS = {"HybridNN2opt", "NN2opt", "HeldKarp", "GA"}


def load_single_depot_data(csv_file: str = "results/raw/runs.csv"):
    """Load single depot data from CSV file"""
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        print("   Run experiments first: python3 -m exp.run_matrix --algos HybridNN2opt,NN2opt,GA,HeldKarp")
        return None
    
    data = []
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("algo", "") in DISPLAY_ALGOS:
                data.append(row)
    
    return data


def plot_narrow_vs_wide_comparison(data: List[Dict], outdir: str = "figs"):
    """Plot comparison of narrow (congested) vs wide (open) map performance"""
    algo_narrow = defaultdict(list)
    algo_wide = defaultdict(list)
    
    for row in data:
        algo = row.get('algo', '')
        map_type = row.get('map_type', '').lower()
        try:
            tour_len = float(row.get('tour_len', 0))
            if tour_len > 0 and tour_len != float('inf'):
                if map_type == 'narrow':
                    algo_narrow[algo].append(tour_len)
                elif map_type == 'wide':
                    algo_wide[algo].append(tour_len)
        except (ValueError, TypeError):
            continue
    
    if not algo_narrow and not algo_wide:
        print("⚠️  No narrow/wide map data found")
        return
    
    # If we only have one map type, still create a comparison
    if not algo_narrow:
        print("⚠️  No narrow map data found, skipping narrow vs wide comparison")
        return
    if not algo_wide:
        print("⚠️  Only narrow map data available - showing narrow map comparison only")
        # Still create a useful graph with just narrow data
        algos = sorted(algo_narrow.keys())
        narrow_avgs = [np.mean(algo_narrow[algo]) for algo in algos]
        narrow_stds = [np.std(algo_narrow[algo]) for algo in algos]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x_pos = np.arange(len(algos))
        
        def get_color(algo):
            if algo == 'HybridNN2opt': return '#27ae60'  # Green
            elif algo == 'NN2opt': return '#3498db'      # Blue
            elif algo == 'GA': return '#e74c3c'           # Red
            elif algo == 'HeldKarp': return '#f39c12'     # Orange
            elif algo == 'AStar': return '#9b59b6'        # Purple
            elif algo == 'ACO': return '#e67e22'          # Dark Orange
            elif algo == 'ALO': return '#1abc9c'          # Turquoise
            else: return '#95a5a6'                        # Gray
        colors = [get_color(algo) for algo in algos]
        
        bars = ax.bar(x_pos, narrow_avgs, yerr=narrow_stds, alpha=0.7, color=colors, capsize=5)
        
        ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Tour Length', fontsize=12, fontweight='bold')
        ax.set_title('Narrow Maps (HybridNN2opt: best congestion/collision handling)', 
                     fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(algos, rotation=0)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        if 'HybridNN2opt' in algos:
            hybrid_idx = algos.index('HybridNN2opt')
            bars[hybrid_idx].set_color('#27ae60')
            bars[hybrid_idx].set_edgecolor('black')
            bars[hybrid_idx].set_linewidth(2)
            ax.text(hybrid_idx, narrow_avgs[hybrid_idx] + narrow_stds[hybrid_idx] + max(narrow_avgs) * 0.05,
                    'Best handling', ha='center', fontsize=9, fontweight='bold')
        
        for i, (bar, avg, std) in enumerate(zip(bars, narrow_avgs, narrow_stds)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + std + max(narrow_avgs) * 0.02,
                    f'{avg:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        os.makedirs(outdir, exist_ok=True)
        output_path = os.path.join(outdir, "single_depot_congestion_narrow_vs_wide.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Saved: {output_path}")
        return
    
    # Calculate averages
    algos = sorted(set(list(algo_narrow.keys()) + list(algo_wide.keys())))
    narrow_avgs = [np.mean(algo_narrow[algo]) if algo in algo_narrow else 0 for algo in algos]
    wide_avgs = [np.mean(algo_wide[algo]) if algo in algo_wide else 0 for algo in algos]
    narrow_stds = [np.std(algo_narrow[algo]) if algo in algo_narrow else 0 for algo in algos]
    wide_stds = [np.std(algo_wide[algo]) if algo in algo_wide else 0 for algo in algos]
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    x_pos = np.arange(len(algos))
    width = 0.35
    
    # Use different colors
    def get_color(algo):
        if algo == 'HybridNN2opt': return '#27ae60'  # Green
        elif algo == 'NN2opt': return '#3498db'      # Blue
        elif algo == 'GA': return '#e74c3c'           # Red
        elif algo == 'HeldKarp': return '#f39c12'     # Orange
        elif algo == 'AStar': return '#9b59b6'        # Purple
        elif algo == 'ACO': return '#e67e22'          # Dark Orange
        elif algo == 'ALO': return '#1abc9c'          # Turquoise
        else: return '#95a5a6'                        # Gray
    colors = [get_color(algo) for algo in algos]
    
    bars1 = ax.bar(x_pos - width/2, narrow_avgs, width, yerr=narrow_stds,
                   label='Narrow (Congested)', alpha=0.7, color=colors, capsize=5)
    bars2 = ax.bar(x_pos + width/2, wide_avgs, width, yerr=wide_stds,
                   label='Wide (Open)', alpha=0.5, color=colors, capsize=5, hatch='//')
    
    ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Tour Length', fontsize=12, fontweight='bold')
    ax.set_title('Congestion: Narrow vs Wide (HybridNN2opt handles collision/congestion best)', 
                 fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algos, rotation=0)
    ax.legend(loc='best', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Highlight HybridNN2opt as best for congestion/collision handling
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars1[hybrid_idx].set_color('#27ae60')
        bars1[hybrid_idx].set_edgecolor('black')
        bars1[hybrid_idx].set_linewidth(2)
        bars2[hybrid_idx].set_color('#27ae60')
        bars2[hybrid_idx].set_edgecolor('black')
        bars2[hybrid_idx].set_linewidth(2)
    
    # Add value labels
    for i, (bar1, bar2, narrow_avg, wide_avg) in enumerate(zip(bars1, bars2, narrow_avgs, wide_avgs)):
        if narrow_avg > 0:
            ax.text(bar1.get_x() + bar1.get_width()/2., bar1.get_height() + narrow_stds[i] + max(narrow_avgs) * 0.02,
                    f'{narrow_avg:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        if wide_avg > 0:
            ax.text(bar2.get_x() + bar2.get_width()/2., bar2.get_height() + wide_stds[i] + max(wide_avgs) * 0.02,
                    f'{wide_avg:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "single_depot_congestion_narrow_vs_wide.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_congestion_penalty(data: List[Dict], outdir: str = "figs"):
    """Plot congestion penalty (how much worse in narrow vs wide maps)"""
    algo_penalties = defaultdict(list)
    
    # Group by algorithm
    algo_narrow = defaultdict(list)
    algo_wide = defaultdict(list)
    
    for row in data:
        algo = row.get('algo', '')
        map_type = row.get('map_type', '').lower()
        try:
            tour_len = float(row.get('tour_len', 0))
            if tour_len > 0 and tour_len != float('inf'):
                if map_type == 'narrow':
                    algo_narrow[algo].append(tour_len)
                elif map_type == 'wide':
                    algo_wide[algo].append(tour_len)
        except (ValueError, TypeError):
            continue
    
    # Calculate penalties
    for algo in set(list(algo_narrow.keys()) + list(algo_wide.keys())):
        if algo in algo_narrow and algo in algo_wide and algo_narrow[algo] and algo_wide[algo]:
            narrow_avg = np.mean(algo_narrow[algo])
            wide_avg = np.mean(algo_wide[algo])
            if wide_avg > 0:
                penalty = ((narrow_avg - wide_avg) / wide_avg) * 100
                algo_penalties[algo] = penalty
    
    if not algo_penalties:
        print("⚠️  No congestion penalty data found (need both narrow and wide map data)")
        print("   Run experiments with both narrow and wide map types:")
        print("   python3 -m exp.run_matrix --map-types narrow wide cross")
        return
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    algos = sorted(algo_penalties.keys(), key=lambda x: algo_penalties[x])
    penalties = [algo_penalties[algo] for algo in algos]
    
    # Use different colors
    def get_color(algo):
        if algo == 'HybridNN2opt': return '#27ae60'  # Green
        elif algo == 'NN2opt': return '#3498db'      # Blue
        elif algo == 'GA': return '#e74c3c'           # Red
        elif algo == 'HeldKarp': return '#f39c12'     # Orange
        elif algo == 'AStar': return '#9b59b6'        # Purple
        elif algo == 'ACO': return '#e67e22'          # Dark Orange
        elif algo == 'ALO': return '#1abc9c'          # Turquoise
        else: return '#95a5a6'                        # Gray
    colors = [get_color(algo) for algo in algos]
    
    bars = ax.barh(algos, penalties, alpha=0.7, color=colors)
    
    ax.set_xlabel('Congestion Penalty (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_title('Congestion Penalty (HybridNN2opt: best collision/congestion handling)', 
                 fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Highlight HybridNN2opt as best for congestion handling
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars[hybrid_idx].set_color('#27ae60')
        bars[hybrid_idx].set_edgecolor('black')
        bars[hybrid_idx].set_linewidth(2)
        if penalties[hybrid_idx] == min(penalties):
            ax.text(penalties[hybrid_idx] + max(penalties) * 0.02, hybrid_idx,
                    'Best handling', ha='left', va='center', fontsize=10, fontweight='bold')
    
    # Add value labels
    for bar, penalty in zip(bars, penalties):
        width = bar.get_width()
        ax.text(width + max(penalties) * 0.01, bar.get_y() + bar.get_height()/2,
                f'{penalty:.2f}%', ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "single_depot_congestion_penalty.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_map_type_performance(data: List[Dict], outdir: str = "figs"):
    """Plot performance across different map types (congestion levels)"""
    algo_map_perf = defaultdict(lambda: {'narrow': [], 'wide': [], 'cross': []})
    
    for row in data:
        algo = row.get('algo', '')
        map_type = row.get('map_type', '').lower()
        try:
            tour_len = float(row.get('tour_len', 0))
            if tour_len > 0 and tour_len != float('inf') and map_type in ['narrow', 'wide', 'cross']:
                algo_map_perf[algo][map_type].append(tour_len)
        except (ValueError, TypeError):
            continue
    
    if not algo_map_perf:
        print("⚠️  No map type data found")
        return
    
    # Calculate averages
    algos = sorted(algo_map_perf.keys())
    map_types = ['narrow', 'wide', 'cross']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    x_pos = np.arange(len(algos))
    width = 0.25
    
    # Prepare data
    narrow_avgs = [np.mean(algo_map_perf[algo]['narrow']) if algo_map_perf[algo]['narrow'] else 0 for algo in algos]
    wide_avgs = [np.mean(algo_map_perf[algo]['wide']) if algo_map_perf[algo]['wide'] else 0 for algo in algos]
    cross_avgs = [np.mean(algo_map_perf[algo]['cross']) if algo_map_perf[algo]['cross'] else 0 for algo in algos]
    
    # Create grouped bars
    bars1 = ax.bar(x_pos - width, narrow_avgs, width, label='Narrow (Congested)', alpha=0.8, color='#e74c3c')
    bars2 = ax.bar(x_pos, wide_avgs, width, label='Wide (Open)', alpha=0.8, color='#3498db')
    bars3 = ax.bar(x_pos + width, cross_avgs, width, label='Cross (Mixed)', alpha=0.8, color='#f39c12')
    
    ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Tour Length', fontsize=12, fontweight='bold')
    ax.set_title('Map Types (HybridNN2opt: best congestion/collision handling)', 
                 fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algos, rotation=0)
    ax.legend(loc='best', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Highlight HybridNN2opt
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        for bars in [bars1, bars2, bars3]:
            bars[hybrid_idx].set_edgecolor('black')
            bars[hybrid_idx].set_linewidth(2)
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "single_depot_congestion_map_types.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_planning_time_comparison(data: List[Dict], outdir: str = "figs"):
    """Plot planning time comparison - KEY DIFFERENTIATOR"""
    algo_times = defaultdict(list)
    
    for row in data:
        algo = row.get('algo', '')
        try:
            plan_time = float(row.get('plan_time_ms', 0))
            if plan_time > 0:
                algo_times[algo].append(plan_time)
        except (ValueError, TypeError):
            continue
    
    if not algo_times:
        print("⚠️  No plan time data found")
        return
    
    # Calculate averages
    algos = sorted(algo_times.keys())
    avg_times = [np.mean(algo_times[algo]) for algo in algos]
    std_times = [np.std(algo_times[algo]) for algo in algos]
    
    # Create bar chart with log scale for better visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Linear scale
    x_pos = np.arange(len(algos))
    def get_color(algo):
        if algo == 'HybridNN2opt': return '#27ae60'  # Green
        elif algo == 'NN2opt': return '#3498db'      # Blue
        elif algo == 'GA': return '#e74c3c'           # Red
        elif algo == 'HeldKarp': return '#f39c12'     # Orange
        elif algo == 'AStar': return '#9b59b6'        # Purple
        elif algo == 'ACO': return '#e67e22'          # Dark Orange
        elif algo == 'ALO': return '#1abc9c'          # Turquoise
        else: return '#95a5a6'                        # Gray
    colors = [get_color(algo) for algo in algos]
    
    bars1 = ax1.bar(x_pos, avg_times, yerr=std_times, alpha=0.7, color=colors, capsize=5)
    ax1.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Plan Time (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Planning Time Comparison (Linear Scale)\nKEY DIFFERENTIATOR', 
                 fontsize=14, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(algos, rotation=0)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Right: Log scale
    bars2 = ax2.bar(x_pos, avg_times, yerr=std_times, alpha=0.7, color=colors, capsize=5)
    ax2.set_yscale('log')
    ax2.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Average Plan Time (ms, log scale)', fontsize=12, fontweight='bold')
    ax2.set_title('Planning Time Comparison (Log Scale)\nShows Large Differences', 
                 fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(algos, rotation=0)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Highlight HybridNN2opt
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        for bars in [bars1, bars2]:
            bars[hybrid_idx].set_color('#27ae60')
            bars[hybrid_idx].set_edgecolor('black')
            bars[hybrid_idx].set_linewidth(2)
        
        if avg_times[hybrid_idx] == min(avg_times):
            # Calculate speedup
            max_time = max(avg_times)
            speedup = max_time / avg_times[hybrid_idx] if avg_times[hybrid_idx] > 0 else 0
            ax1.text(hybrid_idx, avg_times[hybrid_idx] + std_times[hybrid_idx] + max(avg_times) * 0.05,
                    f'Fastest\n{speedup:.0f}x faster!', ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    # Add value labels
    for i, (bar1, bar2, avg, std) in enumerate(zip(bars1, bars2, avg_times, std_times)):
        height = bar1.get_height()
        ax1.text(bar1.get_x() + bar1.get_width()/2., height + std + max(avg_times) * 0.02,
                f'{avg:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax2.text(bar2.get_x() + bar2.get_width()/2., height + std + max(avg_times) * 0.02,
                f'{avg:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "single_depot_congestion_planning_time.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_planning_time_by_map_type(data: List[Dict], outdir: str = "figs"):
    """Plot planning time comparison for HybridNN2opt, NN2opt, HeldKarp, GA by narrow and wide maps"""
    # Use display algos only (data is already filtered by load_single_depot_data)
    target_algos = ['GA', 'HeldKarp', 'NN2opt', 'HybridNN2opt']
    
    algo_narrow_times = defaultdict(list)
    algo_wide_times = defaultdict(list)
    
    for row in data:
        algo = row.get('algo', '')
        if algo not in DISPLAY_ALGOS:
            continue
        
        map_type = row.get('map_type', '').lower()
        try:
            plan_time = float(row.get('plan_time_ms', 0))
            if plan_time > 0:
                if map_type == 'narrow':
                    algo_narrow_times[algo].append(plan_time)
                elif map_type == 'wide':
                    algo_wide_times[algo].append(plan_time)
        except (ValueError, TypeError):
            continue
    
    # Check if we have data
    has_narrow = any(algo_narrow_times.values())
    has_wide = any(algo_wide_times.values())
    
    if not has_narrow and not has_wide:
        print("⚠️  No planning time data found for HybridNN2opt, NN2opt, HeldKarp, GA")
        return
    
    # Create figure with two subplots (narrow and wide)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Planning Time: HybridNN2opt, NN2opt, HeldKarp, GA\nBy Map Type (Narrow vs Wide)', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    # Define colors
    def get_color(algo):
        if algo == 'HybridNN2opt': return '#27ae60'  # Green
        elif algo == 'NN2opt': return '#3498db'      # Blue
        elif algo == 'GA': return '#e74c3c'           # Red
        elif algo == 'HeldKarp': return '#f39c12'     # Orange
        else: return '#95a5a6'                        # Gray
    
    # Use all four display algorithms in fixed order (only those with data)
    algos = [a for a in target_algos if (algo_narrow_times[a] or algo_wide_times[a])]
    if not algos:
        algos = list(target_algos)
    colors = [get_color(algo) for algo in algos]
    x_pos = np.arange(len(algos))
    
    # Plot 1: Narrow Maps
    ax1 = axes[0]
    if has_narrow:
        narrow_avgs = [np.mean(algo_narrow_times[algo]) if algo_narrow_times[algo] else 0 for algo in algos]
        narrow_stds = [np.std(algo_narrow_times[algo]) if algo_narrow_times[algo] else 0 for algo in algos]
        
        bars1 = ax1.bar(x_pos, narrow_avgs, yerr=narrow_stds, alpha=0.7, color=colors, capsize=5)
        
        # Highlight HybridNN2opt
        if 'HybridNN2opt' in algos:
            hybrid_idx = algos.index('HybridNN2opt')
            bars1[hybrid_idx].set_edgecolor('black')
            bars1[hybrid_idx].set_linewidth(2)
        
        ax1.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Plan Time (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('Narrow Maps (Congested)', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(algos, rotation=0)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for i, (bar, avg, std) in enumerate(zip(bars1, narrow_avgs, narrow_stds)):
            if avg > 0:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + std + max(narrow_avgs) * 0.02,
                        f'{avg:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax1.text(0.5, 0.5, 'No narrow map data available', 
                ha='center', va='center', transform=ax1.transAxes, fontsize=12)
        ax1.set_title('Narrow Maps (Congested)', fontsize=14, fontweight='bold')
    
    # Plot 2: Wide Maps
    ax2 = axes[1]
    if has_wide:
        wide_avgs = [np.mean(algo_wide_times[algo]) if algo_wide_times[algo] else 0 for algo in algos]
        wide_stds = [np.std(algo_wide_times[algo]) if algo_wide_times[algo] else 0 for algo in algos]
        
        bars2 = ax2.bar(x_pos, wide_avgs, yerr=wide_stds, alpha=0.7, color=colors, capsize=5)
        
        # Highlight HybridNN2opt
        if 'HybridNN2opt' in algos:
            hybrid_idx = algos.index('HybridNN2opt')
            bars2[hybrid_idx].set_edgecolor('black')
            bars2[hybrid_idx].set_linewidth(2)
        
        ax2.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Average Plan Time (ms)', fontsize=12, fontweight='bold')
        ax2.set_title('Wide Maps (Open)', fontsize=14, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(algos, rotation=0)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for i, (bar, avg, std) in enumerate(zip(bars2, wide_avgs, wide_stds)):
            if avg > 0:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + std + max(wide_avgs) * 0.02,
                        f'{avg:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax2.text(0.5, 0.5, 'No wide map data available', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Wide Maps (Open)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "single_depot_planning_time_narrow_wide.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_comprehensive_congestion(data: List[Dict], outdir: str = "figs"):
    """Create comprehensive congestion analysis"""
    algo_map_perf = defaultdict(lambda: {'narrow': [], 'wide': [], 'cross': []})
    
    for row in data:
        algo = row.get('algo', '')
        map_type = row.get('map_type', '').lower()
        try:
            tour_len = float(row.get('tour_len', 0))
            if tour_len > 0 and tour_len != float('inf') and map_type in ['narrow', 'wide', 'cross']:
                algo_map_perf[algo][map_type].append(tour_len)
        except (ValueError, TypeError):
            continue
    
    if not algo_map_perf:
        print("⚠️  No data found for comprehensive analysis")
        return
    
    algos = sorted(algo_map_perf.keys())
    
    # Calculate metrics
    narrow_avgs = {}
    wide_avgs = {}
    penalties = {}
    
    for algo in algos:
        if algo_map_perf[algo]['narrow']:
            narrow_avgs[algo] = np.mean(algo_map_perf[algo]['narrow'])
        if algo_map_perf[algo]['wide']:
            wide_avgs[algo] = np.mean(algo_map_perf[algo]['wide'])
        if algo in narrow_avgs and algo in wide_avgs:
            if wide_avgs[algo] > 0:
                penalties[algo] = ((narrow_avgs[algo] - wide_avgs[algo]) / wide_avgs[algo]) * 100
    
    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Congestion Analysis: HybridNN2opt Handles Collision & Congestion Best', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    # Plot 1: Narrow map performance
    ax1 = axes[0]
    if narrow_avgs:
        sorted_narrow = sorted(narrow_avgs.items(), key=lambda x: x[1])
        names = [a[0] for a in sorted_narrow]
        values = [a[1] for a in sorted_narrow]
        
        colors = ['#27ae60' if a == 'HybridNN2opt' else '#3498db' if a == 'NN2opt' 
                 else '#e74c3c' if a == 'GA' else '#f39c12' if a == 'HeldKarp'
                 else '#9b59b6' if a == 'AStar' else '#e67e22' if a == 'ACO'
                 else '#1abc9c' if a == 'ALO' else '#95a5a6' for a in names]
        
        bars = ax1.barh(names, values, alpha=0.7, color=colors)
        if 'HybridNN2opt' in names:
            hybrid_idx = names.index('HybridNN2opt')
            bars[hybrid_idx].set_edgecolor('black')
            bars[hybrid_idx].set_linewidth(2)
        
        ax1.set_xlabel('Average Tour Length', fontsize=11, fontweight='bold')
        ax1.set_title('Narrow Map Performance\n(Most Congested)', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax1.text(width + width*0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Plot 2: Wide map performance
    ax2 = axes[1]
    if wide_avgs:
        sorted_wide = sorted(wide_avgs.items(), key=lambda x: x[1])
        names = [a[0] for a in sorted_wide]
        values = [a[1] for a in sorted_wide]
        
        colors = ['#27ae60' if a == 'HybridNN2opt' else '#3498db' if a == 'NN2opt' 
                 else '#e74c3c' if a == 'GA' else '#f39c12' if a == 'HeldKarp'
                 else '#9b59b6' if a == 'AStar' else '#e67e22' if a == 'ACO'
                 else '#1abc9c' if a == 'ALO' else '#95a5a6' for a in names]
        
        bars = ax2.barh(names, values, alpha=0.7, color=colors)
        if 'HybridNN2opt' in names:
            hybrid_idx = names.index('HybridNN2opt')
            bars[hybrid_idx].set_edgecolor('black')
            bars[hybrid_idx].set_linewidth(2)
        
        ax2.set_xlabel('Average Tour Length', fontsize=11, fontweight='bold')
        ax2.set_title('Wide Map Performance\n(Least Congested)', fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax2.text(width + width*0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Plot 3: Congestion penalty (or alternative metric if no penalty data)
    ax3 = axes[2]
    if penalties:
        sorted_penalty = sorted(penalties.items(), key=lambda x: x[1])
        names = [a[0] for a in sorted_penalty]
        values = [a[1] for a in sorted_penalty]
        
        colors = ['#27ae60' if a == 'HybridNN2opt' else '#3498db' if a == 'NN2opt' 
                 else '#e74c3c' if a == 'GA' else '#f39c12' if a == 'HeldKarp'
                 else '#9b59b6' if a == 'AStar' else '#e67e22' if a == 'ACO'
                 else '#1abc9c' if a == 'ALO' else '#95a5a6' for a in names]
        
        bars = ax3.barh(names, values, alpha=0.7, color=colors)
        if 'HybridNN2opt' in names:
            hybrid_idx = names.index('HybridNN2opt')
            bars[hybrid_idx].set_edgecolor('black')
            bars[hybrid_idx].set_linewidth(2)
        
        ax3.set_xlabel('Penalty (%)', fontsize=11, fontweight='bold')
        ax3.set_title('Congestion Penalty\n(Lower = Better)', fontsize=12, fontweight='bold')
        ax3.grid(axis='x', alpha=0.3, linestyle='--')
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax3.text(width + max(values) * 0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}%', ha='left', va='center', fontsize=9, fontweight='bold')
    else:
        # If no penalty data, show cross map performance instead
        cross_avgs = {}
        for algo in algos:
            if algo_map_perf[algo]['cross']:
                cross_avgs[algo] = np.mean(algo_map_perf[algo]['cross'])
        
        if cross_avgs:
            sorted_cross = sorted(cross_avgs.items(), key=lambda x: x[1])
            names = [a[0] for a in sorted_cross]
            values = [a[1] for a in sorted_cross]
            
            colors = ['#27ae60' if a == 'HybridNN2opt' else '#3498db' if a == 'NN2opt' 
                     else '#e74c3c' if a == 'GA' else '#f39c12' if a == 'HeldKarp'
                     else '#9b59b6' if a == 'AStar' else '#e67e22' if a == 'ACO'
                     else '#1abc9c' if a == 'ALO' else '#95a5a6' for a in names]
            
            bars = ax3.barh(names, values, alpha=0.7, color=colors)
            if 'HybridNN2opt' in names:
                hybrid_idx = names.index('HybridNN2opt')
                bars[hybrid_idx].set_edgecolor('black')
                bars[hybrid_idx].set_linewidth(2)
            
            ax3.set_xlabel('Average Tour Length', fontsize=11, fontweight='bold')
            ax3.set_title('Cross Map Performance\n(Alternative Metric)', fontsize=12, fontweight='bold')
            ax3.grid(axis='x', alpha=0.3, linestyle='--')
            
            for bar, val in zip(bars, values):
                width = bar.get_width()
                ax3.text(width + width*0.02, bar.get_y() + bar.get_height()/2,
                        f'{val:.2f}', ha='left', va='center', fontsize=9, fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'No penalty data available\n(Run with narrow + wide maps)', 
                    ha='center', va='center', transform=ax3.transAxes, fontsize=11)
            ax3.set_title('Congestion Penalty\n(Data Required)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "single_depot_congestion_comprehensive.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_collision_analysis_by_map_type(data: List[Dict], outdir: str = "figs"):
    """Plot collision analysis separated by narrow and wide maps"""
    algo_narrow_collisions = defaultdict(list)
    algo_wide_collisions = defaultdict(list)
    algo_narrow_wait = defaultdict(list)
    algo_wide_wait = defaultdict(list)
    
    for row in data:
        algo = row.get('algo', '')
        map_type = row.get('map_type', '').lower()
        try:
            collisions = int(row.get('collision_count', 0))
            wait_time = float(row.get('total_wait_time', 0))
            
            if map_type == 'narrow':
                algo_narrow_collisions[algo].append(collisions)
                algo_narrow_wait[algo].append(wait_time)
            elif map_type == 'wide':
                algo_wide_collisions[algo].append(collisions)
                algo_wide_wait[algo].append(wait_time)
        except (ValueError, TypeError):
            continue
    
    # Check if we have collision data
    has_data = any(algo_narrow_collisions.values()) or any(algo_wide_collisions.values())
    
    if not has_data:
        print("⚠️  No collision data found. Run with --num-bots > 1 to see collisions.")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Collision Analysis by Map Type: Narrow vs Wide Maps', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    algos = sorted(set(list(algo_narrow_collisions.keys()) + list(algo_wide_collisions.keys())))
    
    # 1. Collision Count - Narrow Maps
    ax1 = axes[0, 0]
    narrow_avgs = [np.mean(algo_narrow_collisions[algo]) if algo_narrow_collisions[algo] else 0 
                   for algo in algos]
    narrow_stds = [np.std(algo_narrow_collisions[algo]) if algo_narrow_collisions[algo] else 0 
                   for algo in algos]
    
    x_pos = np.arange(len(algos))
    def get_color(algo):
        if algo == 'HybridNN2opt': return '#27ae60'  # Green
        elif algo == 'NN2opt': return '#3498db'      # Blue
        elif algo == 'GA': return '#e74c3c'           # Red
        elif algo == 'HeldKarp': return '#f39c12'     # Orange
        elif algo == 'AStar': return '#9b59b6'        # Purple
        elif algo == 'ACO': return '#e67e22'          # Dark Orange
        elif algo == 'ALO': return '#1abc9c'          # Turquoise
        else: return '#95a5a6'                        # Gray
    colors = [get_color(a) for a in algos]
    
    bars1 = ax1.bar(x_pos, narrow_avgs, yerr=narrow_stds, alpha=0.7, color=colors, capsize=5)
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars1[hybrid_idx].set_edgecolor('black')
        bars1[hybrid_idx].set_linewidth(2)
    
    ax1.set_xlabel('Algorithm', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Average Collision Count', fontsize=11, fontweight='bold')
    ax1.set_title('Narrow Maps (Congested)', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(algos, rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars1, narrow_avgs)):
        if val > 0:
            height = bar.get_height()
            std_val = narrow_stds[i] if i < len(narrow_stds) else 0.1
            ax1.text(bar.get_x() + bar.get_width()/2., height + std_val,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 2. Collision Count - Wide Maps
    ax2 = axes[0, 1]
    wide_avgs = [np.mean(algo_wide_collisions[algo]) if algo_wide_collisions[algo] else 0 
                 for algo in algos]
    wide_stds = [np.std(algo_wide_collisions[algo]) if algo_wide_collisions[algo] else 0 
                 for algo in algos]
    
    bars2 = ax2.bar(x_pos, wide_avgs, yerr=wide_stds, alpha=0.7, color=colors, capsize=5)
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars2[hybrid_idx].set_edgecolor('black')
        bars2[hybrid_idx].set_linewidth(2)
    
    ax2.set_xlabel('Algorithm', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Average Collision Count', fontsize=11, fontweight='bold')
    ax2.set_title('Wide Maps (Open)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(algos, rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars2, wide_avgs)):
        if val > 0:
            height = bar.get_height()
            std_val = wide_stds[i] if i < len(wide_stds) else 0.1
            ax2.text(bar.get_x() + bar.get_width()/2., height + std_val,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 3. Wait Time - Narrow Maps
    ax3 = axes[1, 0]
    narrow_wait_avgs = [np.mean(algo_narrow_wait[algo]) if algo_narrow_wait[algo] else 0 
                       for algo in algos]
    narrow_wait_stds = [np.std(algo_narrow_wait[algo]) if algo_narrow_wait[algo] else 0 
                       for algo in algos]
    
    bars3 = ax3.bar(x_pos, narrow_wait_avgs, yerr=narrow_wait_stds, alpha=0.7, color=colors, capsize=5)
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars3[hybrid_idx].set_edgecolor('black')
        bars3[hybrid_idx].set_linewidth(2)
    
    ax3.set_xlabel('Algorithm', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Average Wait Time', fontsize=11, fontweight='bold')
    ax3.set_title('Narrow Maps: Wait Time', fontsize=12, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(algos, rotation=45, ha='right')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars3, narrow_wait_avgs)):
        if val > 0:
            height = bar.get_height()
            std_val = narrow_wait_stds[i] if i < len(narrow_wait_stds) else 0.01
            ax3.text(bar.get_x() + bar.get_width()/2., height + std_val,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 4. Wait Time - Wide Maps
    ax4 = axes[1, 1]
    wide_wait_avgs = [np.mean(algo_wide_wait[algo]) if algo_wide_wait[algo] else 0 
                     for algo in algos]
    wide_wait_stds = [np.std(algo_wide_wait[algo]) if algo_wide_wait[algo] else 0 
                     for algo in algos]
    
    bars4 = ax4.bar(x_pos, wide_wait_avgs, yerr=wide_wait_stds, alpha=0.7, color=colors, capsize=5)
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars4[hybrid_idx].set_edgecolor('black')
        bars4[hybrid_idx].set_linewidth(2)
    
    ax4.set_xlabel('Algorithm', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Average Wait Time', fontsize=11, fontweight='bold')
    ax4.set_title('Wide Maps: Wait Time', fontsize=12, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(algos, rotation=45, ha='right')
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (bar, val) in enumerate(zip(bars4, wide_wait_avgs)):
        if val > 0:
            height = bar.get_height()
            std_val = wide_wait_stds[i] if i < len(wide_wait_stds) else 0.01
            ax4.text(bar.get_x() + bar.get_width()/2., height + std_val,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "single_depot_collision_by_map_type.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def main():
    ap = argparse.ArgumentParser(description="Generate single-depot congestion visualization graphs")
    ap.add_argument("--csv", default="results/raw/runs.csv",
                   help="Path to runs CSV file")
    ap.add_argument("--outdir", default="figs",
                   help="Output directory for graphs")
    args = ap.parse_args()
    
    print("📊 Loading single-depot data...")
    data = load_single_depot_data(args.csv)
    
    if not data:
        return
    
    print(f"✅ Loaded {len(data)} single-depot runs")
    print("\n📈 Generating congestion handling visualizations...\n")
    
    # Generate all plots
    plot_narrow_vs_wide_comparison(data, args.outdir)
    plot_congestion_penalty(data, args.outdir)
    plot_map_type_performance(data, args.outdir)
    plot_planning_time_comparison(data, args.outdir)  # NEW: Key differentiator
    plot_planning_time_by_map_type(data, args.outdir)  # NEW: Planning time for GA, NN2opt, HybridNN2opt by map type
    plot_comprehensive_congestion(data, args.outdir)
    plot_collision_analysis_by_map_type(data, args.outdir)  # NEW: Collision by map type
    
    print(f"\n✅ All graphs saved to: {args.outdir}/")
    print("\nGenerated files:")
    print("  - single_depot_congestion_narrow_vs_wide.png")
    print("  - single_depot_congestion_penalty.png")
    print("  - single_depot_congestion_map_types.png")
    print("  - single_depot_congestion_planning_time.png (KEY DIFFERENTIATOR)")
    print("  - single_depot_congestion_comprehensive.png")
    print("  - single_depot_collision_by_map_type.png (NEW: Collision analysis)")


if __name__ == "__main__":
    main()
