import csv
from heuristica_distribuicao import Container

def carregar_containers_csv(caminho_arquivo):
    """
    Lê um CSV de contêineres com colunas: id, tipo (20ft/40ft) e peso.
    Retorna lista de objetos Container.
    """
    containers = []
    with open(caminho_arquivo, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cid = int(row['id'])
            tipo = row['tipo']
            peso = int(row['peso'])
            containers.append(Container(cid, tipo, peso))
    return containers