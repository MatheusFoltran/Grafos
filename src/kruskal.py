from typing import List, Tuple


class UnionFind:
    
    def __init__(self, n: int):
        self.pai = list(range(n))
        self.altura = [0] * n
        self.num_componentes = n
    
    def find(self, x: int) -> int:
        if self.pai[x] != x:
            self.pai[x] = self.find(self.pai[x])
        return self.pai[x]
    
    def union(self, x: int, y: int) -> bool:
        raiz_x = self.find(x)
        raiz_y = self.find(y)
        
        if raiz_x == raiz_y:
            return False
        
        # unir pela altura
        if self.altura[raiz_x] < self.altura[raiz_y]:
            self.pai[raiz_x] = raiz_y
        elif self.altura[raiz_x] > self.altura[raiz_y]:
            self.pai[raiz_y] = raiz_x
        else:
            self.pai[raiz_y] = raiz_x
            self.altura[raiz_x] += 1
        
        self.num_componentes -= 1
        return True
    
    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


def _busca_raiz_com_compressao(vertice: int, pai: List[int]) -> int:
    """Busca iterativa da raiz com compressão de caminho."""
    raiz = vertice
    while pai[raiz] != raiz:
        raiz = pai[raiz]
    
    # comprimir o caminho
    atual = vertice
    while atual != raiz:
        proximo = pai[atual]
        pai[atual] = raiz
        atual = proximo
    
    return raiz


def kruskal(n_vertices: int, arestas: List[Tuple[int, int, float]]) -> Tuple[List[Tuple[int, int, float]], float]:
    # Algoritmo de Kruskal usando Union Find
    if n_vertices == 0:
        return [], 0.0
    
    if not arestas:
        return [], 0.0
    
    # Ordena arestas por peso
    arestas_ordenadas = sorted(arestas, key=lambda aresta: aresta[2])
    
    pai = list(range(n_vertices))
    altura = [0] * n_vertices
    
    arestas_mst = []
    peso_total = 0.0
    max_arestas = n_vertices - 1
    
    for u, v, peso in arestas_ordenadas:
        raiz_u = _busca_raiz_com_compressao(u, pai)
        raiz_v = _busca_raiz_com_compressao(v, pai)
        
        if raiz_u != raiz_v:
            # unir pela altura
            if altura[raiz_u] < altura[raiz_v]:
                pai[raiz_u] = raiz_v
            elif altura[raiz_u] > altura[raiz_v]:
                pai[raiz_v] = raiz_u
            else:
                pai[raiz_v] = raiz_u
                altura[raiz_u] += 1
            
            arestas_mst.append((u, v, peso))
            peso_total += peso
            
            # Otimização: para quando temos MST completa
            if len(arestas_mst) == max_arestas:
                break
    
    return arestas_mst, peso_total


def validar_mst_local(n_vertices: int, arestas: List[Tuple[int, int, float]], 
                 arestas_mst: List[Tuple[int, int, float]]) -> dict:
    
    resultado = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    # Verifica número de arestas
    if len(arestas_mst) == n_vertices - 1:
        resultado['info']['is_spanning_tree'] = True
    else:
        resultado['warnings'].append(
            f"MST tem {len(arestas_mst)} arestas, esperado {n_vertices - 1}. "
            "Grafo pode estar desconexo."
        )
        resultado['info']['is_spanning_tree'] = False
    
    # verifica ciclos usando Union-Find
    validador = UnionFind(n_vertices)
    for u, v, _ in arestas_mst:
        if not validador.union(u, v):
            resultado['is_valid'] = False
            resultado['errors'].append(f"Ciclo detectado: aresta ({u}, {v})")
    
    # verifica se arestas da MST existem no grafo original
    conjunto_arestas = {(min(u, v), max(u, v), peso) for u, v, peso in arestas}
    for u, v, peso in arestas_mst:
        aresta_normalizada = (min(u, v), max(u, v), peso)
        if aresta_normalizada not in conjunto_arestas:
            resultado['is_valid'] = False
            resultado['errors'].append(f"Aresta ({u}, {v}, {peso}) não existe no grafo original")
    
    resultado['info']['n_components'] = validador.num_componentes
    resultado['info']['n_edges'] = len(arestas_mst)
    
    return resultado