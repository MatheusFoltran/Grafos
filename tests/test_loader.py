import csv
from pathlib import Path
import importlib.util


def _load_module(name: str, relpath: str):
    # Resolve module from the project's `src/` directory to match package layout
    src = Path(__file__).resolve().parents[1] / 'src' / relpath
    spec = importlib.util.spec_from_file_location(name, str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


graph_loader = _load_module('graph_loader', 'graph_loader.py')


def test_load_graph_basic(tmp_path):
    # Create vertices file (no header, x,y)
    vfile = tmp_path / "vertices.csv"
    vfile.write_text("0,0\n1,0\n0,1\n")

    # Create edges file using 1-based indices
    efile = tmp_path / "edges.csv"
    efile.write_text("1,2\n2,3\n1,3\n")

    graph = graph_loader.load_graph(str(vfile), str(efile), coord_tolerance=0.0)
    assert graph.n_vertices == 3
    # three edges added
    assert graph.n_edges == 3
    # adjacency list length equals number of vertices
    adj = graph.get_adjacency_list()
    assert len(adj) == 3
