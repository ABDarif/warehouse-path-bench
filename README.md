
# Warehouse Path Benchmark (SimPy + Python)

## Layout
```
sim/        grid.py, routing.py, simpy_exec.py
algos/      tsp_exact.py, tsp_nn_2opt.py, tsp_ga.py, hybrids.py
exp/        scenarios.py, run_matrix.py, eval.py
viz/        plots.py
results/    (created at runtime)
```
Open the following notebooks (optional) from Colab after cloning this repo:
- `00_setup.ipynb` (install deps + mount Drive)
- `10_quick_sanity.ipynb` (run a tiny demo end-to-end)
- `20_full_experiments.ipynb` (launch full grid of runs)
- `30_make_figures.ipynb` (render figures)

## Quick start (local)
```bash
python -m pip install -r requirements.txt
python -m exp.run_matrix --algos HeldKarp,NN2opt,GA --K 5 --map-types narrow --seeds 3 --out results/raw
python -m exp.eval --raw results/raw --out results/summary/summary.csv
python -m viz.plots --summary results/summary/summary.csv --outdir figs
```
