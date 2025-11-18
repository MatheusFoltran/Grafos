"""
Módulo de validação robusta para Árvores/Florestas Geradoras Mínimas.

Verifica:
1. Ausência de ciclos (acyclicity)
2. Cobertura completa de vértices (completeness)
3. Número correto de arestas por componente conexa
"""
from typing import List, Tuple, Dict, Set


class UnionFind:
    """Union-Find para validação."""
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.n_components = n
    
    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
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
    
    def get_component_sizes(self) -> dict:
        """Retorna tamanho de cada componente."""
        components = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            components[root] = components.get(root, 0) + 1
        return components


def get_original_components(n_vertices: int, edges: List[Tuple[int, int, float]]) -> dict:
    """
    Identifica componentes conexas do grafo original.
    
    Args:
        n_vertices: número de vértices
        edges: lista de arestas do grafo original (u, v, peso)
    
    Returns:
        Dicionário {componente_id: {vértices}}
    """
    uf = UnionFind(n_vertices)
    
    # Unir vértices conectados
    for u, v, _ in edges:
        uf.union(u, v)
    
    # Agrupar vértices por componente
    components = {}
    for v in range(n_vertices):
        root = uf.find(v)
        if root not in components:
            components[root] = set()
        components[root].add(v)
    
    return components


def validate_mst(n_vertices: int,
                 original_edges: List[Tuple[int, int, float]],
                 mst_edges: List[Tuple[int, int, float]]) -> Tuple[bool, str]:
    """Validação completa de MST/Floresta.

    Condições verificadas:
    1. Não há ciclos (acyclicidade)
    2. Nenhuma aresta conecta componentes diferentes do grafo original
    3. Para cada componente com k vértices, existem exatamente k-1 arestas na MST
    """

    # 1) Componentes do grafo original
    original_components = get_original_components(n_vertices, original_edges)
    comp_list = list(original_components.values())  # lista de conjuntos de vértices

    # Mapear cada vértice para o índice de sua componente
    vertex_to_comp: Dict[int, int] = {}
    for idx, vertices in enumerate(comp_list):
        for v in vertices:
            vertex_to_comp[v] = idx

    # Contador de arestas por componente
    comp_edge_counts: Dict[int, int] = {}

    # 2) Verificar aciclicidade e conexões válidas
    mst_uf = UnionFind(n_vertices)
    for u, v, _ in mst_edges:
        if not (0 <= u < n_vertices and 0 <= v < n_vertices):
            return False, f"Índices inválidos na MST: ({u}, {v})"

        if not mst_uf.union(u, v):
            return False, f"Ciclo detectado ao adicionar aresta ({u}, {v})"

        comp_u = vertex_to_comp.get(u)
        comp_v = vertex_to_comp.get(v)
        if comp_u is None or comp_v is None:
            return False, "Vértice da MST não pertence ao grafo original"
        if comp_u != comp_v:
            return False, "Aresta da MST conecta componentes distintas do grafo original"

        comp_edge_counts[comp_u] = comp_edge_counts.get(comp_u, 0) + 1

    # 3) Conferir número de arestas por componente (k-1)
    for idx, vertices in enumerate(comp_list):
        k = len(vertices)
        expected = max(0, k - 1)
        actual = comp_edge_counts.get(idx, 0)
        if actual != expected:
            return False, (f"Componente {idx} possui {k} vértices e deveria ter "
                          f"{expected} arestas na MST, mas possui {actual}")

    return True, "✓ MST/Floresta válida (aciclicidade e cobertura por componente confirmadas)"


# Testes unitários
if __name__ == "__main__":
    print("="*70)
    print("TESTES DE VALIDAÇÃO DE MST")
    print("="*70)
    
    # Teste 1: MST válida em grafo conexo
    print("\n1. MST válida (grafo conexo):")
    n = 4
    original = [(0, 1, 1.0), (1, 2, 2.0), (2, 3, 3.0), (0, 3, 4.0)]
    mst = [(0, 1, 1.0), (1, 2, 2.0), (2, 3, 3.0)]
    valid, msg = validate_mst(n, original, mst)
    print(f"   {msg}")
    assert valid, "Deveria ser válida!"
    
    # Teste 2: MST incompleta (faltando vértice)
    print("\n2. MST incompleta (faltando vértice):")
    mst_incomplete = [(0, 1, 1.0), (1, 2, 2.0)]  # Falta vértice 3!
    valid, msg = validate_mst(n, original, mst_incomplete)
    print(f"   {msg}")
    assert not valid, "Deveria ser inválida!"
    
    # Teste 3: MST com ciclo
    print("\n3. MST com ciclo:")
    mst_cycle = [(0, 1, 1.0), (1, 2, 2.0), (2, 3, 3.0), (0, 3, 4.0)]
    valid, msg = validate_mst(n, original, mst_cycle)
    print(f"   {msg}")
    assert not valid, "Deveria ser inválida!"
    
    # Teste 4: Grafo desconexo (2 componentes)
    print("\n4. Floresta válida (grafo desconexo):")
    n = 6
    original = [(0, 1, 1.0), (1, 2, 2.0),  # Componente 1
                (3, 4, 3.0), (4, 5, 4.0)]   # Componente 2
    mst = [(0, 1, 1.0), (1, 2, 2.0),       # 2 arestas para 3 vértices
           (3, 4, 3.0), (4, 5, 4.0)]        # 2 arestas para 3 vértices
    valid, msg = validate_mst(n, original, mst)
    print(f"   {msg}")
    assert valid, "Deveria ser válida!"
    
    # Teste 5: Floresta incompleta
    print("\n5. Floresta incompleta (faltando aresta):")
    mst_incomplete = [(0, 1, 1.0), (1, 2, 2.0),  # Componente 1 OK
                      (3, 4, 3.0)]                # Componente 2 incompleta!
    valid, msg = validate_mst(n, original, mst_incomplete)
    print(f"   {msg}")
    assert not valid, "Deveria ser inválida!"
    
    # Teste 6: Grafo com vértice isolado
    print("\n6. Grafo com vértice isolado:")
    n = 4
    original = [(0, 1, 1.0), (1, 2, 2.0)]  # Vértice 3 isolado
    mst = [(0, 1, 1.0), (1, 2, 2.0)]
    valid, msg = validate_mst(n, original, mst)
    print(f"   {msg}")
    assert valid, "Deveria ser válida!"
    
    print("\n" + "="*70)
    print("✓ TODOS OS TESTES PASSARAM!")
    print("="*70)