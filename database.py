import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple

DB_PATH = os.path.join("data", "planilhado.db")


def init_db():
    """Inicializa o banco de dados criando a tabela se não existir."""
    # Criar diretório data se não existir
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hunts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respawn TEXT NOT NULL,
            horario_inicio TEXT NOT NULL,
            horario_fim TEXT NOT NULL,
            integrante1 TEXT,
            integrante2 TEXT,
            integrante3 TEXT,
            integrante4 TEXT,
            integrante5 TEXT,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de requisições pendentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requisicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            respawn TEXT NOT NULL,
            horario_inicio TEXT NOT NULL,
            horario_fim TEXT NOT NULL,
            integrante1 TEXT,
            integrante2 TEXT,
            integrante3 TEXT,
            integrante4 TEXT,
            integrante5 TEXT,
            data_requisicao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def get_respawns() -> List[str]:
    """Retorna lista de todos os respawns únicos cadastrados (hunts + requisições)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar respawns de hunts
    cursor.execute("SELECT DISTINCT respawn FROM hunts")
    respawns_hunts = {row[0] for row in cursor.fetchall()}
    
    # Buscar respawns de requisições
    cursor.execute("SELECT DISTINCT respawn FROM requisicoes")
    respawns_requisicoes = {row[0] for row in cursor.fetchall()}
    
    # Unir e ordenar
    respawns = sorted(respawns_hunts.union(respawns_requisicoes))
    
    conn.close()
    return respawns


def insert_hunt(respawn: str, horario_inicio: str, horario_fim: str,
                integrante1: Optional[str] = None,
                integrante2: Optional[str] = None,
                integrante3: Optional[str] = None,
                integrante4: Optional[str] = None,
                integrante5: Optional[str] = None) -> int:
    """Insere uma nova hunt no banco de dados. Retorna o ID inserido."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO hunts (respawn, horario_inicio, horario_fim,
                          integrante1, integrante2, integrante3,
                          integrante4, integrante5)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (respawn, horario_inicio, horario_fim,
          integrante1, integrante2, integrante3, integrante4, integrante5))
    
    hunt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return hunt_id


def get_hunts_by_respawn(respawn: str) -> List[Tuple]:
    """Retorna todas as hunts de um respawn específico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, respawn, horario_inicio, horario_fim,
               integrante1, integrante2, integrante3, integrante4, integrante5,
               data_cadastro
        FROM hunts
        WHERE respawn = ?
        ORDER BY horario_inicio
    """, (respawn,))
    
    hunts = cursor.fetchall()
    conn.close()
    
    return hunts


def get_all_hunts() -> List[Tuple]:
    """Retorna todas as hunts cadastradas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, respawn, horario_inicio, horario_fim,
               integrante1, integrante2, integrante3, integrante4, integrante5,
               data_cadastro
        FROM hunts
        ORDER BY respawn, horario_inicio
    """)
    
    hunts = cursor.fetchall()
    conn.close()
    
    return hunts


def get_hunts_by_respawn_for_validation(respawn: str, exclude_id: Optional[int] = None) -> List[Tuple]:
    """Retorna hunts de um respawn para validação de overlap, excluindo um ID se fornecido."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if exclude_id:
        cursor.execute("""
            SELECT id, horario_inicio, horario_fim
            FROM hunts
            WHERE respawn = ? AND id != ?
        """, (respawn, exclude_id))
    else:
        cursor.execute("""
            SELECT id, horario_inicio, horario_fim
            FROM hunts
            WHERE respawn = ?
        """, (respawn,))
    
    hunts = cursor.fetchall()
    conn.close()
    
    return hunts


def delete_hunt(hunt_id: int) -> bool:
    """Deleta uma hunt pelo ID. Retorna True se deletado com sucesso."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM hunts WHERE id = ?", (hunt_id,))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted


# ========== FUNÇÕES DE REQUISIÇÕES ==========

def insert_requisicao(respawn: str, horario_inicio: str, horario_fim: str,
                     integrante1: Optional[str] = None,
                     integrante2: Optional[str] = None,
                     integrante3: Optional[str] = None,
                     integrante4: Optional[str] = None,
                     integrante5: Optional[str] = None) -> int:
    """Insere uma nova requisição no banco de dados. Retorna o ID inserido."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO requisicoes (respawn, horario_inicio, horario_fim,
                                integrante1, integrante2, integrante3,
                                integrante4, integrante5)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (respawn, horario_inicio, horario_fim,
          integrante1, integrante2, integrante3, integrante4, integrante5))
    
    requisicao_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return requisicao_id


def get_all_requisicoes() -> List[Tuple]:
    """Retorna todas as requisições pendentes."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, respawn, horario_inicio, horario_fim,
               integrante1, integrante2, integrante3, integrante4, integrante5,
               data_requisicao
        FROM requisicoes
        ORDER BY data_requisicao DESC
    """)
    
    requisicoes = cursor.fetchall()
    conn.close()
    
    return requisicoes


def get_requisicao_by_id(requisicao_id: int) -> Optional[Tuple]:
    """Retorna uma requisição específica pelo ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, respawn, horario_inicio, horario_fim,
               integrante1, integrante2, integrante3, integrante4, integrante5,
               data_requisicao
        FROM requisicoes
        WHERE id = ?
    """, (requisicao_id,))
    
    requisicao = cursor.fetchone()
    conn.close()
    
    return requisicao


def delete_requisicao(requisicao_id: int) -> bool:
    """Deleta uma requisição pelo ID. Retorna True se deletado com sucesso."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM requisicoes WHERE id = ?", (requisicao_id,))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted


def count_requisicoes_pendentes() -> int:
    """Retorna o número de requisições pendentes."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM requisicoes")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count


def get_requisicoes_by_respawn_for_validation(respawn: str, exclude_id: Optional[int] = None) -> List[Tuple]:
    """Retorna requisições de um respawn para validação de overlap."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if exclude_id:
        cursor.execute("""
            SELECT id, horario_inicio, horario_fim
            FROM requisicoes
            WHERE respawn = ? AND id != ?
        """, (respawn, exclude_id))
    else:
        cursor.execute("""
            SELECT id, horario_inicio, horario_fim
            FROM requisicoes
            WHERE respawn = ?
        """, (respawn,))
    
    requisicoes = cursor.fetchall()
    conn.close()
    
    return requisicoes
