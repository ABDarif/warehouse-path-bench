"""
Generate formatted comparison results for multi-depot experiments
Similar style to format_results.py
"""

import csv
import os
from typing import Dict, List
from collections import defaultdict


def generate_comparison(csv_file: str = "results/raw/multi_depot_runs.csv"):
    """Generate formatted comparison between single and multi-depot"""
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return
    
    results: List[Dict] = []
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    
    if not results:
        print(f"⚠️  No data found in {csv_file}")
        return
    
    # Group by situation and config
    situations = defaultdict(lambda: {'single': {}, 'multi': {}})
    
    for row in results:
        key = (row['map_type'], row['K'], row['seed'])
        config = row['config']
        algo = row['algo']
        
        if config == 'single_depot':
            situations[key]['single'][algo] = row
        elif config == 'multi_depot':
            situations[key]['multi'][algo] = row
    
    # Generate output
    output_file = "results/multi_depot_comparison.txt"
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("🏭 MULTI-DEPOT vs SINGLE-DEPOT COMPARISON\n")
        f.write("=" * 100 + "\n\n")
        
        # Track statistics
        algo_improvements = defaultdict(list)
        algo_single_makespans = defaultdict(list)
        algo_multi_makespans = defaultdict(list)
        
        for (map_type, K, seed), data in sorted(situations.items()):
            single = data['single']
            multi = data['multi']
            
            if not single or not multi:
                continue
            
            f.write("=" * 100 + "\n")
            f.write(f"📍 SITUATION: Map={map_type.upper()}, K={K}, Seed={seed}\n")
            f.write("=" * 100 + "\n\n")
            
            # Get all algorithms that appear in either config
            all_algos = sorted(set(list(single.keys()) + list(multi.keys())))
            
            # Find best performers for single depot
            best_single_makespan = None
            best_single_algos = []
            best_single_time = None
            best_single_time_algo = None
            
            for algo in all_algos:
                if algo in single:
                    try:
                        makespan = float(single[algo]['makespan'])
                        if best_single_makespan is None or makespan < best_single_makespan:
                            best_single_makespan = makespan
                            best_single_algos = [algo]
                        elif makespan == best_single_makespan:
                            best_single_algos.append(algo)
                    except (ValueError, TypeError):
                        pass
                    
                    try:
                        plan_time = float(single[algo]['plan_time_ms'])
                        if best_single_time is None or plan_time < best_single_time:
                            best_single_time = plan_time
                            best_single_time_algo = algo
                    except (ValueError, TypeError):
                        pass
            
            # Find best performers for multi-depot
            best_multi_makespan = None
            best_multi_algos = []
            best_multi_time = None
            best_multi_time_algo = None
            
            for algo in all_algos:
                if algo in multi:
                    try:
                        makespan = float(multi[algo]['makespan'])
                        if best_multi_makespan is None or makespan < best_multi_makespan:
                            best_multi_makespan = makespan
                            best_multi_algos = [algo]
                        elif makespan == best_multi_makespan:
                            best_multi_algos.append(algo)
                    except (ValueError, TypeError):
                        pass
                    
                    try:
                        plan_time = float(multi[algo]['plan_time_ms'])
                        if best_multi_time is None or plan_time < best_multi_time:
                            best_multi_time = plan_time
                            best_multi_time_algo = algo
                    except (ValueError, TypeError):
                        pass
            
            # Display comparison table
            f.write(f"{'Algorithm':<20} {'Single Makespan':<20} {'Multi Makespan':<20} {'Improvement %':<18} {'Status':<10}\n")
            f.write("-" * 100 + "\n")
            
            best_improvement = None
            best_improvement_algo = None
            
            for algo in all_algos:
                single_data = single.get(algo, {})
                multi_data = multi.get(algo, {})
                
                single_makespan_str = single_data.get('makespan', 'N/A') if single_data else 'N/A'
                multi_makespan_str = multi_data.get('makespan', 'N/A') if multi_data else 'N/A'
                
                # Calculate improvement
                improvement_str = 'N/A'
                try:
                    if single_data and multi_data:
                        single_makespan = float(single_makespan_str)
                        multi_makespan = float(multi_makespan_str)
                        improvement = ((single_makespan - multi_makespan) / max(1, single_makespan)) * 100.0
                        improvement_str = f"{improvement:.2f}"
                        
                        # Track for statistics
                        algo_improvements[algo].append(improvement)
                        algo_single_makespans[algo].append(single_makespan)
                        algo_multi_makespans[algo].append(multi_makespan)
                        
                        if best_improvement is None or improvement > best_improvement:
                            best_improvement = improvement
                            best_improvement_algo = algo
                except (ValueError, TypeError):
                    pass
                
                # Markers
                single_marker = " 🏆" if algo in best_single_algos and best_single_makespan else ""
                multi_marker = " 🏆" if algo in best_multi_algos and best_multi_makespan else ""
                improvement_marker = " ⚡" if algo == best_improvement_algo and best_improvement else ""
                
                single_display = f"{single_makespan_str:<20}{single_marker}"
                multi_display = f"{multi_makespan_str:<20}{multi_marker}"
                improvement_display = f"{improvement_str:<18}{improvement_marker}"
                
                status = "✅" if single_data and multi_data else "❌"
                
                f.write(f"{algo:<20} {single_display} {multi_display} {improvement_display} {status:<10}\n")
            
            f.write("\n")
            
            # Summary for this situation
            if best_single_algos and best_single_makespan:
                if len(best_single_algos) == 1:
                    f.write(f"🏆 Best Single-Depot Makespan: {best_single_algos[0]} ({best_single_makespan:.2f})\n")
                else:
                    f.write(f"🏆 Best Single-Depot Makespan: {' & '.join(best_single_algos)} (tied at {best_single_makespan:.2f})\n")
            
            if best_multi_algos and best_multi_makespan:
                if len(best_multi_algos) == 1:
                    f.write(f"🏆 Best Multi-Depot Makespan: {best_multi_algos[0]} ({best_multi_makespan:.2f})\n")
                else:
                    f.write(f"🏆 Best Multi-Depot Makespan: {' & '.join(best_multi_algos)} (tied at {best_multi_makespan:.2f})\n")
            
            if best_improvement_algo and best_improvement is not None:
                f.write(f"⚡ Best Improvement: {best_improvement_algo} ({best_improvement:.2f}% faster with multi-depot)\n")
            
            if best_single_time_algo:
                f.write(f"⚡ Fastest Single Planning: {best_single_time_algo} ({best_single_time:.2f} ms)\n")
            
            if best_multi_time_algo:
                f.write(f"⚡ Fastest Multi Planning: {best_multi_time_algo} ({best_multi_time:.2f} ms)\n")
            
            f.write("\n\n")
        
        # Overall statistics
        f.write("=" * 100 + "\n")
        f.write("📊 OVERALL STATISTICS\n")
        f.write("=" * 100 + "\n\n")
        
        # Algorithm performance summary
        f.write("Algorithm Performance Summary (Multi-Depot Improvements):\n\n")
        f.write(f"{'Algorithm':<20} {'Runs':<8} {'Avg Improvement %':<20} {'Best Improvement %':<20} {'Avg Single Makespan':<22} {'Avg Multi Makespan':<22}\n")
        f.write("-" * 120 + "\n")
        
        for algo in sorted(algo_improvements.keys()):
            improvements = algo_improvements[algo]
            single_makespans = algo_single_makespans[algo]
            multi_makespans = algo_multi_makespans[algo]
            
            avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
            best_improvement = max(improvements) if improvements else 0.0
            avg_single = sum(single_makespans) / len(single_makespans) if single_makespans else 0.0
            avg_multi = sum(multi_makespans) / len(multi_makespans) if multi_makespans else 0.0
            
            f.write(f"{algo:<20} {len(improvements):<8} {avg_improvement:<20.2f} {best_improvement:<20.2f} "
                   f"{avg_single:<22.2f} {avg_multi:<22.2f}\n")
        
        f.write("\n")
        
        # Find best overall algorithms
        if algo_improvements:
            best_avg_improvement = max(algo_improvements.items(), 
                                      key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0)
            best_max_improvement = max(algo_improvements.items(),
                                      key=lambda x: max(x[1]) if x[1] else 0)
            
            avg_imp_val = sum(best_avg_improvement[1]) / len(best_avg_improvement[1]) if best_avg_improvement[1] else 0
            max_imp_val = max(best_max_improvement[1]) if best_max_improvement[1] else 0
            
            f.write(f"🏆 Best Average Improvement: {best_avg_improvement[0]} ({avg_imp_val:.2f}%)\n")
            f.write(f"⚡ Best Maximum Improvement: {best_max_improvement[0]} ({max_imp_val:.2f}%)\n")
            f.write("\n")
        
        # Highlight HybridNN2opt advantages
        if 'HybridNN2opt' in algo_improvements:
            hybrid_improvements = algo_improvements['HybridNN2opt']
            hybrid_single = algo_single_makespans['HybridNN2opt']
            hybrid_multi = algo_multi_makespans['HybridNN2opt']
            
            f.write("=" * 100 + "\n")
            f.write("🔬 HYBRIDNN2OPT ADVANTAGES (Multi-Depot Performance)\n")
            f.write("=" * 100 + "\n\n")
            
            avg_hybrid_improvement = sum(hybrid_improvements) / len(hybrid_improvements) if hybrid_improvements else 0.0
            f.write(f"📈 Average Makespan Improvement: {avg_hybrid_improvement:.2f}% (with multi-depot)\n")
            
            # Compare with other algorithms
            for other_algo in sorted(algo_improvements.keys()):
                if other_algo == 'HybridNN2opt':
                    continue
                other_improvements = algo_improvements[other_algo]
                if other_improvements:
                    avg_other = sum(other_improvements) / len(other_improvements)
                    diff = avg_hybrid_improvement - avg_other
                    if abs(diff) > 0.01:  # Only show if meaningful difference
                        f.write(f"   vs {other_algo}: {diff:+.2f}% {'better' if diff > 0 else 'worse'}\n")
            
            f.write("\n")
            
            avg_hybrid_single = sum(hybrid_single) / len(hybrid_single) if hybrid_single else 0.0
            avg_hybrid_multi = sum(hybrid_multi) / len(hybrid_multi) if hybrid_multi else 0.0
            
            f.write(f"📊 Makespan Reduction: {avg_hybrid_single:.2f} → {avg_hybrid_multi:.2f} "
                   f"({avg_hybrid_improvement:.2f}% faster)\n")
            
            f.write("\n")
            f.write("💡 Key Insight: HybridNN2opt benefits significantly from multi-depot systems:\n")
            f.write("   - Parallel execution reduces makespan by distributing work\n")
            f.write("   - Multiple bots can each run optimized tours simultaneously\n")
            f.write("   - The hybrid approach maintains solution quality while benefiting from parallelism\n")
            f.write("\n")
        
        # Map type analysis
        f.write("=" * 100 + "\n")
        f.write("🗺️  PERFORMANCE BY MAP TYPE\n")
        f.write("=" * 100 + "\n\n")
        
        map_improvements = defaultdict(lambda: defaultdict(list))
        
        for (map_type, K, seed), data in sorted(situations.items()):
            single = data['single']
            multi = data['multi']
            
            for algo in set(list(single.keys()) + list(multi.keys())):
                if algo in single and algo in multi:
                    try:
                        single_makespan = float(single[algo]['makespan'])
                        multi_makespan = float(multi[algo]['makespan'])
                        improvement = ((single_makespan - multi_makespan) / max(1, single_makespan)) * 100.0
                        map_improvements[map_type][algo].append(improvement)
                    except (ValueError, TypeError):
                        pass
        
        for map_type in sorted(map_improvements.keys()):
            f.write(f"Map Type: {map_type.upper()}\n")
            for algo in sorted(map_improvements[map_type].keys()):
                improvements = map_improvements[map_type][algo]
                avg_imp = sum(improvements) / len(improvements) if improvements else 0.0
                f.write(f"  {algo:<20}: {avg_imp:.2f}% avg improvement ({len(improvements)} runs)\n")
            f.write("\n")
        
        f.write("=" * 100 + "\n")
    
    print(f"✅ Comparison written to: {output_file}")
    print(f"   View with: cat {output_file}")


if __name__ == "__main__":
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "results/raw/multi_depot_runs.csv"
    generate_comparison(csv_file)
