"""
Run all table generators (performance, metrics, characteristics, scenario comparison).
Run from project root: python3 scripts/generate_tables.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _run(module_name: str, argv: list):
    sys.argv = [module_name] + argv
    mod = __import__(module_name)
    mod.main()


def main():
    csv_single = "results/raw/runs.csv"
    csv_multi = "results/raw/multi_depot_runs.csv"
    _run("generate_performance_table", ["--csv", csv_single])
    _run("generate_metrics_table", ["--csv", csv_single])
    _run("generate_characteristics_table", ["--csv", csv_single])
    _run("generate_scenario_comparison_table", ["--single-csv", csv_single, "--multi-csv", csv_multi])
    print("All tables written to results/")


if __name__ == "__main__":
    main()
