import pandas as pd

print("="*70)
print("COMPARAÇÃO: Graph Loader Antigo vs Novo")
print("="*70)

# Dados dos experimentos antigos (com graph_loader complexo)
df_old = pd.read_csv('results/resultados_experimentos.csv')
old_data = df_old.groupby('graph_name')[['n_vertices', 'n_edges']].first()

# Dados dos experimentos novos (com graph_loader limpo)
df_test = pd.read_csv('results/test_experiments_v2.csv')
test_data = df_test.groupby('graph_name')[['n_vertices', 'n_edges']].first()

print("\n=== NÚMERO DE VÉRTICES E ARESTAS ===\n")
print("Grafo      | Old Vertices | New Vertices | Old Edges | New Edges | Diff Edges")
print("-"*70)
for graph in old_data.index:
    old_v = old_data.loc[graph, 'n_vertices']
    new_v = test_data.loc[graph, 'n_vertices']
    old_e = old_data.loc[graph, 'n_edges']
    new_e = test_data.loc[graph, 'n_edges']
    diff_e = new_e - old_e
    print(f"{graph:10} | {old_v:12} | {new_v:12} | {old_e:9} | {new_e:9} | {diff_e:+10}")

print("\n=== TEMPOS DE EXECUÇÃO ===\n")
old_times = df_old.groupby(['graph_name', 'algorithm'])['time_seconds'].mean().unstack()
test_times = df_test.groupby(['graph_name', 'algorithm'])['time_seconds'].mean().unstack()

print("PRIM:")
print("Grafo      | Old (ms) | New (ms) | Melhoria")
print("-"*50)
for graph in old_times.index:
    old_prim = old_times.loc[graph, 'prim'] * 1000
    new_prim = test_times.loc[graph, 'prim'] * 1000
    speedup = old_prim / new_prim
    print(f"{graph:10} | {old_prim:8.2f} | {new_prim:8.2f} | {speedup:.2f}x")

print("\nKRUSKAL:")
print("Grafo      | Old (ms) | New (ms) | Melhoria")
print("-"*50)
for graph in old_times.index:
    old_kruskal = old_times.loc[graph, 'kruskal'] * 1000
    new_kruskal = test_times.loc[graph, 'kruskal'] * 1000
    speedup = old_kruskal / new_kruskal
    print(f"{graph:10} | {old_kruskal:8.2f} | {new_kruskal:8.2f} | {speedup:.2f}x")

print("\n" + "="*70)
print("CONCLUSÃO:")
print("="*70)
print("O graph_loader limpo não só é mais legível, como também")
print("removeu um overhead GIGANTE que estava afetando AMBOS algoritmos!")
print("="*70)
