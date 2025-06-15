# Arquivo: analyze_results.py (CORRIGIDO)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

INPUT_CSV = 'results.csv'
OUTPUT_DIR = 'graficos'

def analyze_and_plot_combined():
    print(f">>> Lendo resultados de '{INPUT_CSV}' <<<")
    if not os.path.exists(INPUT_CSV):
        print(f"ERRO: Arquivo '{INPUT_CSV}' não encontrado. Execute 'run_experiments.py' primeiro.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = pd.read_csv(INPUT_CSV)

    # --- Preparação dos Dados ---
    # Agora a coluna 'containers_alocados' já é numérica
    df_grouped = df.groupby(['instancia', 'max_iter', 'perturb_size']).agg(
        tempo_medio=('tempo_s', 'mean'),
        qualidade_media=('taxa_ocupacao', 'mean'),
        containers_medios=('containers_alocados', 'mean') # <-- LENDO A COLUNA CORRETA
    ).reset_index()

    df_grouped['config_label'] = df_grouped['instancia'] + \
                               '\n(iter=' + df_grouped['max_iter'].astype(str) + \
                               ', perturb=' + df_grouped['perturb_size'].astype(str) + ')'

    print("\n--- Médias Calculadas ---")
    print(df_grouped)

    # --- Geração do Gráfico Combinado ---
    fig, ax1 = plt.subplots(figsize=(18, 10))
    sns.set_style("whitegrid")

    # Eixo Y Primário (Esquerda) - Quantidade de Contêineres
    color_bar = 'skyblue'
    ax1.set_xlabel('Configuração do Teste (Instância e Parâmetros)', fontsize=14, labelpad=15)
    ax1.set_ylabel('Quantidade Média de Contêineres Alocados', color=color_bar, fontsize=14)
    sns.barplot(data=df_grouped, x='config_label', y='containers_medios', color=color_bar, ax=ax1, label='Contêineres Alocados')
    ax1.tick_params(axis='y', labelcolor=color_bar)
    ax1.tick_params(axis='x', rotation=45, labelsize=10)

    for p in ax1.patches:
        ax1.annotate(f"{p.get_height():.0f}",
                     (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=10)

    # Eixo Y Secundário (Direita) - Tempo e Taxa de Ocupação
    ax2 = ax1.twinx()
    color_line_tempo = 'red'
    color_line_qualidade = 'green'
    ax2.set_ylabel('Tempo (s) e Taxa de Ocupação (%)', fontsize=14)
    sns.lineplot(data=df_grouped, x='config_label', y='tempo_medio', color=color_line_tempo, marker='o', sort=False, ax=ax2, label='Tempo Médio (s)')
    sns.lineplot(data=df_grouped, x='config_label', y='qualidade_media', color=color_line_qualidade, marker='X', sort=False, ax=ax2, label='Taxa de Ocupação (%)')
    ax2.tick_params(axis='y')

    # Unificar legendas
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')
    
    plt.title('Análise de Desempenho e Qualidade da Heurística BLI', fontsize=18, pad=20)
    fig.tight_layout()

    path_combinado = os.path.join(OUTPUT_DIR, 'grafico_combinado.png')
    plt.savefig(path_combinado)
    print(f"\nGráfico combinado salvo em: '{path_combinado}'")
    plt.show()

if __name__ == '__main__':
    analyze_and_plot_combined()