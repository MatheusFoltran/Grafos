"""
Módulo para medição de desempenho (tempo e memória) dos algoritmos.
"""
import time
import tracemalloc
from typing import Callable, Any, Dict


def measure_performance(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Mede tempo de execução e uso de memória de uma função.
    
    Args:
        func: função a ser medida
        *args, **kwargs: argumentos para a função
    
    Returns:
        Dicionário com:
        - result: resultado da função
        - time_seconds: tempo de execução em segundos
        - memory_mb: memória usada em MB
        - peak_memory_mb: pico de memória em MB
    """
    # Iniciar medição de memória
    tracemalloc.start()
    
    # Medir tempo
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    
    # Obter estatísticas de memória
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return {
        'result': result,
        'time_seconds': end_time - start_time,
        'memory_mb': current / (1024 * 1024),
        'peak_memory_mb': peak / (1024 * 1024)
    }


def format_time(seconds: float) -> str:
    """Formata tempo em unidade apropriada."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1_000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def format_memory(mb: float) -> str:
    """Formata memória em unidade apropriada."""
    if mb < 1:
        return f"{mb * 1024:.2f} KB"
    elif mb < 1024:
        return f"{mb:.2f} MB"
    else:
        return f"{mb / 1024:.2f} GB"


class PerformanceTracker:
    """Classe para rastrear múltiplas execuções e calcular estatísticas."""
    
    def __init__(self):
        self.runs = []
    
    def add_run(self, metrics: Dict[str, Any]):
        """Adiciona resultado de uma execução."""
        self.runs.append(metrics)
    
    def get_statistics(self) -> Dict[str, float]:
        """Calcula estatísticas das execuções."""
        if not self.runs:
            return {}
        
        times = [r['time_seconds'] for r in self.runs]
        memories = [r['peak_memory_mb'] for r in self.runs]
        
        return {
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'avg_memory': sum(memories) / len(memories),
            'min_memory': min(memories),
            'max_memory': max(memories),
            'n_runs': len(times)
        }
    
    def print_summary(self, algorithm_name: str = ""):
        """Imprime resumo das estatísticas."""
        stats = self.get_statistics()
        if not stats:
            print("Nenhuma execução registrada.")
            return
        
        print(f"\n{'='*60}")
        if algorithm_name:
            print(f"Resumo: {algorithm_name}")
        print(f"{'='*60}")
        print(f"Execuções: {stats['n_runs']}")
        print(f"\nTempo:")
        print(f"  Média:  {format_time(stats['avg_time'])}")
        print(f"  Mínimo: {format_time(stats['min_time'])}")
        print(f"  Máximo: {format_time(stats['max_time'])}")
        print(f"\nMemória (pico):")
        print(f"  Média:  {format_memory(stats['avg_memory'])}")
        print(f"  Mínimo: {format_memory(stats['min_memory'])}")
        print(f"  Máximo: {format_memory(stats['max_memory'])}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Teste de medição
    import random
    
    def exemplo_funcao(n):
        """Função de teste que consome tempo e memória."""
        dados = [random.random() for _ in range(n)]
        dados.sort()
        return sum(dados)
    
    print("Testando medição de desempenho...")
    
    tracker = PerformanceTracker()
    
    for i in range(5):
        metrics = measure_performance(exemplo_funcao, 100000)
        tracker.add_run(metrics)
        print(f"Run {i+1}: {format_time(metrics['time_seconds'])}, "
              f"{format_memory(metrics['peak_memory_mb'])}")
    
    tracker.print_summary("Função de Exemplo")