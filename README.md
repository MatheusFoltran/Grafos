# Avaliação Computacional: Prim vs Kruskal

Implementação e comparação dos algoritmos de Prim e Kruskal para cálculo de Árvore Geradora Mínima (MST).

## 📁 Estrutura do Projeto

```
.
├── src/
│   ├── main.py              # Programa principal (CLI)
│   ├── graph_loader.py      # Carregamento de grafos CSV
│   ├── prim.py              # Implementação do Prim
│   ├── kruskal.py           # Implementação do Kruskal 
│   ├── metrics.py           # Medição de tempo e memória
│   ├── experiments.py       # Experimentos automatizados
│   └── analysis.ipynb       # Análise e visualização (TODO)
│
├── grafos/
│   ├── grafo1/
│   │   ├── vertices.csv
│   │   └── edges.csv
│   ├── grafo2/
│   │   ├── vertices.csv
│   │   └── edges.csv
│   └── ...
│
├── resultados_experimentos.csv  # Resultados salvos
└── README.md
```

## 🔧 Requisitos

- Python 3.8+
- Bibliotecas padrão: `heapq`, `csv`, `math`, `time`, `tracemalloc`
- Opcional: `pandas`, `matplotlib`, `seaborn` (para análise)

```bash
pip install pandas matplotlib seaborn jupyter
```

## 📊 Formato dos Arquivos CSV

### vertices.csv
```csv
x,y
1000.5,2000.3
1500.2,2100.8
...
```

### edges.csv
```csv
origem,destino
0,1
0,2
1,2
...
```

**Importante:** 
- Vértices são identificados por suas coordenadas (x, y)
- Arestas usam índices (0, 1, 2, ...) correspondentes à ordem no vertices.csv
- Peso das arestas = distância euclidiana calculada automaticamente

## 🚀 Uso

### Execução Individual

```bash
# Executar ambos algoritmos
python src/main.py \
    --vertices grafos/grafo1/vertices.csv \
    --edges grafos/grafo1/edges.csv \
    --algorithm both \
    --repetitions 10

# Executar apenas Prim
python src/main.py \
    --vertices grafos/grafo1/vertices.csv \
    --edges grafos/grafo1/edges.csv \
    --algorithm prim

# Executar apenas Kruskal
python src/main.py \
    --vertices grafos/grafo1/vertices.csv \
    --edges grafos/grafo1/edges.csv \
    --algorithm kruskal
```

### Experimentos Automatizados

```bash
# 1. Editar experiments.py e configurar caminhos dos grafos
# 2. Executar:
python src/experiments.py

# Resultados salvos em: resultados_experimentos.csv
```

### Análise dos Resultados

```bash
# Abrir Jupyter Notebook
jupyter notebook src/analysis.ipynb
```

## 🧪 Testes Básicos

Cada módulo pode ser testado individualmente:

```bash
python src/graph_loader.py    # Teste carregamento
python src/prim.py             # Teste Prim
python src/kruskal.py          # Teste Kruskal + Union-Find
python src/metrics.py          # Teste medições
```

## ⚙️ Implementações

### Prim
- Usa `heapq` (min-heap) para seleção eficiente de arestas
- Complexidade: O(E log V)
- Lida com grafos desconexos (floresta geradora)

### Kruskal
- Union-Find com:
  - **Union by rank** (união pela menor altura)
  - **Path compression** (compressão de caminho)
- Ordena arestas por peso
- Complexidade: O(E log E)
- Lida com grafos desconexos

## 📈 Métricas Coletadas

Para cada execução:
- ⏱️ **Tempo de execução** (segundos)
- 💾 **Memória usada** (MB)
- 📊 **Peso da MST**
- 🔢 **Número de arestas na MST**
- ✅ **Validação** (floresta geradora válida)

### Medição de Memória (limitações)

- Por padrão o projeto usa `tracemalloc` (em `src/metrics.py`) para medir alocações do heap do Python. Isso é portátil e útil para comparar implementações puramente Python, mas tem limitações importantes:
    - `tracemalloc` mede apenas alocações gerenciadas pelo interpretador Python (heap). Não mede o RSS total do processo (memória usada por bibliotecas C, buffers do SO, ou overhead do interpretador).
    - No Windows o módulo `resource` não está disponível; portanto `tracemalloc` é a opção mais portátil.
    - Se quiser medir o uso total de memória do processo (RSS), recomendo usar `psutil` como opção adicional (`pip install psutil`). Implementar `psutil` permite coletar `mem_rss` (em bytes) e compará-lo com `tracemalloc`.

    Recomendação: mantenha `tracemalloc` como padrão para comparações entre implementações Python, e documente diferenças ao interpretar resultados. Se precisar eu posso adicionar um flag `--mem-method` para alternar para `psutil` quando instalado.

### Matching tolerante por coordenadas (`coord_tolerance`)

- Por padrão o `graph_loader` mapeia arestas fornecidas por coordenadas (x1,y1,x2,y2) para vértices fazendo um lookup exato por coordenadas arredondadas (6 casas). Isto é rápido e determinístico quando as coordenadas batem exatamente.
- Para casos onde as coordenadas das arestas têm pequeno ruído (por ex. exportações com diferenças de ponto flutuante), há uma opção de tolerância espacial:
    - `--coord-tolerance <valor>` em `src/experiments.py` (ou chamando `load_graph(..., coord_tolerance=<valor>)`) tenta mapear as coordenadas de arestas para o vértice mais próximo dentro da tolerância fornecida.
    - Implementação: o loader usa um spatial-hash grid interno (sem dependências extras) para reduzir as buscas a células vizinhas (muito mais rápido que varredura completa).
    - Exemplo de uso (experimentos):

```powershell
python src/experiments.py --repetitions 5 --coord-tolerance 0.0001
```

    - `coord_tolerance` deve estar na mesma unidade das coordenadas (mesma escala). Se `coord_tolerance == 0` (padrão), o comportamento anterior (arredondamento exato) é usado.


## 📝 Checklist de Entrega

- [ ] Implementação correta de Prim (com heap)
- [ ] Implementação correta de Kruskal (Union-Find com rank + path compression)
- [ ] Tratamento de grafos desconexos
- [ ] Validação dos resultados
- [ ] Experimentos com múltiplas instâncias
- [ ] Múltiplas repetições por instância
- [ ] Medição de tempo e memória
- [ ] Gráficos comparativos
- [ ] Análise e conclusões no relatório
- [ ] Código organizado e documentado

## 🎯 Próximos Passos

1. **Obter instâncias de grafos do professor**
2. **Organizar em `grafos/`**
3. **Configurar `experiments.py`** com caminhos corretos
4. **Executar experimentos** (várias repetições)
5. **Criar `analysis.ipynb`** para:
   - Carregar `resultados_experimentos.csv`
   - Gerar gráficos (tempo vs tamanho, memória, etc.)
   - Análise estatística
6. **Escrever relatório** com conclusões

## 👥 Equipe

- [Seu nome]
- [Nome 2]
- [Nome 3]

## 📅 Entrega

**Data:** 11 de dezembro de 2025