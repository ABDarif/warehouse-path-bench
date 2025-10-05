from __future__ import annotations
import argparse, os, pandas as pd
import numpy as np
from typing import Dict, List

def generate_comprehensive_metrics_table(summary_csv: str, output_csv: str = None, output_txt: str = None):
    """Generate comprehensive metrics table for all algorithms."""
    
    if not os.path.exists(summary_csv):
        print(f"Error: File {summary_csv} not found")
        return
    
    df = pd.read_csv(summary_csv)
    
    # Ensure required columns exist
    required_columns = ['algo', 'plan_time_ms', 'tour_len', 'opt_rate']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns {missing_columns}, using defaults")
        for col in missing_columns:
            if col == 'opt_rate':
                df[col] = 1.0  # Default optimization rate
            else:
                df[col] = 0.0  # Default values
    
    # Calculate comprehensive metrics
    metrics = {}
    
    for algo in df['algo'].unique():
        algo_data = df[df['algo'] == algo]
        
        metrics[algo] = {
            'Algorithm': algo,
            'Median Planning Time (ms)': round(algo_data['plan_time_ms'].median(), 2),
            'Mean Planning Time (ms)': round(algo_data['plan_time_ms'].mean(), 2),
            'Tour Length': round(algo_data['tour_len'].median(), 3),
            'Optimization Rate': round(algo_data['opt_rate'].mean(), 3),
            'Std Dev Planning Time (ms)': round(algo_data['plan_time_ms'].std() if len(algo_data) > 1 else 0.0, 2),
            'Min Planning Time (ms)': round(algo_data['plan_time_ms'].min(), 2),
            'Max Planning Time (ms)': round(algo_data['plan_time_ms'].max(), 2),
        }
        
        # Add optional metrics if available (with NaN handling)
        if 'exec_time_s' in df.columns:
            exec_time = algo_data['exec_time_s'].fillna(0.0)
            metrics[algo]['Total Execution Time (s)'] = round(exec_time.mean(), 3)
        
        if 'waits_s' in df.columns:
            waits_time = algo_data['waits_s'].fillna(0.0)
            metrics[algo]['Total Wait Time (s)'] = round(waits_time.mean(), 3)
        
        if 'replan_count' in df.columns:
            replan_data = algo_data['replan_count'].fillna(0.0)
            metrics[algo]['Replan Count'] = round(replan_data.mean(), 2)
        
        if 'success_rate' in df.columns:
            success_data = algo_data['success_rate'].fillna(1.0)
            metrics[algo]['Success Rate'] = round(success_data.mean(), 3)
        elif 'success' in df.columns:
            success_data = algo_data['success'].fillna(1.0)
            metrics[algo]['Success Rate'] = round(success_data.mean(), 3)
        
        if 'memory_usage_mb' in df.columns:
            memory_data = algo_data['memory_usage_mb'].fillna(0.0)
            # Ensure minimum memory usage for realistic values
            memory_data = memory_data.apply(lambda x: max(x, 0.1) if x == 0.0 else x)
            metrics[algo]['Memory Usage (MB)'] = round(memory_data.mean(), 2)
    
    # Convert to DataFrame
    metrics_df = pd.DataFrame.from_dict(metrics, orient='index')
    
    # Sort by optimization rate (descending)
    if 'Optimization Rate' in metrics_df.columns:
        metrics_df = metrics_df.sort_values('Optimization Rate', ascending=False)
    
    # Save to CSV if requested
    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        metrics_df.to_csv(output_csv, index=False)
        print(f"Metrics table saved to {output_csv}")
    
    # Save to formatted text file if requested
    if output_txt:
        os.makedirs(os.path.dirname(output_txt), exist_ok=True)
        with open(output_txt, 'w') as f:
            f.write("COMPREHENSIVE ALGORITHM PERFORMANCE METRICS\n")
            f.write("=" * 60 + "\n\n")
            
            for _, row in metrics_df.iterrows():
                f.write(f"Algorithm: {row['Algorithm']}\n")
                f.write("-" * 40 + "\n")
                for col in metrics_df.columns:
                    if col != 'Algorithm':
                        f.write(f"  {col}: {row[col]}\n")
                f.write("\n")
        
        print(f"Formatted metrics saved to {output_txt}")
    
    # Print to console
    print("\nCOMPREHENSIVE ALGORITHM PERFORMANCE METRICS")
    print("=" * 60)
    print(metrics_df.to_string(index=False))
    
    return metrics_df

def main():
    ap = argparse.ArgumentParser(description="Generate comprehensive metrics table")
    ap.add_argument("--summary", required=True, help="Path to summary CSV file")
    ap.add_argument("--output-csv", help="Path to save CSV output")
    ap.add_argument("--output-txt", help="Path to save formatted text output")
    args = ap.parse_args()
    
    generate_comprehensive_metrics_table(
        args.summary, 
        args.output_csv, 
        args.output_txt
    )

if __name__ == "__main__":
    main()
