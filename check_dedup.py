import pandas as pd

print('='*70)
print('VERIFICAÇÃO: Contagem de arestas')
print('='*70)

df_old = pd.read_csv('results/resultados_experimentos.csv')
df_new = pd.read_csv('results/test_experiments_dedup.csv')

old_data = df_old.groupby('graph_name')[['n_edges']].first()
new_data = df_new.groupby('graph_name')[['n_edges']].first()

print('\nGrafo      | Old Edges | New Edges | Diferença')
print('-'*55)
for g in old_data.index:
    old_e = old_data.loc[g, 'n_edges']
    new_e = new_data.loc[g, 'n_edges']
    diff = new_e - old_e
    print(f'{g:10} | {old_e:9,} | {new_e:9,} | {diff:+9,}')

total_diff = (new_data['n_edges'] - old_data['n_edges']).sum()
print(f'\nDiferença TOTAL: {total_diff:+,} arestas')

if total_diff > 0:
    print('\n❌ PROBLEMA: Deduplicação NÃO está funcionando!')
    print('   A versão nova tem MAIS arestas que a antiga.')
elif total_diff == 0:
    print('\n✓ OK: Mesmo número de arestas')
else:
    print('\n✓ DEDUPLICAÇÃO FUNCIONOU!')
    print(f'   Removeu {-total_diff:,} arestas duplicadas')
