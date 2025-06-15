import time
import statistics
import carregar_containers_csv
import heuristica_distribuicao
from carregar_vessel import load_vessel_profile

# Parâmetros da heurística BLI (ILS), conforme artigo 2.4.2
MAX_ITER = 20
PERTURB_SIZE = 2

# --- Configuração dos Testes ---
# Ajuste o caminho base se a sua estrutura de pastas for diferente
BASE_PATH = './' 
INSTANCIAS = ['VSLow1', 'VSMed1', 'VSHigh1']
VESSEL_PROFILE = f'{BASE_PATH}bases/navio/vessel_s.txt'

def calcular_metricas(solucao_final, vessel_profile):
    """
    Calcula as métricas de qualidade da solução final.
    - solucao_final: O objeto Navio retornado pela heurística.
    - vessel_profile: O objeto com os dados do perfil do navio (dimensões, etc.).
    """
    if not solucao_final.allocated:
        return 0.0, 0.0, 0.0

    total_peso = sum(c.peso for c in solucao_final.allocated)
    if total_peso == 0:
        return 0.0, 0.0, 0.0

    # Calcula o Centro de Gravidade (CG) Normalizado
    # A posição do contêiner é uma tupla (baia, fileira, nível)
    # Normalizamos dividindo pela dimensão correspondente - 1 para obter um valor entre 0 e 1.
    m_long = sum(c.peso * (c.position[0] / (vessel_profile.num_baias - 1)) for c in solucao_final.allocated)
    m_trans = sum(c.peso * (c.position[1] / (vessel_profile.num_pilhas - 1)) for c in solucao_final.allocated)

    cg_long_norm = m_long / total_peso
    cg_trans_norm = m_trans / total_peso

    # Calcula o Desvio Padrão do Peso entre as Pilhas
    pesos_por_pilha = {}
    for c in solucao_final.allocated:
        # A identidade da pilha é sua coordenada (baia, fileira)
        pilha_id = (c.position[0], c.position[1])
        pesos_por_pilha[pilha_id] = pesos_por_pilha.get(pilha_id, 0) + c.peso

    lista_de_pesos = list(pesos_por_pilha.values())
    desvio_padrao = statistics.stdev(lista_de_pesos) if len(lista_de_pesos) > 1 else 0.0

    return cg_long_norm, cg_trans_norm, desvio_padrao


def main():
    print("Iniciando a execução dos experimentos...")
    vessel = load_vessel_profile(VESSEL_PROFILE)
    resultados_finais = []

    for inst_nome in INSTANCIAS:
        print(f"\n--- Processando instância: {inst_nome} ---")
        
        # Carrega a lista de contêineres para a instância atual
        path_instancia = f"{BASE_PATH}bases/container/vessel_s/{inst_nome}.csv"
        containers_a_alocar = carregar_containers_csv.carregar_containers_csv(path_instancia)
        total_de_containers = len(containers_a_alocar)

        # Cria um objeto Navio vazio para a execução
        navio = heuristica_distribuicao.Navio(vessel)

        # Executa a sua heurística
        start_time = time.perf_counter()
        # Assumindo que sua função retorna o objeto Navio com a solução final
        solucao_final = heuristica_distribuicao.heuristica_distribuicao(
            containers_a_alocar, navio, MAX_ITER, PERTURB_SIZE
        )
        end_time = time.perf_counter()
        duracao = end_time - start_time

        # Coleta e calcula as métricas da solução encontrada
        alocados = len(solucao_final.allocated)
        taxa_ocupacao = (alocados / total_de_containers) * 100 if total_de_containers > 0 else 0
        cg_long, cg_trans, desvio = calcular_metricas(solucao_final, vessel)

        # Armazena os resultados em um dicionário
        resultados_finais.append({
            'Instância': inst_nome,
            'Contêineres Alocados': f"{alocados}/{total_de_containers}",
            'Taxa de Ocupação (%)': round(taxa_ocupacao, 2),
            'Tempo (s)': round(duracao, 2),
            'CG Long. (Norm)': round(cg_long, 4),
            'CG Trans. (Norm)': round(cg_trans, 4),
            'Desvio Padrão Peso (t)': round(desvio, 2)
        })

    # Imprime a tabela de resultados final em formato Markdown
    print("\n\n" + "="*60)
    print("### TABELA DE RESULTADOS PARA O ARTIGO ###")
    print("="*60)

    headers = list(resultados_finais[0].keys())
    print('| ' + ' | '.join(headers) + ' |')
    print('|' + '---:|' * len(headers))
    for row in resultados_finais:
        print('| ' + ' | '.join(str(row[h]) for h in headers) + ' |')

if __name__ == '__main__':
    main()