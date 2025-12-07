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
│   ├── validation.py        # Validação de MST
│   ├── metrics.py           # Medição de tempo e memória
│   ├── experiments.py       # Experimentos automatizados
│   └── analysis.ipynb       # Análise e visualização
│
├── Grafos/
│   ├── Grafo1/
│   │   ├── Nodes1.csv
│   │   └── Edges1.csv
│   ├── Grafo2/
│   │   ├── Nodes2.csv
│   │   └── Edges2.csv
│   └── ...
│
├── results/
│   └── resultados_experimentos.csv  # Resultados salvos
└── README.md
```

## 🔧 Requisitos

- Python 3.8+
- Bibliotecas padrão: `heapq`, `csv`, `math`, `time`, `tracemalloc`

### Instalação de Dependências

```bash
# Instalar dependências opcionais (recomendado)
pip install -r requirements.txt
```

**Dependências opcionais:**
- `psutil` - Medição de RSS (memória total do processo) - **já implementado**
- `pandas`, `matplotlib`, `seaborn` - Análise e visualização de resultados
- `jupyter` - Para rodar o notebook de análise

**Nota:** O projeto funciona sem essas dependências, mas com funcionalidade reduzida:
- Sem `psutil`: apenas medição via `tracemalloc` (heap Python)
- Sem pandas/matplotlib: não é possível gerar gráficos no notebook

## 📊 Formato dos Arquivos CSV

### Nodes*.csv (Vértices)
```csv
# Formato: id,x,y (coordenadas UTM)
id,x,y
1,673571.91,3796789.73
2,673532.44,3797021.58
3,673725.67,3796734.16
```

### Edges*.csv (Arestas)
```csv
# Formato: source,target (IDs dos vértices)
source,target
1,2
2,3
1,3
```

**Importante:** 
- Vértices têm ID numérico + coordenadas UTM (Universal Transverse Mercator)
- Arestas usam os IDs dos vértices (podem começar em 1, são normalizados internamente)
- Peso das arestas = distância euclidiana calculada automaticamente: d = √[(x₁-x₂)² + (y₁-y₂)²]

## 🚀 Uso

### Execução Individual (CLI)

```bash
# Executar ambos algoritmos em um grafo
python src/main.py \
    --vertices Grafos/Grafo1/Nodes1.csv \
    --edges Grafos/Grafo1/Edges1.csv \
    --algorithm both \
    --repetitions 3

# Executar apenas Prim
python src/main.py \
    --vertices Grafos/Grafo1/Nodes1.csv \
    --edges Grafos/Grafo1/Edges1.csv \
    --algorithm prim

# Executar apenas Kruskal
python src/main.py \
    --vertices Grafos/Grafo1/Nodes1.csv \
    --edges Grafos/Grafo1/Edges1.csv \
    --algorithm kruskal
```

**Parâmetros:**
- `--vertices`: arquivo CSV com vértices (Nodes*.csv)
- `--edges`: arquivo CSV com arestas (Edges*.csv)
- `--algorithm`: prim | kruskal | both (padrão: both)
- `--repetitions`: número de repetições (padrão: 1)

**Saída típica:**
```
Grafo carregado:
  Vértices: 8980
  Arestas:  12629

PRIM - Execução 1/3
  Peso da MST: 3015372.43
  Arestas na MST: 8979
  Validação: ✓ MST/Floresta válida
  Tempo: 30.69 ms
  Memória pico: 751.18 KB

KRUSKAL - Execução 1/3
  Peso da MST: 3015372.43
  Arestas na MST: 8979
  Validação: ✓ MST/Floresta válida
  Tempo: 23.91 ms
  Memória pico: 749.21 KB

COMPARAÇÃO FINAL
  Kruskal é 1.14x mais rápido
  ✓ Pesos idênticos (diff: 0.000000)
```

### Experimentos Automatizados

```bash
# Executar experimentos em todos os grafos com 5 repetições
python src/experiments.py -r 5 -o results/resultados_experimentos.csv
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
- Usa `heapq` (min-heap) para seleção eficiente de vértices
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
- ⏱️ **Tempo de execução** (wall time e CPU time)
- 💾 **Memória heap Python** (`tracemalloc`) - alocações Python
- 💾 **Memória RSS** (`psutil`, se instalado) - memória total do processo
- 📊 **Peso da MST**
- 🔢 **Número de arestas na MST**
- ✅ **Validação** (floresta geradora válida)

### Medição de Memória

O projeto usa duas abordagens complementares:

1. **`tracemalloc` (sempre ativo):**
   - Mede alocações do heap gerenciado pelo Python
   - Portátil (funciona em todos os SOs)
   - Útil para comparar implementações Python
   - Limitação: não mede overhead do interpretador nem bibliotecas C

2. **`psutil` (opcional, mas implementado):**
   - Mede RSS (Resident Set Size) do processo inteiro
   - Inclui memória de bibliotecas C, buffers do SO, overhead do interpretador
   - Instalação: `pip install psutil`
   - Se não instalado, o código continua funcionando (apenas sem métricas RSS)

## Autor

- Matheus Foltran Consonni