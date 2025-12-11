import argparse
import sys
from pathlib import Path

from graph_loader import carregar_grafo
from prim import prim
from kruskal import kruskal
from validation import validar_mst
from metrics import medir_desempenho, formatar_tempo, formatar_memoria


def executar_algoritmo(algoritmo: str, grafo, repeticoes: int = 1):
    resultados = []
    
    for i in range(repeticoes):
        if algoritmo == 'prim':
            adj = grafo.obter_lista_adjacencias()
            metricas = medir_desempenho(prim, grafo.n_vertices, adj)
            arestas_mst, peso_total = metricas['result']
            valida = validar_mst(grafo.n_vertices, grafo.arestas, arestas_mst)
            mensagem = "Válida" if valida else "Inválida"
        
        elif algoritmo == 'kruskal':
            metricas = medir_desempenho(kruskal, grafo.n_vertices, grafo.arestas)
            arestas_mst, peso_total = metricas['result']
            valida = validar_mst(grafo.n_vertices, grafo.arestas, arestas_mst)
            mensagem = "Válida" if valida else "Inválida"
        
        else:
            raise ValueError(f"Algoritmo inválido: {algoritmo}")
        
        resultados.append({
            'algorithm': algoritmo,
            'repetition': i + 1,
            'time_seconds': metricas['time_seconds'],
            'memory_mb': metricas.get('memory_mb'),
            'peak_memory_mb': metricas.get('peak_memory_mb'),
            'cpu_seconds': metricas.get('cpu_seconds'),
            'mem_rss_before_mb': metricas.get('mem_rss_before_mb'),
            'mem_rss_mb': metricas.get('mem_rss_mb'),
            'mst_weight': peso_total,
            'mst_edges_count': len(arestas_mst),
            'valid': valida,
            'validation_msg': mensagem
        })
        
        if i == 0:
            print(f"\n{algoritmo.upper()} - Execução 1/{repeticoes}")
            print(f"  Peso da MST: {peso_total:.2f}")
            print(f"  Arestas na MST: {len(arestas_mst)}")
            print(f"  Validação: {mensagem}")
            print(f"  Tempo: {formatar_tempo(metricas['time_seconds'])}")
            print(f"  Memória pico: {formatar_memoria(metricas['peak_memory_mb'])}")
            mem_rss = metricas.get('mem_rss_mb')
            mem_rss_before = metricas.get('mem_rss_before_mb')
            if mem_rss is not None:
                if mem_rss_before is not None:
                    print(f"  RSS antes: {formatar_memoria(mem_rss_before)} | RSS depois: {formatar_memoria(mem_rss)}")
                else:
                    print(f"  RSS: {formatar_memoria(mem_rss)}")
            
            if not valida:
                print(f"MST inválida!")
    
    return resultados


def print_comparison(resultados_prim, resultados_kruskal):
    print("\nCOMPARAÇÃO FINAL")
    
    # Calcular médias de tempo
    tempos_prim = [r['time_seconds'] for r in resultados_prim]
    tempos_kruskal = [r['time_seconds'] for r in resultados_kruskal]
    tempo_medio_prim = sum(tempos_prim) / len(tempos_prim)
    tempo_medio_kruskal = sum(tempos_kruskal) / len(tempos_kruskal)
    
    # Calcular médias de memória
    memorias_prim = [r['peak_memory_mb'] for r in resultados_prim]
    memorias_kruskal = [r['peak_memory_mb'] for r in resultados_kruskal]
    mem_media_prim = sum(memorias_prim) / len(memorias_prim)
    mem_media_kruskal = sum(memorias_kruskal) / len(memorias_kruskal)
    
    peso_prim = resultados_prim[0]['mst_weight']
    peso_kruskal = resultados_kruskal[0]['mst_weight']
    
    print(f"\nTempo médio ({len(resultados_prim)} execuções):")
    print(f"  Prim:    {formatar_tempo(tempo_medio_prim)}")
    print(f"  Kruskal: {formatar_tempo(tempo_medio_kruskal)}")
    
    if tempo_medio_prim < tempo_medio_kruskal:
        aceleracao = tempo_medio_kruskal / tempo_medio_prim
        print(f" Prim é {aceleracao:.2f}x mais rápido")
    else:
        aceleracao = tempo_medio_prim / tempo_medio_kruskal
        print(f" Kruskal é {aceleracao:.2f}x mais rápido")
    
    print(f"\nMemória média (pico):")
    print(f"  Prim:    {formatar_memoria(mem_media_prim)}")
    print(f"  Kruskal: {formatar_memoria(mem_media_kruskal)}")
    
    print(f"\nPeso da MST:")
    print(f"  Prim:    {peso_prim:.2f}")
    print(f"  Kruskal: {peso_kruskal:.2f}")
    
    diferenca_peso = abs(peso_prim - peso_kruskal)
    if diferenca_peso < 0.01:
        print(f"Pesos idênticos (diferença: {diferenca_peso:.6f})")
    else:
        print(f"Pesos diferentes (diferença: {diferenca_peso:.2f})")


def main():
    parser = argparse.ArgumentParser(
        description='Compara algoritmos Prim e Kruskal para MST'
    )
    parser.add_argument(
        '--vertices',
        required=True,
        help='Arquivo CSV com vértices'
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
    
    argumentos = parser.parse_args()
    
    # Valida a existência dos arquivos
    if not Path(argumentos.vertices).exists():
        print(f"Arquivo não encontrado: {argumentos.vertices}")
        sys.exit(1)
    if not Path(argumentos.edges).exists():
        print(f"Arquivo não encontrado: {argumentos.edges}")
        sys.exit(1)
    
    print(f"\nCarregando grafo...")
    print(f"  Vértices: {argumentos.vertices}")
    print(f"  Arestas:  {argumentos.edges}")
    
    try:
        grafo = carregar_grafo(argumentos.vertices, argumentos.edges)
        grafo = grafo.normalizar_para_zero()
    except Exception as erro:
        print(f"ERRO ao carregar grafo: {erro}")
        sys.exit(1)
    
    print(f"\nGrafo carregado:")
    print(f"  Vértices: {grafo.n_vertices}")
    print(f"  Arestas:  {grafo.n_arestas}")
    
    # Executar algoritmos
    resultados = {}
    
    if argumentos.algorithm in ['prim', 'both']:
        print(f"EXECUTANDO PRIM ({argumentos.repetitions} repetições)")
        resultados['prim'] = executar_algoritmo('prim', grafo, argumentos.repetitions)
    
    if argumentos.algorithm in ['kruskal', 'both']:
        print(f"EXECUTANDO KRUSKAL ({argumentos.repetitions} repetições)")
        resultados['kruskal'] = executar_algoritmo('kruskal', grafo, argumentos.repetitions)
    
    # Compara os dois algoritmos
    if argumentos.algorithm == 'both':
        print_comparison(resultados['prim'], resultados['kruskal'])
    
    return resultados


if __name__ == "__main__":
    main()