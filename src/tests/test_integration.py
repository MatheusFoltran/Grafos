import csv
from pathlib import Path
from math import isclose

import importlib.util
from pathlib import Path


def _load_module(name: str, relpath: str):
    src = Path(__file__).resolve().parents[1] / relpath
    spec = importlib.util.spec_from_file_location(name, str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


graph_loader = _load_module('graph_loader', 'graph_loader.py')
prim = _load_module('prim', 'prim.py')
kruskal = _load_module('kruskal', 'kruskal.py')
validation = _load_module('validation', 'validation.py')


def write_vertices_csv(path, rows, with_id=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if with_id:
            writer.writerow(['id', 'x', 'y'])
            for i, (x, y) in enumerate(rows, start=1):
                writer.writerow([i, f"{x:.6f}", f"{y:.6f}"])
        else:
            writer.writerow(['x', 'y'])
            for x, y in rows:
                writer.writerow([f"{x:.6f}", f"{y:.6f}"])


def write_edges_csv_indices(path, edges, one_based=True):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target'])
        for u, v in edges:
            if one_based:
                writer.writerow([u + 1, v + 1])
            else:
                writer.writerow([u, v])


def test_prim_kruskal_agree_on_manual_graph():
    # Grafo simples (quadrado com diagonais)
    # Vértices em um quadrado unitário
    verts = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    # Arestas (todas as combinações sem repetição)
    edges = []
    from math import sqrt
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            x1, y1 = verts[i]
            x2, y2 = verts[j]
            w = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            edges.append((i, j, w))

    # Construir adj list para Prim
    adj = [[] for _ in range(len(verts))]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    mst_p, w_p = prim.prim(len(verts), adj)
    mst_k, w_k = kruskal.kruskal(len(verts), edges)

    assert isclose(w_p, w_k, rel_tol=1e-9)

    # Validate using validate_mst (original_edges must include full set)
    valid_p, msg_p = validation.validate_mst(len(verts), edges, mst_p)
    valid_k, msg_k = validation.validate_mst(len(verts), edges, mst_k)
    assert valid_p and valid_k


def test_graph_loader_integration_with_algorithms(tmp_path):
    # Create a small graph on disk and load with graph_loader
    verts = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
    # connect as a ring
    edge_indices = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]  # includes one diagonal

    vfile = tmp_path / 'vertices.csv'
    efile = tmp_path / 'edges.csv'
    write_vertices_csv(vfile, verts, with_id=True)
    write_edges_csv_indices(efile, edge_indices, one_based=True)

    g = graph_loader.load_graph(str(vfile), str(efile), coord_tolerance=0.0)
    assert g.n_vertices == 4
    assert g.n_edges >= 4

    adj = g.get_adjacency_list()
    mst_p, wp = prim.prim(g.n_vertices, adj)
    mst_k, wk = kruskal.kruskal(g.n_vertices, g.edges)

    assert isclose(wp, wk, rel_tol=1e-9)

    valid, msg = validation.validate_mst(g.n_vertices, g.edges, mst_k)
    assert valid, msg
