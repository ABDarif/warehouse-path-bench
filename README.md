# Warehouse Path Benchmark (SimPy + Python)

A comprehensive benchmark for comparing shortest-path and TSP sequencing algorithms for warehouse order picking.

## Refactored Structure

The codebase has been organized into logical modules:

```
algos/          # TSP algorithms
├── tsp_exact.py       # Held-Karp exact algorithm
├── tsp_ga.py          # Genetic Algorithm
├── tsp_nn_2opt.py     # Nearest Neighbor + 2-opt
└── hybrids.py         # Hybrid algorithms

sim/            # Simulation components
├── grid.py           # Grid representation
├── routing.py        # A* and Dijkstra pathfinding
├── simpy_exec.py     # SimPy simulation engine
└── distance_service.py # Distance calculation service

exp/            # Experiment framework
├── scenarios.py      # Map generation and sampling
├── run_matrix.py     # Experiment runner
├── eval.py          # Results evaluation
└── demo.py          # Simple demonstration

viz/            # Visualization
└── plots.py         # Plotting functions

tests/          # Test suite
└── test_algorithms.py # Algorithm tests

results/        # Generated results (created at runtime)
figs/          # Generated plots (created at runtime)
```

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run a simple demo:**
```bash
python exp/demo.py
```

3. **Run experiments:**
```bash
python -m exp.run_matrix --algos HeldKarp,NN2opt,GA --K 5 --map-types narrow --seeds 3 --out results/raw
python -m exp.eval --raw results/raw --out results/summary/summary.csv
python -m viz.plots --summary results/summary/summary.csv --outdir figs
```

4. **Run SimPy simulation:**
```bash
python -m sim.simpy_exec --with-simpy
```

5. **Run tests:**
```bash
python tests/test_algorithms.py
```

6. **Quick sanity check:**
```bash
python run_sanity_check.py
```

## Key Features

- **Modular Design**: Clean separation of algorithms, simulation, experiments, and visualization
- **Multiple Algorithms**: Held-Karp (exact), Genetic Algorithm, Nearest Neighbor + 2-opt
- **SimPy Integration**: Real-time simulation with congestion and replanning
- **Comprehensive Testing**: Unit tests and micro-benchmarks
- **Easy Experimentation**: Command-line tools for running experiments
- **Visualization**: Automatic plot generation for results analysis

## Algorithm Comparison

The benchmark compares:
- **Held-Karp**: Exact TSP solution (for small problems)
- **GA**: Genetic Algorithm with tournament selection and OX crossover
- **NN+2opt**: Nearest Neighbor initialization with 2-opt local search

## Simulation Features

- Grid-based warehouse representation
- A* pathfinding with obstacle avoidance
- SimPy discrete-event simulation
- Dynamic congestion and replanning
- Performance metrics tracking (execution time, wait times, replanning)

## Results

Results are automatically saved to:
- `results/raw/runs.csv` - Raw experiment data
- `results/summary/summary.csv` - Aggregated statistics
- `figs/` - Generated plots and visualizations