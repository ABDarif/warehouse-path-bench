"""
Generate collision visualization graphs from multi-depot experiment results
"""

from __future__ import annotations
import argparse
import os
import csv
from typing import Dict, List
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


def load_collision_data(csv_file: str = "results/raw/multi_depot_runs.csv"):
    """Load collision data from CSV file"""
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        print("   Run experiments first: ./run_quick_test.sh")
        return None
    
    data = []
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only use multi-depot data (has collisions)
            if row.get('config') == 'multi_depot':
                data.append(row)
    
    return data


def plot_collision_comparison(data: List[Dict], outdir: str = "figs"):
    """Plot collision count comparison across algorithms"""
    algo_collisions = defaultdict(list)
    
    for row in data:
        algo = row.get('algo', '')
        try:
            collisions = int(row.get('collision_count', 0))
            algo_collisions[algo].append(collisions)
        except (ValueError, TypeError):
            continue
    
    if not algo_collisions:
        print("⚠️  No collision data found")
        return
    
    # Calculate averages
    algos = sorted(algo_collisions.keys())
    avg_collisions = [np.mean(algo_collisions[algo]) for algo in algos]
    std_collisions = [np.std(algo_collisions[algo]) for algo in algos]
    
    # Check if all values are zero
    all_zero = all(avg == 0 for avg in avg_collisions)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    x_pos = np.arange(len(algos))
    
    # Use different colors
    def get_color(algo):
        if algo == 'HybridNN2opt': return '#27ae60'  # Green
        elif algo == 'NN2opt': return '#3498db'      # Blue
        elif algo == 'AStar': return '#9b59b6'        # Purple
        elif algo == 'GA': return '#e74c3c'           # Red
        elif algo == 'HeldKarp': return '#f39c12'     # Orange
        else: return '#95a5a6'                        # Gray
    colors = [get_color(algo) for algo in algos]
    
    bars = ax.bar(x_pos, avg_collisions, yerr=std_collisions if not all_zero else None, 
                  capsize=5, alpha=0.7, color=colors)
    
    ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Collision Count', fontsize=12, fontweight='bold')
    
    if all_zero:
        title = 'Collision Comparison: All Algorithms Show Zero Collisions\n(Scenario too small - increase bots/packages to see collisions)'
        ax.set_ylim(-0.1, 0.5)  # Small range to show bars
    else:
        title = 'Collision Comparison: HybridNN2opt vs Other Algorithms'
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algos, rotation=0)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Highlight HybridNN2opt
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars[hybrid_idx].set_color('#27ae60')
        bars[hybrid_idx].set_edgecolor('black')
        bars[hybrid_idx].set_linewidth(2)
        if not all_zero and avg_collisions[hybrid_idx] == min(avg_collisions):
            ax.text(hybrid_idx, avg_collisions[hybrid_idx] + (std_collisions[hybrid_idx] if not all_zero else 0.1) + 0.5,
                    '🛡️ Best', ha='center', fontsize=10, fontweight='bold')
    
    # Add value labels on bars
    for i, (bar, avg) in enumerate(zip(bars, avg_collisions)):
        height = max(bar.get_height(), 0.1)  # Minimum height for visibility
        label_y = height + (std_collisions[i] if not all_zero else 0.05)
        ax.text(bar.get_x() + bar.get_width()/2., label_y,
                f'{avg:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    if all_zero:
        ax.text(0.5, 0.95, '⚠️ Note: With small scenarios (few bots/packages),\ncollisions are rare. Use 15+ bots for realistic results.',
                transform=ax.transAxes, ha='center', va='top', 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
                fontsize=9)
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "collision_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_wait_time_comparison(data: List[Dict], outdir: str = "figs"):
    """Plot wait time comparison across algorithms"""
    algo_waits = defaultdict(list)
    
    for row in data:
        algo = row.get('algo', '')
        try:
            wait_time = float(row.get('total_wait_time', 0))
            algo_waits[algo].append(wait_time)
        except (ValueError, TypeError):
            continue
    
    if not algo_waits:
        print("⚠️  No wait time data found")
        return
    
    # Calculate averages
    algos = sorted(algo_waits.keys())
    avg_waits = [np.mean(algo_waits[algo]) for algo in algos]
    std_waits = [np.std(algo_waits[algo]) for algo in algos]
    
    # Check if all values are zero
    all_zero = all(avg == 0 for avg in avg_waits)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    x_pos = np.arange(len(algos))
    
    # Use different colors
    def get_color(algo):
        if algo == 'HybridNN2opt': return '#27ae60'  # Green
        elif algo == 'NN2opt': return '#3498db'      # Blue
        elif algo == 'AStar': return '#9b59b6'        # Purple
        elif algo == 'GA': return '#e74c3c'           # Red
        elif algo == 'HeldKarp': return '#f39c12'     # Orange
        else: return '#95a5a6'                        # Gray
    colors = [get_color(algo) for algo in algos]
    
    bars = ax.bar(x_pos, avg_waits, yerr=std_waits if not all_zero else None, 
                  capsize=5, alpha=0.7, color=colors)
    
    ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Total Wait Time', fontsize=12, fontweight='bold')
    
    if all_zero:
        title = 'Wait Time Comparison: All Algorithms Show Zero Wait Time\n(No collisions = no wait time)'
        ax.set_ylim(-0.01, 0.1)
    else:
        title = 'Wait Time Comparison: HybridNN2opt vs Other Algorithms'
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algos, rotation=0)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Highlight HybridNN2opt
    if 'HybridNN2opt' in algos:
        hybrid_idx = algos.index('HybridNN2opt')
        bars[hybrid_idx].set_color('#27ae60')
        bars[hybrid_idx].set_edgecolor('black')
        bars[hybrid_idx].set_linewidth(2)
        if not all_zero and avg_waits[hybrid_idx] == min(avg_waits):
            ax.text(hybrid_idx, avg_waits[hybrid_idx] + (std_waits[hybrid_idx] if not all_zero else 0.02) + 0.1,
                    '⚡ Best', ha='center', fontsize=10, fontweight='bold')
    
    # Add value labels
    for i, (bar, avg) in enumerate(zip(bars, avg_waits)):
        height = max(bar.get_height(), 0.01)  # Minimum height for visibility
        label_y = height + (std_waits[i] if not all_zero else 0.01)
        ax.text(bar.get_x() + bar.get_width()/2., label_y,
                f'{avg:.2f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    if all_zero:
        ax.text(0.5, 0.95, '⚠️ Note: Wait time is zero because there are no collisions.\nUse 15+ bots for realistic collision scenarios.',
                transform=ax.transAxes, ha='center', va='top', 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
                fontsize=9)
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "wait_time_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_collision_vs_makespan(data: List[Dict], outdir: str = "figs"):
    """Plot collision count vs makespan to show correlation"""
    algo_data = defaultdict(lambda: {'collisions': [], 'makespan': []})
    
    for row in data:
        algo = row.get('algo', '')
        try:
            collisions = int(row.get('collision_count', 0))
            makespan = float(row.get('collision_makespan', 0))
            algo_data[algo]['collisions'].append(collisions)
            algo_data[algo]['makespan'].append(makespan)
        except (ValueError, TypeError):
            continue
    
    if not algo_data:
        print("⚠️  No data found for scatter plot")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {'HybridNN2opt': '#27ae60', 'NN2opt': '#3498db', 
              'GA': '#e74c3c', 'HeldKarp': '#f39c12', 'AStar': '#9b59b6'}
    markers = {'HybridNN2opt': 'o', 'NN2opt': 's', 'GA': '^', 
               'HeldKarp': 'D', 'AStar': 'v'}
    
    # Check if all collisions are zero
    all_zero_collisions = all(
        all(c == 0 for c in algo_data[algo]['collisions'])
        for algo in algo_data.keys()
    )
    
    # Use jitter to separate overlapping points
    jitter_amount = 0.1 if all_zero_collisions else 0.0
    
    for algo in sorted(algo_data.keys()):
        collisions = algo_data[algo]['collisions']
        makespan = algo_data[algo]['makespan']
        color = colors.get(algo, '#95a5a6')
        marker = markers.get(algo, 'o')
        
        # Add small jitter if all collisions are zero
        if all_zero_collisions:
            jittered_collisions = [c + np.random.uniform(-jitter_amount, jitter_amount) for c in collisions]
        else:
            jittered_collisions = collisions
        
        scatter = ax.scatter(jittered_collisions, makespan, label=algo, 
                  color=color, marker=marker, s=100, alpha=0.6, edgecolors='black', linewidth=1.5)
    
    ax.set_xlabel('Collision Count', fontsize=12, fontweight='bold')
    ax.set_ylabel('Collision Makespan', fontsize=12, fontweight='bold')
    
    if all_zero_collisions:
        title = 'Collision Count vs Makespan\n(All collisions are 0 - scenario too small)'
        ax.set_xlim(-0.5, 0.5)
        ax.text(0.5, 0.95, '⚠️ Note: With small scenarios, collisions are rare.\nUse 15+ bots for realistic collision data.',
                transform=ax.transAxes, ha='center', va='top', 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
                fontsize=9)
    else:
        title = 'Collision Count vs Makespan: Impact of Collisions on Performance'
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "collision_vs_makespan.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def plot_comprehensive_comparison(data: List[Dict], outdir: str = "figs"):
    """Create a comprehensive comparison with multiple metrics"""
    algos = sorted(set(row.get('algo', '') for row in data if row.get('algo')))
    
    if not algos:
        print("⚠️  No algorithm data found")
        return
    
    metrics = {
        'Collisions': defaultdict(list),
        'Wait Time': defaultdict(list),
        'Max Wait': defaultdict(list),
        'Collision Makespan': defaultdict(list)
    }
    
    for row in data:
        algo = row.get('algo', '')
        if not algo:
            continue
        
        try:
            metrics['Collisions'][algo].append(int(row.get('collision_count', 0)))
            metrics['Wait Time'][algo].append(float(row.get('total_wait_time', 0)))
            metrics['Max Wait'][algo].append(float(row.get('max_wait_time', 0)))
            metrics['Collision Makespan'][algo].append(float(row.get('collision_makespan', 0)))
        except (ValueError, TypeError):
            continue
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Comprehensive Collision Analysis: HybridNN2opt Performance', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    colors = ['#27ae60', '#3498db', '#e74c3c', '#f39c12']
    
    for idx, (metric_name, algo_data) in enumerate(metrics.items()):
        ax = axes[idx // 2, idx % 2]
        
        # Calculate averages
        algo_avgs = {}
        for algo in algos:
            if algo in algo_data and algo_data[algo]:
                algo_avgs[algo] = np.mean(algo_data[algo])
        
        if not algo_avgs:
            continue
        
        sorted_algos = sorted(algo_avgs.items(), key=lambda x: x[1])
        sorted_names = [a[0] for a in sorted_algos]
        sorted_values = [a[1] for a in sorted_algos]
        
        bars = ax.barh(sorted_names, sorted_values, 
                      color=colors[:len(sorted_names)], alpha=0.7)
        
        # Highlight HybridNN2opt
        if 'HybridNN2opt' in sorted_names:
            hybrid_idx = sorted_names.index('HybridNN2opt')
            bars[hybrid_idx].set_color('#27ae60')
            bars[hybrid_idx].set_edgecolor('black')
            bars[hybrid_idx].set_linewidth(2)
        
        ax.set_xlabel(metric_name, fontsize=11, fontweight='bold')
        ax.set_title(f'Average {metric_name}', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bar, val in zip(bars, sorted_values):
            width = bar.get_width()
            ax.text(width + width*0.02, bar.get_y() + bar.get_height()/2,
                   f'{val:.2f}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "comprehensive_collision_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {output_path}")


def main():
    ap = argparse.ArgumentParser(description="Generate collision visualization graphs")
    ap.add_argument("--csv", default="results/raw/multi_depot_runs.csv",
                   help="Path to multi-depot runs CSV file")
    ap.add_argument("--outdir", default="figs",
                   help="Output directory for graphs")
    args = ap.parse_args()
    
    print("📊 Loading collision data...")
    data = load_collision_data(args.csv)
    
    if not data:
        return
    
    print(f"✅ Loaded {len(data)} multi-depot runs")
    print("\n📈 Generating collision visualizations...\n")
    
    # Generate all plots
    plot_collision_comparison(data, args.outdir)
    plot_wait_time_comparison(data, args.outdir)
    plot_collision_vs_makespan(data, args.outdir)
    plot_comprehensive_comparison(data, args.outdir)
    
    print(f"\n✅ All graphs saved to: {args.outdir}/")
    print("\nGenerated files:")
    print("  - collision_comparison.png")
    print("  - wait_time_comparison.png")
    print("  - collision_vs_makespan.png")
    print("  - comprehensive_collision_analysis.png")


if __name__ == "__main__":
    main()
