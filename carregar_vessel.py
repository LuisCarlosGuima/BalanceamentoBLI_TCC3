import csv
import os

class VesselProfile:
    def __init__(
        self,
        num_baias,
        num_pilhas,
        altura_max,
        capacidade_20ft,
        capacidade_40ft,
        peso_max_pilha,
        limite_grav_long,
        limite_grav_trans,
        hydrostatic=None
    ):
        self.num_baias = int(num_baias)
        self.num_pilhas = int(num_pilhas)
        self.altura_max = int(altura_max)
        self.capacidade_celula = {
            '20ft': int(capacidade_20ft),
            '40ft': int(capacidade_40ft)
        }
        self.peso_max_pilha = int(peso_max_pilha)
        self.limite_grav_long = float(limite_grav_long)
        self.limite_grav_trans = float(limite_grav_trans)
        self.hydrostatic = hydrostatic or []


def load_vessel_profile(path):
    """
    Carrega perfil de navio de CSV ou TXT (VSLow format).
    Se ext == .csv, carrega colunas pré-definidas.
    Se ext == .txt ou .dat, busca dados iniciais e HydroPoints.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        return _load_vessel_csv(path)
    elif ext in ('.txt', '.dat'):
        return _load_vessel_txt(path)
    else:
        raise ValueError(f"Formato de perfil de navio não suportado: {ext}")


def _load_vessel_csv(path):
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        return VesselProfile(
            num_baias=row['num_baias'],
            num_pilhas=row['num_pilhas'],
            altura_max=row['altura_max'],
            capacidade_20ft=row['capacidade_20ft'],
            capacidade_40ft=row['capacidade_40ft'],
            peso_max_pilha=row['peso_max_pilha'],
            limite_grav_long=row['limite_grav_long'],
            limite_grav_trans=row['limite_grav_trans'],
            hydrostatic=None
        )


def _load_vessel_txt(path):
    hydro = []
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    # encontrar primeira linha não comentário com 4 valores numéricos
    first = None
    for line in lines:
        if line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 4 and all(p.replace('.', '', 1).isdigit() for p in parts[:4]):
            first = parts
            break
    if first is None:
        raise ValueError("Linha de perfil não encontrada no arquivo TXT")
    num_baias, num_pilhas, tiers, tolerance = first[:4]
    # buscar seção HydroPoints
    for i, l in enumerate(lines):
        if l.startswith('## HydroPoints'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('##'):
                parts = lines[j].split()
                if len(parts) >= 4:
                    disp, min_lcg, max_lcg, meta = parts[:4]
                    hydro.append({
                        'displacement': float(disp),
                        'min_lcg': float(min_lcg),
                        'max_lcg': float(max_lcg),
                        'metacenter': float(meta)
                    })
                j += 1
            break
    cap20 = tiers   # ou um valor bem grande: num_baias * num_pilhas
    cap40 = tiers   # idem
    return VesselProfile(
        num_baias=num_baias,
        num_pilhas=num_pilhas,
        altura_max=tiers,
        capacidade_20ft=cap20,
        capacidade_40ft=cap40,
        peso_max_pilha=999999,
        limite_grav_long=tolerance,
        limite_grav_trans=tolerance,
        hydrostatic=hydro
    )