"""
Camada de banco de dados com suporte a SQLite (local) e PostgreSQL (Streamlit Cloud).
Aceita:
  - DATABASE_URL (string única) nos secrets ou variável de ambiente
  - [connections.postgresql] no formato nativo do Streamlit (host, port, database, username, password, sslmode)
"""
import os
import re
from typing import List, Optional, Tuple
from urllib.parse import quote_plus, unquote

from sqlalchemy import create_engine, text

# Caminho local do SQLite
DB_PATH = os.path.join("data", "planilhado.db")
SQLITE_URL = f"sqlite:///{DB_PATH}"

_engine = None
_postgres_failed = False  # True quando PostgreSQL falhou e usamos SQLite


def _normalize_postgres_url(url: str) -> str:
    """
    Corrige a URL do PostgreSQL quando a senha tem caracteres especiais (#, !, ^, etc).
    Esses caracteres quebram a URL; re codificamos a senha para que a conexão funcione.
    """
    if not url or not url.strip().startswith(("postgresql://", "postgres://")):
        return url
    url = url.strip()
    try:
        # Encontra user:password@ (o @ que separa userinfo de host)
        # Formato: postgresql://USER:PASSWORD@HOST:PORT/DB?params
        match = re.match(r"(postgres(?:ql)?://)([^/]+)(/.*)", url, re.IGNORECASE)
        if not match:
            return url
        prefix, userinfo_host, path = match.groups()
        # userinfo_host = "user:password@host:port" ou "user:password@host"
        at_idx = userinfo_host.rfind("@")
        if at_idx == -1:
            return url
        userinfo = userinfo_host[:at_idx]  # user:password (password pode ter : e @)
        host_part = userinfo_host[at_idx + 1 :]
        # user:password - senha é tudo após o primeiro ":"
        colon = userinfo.find(":")
        if colon == -1:
            return url
        user = userinfo[:colon]
        password = userinfo[colon + 1 :]
        # Decodifica se já veio codificado, depois codifica de forma segura
        password_decoded = unquote(password)
        password_encoded = quote_plus(password_decoded)
        new_url = f"{prefix}{user}:{password_encoded}@{host_part}{path}"
        return new_url
    except Exception:
        return url


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
            try:
                if hasattr(st.secrets, "connections") and hasattr(st.secrets.connections, "postgresql"):
                    conn = st.secrets.connections.postgresql
                if conn is None and "connections" in st.secrets:
                    conn = st.secrets["connections"].get("postgresql") if hasattr(st.secrets["connections"], "get") else st.secrets["connections"]["postgresql"]
            except Exception:
                conn = None

            if conn is not None:
                keys = ("host", "port", "database", "username", "password", "sslmode")
                c = {}
                # Converter para dict se for outro tipo (Streamlit usa objeto tipo AttrDict)
                try:
                    if hasattr(conn, "__iter__") and not isinstance(conn, (str, bytes)):
                        conn = dict(conn) if not isinstance(conn, dict) else conn
                except Exception:
                    pass
                for k in keys:
                    try:
                        if isinstance(conn, dict):
                            c[k] = conn.get(k)
                        elif hasattr(conn, "keys") and k in conn.keys():
                            c[k] = conn[k]
                        else:
                            c[k] = getattr(conn, k, None)
                    except Exception:
                        c[k] = None
                if c.get("host"):
                    return _build_url_from_connection(c)
    except Exception:
        pass
    # 3) Variável de ambiente
    url = os.environ.get("DATABASE_URL", "").strip()
    return url if url else None


def get_engine():
    """Retorna o engine SQLAlchemy (SQLite ou PostgreSQL). Se PostgreSQL falhar, usa SQLite."""
    global _engine, _postgres_failed
    if _engine is not None:
        return _engine

    url = _get_database_url()
    if url and (url.startswith("postgresql://") or url.startswith("postgres://")):
        url = _normalize_postgres_url(url)  # codifica senha com #, !, ^ etc.

    if url and (url.startswith("postgresql://") or url.startswith("postgres://")):
        try:
            # connect_args garante SSL para Supabase/pooler
            _engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_size=1,
                max_overflow=0,
                connect_args={"sslmode": "require"} if "sslmode" not in url else {},
            )
            with _engine.connect() as test_conn:
                test_conn.execute(text("SELECT 1"))
            _postgres_failed = False
        except Exception:
            _engine = None
            _postgres_failed = True
            os.makedirs("data", exist_ok=True)
            _engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    else:
        os.makedirs("data", exist_ok=True)
        _engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
        _postgres_failed = False

    return _engine


def get_connection_status() -> str:
    """Retorna uma string indicando qual banco está em uso (para debug/confirmação)."""
    global _postgres_failed
    try:
        engine = get_engine()
        if _postgres_failed:
            return "SQLite (fallback: PostgreSQL falhou)"
        url_str = str(engine.url)
        if "postgresql" in url_str or "postgres" in url_str:
            return "PostgreSQL (nuvem)"
        return "SQLite (local)"
    except Exception as e:
        return f"Erro: {e}"


def postgres_failed() -> bool:
    """Retorna True se a conexão PostgreSQL falhou e estamos em SQLite por fallback."""
    return _postgres_failed


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
