from typing import Optional, Tuple
from database import get_hunts_by_respawn_for_validation, get_requisicoes_by_respawn_for_validation


def verificar_overlap(respawn: str, horario_inicio: str, horario_fim: str, 
                     exclude_id: Optional[int] = None, 
                     verificar_requisicoes: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Verifica se há overlap de horário para um respawn específico.
    
    Args:
        respawn: Nome do respawn
        horario_inicio: Horário de início no formato HH:MM
        horario_fim: Horário de fim no formato HH:MM
        exclude_id: ID de uma hunt/requisição a ser excluída da verificação (útil para edição)
        verificar_requisicoes: Se True, também verifica overlaps com requisições pendentes
    
    Returns:
        Tupla (tem_overlap, mensagem_erro)
        Se tem_overlap é True, mensagem_erro contém detalhes do conflito
    """
    # Buscar todas as hunts do mesmo respawn
    hunts_existentes = get_hunts_by_respawn_for_validation(respawn, exclude_id)
    
    # Converter horários para minutos para facilitar comparação
    inicio_minutos = _horario_para_minutos(horario_inicio)
    fim_minutos = _horario_para_minutos(horario_fim)
    segmentos_novo = _segmentos_intervalo(inicio_minutos, fim_minutos)
    
    def _tem_overlap_segmentos(seg_a, seg_b) -> bool:
        for (a1, a2) in seg_a:
            for (b1, b2) in seg_b:
                if _segmentos_se_sobrepoem(a1, a2, b1, b2):
                    return True
        return False

    # Verificar overlap com cada hunt existente
    for hunt_id, h_inicio, h_fim in hunts_existentes:
        h_inicio_min = _horario_para_minutos(h_inicio)
        h_fim_min = _horario_para_minutos(h_fim)
        segmentos_existente = _segmentos_intervalo(h_inicio_min, h_fim_min)
        if _tem_overlap_segmentos(segmentos_novo, segmentos_existente):
            mensagem = f"Conflito de horário! Já existe uma hunt cadastrada das {h_inicio} às {h_fim}."
            return True, mensagem
    
    # Verificar overlap com requisições pendentes (se solicitado)
    if verificar_requisicoes:
        requisicoes_existentes = get_requisicoes_by_respawn_for_validation(respawn, exclude_id)
        
        for req_id, h_inicio, h_fim in requisicoes_existentes:
            h_inicio_min = _horario_para_minutos(h_inicio)
            h_fim_min = _horario_para_minutos(h_fim)
            segmentos_existente = _segmentos_intervalo(h_inicio_min, h_fim_min)
            if _tem_overlap_segmentos(segmentos_novo, segmentos_existente):
                mensagem = f"Conflito de horário! Já existe uma requisição pendente das {h_inicio} às {h_fim}."
                return True, mensagem
    
    return False, None


def _horario_para_minutos(horario: str) -> int:
    """Converte horário no formato HH:MM para minutos desde meia-noite."""
    horas, minutos = map(int, horario.split(':'))
    return horas * 60 + minutos


MINUTOS_POR_DIA = 24 * 60  # 1440


def _segmentos_intervalo(inicio_min: int, fim_min: int):
    """
    Retorna os segmentos [início, fim] em minutos que o intervalo cobre.
    Se o intervalo cruza meia-noite (fim <= início), retorna dois segmentos.
    """
    if inicio_min < fim_min:
        return [(inicio_min, fim_min)]
    # Cruza meia-noite: [inicio_min, 24h) e [0, fim_min]
    return [(inicio_min, MINUTOS_POR_DIA), (0, fim_min)]


def _segmentos_se_sobrepoem(a1: int, a2: int, b1: int, b2: int) -> bool:
    """Verifica se os segmentos [a1, a2] e [b1, b2] se sobrepõem."""
    return a1 < b2 and a2 > b1


def validar_horarios(horario_inicio: str, horario_fim: str) -> Tuple[bool, Optional[str]]:
    """
    Valida os horários. Não há restrição de ordem: o horário final pode ser menor
    que o inicial (ex.: 23:00 às 02:00). Conflitos são tratados apenas em verificar_overlap.
    
    Returns:
        Tupla (valido, mensagem_erro)
    """
    return True, None
