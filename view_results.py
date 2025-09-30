import pandas as pd
import os

def view_csv(filepath):
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

# View both files
view_csv("results/raw/runs.csv")
view_csv("results/summary/summary.csv")