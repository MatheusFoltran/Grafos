"""Verify experiment results by re-running one execution per graph.

This script:
- discovers graphs under `Grafos/` (same logic as `experiments.py`)
- loads each graph with `graph_loader.load_graph`
- runs `prim` and `kruskal` once each
- validates the produced MSTs with `validation.validate_mst`
- compares computed weights/counts with `src/resultados_experimentos.csv`

Run from project root inside the virtualenv.
"""
from pathlib import Path
import csv
import math

from graph_loader import load_graph
from prim import prim
from kruskal import kruskal
from validation import validate_mst


def discover_graphs(root: Path):
    grafos_dir = root / 'Grafos'
    configs = []
    if not grafos_dir.exists():
        return configs
    for sub in sorted(grafos_dir.iterdir()):
        if not sub.is_dir():
            continue
        nodes = None
        edges = None
        for f in sub.iterdir():
            name = f.name.lower()
            if any(k in name for k in ('node', 'nodes', 'vert', 'vertices')) and nodes is None:
                nodes = str(f)
            if 'edge' in name and edges is None:
                edges = str(f)
        if nodes and edges:
            configs.append({'name': sub.name, 'vertices': nodes, 'edges': edges})
    return configs


def read_results(csv_path: Path):
    data = {}
    if not csv_path.exists():
        return data
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = (row['graph_name'], row['algorithm'])
            # keep first occurrence (repetition 1) for simple check
            if key in data:
                continue
            # parse numeric fields
            try:
                weight = float(row.get('mst_weight', 'nan'))
            except Exception:
                weight = float('nan')
            try:
                edges_count = int(row.get('mst_edges_count', 0))
            except Exception:
                edges_count = 0
            data[key] = {'mst_weight': weight, 'mst_edges_count': edges_count, 'raw': row}
    return data


def almost_equal(a, b, rel=1e-6, abs_tol=1e-6):
    if math.isnan(a) or math.isnan(b):
        return False
    return abs(a - b) <= max(rel * max(abs(a), abs(b)), abs_tol)


def main():
    project_root = Path(__file__).resolve().parents[1]
    graphs = discover_graphs(project_root)
    if not graphs:
        print('No graphs found under Grafos/.')
        return 1

    csv_path = project_root / 'src' / 'resultados_experimentos.csv'
    reported = read_results(csv_path)

    overall_ok = True
    for cfg in graphs:
        name = cfg['name']
        print('\n' + '='*60)
        print(f'Graph: {name}')
        print('='*60)
        try:
            g = load_graph(cfg['vertices'], cfg['edges'], coord_tolerance=0.0)
        except Exception as e:
            print('  ERROR loading graph:', e)
            overall_ok = False
            continue

        print(f"  vertices={g.n_vertices}, edges={g.n_edges}")

        # Run Prim
        prim_result = prim(g.n_vertices, g.get_adjacency_list())
        prim_edges, prim_weight = prim_result
        prim_valid, prim_msg = validate_mst(g.n_vertices, g.edges, prim_edges)

        # Run Kruskal
        kruskal_result = kruskal(g.n_vertices, g.edges)
        kruskal_edges, kruskal_weight = kruskal_result
        kruskal_valid, kruskal_msg = validate_mst(g.n_vertices, g.edges, kruskal_edges)

        print(f"  Prim:   weight={prim_weight:.6f}, edges={len(prim_edges)}, valid={prim_valid}")
        print(f"  Kruskal:weight={kruskal_weight:.6f}, edges={len(kruskal_edges)}, valid={kruskal_valid}")

        # compare with reported CSV values (first repetition)
        r_prim = reported.get((name, 'prim'))
        r_krus = reported.get((name, 'kruskal'))

        if r_prim:
            csv_w = r_prim['mst_weight']
            csv_e = r_prim['mst_edges_count']
            ok_w = almost_equal(csv_w, prim_weight, rel=1e-6, abs_tol=1e-4)
            ok_e = (csv_e == len(prim_edges))
            print(f"  CSV Prim: weight={csv_w:.6f}, edges={csv_e} -> weight_match={ok_w}, edges_match={ok_e}")
            if not (ok_w and ok_e):
                overall_ok = False
        else:
            print('  No CSV entry for Prim')
            overall_ok = False

        if r_krus:
            csv_w = r_krus['mst_weight']
            csv_e = r_krus['mst_edges_count']
            ok_w = almost_equal(csv_w, kruskal_weight, rel=1e-6, abs_tol=1e-4)
            ok_e = (csv_e == len(kruskal_edges))
            print(f"  CSV Kruskal: weight={csv_w:.6f}, edges={csv_e} -> weight_match={ok_w}, edges_match={ok_e}")
            if not (ok_w and ok_e):
                overall_ok = False
        else:
            print('  No CSV entry for Kruskal')
            overall_ok = False

        # compare prim vs kruskal
        same = almost_equal(prim_weight, kruskal_weight, rel=1e-9, abs_tol=1e-6)
        print(f"  Prim vs Kruskal weight equal? {same} (diff={abs(prim_weight-kruskal_weight):.9f})")

    print('\n' + '='*60)
    if overall_ok:
        print('Verification PASSED: computed values match CSV (within tolerances).')
        return 0
    else:
        print('Verification FAILED: discrepancies found. Inspect output above.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
