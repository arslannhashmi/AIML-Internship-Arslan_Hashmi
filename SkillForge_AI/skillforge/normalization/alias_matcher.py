"""Exact canonical/alias matching for extracted skill mentions."""

from __future__ import annotations

import re

from db.db_client import get_connection


def normalize_text(value: str) -> str:
    """Normalize formatting variants such as Machine-Learning and ML."""
    value = value.casefold().strip()
    value = re.sub(r"[/_–—-]+", " ", value)
    value = re.sub(r"[^a-z0-9+#. ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def load_alias_index(conn=None) -> dict[str, dict]:
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        index = {}
        for row in conn.execute("SELECT skill_id, name FROM skills").fetchall():
            skill_id = row["skill_id"] if hasattr(row, "keys") else row[0]
            name = row["name"] if hasattr(row, "keys") else row[1]
            index[normalize_text(name)] = {
                "skill_id": int(skill_id),
                "canonical_name": name,
            }
        query = (
            "SELECT sa.skill_id, sa.alias_text, s.name "
            "FROM skill_aliases sa JOIN skills s ON sa.skill_id = s.skill_id"
        )
        for row in conn.execute(query).fetchall():
            skill_id = row["skill_id"] if hasattr(row, "keys") else row[0]
            alias = row["alias_text"] if hasattr(row, "keys") else row[1]
            canonical = row["name"] if hasattr(row, "keys") else row[2]
            index[normalize_text(alias)] = {
                "skill_id": int(skill_id),
                "canonical_name": canonical,
            }
        return index
    finally:
        if own_conn:
            conn.close()


def match_alias(raw_text: str, *, conn=None) -> dict | None:
    """Return a canonical match or None without guessing."""
    index = load_alias_index(conn)
    match = index.get(normalize_text(raw_text))
    if not match:
        return None
    return {
        **match,
        "matched_text": raw_text,
        "method": "alias",
        "confidence": 1.0,
    }