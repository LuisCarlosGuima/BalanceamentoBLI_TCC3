import csv
import random
import re
import os
import glob

# Parâmetros de variação (±10% do peso nominal)
VARIACAO = 0.1

# Diretório raiz onde estão as pastas Vessel_S, Vessel_M e Vessel_L
BASE_DIR = 'bases/containerEmTxt'
PASTAS = ['Vessel_S', 'Vessel_M', 'Vessel_L']

def parse_transport_types(lines):
    types = {}
    for ln in lines:
        ln = ln.strip()
        if ln.startswith('# Container'):
            break
        if ln.startswith('#') or not ln:
            continue
        parts = ln.split()
        if len(parts) == 4 and re.match(r'^\d+$', parts[0]):
            tid, length, weight, _ = parts
            types[int(tid)] = (int(length), int(weight))
    return types

def parse_containers(lines, transport_types):
    containers = []
    in_block = False
    cid = 0
    for ln in lines:
        ln = ln.strip()
        if ln.startswith('# Container'):
            in_block = True
            continue
        if not in_block:
            continue
        if ln.startswith('#') or not ln:
            break
        parts = ln.split()
        if len(parts) < 3:
            continue
        _, _, tid, *_ = parts
        tid = int(tid)
        if tid not in transport_types:
            continue
        length, nominal = transport_types[tid]
        peso = int(random.uniform(nominal * (1 - VARIACAO), nominal * (1 + VARIACAO)))
        containers.append({
            'id': cid,
            'tipo': f'{length}ft',
            'peso': peso
        })
        cid += 1
    return containers

def processar_arquivo(caminho_arquivo, caminho_saida_csv):
    with open(caminho_arquivo, 'r') as f:
        lines = f.readlines()

    transport_types = parse_transport_types(lines)
    containers = parse_containers(lines, transport_types)

    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(caminho_saida_csv), exist_ok=True)

    # Escreve o CSV
    with open(caminho_saida_csv, 'w', newline='') as csvfile:
        fieldnames = ['id', 'tipo', 'peso']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for c in containers:
            writer.writerow(c)

    print(f'[{caminho_arquivo}] → Gerado {len(containers)} contêineres em "{caminho_saida_csv}".')

def main():
    for pasta in PASTAS:
        caminho_pasta = os.path.join(BASE_DIR, pasta)
        arquivos_txt = glob.glob(os.path.join(caminho_pasta, '*.txt'))
        for arquivo in arquivos_txt:
            nome_base = os.path.splitext(os.path.basename(arquivo))[0]
            caminho_saida = os.path.join('containers_csv', pasta, f'{nome_base}.csv')
            processar_arquivo(arquivo, caminho_saida)

if __name__ == '__main__':
    main()
