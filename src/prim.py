"""
Implementação do algoritmo de Prim usando heap de prioridade.
Usa heapq para selecionar o vértice de menor custo.
Funciona com grafos desconexos (retorna floresta geradora).
"""
import heapq
from typing import List, Tuple


def prim(n_vertices: int, adj: List[List[Tuple[int, float]]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Algoritmo de Prim para MST usando heap.
    
    Args:
        n_vertices: número de vértices
        adj: lista de adjacências adj[u] = [(v, peso), ...]
    
    Returns:
        (mst_edges, total_weight) - arestas da MST e peso total
    """
    if n_vertices == 0:
        return [], 0.0
    
    mst_edges = []
    total_weight = 0.0
    
    in_mst = [False] * n_vertices
    key = [float('inf')] * n_vertices
    parent = [-1] * n_vertices
    
    # processar cada componente conexa
    for start_vertex in range(n_vertices):
        if in_mst[start_vertex]:
            continue
        
        key[start_vertex] = 0.0
        heap = [(0.0, start_vertex)]
        
        while heap:
            curr_key, u = heapq.heappop(heap)
            
            if in_mst[u]:  # já processado
                continue
            
            in_mst[u] = True
            total_weight += curr_key
            
            if parent[u] != -1:
                mst_edges.append((parent[u], u, curr_key))
            
            # atualizar vizinhos
            for v, weight in adj[u]:
                if not in_mst[v] and weight < key[v]:
                    key[v] = weight
                    parent[v] = u
                    heapq.heappush(heap, (weight, v))
    
    return mst_edges, total_weight


def validate_mst(n_vertices: int, adj: List[List[Tuple[int, float]]], 
                 mst_edges: List[Tuple[int, int, float]]) -> dict:
    """
    Valida se a MST está correta.
    
    Args:
        n_vertices: número de vértices
        adj: lista de adjacências original
        mst_edges: MST calculada
    
    Returns:
        Dicionário com resultados da validação
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    # Construir conjunto de arestas do grafo original
    edge_set = set()
    for u in range(len(adj)):
        for v, weight in adj[u]:
            edge_set.add((min(u, v), max(u, v), weight))
    
    # Verificar se todas as arestas da MST existem no grafo
    for u, v, weight in mst_edges:
        normalized = (min(u, v), max(u, v), weight)
        if normalized not in edge_set:
            result['is_valid'] = False
            result['errors'].append(f"Aresta ({u}, {v}, {weight}) não existe no grafo")
    
    # Verificar se forma ciclo usando Union-Find
    parent = list(range(n_vertices))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        parent[px] = py
        return True
    
    for u, v, _ in mst_edges:
        if not union(u, v):
            result['is_valid'] = False
            result['errors'].append(f"Ciclo detectado: aresta ({u}, {v})")
    
    # Contar componentes
    components = len(set(find(i) for i in range(n_vertices)))
    result['info']['n_components'] = components
    result['info']['n_edges'] = len(mst_edges)
    
    # Verificar número de arestas
    if len(mst_edges) == n_vertices - 1:
        result['info']['is_spanning_tree'] = True
    else:
        result['warnings'].append(
            f"MST tem {len(mst_edges)} arestas, esperado {n_vertices - 1}. "
            f"Grafo tem {components} componente(s) conexa(s)."
        )
        result['info']['is_spanning_tree'] = False
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: Prim com Heap de Vértices")
    print("=" * 70)
    
    # Teste 1: Grafo conexo simples
    print("\n[Teste 1] Grafo conexo (4 vértices)")
    print("-" * 70)
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
    print(f"Arestas: {len(mst)} (esperado: {n-1})")
    
    validation = validate_mst(n, adj, mst)
    print(f"Validação: {'PASSOU' if validation['is_valid'] else 'FALHOU'}")
    
    # Teste 2: Grafo desconexo
    print("\n[Teste 2] Grafo desconexo (2 componentes)")
    print("-" * 70)
    n = 5
    adj = [
        [(1, 1.0)],           # 0
        [(0, 1.0), (2, 2.0)], # 1
        [(1, 2.0)],           # 2
        [(4, 3.0)],           # 3
        [(3, 3.0)]            # 4
    ]
    
    mst, weight = prim(n, adj)
    print(f"MST (floresta): {mst}")
    print(f"Peso total: {weight}")
    print(f"Arestas: {len(mst)}")
    
    validation = validate_mst(n, adj, mst)
    print(f"Validação: {'PASSOU' if validation['is_valid'] else 'FALHOU'}")
    print(f"Componentes conexas: {validation['info']['n_components']}")
    
    # Teste 3: Comparação com versão anterior
    print("\n[Teste 3] Benchmark de performance")
    print("-" * 70)
    
    # Criar grafo maior para teste
    import random
    n_large = 1000
    adj_large = [[] for _ in range(n_large)]
    
    # Grafo esparso tipo malha (cada vértice conecta com ~4 vizinhos)
    for i in range(n_large):
        for j in range(max(0, i-2), min(n_large, i+3)):
            if i != j:
                weight = random.uniform(1.0, 10.0)
                adj_large[i].append((j, weight))
    
    import time
    
    start = time.perf_counter()
    mst_large, weight_large = prim(n_large, adj_large)
    elapsed = time.perf_counter() - start
    
    print(f"Grafo com {n_large} vértices")
    print(f"Tempo: {elapsed*1000:.2f} ms")
    print(f"MST peso: {weight_large:.2f}")
    print(f"MST arestas: {len(mst_large)}")
    
    print("\n" + "=" * 70)
    print("TODOS OS TESTES CONCLUÍDOS")
    print("=" * 70)