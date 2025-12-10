import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict
from graph_loader import carregar_grafo
from prim import prim
from kruskal import kruskal
from validation import validar_mst
from metrics import medir_desempenho


def executar_experimentos(configuracoes_grafos: List[Dict], repeticoes: int = 5) -> List[Dict]:
    todos_resultados = []
    
    for configuracao in configuracoes_grafos:
        nome = configuracao['name']
        arquivo_vertices = configuracao['vertices']
        arquivo_arestas = configuracao['edges']
        
        print(f"\nProcessando: {nome}")
        
        try:
            grafo = carregar_grafo(arquivo_vertices, arquivo_arestas)
            grafo = grafo.normalizar_para_zero()
            print(f"Grafo: {grafo.n_vertices} vértices, {grafo.n_arestas} arestas")
            
            print(f"\nExecutando Prim ({repeticoes} repetições)...")
            adjacencias = grafo.obter_lista_adjacencias()
            
            for rep in range(repeticoes):
                metricas = medir_desempenho(prim, grafo.n_vertices, adjacencias)
                arestas_mst, peso_total = metricas['result']
                valida = validar_mst(grafo.n_vertices, grafo.arestas, arestas_mst)
                mensagem = "Válida" if valida else "Inválida"
                
                todos_resultados.append({
                    'graph_name': nome,
                    'n_nodes': grafo.n_vertices,
                    'n_edges': grafo.n_arestas,
                    'algorithm': 'prim',
                    'repetition': rep + 1,
                    'time_seconds': metricas['time_seconds'],
                    'cpu_seconds': metricas.get('cpu_seconds'),
                    'memory_mb': metricas['memory_mb'],
                    'peak_memory_mb': metricas['peak_memory_mb'],
                    'mem_rss_before_mb': metricas.get('mem_rss_before_mb'),
                    'mem_rss_mb': metricas.get('mem_rss_mb'),
                    'mst_weight': peso_total,
                    'mst_edges_count': len(arestas_mst),
                    'valid': valida,
                    'validation_msg': mensagem
                })
                
                if rep == 0:
                    print(f"  Peso MST: {peso_total:.2f}, "
                          f"Tempo: {metricas['time_seconds']*1000:.2f}ms, "
                          f"Válida: {'Sim' if valida else 'Não'}")
            
            print(f"\nExecutando Kruskal ({repeticoes} repetições)...")
            
            for rep in range(repeticoes):
                metricas = medir_desempenho(kruskal, grafo.n_vertices, grafo.arestas)
                arestas_mst, peso_total = metricas['result']
                valida = validar_mst(grafo.n_vertices, grafo.arestas, arestas_mst)
                mensagem = "Válida" if valida else "Inválida"
                
                todos_resultados.append({
                    'graph_name': nome,
                    'n_nodes': grafo.n_vertices,
                    'n_edges': grafo.n_arestas,
                    'algorithm': 'kruskal',
                    'repetition': rep + 1,
                    'time_seconds': metricas['time_seconds'],
                    'cpu_seconds': metricas.get('cpu_seconds'),
                    'memory_mb': metricas['memory_mb'],
                    'peak_memory_mb': metricas['peak_memory_mb'],
                    'mem_rss_before_mb': metricas.get('mem_rss_before_mb'),
                    'mem_rss_mb': metricas.get('mem_rss_mb'),
                    'mst_weight': peso_total,
                    'mst_edges_count': len(arestas_mst),
                    'valid': valida,
                    'validation_msg': mensagem
                })
                
                if rep == 0:
                    print(f"  Peso MST: {peso_total:.2f}, "
                          f"Tempo: {metricas['time_seconds']*1000:.2f}ms, "
                          f"Válida: {'Sim' if valida else 'Não'}")
        
        except Exception as erro:
            print(f"ERRO ao processar {nome}: {erro}")
            continue
    
    return todos_resultados


def salvar_resultados(resultados: List[Dict], arquivo_saida: str):
    if not resultados:
        print("Nenhum resultado para salvar.")
        return
    
    nomes_campos = [
        'graph_name', 'n_nodes', 'n_edges', 'algorithm', 'repetition',
        'time_seconds', 'memory_mb', 'peak_memory_mb',
        'cpu_seconds',
        'mst_weight', 'mst_edges_count', 'valid'
    ]
    if 'validation_msg' in resultados[0]:
        nomes_campos.append('validation_msg')
    if 'mem_rss_mb' in resultados[0]:
        nomes_campos.append('mem_rss_mb')
    if 'mem_rss_before_mb' in resultados[0]:
        nomes_campos.append('mem_rss_before_mb')
    
    with open(arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=nomes_campos)
        escritor.writeheader()
        escritor.writerows(resultados)
    
    print(f"\nResultados salvos em: {arquivo_saida}")

def main():
    # Configuração simples dos argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='Grafos', help='Diretório dos grafos')
    parser.add_argument('--rep', type=int, default=10, help='Número de repetições')
    parser.add_argument('--graphs', nargs='*', help='Filtrar grafos específicos')
    parser.add_argument('--out', default='results/resultados_experimentos.csv', help='Arquivo de saída')
    args = parser.parse_args()

    path_grafos = Path(args.dir)
    
    # Se não achar a pasta direto, tenta voltar um nível (caso esteja rodando de src/)
    if not path_grafos.exists():
        path_grafos = Path('..') / args.dir
        
    if not path_grafos.exists():
        print(f"Erro: Pasta '{args.dir}' não encontrada.")
        return

    lista_grafos = []
    print(f"Lendo grafos de: {path_grafos.resolve()}")

    # Varre as pastas para procurar os grafos
    for pasta in sorted(path_grafos.iterdir()):
        if not pasta.is_dir():
            continue
            
        if args.graphs and pasta.name not in args.graphs:
            continue
            
        # Tenta identificar arquivos de vertices e arestas
        arq_vertices = None
        arq_arestas = None
        
        for arquivo in pasta.iterdir():
            nome = arquivo.name.lower()
            if 'node' in nome or 'vert' in nome:
                arq_vertices = str(arquivo)
            elif 'edge' in nome:
                arq_arestas = str(arquivo)
        
        if arq_vertices and arq_arestas:
            lista_grafos.append({
                'name': pasta.name,
                'vertices': arq_vertices,
                'edges': arq_arestas
            })
            print(f"{pasta.name}")
    
    if not lista_grafos:
        print("Nenhum grafo encontrado.")
        return

    print(f"\nRodando experimentos ({args.rep} repetições)...")
    resultados = executar_experimentos(lista_grafos, args.rep)
    
    # Garantir que pasta de resultados existe
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    
    salvar_resultados(resultados, args.out)
    print("Concluído.")


if __name__ == "__main__":
    main()