# utils/gut_calculator.py

def calcular_gut(gravidade: int, urgencia: int, tendencia: int) -> dict:
    """
    Calcula o resultado GUT e retorna um dicionário com resultado, nível, cor e label.
    """
    resultado = gravidade * urgencia * tendencia
    if resultado <= 25:
        nivel = "baixo"
        cor = "🟢"
        label = "Baixo"
    elif resultado <= 74:
        nivel = "medio"
        cor = "🟡"
        label = "Médio"
    else:
        nivel = "alto"
        cor = "🔴"
        label = "Alto"
    return {
        "resultado": resultado,
        "nivel": nivel,
        "cor": cor,
        "label": label
    }

def get_descricao_gravidade(nivel: int) -> str:
    descricoes = {
        1: "Sem gravidade: sem impacto nos resultados.",
        2: "Pouco grave: impacta minimamente, facilmente reversível.",
        3: "Grave: impacta moderadamente, exige atenção.",
        4: "Muito grave: grandes prejuízos, difícil reversão.",
        5: "Extremamente grave: danos irreparáveis, catástrofe."
    }
    return descricoes.get(nivel, "")

def get_descricao_urgencia(nivel: int) -> str:
    descricoes = {
        1: "Pode esperar: não há pressa para resolver.",
        2: "Pouco urgente: pode aguardar um pouco.",
        3: "Urgente: deve ser resolvido o mais breve possível.",
        4: "Muito urgente: requer ação rápida.",
        5: "Urgentíssimo e inadiável: ação imediata necessária."
    }
    return descricoes.get(nivel, "")

def get_descricao_tendencia(nivel: int) -> str:
    descricoes = {
        1: "Manterá estabilidade: não irá piorar.",
        2: "Piora a longo prazo: pode piorar se nada for feito.",
        3: "Piora a médio prazo: tendência de agravamento.",
        4: "Piora a curto prazo: agravamento rápido.",
        5: "Piora imediata: vai piorar drasticamente se não agir agora."
    }
    return descricoes.get(nivel, "")
