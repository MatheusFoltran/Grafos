"""
Programa principal para comparação de Prim vs Kruskal.
Executa algoritmos e coleta métricas de desempenho.
"""
import argparse
import sys
from pathlib import Path

# Importações dos módulos do projeto
from graph_loader import load_graph
from prim import prim
from kruskal import kruskal
from validation import validate_mst
from metrics import measure_performance, format_time, format_memory


def run_algorithm(algorithm: str, graph, repetitions: int = 1):
    """
    Executa um algoritmo múltiplas vezes e coleta métricas.
    
    Args:
        algorithm: 'prim' ou 'kruskal'
        graph: objeto Graph
        repetitions: número de repetições
    
    Returns:
        Lista de dicionários com métricas de cada execução
    """
    results = []
    
    for i in range(repetitions):
        if algorithm == 'prim':
            adj = graph.get_adjacency_list()
            metrics = measure_performance(prim, graph.n_vertices, adj)
            mst_edges, total_weight = metrics['result']
            # Validação completa
            valid, msg = validate_mst(graph.n_vertices, graph.edges, mst_edges)
        
        elif algorithm == 'kruskal':
            metrics = measure_performance(kruskal, graph.n_vertices, graph.edges)
            mst_edges, total_weight = metrics['result']
            # Validação completa
            valid, msg = validate_mst(graph.n_vertices, graph.edges, mst_edges)
        
        else:
            raise ValueError(f"Algoritmo inválido: {algorithm}")
        
        results.append({
            'algorithm': algorithm,
            'repetition': i + 1,
            'time_seconds': metrics['time_seconds'],
            'memory_mb': metrics.get('memory_mb'),
            'peak_memory_mb': metrics.get('peak_memory_mb'),
            'cpu_seconds': metrics.get('cpu_seconds'),
            'mem_rss_before_mb': metrics.get('mem_rss_before_mb'),
            'mem_rss_mb': metrics.get('mem_rss_mb'),
            'mst_weight': total_weight,
            'mst_edges_count': len(mst_edges),
            'valid': valid,
            'validation_msg': msg
        })
        
        if i == 0:  # Primeira execução
            print(f"\n{algorithm.upper()} - Execução 1/{repetitions}")
            print(f"  Peso da MST: {total_weight:.2f}")
            print(f"  Arestas na MST: {len(mst_edges)}")
            print(f"  Validação: {msg}")
            print(f"  Tempo: {format_time(metrics['time_seconds'])}")
            print(f"  Memória pico: {format_memory(metrics['peak_memory_mb'])}")
            # Mostrar RSS do processo se disponível (psutil)
            mem_rss = metrics.get('mem_rss_mb')
            mem_rss_before = metrics.get('mem_rss_before_mb')
            if mem_rss is not None:
                if mem_rss_before is not None:
                    print(f"  RSS antes: {format_memory(mem_rss_before)} | RSS depois: {format_memory(mem_rss)}")
                else:
                    print(f"  RSS: {format_memory(mem_rss)}")
            
            if not valid:
                print(f"  ⚠️  ATENÇÃO: MST INVÁLIDA!")
    
    return results


def print_comparison(prim_results, kruskal_results):
    """Imprime comparação entre os algoritmos."""
    print("\n" + "="*70)
    print("COMPARAÇÃO FINAL")
    print("="*70)
    
    # Médias
    prim_avg_time = sum(r['time_seconds'] for r in prim_results) / len(prim_results)
    kruskal_avg_time = sum(r['time_seconds'] for r in kruskal_results) / len(kruskal_results)
    
    prim_avg_mem = sum(r['peak_memory_mb'] for r in prim_results) / len(prim_results)
    kruskal_avg_mem = sum(r['peak_memory_mb'] for r in kruskal_results) / len(kruskal_results)
    
    prim_weight = prim_results[0]['mst_weight']
    kruskal_weight = kruskal_results[0]['mst_weight']
    
    print(f"\nTempo médio ({len(prim_results)} execuções):")
    print(f"  Prim:    {format_time(prim_avg_time)}")
    print(f"  Kruskal: {format_time(kruskal_avg_time)}")
    
    if prim_avg_time < kruskal_avg_time:
        speedup = kruskal_avg_time / prim_avg_time
        print(f"  → Prim é {speedup:.2f}x mais rápido")
    else:
        speedup = prim_avg_time / kruskal_avg_time
        print(f"  → Kruskal é {speedup:.2f}x mais rápido")
    
    print(f"\nMemória média (pico):")
    print(f"  Prim:    {format_memory(prim_avg_mem)}")
    print(f"  Kruskal: {format_memory(kruskal_avg_mem)}")
    
    print(f"\nPeso da MST:")
    print(f"  Prim:    {prim_weight:.2f}")
    print(f"  Kruskal: {kruskal_weight:.2f}")
    
    weight_diff = abs(prim_weight - kruskal_weight)
    if weight_diff < 0.01:
        print(f"  ✓ Pesos idênticos (diff: {weight_diff:.6f})")
    else:
        print(f"  ⚠ ATENÇÃO: Pesos diferentes! (diff: {weight_diff:.2f})")
    
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Compara algoritmos Prim e Kruskal para MST'
    )
    parser.add_argument(
        '--vertices',
        required=True,
        help='Arquivo CSV com vértices (coordenadas)'
    )
    parser.add_argument(
        '--edges',
        required=True,
        help='Arquivo CSV com arestas'
    )
    parser.add_argument(
        '--algorithm',
        choices=['prim', 'kruskal', 'both'],
        default='both',
        help='Qual algoritmo executar (padrão: both)'
    )
    parser.add_argument(
        '--repetitions',
        type=int,
        default=1,
        help='Número de repetições (padrão: 1)'
    )
    
    args = parser.parse_args()
    
    # Validar arquivos
    if not Path(args.vertices).exists():
        print(f"ERRO: Arquivo não encontrado: {args.vertices}")
        sys.exit(1)
    if not Path(args.edges).exists():
        print(f"ERRO: Arquivo não encontrado: {args.edges}")
        sys.exit(1)
    
    # Carregar grafo
    print(f"\nCarregando grafo...")
    print(f"  Vértices: {args.vertices}")
    print(f"  Arestas:  {args.edges}")
    
    try:
        graph = load_graph(args.vertices, args.edges)
        graph = graph.normalize_to_zero_based()
    except Exception as e:
        print(f"ERRO ao carregar grafo: {e}")
        sys.exit(1)
    
    print(f"\nGrafo carregado:")
    print(f"  Vértices: {graph.n_vertices}")
    print(f"  Arestas:  {graph.n_edges}")
    
    # Executar algoritmos
    results = {}
    
    if args.algorithm in ['prim', 'both']:
        print(f"\n{'='*70}")
        print(f"EXECUTANDO PRIM ({args.repetitions} repetições)")
        print(f"{'='*70}")
        results['prim'] = run_algorithm('prim', graph, args.repetitions)
    
    if args.algorithm in ['kruskal', 'both']:
        print(f"\n{'='*70}")
        print(f"EXECUTANDO KRUSKAL ({args.repetitions} repetições)")
        print(f"{'='*70}")
        results['kruskal'] = run_algorithm('kruskal', graph, args.repetitions)
    
    # Comparação
    if args.algorithm == 'both':
        print_comparison(results['prim'], results['kruskal'])
    
    return results


if __name__ == "__main__":
    main()