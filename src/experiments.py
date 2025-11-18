"""
Script para executar experimentos automatizados em múltiplos grafos.
Salva resultados em CSV para análise posterior.
"""
import csv
import sys
from pathlib import Path
from typing import List, Dict
from graph_loader import load_graph
from prim import prim
from kruskal import kruskal
from validation import validate_mst
from metrics import measure_performance


def run_experiments(graph_configs: List[Dict], repetitions: int = 5) -> List[Dict]:
    """
    Executa experimentos em múltiplos grafos.
    
    Args:
        graph_configs: lista de dicionários com 'name', 'vertices', 'edges'
        repetitions: número de repetições por grafo/algoritmo
    
    Returns:
        Lista de resultados (um dicionário por execução)
    """
    all_results = []
    
    for config in graph_configs:
        name = config['name']
        vertices_file = config['vertices']
        edges_file = config['edges']
        
        print(f"\n{'='*70}")
        print(f"Processando: {name}")
        print(f"{'='*70}")
        
        try:
            # Carregar grafo
            graph = load_graph(vertices_file, edges_file)
            print(f"Grafo: {graph.n_vertices} vértices, {graph.n_edges} arestas")
            
            # Executar Prim
            print(f"\nExecutando Prim ({repetitions} repetições)...")
            adj = graph.get_adjacency_list()
            
            for rep in range(repetitions):
                metrics = measure_performance(prim, graph.n_vertices, adj)
                mst_edges, total_weight = metrics['result']
                valid, msg = validate_mst(graph.n_vertices, graph.edges, mst_edges)
                
                all_results.append({
                    'graph_name': name,
                    'n_vertices': graph.n_vertices,
                    'n_edges': graph.n_edges,
                    'algorithm': 'prim',
                    'repetition': rep + 1,
                    'time_seconds': metrics['time_seconds'],
                    'memory_mb': metrics['memory_mb'],
                    'peak_memory_mb': metrics['peak_memory_mb'],
                    'mst_weight': total_weight,
                    'mst_edges_count': len(mst_edges),
                    'valid': valid,
                    'validation_msg': msg
                })
                
                if rep == 0:
                    print(f"  Peso MST: {total_weight:.2f}, "
                          f"Tempo: {metrics['time_seconds']*1000:.2f}ms, "
                          f"Válida: {'✓' if valid else '✗'}")
            
            # Executar Kruskal
            print(f"\nExecutando Kruskal ({repetitions} repetições)...")
            
            for rep in range(repetitions):
                metrics = measure_performance(kruskal, graph.n_vertices, graph.edges)
                mst_edges, total_weight = metrics['result']
                valid, msg = validate_mst(graph.n_vertices, graph.edges, mst_edges)
                
                all_results.append({
                    'graph_name': name,
                    'n_vertices': graph.n_vertices,
                    'n_edges': graph.n_edges,
                    'algorithm': 'kruskal',
                    'repetition': rep + 1,
                    'time_seconds': metrics['time_seconds'],
                    'memory_mb': metrics['memory_mb'],
                    'peak_memory_mb': metrics['peak_memory_mb'],
                    'mst_weight': total_weight,
                    'mst_edges_count': len(mst_edges),
                    'valid': valid,
                    'validation_msg': msg
                })
                
                if rep == 0:
                    print(f"  Peso MST: {total_weight:.2f}, "
                          f"Tempo: {metrics['time_seconds']*1000:.2f}ms, "
                          f"Válida: {'✓' if valid else '✗'}")
        
        except Exception as e:
            print(f"ERRO ao processar {name}: {e}")
            continue
    
    return all_results


def save_results(results: List[Dict], output_file: str):
    """Salva resultados em arquivo CSV."""
    if not results:
        print("Nenhum resultado para salvar.")
        return
    
    fieldnames = [
        'graph_name', 'n_vertices', 'n_edges', 'algorithm', 'repetition',
        'time_seconds', 'memory_mb', 'peak_memory_mb',
        'mst_weight', 'mst_edges_count', 'valid'
    ]
    # include validation message for debugging invalid MSTs
    if 'validation_msg' in results[0]:
        fieldnames.append('validation_msg')
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✓ Resultados salvos em: {output_file}")

def main():
    """Executa experimentos em grafos configurados.

    Agora o script tenta descobrir automaticamente subpastas em `Grafos/` e localizar
    os arquivos de nós e arestas (por exemplo `Nodes*.csv` e `Edges*.csv`). Isso evita
    problemas com nomes/capitalização diferentes (ex: `Nodes1.csv`, `EEdges2.csv`).
    """

    # Descobrir grafos automaticamente na pasta raiz 'Grafos'
    project_root = Path(__file__).resolve().parents[1]
    grafos_dir = project_root / 'Grafos'

    graph_configs = []
    if grafos_dir.exists() and grafos_dir.is_dir():
        for sub in sorted(grafos_dir.iterdir()):
            if not sub.is_dir():
                continue

            # Procurar arquivos de nós e arestas por padrões simples (case-insensitive)
            nodes_file = None
            edges_file = None
            for f in sub.iterdir():
                name = f.name.lower()
                if any(k in name for k in ('node', 'nodes', 'vert', 'vertices')) and nodes_file is None:
                    nodes_file = str(f)
                if 'edge' in name and edges_file is None:
                    edges_file = str(f)

            if nodes_file and edges_file:
                graph_configs.append({
                    'name': sub.name,
                    'vertices': nodes_file,
                    'edges': edges_file
                })
            else:
                print(f"⚠ Pulando {sub.name}: não foi possível localizar nodes/edges")
    else:
        print(f"ERRO: pasta de grafos não encontrada: {grafos_dir}")

    # Número de repetições por experimento
    repetitions = 10

    # Validar que arquivos existem
    valid_configs = []
    for config in graph_configs:
        if Path(config['vertices']).exists() and Path(config['edges']).exists():
            valid_configs.append(config)
        else:
            print(f"⚠ Pulando {config['name']}: arquivos não encontrados")
    
    if not valid_configs:
        print("\nERRO: Nenhum grafo válido encontrado!")
        print("Ajuste os caminhos em experiments.py")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"INICIANDO EXPERIMENTOS")
    print(f"{'='*70}")
    print(f"Grafos: {len(valid_configs)}")
    print(f"Repetições por algoritmo: {repetitions}")
    print(f"Total de execuções: {len(valid_configs) * 2 * repetitions}")
    
    # Executar experimentos
    results = run_experiments(valid_configs, repetitions)
    
    # Salvar resultados
    output_file = 'resultados_experimentos.csv'
    save_results(results, output_file)
    
    # Resumo
    print(f"\n{'='*70}")
    print("RESUMO")
    print(f"{'='*70}")
    print(f"Total de execuções: {len(results)}")
    print(f"Grafos processados: {len(valid_configs)}")
    print(f"\nPróximo passo: use analysis.ipynb para gerar gráficos e análises")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()