
from __future__ import annotations
import argparse, os, pandas as pd
import matplotlib.pyplot as plt

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
