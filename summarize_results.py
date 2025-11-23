"""Summarize experiment CSV results.

Usage:
  python summarize_results.py [input_csv]

Reads the CSV (expects headers with: graph_name, algorithm, time_seconds, cpu_seconds, memory_mb, peak_memory_mb, mst_weight)
and writes a summary CSV `results/summary_results.csv` with mean/std/count grouped by graph_name and algorithm.
"""
import csv
import sys
from collections import defaultdict
from statistics import mean, pstdev


def summarize(input_csv: str, output_csv: str = 'results/summary_results.csv'):
    groups = defaultdict(list)

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get('graph_name', ''), row.get('algorithm', ''))
            try:
                t = float(row.get('time_seconds') or 0.0)
                cpu = float(row.get('cpu_seconds') or 0.0)
                mem = float(row.get('memory_mb') or 0.0)
                peak = float(row.get('peak_memory_mb') or 0.0)
                weight = float(row.get('mst_weight') or 0.0)
            except Exception:
                # skip rows with malformed numbers
                continue
            groups[key].append({'time': t, 'cpu': cpu, 'mem': mem, 'peak': peak, 'weight': weight})

    fieldnames = ['graph_name', 'algorithm', 'n_runs', 'mean_time', 'std_time', 'mean_cpu', 'std_cpu', 'mean_peak_mem', 'std_peak_mem', 'mean_weight', 'std_weight']
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for (graph, alg), rows in sorted(groups.items()):
            times = [r['time'] for r in rows]
            cpus = [r['cpu'] for r in rows]
            peaks = [r['peak'] for r in rows]
            weights = [r['weight'] for r in rows]
            n = len(rows)
            row_out = {
                'graph_name': graph,
                'algorithm': alg,
                'n_runs': n,
                'mean_time': f"{mean(times):.6f}",
                'std_time': f"{(pstdev(times) if n>1 else 0.0):.6f}",
                'mean_cpu': f"{mean(cpus):.6f}",
                'std_cpu': f"{(pstdev(cpus) if n>1 else 0.0):.6f}",
                'mean_peak_mem': f"{mean(peaks):.6f}",
                'std_peak_mem': f"{(pstdev(peaks) if n>1 else 0.0):.6f}",
                'mean_weight': f"{mean(weights):.6f}",
                'std_weight': f"{(pstdev(weights) if n>1 else 0.0):.6f}",
            }
            writer.writerow(row_out)


if __name__ == '__main__':
    # default to canonical results location when no argument is provided
    if len(sys.argv) < 2:
        input_csv = 'results/resultados_experimentos.csv'
    else:
        input_csv = sys.argv[1]

    # ensure results directory exists for output
    try:
        import os
        os.makedirs('results', exist_ok=True)
    except Exception:
        pass

    summarize(input_csv)
