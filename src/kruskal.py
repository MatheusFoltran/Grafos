from typing import List, Tuple


class UnionFind:
    """Union-Find com union by rank e path compression."""
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.n_components = n
    
    def find(self, x: int) -> int:
        """Encontra raiz do conjunto com path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """Une dois conjuntos. Retorna True se eram diferentes."""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        self.n_components -= 1
        return True
    
    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


def _find_with_compression(node: int, parent: List[int]) -> int:
    """Find iterativo com path compression."""
    root = node
    while parent[root] != root:
        root = parent[root]
    
    # comprimir caminho
    curr = node
    while curr != root:
        next_node = parent[curr]
        parent[curr] = root
        curr = next_node
    
    return root


def kruskal(n_vertices: int, edges: List[Tuple[int, int, float]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Algoritmo de Kruskal para MST usando Union-Find.
    
    Args:
        n_vertices: número de vértices
        edges: lista (u, v, peso)
    
    Returns:
        (mst_edges, total_weight)
    """
    if n_vertices == 0:
        return [], 0.0
    
    if not edges:
        return [], 0.0
    
    # ordenar por peso (parte mais cara do algoritmo)
    sorted_edges = sorted(edges, key=lambda e: e[2])
    
    parent = list(range(n_vertices))
    rank = [0] * n_vertices
    
    mst_edges = []
    total_weight = 0.0
    target_edges = n_vertices - 1
    
    for u, v, weight in sorted_edges:
        root_u = _find_with_compression(u, parent)
        root_v = _find_with_compression(v, parent)
        
        if root_u != root_v:
            # union by rank
            if rank[root_u] < rank[root_v]:
                parent[root_u] = root_v
            elif rank[root_u] > rank[root_v]:
                parent[root_v] = root_u
            else:
                parent[root_v] = root_u
                rank[root_u] += 1
            
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            if len(mst_edges) == target_edges:
                break
    
    return mst_edges, total_weight


def validate_mst(n_vertices: int, edges: List[Tuple[int, int, float]], 
                 mst_edges: List[Tuple[int, int, float]]) -> dict:
    """
    Valida se a MST calculada está correta.
    
    Args:
        n_vertices: número de vértices
        edges: lista original de arestas
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
    
    # Verificar número de arestas
    if len(mst_edges) == n_vertices - 1:
        result['info']['is_spanning_tree'] = True
    else:
        result['warnings'].append(
            f"MST tem {len(mst_edges)} arestas, esperado {n_vertices - 1}. "
            "Grafo pode estar desconexo."
        )
        result['info']['is_spanning_tree'] = False
    
    # Verificar se forma ciclo usando Union-Find
    uf = UnionFind(n_vertices)
    for u, v, _ in mst_edges:
        if not uf.union(u, v):
            result['is_valid'] = False
            result['errors'].append(f"Ciclo detectado: aresta ({u}, {v})")
    
    # Verificar se todas as arestas da MST existem no grafo original
    edge_set = {(min(u, v), max(u, v), w) for u, v, w in edges}
    for u, v, w in mst_edges:
        normalized = (min(u, v), max(u, v), w)
        if normalized not in edge_set:
            result['is_valid'] = False
            result['errors'].append(f"Aresta ({u}, {v}, {w}) não existe no grafo original")
    
    result['info']['n_components'] = uf.n_components
    result['info']['n_edges'] = len(mst_edges)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: Algoritmo de Kruskal")
    print("=" * 70)
    
    # Teste 1: Grafo conexo simples
    print("\n[Teste 1] Grafo conexo (4 vértices)")
    print("-" * 70)
    n = 4
    edges = [
        (0, 1, 1.0),
        (0, 2, 4.0),
        (0, 3, 3.0),
        (1, 2, 2.0),
        (2, 3, 5.0)
    ]
    
    mst, weight = kruskal(n, edges)
    print(f"Arestas do grafo: {len(edges)}")
    print(f"MST calculada: {mst}")
    print(f"Peso total: {weight}")
    print(f"Arestas na MST: {len(mst)} (esperado: {n-1})")
    
    # Validação
    validation = validate_mst(n, edges, mst)
    print(f"Validação: {'PASSOU' if validation['is_valid'] else 'FALHOU'}")
    if validation['errors']:
        print(f"Erros: {validation['errors']}")
    if validation['warnings']:
        print(f"Avisos: {validation['warnings']}")
    
    # Teste 2: Grafo desconexo
    print("\n[Teste 2] Grafo desconexo (2 componentes)")
    print("-" * 70)
    n = 5
    edges = [
        (0, 1, 1.0),
        (1, 2, 2.0),
        (3, 4, 3.0)
    ]
    
    mst, weight = kruskal(n, edges)
    print(f"MST (floresta): {mst}")
    print(f"Peso total: {weight}")
    print(f"Arestas: {len(mst)} (esperado para MSF: {len(edges)})")
    
    validation = validate_mst(n, edges, mst)
    print(f"Validação: {'PASSOU' if validation['is_valid'] else 'FALHOU'}")
    print(f"Componentes conexas: {validation['info']['n_components']}")
    
    # Teste 3: Union-Find standalone
    print("\n[Teste 3] Union-Find isolado")
    print("-" * 70)
    uf = UnionFind(5)
    print(f"Componentes iniciais: {uf.n_components}")
    print(f"Union(0, 1): {uf.union(0, 1)}")
    print(f"Union(2, 3): {uf.union(2, 3)}")
    print(f"Union(0, 1) novamente: {uf.union(0, 1)} (esperado: False)")
    print(f"Componentes após unions: {uf.n_components}")
    print(f"Conectados(0, 1): {uf.connected(0, 1)}")
    print(f"Conectados(0, 2): {uf.connected(0, 2)}")
    print(f"Conectados(2, 3): {uf.connected(2, 3)}")
    
    print("\n" + "=" * 70)
    print("Todos os testes concluídos!")
    print("=" * 70)