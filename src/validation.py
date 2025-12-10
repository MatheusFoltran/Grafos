from typing import List, Tuple, Dict


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
        
        if self.altura[raiz_x] < self.altura[raiz_y]:
            self.pai[raiz_x] = raiz_y
        elif self.altura[raiz_x] > self.altura[raiz_y]:
            self.pai[raiz_y] = raiz_x
        else:
            self.pai[raiz_y] = raiz_x
            self.altura[raiz_x] += 1
        
        self.num_componentes -= 1
        return True
    
    def obter_tamanhos_componentes(self) -> dict:
        componentes = {}
        for i in range(len(self.pai)):
            raiz = self.find(i)
            componentes[raiz] = componentes.get(raiz, 0) + 1
        return componentes


def obter_componentes_originais(n_vertices: int, arestas: List[Tuple[int, int, float]]) -> dict:
    uf = UnionFind(n_vertices)
    
    for u, v, _ in arestas:
        uf.union(u, v)
    
    componentes = {}
    for vertice in range(n_vertices):
        raiz = uf.find(vertice)
        if raiz not in componentes:
            componentes[raiz] = set()
        componentes[raiz].add(vertice)
    
    return componentes


def validar_mst(n_vertices: int,
                arestas_originais: List[Tuple[int, int, float]],
                arestas_mst: List[Tuple[int, int, float]]) -> bool:
    # Encontra componentes conexas do grafo original
    componentes_originais = obter_componentes_originais(n_vertices, arestas_originais)
    lista_componentes = list(componentes_originais.values())

    # Mapeia cada vértice para sua componente (para validação rápida)
    vertice_para_comp: Dict[int, int] = {}
    for idx, vertices in enumerate(lista_componentes):
        for v in vertices:
            vertice_para_comp[v] = idx

    contagem_arestas_comp: Dict[int, int] = {}

    validador_mst = UnionFind(n_vertices)
    for u, v, _ in arestas_mst:
        if not (0 <= u < n_vertices and 0 <= v < n_vertices):
            print(f"Índices inválidos ({u}, {v})")
            return False

        if not validador_mst.union(u, v):
            print(f"Ciclo detectado ({u}, {v})")
            return False

        comp_u = vertice_para_comp.get(u)
        comp_v = vertice_para_comp.get(v)
        if comp_u is None or comp_v is None:
            print("Vértice fora do grafo original")
            return False
            
        # MST não pode conectar componentes desconexas do grafo original
        if comp_u != comp_v:
            print("Aresta conecta componentes distintas")
            return False

        contagem_arestas_comp[comp_u] = contagem_arestas_comp.get(comp_u, 0) + 1

    # Verifica se cada componente tem exatamente (n-1) arestas (floresta geradora)
    for idx, vertices in enumerate(lista_componentes):
        tamanho_comp = len(vertices)
        arestas_esperadas = max(0, tamanho_comp - 1)
        arestas_reais = contagem_arestas_comp.get(idx, 0)
        if arestas_reais != arestas_esperadas:
            print(f"Componente {idx} com arestas incorretas")
            return False

    return True