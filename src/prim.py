"""
Implementação do algoritmo de Prim para Árvore Geradora Mínima.
Utiliza heap (min-heap) para seleção eficiente de arestas.
"""
import heapq
from typing import List, Tuple, Set


def prim(n_vertices: int, adj: List[List[Tuple[int, float]]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Algoritmo de Prim para encontrar a Árvore Geradora Mínima (MST).
    
    Args:
        n_vertices: número de vértices no grafo
        adj: lista de adjacências adj[u] = [(v, peso), ...]
    
    Returns:
        (mst_edges, total_weight): lista de arestas da MST e peso total
        - mst_edges: lista de tuplas (u, v, peso)
        - total_weight: soma dos pesos das arestas na MST
    """
    if n_vertices == 0:
        return [], 0.0
    
    mst_edges = []
    total_weight = 0.0
    visited = [False] * n_vertices
    min_heap = []
    
    # Encontrar todas as componentes conexas
    for start_vertex in range(n_vertices):
        if visited[start_vertex]:
            continue
        
        # Iniciar Prim a partir de start_vertex
        visited[start_vertex] = True
        
        # Adicionar todas as arestas do vértice inicial ao heap
        for neighbor, weight in adj[start_vertex]:
            heapq.heappush(min_heap, (weight, start_vertex, neighbor))
        
        # Processar heap até esvaziar ou visitar todos os vértices da componente
        while min_heap:
            weight, u, v = heapq.heappop(min_heap)
            
            # Se o vértice destino já foi visitado, ignorar
            if visited[v]:
                continue
            
            # Adicionar aresta à MST
            visited[v] = True
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # Adicionar arestas do novo vértice ao heap
            for neighbor, edge_weight in adj[v]:
                if not visited[neighbor]:
                    heapq.heappush(min_heap, (edge_weight, v, neighbor))
    
    return mst_edges, total_weight


def validate_mst_prim(n_vertices: int, mst_edges: List[Tuple[int, int, float]]) -> bool:
    """
    Valida se o resultado é uma floresta geradora válida.
    
    Args:
        n_vertices: número de vértices
        mst_edges: arestas retornadas pelo algoritmo
    
    Returns:
        True se válida, False caso contrário
    """
    # Verificar se não há ciclos usando Union-Find simples
    parent = list(range(n_vertices))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False  # Ciclo detectado
        parent[px] = py
        return True
    
    for u, v, _ in mst_edges:
        if not union(u, v):
            return False
    
    return True


if __name__ == "__main__":
    # Teste com grafo simples
    print("Testando Prim...")
    
    # Grafo de exemplo: triângulo
    #   0
    #  /|\
    # 1-2-3
    n = 4
    adj = [
        [(1, 1.0), (2, 4.0), (3, 3.0)],  # 0
        [(0, 1.0), (2, 2.0)],            # 1
        [(0, 4.0), (1, 2.0), (3, 5.0)],  # 2
        [(0, 3.0), (2, 5.0)]             # 3
    ]
    
    mst, weight = prim(n, adj)
    print(f"MST: {mst}")
    print(f"Peso total: {weight}")
    print(f"Válida: {validate_mst_prim(n, mst)}")