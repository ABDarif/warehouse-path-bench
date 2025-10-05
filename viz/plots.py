
from __future__ import annotations
import argparse, os, pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_bar(summary_csv: str, save_to: str):
    df = pd.read_csv(summary_csv)
    # Handle both old and new column names
    opt_col = 'opt_rate_pct' if 'opt_rate_pct' in df.columns else 'opt_rate'
    m = (df.groupby('algo')[opt_col].mean().sort_values())
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(range(len(m)), m.values)
    plt.yticks(range(len(m)), m.index)
    plt.xlabel('Optimization Rate')
    plt.title('Algorithm Optimization Rate Comparison')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, m.values)):
        plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{value:.3f}', va='center', fontsize=9)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    plt.savefig(save_to, dpi=180)
    plt.close()

def plot_complexity(summary_csv: str, save_to: str):
    """Plot planning time vs optimization rate with clear legends."""
    df = pd.read_csv(summary_csv)
    # Handle both old and new column names
    opt_col = 'opt_rate_pct' if 'opt_rate_pct' in df.columns else 'opt_rate'
    
    g = df.groupby('algo').agg(y=(opt_col,'mean'),
                               x=('plan_time_ms','median'))
    
    plt.figure(figsize=(10, 6))
    
    # Create scatter plot with different colors and markers for each algorithm
    colors = plt.cm.Set1(np.linspace(0, 1, len(g)))
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    
    for i, (algo_name, (x, y)) in enumerate(g.iterrows()):
        color = colors[i]
        marker = markers[i % len(markers)]
        
        plt.scatter(x, y, s=120, color=color, marker=marker, 
                   label=f'{algo_name}', alpha=0.8, edgecolors='black', linewidth=1)
        
        # Add clear value annotations
        plt.annotate(f'{algo_name}\n({x:.1f}ms, {y:.3f})', (x, y), 
                    xytext=(8, 8), textcoords='offset points', 
                    fontsize=9, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7))
    
    plt.xlabel('Median Planning Time (ms)', fontsize=12)
    plt.ylabel('Optimization Rate', fontsize=12)
    plt.title('Planning Time vs Optimization Rate by Algorithm', fontsize=14, fontweight='bold')
    
    # Add clear legend with algorithm names
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, title='Algorithms')
    
    # Set axis limits and grid
    plt.xlim(left=0)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    plt.savefig(save_to, dpi=180, bbox_inches='tight')
    plt.close()

def plot_planning_vs_success_rate(summary_csv: str, save_to: str):
    """Plot planning time vs success rate with proper legends."""
    df = pd.read_csv(summary_csv)
    
    # Handle both old and new column names for success rate
    success_col = 'success_rate' if 'success_rate' in df.columns else 'success'
    
    g = df.groupby('algo').agg(
        success_rate=(success_col, 'mean'),
        planning_time=('plan_time_ms', 'median')
    )
    
    plt.figure(figsize=(10, 6))
    
    # Create scatter plot with different colors and markers for each algorithm
    colors = plt.cm.Set1(np.linspace(0, 1, len(g)))
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    
    for i, (algo_name, row) in enumerate(g.iterrows()):
        color = colors[i]
        marker = markers[i % len(markers)]
        
        plt.scatter(row['planning_time'], row['success_rate'], 
                   s=120, color=color, marker=marker, 
                   label=f'{algo_name}', alpha=0.8, edgecolors='black', linewidth=1)
        
        # Add value annotations
        plt.annotate(f'{algo_name}\n({row["planning_time"]:.1f}ms, {row["success_rate"]:.3f})', 
                    (row['planning_time'], row['success_rate']), 
                    xytext=(8, 8), textcoords='offset points', 
                    fontsize=9, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7))
    
    plt.xlabel('Median Planning Time (ms)', fontsize=12)
    plt.ylabel('Success Rate', fontsize=12)
    plt.title('Planning Time vs Success Rate by Algorithm', fontsize=14, fontweight='bold')
    
    # Add legend with clear algorithm names
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    
    # Set axis limits and grid
    plt.xlim(left=0)
    plt.ylim(0, 1.1)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add horizontal line at 100% success rate
    plt.axhline(y=1.0, color='green', linestyle=':', alpha=0.7, label='Perfect Success')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    plt.savefig(save_to, dpi=180, bbox_inches='tight')
    plt.close()


def plot_bar_opt_rate(df, out_path='figs/bar_opt_rate.png'):
    """Plots a bar chart of the optimization/success rate."""
    opt_rate = 100.0 * df['success'].sum() / max(1, len(df))
    plt.figure(figsize=(4, 3))
    plt.bar(['Success Rate'], [opt_rate], color='skyblue')
    plt.ylim(0, 100)
    plt.ylabel('Success Rate (%)')
    plt.title('Order Success Rate')
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def plot_radar(df, out_path='figs/radar_metrics.png'):
    """Plots a radar chart of overall performance metrics."""
    if df is None or df.empty:
        metrics = [0.0] * 6
    else:
        n = len(df)
        replans = df['replan_count'].fillna(0)
        planning_mean = float(df['planning_time_s'].fillna(0).mean())
        planning_var = float(df['planning_time_s'].fillna(0).var())
        exec_mean = float(df['exec_time_s'].fillna(0).mean())

        opt_rate = float(df['success'].fillna(0).sum()) / max(1.0, n)
        # sol_quality: fewer replans is better
        max_replans = replans.max() if replans.max() > 0 else 1.0
        sol_quality = 1.0 - (replans.mean() / (1.0 + max_replans))
        constraint_handling = opt_rate
        # memory eff & real-time proxies: faster is better
        memory_eff = 1.0 / (1.0 + planning_mean)
        real_time = 1.0 / (1.0 + exec_mean)
        # scalability proxy: low variance in planning time is better
        scalability = 1.0 / (1.0 + planning_var)

        metrics = [opt_rate, sol_quality, constraint_handling, memory_eff, real_time, scalability]

    metrics_list = list(np.clip(metrics, 0.0, 1.0))
    metrics_plot = metrics_list + metrics_list[:1]

    labels = ['Opt Rate', 'Sol Quality', 'Constraint', 'Mem Eff', 'Real-Time', 'Scalability']
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, metrics_plot, linewidth=2, color='royalblue')
    ax.fill(angles, metrics_plot, alpha=0.25, color='royalblue')
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 1)
    plt.title('Performance Radar (Normalized)')
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()


def plot_full_planning_time(summary_csv: str, save_to: str):
    """Plot full planning time including replanning with legends."""
    df = pd.read_csv(summary_csv)
    
    # Calculate full planning time (initial + replanning)
    if 'replan_count' in df.columns and 'plan_time_ms' in df.columns:
        # Estimate replanning time as replan_count * avg_plan_time_per_replan
        df['full_plan_time_ms'] = df['plan_time_ms'] + (df['replan_count'] * df['plan_time_ms'] * 0.5)
    else:
        df['full_plan_time_ms'] = df['plan_time_ms']
    
    g = df.groupby('algo').agg(
        full_time=('full_plan_time_ms', 'median'),
        opt_rate=('opt_rate', 'mean')
    )
    
    plt.figure(figsize=(10, 6))
    
    # Create scatter plot with different colors for each algorithm
    colors = plt.cm.Set3(np.linspace(0, 1, len(g)))
    for i, (name, (x, y)) in enumerate(g.iterrows()):
        plt.scatter(x, y, s=120, color=colors[i], label=name, alpha=0.7, edgecolors='black')
        plt.annotate(f'{name}\n({x:.1f}ms, {y:.3f})', (x, y), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    plt.xlabel('Full Planning Time (ms) - Including Replanning')
    plt.ylabel('Optimization Rate')
    plt.title('Full Planning Time vs Optimization Rate')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    plt.savefig(save_to, dpi=180, bbox_inches='tight')
    plt.close()

def plot_scatter(planner_stats, df, out_path='figs/scatter_planning_vs_opt.png'):
    """Plots planning time vs. optimization rate."""
    planning_times = list(planner_stats.get('planning_times', {}).values())
    x = np.mean(planning_times) if planning_times else 0.0
    opt_rate = 100.0 * df['success'].sum() / max(1, len(df))

    plt.figure(figsize=(6, 4))
    plt.scatter([x], [opt_rate], s=100, label='A* Planner')
    plt.xlabel('Mean Planning Time (s)')
    plt.ylabel('Success Rate (%)')
    plt.title('Planning Time vs. Success Rate')
    plt.xlim(left=0)
    plt.ylim(0, 105)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", default="results/summary/summary.csv")
    ap.add_argument("--outdir", default="figs")
    args = ap.parse_args()
    
    # Generate the required plots according to feedback
    plot_bar(args.summary, os.path.join(args.outdir, "optimization_rate.png"))
    plot_complexity(args.summary, os.path.join(args.outdir, "planning_time_vs_opt.png"))
    plot_planning_vs_success_rate(args.summary, os.path.join(args.outdir, "planning_time_vs_success_rate.png"))
    plot_full_planning_time(args.summary, os.path.join(args.outdir, "full_planning_time_vs_opt.png"))
    
    print("Wrote figures to", args.outdir)
    print("Generated plots:")
    print("- optimization_rate.png: Optimization rate comparison with values")
    print("- planning_time_vs_opt.png: Planning time vs optimization rate with legends")
    print("- planning_time_vs_success_rate.png: Planning time vs success rate with proper legends")
    print("- full_planning_time_vs_opt.png: Full planning time including replanning")

if __name__ == "__main__":
    main()
