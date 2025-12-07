"""
Módulo para carregar grafos a partir de arquivos CSV.

Formato esperado (conforme especificação UEM):
- Vértices: CSV com coordenadas UTM (id, x, y) ou (x, y)
- Arestas: CSV com pares de vértices (u, v)
- Peso: calculado pela distância euclidiana entre coordenadas

Autor: [Seu Nome/Equipe]
Disciplina: Algoritmos em Grafos - UEM
Data: Dezembro 2025
"""
import csv
import math
from typing import List, Tuple, Dict


class Graph:
    """
    Representação de um grafo ponderado não-direcionado.
    
    Estrutura simples para armazenar vértices (com coordenadas) e arestas
    (com pesos calculados por distância euclidiana).
    """
    
    def __init__(self):
        """Inicializa grafo vazio."""
        self.vertices: Dict[int, Tuple[float, float]] = {}  # id -> (x, y)
        self.edges: List[Tuple[int, int, float]] = []        # (u, v, peso)
        self.n_vertices = 0
        self.n_edges = 0
    
    def add_vertex(self, vertex_id: int, x: float, y: float):
        """
        Adiciona um vértice ao grafo.
        
        Args:
            vertex_id: identificador do vértice
            x, y: coordenadas UTM
        """
        if vertex_id not in self.vertices:
            self.vertices[vertex_id] = (x, y)
            self.n_vertices += 1
    
    def add_edge(self, u: int, v: int, weight: float):
        """
        Adiciona uma aresta ao grafo.
        
        Args:
            u, v: vértices conectados
            weight: peso da aresta (distância euclidiana)
        """
        self.edges.append((u, v, weight))
        self.n_edges += 1
    
    def get_adjacency_list(self) -> List[List[Tuple[int, float]]]:
        """
        Retorna lista de adjacências para uso no algoritmo de Prim.
        
        Returns:
            adj[u] = [(v1, peso1), (v2, peso2), ...]
        """
        # Encontrar ID máximo para dimensionar a lista
        if not self.vertices:
            return []
        
        max_id = max(self.vertices.keys())
        adj = [[] for _ in range(max_id + 1)]
        
        # Adicionar arestas (grafo não-direcionado)
        for u, v, weight in self.edges:
            adj[u].append((v, weight))
            adj[v].append((u, weight))
        
        return adj
    
    def get_vertex_mapping(self) -> Dict[int, int]:
        """
        Retorna mapeamento de IDs originais para índices 0-based contíguos.
        
        Útil quando IDs dos vértices não são contíguos (ex: 1, 5, 10, ...).
        
        Returns:
            Dicionário {id_original: índice_contíguo}
        """
        return {vid: idx for idx, vid in enumerate(sorted(self.vertices.keys()))}
    
    def normalize_to_zero_based(self) -> 'Graph':
        """
        Retorna novo grafo com IDs de vértices normalizados para 0-based contíguo.
        
        Necessário para algoritmos que assumem vértices 0, 1, 2, ..., n-1.
        
        Returns:
            Novo objeto Graph com IDs normalizados
        """
        mapping = self.get_vertex_mapping()
        
        new_graph = Graph()
        
        # Adicionar vértices com novos IDs
        for old_id, (x, y) in self.vertices.items():
            new_id = mapping[old_id]
            new_graph.add_vertex(new_id, x, y)
        
        # Adicionar arestas com novos IDs
        for u, v, weight in self.edges:
            new_u = mapping[u]
            new_v = mapping[v]
            new_graph.add_edge(new_u, new_v, weight)
        
        return new_graph


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calcula distância euclidiana entre dois pontos.
    
    Fórmula: d = √[(x₁-x₂)² + (y₁-y₂)²]
    
    Args:
        x1, y1: coordenadas do primeiro ponto
        x2, y2: coordenadas do segundo ponto
    
    Returns:
        Distância euclidiana
    """
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def load_graph(vertices_file: str, edges_file: str) -> Graph:
    """
    Carrega grafo a partir de arquivos CSV.
    
    Formato esperado (conforme especificação do trabalho):
    
    **Vértices (vertices.csv):**
    - Com header: id,x,y
    - Sem header: id,x,y (primeira linha de dados)
    - Coordenadas em sistema UTM (Universal Transverse Mercator)
    
    **Arestas (edges.csv):**
    - Com header: source,target ou u,v
    - Sem header: u,v (primeira linha de dados)
    - IDs devem corresponder aos IDs dos vértices
    
    **Peso das arestas:**
    Calculado automaticamente pela distância euclidiana entre vértices:
    d(vᵢ, vⱼ) = √[(xᵢ-xⱼ)² + (yᵢ-yⱼ)²]
    
    Args:
        vertices_file: caminho para CSV de vértices
        edges_file: caminho para CSV de arestas
    
    Returns:
        Objeto Graph com vértices e arestas carregados
    
    Raises:
        FileNotFoundError: se arquivos não existirem
        ValueError: se formato CSV for inválido
    
    Exemplo:
        >>> graph = load_graph('grafos/cidade1/vertices.csv', 
        ...                    'grafos/cidade1/edges.csv')
        >>> print(f"Vértices: {graph.n_vertices}, Arestas: {graph.n_edges}")
    """
    graph = Graph()
    
    # ===== CARREGAR VÉRTICES =====
    with open(vertices_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Ler primeira linha
        first_row = next(reader, None)
        if first_row is None:
            raise ValueError(f"Arquivo de vértices vazio: {vertices_file}")
        
        # Detectar se é header (texto) ou dados (números)
        is_header = False
        try:
            # Tentar converter para números
            int(first_row[0])
            float(first_row[1])
            float(first_row[2])
        except (ValueError, IndexError):
            # Primeira linha é header
            is_header = True
        
        # Processar primeira linha se for dados
        if not is_header:
            try:
                vertex_id = int(first_row[0])
                x = float(first_row[1])
                y = float(first_row[2])
                graph.add_vertex(vertex_id, x, y)
            except (ValueError, IndexError) as e:
                raise ValueError(f"Formato inválido no arquivo de vértices: {e}")
        
        # Processar linhas restantes
        for row in reader:
            if len(row) < 3:
                continue  # Pular linhas vazias ou incompletas
            
            try:
                vertex_id = int(row[0])
                x = float(row[1])
                y = float(row[2])
                graph.add_vertex(vertex_id, x, y)
            except (ValueError, IndexError):
                # Pular linha com formato inválido
                continue
    
    if graph.n_vertices == 0:
        raise ValueError(f"Nenhum vértice válido encontrado em: {vertices_file}")
    
    # ===== CARREGAR ARESTAS E CALCULAR PESOS =====
    # Set para deduplicar arestas (grafo não-direcionado)
    seen_edges = set()
    
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Ler primeira linha
        first_row = next(reader, None)
        if first_row is None:
            # Grafo sem arestas (vértices isolados) é válido
            return graph
        
        # Detectar se é header
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
                
                # Validar que vértices existem
                if u in graph.vertices and v in graph.vertices:
                    # Deduplicar: normalizar ordem (menor, maior)
                    edge_key = (min(u, v), max(u, v))
                    if edge_key not in seen_edges:
                        x1, y1 = graph.vertices[u]
                        x2, y2 = graph.vertices[v]
                        weight = euclidean_distance(x1, y1, x2, y2)
                        graph.add_edge(u, v, weight)
                        seen_edges.add(edge_key)
            except (ValueError, IndexError, KeyError):
                pass  # Pular aresta inválida
        
        # Processar linhas restantes
        for row in reader:
            if len(row) < 2:
                continue
            
            try:
                u = int(row[0])
                v = int(row[1])
                
                # Validar que vértices existem
                if u not in graph.vertices or v not in graph.vertices:
                    continue  # Pular aresta com vértice inexistente
                
                # Deduplicar: normalizar ordem (menor, maior)
                edge_key = (min(u, v), max(u, v))
                if edge_key in seen_edges:
                    continue  # Aresta duplicada
                
                # Calcular peso pela distância euclidiana
                x1, y1 = graph.vertices[u]
                x2, y2 = graph.vertices[v]
                weight = euclidean_distance(x1, y1, x2, y2)
                
                graph.add_edge(u, v, weight)
                seen_edges.add(edge_key)
            except (ValueError, IndexError, KeyError):
                continue  # Pular aresta inválida
    
    return graph