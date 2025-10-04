
from __future__ import annotations
import argparse, os, pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_bar(summary_csv: str, save_to: str):
    df = pd.read_csv(summary_csv)
    m = (df.groupby('algo')['opt_rate_pct'].mean().sort_values())
    plt.figure(figsize=(8,5))
    m.plot(kind='barh')
    plt.xlabel('Optimize Rate (%)')
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    plt.savefig(save_to, dpi=180)
    plt.close()

def plot_complexity(summary_csv: str, save_to: str):
    # minimal placeholder scatter: use plan_time_ms percentile as X
    df = pd.read_csv(summary_csv)
    g = df.groupby('algo').agg(y=('opt_rate_pct','mean'),
                               x=('plan_time_ms','median'))
    plt.figure(figsize=(6,5))
    plt.scatter(g['x'], g['y'])
    for name,(x,y) in g.iterrows():
        plt.annotate(name, (x,y))
    plt.xlabel('Median Plan Time (ms)')
    plt.ylabel('Opt Rate (%)')
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    plt.savefig(save_to, dpi=180)
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


def plot_scatter(planner_stats, df, out_path='figs/scatter_planning_vs_opt.png'):
    """Plots planning time vs. optimization rate."""
    import numpy as np
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
    plot_bar(args.summary, os.path.join(args.outdir, "bar.png"))
    plot_complexity(args.summary, os.path.join(args.outdir, "complexity.png"))
    print("Wrote figures to", args.outdir)

if __name__ == "__main__":
    main()
