"""
SkillForge AI — Phase 3: Database initialisation script.

Builds db/skillforge.db from schema.sql and populates it with seed_data.py.
Translates Postgres-specific syntax to SQLite automatically (SERIAL → INTEGER,
ON DELETE CASCADE requires PRAGMA foreign_keys = ON, etc.).

Run from the repo root (or from anywhere — paths are resolved relative to this
file):
    python db/init_db.py

Exports a JSON snapshot of each static table to data/*_export.json for
offline inspection and Phase 5+ debug use.
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

# ─── Path setup ──────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH   = REPO_ROOT / "db" / "skillforge.db"
SCHEMA    = REPO_ROOT / "schema.sql"
DATA_DIR  = REPO_ROOT / "data"
sys.path.insert(0, str(REPO_ROOT))
from data.seed_data import (  # noqa: E402
    SKILLS, SKILL_ALIASES, SKILL_PREREQUISITES, CAREERS,
    CAREER_SKILL_REQUIREMENTS,
)


# ─── SQLite-compatibility shim ────────────────────────────────────────────────

def postgres_to_sqlite(sql: str) -> str:
    """Strip/translate Postgres-isms so the schema runs on SQLite."""
    # SERIAL → INTEGER (SQLite uses rowid autoincrement via INTEGER PRIMARY KEY)
    sql = re.sub(r"\bSERIAL\b", "INTEGER", sql, flags=re.IGNORECASE)
    # Remove REFERENCES … ON DELETE CASCADE (handled by PRAGMA + triggers;
    # SQLite does support ON DELETE CASCADE with PRAGMA foreign_keys = ON)
    # — actually SQLite *does* support it with the pragma, so we keep it.
    # Remove CHECK constraints that reference multiple columns (SQLite 3.25+
    # supports them, so we also keep them).
    # DROP unsupported column-level DEFAULT for CURRENT_TIMESTAMP inside CHECK
    # (not needed here, so nothing to do).
    return sql


# ─── Build + populate ────────────────────────────────────────────────────────

def build_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create + populate the SQLite database.  Drops existing data each run."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Apply schema via executescript (handles multi-statement SQL correctly).
    # executescript issues an implicit COMMIT first, so we enable foreign keys
    # after it completes.
    raw_schema = SCHEMA.read_text(encoding="utf-8")
    sqlite_schema = postgres_to_sqlite(raw_schema)
    conn.executescript(sqlite_schema)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    print(f"Schema applied ({SCHEMA.name})")

    # Seed skills
    conn.executemany(
        "INSERT INTO skills (skill_id, name, category, subcategory, difficulty, description)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        SKILLS,
    )
    print(f"  → {len(SKILLS)} skills inserted")

    # Seed aliases
    conn.executemany(
        "INSERT INTO skill_aliases (skill_id, alias_text) VALUES (?, ?)",
        SKILL_ALIASES,
    )
    print(f"  → {len(SKILL_ALIASES)} aliases inserted")

    # Seed prerequisites
    conn.executemany(
        "INSERT INTO skill_prerequisites (from_skill_id, to_skill_id, relation_type)"
        " VALUES (?, ?, ?)",
        SKILL_PREREQUISITES,
    )
    print(f"  → {len(SKILL_PREREQUISITES)} prerequisite edges inserted")

    # Seed careers
    conn.executemany(
        "INSERT INTO careers (career_id, name, description) VALUES (?, ?, ?)",
        CAREERS,
    )
    print(f"  → {len(CAREERS)} careers inserted")

    # Seed career-skill requirements
    conn.executemany(
        "INSERT INTO career_skill_requirements"
        " (career_id, skill_id, importance, minimum_proficiency, preferred_proficiency)"
        " VALUES (?, ?, ?, ?, ?)",
        CAREER_SKILL_REQUIREMENTS,
    )
    print(f"  → {len(CAREER_SKILL_REQUIREMENTS)} career-skill requirements inserted")

    conn.commit()
    print(f"\nDatabase built: {db_path}")
    return conn


# ─── Validation ──────────────────────────────────────────────────────────────

def validate(conn: sqlite3.Connection) -> bool:
    """Quick sanity checks — same suite as query_test.py but inline here."""
    ok = True
    checks = [
        ("SELECT COUNT(*) FROM skills",                    len(SKILLS)),
        ("SELECT COUNT(*) FROM skill_aliases",             len(SKILL_ALIASES)),
        ("SELECT COUNT(*) FROM skill_prerequisites",       len(SKILL_PREREQUISITES)),
        ("SELECT COUNT(*) FROM careers",                   len(CAREERS)),
        ("SELECT COUNT(*) FROM career_skill_requirements", len(CAREER_SKILL_REQUIREMENTS)),
    ]
    for sql, expected in checks:
        row = conn.execute(sql).fetchone()
        actual = row[0]
        status = "OK" if actual == expected else f"FAIL (expected {expected})"
        print(f"  {sql.split('FROM')[1].strip():45s} → {actual:4d}  {status}")
        if actual != expected:
            ok = False

    # Check that every alias resolves to a real skill
    orphan = conn.execute(
        "SELECT COUNT(*) FROM skill_aliases sa"
        " LEFT JOIN skills s ON sa.skill_id = s.skill_id"
        " WHERE s.skill_id IS NULL"
    ).fetchone()[0]
    print(f"  Orphan aliases (should be 0):                           → {orphan:4d}  {'OK' if orphan == 0 else 'FAIL'}")
    ok = ok and (orphan == 0)

    # Check that every career has at least one skill requirement
    careers_without_reqs = conn.execute(
        "SELECT COUNT(*) FROM careers c"
        " LEFT JOIN career_skill_requirements csr ON c.career_id = csr.career_id"
        " WHERE csr.career_id IS NULL"
    ).fetchone()[0]
    print(f"  Careers with no requirements (should be 0):             → {careers_without_reqs:4d}  "
          f"{'OK' if careers_without_reqs == 0 else 'FAIL'}")
    ok = ok and (careers_without_reqs == 0)

    return ok


# ─── JSON export ─────────────────────────────────────────────────────────────

def export_json(conn: sqlite3.Connection) -> None:
    """Export each static table to data/*_export.json for offline use."""
    DATA_DIR.mkdir(exist_ok=True)
    exports = {
        "skills_export.json":                    "SELECT * FROM skills",
        "skill_aliases_export.json":             "SELECT * FROM skill_aliases",
        "skill_prerequisites_export.json":       "SELECT * FROM skill_prerequisites",
        "careers_export.json":                   "SELECT * FROM careers",
        "career_skill_requirements_export.json": "SELECT * FROM career_skill_requirements",
    }
    for filename, sql in exports.items():
        rows = [dict(r) for r in conn.execute(sql).fetchall()]
        out = DATA_DIR / filename
        out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Exported {len(rows):4d} rows → {out.relative_to(REPO_ROOT)}")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SkillForge AI — init_db.py")
    print("=" * 60)

    conn = build_db()

    print("\nValidation:")
    all_ok = validate(conn)

    print("\nJSON export:")
    export_json(conn)

    conn.close()
    print(f"\n{'ALL CHECKS PASS' if all_ok else 'SOME CHECKS FAILED — see above'}")
    sys.exit(0 if all_ok else 1)
