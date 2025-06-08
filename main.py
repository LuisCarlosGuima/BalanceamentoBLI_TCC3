import time
import statistics
from carregar_containers_csv import carregar_containers_csv
from heuristica_distribuicao import Navio, heuristica_distribuicao
from carregar_vessel import load_vessel_profile

# Parâmetros BLI (ILS) conforme artigo 2.4.2
MAX_ITER = 20  # mesmo número de iterações do artigo
PERTURB = 2    # mesma intensidade de perturbação

# Instâncias do artigo Larsen (CSV convertido)
BASE_CSV = 'bases/container/vessel_s'
INSTANCIAS = [
    'VSLow1',
    # Adicione as demais instâncias conforme o artigo
]

# Função utilitária para calcular CG normalizado e desvio peso por pilha
def calcular_metricas(navio, vessel):
    total_peso = sum(c.peso for c in navio.allocated)
    # Momentos normalizados
    m_long = sum(c.peso * (c.position[0] / (vessel.num_baias - 1)) for c in navio.allocated)
    m_trans = sum(c.peso * (c.position[1] / (vessel.num_pilhas - 1)) for c in navio.allocated)
    # CG normalizado
    cg_long_norm = m_long / total_peso
    cg_trans_norm = m_trans / total_peso
    # Pesos por pilha
    pesos = [sum(c.peso for c in navio.allocated if c.position == pos)
             for pos in navio.positions]
    desvio = statistics.stdev(pesos) if len(pesos) > 1 else 0.0
    return cg_long_norm, cg_trans_norm, desvio


def main():
    vessel = load_vessel_profile('bases/navio/vessel_s.txt')
    resultados = []

    for inst in INSTANCIAS:
        # Carrega containers
        containers = carregar_containers_csv(f"{BASE_CSV}/{inst}.csv")

        # Executa BLI (ILS)
        navio = Navio(vessel)
        start = time.perf_counter()
        best = heuristica_distribuicao(containers, navio, MAX_ITER, PERTURB)
        dur = time.perf_counter() - start

        # Métricas próprias
        alocados = len(best.allocated)
        cg_long, cg_trans, desvio = calcular_metricas(best, vessel)

        resultados.append({
            'Instância': inst,
            'Alocados': alocados,
            'Tempo(s)': round(dur, 2),
            'CG_Long_Norm': round(cg_long, 3),
            'CG_Trans_Norm': round(cg_trans, 3),
            'Desvio_Peso_Pilha': round(desvio, 2)
        })

    # Impressão de tabela comparativa em Markdown
    header = ['Instância', 'Alocados', 'Tempo(s)', 'CG_Long_Norm', 'CG_Trans_Norm', 'Desvio_Peso_Pilha']
    print('| ' + ' | '.join(header) + ' |')
    print('|' + '----|' * len(header))
    for r in resultados:
        print('| ' + ' | '.join(str(r[h]) for h in header) + ' |')

if __name__ == '__main__':
    main()
