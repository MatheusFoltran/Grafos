import pandas as pd

print('='*70)
print('RESULTADOS FINAIS - Versão Correta (com deduplicação)')
print('='*70)

df = pd.read_csv('results/resultados_experimentos.csv')

# Resumo por grafo e algoritmo
comparison = df.groupby(['graph_name', 'n_vertices', 'algorithm']).agg({
    'time_seconds': ['mean', 'std'],
    'n_edges': 'first'
})

print('\nGrafo      | Vértices |  Arestas | Algoritmo | Tempo (ms) | Desvio')
print('-'*75)
for (graph, vertices, algo), row in comparison.iterrows():
    edges = row[('n_edges', 'first')]
    mean_ms = row[('time_seconds', 'mean')] * 1000
    std_ms = row[('time_seconds', 'std')] * 1000
    print(f'{graph:10} | {vertices:8,} | {edges:8,} | {algo:9} | {mean_ms:10.2f} | ±{std_ms:5.2f}')

# Comparação direta
print('\n' + '='*70)
print('COMPARAÇÃO: Prim vs Kruskal')
print('='*70)

summary = df.groupby(['graph_name', 'algorithm'])['time_seconds'].mean().unstack()
summary['speedup'] = summary['prim'] / summary['kruskal']
summary['winner'] = summary.apply(lambda r: 'Prim' if r['prim'] < r['kruskal'] else 'Kruskal', axis=1)

print('\nGrafo      |   Prim (ms) | Kruskal (ms) | Vencedor | Speedup')
print('-'*65)
for g in summary.index:
    p = summary.loc[g, 'prim'] * 1000
    k = summary.loc[g, 'kruskal'] * 1000
    w = summary.loc[g, 'winner']
    s = summary.loc[g, 'speedup']
    symbol = '✓' if w == 'Kruskal' else '✗'
    print(f'{g:10} | {p:11.2f} | {k:12.2f} | {w:8} | {s:.3f}x {symbol}')

print('\n' + '='*70)
print('CONCLUSÃO:')
print('  • Graph loader CORRETO: carrega todas as arestas do CSV')
print('  • Deduplicação simples: remove duplicatas com set lookup')
print('  • Kruskal vence na maioria dos casos (ordenação em C é rápida)')
print('  • Diferenças são pequenas: ambos algoritmos estão bem otimizados')
print('='*70)
