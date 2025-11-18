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
    
    Args:
        vertices_file: arquivo CSV com coordenadas (x, y)
        edges_file: arquivo CSV com arestas (id_origem, id_destino)
    
    Returns:
        Objeto Graph com o grafo carregado
    """
    graph = Graph()
    coords = []
    
    # Ler vértices
    with open(vertices_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # pula cabeçalho se existir
        for row in reader:
            if len(row) >= 2:
                x, y = float(row[0]), float(row[1])
                vertex_id = graph.add_vertex(x, y)
                coords.append((x, y))
    
    # Ler arestas e calcular pesos
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # pula cabeçalho se existir
        for row in reader:
            if len(row) >= 2:
                u, v = int(row[0]), int(row[1])
                
                # Validar índices
                if 0 <= u < len(coords) and 0 <= v < len(coords):
                    x1, y1 = coords[u]
                    x2, y2 = coords[v]
                    weight = euclidean_distance(x1, y1, x2, y2)
                    graph.add_edge(u, v, weight)
    
    return graph


if __name__ == "__main__":
    # Teste básico
    print("Testando carregamento de grafo...")
    # Descomente e ajuste os caminhos para testar:
    # graph = load_graph("grafos/grafo1/vertices.csv", "grafos/grafo1/edges.csv")
    # print(f"Vértices: {graph.n_vertices}, Arestas: {graph.n_edges}")