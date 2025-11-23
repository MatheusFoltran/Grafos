import importlib.util
from pathlib import Path


def load_testes_module():
    # Try several likely locations for testes.py (user may have moved it)
    here = Path(__file__).resolve().parent / "testes.py"
    src_root = Path(__file__).resolve().parents[1] / "testes.py"
    candidates = [here, src_root]
    src = None
    for c in candidates:
        if c.exists():
            src = c
            break
    if src is None:
        raise FileNotFoundError("Could not find testes.py in expected locations: {}".format(candidates))
    spec = importlib.util.spec_from_file_location("testes", str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generate_random_graph_basic():
    mod = load_testes_module()
    vertices, edges = mod.generate_random_graph(10, density=0.2)
    assert len(vertices) == 10
    # deve ser conectado: pelo menos n-1 arestas
    assert len(edges) >= 9
    # arestas não devem ter duplicatas (undirected)
    normalized = set((min(u, v), max(u, v)) for u, v in edges)
    assert len(normalized) == len(edges)


def test_generate_grid_graph_dimensions_and_edges():
    mod = load_testes_module()
    rows, cols = 3, 4
    vertices, edges = mod.generate_grid_graph(rows, cols, connection_prob=1.0)
    assert len(vertices) == rows * cols
    expected_edges = rows * (cols - 1) + (rows - 1) * cols
    assert len(edges) == expected_edges


def test_save_graph_writes_files(tmp_path):
    mod = load_testes_module()
    verts = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    eds = [(0, 1), (1, 2)]
    out = tmp_path / "outgraph"
    mod.save_graph(verts, eds, out)
    vfile = out / "vertices.csv"
    efile = out / "edges.csv"
    assert vfile.exists()
    assert efile.exists()
    # verificar linhas (header + 3 vértices)
    with open(vfile, "r", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    assert len(lines) == 1 + 3
    with open(efile, "r", encoding="utf-8") as f:
        lines2 = f.read().strip().splitlines()
    assert len(lines2) == 1 + 2
