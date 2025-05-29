import time
from carregar_containers_csv import carregar_containers_csv
from heuristica_distribuicao import Navio, heuristica_distribuicao
from carregar_vessel import load_vessel_profile
import statistics

# Perfis de execução
PROFILES = {
    'fast':    {'max_iter': 50,  'perturb': 1},
    'thorough':{'max_iter': 200, 'perturb': 3}
}

# Bases disponíveis
BASES = [
    "VLHigh2",
]

# --- Helpers adicionados no topo de main.py ---

def print_distribution_matrix(best, vessel):
    """Imprime a distribuição completa de containers por baia × pilha."""
    print("Distribuição por baia × pilha:")
    for x in range(vessel.num_baias):
        row = [best.positions.get((x, y), 0) for y in range(vessel.num_pilhas)]
        print(f"  Baia {x:02d}: {row}")
    print()

def print_cg_with_limits(best, vessel):
    """Calcula e imprime CG absoluto, normalizado e mostra os limites definidos no perfil."""
    total_peso = sum(c.peso for c in best.allocated)
    cg_long = sum(c.peso * c.position[0] for c in best.allocated) / total_peso
    cg_trans = sum(c.peso * c.position[1] for c in best.allocated) / total_peso

    # normalização em [0,1]
    cg_long_norm = cg_long / (vessel.num_baias - 1)
    cg_trans_norm = cg_trans / (vessel.num_pilhas - 1)

    # usa os limites definidos no perfil
    lim_long = vessel.limite_grav_long
    lim_trans = vessel.limite_grav_trans

    print(f"Centro de gravidade longitudinal: {cg_long:.2f}")
    print(f"  Normalizado: {cg_long_norm:.3f} (limite ±{lim_long:.3f})")
    print(f"Centro de gravidade transversal: {cg_trans:.2f}")
    print(f"  Normalizado: {cg_trans_norm:.3f} (limite ±{lim_trans:.3f})\n")


# --- Função rodar_base com as impressões atualizadas ---

def rodar_base(nome, profile_key):
    profile = PROFILES.get(profile_key)
    if profile is None:
        raise ValueError(f"Perfil desconhecido: {profile_key}")
    max_iter = profile['max_iter']
    perturb = profile['perturb']

    # marca início
    start = time.perf_counter()

    vessel = load_vessel_profile('bases/navio/vessel_l.txt')
    print("--- Perfil do navio ---")
    print(f"Baias: {vessel.num_baias}, Pilhas por baia: {vessel.num_pilhas}, Altura máxima: {vessel.altura_max}")
    print(f"Limite grav. longitudinal: {vessel.limite_grav_long}, grav. transversal: {vessel.limite_grav_trans}\n")

    containers = carregar_containers_csv(f'bases/container/vessel_l/{nome}.csv')
    print(f"Carregados {len(containers)} containers da base '{nome}'\n")

    navio = Navio(vessel)
    best = heuristica_distribuicao(containers, navio, max_iter, perturb)
    alocados = len(best.allocated)

    # marca fim
    end = time.perf_counter()
    duracao = end - start

    print("--- Resultados da Heurística ---")
    print(f"Perfil usado: {profile_key} (iter={max_iter}, perturb={perturb})")
    print(f"Containers alocados: {alocados}/{len(containers)}\n")

    # contagem por baia (0..num_baias-1)
    alocacoes_por_baia = [0] * vessel.num_baias
    for c in best.allocated:
        x, _ = c.position
        alocacoes_por_baia[x] += 1
    print(f"Alocações por baia: {alocacoes_por_baia}\n")

    # matriz completa de distribuição
    print_distribution_matrix(best, vessel)

    # cálculo e validação do centro de gravidade usando os limites existentes
    print_cg_with_limits(best, vessel)
    
    # estatísticas de peso por pilha (já tratado para >=1 ponto)
    pesos = [sum(c.peso for c in best.allocated if c.position == (x, y))
             for (x, y) in best.positions]
    if pesos:
        print("Estatísticas de peso por pilha:")
        media = statistics.mean(pesos)
        desvio = statistics.stdev(pesos) if len(pesos) > 1 else 0.0
        print(f"  Média: {media:.2f}, Desvio Padrão: {desvio:.2f}\n")

    print(f"Tempo de execução: {duracao:.2f} segundos\n")
    return best


if __name__ == '__main__':
    for base in BASES:
        for chave in PROFILES:
            rodar_base(base, chave)