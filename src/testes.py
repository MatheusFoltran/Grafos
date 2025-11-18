"""
Script para gerar grafos de teste.
Útil para testar o código antes de receber as instâncias do professor.
"""
import csv
import random
import math
from pathlib import Path


def generate_random_graph(n_vertices, density=0.3, area_size=10000):
    """
    Gera um grafo aleatório.
    
    Args:
        n_vertices: número de vértices
        density: densidade de arestas (0.0 a 1.0)
        area_size: tamanho da área para distribuir vértices
    
    Returns:
        (vertices, edges): listas de vértices e arestas
    """
    # Gerar vértices com coordenadas aleatórias
    vertices = []
    for _ in range(n_vertices):
        x = random.uniform(0, area_size)
        y = random.uniform(0, area_size)
        vertices.append((x, y))
    
    # Gerar arestas com base na densidade
    edges = []
    max_edges = n_vertices * (n_vertices - 1) // 2
    n_edges = int(max_edges * density)
    
    # Garantir grafo conexo (MST aleatória)
    available = list(range(1, n_vertices))
    connected = [0]
    
    while available:
        u = random.choice(connected)
        v = random.choice(available)
        edges.append((u, v))
        connected.append(v)
        available.remove(v)
    
    # Adicionar arestas extras aleatórias
    all_possible = [(i, j) for i in range(n_vertices) 
                    for j in range(i+1, n_vertices)]
    existing = set((min(u,v), max(u,v)) for u, v in edges)
    
    remaining = [e for e in all_possible if e not in existing]
    random.shuffle(remaining)
    
    extra_edges = min(n_edges - len(edges), len(remaining))
    edges.extend(remaining[:extra_edges])
    
    return vertices, edges


def generate_grid_graph(rows, cols, connection_prob=0.8):
    """
    Gera um grafo em grade (grid).
    
    Args:
        rows, cols: dimensões da grade
        connection_prob: probabilidade de manter cada aresta
    
    Returns:
        (vertices, edges): listas de vértices e arestas
    """
    spacing = 100
    vertices = []
    
    # Criar vértices na grade
    for i in range(rows):
        for j in range(cols):
            x = j * spacing + random.uniform(-10, 10)  # pequena perturbação
            y = i * spacing + random.uniform(-10, 10)
            vertices.append((x, y))
    
    # Criar arestas (vizinhos na grade)
    edges = []
    
    def get_index(r, c):
        return r * cols + c
    
    for i in range(rows):
        for j in range(cols):
            current = get_index(i, j)
            
            # Conectar com vizinho à direita
            if j < cols - 1 and random.random() < connection_prob:
                edges.append((current, get_index(i, j + 1)))
            
            # Conectar com vizinho abaixo
            if i < rows - 1 and random.random() < connection_prob:
                edges.append((current, get_index(i + 1, j)))
    
    return vertices, edges


def save_graph(vertices, edges, output_dir):
    """Salva grafo em arquivos CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar vértices
    vertices_file = output_dir / 'vertices.csv'
    with open(vertices_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y'])
        for x, y in vertices:
            writer.writerow([f"{x:.2f}", f"{y:.2f}"])
    
    # Salvar arestas
    edges_file = output_dir / 'edges.csv'
    with open(edges_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['origem', 'destino'])
        for u, v in edges:
            writer.writerow([u, v])
    
    print(f"✓ Grafo salvo em: {output_dir}")
    print(f"  Vértices: {len(vertices)}")
    print(f"  Arestas: {len(edges)}")


def main():
    """Gera vários grafos de teste."""
    
    print("Gerando grafos de teste...\n")
    
    # Grafo pequeno (para debug)
    print("1. Grafo pequeno (50 vértices)")
    v, e = generate_random_graph(50, density=0.2)
    save_graph(v, e, 'grafos/teste_pequeno')
    
    # Grafo médio
    print("\n2. Grafo médio (200 vértices)")
    v, e = generate_random_graph(200, density=0.15)
    save_graph(v, e, 'grafos/teste_medio')
    
    # Grafo grande
    print("\n3. Grafo grande (500 vértices)")
    v, e = generate_random_graph(500, density=0.1)
    save_graph(v, e, 'grafos/teste_grande')
    
    # Grafo em grade
    print("\n4. Grafo grade (20x20)")
    v, e = generate_grid_graph(20, 20, connection_prob=0.9)
    save_graph(v, e, 'grafos/teste_grade')
    
    # Grafo denso
    print("\n5. Grafo denso (100 vértices, alta densidade)")
    v, e = generate_random_graph(100, density=0.5)
    save_graph(v, e, 'grafos/teste_denso')
    
    # Grafo esparso
    print("\n6. Grafo esparso (300 vértices, baixa densidade)")
    v, e = generate_random_graph(300, density=0.05)
    save_graph(v, e, 'grafos/teste_esparso')
    
    print("\n" + "="*60)
    print("✓ Todos os grafos foram gerados!")
    print("="*60)
    print("\nPara testar:")
    print("  python src/main.py --vertices grafos/teste_pequeno/vertices.csv \\")
    print("                     --edges grafos/teste_pequeno/edges.csv \\")
    print("                     --algorithm both --repetitions 5")


if __name__ == "__main__":
    main()