import csv
from pathlib import Path
from math import isclose
import importlib.util


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


def write_edges_csv_coords(path, coord_edges):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x1', 'y1', 'x2', 'y2'])
        for x1, y1, x2, y2 in coord_edges:
            writer.writerow([f"{x1:.6f}", f"{y1:.6f}", f"{x2:.6f}", f"{y2:.6f}"])


def test_coordinate_edge_exact_mapping(tmp_path):
    # Vertices exactly match coordinate edges (no tolerance needed)
    verts = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
    # edges specified by coordinates matching vertices exactly
    coord_edges = [
        (0.0, 0.0, 1.0, 0.0),
        (1.0, 0.0, 1.0, 1.0),
    ]

    vfile = tmp_path / 'nodes.csv'
    efile = tmp_path / 'edges_coords.csv'
    write_vertices_csv(vfile, verts, with_id=False)
    write_edges_csv_coords(efile, coord_edges)

    g = graph_loader.load_graph(str(vfile), str(efile), coord_tolerance=0.0)
    # should map 3 vertices
    assert g.n_vertices == 3
    # Should have mapped 2 edges
    assert g.n_edges == 2

    adj = g.get_adjacency_list()
    mst_p, wp = prim.prim(g.n_vertices, adj)
    mst_k, wk = kruskal.kruskal(g.n_vertices, g.edges)
    assert isclose(wp, wk, rel_tol=1e-9)

    valid, msg = validation.validate_mst(g.n_vertices, g.edges, mst_k)
    assert valid, msg


def test_coordinate_edge_with_tolerance(tmp_path):
    # Vertices and edges coordinates are slightly different; require tolerance
    verts = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
    # edge coords are slightly perturbed (0.005) from true vertex coords
    eps = 0.005
    coord_edges = [
        (0.0 + eps, 0.0 - eps, 2.0 + eps, 0.0 - eps),
        (2.0 + eps, 0.0 - eps, 2.0 + eps, 2.0 - eps),
        (2.0 + eps, 2.0 - eps, 0.0 + eps, 2.0 - eps),
    ]

    vfile = tmp_path / 'nodes2.csv'
    efile = tmp_path / 'edges_coords2.csv'
    write_vertices_csv(vfile, verts, with_id=True)
    write_edges_csv_coords(efile, coord_edges)

    # Use tolerance slightly larger than epsilon
    g = graph_loader.load_graph(str(vfile), str(efile), coord_tolerance=0.01)
    # Should have 4 vertices
    assert g.n_vertices == 4
    # Should have mapped 3 edges
    assert g.n_edges == 3

    adj = g.get_adjacency_list()
    mst_p, wp = prim.prim(g.n_vertices, adj)
    mst_k, wk = kruskal.kruskal(g.n_vertices, g.edges)
    assert isclose(wp, wk, rel_tol=1e-9)

    valid, msg = validation.validate_mst(g.n_vertices, g.edges, mst_k)
    assert valid, msg
