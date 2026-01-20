#!/usr/bin/env python3
"""
Quick view script for multi-depot comparison results
"""

import sys
import os

def main():
    result_file = "results/multi_depot_comparison.txt"
    
    if not os.path.exists(result_file):
        print(f"❌ Results file not found: {result_file}")
        print("   Run: python3 -m exp.run_multi_depot --K 10 --seeds 3 --num-depots 3")
        return
    
    with open(result_file, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    main()
