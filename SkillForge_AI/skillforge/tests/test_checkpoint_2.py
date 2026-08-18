"""Checkpoint 2 tests: normalization chain and prerequisite graph."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection  # noqa: E402
from knowledge_base.skill_graph import SkillGraph  # noqa: E402
from normalization.alias_matcher import match_alias  # noqa: E402
from normalization.fuzzy_matcher import match_fuzzy  # noqa: E402
from normalization.normalization_pipeline import SkillNormalizer  # noqa: E402


def run() -> bool:
    conn = get_connection()
    checks = []
    try:
        for raw, expected in [
            ("ML", "Machine Learning"),
            ("Machine-Learning", "Machine Learning"),
            ("ReactJS", "React"),
        ]:
            result = match_alias(raw, conn=conn)
            ok = result is not None and result["canonical_name"] == expected
            checks.append((f"alias '{raw}' → {expected}", ok, result))
        fuzzy = match_fuzzy("Pythn", conn=conn)
        checks.append(("fuzzy 'Pythn' → Python", fuzzy is not None and fuzzy["canonical_name"] == "Python", fuzzy))
        semantic = SkillNormalizer(conn=conn, semantic_threshold=0.3323).resolve("data plotting")
        checks.append(("semantic 'data plotting' → Data Visualization", semantic is not None and semantic["canonical_name"] == "Data Visualization" and semantic["method"] == "semantic", semantic))
        graph = SkillGraph(conn=conn)
        python_id = conn.execute("SELECT skill_id FROM skills WHERE name='Python'").fetchone()[0]
        ml_id = conn.execute("SELECT skill_id FROM skills WHERE name='Machine Learning'").fetchone()[0]
        checks.append(("Machine Learning has Python prerequisite", python_id in graph.get_prerequisites(ml_id), graph.get_prerequisites(ml_id)))
        checks.append(("skill graph has_cycle() is False", graph.has_cycle() is False, graph.graph.number_of_edges()))
        order = graph.topological_order([python_id, ml_id])
        checks.append(("topological order puts Python before Machine Learning", order == [python_id, ml_id], order))
    finally:
        conn.close()
    for label, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if not ok else ""))
    passed = sum(ok for _, ok, _ in checks)
    print(f"\nCheckpoint 2 deterministic results: {passed}/{len(checks)} passed")
    return passed == len(checks)


if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)