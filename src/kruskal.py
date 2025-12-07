from typing import List, Tuple


class UnionFind:
    """
    Estrutura Union-Find (Disjoint Set Union) com otimizações:
    - Union by rank (união pela menor altura)
    - Path compression (compressão de caminho)
    
    NOTA: Esta classe existe para testes e demonstração.
    A função kruskal() usa implementação inline para máxima performance.
    """
    
    def __init__(self, n: int):
        """
        Inicializa Union-Find com n elementos.
        
        Args:
            n: número de elementos (0 a n-1)
        """
        self.parent = list(range(n))
        self.rank = [0] * n
        self.n_components = n
    
    def find(self, x: int) -> int:
        """
        Encontra o representante do conjunto de x com path compression.
        
        Complexidade: O(α(n)) amortizado, onde α é a função inversa de Ackermann.
        
        Args:
            x: elemento a buscar
        
        Returns:
            representante do conjunto
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """
        Une os conjuntos de x e y usando union by rank.
        
        Complexidade: O(α(n)) amortizado.
        
        Args:
            x, y: elementos a unir
        
        Returns:
            True se uniu (estavam em conjuntos diferentes), False caso contrário
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        # Union by rank: anexar árvore de menor altura na maior
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
        """Verifica se x e y estão no mesmo conjunto."""
        return self.find(x) == self.find(y)


def _find_with_compression(node: int, parent: List[int]) -> int:
    """
    Find com path compression (inline optimized).
    
    Esta função implementa o find de forma iterativa para evitar
    overhead de chamadas recursivas em Python.
    
    Args:
        node: nó a buscar
        parent: vetor de pais
    
    Returns:
        raiz do conjunto
    """
    # Encontrar a raiz
    root = node
    while parent[root] != root:
        root = parent[root]
    
    # Path compression: apontar todos os nós no caminho diretamente para a raiz
    curr = node
    while curr != root:
        next_node = parent[curr]
        parent[curr] = root
        curr = next_node
    
    return root


def kruskal(n_vertices: int, edges: List[Tuple[int, int, float]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Algoritmo de Kruskal para encontrar a Árvore Geradora Mínima (MST).
    
    Implementação OTIMIZADA com Union-Find inline para máxima performance.
    Usa vetor de índices (parent) e união pela menor altura (rank).
    
    Complexidade:
    - Tempo: O(E log E) dominado pela ordenação das arestas
      - Ordenação: O(E log E)
      - Union-Find: O(E · α(V)) ≈ O(E) na prática
    - Espaço: O(V + E)
    
    Otimizações implementadas:
    1. Find iterativo com path compression (evita recursão)
    2. Union by rank (mantém árvore balanceada)
    3. Early stopping quando MST completa (n-1 arestas)
    4. Operações inline (reduz overhead de chamadas de função)
    
    Args:
        n_vertices: número de vértices no grafo (0 a n-1)
        edges: lista de arestas no formato (u, v, peso)
               onde u, v são índices de vértices e peso é float
    
    Returns:
        Tupla contendo:
        - mst_edges: lista de arestas da MST no formato (u, v, peso)
        - total_weight: soma total dos pesos das arestas na MST
        
    Tratamento de grafos desconexos:
        Se o grafo for desconexo, retorna uma floresta geradora mínima
        (MSF - Minimum Spanning Forest) contendo menos de n-1 arestas.
    
    Exemplo:
        >>> edges = [(0, 1, 1.0), (1, 2, 2.0), (0, 2, 3.0)]
        >>> mst, weight = kruskal(3, edges)
        >>> print(mst)
        [(0, 1, 1.0), (1, 2, 2.0)]
        >>> print(weight)
        3.0
    """
    # Casos base
    if n_vertices == 0:
        return [], 0.0
    
    if not edges:
        return [], 0.0
    
    # PASSO 1: Ordenar arestas por peso (crescente)
    # Complexidade: O(E log E)
    sorted_edges = sorted(edges, key=lambda e: e[2])
    
    # PASSO 2: Inicializar estruturas do Union-Find
    # parent[i] = pai do nó i (inicialmente cada nó é seu próprio pai)
    # rank[i] = altura aproximada da árvore enraizada em i
    parent = list(range(n_vertices))
    rank = [0] * n_vertices
    
    # Estruturas para armazenar resultado
    mst_edges = []
    total_weight = 0.0
    target_edges = n_vertices - 1  # Uma MST tem exatamente n-1 arestas
    
    # PASSO 3: Processar arestas em ordem crescente de peso
    # Para cada aresta, verificar se conecta componentes diferentes
    for u, v, weight in sorted_edges:
        # ===== FIND para u (inline com path compression) =====
        root_u = _find_with_compression(u, parent)
        
        # ===== FIND para v (inline com path compression) =====
        root_v = _find_with_compression(v, parent)
        
        # ===== UNION by rank =====
        if root_u != root_v:
            # Os vértices estão em componentes diferentes
            # Unir as componentes usando union by rank
            
            if rank[root_u] < rank[root_v]:
                # Árvore de u é menor, anexar em v
                parent[root_u] = root_v
            elif rank[root_u] > rank[root_v]:
                # Árvore de v é menor, anexar em u
                parent[root_v] = root_u
            else:
                # Árvores de mesma altura, escolher uma como raiz
                # e incrementar sua altura
                parent[root_v] = root_u
                rank[root_u] += 1
            
            # Adicionar aresta à MST
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # OTIMIZAÇÃO: Early stopping
            # Se já temos n-1 arestas, a MST está completa (grafo conexo)
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
    print("TESTE: Algoritmo de Kruskal Otimizado")
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
    print(f"Validação: {'✓ PASSOU' if validation['is_valid'] else '✗ FALHOU'}")
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
    print(f"Validação: {'✓ PASSOU' if validation['is_valid'] else '✗ FALHOU'}")
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