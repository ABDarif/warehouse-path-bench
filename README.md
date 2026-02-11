# Warehouse Path Benchmark

A comprehensive benchmarking system for comparing Traveling Salesman Problem (TSP) algorithms in warehouse order picking scenarios. This project evaluates multiple TSP algorithms (Held-Karp, Nearest Neighbor + 2-opt, Genetic Algorithm, and HybridNN2opt) on various warehouse layouts, with support for single-depot and multi-depot, multi-bot configurations.

---

## Table of Contents

1. [Project Overview](#-project-overview)
2. [Quick Start](#-quick-start)
3. [Project Structure](#-project-structure)
4. [Running Experiments](#-running-experiments)
5. [Results & Tables](#-results--tables)
6. [Visualization](#-visualization)
7. [Collision & Congestion](#-collision--congestion)
8. [NN2opt vs HybridNN2opt](#-nn2opt-vs-hybridnn2opt)
9. [Troubleshooting](#-troubleshooting)
10. [Requirements](#-requirements)

---

## 🎯 Project Overview

### Goals

- **Algorithm comparison**: Benchmarks multiple TSP algorithms on warehouse pathfinding problems.
- **Multi-depot support**: Compares single-depot vs multi-depot configurations with parallel bot execution.
- **Performance analysis**: Detailed statistics and formatted comparisons (best algorithm per situation).
- **Warehouse simulation**: Realistic layouts (narrow/wide/cross aisles) with obstacles and pathfinding.

### Core Features

- **TSP algorithms**: `HeldKarp` (exact), `NN2opt` (fast heuristic), `GA` (metaheuristic), `HybridNN2opt` (best quality).
- **Layouts**: `narrow`, `wide`, `cross`.
- **Single-depot**: Traditional single-bot and multi-bot from one depot.
- **Multi-depot**: Multiple depots with parallel bots (typically 55–60% makespan improvement).

### Analysis Features

- Per-situation and overall comparison, HybridNN2opt highlights, map-type breakdown, collision and congestion metrics.

---

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
# Or minimal: pip install -r requirements-minimal.txt
```

### Quick test (single-depot)

```bash
./run_single_depot_test.sh
python3 format_results.py results/raw/runs.csv
```

### Quick test (multi-depot + collision)

```bash
./run_quick_test.sh
cat results/multi_depot_comparison.txt
python3 viz/collision_plots.py
```

### Single-depot (full)

```bash
python3 -m exp.run_matrix --algos HybridNN2opt,NN2opt,HeldKarp,GA --K 10 15 --map-types narrow wide cross --seeds 5 --out results/raw
python3 format_results.py results/raw/runs.csv
# Or write to file: python3 format_results.py results/raw/runs.csv --out results/formatted_results.txt
```

### Multi-depot (full)

```bash
python3 -m exp.run_multi_depot --K 10 15 --seeds 10 --num-depots 3 --map-types narrow wide cross --algos HybridNN2opt,NN2opt,HeldKarp,GA
cat results/multi_depot_comparison.txt
```

### Command reference

| Runner | Key options |
|--------|-------------|
| `exp.run_matrix` | `--algos`, `--K`, `--map-types`, `--seeds`, `--out`, `--num-bots` |
| `exp.run_multi_depot` | `--algos`, `--K`, `--seeds`, `--num-depots`, `--map-types`, `--out` |

---

## 📁 Project Structure

```
warehouse-path-bench/
├── algos/              # TSP implementations (Held-Karp, NN2opt, GA, HybridNN2opt, ACO, ALO, A*)
├── sim/                # Grid, routing (A*), distance service, SimPy execution, collision tracker
├── exp/                # Scenarios, run_matrix (single/multi-bot), run_multi_depot, eval
├── utils/              # view_results
├── viz/                # Plots: single_depot, congestion, collision, Gantt, etc.
├── format_results.py   # Format runs.csv (terminal or --out file)
├── generate_*.py       # Single-depot, multi-depot, congestion, table generators
├── scripts/
│   └── generate_tables.py  # Run all table generators at once
├── run_*.sh            # Convenience scripts (quick test, 15/30 bots, etc.)
└── results/            # raw/, formatted_results.txt, multi_depot_comparison.txt, tables
```

---

## 📊 Running Experiments

### Single-depot (1 bot or multi-bot)

```bash
# Default (all algos, all map types)
python3 -m exp.run_matrix

# Custom
python3 -m exp.run_matrix --algos HybridNN2opt,NN2opt,GA --K 10 15 20 --map-types narrow wide cross --seeds 10 --out results/raw

# Multi-bot from one depot (collision tracking)
python3 -m exp.run_matrix --num-bots 3 --map-types narrow wide --K 15 20 --seeds 5 --algos HybridNN2opt,NN2opt,GA
```

### Multi-depot

```bash
python3 -m exp.run_multi_depot --K 10 15 --seeds 10 --num-depots 3 --map-types narrow wide cross --algos HybridNN2opt,NN2opt,HeldKarp,GA
```

### Viewing results

```bash
# Terminal
python3 format_results.py results/raw/runs.csv

# To file
python3 format_results.py results/raw/runs.csv --out results/formatted_results.txt

# Single-depot comparison file
python3 generate_single_depot_results.py results/raw/runs.csv
cat results/single_depot_comparison.txt

# Multi-depot
cat results/multi_depot_comparison.txt

# Raw CSV
python3 -m utils.view_results results/raw/runs.csv
```

---

## 📈 Results & Tables

### Formatted output (single-depot)

- Per situation: map type, K, seed → algorithm comparison (tour length, plan time, improvement %, status).
- Best performers: 🏆 tour length, ⚡ fastest, 📈 best improvement.
- Overall statistics, HybridNN2opt advantages, performance by map type.

### Multi-depot output

- Single vs multi-depot makespan, improvement %, avg tour per bot.
- Collision stats (when available): collision count, wait times, collision makespan.

### Table generators

From `results/raw/runs.csv` and (for scenario table) `results/raw/multi_depot_runs.csv`:

```bash
# All tables (performance, metrics, characteristics, scenario comparison)
python3 scripts/generate_tables.py

# Or individually
python3 generate_performance_table.py --csv results/raw/runs.csv
python3 generate_metrics_table.py --csv results/raw/runs.csv
python3 generate_characteristics_table.py --csv results/raw/runs.csv
python3 generate_scenario_comparison_table.py --single-csv results/raw/runs.csv --multi-csv results/raw/multi_depot_runs.csv
```

Outputs: `results/performance_table.txt`, `results/metrics_table.txt`, `results/characteristics_table.txt`, `results/scenario_comparison_table.txt` (and .csv variants).

### Congestion (single-depot)

- Narrow vs wide: congestion penalty = `(narrow_avg - wide_avg) / wide_avg * 100%`.
- Run with `--map-types narrow wide cross` for full penalty; narrow-only still gives per-algorithm comparison.

```bash
python3 generate_single_depot_congestion.py
cat results/single_depot_congestion.txt
```

---

## 📉 Visualization

- **Single-depot**: `python3 viz/single_depot_plots.py` → tour length, plan time, improvement, comprehensive.
- **Congestion**: `python3 viz/single_depot_congestion_plots.py` → narrow vs wide, penalty, map types, comprehensive.
- **Multi-depot / collision**: `python3 viz/collision_plots.py` → collision comparison, wait time, collision vs makespan, comprehensive.
- **Gantt**: `python3 viz/gantt_timeline.py` for timeline figure.

Other plots in `viz/`: algorithm_performance, complexity_performance, radar, optimality_vs_congestion, collision_narrow_wide, etc.

---

## 🛡️ Collision & Congestion

### Collision tracking

- **Where**: Multi-depot and single-depot multi-bot runs (SimPy: one bot per cell; wait = collision).
- **Metrics**: Collision count, total/max/avg wait time, collision makespan.
- **Why HybridNN2opt often wins**: Better tour quality and less path overlap → fewer collisions and lower wait times.

Collision graphs (e.g. from `viz/collision_plots.py`) can show many zeros in small setups (few bots, small K). Use 15+ bots and larger K for meaningful differences (e.g. `./run_15_bots.sh`, `./run_30_bots.sh`).

### Congestion (narrow vs wide)

- **Narrow** = more congested; **wide** = more open.
- Congestion penalty requires both narrow and wide data: `--map-types narrow wide cross`.
- HybridNN2opt typically has lower penalty (better congestion handling).

### Multi-bot single-depot

- `--num-bots N` with `exp.run_matrix`: multiple bots from one depot, round-robin package assignment, collision tracking, metrics by map type.
- CSV fields: `num_bots`, `theoretical_makespan`, `collision_makespan`, `collision_count`, `total_wait_time`, etc.

---

## 🔬 NN2opt vs HybridNN2opt

| Aspect | NN2opt | HybridNN2opt |
|--------|--------|--------------|
| NN starts | 1 | 3 (depot, n/2, n/4) |
| 2-opt max swaps | 1,000 | 3,000 |
| 2-opt max time | 1.0 s | 3.0 s |
| Quality | Good | Better (shorter tours) |
| Improvement % | ~9–10% | ~12–18% |
| Planning time | ~8 ms | ~10 ms |

**Use NN2opt** when speed is critical; **HybridNN2opt** when quality and consistency matter (recommended for most cases).

---

## 🔧 Troubleshooting

### "Skipping..." messages

Some runs are skipped (e.g. GA with too few waypoints, Held-Karp timeout, insufficient free cells). The rest of the experiment continues; skipped runs are not in statistics.

### Held-Karp timeout

- Held-Karp is O(2^n × n²) with a 30 s limit. For large K (e.g. ≥ 30), use smaller K or omit it: `--algos HybridNN2opt,NN2opt,GA`.

### Recommended configs

- **15 bots**: `--num-depots 15 --K 30 45 60 --seeds 10 --algos HybridNN2opt,NN2opt,GA` (or smaller K if including HeldKarp).
- **30 bots**: Same, exclude HeldKarp for large K.

### Missing narrow/wide or congestion penalty

- Run with `--map-types narrow wide cross` for full congestion analysis.

### Collision graphs all zeros

- Normal for quick/small runs. Use more bots and larger K (e.g. `./run_15_bots.sh`) for visible collision differences.

---

## 📝 Requirements

- **Core**: simpy, networkx, numpy; **optional**: matplotlib, pandas, tqdm. See `requirements.txt`.

---

## 🤝 Contributing

Possible extensions: more TSP algorithms, layout types, collision avoidance, replanning, load balancing.
