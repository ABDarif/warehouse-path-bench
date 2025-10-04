
from __future__ import annotations
import argparse, os, pandas as pd, numpy as np

def summarize(raw_csv: str, out_csv: str):
    df = pd.read_csv(raw_csv)
    # Compute per (map_type,K) best tour length to derive "opt rate"
    grp = df.groupby(['map_type','K'])
    best = grp['tour_len'].transform('min')
    df['opt_rate_pct'] = 100.0 * (best / df['tour_len']).clip(upper=1.0)
    # Save
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    return out_csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="results/raw/runs.csv")
    ap.add_argument("--out", default="results/summary/summary.csv")
    args = ap.parse_args()
    out = summarize(args.raw, args.out)
    print("Wrote", out)

if __name__ == "__main__":
    main()
