"""FastAPI dependencies backed by the existing db_client abstraction."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException

from db.db_client import get_connection


def get_db() -> Generator:
    """Yield one request-scoped connection from SkillForge's db_client."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def require_user(user_id: int, conn=Depends(get_db)) -> int:
    """Validate that a user exists and return its integer ID."""
    row = conn.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (int(user_id),),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Unknown user_id: {user_id}")
    return int(row["user_id"] if hasattr(row, "keys") else row[0])


def load_user_profile(user_id: int, conn) -> dict[int, int]:
    """Load the profile used by Phase 9–12 from persisted user skills."""
    rows = conn.execute(
        "SELECT skill_id, proficiency FROM user_skills "
        "WHERE user_id = ? ORDER BY skill_id",
        (int(user_id),),
    ).fetchall()
    return {
        int(row["skill_id"] if hasattr(row, "keys") else row[0]): int(
            row["proficiency"] if hasattr(row, "keys") else row[1]
        )
        for row in rows
    }


def get_user_with_profile(
    user_id: int,
    conn=Depends(get_db),
) -> tuple[int, dict[int, int]]:
    """Validate a user and return ``(user_id, skill_id -> proficiency)``."""
    checked_user_id = require_user(user_id, conn)
    return checked_user_id, load_user_profile(checked_user_id, conn)
