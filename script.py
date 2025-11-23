import pandas as pd
# read canonical results location
df = pd.read_csv('results/resultados_experimentos.csv')

# Estatísticas por grafo e algoritmo
group = df.groupby(['graph_name','algorithm'])
summary = group.agg(
    runs=('repetition','count'),
    mean_time=('time_seconds','mean'),
    std_time=('time_seconds','std'),
    mean_mem=('memory_mb','mean'),
    mean_peak=('peak_memory_mb','mean'),
    mean_weight=('mst_weight','mean'),
    std_weight=('mst_weight','std'),
    mean_edges=('mst_edges_count','mean'),
    invalid_runs=('valid', lambda x: (~x).sum())
).reset_index()

print(summary.to_string(index=False))

# Checar igualdade de pesos entre algoritmos (por grafo)
pivot = df.pivot_table(index='graph_name', columns='algorithm', values='mst_weight', aggfunc='mean')
print("\nPesos médios por grafo (Prim vs Kruskal):")
print(pivot)

# Mostrar quaisquer mensagens de validação diferentes de OK
bad = df[df['valid'] == False]
if not bad.empty:
    print("\nExecutions invalidas (mostrando mensagens):")
    print(bad[['graph_name','algorithm','repetition','validation_msg']].to_string(index=False))
else:
    print("\nNenhuma execução inválida encontrada.")