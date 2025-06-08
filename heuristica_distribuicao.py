import random
from carregar_vessel import VesselProfile

class Container:
    def __init__(self, cid, tipo, peso):
        self.id = cid
        self.tipo = tipo
        self.peso = peso


from carregar_vessel import VesselProfile

class Navio:
    def __init__(self, vessel_profile: VesselProfile):
        # armazena profile para clones
        self._vessel_profile = vessel_profile
        # parâmetros do navio
        self.num_baias = vessel_profile.num_baias
        self.num_pilhas = vessel_profile.num_pilhas
        self.altura_max = vessel_profile.altura_max
        self.capacidade_celula = vessel_profile.capacidade_celula
        self.peso_max_pilha = vessel_profile.peso_max_pilha
        self.limite_grav_long = vessel_profile.limite_grav_long
        self.limite_grav_trans = vessel_profile.limite_grav_trans
        # estado da alocação
        self.allocated = []        # lista de objetos Container
        self.positions = {}        # mapa (x,y) -> ocupação

    def adicionar_container(self, container, x, y):
        """Compatibilidade com greedy_allocation"""
        return self.alocar(container, x, y)

    def alocar(self, container, x, y):
        """Registra container no navio"""
        container.position = (x, y)
        self.allocated.append(container)
        self.positions[(x, y)] = self.positions.get((x, y), 0) + 1

    def verificar_restricoes(self, container, x, y):
        """
        Checa:
        1) altura máxima por pilha,
        2) peso máximo por pilha,
        3) CG normalizado após adicionar o container dentro da tolerância.
        """
        # 1) Altura
        ocup = self.positions.get((x, y), 0)
        if ocup >= self.altura_max:
            return False

        # 2) Peso por pilha
        peso_pilha = sum(c.peso for c in self.allocated if c.position == (x, y))
        if peso_pilha + container.peso > self.peso_max_pilha:
            return False

        # prepara dados atuais
        total_peso = sum(c.peso for c in self.allocated)
        total_m_long = sum(c.peso * (c.position[0] / (self.num_baias - 1))
                        for c in self.allocated)
        total_m_trans = sum(c.peso * (c.position[1] / (self.num_pilhas - 1))
                            for c in self.allocated)

        # valores normalizados da posição candidata
        x_norm = x / (self.num_baias - 1)
        y_norm = y / (self.num_pilhas - 1)

        # momento atualizado ao adicionar este container
        new_peso = total_peso + container.peso
        new_m_long = total_m_long + container.peso * x_norm
        new_m_trans = total_m_trans + container.peso * y_norm

        # 3) CG normalizado e comparação com tolerância
        cg_long_norm = new_m_long / new_peso   # fração [0,1] ao longo do navio
        cg_trans_norm = new_m_trans / new_peso # fração [0,1] na largura

        tol = self.limite_grav_long  # igual a limite_grav_long em VesselProfile

        # aceitável se dentro de ±tol em relação ao centro (0.5)
        if not (0.5 - tol <= cg_long_norm <= 0.5 + tol):
            return False
        if not (0.5 - tol <= cg_trans_norm <= 0.5 + tol):
            return False

        return True


    def clone(self):
        """Retorna uma cópia profunda da solução (Navio)."""
        novo = Navio(self._vessel_profile)
        # reproduz todas as alocações no clone
        for c in self.allocated:
            x, y = c.position
            novo.alocar(c, x, y)
        return novo
    
    
    def _remove(self, container):
        """Remove um container de allocated e atualiza positions."""
        self.allocated.remove(container)
        x, y = container.position
        # atualiza contador de posição
        if self.positions.get((x, y), 0) > 1:
            self.positions[(x, y)] -= 1
        else:
            del self.positions[(x, y)]
# ILS: solução inicial, perturbação e busca local

def evaluate(navio):
    return len(navio.allocated)


def greedy_allocation(containers, navio):
    """
    Aloca cada container **uma única vez** num único porto,
    tentando as posições em ordem aleatória.
    """
    # lista de todas as posições possíveis (x=baia, y=pilha)
    positions = [(x, y)
                 for x in range(navio.num_baias)
                 for y in range(navio.num_pilhas)]

    for idx, c in enumerate(containers):
        # computa só as posições que passam nas restrições
        valid = [(x, y) for (x, y) in positions
                      if navio.verificar_restricoes(c, x, y)]

        # DEBUG: para o primeiro container, imprime as posições válidas
        if idx == 0:
            print(f"[DEBUG] Posições válidas para c0: {valid}")

        # embaralha para não privilegiar sempre a mesma baia
        random.shuffle(valid)

        # aloca na primeira posição válida (se houver)
        if valid:
            x, y = valid[0]
            navio.alocar(c, x, y)
        # se não tiver posição válida, simplesmente pula este container

    return navio


def perturb(navio, perturb_size):
    """
    Remove até `perturb_size` containers aleatoriamente e realoca-os
    (usando sempre navio.alocar), sem duplicar objetos.
    """
    k = min(perturb_size, len(navio.allocated))
    if k == 0:
        return navio

    indices = random.sample(range(len(navio.allocated)), k)
    removed = []

    # remove containers (do topo para baixo) e atualiza positions
    for idx in sorted(indices, reverse=True):
        c = navio.allocated.pop(idx)
        x, y = c.position

        cnt = navio.positions.get((x, y), 0)
        if cnt > 1:
            navio.positions[(x, y)] = cnt - 1
        else:
            del navio.positions[(x, y)]

        removed.append(c)

    # tenta realocar cada um
    for c in removed:
        positions = [(x, y)
                     for x in range(navio.num_baias)
                     for y in range(navio.num_pilhas)]
        random.shuffle(positions)
        for x, y in positions:
            if navio.verificar_restricoes(c, x, y):
                navio.alocar(c, x, y)
                break

    return navio




def local_search(navio, max_no_improve=50):
    """
    Busca local por swap: tenta trocar dois containers de lugar
    e aceita apenas se houver melhoria.
    """
    best = navio.clone()
    best_score = evaluate(best)
    no_improve = 0

    while no_improve < max_no_improve and len(best.allocated) >= 2:
        cand = best.clone()
        i1, i2 = random.sample(range(len(cand.allocated)), 2)
        c1, c2 = cand.allocated[i1], cand.allocated[i2]
        x1, y1 = c1.position
        x2, y2 = c2.position

        # remove antes de trocar
        cand._remove(c1)
        cand._remove(c2)

        # tenta trocar se ambas posições ainda forem válidas
        if (cand.verificar_restricoes(c1, x2, y2) and
            cand.verificar_restricoes(c2, x1, y1)):
            cand.alocar(c1, x2, y2)
            cand.alocar(c2, x1, y1)
        else:
            # volta ao original se não for possível
            cand.alocar(c1, x1, y1)
            cand.alocar(c2, x2, y2)

        score = evaluate(cand)
        if score > best_score:
            best, best_score, no_improve = cand, score, 0
        else:
            no_improve += 1

    return best



def heuristica_distribuicao(containers, navio, max_iter=100, perturb_size=2):
    """
    Heurística baseada em ILS:
    1. Alocação inicial gulosa
    2. Iterated Local Search com perturbações e busca local
    """
    # etapa 1: alocação inicial gulosa
    greedy_allocation(containers, navio)
    # clona solução inicial
    best = navio.clone()
    best_score = evaluate(best)

    # etapa 2: loop de ILS
    for _ in range(max_iter):
        # cópia e perturbação
        cand = best.clone()
        cand = perturb(cand, perturb_size)
        # busca local
        cand = local_search(cand)
        cand_score = evaluate(cand)
        # aceita melhor
        if cand_score > best_score:
            best = cand
            best_score = cand_score

    return best