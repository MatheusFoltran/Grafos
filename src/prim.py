import heapq
from typing import List, Tuple


def prim(n_vertices: int, adjacencias: List[List[Tuple[int, float]]]) -> Tuple[List[Tuple[int, int, float]], float]:
    # Algoritmo de Prim usando heap de vértices
    if n_vertices == 0:
        return [], 0.0
    
    arestas_arvore = []
    peso_total = 0.0
    
    visitado = [False] * n_vertices
    custo = [float('inf')] * n_vertices
    pai = [-1] * n_vertices
    
    # Processa cada componente conexa separadamente (gera floresta se desconexo)
    for vertice_inicial in range(n_vertices):
        if visitado[vertice_inicial]:
            continue
        
        custo[vertice_inicial] = 0.0
        fila_prioridade = [(0.0, vertice_inicial)]
        
        while fila_prioridade:
            custo_atual, vertice = heapq.heappop(fila_prioridade)
            
            if visitado[vertice]:
                continue
            
            visitado[vertice] = True
            peso_total += custo_atual
            
            if pai[vertice] != -1:
                arestas_arvore.append((pai[vertice], vertice, custo_atual))
            
            for v, peso in adjacencias[vertice]:
                if not visitado[v] and peso < custo[v]:
                    custo[v] = peso
                    pai[v] = vertice
                    heapq.heappush(fila_prioridade, (peso, v))
    
    return arestas_arvore, peso_total


def validar_mst_local(n_vertices: int, adjacencias: List[List[Tuple[int, float]]], 
                 arestas_mst: List[Tuple[int, int, float]]):

    erros = []
    valido = True
    
    # Constrói conjunto de arestas do grafo original
    conjunto_arestas = set()
    for u in range(len(adjacencias)):
        for v, peso in adjacencias[u]:
            conjunto_arestas.add((min(u, v), max(u, v), peso))
    
    # Verifica se todas as arestas da MST existem no grafo
    for u, v, peso in arestas_mst:
        aresta_normalizada = (min(u, v), max(u, v), peso)
        if aresta_normalizada not in conjunto_arestas:
            valido = False
            erros.append(f"Aresta ({u}, {v}, {peso}) não existe no grafo")
    
    # Verifica se forma ciclo usando Union-Find
    pai = list(range(n_vertices))
    
    def buscar(x):
        if pai[x] != x:
            pai[x] = buscar(pai[x])
        return pai[x]
    
    def unir(x, y):
        px, py = buscar(x), buscar(y)
        if px == py:
            return False
        pai[px] = py
        return True
    
    for u, v, _ in arestas_mst:
        if not unir(u, v):
            valido = False
            erros.append(f"Ciclo detectado: aresta ({u}, {v})")
    
    # Confere se o número de arestas é válido
    if len(arestas_mst) != n_vertices - 1:
        print(f"MST tem número de arestas diferente do esperado")
    
    return valido, erros