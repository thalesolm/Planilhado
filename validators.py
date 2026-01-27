from typing import Optional, Tuple
from database import get_hunts_by_respawn_for_validation


def verificar_overlap(respawn: str, horario_inicio: str, horario_fim: str, 
                     exclude_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """
    Verifica se há overlap de horário para um respawn específico.
    
    Args:
        respawn: Nome do respawn
        horario_inicio: Horário de início no formato HH:MM
        horario_fim: Horário de fim no formato HH:MM
        exclude_id: ID de uma hunt a ser excluída da verificação (útil para edição)
    
    Returns:
        Tupla (tem_overlap, mensagem_erro)
        Se tem_overlap é True, mensagem_erro contém detalhes do conflito
    """
    # Buscar todas as hunts do mesmo respawn
    hunts_existentes = get_hunts_by_respawn_for_validation(respawn, exclude_id)
    
    # Converter horários para minutos para facilitar comparação
    inicio_minutos = _horario_para_minutos(horario_inicio)
    fim_minutos = _horario_para_minutos(horario_fim)
    
    # Verificar overlap com cada hunt existente
    for hunt_id, h_inicio, h_fim in hunts_existentes:
        h_inicio_min = _horario_para_minutos(h_inicio)
        h_fim_min = _horario_para_minutos(h_fim)
        
        # Dois intervalos [A1, A2] e [B1, B2] se sobrepõem se: A1 < B2 AND A2 > B1
        if inicio_minutos < h_fim_min and fim_minutos > h_inicio_min:
            mensagem = f"Conflito de horário! Já existe uma hunt cadastrada das {h_inicio} às {h_fim}."
            return True, mensagem
    
    return False, None


def _horario_para_minutos(horario: str) -> int:
    """Converte horário no formato HH:MM para minutos desde meia-noite."""
    horas, minutos = map(int, horario.split(':'))
    return horas * 60 + minutos


def validar_horarios(horario_inicio: str, horario_fim: str) -> Tuple[bool, Optional[str]]:
    """
    Valida se o horário final é maior que o inicial.
    
    Returns:
        Tupla (valido, mensagem_erro)
    """
    inicio_minutos = _horario_para_minutos(horario_inicio)
    fim_minutos = _horario_para_minutos(horario_fim)
    
    if fim_minutos <= inicio_minutos:
        return False, "O horário final deve ser maior que o horário inicial."
    
    return True, None
