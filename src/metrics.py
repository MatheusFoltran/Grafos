import time
import tracemalloc
from typing import Callable, Any, Dict

try:
    import psutil
    _HAS_PSUTIL = True
except Exception:
    psutil = None
    _HAS_PSUTIL = False


def medir_desempenho(funcao: Callable, *argumentos, **kwargs_dict) -> Dict[str, Any]:
    # pegar RSS antes (se tiver psutil)
    rss_antes = None
    if _HAS_PSUTIL:
        try:
            processo = psutil.Process()
            rss_antes = processo.memory_info().rss
        except Exception:
            rss_antes = None

    tracemalloc.start()

    tempo_inicio = time.perf_counter()
    cpu_inicio = time.process_time()
    resultado = funcao(*argumentos, **kwargs_dict)
    cpu_fim = time.process_time()
    tempo_fim = time.perf_counter()

    atual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # pegar RSS depois
    rss_depois = None
    if _HAS_PSUTIL:
        try:
            rss_depois = processo.memory_info().rss
        except Exception:
            rss_depois = None

    saida = {
        'result': resultado,
        'time_seconds': tempo_fim - tempo_inicio,
        'cpu_seconds': cpu_fim - cpu_inicio,
        'memory_mb': atual / (1024 * 1024),
        'peak_memory_mb': pico / (1024 * 1024)
    }

    if rss_antes is not None:
        saida['mem_rss_before_mb'] = rss_antes / (1024 * 1024)
    if rss_depois is not None:
        saida['mem_rss_mb'] = rss_depois / (1024 * 1024)

    return saida


def formatar_tempo(segundos: float) -> str:
    if segundos < 0.001:
        return f"{segundos * 1_000_000:.2f} μs"
    elif segundos < 1:
        return f"{segundos * 1_000:.2f} ms"
    else:
        return f"{segundos:.2f} s"


def formatar_memoria(megabytes: float) -> str:
    if megabytes < 1:
        return f"{megabytes * 1024:.2f} KB"
    elif megabytes < 1024:
        return f"{megabytes:.2f} MB"
    else:
        return f"{megabytes / 1024:.2f} GB"


class RastreadorDesempenho:
    def __init__(self):
        self.execucoes = []
    
    def adicionar_execucao(self, metricas: Dict[str, Any]):
        self.execucoes.append(metricas)
    
    def obter_estatisticas(self) -> Dict[str, float]:
        if not self.execucoes:
            return {}
        
        tempos = [r['time_seconds'] for r in self.execucoes]
        memorias = [r['peak_memory_mb'] for r in self.execucoes]
        
        return {
            'avg_time': sum(tempos) / len(tempos),
            'min_time': min(tempos),
            'max_time': max(tempos),
            'avg_memory': sum(memorias) / len(memorias),
            'min_memory': min(memorias),
            'max_memory': max(memorias),
            'n_runs': len(tempos)
        }
    
    def imprimir_resumo(self, nome_algoritmo: str = ""):
        estatisticas = self.obter_estatisticas()
        if not estatisticas:
            print("Nenhuma execução registrada.")
            return
        
        if nome_algoritmo:
            print(f"Resumo: {nome_algoritmo}")
        print(f"{'='*60}")
        print(f"Execuções: {estatisticas['n_runs']}")
        print(f"\nTempo:")
        print(f"  Média:  {formatar_tempo(estatisticas['avg_time'])}")
        print(f"  Mínimo: {formatar_tempo(estatisticas['min_time'])}")
        print(f"  Máximo: {formatar_tempo(estatisticas['max_time'])}")
        print(f"\nMemória (pico):")
        print(f"  Média:  {formatar_memoria(estatisticas['avg_memory'])}")
        print(f"  Mínimo: {formatar_memoria(estatisticas['min_memory'])}")
        print(f"  Máximo: {formatar_memoria(estatisticas['max_memory'])}")