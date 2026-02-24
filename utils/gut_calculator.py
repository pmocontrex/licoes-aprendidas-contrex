def calcular_gut(gravidade: int, urgencia: int, tendencia: int) -> dict:
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
    desc = {1: "Sem gravidade", 2: "Pouco grave", 3: "Grave", 4: "Muito grave", 5: "Extremamente grave"}
    return desc.get(nivel, "")

def get_descricao_urgencia(nivel: int) -> str:
    desc = {1: "Pode esperar", 2: "Pouco urgente", 3: "Urgente", 4: "Muito urgente", 5: "Urgentíssimo"}
    return desc.get(nivel, "")

def get_descricao_tendencia(nivel: int) -> str:
    desc = {1: "Estável", 2: "Piora a longo prazo", 3: "Piora a médio prazo", 4: "Piora a curto prazo", 5: "Piora imediata"}
    return desc.get(nivel, "")
