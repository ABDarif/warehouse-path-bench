import argparse
import os
import random
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import simpy
from tqdm import tqdm

# ----------------------------- Utilities & Planner ------------------------------

def make_grid_graph(width, height, diagonal=False):
    """Creates a grid graph using networkx."""
    G = nx.grid_2d_graph(width, height)
    # convert node names to single ints for convenience
    mapping = {n: i for i, n in enumerate(G.nodes())}
    G = nx.relabel_nodes(G, mapping)
    pos = {mapping[n]: (n[0], n[1]) for n in mapping}
    return G, pos


def manhattan(u, v, pos):
    """Manhattan distance heuristic for A*."""
    (x1, y1) = pos[u]
    (x2, y2) = pos[v]
    return abs(x1 - x2) + abs(y1 - y2)


def astar_path_avoid(G, source, target, blocked_set, pos):
    """Wrapper around networkx.astar_path that avoids a set of blocked nodes."""
    # if no path -> raise nx.NetworkXNoPath
    if source == target:
        return [source]
    H = G.copy()
    H.remove_nodes_from(blocked_set)
    return nx.astar_path(H, source, target, heuristic=lambda a, b: manhattan(a, b, pos))


# --------------------------- SimPy cell resource wrapper ------------------------

class GridSim:
    """Manages SimPy resources for each cell in the grid."""
    def __init__(self, env, G, capacity_per_cell=1):
        self.env = env
        self.G = G
        self.cells = {n: simpy.Resource(env, capacity=capacity_per_cell) for n in G.nodes}
        self.blocked = set()  # blocked nodes (temporarily unavailable for planning)

    def block_cell(self, node):
        self.blocked.add(node)

    def unblock_cell(self, node):
        self.blocked.discard(node)

    def is_blocked(self, node):
        return node in self.blocked


# --------------------------- Order / Robot process --------------------------------

class OrderKPIs:
    """A data class to store Key Performance Indicators for an order."""
    def __init__(self, order_id, start_time):
        self.order_id = order_id
        self.start_time = start_time
        self.end_time = None
        self.waits_s = 0.0
        self.replan_count = 0
        self.success = False
        self.planning_time_s = 0.0

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'exec_time_s': (self.end_time - self.start_time) if self.end_time is not None else None,
            'waits_s': self.waits_s,
            'replan_count': self.replan_count,
            'success': int(self.success),
            'planning_time_s': self.planning_time_s,
        }


def robot_process(env, name, grid_sim, path, step_time, kpis: OrderKPIs, blocked_on_fail=True):
    """SimPy process for a robot moving along a path.
    
    Movement policy:
        - Acquire next cell resource, record waiting time, move (timeout=step_time), release previous cell.
        - If next cell is blocked (grid_sim.is_blocked) then raise replanning condition by returning False
    """
    # Acquire first cell (start position) immediately
    current = path[0]
    req = grid_sim.cells[current].request()
    t0 = env.now
    yield req
    kpis.waits_s += (env.now - t0)
    held = current
    
    # Iterate over remaining waypoints
    for nxt in path[1:]:
        # If the next cell is currently blocked for planning, indicate failure
        if grid_sim.is_blocked(nxt) and blocked_on_fail:
            # Release current cell and signal replanning
            grid_sim.cells[held].release(req)
            return False  # Indicate replanning needed

        # Attempt to acquire next cell resource
        t_req = env.now
        req_next = grid_sim.cells[nxt].request()
        yield req_next
        wait_here = env.now - t_req
        kpis.waits_s += wait_here

        # Simulate move time
        yield env.timeout(step_time)

        # Release previous cell and update state
        grid_sim.cells[held].release(req)
        req = req_next
        held = nxt

    # Reached destination, release final cell
    grid_sim.cells[held].release(req)
    kpis.success = True
    return True


# ---------------------------- Blocking stochastic process ------------------------

def stochastic_blocker(env, grid_sim: GridSim, interval_mean=5.0, block_duration_mean=4.0, seed=0):
    """A SimPy process that randomly blocks and unblocks cells."""
    random.seed(seed)
    while True:
        yield env.timeout(random.expovariate(1.0 / interval_mean))
        node = random.choice(list(grid_sim.G.nodes))
        if node in grid_sim.blocked:
            continue
        grid_sim.block_cell(node)
        d = random.expovariate(1.0 / block_duration_mean)
        # Schedule the cell to be unblocked later
        env.process(unblock_after(env, grid_sim, node, d))


def unblock_after(env, grid_sim, node, delay):
    """SimPy process to unblock a cell after a delay."""
    yield env.timeout(delay)
    grid_sim.unblock_cell(node)


# ----------------------------- Experiment runner ---------------------------------

def run_simulation_scenario(with_simpy=True,
                            width=6,
                            height=3,
                            capacity_per_cell=1,
                            speed_mps=1.0,
                            meters_per_cell=1.0,
                            orders=None,
                            seed=42,
                            forced_block_tests=None):
    """Runs a complete simulation scenario and returns KPIs."""
    random.seed(seed)
    np.random.seed(seed)

    G, pos = make_grid_graph(width, height)

    if orders is None:
        # Default two-robot narrow-aisle stress test
        nodes = list(G.nodes)
        if width <= 6 and height <= 3:
            orders = [
                {'order_id': 'A', 'start': nodes[0], 'goal': nodes[-1]},
                {'order_id': 'B', 'start': nodes[width - 1], 'goal': nodes[-width]},
            ]
        else:
            orders = [
                {'order_id': i, 'start': random.choice(nodes), 'goal': random.choice(nodes)} for i in range(4)
            ]

    # Pre-sequencing & planning step (A*)
    planned_paths = {}
    planning_times = {}
    blocked_for_planning = set()

    for o in orders:
        s, g = o['start'], o['goal']
        t0 = time.time()
        try:
            p = astar_path_avoid(G, s, g, blocked_for_planning, pos)
        except Exception:
            p = [s]
        t1 = time.time()
        planned_paths[o['order_id']] = p
        planning_times[o['order_id']] = t1 - t0

    if not with_simpy:
        # Produce KPI dataframe stub from planning only
        rows = [{'order_id': o['order_id'], 'exec_time_s': None, 'waits_s': None, 'replan_count': 0, 'success': 0, 'planning_time_s': planning_times[o['order_id']]} for o in orders]
        return pd.DataFrame(rows), {'planned_paths': planned_paths, 'planning_times': planning_times}

    # With simpy: instantiate env, grid, and processes
    env = simpy.Environment()
    grid_sim = GridSim(env, G, capacity_per_cell=capacity_per_cell)
    env.process(stochastic_blocker(env, grid_sim, interval_mean=6.0, block_duration_mean=3.0, seed=seed))
    step_time = meters_per_cell / max(1e-6, speed_mps)
    kpi_records = []

    def launch_order(o):
        """Launches and monitors a single order, with replanning logic."""
        oid, s, g = o['order_id'], o['start'], o['goal']
        kpi = OrderKPIs(oid, start_time=env.now)

        # Initial plan
        tplan_t0 = time.time()
        try:
            plan = astar_path_avoid(G, s, g, grid_sim.blocked, pos)
        except Exception:
            plan = [s]
        tplan_t1 = time.time()
        kpi.planning_time_s += (tplan_t1 - tplan_t0)

        follow_proc = env.process(robot_process(env, f"robot-{oid}", grid_sim, plan, step_time, kpi))

        def monitor():
            """Monitors the robot process and replans if it fails."""
            nonlocal plan, follow_proc
            while True:
                result = yield follow_proc
                if result is True: # Success
                    kpi.end_time = env.now
                    kpi_records.append(kpi.to_dict())
                    return
                else: # Replanning needed
                    kpi.replan_count += 1
                    fallback = next((n for n in plan if not grid_sim.is_blocked(n)), None)
                    
                    if fallback is None: # No valid fallback, give up
                        kpi.end_time = env.now
                        kpi.success = False
                        kpi_records.append(kpi.to_dict())
                        return

                    # Replan from fallback to goal
                    t0p = time.time()
                    try:
                        plan = astar_path_avoid(G, fallback, g, grid_sim.blocked, pos)
                    except Exception:
                        plan = [fallback]
                    t1p = time.time()
                    kpi.planning_time_s += (t1p - t0p)
                    
                    # Start following the new plan
                    follow_proc = env.process(robot_process(env, f"robot-{oid}", grid_sim, plan, step_time, kpi))
        
        env.process(monitor())

    # Launch all orders
    for o in orders:
        launch_order(o)

    # Schedule forced blockages for testing
    if forced_block_tests:
        for node, when, duration in forced_block_tests:
            def block_later(node=node, when=when, duration=duration):
                yield env.timeout(when)
                grid_sim.block_cell(node)
                yield env.timeout(duration)
                grid_sim.unblock_cell(node)
            env.process(block_later())

    # Run simulation
    max_sim_time = 1000
    env.run(until=max_sim_time)
    
    # Mark any unfinished orders as failed
    finished_ids = {r['order_id'] for r in kpi_records}
    for o in orders:
        if o['order_id'] not in finished_ids:
            stub = {
                'order_id': o['order_id'], 'exec_time_s': env.now, 'waits_s': 0.0,
                'replan_count': 0, 'success': 0,
                'planning_time_s': planning_times.get(o['order_id'], 0.0),
            }
            kpi_records.append(stub)

    df = pd.DataFrame(kpi_records)
    return df, {'planned_paths': planned_paths, 'planning_times': planning_times}


# ---------------------------- Plotting functions ----------------------------------

def ensure_figs_dir():
    os.makedirs('figs', exist_ok=True)


def plot_bar_opt_rate(df, out_path='figs/bar_opt_rate.png'):
    """Plots a bar chart of the optimization/success rate."""
    opt_rate = 100.0 * df['success'].sum() / max(1, len(df))
    plt.figure(figsize=(4, 3))
    plt.bar(['Success Rate'], [opt_rate], color='skyblue')
    plt.ylim(0, 100)
    plt.ylabel('Success Rate (%)')
    plt.title('Order Success Rate')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_radar(df, out_path='figs/radar_metrics.png'):
    """Plots a radar chart of overall performance metrics."""
    if df is None or df.empty:
        metrics = [0.0] * 6
    else:
        n = len(df)
        replans = df['replan_count'].fillna(0)
        planning_mean = float(df['planning_time_s'].fillna(0).mean())
        planning_var = float(df['planning_time_s'].fillna(0).var())
        exec_mean = float(df['exec_time_s'].fillna(0).mean())

        opt_rate = float(df['success'].fillna(0).sum()) / max(1.0, n)
        # sol_quality: fewer replans is better
        max_replans = replans.max() if replans.max() > 0 else 1.0
        sol_quality = 1.0 - (replans.mean() / (1.0 + max_replans))
        constraint_handling = opt_rate
        # memory eff & real-time proxies: faster is better
        memory_eff = 1.0 / (1.0 + planning_mean)
        real_time = 1.0 / (1.0 + exec_mean)
        # scalability proxy: low variance in planning time is better
        scalability = 1.0 / (1.0 + planning_var)

        metrics = [opt_rate, sol_quality, constraint_handling, memory_eff, real_time, scalability]

    metrics_list = list(np.clip(metrics, 0.0, 1.0))
    metrics_plot = metrics_list + metrics_list[:1]

    labels = ['Opt Rate', 'Sol Quality', 'Constraint', 'Mem Eff', 'Real-Time', 'Scalability']
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, metrics_plot, linewidth=2, color='royalblue')
    ax.fill(angles, metrics_plot, alpha=0.25, color='royalblue')
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 1)
    plt.title('Performance Radar (Normalized)')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_scatter(planner_stats, df, out_path='figs/scatter_planning_vs_opt.png'):
    """Plots planning time vs. optimization rate."""
    planning_times = list(planner_stats.get('planning_times', {}).values())
    x = np.mean(planning_times) if planning_times else 0.0
    opt_rate = 100.0 * df['success'].sum() / max(1, len(df))

    plt.figure(figsize=(6, 4))
    plt.scatter([x], [opt_rate], s=100, label='A* Planner')
    plt.xlabel('Mean Planning Time (s)')
    plt.ylabel('Success Rate (%)')
    plt.title('Planning Time vs. Success Rate')
    plt.xlim(left=0)
    plt.ylim(0, 105)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


# ------------------------------- Main CLI ----------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Module 3 - SimPy Execution & Visualization")
    parser.add_argument('--with-simpy', action='store_true', help='Run SimPy execution after planning')
    parser.add_argument('--capacity', type=int, default=1, help='Capacity per cell')
    parser.add_argument('--speed_mps', type=float, default=0.5, help='Robot speed (m/s)')
    parser.add_argument('--meters_per_cell', type=float, default=1.0, help='Meters per grid cell')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    ensure_figs_dir()

    # Run the narrow map scenario to demonstrate congestion and replanning.
    # The forced_block_tests argument ensures a replan event occurs for testing.
    df, planner_stats = run_simulation_scenario(
        with_simpy=args.with_simpy,
        width=6, height=3,
        capacity_per_cell=args.capacity,
        speed_mps=args.speed_mps,
        meters_per_cell=args.meters_per_cell,
        seed=args.seed,
        forced_block_tests=[(5, 2.0, 3.0)]  # Block node 5 at t=2.0s for 3.0s
    )
    
    # Normalize KPI df to numeric types and fill missing values
    if df is None:
        df = pd.DataFrame(columns=['order_id','exec_time_s','waits_s','replan_count','success','planning_time_s'])

    for col in ['exec_time_s', 'waits_s', 'planning_time_s']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    for col in ['replan_count', 'success']:
         df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    if df.empty:
        print('No KPIs produced (likely because --with-simpy was not passed). Producing planning-only outputs.')
    else:
        print('\nKPIs:')
        print(df.round(3))

    # Produce plots
    plot_bar_opt_rate(df)
    plot_radar(df)
    plot_scatter(planner_stats, df)

    print('\nSaved figures to ./figs/: bar_opt_rate.png, radar_metrics.png, scatter_planning_vs_opt.png')
    print('Acceptance checks:')
    if args.with_simpy:
        if (df['waits_s'].fillna(0) > 0).any():
            print('✅ - Non-zero wait times observed (congestion present).')
        else:
            print('⚠️ - Warning: No waits observed. Congestion was not provoked.')
        if (df['replan_count'].fillna(0) > 0).any():
            print('✅ - Replanning events observed (replan_count incremented).')
        else:
            print('⚠️ - Warning: No replans observed. The forced blockage test may need adjustment.')


if __name__ == '__main__':
    main()