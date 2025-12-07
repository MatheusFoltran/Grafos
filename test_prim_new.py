import sys
import time
sys.path.insert(0, 'src')
from graph_loader import load_graph
from prim import prim
from kruskal import kruskal

print("="*70)
print("TESTE: Nova versão Prim (heap de vértices) vs Kruskal")
print("="*70)

# Testar com todos os grafos
for i in [1, 2, 3, 4, 5, 6]:
    graph_name = f'Grafo{i}'
    g = load_graph(f'Grafos/{graph_name}/Nodes{i}.csv', 
                   f'Grafos/{graph_name}/Edges{i}.csv')
    g = g.normalize_to_zero_based()
    
    n = g.n_vertices
    adj = g.get_adjacency_list()
    edges = g.edges
    
    # Benchmark Prim (3 runs)
    times_prim = []
    for _ in range(3):
        start = time.perf_counter()
        mst_p, weight_p = prim(n, adj)
        times_prim.append(time.perf_counter() - start)
    
    # Benchmark Kruskal (3 runs)
    times_kruskal = []
    for _ in range(3):
        start = time.perf_counter()
        mst_k, weight_k = kruskal(n, edges)
        times_kruskal.append(time.perf_counter() - start)
    
    avg_prim = sum(times_prim) / len(times_prim)
    avg_kruskal = sum(times_kruskal) / len(times_kruskal)
    
    winner = "Prim" if avg_prim < avg_kruskal else "Kruskal"
    speedup = max(avg_prim, avg_kruskal) / min(avg_prim, avg_kruskal)
    
    print(f"\n{graph_name:8} ({n:>7,} v) | Prim: {avg_prim*1000:6.2f}ms | Kruskal: {avg_kruskal*1000:6.2f}ms | {winner:7} {speedup:.2f}x")

print("\n" + "="*70)
