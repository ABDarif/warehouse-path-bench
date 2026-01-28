"""
View A* Algorithm Congestion Handling Metrics
Extracts and displays only AStar algorithm results from multi-depot experiments
"""

from __future__ import annotations
import csv
import os
from typing import Dict, List
from collections import defaultdict


def load_astar_data(csv_file: str = "results/raw/multi_depot_runs.csv"):
    """Load only AStar algorithm data from CSV"""
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        print("   Run experiments first: ./run_astar_comparison.sh")
        return None
    
    astar_data = []
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('algo', '').strip() == 'AStar':
                astar_data.append(row)
    
    return astar_data


def format_astar_metrics(data: List[Dict], output_file: str = "results/astar_congestion_metrics.txt"):
    """Format and display A* congestion handling metrics"""
    
    if not data:
        print("⚠️  No AStar data found in results")
        print("   Run experiments with AStar: ./run_astar_comparison.sh")
        return
    
    # Group by situation
    situations = defaultdict(list)
    for row in data:
        key = (row['map_type'], row['K'], row['seed'], row['config'])
        situations[key].append(row)
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("⭐ A* ALGORITHM - CONGESTION HANDLING METRICS\n")
        f.write("=" * 100 + "\n\n")
        
        # Overall statistics
        total_runs = len(data)
        multi_depot_runs = [r for r in data if r.get('config') == 'multi_depot']
        single_depot_runs = [r for r in data if r.get('config') == 'single_depot']
        
        f.write("📊 OVERALL STATISTICS\n")
        f.write("-" * 100 + "\n")
        f.write(f"Total A* Runs: {total_runs}\n")
        f.write(f"  - Single Depot: {len(single_depot_runs)}\n")
        f.write(f"  - Multi Depot: {len(multi_depot_runs)}\n\n")
        
        # Calculate averages for multi-depot (where collisions occur)
        if multi_depot_runs:
            avg_collisions = sum(float(r.get('collision_count', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
            avg_wait_total = sum(float(r.get('total_wait_time', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
            avg_wait_max = sum(float(r.get('max_wait_time', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
            avg_wait_avg = sum(float(r.get('avg_wait_time', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
            avg_collision_makespan = sum(float(r.get('collision_makespan', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
            avg_theoretical_makespan = sum(float(r.get('makespan', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
            avg_plan_time = sum(float(r.get('plan_time_ms', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
            
            f.write("📈 AVERAGE CONGESTION METRICS (Multi-Depot Only)\n")
            f.write("-" * 100 + "\n")
            f.write(f"Average Collision Count:        {avg_collisions:.2f}\n")
            f.write(f"Average Total Wait Time:        {avg_wait_total:.2f} seconds\n")
            f.write(f"Average Max Wait Time:          {avg_wait_max:.2f} seconds\n")
            f.write(f"Average Wait Time per Collision: {avg_wait_avg:.2f} seconds\n")
            f.write(f"Average Collision Makespan:     {avg_collision_makespan:.2f} seconds\n")
            f.write(f"Average Theoretical Makespan:  {avg_theoretical_makespan:.2f} seconds\n")
            f.write(f"Average Planning Time:          {avg_plan_time:.2f} ms\n\n")
            
            # Find min/max
            max_collisions = max(float(r.get('collision_count', 0)) for r in multi_depot_runs)
            min_collisions = min(float(r.get('collision_count', 0)) for r in multi_depot_runs)
            max_wait = max(float(r.get('total_wait_time', 0)) for r in multi_depot_runs)
            
            f.write("📊 RANGE STATISTICS\n")
            f.write("-" * 100 + "\n")
            f.write(f"Collision Count Range: {min_collisions:.0f} - {max_collisions:.0f}\n")
            f.write(f"Max Total Wait Time:   {max_wait:.2f} seconds\n\n")
        
        # Detailed per-situation breakdown
        f.write("=" * 100 + "\n")
        f.write("📍 DETAILED RESULTS BY SITUATION\n")
        f.write("=" * 100 + "\n\n")
        
        for (map_type, K, seed, config), rows in sorted(situations.items()):
            for row in rows:
                f.write("-" * 100 + "\n")
                f.write(f"Map: {map_type.upper()} | Packages (K): {K} | Seed: {seed} | Config: {config.upper()}\n")
                f.write("-" * 100 + "\n")
                
                f.write(f"Depots/Bots:           {row.get('num_depots', 'N/A')}\n")
                f.write(f"Packages per Bot:      {row.get('packages_per_bot', 'N/A')}\n")
                f.write(f"Tour Length:           {float(row.get('tour_len', 0)):.2f}\n")
                f.write(f"Planning Time:         {float(row.get('plan_time_ms', 0)):.2f} ms\n")
                f.write(f"Theoretical Makespan:  {float(row.get('makespan', 0)):.2f} seconds\n")
                
                if config == 'multi_depot':
                    f.write(f"\n🛡️  CONGESTION METRICS:\n")
                    f.write(f"  Collision Count:        {int(row.get('collision_count', 0))}\n")
                    f.write(f"  Collision Makespan:     {float(row.get('collision_makespan', 0)):.2f} seconds\n")
                    f.write(f"  Total Wait Time:        {float(row.get('total_wait_time', 0)):.2f} seconds\n")
                    f.write(f"  Max Wait Time:          {float(row.get('max_wait_time', 0)):.2f} seconds\n")
                    f.write(f"  Avg Wait Time:          {float(row.get('avg_wait_time', 0)):.2f} seconds\n")
                    
                    # Calculate impact
                    theoretical = float(row.get('makespan', 0))
                    collision = float(row.get('collision_makespan', 0))
                    if theoretical > 0:
                        impact_pct = ((collision - theoretical) / theoretical) * 100
                        f.write(f"  Collision Impact:       {impact_pct:+.2f}% (vs theoretical)\n")
                
                f.write("\n")
        
        # Summary insights
        f.write("=" * 100 + "\n")
        f.write("💡 KEY INSIGHTS\n")
        f.write("=" * 100 + "\n\n")
        
        if multi_depot_runs:
            zero_collision_runs = sum(1 for r in multi_depot_runs if float(r.get('collision_count', 0)) == 0)
            zero_pct = (zero_collision_runs / len(multi_depot_runs)) * 100
            
            f.write(f"• Zero Collision Rate: {zero_collision_runs}/{len(multi_depot_runs)} runs ({zero_pct:.1f}%)\n")
            f.write(f"• Average Collisions per Run: {avg_collisions:.2f}\n")
            
            if avg_collisions < 1.0:
                f.write(f"• A* shows excellent congestion avoidance (avg < 1 collision per run)\n")
            elif avg_collisions < 5.0:
                f.write(f"• A* shows good congestion handling (avg < 5 collisions per run)\n")
            else:
                f.write(f"• A* experiences moderate congestion (avg {avg_collisions:.1f} collisions per run)\n")
            
            if avg_wait_total < 0.5:
                f.write(f"• Very low wait times indicate efficient path planning\n")
            elif avg_wait_total < 2.0:
                f.write(f"• Low wait times show good congestion management\n")
            
            f.write(f"\n• Planning Speed: {avg_plan_time:.2f} ms average (very fast)\n")
            f.write(f"• Makespan Impact: Collisions add {avg_collision_makespan - avg_theoretical_makespan:.2f}s on average\n")
        
        f.write("\n" + "=" * 100 + "\n")
        f.write("See ASTAR_CONGESTION_EXPLANATION.md for details on how A* handles congestion\n")
        f.write("=" * 100 + "\n")
    
    print(f"✅ A* metrics saved to: {output_file}")
    print(f"   Total runs analyzed: {total_runs}")
    if multi_depot_runs:
        print(f"   Multi-depot runs: {len(multi_depot_runs)}")
        avg_coll = sum(float(r.get('collision_count', 0)) for r in multi_depot_runs) / len(multi_depot_runs)
        print(f"   Average collisions: {avg_coll:.2f}")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="View A* algorithm congestion metrics")
    ap.add_argument("--csv", default="results/raw/multi_depot_runs.csv", help="CSV file with results")
    ap.add_argument("--out", default="results/astar_congestion_metrics.txt", help="Output file")
    args = ap.parse_args()
    
    data = load_astar_data(args.csv)
    if data:
        format_astar_metrics(data, args.out)
    else:
        print("❌ No AStar data found. Run experiments first:")
        print("   ./run_astar_comparison.sh")


if __name__ == "__main__":
    main()
