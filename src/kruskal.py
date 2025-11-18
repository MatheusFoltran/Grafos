"""
Implementação do algoritmo de Kruskal para Árvore Geradora Mínima.
Utiliza Union-Find com rank e path compression.
"""
from typing import List, Tuple


class UnionFind:
    """
    Estrutura Union-Find (Disjoint Set Union) com:
    - Union by rank (união pela menor altura)
    - Path compression (compressão de caminho)
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
        Encontra o representante do conjunto de x (com path compression).
        
        Args:
            x: elemento
        
        Returns:
            representante do conjunto
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """
        Une os conjuntos de x e y (union by rank).
        
        Args:
            x, y: elementos a unir
        
        Returns:
            True se uniu (estavam em conjuntos diferentes), False caso contrário
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # Já estão no mesmo conjunto
        
        # Union by rank: anexar árvore menor na maior
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


def kruskal(n_vertices: int, edges: List[Tuple[int, int, float]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Algoritmo de Kruskal para encontrar a Árvore Geradora Mínima (MST).
    
    Args:
        n_vertices: número de vértices no grafo
        edges: lista de arestas (u, v, peso)
    
    Returns:
        (mst_edges, total_weight): lista de arestas da MST e peso total
        - mst_edges: lista de tuplas (u, v, peso)
        - total_weight: soma dos pesos das arestas na MST
    """
    if n_vertices == 0:
        return [], 0.0
    
    # Ordenar arestas por peso (crescente)
    sorted_edges = sorted(edges, key=lambda e: e[2])
    
    # Inicializar Union-Find
    uf = UnionFind(n_vertices)
    
    mst_edges = []
    total_weight = 0.0
    
    # Processar arestas em ordem crescente de peso
    for u, v, weight in sorted_edges:
        # Se u e v estão em componentes diferentes, adicionar aresta
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # Otimização: se temos n-1 arestas em grafo conexo, parar
            # (para grafos desconexos, continuamos até processar todas)
            if len(mst_edges) == n_vertices - 1:
                break
    
    return mst_edges, total_weight


# Validação movida para validation.py
# Use: from validation import validate_mst


if __name__ == "__main__":
    # Teste com grafo simples
    print("Testando Kruskal e Union-Find...")
    
    # Grafo de exemplo: triângulo
    #   0
    #  /|\
    # 1-2-3
    n = 4
    edges = [
        (0, 1, 1.0),
        (0, 2, 4.0),
        (0, 3, 3.0),
        (1, 2, 2.0),
        (2, 3, 5.0)
    ]
    
    mst, weight = kruskal(n, edges)
    print(f"MST: {mst}")
    print(f"Peso total: {weight}")
    print(f"Número de arestas: {len(mst)} (esperado: {n-1})")
    
    # Teste Union-Find isolado
    print("\nTestando Union-Find:")
    uf = UnionFind(5)
    print(f"Componentes iniciais: {uf.n_components}")
    uf.union(0, 1)
    uf.union(2, 3)
    print(f"Após unions: {uf.n_components}")
    print(f"0 e 1 conectados? {uf.connected(0, 1)}")
    print(f"0 e 2 conectados? {uf.connected(0, 2)}")
    print("\nPara validação completa, use validation.py")