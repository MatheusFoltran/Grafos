# Verificação de Conformidade com Especificação UEM

**Disciplina:** Algoritmos em Grafos  
**Avaliação:** 3 - 2025  
**Data de Verificação:** 7 de dezembro de 2025

---

## ✅ 1. Requisitos Mínimos (Implementação)

### ✅ Algoritmos Implementados

**Prim (com heap)** - `src/prim.py`
- ✅ Usa `heapq` (biblioteca padrão Python)
- ✅ Implementação com "heap de vértices" (indexed heap/key-based priority queue)
- ✅ Complexidade: O(E log V)
- ✅ Claramente identificável no código
- ✅ Sem bibliotecas de grafos

**Kruskal (vetor de índices e união pela menor altura)** - `src/kruskal.py`
- ✅ Union-Find com vetor `parent` (índices)
- ✅ Union by rank (união pela menor altura)
- ✅ Path compression (compressão de caminho)
- ✅ Complexidade: O(E log E)
- ✅ Claramente identificável no código
- ✅ Sem bibliotecas de grafos

### ✅ Restrições de Bibliotecas

**Bibliotecas Usadas:**
- ✅ Padrão Python: `heapq`, `csv`, `math`, `time`, `tracemalloc`, `argparse`
- ✅ Análise (permitido): `pandas`, `matplotlib`, `seaborn`, `jupyter`
- ✅ **Nenhuma biblioteca de grafos** (NetworkX, igraph, etc.)

### ✅ Formato de Entrada

**Vértices (Nodes*.csv):**
- ✅ Formato: `id,x,y`
- ✅ Coordenadas em sistema UTM (Universal Transverse Mercator)
- ✅ Detecta automaticamente presença de header

**Arestas (Edges*.csv):**
- ✅ Formato: `source,target` (IDs dos vértices)
- ✅ Detecta automaticamente presença de header
- ✅ Calcula peso pela distância Euclidiana: d(vᵢ, vⱼ) = √[(xᵢ-xⱼ)² + (yᵢ-yⱼ)²]

### ✅ Linha de Comando

**Interface CLI** - `src/main.py`

```bash
python src/main.py \
    --vertices Grafos/Grafo1/Nodes1.csv \
    --edges Grafos/Grafo1/Edges1.csv \
    --algorithm both \
    --repetitions 3
```

Parâmetros:
- ✅ `--vertices`: arquivo CSV de vértices
- ✅ `--edges`: arquivo CSV de arestas
- ✅ `--algorithm`: prim | kruskal | both
- ✅ `--repetitions`: número de repetições

---

## ✅ 2. Implementação Correta (40%)

### ✅ Correção dos Algoritmos

**Teste Executado:**
```
Grafo1 (8,980 vértices, 12,629 arestas)
- Prim: peso = 3015372.43, 8979 arestas na MST
- Kruskal: peso = 3015372.43, 8979 arestas na MST
- ✓ Pesos idênticos (diff: 0.000000)
```

### ✅ Tratamento de Grafos Desconexos

**Prim** (`src/prim.py`, linha 88):
```python
# PASSO 1: Processar cada componente conexa
for start_vertex in range(n_vertices):
    if in_mst[start_vertex]:
        continue  # Pular vértices já processados
    # Iniciar Prim nesta componente...
```
✅ Retorna **Floresta Geradora Mínima** (MSF) quando grafo é desconexo

**Kruskal** (`src/kruskal.py`, linha 135):
```python
# Tratamento de grafos desconexos:
#     Se o grafo for desconexo, retorna uma floresta geradora mínima
#     (MSF - Minimum Spanning Forest) contendo menos de n-1 arestas.
```
✅ Naturalmente lida com grafos desconexos

### ✅ Validação de Resultados

**Módulo de Validação** - `src/validation.py`

Verifica:
1. ✅ Ausência de ciclos (acyclicity)
2. ✅ Cobertura completa de vértices (completeness)
3. ✅ Número correto de arestas por componente conexa
4. ✅ Arestas da MST pertencem ao grafo original
5. ✅ Componentes conexas tratadas separadamente

Saída típica:
```
✓ MST/Floresta válida (aciclicidade e cobertura por componente confirmadas)
```

---

## ✅ 3. Qualidade do Código (10%)

### ✅ Organização

```
src/
├── main.py           # Interface CLI principal
├── graph_loader.py   # Carregamento de grafos
├── prim.py           # Algoritmo de Prim
├── kruskal.py        # Algoritmo de Kruskal
├── validation.py     # Validação robusta de MST
├── metrics.py        # Medição de desempenho
├── experiments.py    # Experimentos automatizados
└── analysis.ipynb    # Análise estatística
```

✅ Separação clara de responsabilidades  
✅ Módulos independentes e reutilizáveis  
✅ Nomes descritivos e consistentes

### ✅ Clareza

**Exemplo de documentação (prim.py):**
```python
def prim(n_vertices: int, adj: List[List[Tuple[int, float]]]) 
    -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Algoritmo de Prim para Árvore Geradora Mínima.
    
    Implementação com HEAP DE VÉRTICES (key-based priority queue).
    
    Complexidade:
    - Tempo: O(E log V) com binary heap
    - Espaço: O(V)
    
    Args:
        n_vertices: número de vértices (0 a n-1)
        adj: lista de adjacências adj[u] = [(v, peso), ...]
    
    Returns:
        Tupla (mst_edges, total_weight)
    """
```

✅ Docstrings em todos os módulos e funções principais  
✅ Explicação de complexidade de tempo e espaço  
✅ Exemplos de uso incluídos

### ✅ Documentação

**README.md:**
- ✅ Estrutura do projeto
- ✅ Requisitos e instalação
- ✅ Formato dos arquivos CSV
- ✅ Exemplos de uso da CLI
- ✅ Instruções para experimentos

**Comentários no código:**
- ✅ Explicações de otimizações (path compression, union by rank)
- ✅ Marcação de passos dos algoritmos
- ✅ Justificativas de escolhas de implementação

---

## ✅ 4. Experimentos (30%)

### ✅ Variedade de Instâncias

**6 Grafos Testados:**
```
Grafo1:  8,980 vértices, 12,629 arestas
Grafo2:  5,152 vértices,  7,086 arestas
Grafo3: 37,128 vértices, 54,867 arestas
Grafo4: 12,368 vértices, 16,965 arestas
Grafo5: 212,341 vértices, 307,292 arestas
Grafo6: 154,938 vértices, 214,893 arestas
```

✅ Diferentes tamanhos (5k a 212k vértices)  
✅ Diferentes densidades  
✅ Formato UTM correto

### ✅ Controles

**Medições:**
- ✅ Tempo de execução (Python `time.perf_counter()`)
- ✅ Memória de pico (`tracemalloc`)
- ✅ RSS antes/depois da execução
- ✅ Peso total da MST
- ✅ Número de arestas na MST

**Validações:**
- ✅ Acyclicity (ausência de ciclos)
- ✅ Completeness (cobertura de vértices)
- ✅ Consistência de pesos entre algoritmos

### ✅ Repetições

**Experimentos Automatizados** - `src/experiments.py`

```bash
python src/experiments.py -r 5 -o results/resultados_experimentos.csv
```

✅ 5 repetições por algoritmo por grafo  
✅ 60 execuções totais (6 grafos × 2 algoritmos × 5 repetições)  
✅ Resultados salvos em CSV estruturado

### ✅ Medições Apropriadas

**Métricas Coletadas:**
- ✅ Tempo médio e desvio padrão
- ✅ Memória média e pico
- ✅ Speedup entre algoritmos
- ✅ Validação de correção (diff de pesos < 0.01)

**Exemplo de Saída:**
```
COMPARAÇÃO FINAL
Tempo médio (3 execuções):
  Prim:    27.71 ms
  Kruskal: 24.26 ms
  → Kruskal é 1.14x mais rápido

Peso da MST:
  Prim:    3015372.43
  Kruskal: 3015372.43
  ✓ Pesos idênticos (diff: 0.000000)
```

---

## ✅ 5. Análise e Relatório (20%)

### ✅ Análise Estatística

**Notebook Jupyter** - `src/analysis.ipynb`

Conteúdo:
1. ✅ Carregamento e limpeza de dados
2. ✅ Estatísticas descritivas (média, desvio padrão)
3. ✅ Gráficos de tempo por tamanho de grafo
4. ✅ Gráficos de memória
5. ✅ Análise de speedup
6. ✅ Comparação lado a lado

### ✅ Gráficos

**Visualizações Geradas:**
- ✅ Tempo de execução por algoritmo (barras)
- ✅ Speedup relativo
- ✅ Memória por algoritmo
- ✅ Tempo vs tamanho do grafo (linhas)
- ✅ Cores consistentes (Prim = azul, Kruskal = laranja)

### ✅ Interpretação

**Conclusões dos Experimentos:**

```
CONCLUSÃO:
• Graph loader CORRETO: carrega todas as arestas do CSV
• Kruskal vence em todos os 6 grafos testados
• Speedup de 1.014x a 1.145x (1.4% a 14.5% mais rápido)
• Diferenças pequenas: ambos algoritmos bem otimizados
• Kruskal se beneficia de ordenação em C (Timsort)
• Prim muito eficiente com heap de vértices
```

✅ Análise fundamentada nos dados  
✅ Explicação das diferenças de desempenho  
✅ Reconhecimento de trade-offs  
✅ Conclusões alinhadas com teoria

---

## 📊 Resultados Finais

| Grafo  | Vértices | Arestas | Prim (ms) | Kruskal (ms) | Vencedor | Speedup |
|--------|----------|---------|-----------|--------------|----------|---------|
| Grafo1 | 8,980    | 12,629  | 26.82     | 24.04        | Kruskal  | 1.115x  |
| Grafo2 | 5,152    | 7,086   | 13.20     | 12.90        | Kruskal  | 1.023x  |
| Grafo3 | 37,128   | 54,867  | 121.05    | 111.59       | Kruskal  | 1.085x  |
| Grafo4 | 12,368   | 16,965  | 34.30     | 33.84        | Kruskal  | 1.014x  |
| Grafo5 | 212,341  | 307,292 | 886.49    | 774.26       | Kruskal  | 1.145x  |
| Grafo6 | 154,938  | 214,893 | 591.48    | 543.71       | Kruskal  | 1.088x  |

---

## ✅ Checklist Final

### Implementação Correta (40%)
- ✅ Prim correto e eficiente
- ✅ Kruskal correto e eficiente
- ✅ Trata grafos desconexos
- ✅ Valida resultados

### Qualidade do Código (10%)
- ✅ Organização clara
- ✅ Código limpo e legível
- ✅ Documentação completa

### Experimentos (30%)
- ✅ Variedade de instâncias
- ✅ Controles adequados
- ✅ Repetições suficientes
- ✅ Medições apropriadas

### Análise e Relatório (20%)
- ✅ Gráficos informativos
- ✅ Interpretação fundamentada
- ✅ Conclusões razoadas

---

## ✨ Destaques da Implementação

1. **Prim Otimizado:** Usa heap de vértices em vez de heap de arestas
   - Heap menor: O(V) vs O(E)
   - Menos operações: sem lazy deletion
   - Ideal para grafos densos

2. **Kruskal Eficiente:** Union-Find com todas as otimizações
   - Path compression iterativo (evita recursão)
   - Union by rank (árvore balanceada)
   - Early stopping quando MST completa

3. **Validação Robusta:** Detecta problemas em grafos desconexos
   - Verifica componentes separadamente
   - Confirma k-1 arestas por componente de k vértices
   - Detecta ciclos e cobertura incompleta

4. **Workflow Profissional:**
   - CLI com argparse
   - Experimentos reproduzíveis
   - Resultados em CSV estruturado
   - Análise estatística rigorosa

---

## 🎯 Conclusão

**O projeto está 100% conforme a especificação UEM.**

Todos os requisitos foram atendidos:
- ✅ Algoritmos corretos e bem implementados
- ✅ Sem bibliotecas de grafos proibidas
- ✅ Aceita formato CSV especificado
- ✅ Interface de linha de comando funcional
- ✅ Tratamento de grafos desconexos
- ✅ Validação robusta de resultados
- ✅ Experimentos completos com repetições
- ✅ Análise estatística e gráficos
- ✅ Código bem organizado e documentado

**Pronto para entrega em 11 de dezembro de 2025.**
