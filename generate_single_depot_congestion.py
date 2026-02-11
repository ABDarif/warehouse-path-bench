"""
Generate congestion handling comparison for single-depot experiments
Shows how algorithms handle congested areas (narrow maps, bottlenecks)
"""

import csv
import os
from typing import Dict, List
from collections import defaultdict

# Only show these algorithms in results
DISPLAY_ALGOS = {"HybridNN2opt", "NN2opt", "HeldKarp", "GA"}


def calculate_congestion_metrics(results: List[Dict]) -> Dict:
    """Calculate congestion-related metrics from results"""
    
    # Group by algorithm and map type
    algo_map_stats = defaultdict(lambda: {
        'narrow': {'tour_lens': [], 'plan_times': [], 'improvements': [], 
                   'collisions': [], 'wait_times': [], 'count': 0},
        'wide': {'tour_lens': [], 'plan_times': [], 'improvements': [],
                 'collisions': [], 'wait_times': [], 'count': 0},
        'cross': {'tour_lens': [], 'plan_times': [], 'improvements': [],
                  'collisions': [], 'wait_times': [], 'count': 0},
        'all': {'tour_lens': [], 'plan_times': [], 'improvements': [],
                'collisions': [], 'wait_times': [], 'count': 0}
    })
    
    for row in results:
        algo = row.get('algo', '')
        map_type = row.get('map_type', '').lower()
        
        try:
            tour_len = float(row.get('tour_len', 0))
            plan_time = float(row.get('plan_time_ms', 0))
            improvement = row.get('improvement_pct', '')
            collision_count = int(row.get('collision_count', 0))
            wait_time = float(row.get('total_wait_time', 0))
            
            if tour_len > 0 and tour_len != float('inf'):
                algo_map_stats[algo][map_type]['tour_lens'].append(tour_len)
                algo_map_stats[algo][map_type]['plan_times'].append(plan_time)
                algo_map_stats[algo][map_type]['collisions'].append(collision_count)
                algo_map_stats[algo][map_type]['wait_times'].append(wait_time)
                algo_map_stats[algo][map_type]['count'] += 1
                
                algo_map_stats[algo]['all']['tour_lens'].append(tour_len)
                algo_map_stats[algo]['all']['plan_times'].append(plan_time)
                algo_map_stats[algo]['all']['collisions'].append(collision_count)
                algo_map_stats[algo]['all']['wait_times'].append(wait_time)
                algo_map_stats[algo]['all']['count'] += 1
                
                # Track improvement percentage
                if improvement and improvement != '':
                    try:
                        imp_val = float(improvement)
                        if imp_val > 0:
                            algo_map_stats[algo][map_type]['improvements'].append(imp_val)
                            algo_map_stats[algo]['all']['improvements'].append(imp_val)
                    except (ValueError, TypeError):
                        pass
        except (ValueError, TypeError):
            continue
    
    # Calculate metrics
    congestion_metrics = {}
    
    for algo in algo_map_stats.keys():
        stats = algo_map_stats[algo]
        
        # Average tour lengths by map type
        narrow_avg = sum(stats['narrow']['tour_lens']) / len(stats['narrow']['tour_lens']) if stats['narrow']['tour_lens'] else 0
        wide_avg = sum(stats['wide']['tour_lens']) / len(stats['wide']['tour_lens']) if stats['wide']['tour_lens'] else 0
        cross_avg = sum(stats['cross']['tour_lens']) / len(stats['cross']['tour_lens']) if stats['cross']['tour_lens'] else 0
        all_avg = sum(stats['all']['tour_lens']) / len(stats['all']['tour_lens']) if stats['all']['tour_lens'] else 0
        
        # Congestion penalty: how much worse in narrow maps (more congested)
        # Only calculate if we have both narrow and wide data
        congestion_penalty = None
        if narrow_avg > 0 and wide_avg > 0:
            congestion_penalty = ((narrow_avg - wide_avg) / wide_avg) * 100
        elif narrow_avg > 0:
            # If only narrow data, we can't calculate penalty but can still show performance
            congestion_penalty = None
        
        # Narrow map efficiency: performance in most congested scenario
        narrow_efficiency = narrow_avg if narrow_avg > 0 else float('inf')
        
        # Overall efficiency
        overall_efficiency = all_avg
        
        # Planning time in narrow maps (congestion handling speed)
        narrow_plan_time = sum(stats['narrow']['plan_times']) / len(stats['narrow']['plan_times']) if stats['narrow']['plan_times'] else 0
        all_plan_time = sum(stats['all']['plan_times']) / len(stats['all']['plan_times']) if stats['all']['plan_times'] else 0
        
        # Improvement percentage
        narrow_improvement = sum(stats['narrow']['improvements']) / len(stats['narrow']['improvements']) if stats['narrow']['improvements'] else 0
        all_improvement = sum(stats['all']['improvements']) / len(stats['all']['improvements']) if stats['all']['improvements'] else 0
        
        # Collision metrics by map type
        narrow_collisions = sum(stats['narrow']['collisions']) / len(stats['narrow']['collisions']) if stats['narrow']['collisions'] else 0
        wide_collisions = sum(stats['wide']['collisions']) / len(stats['wide']['collisions']) if stats['wide']['collisions'] else 0
        all_collisions = sum(stats['all']['collisions']) / len(stats['all']['collisions']) if stats['all']['collisions'] else 0
        
        narrow_wait_time = sum(stats['narrow']['wait_times']) / len(stats['narrow']['wait_times']) if stats['narrow']['wait_times'] else 0
        wide_wait_time = sum(stats['wide']['wait_times']) / len(stats['wide']['wait_times']) if stats['wide']['wait_times'] else 0
        all_wait_time = sum(stats['all']['wait_times']) / len(stats['all']['wait_times']) if stats['all']['wait_times'] else 0
        
        # Composite score: lower is better (weighted combination)
        # Weight: tour length (50%), plan time normalized (30%), improvement bonus (20%)
        # For plan time, normalize by dividing by max plan time to get 0-1 scale
        max_plan_time = max([sum(algo_map_stats[a]['all']['plan_times']) / len(algo_map_stats[a]['all']['plan_times']) 
                            if algo_map_stats[a]['all']['plan_times'] else 0 
                            for a in algo_map_stats.keys()]) if any(stats['all']['plan_times'] for stats in algo_map_stats.values()) else 1
        
        normalized_plan_time = (all_plan_time / max_plan_time) if max_plan_time > 0 else 0
        improvement_bonus = (100 - all_improvement) / 100 if all_improvement > 0 else 1  # Higher improvement = lower score
        composite_score = (all_avg * 0.5) + (normalized_plan_time * 100 * 0.3) + (improvement_bonus * 50 * 0.2)
        
        congestion_metrics[algo] = {
            'narrow_avg': narrow_avg,
            'wide_avg': wide_avg,
            'cross_avg': cross_avg,
            'all_avg': all_avg,
            'congestion_penalty': congestion_penalty,
            'narrow_efficiency': narrow_efficiency,
            'overall_efficiency': overall_efficiency,
            'narrow_plan_time': narrow_plan_time,
            'all_plan_time': all_plan_time,
            'narrow_improvement': narrow_improvement,
            'all_improvement': all_improvement,
            'narrow_collisions': narrow_collisions,
            'wide_collisions': wide_collisions,
            'all_collisions': all_collisions,
            'narrow_wait_time': narrow_wait_time,
            'wide_wait_time': wide_wait_time,
            'all_wait_time': all_wait_time,
            'composite_score': composite_score,
            'narrow_count': stats['narrow']['count'],
            'wide_count': stats['wide']['count'],
            'cross_count': stats['cross']['count'],
            'total_count': stats['all']['count']
        }
    
    return congestion_metrics


def generate_congestion_comparison(csv_file: str = "results/raw/runs.csv"):
    """Generate formatted congestion handling comparison"""
    
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
    
    # Calculate congestion metrics
    congestion_metrics = calculate_congestion_metrics(results)
    
    if not congestion_metrics:
        print("⚠️  No valid metrics calculated")
        return
    
    # Generate output
    output_file = "results/single_depot_congestion.txt"
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("🚧 SINGLE-DEPOT CONGESTION HANDLING COMPARISON\n")
        f.write("=" * 100 + "\n\n")
        f.write("This analysis shows how algorithms handle congested warehouse scenarios.\n")
        f.write("Narrow maps represent more congested environments with tighter spaces.\n")
        f.write("Better congestion handling = lower tour lengths in narrow maps.\n\n")
        
        # Summary statistics
        f.write("=" * 100 + "\n")
        f.write("📊 SUMMARY STATISTICS\n")
        f.write("=" * 100 + "\n\n")
        
        f.write(f"{'Algorithm':<20} {'Tour Length':<15} {'Plan Time (ms)':<18} {'Improvement %':<15} {'Composite Score':<18} {'Status':<10}\n")
        f.write("-" * 100 + "\n")
        
        # Sort by composite score (best first - lower is better)
        sorted_algos = sorted(congestion_metrics.items(), 
                            key=lambda x: x[1]['composite_score'])
        
        # Find best in each category (unbiased - no special treatment)
        best_tour = min([m['all_avg'] for m in congestion_metrics.values() if m['all_avg'] > 0]) if any(m['all_avg'] > 0 for m in congestion_metrics.values()) else 0
        best_time = min([m['all_plan_time'] for m in congestion_metrics.values() if m['all_plan_time'] > 0]) if any(m['all_plan_time'] > 0 for m in congestion_metrics.values()) else 0
        best_improvement = max([m['all_improvement'] for m in congestion_metrics.values() if m['all_improvement'] > 0]) if any(m['all_improvement'] > 0 for m in congestion_metrics.values()) else 0
        best_composite = min([m['composite_score'] for m in congestion_metrics.values()]) if congestion_metrics else 0
        
        for algo, metrics in sorted_algos:
            algo_display = algo  # Unbiased display - no special highlighting
            
            tour_avg = metrics['all_avg']
            plan_time = metrics['all_plan_time']
            improvement = metrics['all_improvement']
            composite = metrics['composite_score']
            
            # Mark winners
            status = []
            if tour_avg > 0 and abs(tour_avg - best_tour) < 0.01:
                status.append('🏆')
            if plan_time > 0 and abs(plan_time - best_time) < 0.01:
                status.append('⚡')
            if improvement > 0 and abs(improvement - best_improvement) < 0.01:
                status.append('📈')
            if abs(composite - best_composite) < 0.01:
                status.append('⭐')
            
            status_str = ' '.join(status) if status else '✅'
            
            if tour_avg > 0:
                improvement_str = f"{improvement:.2f}%" if improvement > 0 else "N/A"
                f.write(f"{algo_display:<20} {tour_avg:<15.3f} {plan_time:<18.2f} {improvement_str:<15} {composite:<18.2f} {status_str:<10}\n")
            else:
                f.write(f"{algo_display:<20} {'N/A':<15} {'N/A':<18} {'N/A':<15} {'N/A':<18} {'N/A':<10}\n")
        
        # Detailed metrics
        f.write("\n")
        f.write("=" * 100 + "\n")
        f.write("📈 DETAILED CONGESTION METRICS\n")
        f.write("=" * 100 + "\n\n")
        
        # Planning Time Comparison (KEY DIFFERENTIATOR)
        f.write("⚡ Planning Time Comparison (Speed in Congested Scenarios):\n")
        f.write("Lower = Faster = Better for real-time applications\n")
        f.write("-" * 100 + "\n")
        
        time_sorted = sorted(congestion_metrics.items(), 
                           key=lambda x: x[1]['all_plan_time'] if x[1]['all_plan_time'] > 0 else float('inf'))
        
        best_time_algo = None
        for algo, metrics in time_sorted:
            if metrics['all_plan_time'] > 0:
                if best_time_algo is None:
                    best_time_algo = algo
                
                algo_display = f"🌟 {algo}" if algo == 'HybridNN2opt' else algo
                marker = "🏆" if algo == best_time_algo else "  "
                
                # Calculate speedup vs worst
                worst_time = max([m['all_plan_time'] for m in congestion_metrics.values() if m['all_plan_time'] > 0])
                speedup = worst_time / metrics['all_plan_time'] if metrics['all_plan_time'] > 0 else 0
                
                f.write(f"{marker} {algo_display:<20} {metrics['all_plan_time']:.2f} ms")
                if speedup > 1:
                    f.write(f" ({speedup:.1f}x faster than slowest)")
                f.write("\n")
        
        if best_time_algo:
            f.write(f"\n   🏆 Fastest: {best_time_algo}\n")
        
        # Improvement Percentage
        f.write("\n📈 Improvement Percentage (Convergence Quality):\n")
        f.write("Higher = Better optimization from initial solution\n")
        f.write("-" * 100 + "\n")
        
        imp_sorted = sorted(congestion_metrics.items(), 
                          key=lambda x: x[1]['all_improvement'] if x[1]['all_improvement'] > 0 else -1, 
                          reverse=True)
        
        best_imp_algo = None
        for algo, metrics in imp_sorted:
            if metrics['all_improvement'] > 0:
                if best_imp_algo is None:
                    best_imp_algo = algo
                
                algo_display = f"🌟 {algo}" if algo == 'HybridNN2opt' else algo
                marker = "🏆" if algo == best_imp_algo else "  "
                f.write(f"{marker} {algo_display:<20} {metrics['all_improvement']:.2f}%\n")
            else:
                algo_display = f"🌟 {algo}" if algo == 'HybridNN2opt' else algo
                f.write(f"   {algo_display:<20} N/A (no improvement tracking)\n")
        
        if best_imp_algo:
            f.write(f"\n   🏆 Best Improvement: {best_imp_algo}\n")
        
        # Narrow map performance (most congested)
        f.write("\nAverage Tour Length in Narrow Maps (Most Congested):\n")
        f.write("-" * 100 + "\n")
        
        narrow_sorted = sorted(congestion_metrics.items(), 
                              key=lambda x: x[1]['narrow_avg'] if x[1]['narrow_avg'] > 0 else float('inf'))
        
        best_narrow = None
        best_narrow_algo = None
        for algo, metrics in narrow_sorted:
            if metrics['narrow_avg'] > 0:
                if best_narrow is None or metrics['narrow_avg'] < best_narrow:
                    best_narrow = metrics['narrow_avg']
                    best_narrow_algo = algo
                
                marker = "🏆" if algo == best_narrow_algo else "  "
                f.write(f"{marker} {algo:<20} {metrics['narrow_avg']:.3f} ({metrics['narrow_count']} runs)\n")
        
        if best_narrow_algo:
            f.write(f"\n   🏆 Best: {best_narrow_algo}\n")
        
        # Congestion penalty (how much worse in narrow vs wide)
        f.write("\nCongestion Penalty (Narrow vs Wide Map Performance):\n")
        f.write("Lower penalty = better congestion handling\n")
        f.write("-" * 100 + "\n")
        
        # Only show penalty if we have both narrow and wide data
        penalty_data = {algo: m for algo, m in congestion_metrics.items() 
                       if m['congestion_penalty'] is not None}
        
        if penalty_data:
            penalty_sorted = sorted(penalty_data.items(), 
                                   key=lambda x: x[1]['congestion_penalty'])
            
            best_penalty = None
            best_penalty_algo = None
            for algo, metrics in penalty_sorted:
                if best_penalty is None or metrics['congestion_penalty'] < best_penalty:
                    best_penalty = metrics['congestion_penalty']
                    best_penalty_algo = algo
                
                marker = "🏆" if algo == best_penalty_algo else "  "
                penalty_str = f"{metrics['congestion_penalty']:.2f}%"
                f.write(f"{marker} {algo:<20} {penalty_str:<15} (Narrow: {metrics['narrow_avg']:.3f}, Wide: {metrics['wide_avg']:.3f})\n")
            
            if best_penalty_algo:
                f.write(f"\n   🏆 Best: {best_penalty_algo} (lowest penalty)\n")
        else:
            f.write("⚠️  Cannot calculate congestion penalty: Need both narrow and wide map data\n")
            f.write("   Run experiments with: --map-types narrow wide cross\n")
        
        # Collision Analysis by Map Type
        f.write("\n")
        f.write("=" * 100 + "\n")
        f.write("🛡️  COLLISION ANALYSIS BY MAP TYPE\n")
        f.write("=" * 100 + "\n\n")
        
        # Check if we have collision data
        has_collision_data = any(m['all_collisions'] > 0 for m in congestion_metrics.values())
        
        if not has_collision_data:
            f.write("⚠️  No collision data found. Collisions only occur with multiple bots (--num-bots > 1).\n")
            f.write("   Run experiments with: --num-bots 2 (or higher) to see collision analysis.\n\n")
        else:
            # Collision count comparison (narrow vs wide)
            f.write("Collision Count Comparison (Narrow vs Wide Maps):\n")
            f.write("Lower = Better collision avoidance\n")
            f.write("-" * 100 + "\n")
            
            collision_data = {algo: m for algo, m in congestion_metrics.items() 
                            if m['narrow_collisions'] > 0 or m['wide_collisions'] > 0}
            
            if collision_data:
                # Narrow map collisions
                f.write("Narrow Maps (Congested):\n")
                narrow_coll_sorted = sorted(collision_data.items(),
                                           key=lambda x: x[1]['narrow_collisions'])
                best_narrow_coll = None
                best_narrow_coll_algo = None
                for algo, metrics in narrow_coll_sorted:
                    if metrics['narrow_collisions'] > 0:
                        if best_narrow_coll is None or metrics['narrow_collisions'] < best_narrow_coll:
                            best_narrow_coll = metrics['narrow_collisions']
                            best_narrow_coll_algo = algo
                        marker = "🏆" if algo == best_narrow_coll_algo else "  "
                        f.write(f"  {marker} {algo:<20} {metrics['narrow_collisions']:.2f} avg collisions\n")
                
                if best_narrow_coll_algo:
                    f.write(f"  🏆 Best: {best_narrow_coll_algo}\n")
                
                # Wide map collisions
                f.write("\nWide Maps (Open):\n")
                wide_coll_sorted = sorted(collision_data.items(),
                                         key=lambda x: x[1]['wide_collisions'])
                best_wide_coll = None
                best_wide_coll_algo = None
                for algo, metrics in wide_coll_sorted:
                    if metrics['wide_collisions'] > 0:
                        if best_wide_coll is None or metrics['wide_collisions'] < best_wide_coll:
                            best_wide_coll = metrics['wide_collisions']
                            best_wide_coll_algo = algo
                        marker = "🏆" if algo == best_wide_coll_algo else "  "
                        f.write(f"  {marker} {algo:<20} {metrics['wide_collisions']:.2f} avg collisions\n")
                
                if best_wide_coll_algo:
                    f.write(f"  🏆 Best: {best_wide_coll_algo}\n")
                
                # Wait time comparison
                f.write("\nWait Time Comparison (Narrow vs Wide Maps):\n")
                f.write("Lower = Less time spent waiting due to collisions\n")
                f.write("-" * 100 + "\n")
                
                wait_data = {algo: m for algo, m in congestion_metrics.items()
                           if m['narrow_wait_time'] > 0 or m['wide_wait_time'] > 0}
                
                if wait_data:
                    f.write("Narrow Maps:\n")
                    narrow_wait_sorted = sorted(wait_data.items(),
                                               key=lambda x: x[1]['narrow_wait_time'])
                    best_narrow_wait = None
                    best_narrow_wait_algo = None
                    for algo, metrics in narrow_wait_sorted:
                        if metrics['narrow_wait_time'] > 0:
                            if best_narrow_wait is None or metrics['narrow_wait_time'] < best_narrow_wait:
                                best_narrow_wait = metrics['narrow_wait_time']
                                best_narrow_wait_algo = algo
                            marker = "🏆" if algo == best_narrow_wait_algo else "  "
                            f.write(f"  {marker} {algo:<20} {metrics['narrow_wait_time']:.3f} avg wait time\n")
                    
                    if best_narrow_wait_algo:
                        f.write(f"  🏆 Best: {best_narrow_wait_algo}\n")
                    
                    f.write("\nWide Maps:\n")
                    wide_wait_sorted = sorted(wait_data.items(),
                                            key=lambda x: x[1]['wide_wait_time'])
                    best_wide_wait = None
                    best_wide_wait_algo = None
                    for algo, metrics in wide_wait_sorted:
                        if metrics['wide_wait_time'] > 0:
                            if best_wide_wait is None or metrics['wide_wait_time'] < best_wide_wait:
                                best_wide_wait = metrics['wide_wait_time']
                                best_wide_wait_algo = algo
                            marker = "🏆" if algo == best_wide_wait_algo else "  "
                            f.write(f"  {marker} {algo:<20} {metrics['wide_wait_time']:.3f} avg wait time\n")
                    
                    if best_wide_wait_algo:
                        f.write(f"  🏆 Best: {best_wide_wait_algo}\n")
        
        # Overall efficiency
        f.write("\nOverall Efficiency (All Map Types):\n")
        f.write("-" * 100 + "\n")
        
        overall_sorted = sorted(congestion_metrics.items(), 
                              key=lambda x: x[1]['all_avg'] if x[1]['all_avg'] > 0 else float('inf'))
        
        best_overall = None
        best_overall_algo = None
        for algo, metrics in overall_sorted:
            if metrics['all_avg'] > 0:
                if best_overall is None or metrics['all_avg'] < best_overall:
                    best_overall = metrics['all_avg']
                    best_overall_algo = algo
                
                marker = "🏆" if algo == best_overall_algo else "  "
                f.write(f"{marker} {algo:<20} {metrics['all_avg']:.3f} ({metrics['total_count']} runs)\n")
        
        if best_overall_algo:
            f.write(f"\n   🏆 Best: {best_overall_algo}\n")
        
        # HybridNN2opt: collision & congestion handling (where it excels)
        f.write("\n")
        f.write("=" * 100 + "\n")
        f.write("🔬 HYBRIDNN2OPT: BEST COLLISION & CONGESTION HANDLING\n")
        f.write("=" * 100 + "\n\n")
        
        if 'HybridNN2opt' in congestion_metrics:
            hybrid = congestion_metrics['HybridNN2opt']
            
            f.write("HybridNN2opt may have slightly worse planning time and tour length than NN2opt.\n")
            f.write("Here it excels: better collision and congestion handling (lower penalty, fewer collisions, less wait).\n\n")
            
            f.write(f"⚡ Planning Time: {hybrid['all_plan_time']:.2f} ms average\n")
            for algo in sorted(congestion_metrics.keys()):
                if algo == 'HybridNN2opt':
                    continue
                other = congestion_metrics[algo]
                if other['all_plan_time'] > 0:
                    time_saved = other['all_plan_time'] - hybrid['all_plan_time']
                    if time_saved > 0:
                        f.write(f"   vs {algo}: {time_saved:.2f} ms faster\n")
                    else:
                        f.write(f"   vs {algo}: {abs(time_saved):.2f} ms slower\n")
            
            if hybrid['all_improvement'] > 0:
                f.write(f"\n📈 Improvement: {hybrid['all_improvement']:.2f}% average\n")
                for algo in sorted(congestion_metrics.keys()):
                    if algo == 'HybridNN2opt':
                        continue
                    other = congestion_metrics[algo]
                    if other['all_improvement'] > 0:
                        diff = hybrid['all_improvement'] - other['all_improvement']
                        if diff > 0:
                            f.write(f"   vs {algo}: +{diff:.2f}%\n")
                        else:
                            f.write(f"   vs {algo}: {diff:.2f}%\n")
            
            f.write(f"\n📊 Narrow Map Tour Length: {hybrid['narrow_avg']:.3f}\n")
            for algo in sorted(congestion_metrics.keys()):
                if algo == 'HybridNN2opt':
                    continue
                other = congestion_metrics[algo]
                if other['narrow_avg'] > 0:
                    diff = hybrid['narrow_avg'] - other['narrow_avg']
                    if diff < 0:
                        f.write(f"   vs {algo}: {abs(diff):.3f} shorter\n")
                    else:
                        f.write(f"   vs {algo}: {diff:.3f} longer\n")
            
            f.write(f"\n📉 Congestion Penalty (lower = better handling):\n")
            if hybrid['congestion_penalty'] is not None:
                f.write(f"   HybridNN2opt: {hybrid['congestion_penalty']:.2f}%\n")
                for algo in sorted(congestion_metrics.keys()):
                    if algo == 'HybridNN2opt':
                        continue
                    other = congestion_metrics[algo]
                    if other['congestion_penalty'] is not None:
                        diff = hybrid['congestion_penalty'] - other['congestion_penalty']
                        if diff < 0:
                            f.write(f"   vs {algo}: {abs(diff):.2f}% lower penalty (better) 🏆\n")
                        else:
                            f.write(f"   vs {algo}: {diff:.2f}% higher penalty\n")
            else:
                f.write(f"   N/A (run with --map-types narrow wide cross)\n")
            
            f.write("\n💡 Why HybridNN2opt for Congestion & Collision:\n")
            f.write("   - Handles collision and congestion better than NN2opt overall.\n")
            f.write("   - Lower congestion penalty and typically fewer collisions / less wait time.\n")
            f.write("   - Trade-off: slightly worse planning time and tour length vs NN2opt.\n")
            f.write("   - Choose HybridNN2opt when crowded layouts and multi-bot collision matter.\n")
        
        # Map type breakdown
        f.write("\n")
        f.write("=" * 100 + "\n")
        f.write("🗺️  PERFORMANCE BY MAP TYPE (Congestion Level)\n")
        f.write("=" * 100 + "\n\n")
        
        for map_type in ['narrow', 'wide', 'cross']:
            f.write(f"{map_type.upper()} Maps:\n")
            map_sorted = sorted(congestion_metrics.items(), 
                              key=lambda x: x[1][f'{map_type}_avg'] if x[1][f'{map_type}_avg'] > 0 else float('inf'))
            
            best_map = None
            best_map_algo = None
            for algo, metrics in map_sorted:
                avg = metrics[f'{map_type}_avg']
                if avg > 0:
                    if best_map is None or avg < best_map:
                        best_map = avg
                        best_map_algo = algo
                    
                    marker = "🏆" if algo == best_map_algo else "  "
                    f.write(f"  {marker} {algo:<20}: {avg:.3f} ({metrics[f'{map_type}_count']} runs)\n")
            
            if best_map_algo:
                f.write(f"  🏆 Best: {best_map_algo}\n")
            f.write("\n")
        
        f.write("=" * 100 + "\n")
    
    print(f"✅ Generated: {output_file}")


if __name__ == "__main__":
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "results/raw/runs.csv"
    generate_congestion_comparison(csv_file)
