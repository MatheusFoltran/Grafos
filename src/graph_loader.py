"""
Módulo para carregar grafos a partir de arquivos CSV.
"""
import csv
import math
from typing import List, Tuple, Dict

class Graph:
    """Representação de um grafo ponderado não-direcionado."""
    
    def __init__(self):
        self.vertices: Dict[Tuple[float, float], int] = {}  # (x, y) -> id
        self.edges: List[Tuple[int, int, float]] = []  # (u, v, peso)
        self.n_vertices = 0
        self.n_edges = 0
    
    def add_vertex(self, x: float, y: float) -> int:
        """Adiciona um vértice e retorna seu ID."""
        coord = (x, y)
        if coord not in self.vertices:
            self.vertices[coord] = self.n_vertices
            self.n_vertices += 1
        return self.vertices[coord]
    
    def add_edge(self, u: int, v: int, weight: float):
        """Adiciona uma aresta ao grafo."""
        self.edges.append((u, v, weight))
        self.n_edges += 1
    
    def get_adjacency_list(self) -> List[List[Tuple[int, float]]]:
        """Retorna lista de adjacências: adj[u] = [(v, peso), ...]"""
        adj = [[] for _ in range(self.n_vertices)]
        for u, v, w in self.edges:
            adj[u].append((v, w))
            adj[v].append((u, w))
        return adj


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calcula distância euclidiana entre dois pontos."""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def load_graph(vertices_file: str, edges_file: str) -> Graph:
    """
    Carrega um grafo a partir de arquivos CSV.

    Suporta formatos encontrados no repositório:
    - `Nodes*.csv` com colunas (id, x, y) ou (x, y) (id pode ser 1-based)
    - `Edges*.csv` com colunas (source, target) contendo índices (1-based ou 0-based)
      OU com 4 colunas representando coordenadas (x1, y1, x2, y2).

    Retorna um objeto `Graph` com índices internos 0-based.
    """
    graph = Graph()

    # Mapeamentos auxiliares
    id_to_index = {}        # original id (from file) -> internal index (0-based)
    coords = []             # list of (x, y) indexed by internal index
    coord_to_index = {}     # rounded coordinate -> internal index (for coordinate-based edges)

    # --- Ler vértices (suporta header com 'id' ou apenas x,y) ---
    with open(vertices_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)

        # Detectar se primeiro campo é um header textual
        has_id_col = False
        if header is not None and any(h.lower() in ('id', 'idx') for h in header):
            # temos uma linha de cabeçalho que inclui 'id'
            has_id_col = True
        else:
            # Se header parece numérico, tratamos como primeira linha de dados
            try:
                # tentar converter primeira campo para float para checar
                if header is not None:
                    float(header[0])
                    # header é na verdade uma linha de dados
                    # processá-la como primeira linha
                    row0 = header
                    header = None
                    # process row0 abaixo
                    rows = [row0] + list(reader)
                else:
                    rows = list(reader)
            except Exception:
                rows = list(reader)

        if has_id_col:
            # Reabrir e usar DictReader para robustez
            f.seek(0)
            dreader = csv.DictReader(f)
            for row in dreader:
                # Expect columns like 'id', 'x', 'y' (nomes podem variar)
                try:
                    orig_id = int(row.get('id') or row.get('ID') or row.get('Id'))
                except Exception:
                    # fallback: try first column
                    try:
                        orig_id = int(next(iter(row.values())))
                    except Exception:
                        continue

                # localizar x,y
                x = float(row.get('x') or row.get('X') or row.get('lon') or row.get('xc') or list(row.values())[1])
                y = float(row.get('y') or row.get('Y') or row.get('lat') or row.get('yc') or list(row.values())[2])

                internal = len(coords)
                id_to_index[orig_id] = internal
                coords.append((x, y))
                coord_to_index[(round(x, 6), round(y, 6))] = internal
        else:
            # header is either None or data; we already collected rows
            if 'rows' not in locals():
                rows = list(reader)

            for row in rows:
                if len(row) < 2:
                    continue
                try:
                    x = float(row[0])
                    y = float(row[1])
                except Exception:
                    continue

                internal = len(coords)
                coords.append((x, y))
                coord_to_index[(round(x, 6), round(y, 6))] = internal

            # Atualizar o objeto graph com os vértices lidos (importante para get_adjacency_list)
            for idx, (x, y) in enumerate(coords):
                # usar coordenadas reais como chave para permitir buscas futuras
                graph.vertices[(x, y)] = idx
            graph.n_vertices = len(coords)

    # Caso o branch com 'id' tenha sido tomado acima, garantir que graph também seja populado
    if graph.n_vertices == 0:
        for idx, (x, y) in enumerate(coords):
            graph.vertices[(x, y)] = idx
        graph.n_vertices = len(coords)

    # --- Ler arestas e calcular pesos (suporta índices 1-based/0-based ou coordenadas) ---
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)

        # decide format by header or by number of columns per row
        # if header contains non-numeric names like 'source'/'target', treat as indices
        header_names = []
        if header:
            header_names = [h.lower() for h in header]

        for row in reader:
            if len(row) < 2:
                continue

            # Case 1: two integer-like columns -> indices
            if len(row) >= 2:
                try:
                    u_raw = int(row[0])
                    v_raw = int(row[1])
                    # Map original id -> internal index if present
                    if u_raw in id_to_index:
                        u = id_to_index[u_raw]
                    else:
                        # assume 1-based indices (common in shapefile exports)
                        u = u_raw - 1

                    if v_raw in id_to_index:
                        v = id_to_index[v_raw]
                    else:
                        v = v_raw - 1

                    # Validate indices
                    if 0 <= u < len(coords) and 0 <= v < len(coords) and u != v:
                        x1, y1 = coords[u]
                        x2, y2 = coords[v]
                        weight = euclidean_distance(x1, y1, x2, y2)
                        graph.add_edge(u, v, weight)
                    continue
                except Exception:
                    # not integers — try coordinate-based edge
                    pass

            # Case 2: coordinate pairs (x1,y1,x2,y2)
            # Accept rows with 4 numeric columns
            if len(row) >= 4:
                try:
                    x1 = float(row[0]); y1 = float(row[1]); x2 = float(row[2]); y2 = float(row[3])
                    key1 = (round(x1, 6), round(y1, 6))
                    key2 = (round(x2, 6), round(y2, 6))
                    if key1 in coord_to_index and key2 in coord_to_index:
                        u = coord_to_index[key1]
                        v = coord_to_index[key2]
                        if u != v:
                            weight = euclidean_distance(x1, y1, x2, y2)
                            graph.add_edge(u, v, weight)
                except Exception:
                    continue

    return graph


if __name__ == "__main__":
    # Teste básico
    print("Testando carregamento de grafo...")
    # Descomente e ajuste os caminhos para testar:
    # graph = load_graph("grafos/grafo1/vertices.csv", "grafos/grafo1/edges.csv")
    # print(f"Vértices: {graph.n_vertices}, Arestas: {graph.n_edges}")