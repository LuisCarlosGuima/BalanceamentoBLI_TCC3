# Arquivo: run_experiments.py (CORRIGIDO)
import time
import statistics
import csv
import os
import carregar_containers_csv
import heuristica_distribuicao
from carregar_vessel import load_vessel_profile

# --- PARÂMETROS CONFIGURÁVEIS DO EXPERIMENTO ---
PARAM_MAX_ITER = [20]
PARAM_PERTURB_SIZE = [2]
NUM_REPETICOES = 5
INSTANCIAS = ['VSLow1', 'VSMed1', 'VSHigh1']
BASE_PATH = './'
VESSEL_PROFILE = f'{BASE_PATH}bases/navio/vessel_s.txt'
OUTPUT_CSV = 'results.csv'

def calcular_metricas(solucao_final, vessel_profile):
    if not solucao_final.allocated: return 0.0, 0.0, 0.0
    total_peso = sum(c.peso for c in solucao_final.allocated)
    if total_peso == 0: return 0.0, 0.0, 0.0
    m_long = sum(c.peso * (c.position[0] / (vessel_profile.num_baias - 1)) for c in solucao_final.allocated)
    m_trans = sum(c.peso * (c.position[1] / (vessel_profile.num_pilhas - 1)) for c in solucao_final.allocated)
    cg_long_norm = m_long / total_peso
    cg_trans_norm = m_trans / total_peso
    pesos_por_pilha = {}
    for c in solucao_final.allocated:
        pilha_id = (c.position[0], c.position[1])
        pesos_por_pilha[pilha_id] = pesos_por_pilha.get(pilha_id, 0) + c.peso
    lista_de_pesos = list(pesos_por_pilha.values())
    desvio_padrao = statistics.stdev(lista_de_pesos) if len(lista_de_pesos) > 1 else 0.0
    return cg_long_norm, cg_trans_norm, desvio_padrao

def run_all_experiments():
    print(">>> INICIANDO EXECUÇÃO DE TODOS OS EXPERIMENTOS <<<")
    write_header = not os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                'instancia', 'max_iter', 'perturb_size', 'repeticao',
                'tempo_s', 'taxa_ocupacao', 'containers_alocados',  # <-- COLUNA ADICIONADA
                'cg_long', 'cg_trans', 'desvio_peso'
            ])
        vessel = load_vessel_profile(VESSEL_PROFILE)
        for instancia_nome in INSTANCIAS:
            for max_iter in PARAM_MAX_ITER:
                for perturb_size in PARAM_PERTURB_SIZE:
                    print(f"\nRodando: {instancia_nome} | max_iter={max_iter} | perturb_size={perturb_size}")
                    for i in range(1, NUM_REPETICOES + 1):
                        print(f"  Repetição {i}/{NUM_REPETICOES}...")
                        path_instancia = f"{BASE_PATH}bases/container/vessel_s/{instancia_nome}.csv"
                        containers_a_alocar = carregar_containers_csv.carregar_containers_csv(path_instancia)
                        total_de_containers = len(containers_a_alocar)
                        navio = heuristica_distribuicao.Navio(vessel)
                        start_time = time.perf_counter()
                        solucao_final = heuristica_distribuicao.heuristica_distribuicao(
                            containers_a_alocar, navio, max_iter, perturb_size
                        )
                        duracao = time.perf_counter() - start_time
                        alocados = len(solucao_final.allocated)
                        taxa_ocupacao = (alocados / total_de_containers) * 100 if total_de_containers > 0 else 0
                        cg_long, cg_trans, desvio = calcular_metricas(solucao_final, vessel)
                        writer.writerow([
                            instancia_nome, max_iter, perturb_size, i,
                            round(duracao, 4), round(taxa_ocupacao, 2),
                            alocados,  # <-- VALOR ADICIONADO
                            round(cg_long, 4), round(cg_trans, 4), round(desvio, 2)
                        ])
    print("\n>>> EXPERIMENTOS FINALIZADOS! Resultados salvos em 'results.csv' <<<")

if __name__ == '__main__':
    run_all_experiments()