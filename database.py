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
    
    conn.commit()
    conn.close()


def get_respawns() -> List[str]:
    """Retorna lista de todos os respawns únicos cadastrados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT respawn FROM hunts ORDER BY respawn")
    respawns = [row[0] for row in cursor.fetchall()]
    
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
