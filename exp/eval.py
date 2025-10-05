
from __future__ import annotations
import argparse, os, pandas as pd, numpy as np

def summarize(raw_csv: str, out_csv: str):
    df = pd.read_csv(raw_csv)
    
    # Compute per (map_type,K) best tour length to derive "opt rate"
    grp = df.groupby(['map_type','K'])
    best = grp['tour_len'].transform('min')
    
    # Handle both old and new data formats
    if 'opt_rate' in df.columns:
        # Already has optimization rate, use it
        pass
    else:
        # Calculate optimization rate from tour length
        df['opt_rate'] = (best / df['tour_len']).clip(upper=1.0)
        df['opt_rate_pct'] = 100.0 * df['opt_rate']
    
    # Fill missing values with defaults
    for col in ['exec_time_s', 'waits_s', 'replan_count', 'success', 'memory_usage_mb']:
        if col not in df.columns:
            if col == 'success':
                df[col] = 1.0  # Default success rate
            else:
                df[col] = 0.0  # Default values
    
    # Rename 'success' to 'success_rate' for consistency
    if 'success' in df.columns and 'success_rate' not in df.columns:
        df['success_rate'] = df['success']
    
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
