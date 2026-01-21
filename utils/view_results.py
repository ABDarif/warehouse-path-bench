"""
Utility script to view results from CSV files or formatted text files
"""

import pandas as pd
import os
import sys


def view_csv(filepath: str):
    """View CSV file with basic statistics"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    df = pd.read_csv(filepath)
    print(f"📊 {filepath}")
    print("=" * 60)
    print(f"Shape: {df.shape} (rows: {df.shape[0]}, cols: {df.shape[1]})")
    print("\nFirst 10 rows:")
    print(df.head(10))
    print("\n" + "=" * 60)
    
    # Show basic stats for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        print("\n📈 Basic Statistics:")
        print(df[numeric_cols].describe())


def view_formatted_text(filepath: str):
    """View formatted text results file"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r') as f:
        print(f.read())


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 -m utils.view_results <file_path>")
        print("\nExamples:")
        print("  python3 -m utils.view_results results/raw/runs.csv")
        print("  python3 -m utils.view_results results/formatted_results.txt")
        print("  python3 -m utils.view_results results/multi_depot_comparison.txt")
        return
    
    filepath = sys.argv[1]
    
    if filepath.endswith('.csv'):
        view_csv(filepath)
    elif filepath.endswith('.txt'):
        view_formatted_text(filepath)
    else:
        # Try to detect file type
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                first_line = f.readline()
                if ',' in first_line:
                    view_csv(filepath)
                else:
                    view_formatted_text(filepath)
        else:
            print(f"❌ File not found: {filepath}")


if __name__ == "__main__":
    main()
