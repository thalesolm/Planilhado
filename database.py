"""
Camada de banco de dados com suporte a SQLite (local) e PostgreSQL (Streamlit Cloud).
Aceita:
  - DATABASE_URL (string única) nos secrets ou variável de ambiente
  - [connections.postgresql] no formato nativo do Streamlit (host, port, database, username, password, sslmode)
"""
import os
from typing import List, Optional, Tuple
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

# Caminho local do SQLite
DB_PATH = os.path.join("data", "planilhado.db")
SQLITE_URL = f"sqlite:///{DB_PATH}"

_engine = None


def _build_url_from_connection(c) -> str:
    """Monta URL PostgreSQL a partir do bloco [connections.postgresql]."""
    host = c.get("host") or ""
    port = c.get("port")
    port = int(port) if port is not None else 5432
    database = c.get("database") or "postgres"
    username = c.get("username") or "postgres"
    password = c.get("password") or ""
    sslmode = c.get("sslmode") or "require"
    # Senha pode ter caracteres especiais; precisa ser codificada na URL
    password_encoded = quote_plus(password) if password else ""
    return f"postgresql://{username}:{password_encoded}@{host}:{port}/{database}?sslmode={sslmode}"


def _get_database_url() -> Optional[str]:
    """Obtém URL do PostgreSQL: DATABASE_URL ou monta a partir de [connections.postgresql]."""
    # 1) DATABASE_URL (string única) nos secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets is not None:
            url = None
            if hasattr(st.secrets, "DATABASE_URL"):
                url = getattr(st.secrets, "DATABASE_URL", None)
            if not url and "DATABASE_URL" in st.secrets:
                url = st.secrets["DATABASE_URL"]
            if not url and hasattr(st.secrets, "get"):
                url = st.secrets.get("DATABASE_URL")
            if url:
                return str(url).strip()

            # 2) Formato [connections.postgresql] (conexão nativa do Streamlit)
            conn = None
            if hasattr(st.secrets, "connections") and hasattr(st.secrets.connections, "postgresql"):
                conn = st.secrets.connections.postgresql
            elif "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
                conn = st.secrets["connections"]["postgresql"]
            if conn is not None:
                keys = ("host", "port", "database", "username", "password", "sslmode")
                if isinstance(conn, dict):
                    c = {k: conn.get(k) for k in keys}
                else:
                    c = {k: getattr(conn, k, None) for k in keys}
                if c.get("host"):
                    return _build_url_from_connection(c)
    except Exception:
        pass
    # 3) Variável de ambiente
    url = os.environ.get("DATABASE_URL", "").strip()
    return url if url else None


def get_engine():
    """Retorna o engine SQLAlchemy (SQLite ou PostgreSQL)."""
    global _engine
    if _engine is not None:
        return _engine

    url = _get_database_url()

    # PostgreSQL: usa a URL diretamente (ex: postgresql://user:pass@host:5432/dbname)
    if url and (url.startswith("postgresql://") or url.startswith("postgres://")):
        _engine = create_engine(url, pool_pre_ping=True, pool_size=1, max_overflow=0)
    else:
        # SQLite local
        os.makedirs("data", exist_ok=True)
        _engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

    return _engine


def get_connection_status() -> str:
    """Retorna uma string indicando qual banco está em uso (para debug/confirmação)."""
    try:
        engine = get_engine()
        url_str = str(engine.url)
        if "postgresql" in url_str or "postgres" in url_str:
            # Não expor a URL completa por segurança
            return "PostgreSQL (nuvem)"
        return "SQLite (local)"
    except Exception as e:
        return f"Erro: {e}"


def init_db():
    """Cria as tabelas se não existirem (compatível com SQLite e PostgreSQL)."""
    engine = get_engine()
    is_postgres = "postgresql" in str(engine.url) or "postgres" in str(engine.url)

    with engine.connect() as conn:
        if is_postgres:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hunts (
                    id SERIAL PRIMARY KEY,
                    respawn VARCHAR(255) NOT NULL,
                    horario_inicio VARCHAR(10) NOT NULL,
                    horario_fim VARCHAR(10) NOT NULL,
                    integrante1 VARCHAR(255),
                    integrante2 VARCHAR(255),
                    integrante3 VARCHAR(255),
                    integrante4 VARCHAR(255),
                    integrante5 VARCHAR(255),
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS requisicoes (
                    id SERIAL PRIMARY KEY,
                    respawn VARCHAR(255) NOT NULL,
                    horario_inicio VARCHAR(10) NOT NULL,
                    horario_fim VARCHAR(10) NOT NULL,
                    integrante1 VARCHAR(255),
                    integrante2 VARCHAR(255),
                    integrante3 VARCHAR(255),
                    integrante4 VARCHAR(255),
                    integrante5 VARCHAR(255),
                    data_requisicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:
            conn.execute(text("""
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
            """))
            conn.execute(text("""
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
            """))
        conn.commit()


def _row_to_tuple(row) -> Tuple:
    """Converte uma Row do SQLAlchemy em tupla para compatibilidade com o resto do código."""
    try:
        return tuple(row)
    except Exception:
        return tuple(row._mapping.values()) if hasattr(row, "_mapping") else tuple(row)


def get_respawns() -> List[str]:
    """Retorna lista de todos os respawns únicos cadastrados (hunts + requisições)."""
    engine = get_engine()
    with engine.connect() as conn:
        r1 = conn.execute(text("SELECT DISTINCT respawn FROM hunts"))
        respawns_hunts = {row[0] for row in r1}
        r2 = conn.execute(text("SELECT DISTINCT respawn FROM requisicoes"))
        respawns_requisicoes = {row[0] for row in r2}
    return sorted(respawns_hunts.union(respawns_requisicoes))


def insert_hunt(
    respawn: str,
    horario_inicio: str,
    horario_fim: str,
    integrante1: Optional[str] = None,
    integrante2: Optional[str] = None,
    integrante3: Optional[str] = None,
    integrante4: Optional[str] = None,
    integrante5: Optional[str] = None,
) -> int:
    """Insere uma nova hunt. Retorna o ID inserido."""
    engine = get_engine()
    is_pg = engine.dialect.name == "postgresql"
    with engine.connect() as conn:
        if is_pg:
            r = conn.execute(
                text("""
                    INSERT INTO hunts (respawn, horario_inicio, horario_fim,
                        integrante1, integrante2, integrante3, integrante4, integrante5)
                    VALUES (:respawn, :horario_inicio, :horario_fim,
                        :i1, :i2, :i3, :i4, :i5)
                    RETURNING id
                """),
                {
                    "respawn": respawn,
                    "horario_inicio": horario_inicio,
                    "horario_fim": horario_fim,
                    "i1": integrante1,
                    "i2": integrante2,
                    "i3": integrante3,
                    "i4": integrante4,
                    "i5": integrante5,
                },
            )
            last_id = r.scalar()
        else:
            r = conn.execute(
                text("""
                    INSERT INTO hunts (respawn, horario_inicio, horario_fim,
                        integrante1, integrante2, integrante3, integrante4, integrante5)
                    VALUES (:respawn, :horario_inicio, :horario_fim,
                        :i1, :i2, :i3, :i4, :i5)
                """),
                {
                    "respawn": respawn,
                    "horario_inicio": horario_inicio,
                    "horario_fim": horario_fim,
                    "i1": integrante1,
                    "i2": integrante2,
                    "i3": integrante3,
                    "i4": integrante4,
                    "i5": integrante5,
                },
            )
            last_id = r.lastrowid
        conn.commit()
    return last_id


def get_hunts_by_respawn(respawn: str) -> List[Tuple]:
    """Retorna todas as hunts de um respawn."""
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(
            text("""
                SELECT id, respawn, horario_inicio, horario_fim,
                    integrante1, integrante2, integrante3, integrante4, integrante5,
                    data_cadastro
                FROM hunts WHERE respawn = :respawn ORDER BY horario_inicio
            """),
            {"respawn": respawn},
        )
        rows = r.fetchall()
    return [_row_to_tuple(row) for row in rows]


def get_all_hunts() -> List[Tuple]:
    """Retorna todas as hunts."""
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT id, respawn, horario_inicio, horario_fim,
                integrante1, integrante2, integrante3, integrante4, integrante5,
                data_cadastro
            FROM hunts ORDER BY respawn, horario_inicio
        """))
        rows = r.fetchall()
    return [_row_to_tuple(row) for row in rows]


def get_hunts_by_respawn_for_validation(
    respawn: str, exclude_id: Optional[int] = None
) -> List[Tuple]:
    """Retorna hunts de um respawn para validação de overlap."""
    engine = get_engine()
    with engine.connect() as conn:
        if exclude_id:
            r = conn.execute(
                text("SELECT id, horario_inicio, horario_fim FROM hunts WHERE respawn = :respawn AND id != :eid"),
                {"respawn": respawn, "eid": exclude_id},
            )
        else:
            r = conn.execute(
                text("SELECT id, horario_inicio, horario_fim FROM hunts WHERE respawn = :respawn"),
                {"respawn": respawn},
            )
        rows = r.fetchall()
    return [_row_to_tuple(row) for row in rows]


def delete_hunt(hunt_id: int) -> bool:
    """Deleta uma hunt pelo ID."""
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(text("DELETE FROM hunts WHERE id = :id"), {"id": hunt_id})
        conn.commit()
        deleted = r.rowcount > 0
    return deleted


# ========== REQUISIÇÕES ==========


def insert_requisicao(
    respawn: str,
    horario_inicio: str,
    horario_fim: str,
    integrante1: Optional[str] = None,
    integrante2: Optional[str] = None,
    integrante3: Optional[str] = None,
    integrante4: Optional[str] = None,
    integrante5: Optional[str] = None,
) -> int:
    """Insere uma requisição. Retorna o ID inserido."""
    engine = get_engine()
    is_pg = engine.dialect.name == "postgresql"
    with engine.connect() as conn:
        if is_pg:
            r = conn.execute(
                text("""
                    INSERT INTO requisicoes (respawn, horario_inicio, horario_fim,
                        integrante1, integrante2, integrante3, integrante4, integrante5)
                    VALUES (:respawn, :horario_inicio, :horario_fim,
                        :i1, :i2, :i3, :i4, :i5)
                    RETURNING id
                """),
                {
                    "respawn": respawn,
                    "horario_inicio": horario_inicio,
                    "horario_fim": horario_fim,
                    "i1": integrante1,
                    "i2": integrante2,
                    "i3": integrante3,
                    "i4": integrante4,
                    "i5": integrante5,
                },
            )
            last_id = r.scalar()
        else:
            r = conn.execute(
                text("""
                    INSERT INTO requisicoes (respawn, horario_inicio, horario_fim,
                        integrante1, integrante2, integrante3, integrante4, integrante5)
                    VALUES (:respawn, :horario_inicio, :horario_fim,
                        :i1, :i2, :i3, :i4, :i5)
                """),
                {
                    "respawn": respawn,
                    "horario_inicio": horario_inicio,
                    "horario_fim": horario_fim,
                    "i1": integrante1,
                    "i2": integrante2,
                    "i3": integrante3,
                    "i4": integrante4,
                    "i5": integrante5,
                },
            )
            last_id = r.lastrowid
        conn.commit()
    return last_id


def get_all_requisicoes() -> List[Tuple]:
    """Retorna todas as requisições pendentes."""
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT id, respawn, horario_inicio, horario_fim,
                integrante1, integrante2, integrante3, integrante4, integrante5,
                data_requisicao
            FROM requisicoes ORDER BY data_requisicao DESC
        """))
        rows = r.fetchall()
    return [_row_to_tuple(row) for row in rows]


def get_requisicao_by_id(requisicao_id: int) -> Optional[Tuple]:
    """Retorna uma requisição pelo ID."""
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(
            text("""
                SELECT id, respawn, horario_inicio, horario_fim,
                    integrante1, integrante2, integrante3, integrante4, integrante5,
                    data_requisicao
                FROM requisicoes WHERE id = :id
            """),
            {"id": requisicao_id},
        )
        row = r.fetchone()
    return _row_to_tuple(row) if row else None


def delete_requisicao(requisicao_id: int) -> bool:
    """Deleta uma requisição pelo ID."""
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(text("DELETE FROM requisicoes WHERE id = :id"), {"id": requisicao_id})
        conn.commit()
        deleted = r.rowcount > 0
    return deleted


def count_requisicoes_pendentes() -> int:
    """Retorna a quantidade de requisições pendentes."""
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*) FROM requisicoes"))
        count = r.scalar() or 0
    return count


def get_requisicoes_by_respawn_for_validation(
    respawn: str, exclude_id: Optional[int] = None
) -> List[Tuple]:
    """Retorna requisições de um respawn para validação de overlap."""
    engine = get_engine()
    with engine.connect() as conn:
        if exclude_id:
            r = conn.execute(
                text("SELECT id, horario_inicio, horario_fim FROM requisicoes WHERE respawn = :respawn AND id != :eid"),
                {"respawn": respawn, "eid": exclude_id},
            )
        else:
            r = conn.execute(
                text("SELECT id, horario_inicio, horario_fim FROM requisicoes WHERE respawn = :respawn"),
                {"respawn": respawn},
            )
        rows = r.fetchall()
    return [_row_to_tuple(row) for row in rows]
