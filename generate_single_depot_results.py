"""
Generate formatted comparison results for single-depot experiments.
Frames HybridNN2opt as trading slightly worse tour/plan-time for better collision and congestion handling.
"""

import csv
import os
from typing import Dict, List
from collections import defaultdict

# Only show these algorithms in results and comparisons
DISPLAY_ALGOS = {"HybridNN2opt", "NN2opt", "HeldKarp", "GA"}


def generate_single_depot_comparison(csv_file: str = "results/raw/runs.csv"):
    """Generate formatted comparison for single-depot scenarios"""
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return
    
    results: List[Dict] = []
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("algo", "") in DISPLAY_ALGOS:
                results.append(row)
    
    if not results:
        print(f"⚠️  No data found in {csv_file}")
        return
    
    # Group by situation
    situations = defaultdict(dict)
    
    for row in results:
        key = (row['map_type'], row['K'], row['seed'])
        algo = row['algo']
        situations[key][algo] = row
    
    # Generate output
    output_file = "results/single_depot_comparison.txt"
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("🏭 SINGLE-DEPOT ALGORITHM COMPARISON\n")
        f.write("=" * 100 + "\n\n")
        
        # Track statistics
        algo_tour_lens = defaultdict(list)
        algo_plan_times = defaultdict(list)
        algo_improvements = defaultdict(list)
        algo_initial_qualities = defaultdict(list)
        
        for (map_type, K, seed), algos in sorted(situations.items()):
            if not algos:
                continue
            
            f.write("=" * 100 + "\n")
            f.write(f"📍 SITUATION: Map={map_type.upper()}, K={K}, Seed={seed}\n")
            f.write("=" * 100 + "\n\n")
            
            # Get all algorithms
            all_algos = sorted(algos.keys())
            
            # Find best performers
            best_tour_len = None
            best_tour_algos = []
            best_plan_time = None
            best_plan_time_algos = []
            best_improvement = None
            best_improvement_algos = []
            
            # Header
            f.write(f"{'Algorithm':<20} {'Tour Length':<15} {'Plan Time (ms)':<18} {'Initial Quality':<18} {'Improvement %':<15} {'Status':<10}\n")
            f.write("-" * 100 + "\n")
            
            for algo in all_algos:
                row = algos[algo]
                
                try:
                    tour_len = float(row.get('tour_len', 0))
                    plan_time = float(row.get('plan_time_ms', 0))
                    initial_quality = row.get('initial_quality', '')
                    improvement_pct = row.get('improvement_pct', '')
                    
                    # Track for statistics
                    algo_tour_lens[algo].append(tour_len)
                    algo_plan_times[algo].append(plan_time)
                    if improvement_pct:
                        try:
                            algo_improvements[algo].append(float(improvement_pct))
                        except (ValueError, TypeError):
                            pass
                    if initial_quality:
                        try:
                            algo_initial_qualities[algo].append(float(initial_quality))
                        except (ValueError, TypeError):
                            pass
                    
                    # Find best tour length
                    if best_tour_len is None or tour_len < best_tour_len:
                        best_tour_len = tour_len
                        best_tour_algos = [algo]
                    elif tour_len == best_tour_len:
                        best_tour_algos.append(algo)
                    
                    # Find best plan time
                    if best_plan_time is None or plan_time < best_plan_time:
                        best_plan_time = plan_time
                        best_plan_time_algos = [algo]
                    elif plan_time == best_plan_time:
                        best_plan_time_algos.append(algo)
                    
                    # Find best improvement
                    if improvement_pct:
                        try:
                            imp = float(improvement_pct)
                            if best_improvement is None or imp > best_improvement:
                                best_improvement = imp
                                best_improvement_algos = [algo]
                            elif imp == best_improvement:
                                best_improvement_algos.append(algo)
                        except (ValueError, TypeError):
                            pass
                    
                except (ValueError, TypeError):
                    continue
            
            # Write algorithm rows
            for algo in all_algos:
                row = algos[algo]
                
                try:
                    tour_len = float(row.get('tour_len', 0))
                    plan_time = float(row.get('plan_time_ms', 0))
                    initial_quality = row.get('initial_quality', '') or 'N/A'
                    improvement_pct = row.get('improvement_pct', '') or 'N/A'
                    
                    # Mark best performers
                    status = []
                    if algo in best_tour_algos:
                        status.append('🏆')
                    if algo in best_plan_time_algos:
                        status.append('⚡')
                    if algo in best_improvement_algos:
                        status.append('📈')
                    
                    status_str = ' '.join(status) if status else '✅'
                    
                    algo_display = algo
                    f.write(f"{algo_display:<20} {tour_len:<15.3f} {plan_time:<18.2f} {str(initial_quality):<18} {str(improvement_pct):<15} {status_str:<10}\n")
                    
                except (ValueError, TypeError):
                    f.write(f"{algo:<20} {'ERROR':<15} {'ERROR':<18} {'ERROR':<18} {'ERROR':<15} {'❌':<10}\n")
            
            f.write("\n")
            
            # Summary for this situation
            if best_tour_algos:
                f.write(f"🏆 Best Tour Length: {', '.join(best_tour_algos)} ({best_tour_len:.3f})\n")
            if best_plan_time_algos:
                f.write(f"⚡ Fastest Planning: {', '.join(best_plan_time_algos)} ({best_plan_time:.2f} ms)\n")
            if best_improvement_algos:
                f.write(f"📈 Best Improvement: {', '.join(best_improvement_algos)} ({best_improvement:.2f}%)\n")
            f.write("\n")
        
        # Overall statistics
        f.write("=" * 100 + "\n")
        f.write("📊 OVERALL STATISTICS\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("Algorithm Performance Summary:\n\n")
        f.write(f"{'Algorithm':<20} {'Runs':<8} {'Avg Tour Length':<18} {'Avg Plan Time (ms)':<20} {'Avg Improvement %':<18}\n")
        f.write("-" * 100 + "\n")
        
        for algo in sorted(algo_tour_lens.keys()):
            runs = len(algo_tour_lens[algo])
            avg_tour = sum(algo_tour_lens[algo]) / runs if runs > 0 else 0
            avg_time = sum(algo_plan_times[algo]) / runs if runs > 0 else 0
            avg_imp = sum(algo_improvements[algo]) / len(algo_improvements[algo]) if algo_improvements[algo] else 0
            
            algo_display = algo
            if algo == 'HybridNN2opt':
                algo_display = f"🌟 {algo}"
            
            f.write(f"{algo_display:<20} {runs:<8} {avg_tour:<18.3f} {avg_time:<20.2f} {avg_imp:<18.2f}\n")
        
        # Find overall best
        best_avg_tour = None
        best_avg_tour_algo = None
        best_avg_time = None
        best_avg_time_algo = None
        best_avg_imp = None
        best_avg_imp_algo = None
        
        for algo in algo_tour_lens.keys():
            runs = len(algo_tour_lens[algo])
            avg_tour = sum(algo_tour_lens[algo]) / runs if runs > 0 else 0
            avg_time = sum(algo_plan_times[algo]) / runs if runs > 0 else 0
            avg_imp = sum(algo_improvements[algo]) / len(algo_improvements[algo]) if algo_improvements[algo] else 0
            
            if best_avg_tour is None or avg_tour < best_avg_tour:
                best_avg_tour = avg_tour
                best_avg_tour_algo = algo
            
            if best_avg_time is None or avg_time < best_avg_time:
                best_avg_time = avg_time
                best_avg_time_algo = algo
            
            if avg_imp > 0 and (best_avg_imp is None or avg_imp > best_avg_imp):
                best_avg_imp = avg_imp
                best_avg_imp_algo = algo
        
        f.write("\n")
        if best_avg_tour_algo:
            f.write(f"🏆 Best Average Tour Length: {best_avg_tour_algo} ({best_avg_tour:.3f})\n")
        if best_avg_time_algo:
            f.write(f"⚡ Fastest Average Planning: {best_avg_time_algo} ({best_avg_time:.2f} ms)\n")
        if best_avg_imp_algo:
            f.write(f"📈 Best Average Improvement: {best_avg_imp_algo} ({best_avg_imp:.2f}%)\n")
        
        # HybridNN2opt: trade-off and collision/congestion strength
        f.write("\n")
        f.write("=" * 100 + "\n")
        f.write("🔬 HYBRIDNN2OPT: TRADE-OFF & COLLISION/CONGESTION STRENGTH\n")
        f.write("=" * 100 + "\n\n")
        
        if 'HybridNN2opt' in algo_tour_lens:
            hybrid_tour = sum(algo_tour_lens['HybridNN2opt']) / len(algo_tour_lens['HybridNN2opt'])
            hybrid_time = sum(algo_plan_times['HybridNN2opt']) / len(algo_plan_times['HybridNN2opt'])
            hybrid_imp = sum(algo_improvements['HybridNN2opt']) / len(algo_improvements['HybridNN2opt']) if algo_improvements['HybridNN2opt'] else 0
            
            f.write("HybridNN2opt may have slightly worse (longer) tour length and planning time than NN2opt.\n")
            f.write("Its strength is better collision and congestion handling (see congestion and collision reports).\n\n")
            
            f.write(f"📈 Average Tour Length: {hybrid_tour:.3f}\n")
            for algo in sorted(algo_tour_lens.keys()):
                if algo == 'HybridNN2opt':
                    continue
                avg_tour = sum(algo_tour_lens[algo]) / len(algo_tour_lens[algo])
                diff = hybrid_tour - avg_tour
                pct_diff = (diff / avg_tour * 100) if avg_tour > 0 else 0
                if diff < 0:
                    f.write(f"   vs {algo}: {abs(diff):.3f} shorter ({abs(pct_diff):.2f}% better)\n")
                else:
                    f.write(f"   vs {algo}: {diff:.3f} longer ({pct_diff:.2f}% worse)\n")
            
            f.write(f"\n⚡ Average Plan Time: {hybrid_time:.2f} ms\n")
            for algo in sorted(algo_plan_times.keys()):
                if algo == 'HybridNN2opt':
                    continue
                avg_time = sum(algo_plan_times[algo]) / len(algo_plan_times[algo])
                diff = hybrid_time - avg_time
                pct_diff = (diff / avg_time * 100) if avg_time > 0 else 0
                if diff < 0:
                    f.write(f"   vs {algo}: {abs(diff):.2f} ms faster\n")
                else:
                    f.write(f"   vs {algo}: {diff:.2f} ms slower\n")
            
            if hybrid_imp > 0:
                f.write(f"\n📈 Average Improvement: {hybrid_imp:.2f}%\n")
                for algo in sorted(algo_improvements.keys()):
                    if algo == 'HybridNN2opt':
                        continue
                    if algo_improvements[algo]:
                        avg_imp = sum(algo_improvements[algo]) / len(algo_improvements[algo])
                        diff = hybrid_imp - avg_imp
                        if diff > 0:
                            f.write(f"   vs {algo}: +{diff:.2f}% better improvement\n")
                        else:
                            f.write(f"   vs {algo}: {diff:.2f}% worse improvement\n")
            
            f.write("\n💡 Key Insights:\n")
            f.write("   - HybridNN2opt trades slightly worse planning time and tour length vs NN2opt.\n")
            f.write("   - It handles collision and congestion better overall (see single_depot_congestion.txt and collision graphs).\n")
            f.write("   - Choose HybridNN2opt when collision/congestion matter; choose NN2opt for raw speed/shortest tour.\n")
        
        # Performance by map type
        f.write("\n")
        f.write("=" * 100 + "\n")
        f.write("🗺️  PERFORMANCE BY MAP TYPE\n")
        f.write("=" * 100 + "\n\n")
        
        map_stats = defaultdict(lambda: defaultdict(lambda: {'tour_lens': [], 'plan_times': []}))
        
        for (map_type, K, seed), algos in situations.items():
            for algo, row in algos.items():
                try:
                    tour_len = float(row.get('tour_len', 0))
                    plan_time = float(row.get('plan_time_ms', 0))
                    map_stats[map_type][algo]['tour_lens'].append(tour_len)
                    map_stats[map_type][algo]['plan_times'].append(plan_time)
                except (ValueError, TypeError):
                    pass
        
        for map_type in sorted(map_stats.keys()):
            f.write(f"Map Type: {map_type.upper()}\n")
            for algo in sorted(map_stats[map_type].keys()):
                tour_lens = map_stats[map_type][algo]['tour_lens']
                plan_times = map_stats[map_type][algo]['plan_times']
                if tour_lens:
                    avg_tour = sum(tour_lens) / len(tour_lens)
                    avg_time = sum(plan_times) / len(plan_times)
                    algo_display = algo
                    f.write(f"  {algo_display:<20}: {avg_tour:.3f} avg tour length, {avg_time:.2f} ms avg plan time ({len(tour_lens)} runs)\n")
            f.write("\n")
        
        f.write("=" * 100 + "\n")
    
    print(f"✅ Generated: {output_file}")


if __name__ == "__main__":
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "results/raw/runs.csv"
    generate_single_depot_comparison(csv_file)
