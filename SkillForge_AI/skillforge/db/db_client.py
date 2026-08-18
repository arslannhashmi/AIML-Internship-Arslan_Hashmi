"""
SkillForge AI — db_client.py

Thin database access layer.  All modules that need the database import this
module — none of them write raw SQL directly.  This isolates the SQLite ↔
Postgres swap to one file: swap the connection factory here without touching
any calling code.

Public API
----------
get_connection() → sqlite3.Connection | psycopg2 connection
    Returns a ready-to-use connection.  Caller is responsible for closing it
    (or use as a context manager).

get_cursor(conn)
    Returns a cursor whose fetchone/fetchall return dicts (Row objects for
    SQLite; RealDictCursor for Postgres).

execute(sql, params=(), *, conn=None) → list[dict]
    Convenience: open connection, run query, return all rows as dicts, close.
    Not suitable for transactions — use get_connection() directly for those.

DB backend selection:
    Reads SKILLFORGE_DB_PATH env var for SQLite (default: db/skillforge.db).
    When DATABASE_URL starts with 'postgresql://' or 'postgres://', uses psycopg2
    (Phase 14+ only; not imported until needed to avoid hard dependency during
    SQLite-only development).
"""

import os
import sqlite3
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_SQLITE = _REPO_ROOT / "db" / "skillforge.db"


def _is_postgres() -> bool:
    # If SKILLFORGE_DB_PATH is set, always use SQLite — this overrides DATABASE_URL
    # so the project's own SQLite database is used even when Replit's platform
    # DATABASE_URL env var points to a managed Postgres instance.
    if os.environ.get("SKILLFORGE_DB_PATH"):
        return False
    url = os.environ.get("DATABASE_URL", "")
    return url.startswith(("postgresql://", "postgres://"))


def get_connection():
    """Return an open database connection (SQLite or Postgres)."""
    if _is_postgres():
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError as exc:
            raise RuntimeError(
                "psycopg2 not installed.  Run: pip install psycopg2-binary"
            ) from exc
        conn = psycopg2.connect(os.environ["DATABASE_URL"],
                                cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    else:
        db_path = os.environ.get("SKILLFORGE_DB_PATH", str(_DEFAULT_SQLITE))
        if not Path(db_path).exists():
            raise FileNotFoundError(
                f"SQLite database not found: {db_path}\n"
                "Run: python db/init_db.py"
            )
        # FastAPI executes synchronous route handlers in a worker thread while
        # dependencies may be created on the request thread. The connection
        # remains request-scoped and is never shared between requests, so
        # disabling SQLite's same-thread guard is safe for this abstraction.
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def get_cursor(conn):
    """Return a dict-yielding cursor for the given connection."""
    if _is_postgres():
        return conn.cursor()   # already RealDictCursor
    return conn.cursor()


def execute(sql: str, params: tuple = (), *, conn=None) -> list[dict]:
    """
    Run a SELECT query and return all rows as plain dicts.
    Opens+closes its own connection unless one is passed in.
    Not safe for INSERT/UPDATE/DELETE (no commit).
    """
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        # Normalise sqlite3.Row objects to plain dicts
        return [dict(r) for r in rows]
    finally:
        if own_conn:
            conn.close()


if __name__ == "__main__":
    # Quick smoke-test: print skill + career counts
    skills  = execute("SELECT COUNT(*) AS n FROM skills")
    careers = execute("SELECT COUNT(*) AS n FROM careers")
    print(f"Skills: {skills[0]['n']}   Careers: {careers[0]['n']}")
