"""
SkillForge AI — Phase 3: Database query sanity tests.

Runs a suite of checks against db/skillforge.db to verify:
  1. Row-count invariants match seed_data.py assertions.
  2. Alias resolution works (a known alias maps to the right skill_id).
  3. Prerequisite edges are queryable and non-cyclic in a shallow sense.
  4. Career requirements are consistent (importance/proficiency in 1–5 range).
  5. Each career has full coverage (has at least one essential skill, importance=5).

Run from the repo root:
    python db/query_test.py
"""

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH   = REPO_ROOT / "db" / "skillforge.db"
sys.path.insert(0, str(REPO_ROOT))
from data.seed_data import (  # noqa: E402
    SKILLS, SKILL_ALIASES, SKILL_PREREQUISITES, CAREERS,
    CAREER_SKILL_REQUIREMENTS,
)


def run() -> bool:
    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}")
        print("Run: python db/init_db.py")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    results = []

    # ── 1. Row counts ─────────────────────────────────────────────────────────
    for table, expected in [
        ("skills",                    len(SKILLS)),
        ("skill_aliases",             len(SKILL_ALIASES)),
        ("skill_prerequisites",       len(SKILL_PREREQUISITES)),
        ("careers",                   len(CAREERS)),
        ("career_skill_requirements", len(CAREER_SKILL_REQUIREMENTS)),
    ]:
        actual = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        ok = actual == expected
        results.append((f"Row count: {table}", ok,
                        f"expected {expected}, got {actual}" if not ok else ""))

    # ── 2. Alias resolution ───────────────────────────────────────────────────
    alias_cases = [
        ("ML",          21),   # Machine Learning
        ("NLP",         23),   # Natural Language Processing
        ("ReactJS",     45),   # React
        ("sklearn",     15),   # Scikit-learn
        ("K8s",         66),   # Kubernetes
        ("Postgres",    34),   # PostgreSQL
        ("REST",        60),   # REST API Design
        ("TF",          16),   # TensorFlow
    ]
    for alias, expected_id in alias_cases:
        row = conn.execute(
            "SELECT s.skill_id, s.name FROM skill_aliases sa"
            " JOIN skills s ON sa.skill_id = s.skill_id"
            " WHERE LOWER(sa.alias_text) = LOWER(?)",
            (alias,),
        ).fetchone()
        ok = row is not None and row["skill_id"] == expected_id
        detail = "" if ok else f"got {dict(row) if row else None}"
        results.append((f"Alias '{alias}' → skill_id {expected_id}", ok, detail))

    # ── 3. Prerequisite look-ups ──────────────────────────────────────────────
    # Python (1) must have prerequisites leading to at least Machine Learning (21)
    prereqs_of_ml = [
        r["from_skill_id"] for r in conn.execute(
            "SELECT from_skill_id FROM skill_prerequisites"
            " WHERE to_skill_id = 21 AND relation_type = 'prerequisite'"
        ).fetchall()
    ]
    results.append(("Python (1) is a prerequisite of Machine Learning (21)",
                    1 in prereqs_of_ml, ""))

    # No self-loops
    self_loops = conn.execute(
        "SELECT COUNT(*) FROM skill_prerequisites WHERE from_skill_id = to_skill_id"
    ).fetchone()[0]
    results.append(("No self-loop prerequisites", self_loops == 0,
                    f"found {self_loops} self-loops"))

    # ── 4. Career requirement validity ────────────────────────────────────────
    invalid_range = conn.execute(
        "SELECT COUNT(*) FROM career_skill_requirements"
        " WHERE importance NOT BETWEEN 1 AND 5"
        "   OR minimum_proficiency NOT BETWEEN 1 AND 5"
        "   OR preferred_proficiency NOT BETWEEN 1 AND 5"
    ).fetchone()[0]
    results.append(("All importance/proficiency values in 1–5 range",
                    invalid_range == 0,
                    f"{invalid_range} out-of-range rows"))

    # min_proficiency ≤ preferred_proficiency
    inverted = conn.execute(
        "SELECT COUNT(*) FROM career_skill_requirements"
        " WHERE minimum_proficiency > preferred_proficiency"
    ).fetchone()[0]
    results.append(("min_proficiency ≤ preferred_proficiency everywhere",
                    inverted == 0,
                    f"{inverted} inverted rows"))

    # ── 5. Every career has at least one essential skill (importance=5) ────────
    careers_no_essential = conn.execute(
        "SELECT c.name FROM careers c"
        " LEFT JOIN career_skill_requirements csr"
        "   ON c.career_id = csr.career_id AND csr.importance = 5"
        " WHERE csr.career_id IS NULL"
    ).fetchall()
    results.append(("Every career has ≥1 essential skill (importance=5)",
                    len(careers_no_essential) == 0,
                    str([r[0] for r in careers_no_essential])))

    conn.close()

    # ── Print results ─────────────────────────────────────────────────────────
    print("=" * 70)
    print("SkillForge AI — db/query_test.py")
    print("=" * 70)
    all_ok = True
    for label, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}" + (f"  ← {detail}" if detail else ""))
        all_ok = all_ok and ok
    print("=" * 70)
    print(f"OVERALL: {'ALL PASS' if all_ok else 'SOME FAILURES — see above'}")
    print("=" * 70)
    return all_ok


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
