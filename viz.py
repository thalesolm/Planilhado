import pandas as pd
from typing import List, Optional, Tuple

# 0=Dom, 1=Seg, 2=Ter, 3=Qua, 4=Qui, 5=Sex, 6=Sab
NOMES_DIAS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]


def formatar_dias_semana(dias_semana_str: Optional[str]) -> str:
    """
    Converte a string salva (ex: '1,2,3,4,5') em texto legível (ex: 'Seg - Sex').
    Retorna '-' se vazio ou inválido.
    """
    if not dias_semana_str or not dias_semana_str.strip():
        return "-"
    try:
        nums = sorted([int(x.strip()) for x in dias_semana_str.split(",") if x.strip()])
    except (ValueError, AttributeError):
        return "-"
    if not nums:
        return "-"
    # Atalhos conhecidos
    if nums == [0, 1, 2, 3, 4, 5, 6]:
        return "Semana toda"
    if nums == [1, 2, 3, 4, 5]:
        return "Seg - Sex"
    if nums == [0, 6]:
        return "Sab - Dom"
    # Exibir dias selecionados
    return ", ".join(NOMES_DIAS[i] for i in nums if 0 <= i <= 6)


def gerar_quadro_respawn(respawn: str, hunts: List[Tuple]) -> pd.DataFrame:
    """
    Gera um DataFrame formatado com as hunts de um respawn específico.
    """
    if not hunts:
        return pd.DataFrame(columns=["Horário Início", "Horário Fim", "Dias", "Integrantes"])

    dados = []
    for hunt in hunts:
        horario_inicio = hunt[2]
        horario_fim = hunt[3]
        integrantes = []
        for i in range(4, 9):
            if hunt[i] and hunt[i].strip():
                integrantes.append(hunt[i].strip())
        integrantes_str = ", ".join(integrantes) if integrantes else "-"
        dias_semana = hunt[9] if len(hunt) > 9 else None
        dados.append({
            "Horário Início": horario_inicio,
            "Horário Fim": horario_fim,
            "Dias": formatar_dias_semana(dias_semana),
            "Integrantes": integrantes_str
        })

    df = pd.DataFrame(dados)
    df = df.sort_values("Horário Início").reset_index(drop=True)
    return df


def agrupar_hunts_por_respawn(hunts: List[Tuple]) -> dict:
    """Agrupa hunts por respawn."""
    agrupadas = {}
    for hunt in hunts:
        respawn = hunt[1]
        if respawn not in agrupadas:
            agrupadas[respawn] = []
        agrupadas[respawn].append(hunt)
    return agrupadas
