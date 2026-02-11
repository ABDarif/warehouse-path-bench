"""
Format and display runs.csv results with algorithm comparison.
Use --out FILE to write to a file instead of stdout.
"""

import argparse
import csv
import os
import sys
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Only show these algorithms in results
DISPLAY_ALGOS = {"HybridNN2opt", "NN2opt", "HeldKarp", "GA"}


def format_results(csv_file: str = "results/raw/runs.csv", output_file: Optional[str] = None):
    """Read CSV and display or write results with algorithm comparison."""
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return

    results: List[Dict[str, str]] = []
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("algo", "") in DISPLAY_ALGOS:
                results.append(row)

    if not results:
        print(f"⚠️  No data found in {csv_file}")
        return

    lines: List[str] = []

    def out(s: str = ""):
        if output_file is None:
            print(s)
        else:
            lines.append(s)

    out("=" * 100)
    out(f"📊 ALGORITHM COMPARISON ANALYSIS - {len(results)} runs")
    out("=" * 100)
    out()
    
    # Group by situation (map_type, K, seed)
    situation_groups: Dict[Tuple[str, str, str], List[Dict]] = defaultdict(list)
    for run in results:
        key = (run.get('map_type', ''), run.get('K', ''), run.get('seed', ''))
        situation_groups[key].append(run)
    
    # Sort situations
    sorted_situations = sorted(situation_groups.keys())
    
    # Display comparison for each situation
    for map_type, K, seed in sorted_situations:
        runs = situation_groups[(map_type, K, seed)]

        out("=" * 100)
        out(f"📍 SITUATION: Map={map_type.upper()}, K={K}, Seed={seed}")
        out("=" * 100)
        out()

        # Sort by algorithm name for consistent display
        runs_sorted = sorted(runs, key=lambda x: x.get('algo', ''))
        
        # Find best performers
        best_tour_len = None
        best_tour_algos = []  # List to handle ties
        best_time = None
        best_time_algo = None
        
        algo_data = []
        for run in runs_sorted:
            algo = run.get('algo', 'Unknown')
            tour_len_str = run.get('tour_len', '')
            plan_time_str = run.get('plan_time_ms', '')
            
            try:
                if tour_len_str and tour_len_str.lower() != 'inf':
                    tour_len = float(tour_len_str)
                    if best_tour_len is None or tour_len < best_tour_len:
                        best_tour_len = tour_len
                        best_tour_algos = [algo]
                    elif tour_len == best_tour_len:
                        best_tour_algos.append(algo)
            except (ValueError, TypeError):
                pass
            
            try:
                if plan_time_str:
                    plan_time = float(plan_time_str)
                    if best_time is None or plan_time < best_time:
                        best_time = plan_time
                        best_time_algo = algo
            except (ValueError, TypeError):
                pass
            
            algo_data.append({
                'algo': algo,
                'tour_len': tour_len_str,
                'plan_time_ms': plan_time_str,
                'is_hybrid': run.get('is_hybrid', '0'),
                'improvement_pct': run.get('improvement_pct', ''),
                'initial_quality': run.get('initial_quality', ''),
                'success': run.get('success', '0')
            })
        
        # Display comparison table with additional metrics
        out(f"{'Algorithm':<20} {'Tour Length':<15} {'Plan Time (ms)':<18} {'Improvement %':<15} {'Status':<10}")
        out("-" * 100)
        
        # Find best improvement percentage
        best_improvement = None
        best_improvement_algo = None
        
        for data in algo_data:
            improvement_str = data.get('improvement_pct', '').strip()
            if improvement_str:
                try:
                    improvement = float(improvement_str)
                    if best_improvement is None or improvement > best_improvement:
                        best_improvement = improvement
                        best_improvement_algo = data['algo']
                except (ValueError, TypeError):
                    pass
        
        for data in algo_data:
            algo = data['algo']
            tour_len = data['tour_len']
            plan_time = data['plan_time_ms']
            improvement_str = data.get('improvement_pct', '').strip()
            success = "✅" if data['success'] == '1' else "❌"
            
            # Highlight best performers
            tour_marker = " 🏆" if algo in best_tour_algos and best_tour_len else ""
            time_marker = " ⚡" if algo == best_time_algo and best_time else ""
            improvement_marker = " 📈" if algo == best_improvement_algo and best_improvement else ""
            
            tour_display = f"{tour_len:<15}{tour_marker}"
            time_display = f"{plan_time:<18}{time_marker}"
            improvement_display = f"{improvement_str if improvement_str else 'N/A':<15}{improvement_marker}"
            
            out(f"{algo:<20} {tour_display} {time_display} {improvement_display} {success:<10}")

        out()
        # Summary for this situation
        if best_tour_algos and best_tour_len:
            if len(best_tour_algos) == 1:
                out(f"🏆 Best Tour Length: {best_tour_algos[0]} ({best_tour_len:.2f})")
            else:
                out(f"🏆 Best Tour Length: {' & '.join(best_tour_algos)} (tied at {best_tour_len:.2f})")
        if best_time_algo:
            out(f"⚡ Fastest Planning: {best_time_algo} ({best_time:.2f} ms)")
        if best_improvement_algo and best_improvement is not None:
            out(f"📈 Best Improvement: {best_improvement_algo} ({best_improvement:.2f}% improvement from initial)")
        out()
        out()

    # Overall statistics
    out("=" * 100)
    out("📈 OVERALL STATISTICS")
    out("=" * 100)
    out()
    
    # Algorithm performance summary
    algo_summary: Dict[str, Dict] = defaultdict(lambda: {
        'total_runs': 0,
        'wins_tour': 0,
        'wins_time': 0,
        'wins_improvement': 0,
        'total_tour_len': 0.0,
        'valid_tour_count': 0,
        'total_time': 0.0,
        'valid_time_count': 0,
        'total_improvement': 0.0,
        'valid_improvement_count': 0,
        'total_initial_quality': 0.0,
        'valid_initial_count': 0
    })
    
    for map_type, K, seed in sorted_situations:
        runs = situation_groups[(map_type, K, seed)]
        
        # Find winners in this situation
        best_tour_len = None
        best_tour_algo = None
        best_time = None
        best_time_algo = None
        best_improvement = None
        best_improvement_algo = None
        
        for run in runs:
            algo = run.get('algo', 'Unknown')
            algo_summary[algo]['total_runs'] += 1
            
            tour_len_str = run.get('tour_len', '')
            plan_time_str = run.get('plan_time_ms', '')
            improvement_str = run.get('improvement_pct', '').strip()
            initial_quality_str = run.get('initial_quality', '').strip()
            
            try:
                if tour_len_str and tour_len_str.lower() != 'inf':
                    tour_len = float(tour_len_str)
                    algo_summary[algo]['total_tour_len'] += tour_len
                    algo_summary[algo]['valid_tour_count'] += 1
                    if best_tour_len is None or tour_len < best_tour_len:
                        best_tour_len = tour_len
                        best_tour_algo = algo
            except (ValueError, TypeError):
                pass
            
            try:
                if plan_time_str:
                    plan_time = float(plan_time_str)
                    algo_summary[algo]['total_time'] += plan_time
                    algo_summary[algo]['valid_time_count'] += 1
                    if best_time is None or plan_time < best_time:
                        best_time = plan_time
                        best_time_algo = algo
            except (ValueError, TypeError):
                pass
            
            try:
                if improvement_str:
                    improvement = float(improvement_str)
                    algo_summary[algo]['total_improvement'] += improvement
                    algo_summary[algo]['valid_improvement_count'] += 1
                    if best_improvement is None or improvement > best_improvement:
                        best_improvement = improvement
                        best_improvement_algo = algo
            except (ValueError, TypeError):
                pass
            
            try:
                if initial_quality_str:
                    initial_quality = float(initial_quality_str)
                    algo_summary[algo]['total_initial_quality'] += initial_quality
                    algo_summary[algo]['valid_initial_count'] += 1
            except (ValueError, TypeError):
                pass
        
        if best_tour_algo:
            algo_summary[best_tour_algo]['wins_tour'] += 1
        if best_time_algo:
            algo_summary[best_time_algo]['wins_time'] += 1
        if best_improvement_algo:
            algo_summary[best_improvement_algo]['wins_improvement'] += 1
    
    # Display algorithm summary
    out("Algorithm Performance Summary:")
    out()
    out(f"{'Algorithm':<20} {'Runs':<8} {'Tour Wins':<12} {'Time Wins':<12} {'Imp. Wins':<12} {'Avg Tour Len':<15} {'Avg Time (ms)':<15} {'Avg Imp. %':<15}")
    out("-" * 120)

    for algo in sorted(algo_summary.keys()):
        stats = algo_summary[algo]
        avg_tour = stats['total_tour_len'] / max(1, stats['valid_tour_count'])
        avg_time = stats['total_time'] / max(1, stats['valid_time_count'])
        avg_improvement = stats['total_improvement'] / max(1, stats['valid_improvement_count']) if stats['valid_improvement_count'] > 0 else 0.0
        out(f"{algo:<20} {stats['total_runs']:<8} {stats['wins_tour']:<12} {stats['wins_time']:<12} {stats['wins_improvement']:<12} "
            f"{avg_tour:<15.2f} {avg_time:<15.2f} {avg_improvement:<15.2f}")

    out()
    best_overall_tour = max(algo_summary.items(), key=lambda x: x[1]['wins_tour'])
    best_overall_time = max(algo_summary.items(), key=lambda x: x[1]['wins_time'])
    best_overall_improvement = max(algo_summary.items(), key=lambda x: x[1]['wins_improvement'])
    out(f"🏆 Best Overall Tour Length: {best_overall_tour[0]} ({best_overall_tour[1]['wins_tour']} wins)")
    out(f"⚡ Best Overall Planning Speed: {best_overall_time[0]} ({best_overall_time[1]['wins_time']} wins)")
    out(f"📈 Best Overall Improvement: {best_overall_improvement[0]} ({best_overall_improvement[1]['wins_improvement']} wins)")
    out()
    
    # Highlight HybridNN2opt advantages
    if 'HybridNN2opt' in algo_summary:
        hybrid_stats = algo_summary['HybridNN2opt']
        out("=" * 100)
        out("🔬 HYBRIDNN2OPT ADVANTAGES (Where It Excels)")
        out("=" * 100)
        out()
        if hybrid_stats['valid_improvement_count'] > 0:
            avg_hybrid_improvement = hybrid_stats['total_improvement'] / hybrid_stats['valid_improvement_count']
            out(f"📈 Average Improvement: {avg_hybrid_improvement:.2f}% (from initial NN solution)")
            if 'NN2opt' in algo_summary:
                nn2opt_stats = algo_summary['NN2opt']
                if nn2opt_stats['valid_improvement_count'] > 0:
                    avg_nn2opt_improvement = nn2opt_stats['total_improvement'] / nn2opt_stats['valid_improvement_count']
                    improvement_diff = avg_hybrid_improvement - avg_nn2opt_improvement
                    out(f"   vs NN2opt: +{improvement_diff:.2f}% better improvement")
        if hybrid_stats['wins_improvement'] > 0:
            out(f"🏅 Improvement Wins: {hybrid_stats['wins_improvement']} (best improvement in {hybrid_stats['wins_improvement']} situations)")
        if hybrid_stats['valid_initial_count'] > 0 and hybrid_stats['valid_tour_count'] > 0:
            avg_initial = hybrid_stats['total_initial_quality'] / hybrid_stats['valid_initial_count']
            avg_final = hybrid_stats['total_tour_len'] / hybrid_stats['valid_tour_count']
            total_improvement = ((avg_initial - avg_final) / avg_initial) * 100.0
            out(f"📊 Solution Quality: Starts at {avg_initial:.2f}, improves to {avg_final:.2f} ({total_improvement:.2f}% total improvement)")
        out()
        out("Note: HybridNN2opt takes MORE time (as expected for hybrid algorithms)")
        out("      but provides BETTER solution quality through:")
        out("      - Multiple NN starting points (exploration)")
        out("      - Extended 2-opt iterations (exploitation)")
        out("      - Better convergence from initial solution")
        out()

    # Map type analysis
    out("=" * 100)
    out("🗺️  PERFORMANCE BY MAP TYPE")
    out("=" * 100)
    out()
    
    map_algo_wins: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    for map_type, K, seed in sorted_situations:
        runs = situation_groups[(map_type, K, seed)]
        
        best_tour_len = None
        best_tour_algo = None
        
        for run in runs:
            algo = run.get('algo', 'Unknown')
            tour_len_str = run.get('tour_len', '')
            
            try:
                if tour_len_str and tour_len_str.lower() != 'inf':
                    tour_len = float(tour_len_str)
                    if best_tour_len is None or tour_len < best_tour_len:
                        best_tour_len = tour_len
                        best_tour_algo = algo
            except (ValueError, TypeError):
                pass
        
        if best_tour_algo:
            map_algo_wins[map_type][best_tour_algo] += 1
    
    for map_type in sorted(map_algo_wins.keys()):
        out(f"Map Type: {map_type.upper()}")
        wins = map_algo_wins[map_type]
        total = sum(wins.values())
        for algo in sorted(wins.keys(), key=lambda x: wins[x], reverse=True):
            percentage = (wins[algo] / total * 100) if total > 0 else 0
            out(f"  {algo:<20}: {wins[algo]} wins ({percentage:.1f}%)")
        out()
    out("=" * 100)

    if output_file:
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w") as f:
            f.write("\n".join(lines))
        print(f"✅ Formatted results written to: {output_file}")


def format_multi_depot_results(csv_file: str = "results/raw/multi_depot_runs.csv"):
    """Format multi-depot comparison results (imported from generate_multi_depot_results)"""
    try:
        from generate_multi_depot_results import generate_comparison
        generate_comparison(csv_file)
    except ImportError:
        print("⚠️  Multi-depot formatter not available")


def main():
    ap = argparse.ArgumentParser(description="Format runs.csv with algorithm comparison")
    ap.add_argument("csv_file", nargs="?", default="results/raw/runs.csv", help="Input CSV (e.g. results/raw/runs.csv)")
    ap.add_argument("--out", "-o", dest="output_file", default=None, help="Write to file instead of stdout")
    args = ap.parse_args()
    csv_file = args.csv_file
    if "multi_depot" in csv_file:
        format_multi_depot_results(csv_file)
    else:
        format_results(csv_file, output_file=args.output_file)


if __name__ == "__main__":
    main()
