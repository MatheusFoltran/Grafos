import csv
import math
from typing import List, Tuple, Dict


class Grafo:
    
    def __init__(self):
        self.vertices: Dict[int, Tuple[float, float]] = {}
        self.arestas: List[Tuple[int, int, float]] = []
        self.n_vertices = 0
        self.n_arestas = 0
    
    def adicionar_vertice(self, vertex_id: int, x: float, y: float):
        if vertex_id not in self.vertices:
            self.vertices[vertex_id] = (x, y)
            self.n_vertices += 1
    
    def adicionar_aresta(self, u: int, v: int, peso: float):
        self.arestas.append((u, v, peso))
        self.n_arestas += 1
    
    def obter_lista_adjacencias(self) -> List[List[Tuple[int, float]]]:
        # Constrói lista de adjacências para o grafo.
        if not self.vertices:
            return []
        
        maior_id = max(self.vertices.keys())
        adjacencias = [[] for _ in range(maior_id + 1)]
        
        for u, v, peso in self.arestas:
            adjacencias[u].append((v, peso))
            adjacencias[v].append((u, peso))
        
        return adjacencias
    
    def obter_mapeamento_vertices(self) -> Dict[int, int]:
        return {vid: idx for idx, vid in enumerate(sorted(self.vertices.keys()))}
    
    def normalizar_para_zero(self) -> 'Grafo':
        mapeamento = self.obter_mapeamento_vertices()
        grafo_novo = Grafo()
        
        for id_antigo, (x, y) in self.vertices.items():
            grafo_novo.adicionar_vertice(mapeamento[id_antigo], x, y)
        
        for u, v, peso in self.arestas:
            grafo_novo.adicionar_aresta(mapeamento[u], mapeamento[v], peso)
        
        return grafo_novo


def distancia_euclidiana(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def carregar_grafo(arquivo_vertices: str, arquivo_arestas: str) -> Grafo:
    grafo = Grafo()
    
    # carregar vértices
    with open(arquivo_vertices, 'r', encoding='utf-8') as f:
        leitor = csv.reader(f)
        
        primeira_linha = next(leitor, None)
        if primeira_linha is None:
            raise ValueError(f"Arquivo de vértices vazio: {arquivo_vertices}")
        
        # detectar se tem header
        tem_cabecalho = False
        try:
            int(primeira_linha[0])
            float(primeira_linha[1])
            float(primeira_linha[2])
        except (ValueError, IndexError):
            tem_cabecalho = True
        
        if not tem_cabecalho:
            try:
                id_vertice = int(primeira_linha[0])
                x = float(primeira_linha[1])
                y = float(primeira_linha[2])
                grafo.adicionar_vertice(id_vertice, x, y)
            except (ValueError, IndexError) as erro:
                raise ValueError(f"Formato inválido no arquivo de vértices: {erro}")
        
        for linha in leitor:
            if len(linha) < 3:
                continue
            
            try:
                id_vertice = int(linha[0])
                x = float(linha[1])
                y = float(linha[2])
                grafo.adicionar_vertice(id_vertice, x, y)
            except (ValueError, IndexError):
                continue
    
    if grafo.n_vertices == 0:
        raise ValueError(f"Nenhum vértice válido encontrado em: {arquivo_vertices}")
    
    # carregar arestas e calcular pesos
    arestas_vistas = set()
    
    with open(arquivo_arestas, 'r', encoding='utf-8') as f:
        leitor = csv.reader(f)
        
        # Ler primeira linha
        primeira_linha = next(leitor, None)
        if primeira_linha is None:
            return grafo
        
        tem_cabecalho = False
        try:
            int(primeira_linha[0])
            int(primeira_linha[1])
        except (ValueError, IndexError):
            tem_cabecalho = True
        
        # Processa primeira linha se for dados
        if not tem_cabecalho:
            try:
                u = int(primeira_linha[0])
                v = int(primeira_linha[1])
                
                if u in grafo.vertices and v in grafo.vertices:
                    chave_aresta = (min(u, v), max(u, v))
                    if chave_aresta not in arestas_vistas:
                        x1, y1 = grafo.vertices[u]
                        x2, y2 = grafo.vertices[v]
                        peso = distancia_euclidiana(x1, y1, x2, y2)
                        grafo.adicionar_aresta(u, v, peso)
                        arestas_vistas.add(chave_aresta)
            except (ValueError, IndexError, KeyError):
                pass
        
        # Processa linhas restantes
        for linha in leitor:
            if len(linha) < 2:
                continue
            
            try:
                u = int(linha[0])
                v = int(linha[1])
                
                if u not in grafo.vertices or v not in grafo.vertices:
                    continue
                
                chave_aresta = (min(u, v), max(u, v))
                if chave_aresta in arestas_vistas:
                    continue
                
                x1, y1 = grafo.vertices[u]
                x2, y2 = grafo.vertices[v]
                peso = distancia_euclidiana(x1, y1, x2, y2)
                
                grafo.adicionar_aresta(u, v, peso)
                arestas_vistas.add(chave_aresta)
            except (ValueError, IndexError, KeyError):
                continue
    
    return grafo