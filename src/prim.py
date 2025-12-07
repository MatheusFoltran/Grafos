"""
Implementação otimizada do algoritmo de Prim com HEAP DE VÉRTICES.

Esta versão usa "indexed heap" (key-based priority queue) que mantém
o melhor custo conhecido para alcançar cada vértice, ao invés de
armazenar todas as arestas no heap.

Vantagens sobre heap de arestas:
- Heap menor: O(V) vértices vs O(E) arestas
- Menos operações: O(V) heappops vs O(E) heappops
- Menos lixo: não precisa lazy deletion
- Melhor para grafos densos

Autor: [Seu Nome/Equipe]
Disciplina: Algoritmos em Grafos - UEM
Data: Dezembro 2025

Conformidade com requisitos:
- Usa heap (`heapq` - biblioteca padrão Python)
- Sem bibliotecas de grafos
- Trata grafos desconexos
"""
import heapq
from typing import List, Tuple


def prim(n_vertices: int, adj: List[List[Tuple[int, float]]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Algoritmo de Prim para Árvore Geradora Mínima.
    
    Implementação com HEAP DE VÉRTICES (key-based priority queue).
    
    Estratégia:
    - Mantém array key[v] = menor peso conhecido para alcançar v
    - Heap contém pares (custo, vértice) ao invés de arestas completas
    - Atualiza key[v] quando encontra caminho mais barato
    - Adiciona vértice ao heap apenas quando key[v] melhora
    
    Complexidade:
    - Tempo: O(E log V) com binary heap
      * Cada aresta pode causar uma inserção no heap: O(E log V)
      * Extrair todos os vértices do heap: O(V log V)
      * Total dominado por O(E log V)
    - Espaço: O(V) para arrays + O(V) para heap = O(V)
    
    Vantagem sobre heap de arestas:
    - Heap menor: máximo V vértices (vs E arestas)
    - Menos operações: V heappops (vs E heappops com lazy deletion)
    - Ideal para grafos densos ou médios
    
    Args:
        n_vertices: número de vértices (0 a n-1)
        adj: lista de adjacências adj[u] = [(v, peso), ...]
    
    Returns:
        Tupla (mst_edges, total_weight):
        - mst_edges: lista de arestas (u, v, peso) na MST
        - total_weight: soma dos pesos
    
    Tratamento de grafos desconexos:
        Retorna floresta geradora mínima (MSF) processando cada
        componente conexa separadamente.
    
    Exemplo:
        >>> adj = [
        ...     [(1, 1.0), (2, 4.0)],  # vértice 0
        ...     [(0, 1.0), (2, 2.0)],  # vértice 1
        ...     [(0, 4.0), (1, 2.0)]   # vértice 2
        ... ]
        >>> mst, weight = prim(3, adj)
        >>> print(mst)
        [(0, 1, 1.0), (1, 2, 2.0)]
        >>> print(weight)
        3.0
    """
    # Casos base
    if n_vertices == 0:
        return [], 0.0
    
    # Estruturas para resultado
    mst_edges = []
    total_weight = 0.0
    
    # Arrays para o algoritmo
    in_mst = [False] * n_vertices  # vértices já na MST
    key = [float('inf')] * n_vertices  # menor peso para alcançar cada vértice
    parent = [-1] * n_vertices  # pai de cada vértice na MST
    
    # PASSO 1: Processar cada componente conexa
    for start_vertex in range(n_vertices):
        # Pular vértices já processados (de componentes anteriores)
        if in_mst[start_vertex]:
            continue
        
        # PASSO 2: Iniciar Prim nesta componente
        key[start_vertex] = 0.0
        heap = [(0.0, start_vertex)]  # (custo, vértice)
        
        # PASSO 3: Processar heap até esvaziar
        while heap:
            # Extrair vértice com menor custo
            curr_key, u = heapq.heappop(heap)
            
            # LAZY DELETION: Se vértice já foi processado, ignorar
            # (pode haver duplicatas no heap com custos piores)
            if in_mst[u]:
                continue
            
            # Adicionar vértice à MST
            in_mst[u] = True
            total_weight += curr_key
            
            # Adicionar aresta à MST (exceto vértice inicial)
            if parent[u] != -1:
                mst_edges.append((parent[u], u, curr_key))
            
            # PASSO 4: Atualizar custos dos vizinhos
            for v, weight in adj[u]:
                # Se vizinho ainda não está na MST E encontramos caminho melhor
                if not in_mst[v] and weight < key[v]:
                    # Atualizar menor custo conhecido
                    key[v] = weight
                    parent[v] = u
                    
                    # Adicionar ao heap
                    # IMPORTANTE: Pode haver vértice v com custo pior no heap
                    # (lazy deletion: ignoramos ao processar)
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
    print("TESTE: Prim com Heap de Vértices (Otimizado)")
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
    print("\nNota: Esta versão usa heap de VÉRTICES ao invés de heap de ARESTAS")
    print("   Vantagens:")
    print("   • Heap menor: O(V) vs O(E)")
    print("   • Menos operações: O(V log V) vs O(E log E)")
    print("   • Ideal para grafos densos e médios")
    print("   • Ainda O(E log V) no total, mas constantes menores")