import pandas as pd
from typing import List, Tuple


def gerar_quadro_respawn(respawn: str, hunts: List[Tuple]) -> pd.DataFrame:
    """
    Gera um DataFrame formatado com as hunts de um respawn específico.
    
    Args:
        respawn: Nome do respawn
        hunts: Lista de tuplas com dados das hunts (id, respawn, horario_inicio, 
               horario_fim, integrante1, ..., integrante5, data_cadastro)
    
    Returns:
        DataFrame com colunas: Horário Início | Horário Fim | Integrantes
    """
    if not hunts:
        return pd.DataFrame(columns=["Horário Início", "Horário Fim", "Integrantes"])
    
    dados = []
    for hunt in hunts:
        # hunt = (id, respawn, horario_inicio, horario_fim, integrante1, ..., integrante5, data_cadastro)
        horario_inicio = hunt[2]
        horario_fim = hunt[3]
        
        # Coletar integrantes não vazios
        integrantes = []
        for i in range(4, 9):  # índices 4 a 8 são integrante1 a integrante5
            if hunt[i] and hunt[i].strip():
                integrantes.append(hunt[i].strip())
        
        integrantes_str = ", ".join(integrantes) if integrantes else "-"
        
        dados.append({
            "Horário Início": horario_inicio,
            "Horário Fim": horario_fim,
            "Integrantes": integrantes_str
        })
    
    df = pd.DataFrame(dados)
    
    # Ordenar por horário de início
    df = df.sort_values("Horário Início").reset_index(drop=True)
    
    return df


def agrupar_hunts_por_respawn(hunts: List[Tuple]) -> dict:
    """
    Agrupa hunts por respawn.
    
    Args:
        hunts: Lista de todas as hunts
    
    Returns:
        Dicionário {respawn: [lista_de_hunts]}
    """
    agrupadas = {}
    
    for hunt in hunts:
        respawn = hunt[1]  # índice 1 é o respawn
        if respawn not in agrupadas:
            agrupadas[respawn] = []
        agrupadas[respawn].append(hunt)
    
    return agrupadas
