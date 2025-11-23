import importlib.util
from pathlib import Path


def _load_module(name: str, relpath: str):
    # Resolve module from the project's `src/` directory to match package layout
    src = Path(__file__).resolve().parents[1] / 'src' / relpath
    spec = importlib.util.spec_from_file_location(name, str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


validation = _load_module('validation', 'validation.py')


def test_validate_mst_simple_valid():
    n = 3
    original = [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 2.0)]
    mst = [(0, 1, 1.0), (1, 2, 1.0)]
    valid, msg = validation.validate_mst(n, original, mst)
    assert valid
    assert 'válida' in msg.lower() or '✓' in msg


def test_validate_mst_invalid_cycle():
    n = 3
    original = [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 2.0)]
    mst_cycle = [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 2.0)]
    valid, msg = validation.validate_mst(n, original, mst_cycle)
    assert not valid
    assert 'ciclo' in msg.lower() or 'inválida' in msg.lower()
