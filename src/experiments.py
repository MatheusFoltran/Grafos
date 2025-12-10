"""
Script para executar experimentos automatizados em múltiplos grafos.
Salva resultados em CSV para análise posterior.
"""
import argparse
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
    """Executa experimentos em múltiplos grafos e retorna resultados."""
    all_results = []
    
    for config in graph_configs:
        name = config['name']
        vertices_file = config['vertices']
        edges_file = config['edges']
        
        print(f"\n{'='*70}")
        print(f"Processando: {name}")
        print(f"{'='*70}")
        
        try:
            # Carregar grafo e normalizar para índices 0-based
            graph = load_graph(vertices_file, edges_file)
            graph = graph.normalize_to_zero_based()
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
                    'cpu_seconds': metrics.get('cpu_seconds'),
                    'memory_mb': metrics['memory_mb'],
                    'peak_memory_mb': metrics['peak_memory_mb'],
                    'mem_rss_before_mb': metrics.get('mem_rss_before_mb'),
                    'mem_rss_mb': metrics.get('mem_rss_mb'),
                    'mst_weight': total_weight,
                    'mst_edges_count': len(mst_edges),
                    'valid': valid,
                    'validation_msg': msg
                })
                
                if rep == 0:
                    print(f"  Peso MST: {total_weight:.2f}, "
                          f"Tempo: {metrics['time_seconds']*1000:.2f}ms, "
                          f"Válida: {'Sim' if valid else 'Não'}")
            
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
                    'cpu_seconds': metrics.get('cpu_seconds'),
                    'memory_mb': metrics['memory_mb'],
                    'peak_memory_mb': metrics['peak_memory_mb'],
                    'mem_rss_before_mb': metrics.get('mem_rss_before_mb'),
                    'mem_rss_mb': metrics.get('mem_rss_mb'),
                    'mst_weight': total_weight,
                    'mst_edges_count': len(mst_edges),
                    'valid': valid,
                    'validation_msg': msg
                })
                
                if rep == 0:
                    print(f"  Peso MST: {total_weight:.2f}, "
                          f"Tempo: {metrics['time_seconds']*1000:.2f}ms, "
                          f"Válida: {'Sim' if valid else 'Não'}")
        
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
        'cpu_seconds',
        'mst_weight', 'mst_edges_count', 'valid'
    ]
    # include validation message for debugging invalid MSTs
    if 'validation_msg' in results[0]:
        fieldnames.append('validation_msg')
    # include RSS memory if present
    if 'mem_rss_mb' in results[0]:
        fieldnames.append('mem_rss_mb')
    if 'mem_rss_before_mb' in results[0]:
        fieldnames.append('mem_rss_before_mb')
    if 'cpu_seconds' in results[0]:
        # ensure cpu column appears near time columns
        pass
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResultados salvos em: {output_file}")

def main():
    """Executa experimentos em grafos configurados.

    Descobre automaticamente grafos em subpastas do diretório especificado.
    """

    parser = argparse.ArgumentParser(
        description='Executa experimentos automáticos para comparar Prim vs Kruskal.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Processar todos os grafos no diretório padrão (Grafos/)
  python experiments.py
  
  # Processar grafos específicos
  python experiments.py --graphs Grafo1 Grafo2
  
  # Usar diretório customizado
  python experiments.py --graph-dir /caminho/para/grafos
  
  # Ajustar repetições e tolerância
  python experiments.py --repetitions 20 --coord-tolerance 0.001
  
  # Customizar arquivo de saída
  python experiments.py --output resultados_custom.csv
        """
    )
    
    parser.add_argument(
        '--graph-dir', 
        type=str,
        default='Grafos',
        help='Diretório contendo subpastas de grafos (default: Grafos)'
    )
    
    parser.add_argument(
        '--graphs', 
        nargs='*',
        metavar='NOME',
        help='Nomes específicos de grafos para processar (ex: Grafo1 Grafo2). '
             'Se omitido, processa todos os grafos encontrados no diretório.'
    )
    
    parser.add_argument(
        '--repetitions', '-r', 
        type=int, 
        default=10,
        metavar='N',
        help='Número de repetições por algoritmo (default: 10)'
    )
    
    parser.add_argument(
        '--coord-tolerance', '-c',
        type=float,
        default=0.0,
        metavar='TOL',
        help='Tolerância para matching por coordenadas (default: 0.0)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='results/resultados_experimentos.csv',
        metavar='ARQUIVO',
        help='Arquivo de saída CSV (default: results/resultados_experimentos.csv)'
    )
    
    args = parser.parse_args()

    # Descobrir grafos automaticamente na pasta raiz especificada
    project_root = Path(__file__).resolve().parents[1]
    grafos_dir = project_root / args.graph_dir

    if not grafos_dir.exists():
        print(f"\nERRO: Diretório não encontrado: {grafos_dir}")
        print(f"   Certifique-se que o diretório existe e contém subpastas com grafos.")
        sys.exit(1)

    graph_configs = []
    
    print(f"\nBuscando grafos em: {grafos_dir}")
    print(f"{'='*70}")
    
    if grafos_dir.exists() and grafos_dir.is_dir():
        for sub in sorted(grafos_dir.iterdir()):
            if not sub.is_dir():
                continue

            # Filtrar por nomes específicos se fornecidos via --graphs
            if args.graphs and sub.name not in args.graphs:
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
                print(f"  - {sub.name}: {Path(nodes_file).name}, {Path(edges_file).name}")
            else:
                print(f"  AVISO: Pulando {sub.name}: arquivos de nós/arestas não encontrados")
    
    if not graph_configs:
        print(f"\nERRO: Nenhum grafo válido encontrado!")
        if args.graphs:
            print(f"   Grafos solicitados: {', '.join(args.graphs)}")
        print(f"\nDicas:")
        print(f"   • Verifique se {grafos_dir} contém subpastas")
        print(f"   • Cada subpasta deve ter arquivos com 'node'/'nodes' e 'edge'/'edges' no nome")
        print(f"   • Use --graph-dir para especificar outro diretório")
        sys.exit(1)

    # Validar que arquivos existem
    valid_configs = []
    for config in graph_configs:
        if Path(config['vertices']).exists() and Path(config['edges']).exists():
            valid_configs.append(config)
        else:
            print(f"AVISO: Pulando {config['name']}: arquivos não encontrados")
    
    if not valid_configs:
        print("\nERRO: Nenhum grafo válido encontrado após verificação de arquivos!")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"CONFIGURAÇÃO DOS EXPERIMENTOS")
    print(f"{'='*70}")
    print(f"Diretório de grafos: {grafos_dir}")
    print(f"Grafos selecionados: {len(valid_configs)}")
    for cfg in valid_configs:
        print(f"  • {cfg['name']}")
    print(f"Repetições por algoritmo: {args.repetitions}")
    print(f"Total de execuções: {len(valid_configs) * 2 * args.repetitions}")
    print(f"Arquivo de saída: {args.output}")
    print(f"{'='*70}")
    
    # Executar experimentos
    results = run_experiments(valid_configs, args.repetitions)
    
    # Salvar resultados usando o nome customizado
    save_results(results, args.output)
    
    # Resumo
    print(f"\n{'='*70}")
    print("EXPERIMENTOS CONCLUÍDOS")
    print(f"{'='*70}")
    print(f"Total de execuções: {len(results)}")
    print(f"Grafos processados: {len(valid_configs)}")
    print(f"Resultados salvos em: {args.output}")
    print(f"\nPróximo passo: use analysis.ipynb para gerar gráficos e análises")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()