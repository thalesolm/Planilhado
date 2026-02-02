import pandas as pd
from typing import List, Tuple


def gerar_quadro_respawn(respawn: str, hunts: List[Tuple]) -> pd.DataFrame:
    """
    Gera um DataFrame formatado com as hunts de um respawn específico.
    """
    if not hunts:
        return pd.DataFrame(columns=["Horário Início", "Horário Fim", "Integrantes"])

    dados = []
    for hunt in hunts:
        horario_inicio = hunt[2]
        horario_fim = hunt[3]
        integrantes = []
        for i in range(4, 9):
            if hunt[i] and hunt[i].strip():
                integrantes.append(hunt[i].strip())
        integrantes_str = ", ".join(integrantes) if integrantes else "-"
        dados.append({
            "Horário Início": horario_inicio,
            "Horário Fim": horario_fim,
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
