"""
Carrega grafos de arquivos CSV.
Vértices com coordenadas UTM, arestas com pares de IDs.
Peso calculado por distância euclidiana.
"""
import csv
import math
from typing import List, Tuple, Dict


class Graph:
    """Grafo ponderado não-direcionado com vértices e arestas."""
    
    def __init__(self):
        self.vertices: Dict[int, Tuple[float, float]] = {}  # id -> (x, y)
        self.edges: List[Tuple[int, int, float]] = []  # (u, v, peso)
        self.n_vertices = 0
        self.n_edges = 0
    
    def add_vertex(self, vertex_id: int, x: float, y: float):
        if vertex_id not in self.vertices:
            self.vertices[vertex_id] = (x, y)
            self.n_vertices += 1
    
    def add_edge(self, u: int, v: int, weight: float):
        self.edges.append((u, v, weight))
        self.n_edges += 1
    
    def get_adjacency_list(self) -> List[List[Tuple[int, float]]]:
        """Retorna lista de adjacências adj[u] = [(v, peso), ...]."""
        if not self.vertices:
            return []
        
        max_id = max(self.vertices.keys())
        adj = [[] for _ in range(max_id + 1)]
        
        for u, v, weight in self.edges:
            adj[u].append((v, weight))
            adj[v].append((u, weight))
        
        return adj
    
    def get_vertex_mapping(self) -> Dict[int, int]:
        """Converte IDs dos vértices para sequência 0, 1, 2, 3..."""
        return {vid: idx for idx, vid in enumerate(sorted(self.vertices.keys()))}
    
    def normalize_to_zero_based(self) -> 'Graph':
        """Converte IDs dos vértices para sequência 0, 1, 2... (necessário pros algoritmos)."""
        mapping = self.get_vertex_mapping()
        new_graph = Graph()
        
        for old_id, (x, y) in self.vertices.items():
            new_graph.add_vertex(mapping[old_id], x, y)
        
        for u, v, weight in self.edges:
            new_graph.add_edge(mapping[u], mapping[v], weight)
        
        return new_graph


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calcula distância euclidiana entre dois pontos."""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def load_graph(vertices_file: str, edges_file: str) -> Graph:
    """
    Carrega grafo de CSVs (vértices com coordenadas UTM, arestas com IDs).
    Peso calculado por distância euclidiana.
    """
    graph = Graph()
    
    # carregar vértices
    with open(vertices_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        first_row = next(reader, None)
        if first_row is None:
            raise ValueError(f"Arquivo de vértices vazio: {vertices_file}")
        
        # detectar se tem header
        is_header = False
        try:
            int(first_row[0])
            float(first_row[1])
            float(first_row[2])
        except (ValueError, IndexError):
            is_header = True
        
        if not is_header:
            try:
                vertex_id = int(first_row[0])
                x = float(first_row[1])
                y = float(first_row[2])
                graph.add_vertex(vertex_id, x, y)
            except (ValueError, IndexError) as e:
                raise ValueError(f"Formato inválido no arquivo de vértices: {e}")
        
        for row in reader:
            if len(row) < 3:
                continue
            
            try:
                vertex_id = int(row[0])
                x = float(row[1])
                y = float(row[2])
                graph.add_vertex(vertex_id, x, y)
            except (ValueError, IndexError):
                continue
    
    if graph.n_vertices == 0:
        raise ValueError(f"Nenhum vértice válido encontrado em: {vertices_file}")
    
    # carregar arestas e calcular pesos
    seen_edges = set()
    
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Ler primeira linha
        first_row = next(reader, None)
        if first_row is None:
            return graph
        
        is_header = False
        try:
            int(first_row[0])
            int(first_row[1])
        except (ValueError, IndexError):
            is_header = True
        
        # Processar primeira linha se for dados
        if not is_header:
            try:
                u = int(first_row[0])
                v = int(first_row[1])
                
                if u in graph.vertices and v in graph.vertices:
                    edge_key = (min(u, v), max(u, v))
                    if edge_key not in seen_edges:
                        x1, y1 = graph.vertices[u]
                        x2, y2 = graph.vertices[v]
                        weight = euclidean_distance(x1, y1, x2, y2)
                        graph.add_edge(u, v, weight)
                        seen_edges.add(edge_key)
            except (ValueError, IndexError, KeyError):
                pass
        
        # Processar linhas restantes
        for row in reader:
            if len(row) < 2:
                continue
            
            try:
                u = int(row[0])
                v = int(row[1])
                
                if u not in graph.vertices or v not in graph.vertices:
                    continue
                
                edge_key = (min(u, v), max(u, v))
                if edge_key in seen_edges:
                    continue
                
                x1, y1 = graph.vertices[u]
                x2, y2 = graph.vertices[v]
                weight = euclidean_distance(x1, y1, x2, y2)
                
                graph.add_edge(u, v, weight)
                seen_edges.add(edge_key)
            except (ValueError, IndexError, KeyError):
                continue
    
    return graph