"""Checkpoint 3 tests: recommendation, gap analysis, and learning paths."""

from __future__ import annotations

import sys
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection  # noqa: E402
from gap_analysis.gap_analyzer import (  # noqa: E402
    analyze_gaps,
    bucket_for_gap_score,
    calculate_gap_score,
)
from knowledge_base.skill_graph import SkillGraph  # noqa: E402
from learning_path.learning_path import order_missing_skill_ids  # noqa: E402
from recommendation.content_based_recommender import ContentBasedRecommender  # noqa: E402
from recommendation.evaluate_recommender import (  # noqa: E402
    EVALUATION_LABEL,
    evaluate_face_validity,
)
from recommendation.vectorizer import cosine_similarity  # noqa: E402


def run() -> bool:
    conn = get_connection()
    checks = []
    try:
        checks.append(("identical vectors have cosine 1", math.isclose(cosine_similarity([1, 2], [1, 2]), 1.0), None))
        checks.append(("orthogonal vectors have cosine 0", cosine_similarity([1, 0], [0, 1]) == 0.0, None))

        recommender = ContentBasedRecommender(conn=conn)
        frontend = {43: 5, 44: 5, 4: 5, 45: 5, 5: 4, 49: 4, 80: 4, 52: 3}
        ranking = recommender.recommend(frontend, top_k=1)
        checks.append(("frontend profile ranks Frontend Developer first", ranking[0]["career_id"] == 4, ranking[0]))

        face_validity = evaluate_face_validity(conn=conn)
        checks.append((
            "hand-built recommender checks are face-validity tests",
            face_validity["evaluation_type"] == EVALUATION_LABEL
            and face_validity["passed"] == face_validity["total"] == 3,
            face_validity,
        ))

        checks.append(("gap score uses importance × deficit", calculate_gap_score(4, 2, 4) == 8.0, None))
        checks.append(("gap buckets cover required labels", [
            bucket_for_gap_score(score) for score in [0, 1, 6, 11, 16]
        ] == ["Strong", "Minor", "Moderate", "Major", "Critical"], None))

        profile_records = [
            {"skill_id": 4, "proficiency": 5},
            {"skill_id": 5, "proficiency": 4},
            {"skill_id": 43, "proficiency": 5},
            {"skill_id": 44, "proficiency": 5},
            {"skill_id": 45, "proficiency": 5},
            {"skill_id": 49, "proficiency": 4},
            {"skill_id": 52, "proficiency": 3},
            {"skill_id": 80, "proficiency": 4},
        ]
        record_gap = analyze_gaps(profile_records, 4, conn=conn)
        record_by_id = {gap["skill_id"]: gap for gap in record_gap["gaps"]}
        checks.append((
            "gap analysis preserves proficiency from extracted skill records",
            record_by_id[4]["current_proficiency"] == 5.0
            and record_by_id[4]["gap_score"] == 0.0
            and record_by_id[52]["current_proficiency"] == 3.0
            and record_by_id[52]["gap_score"] == 0.0,
            record_by_id,
        ))

        gap_report = analyze_gaps({1: 5, 21: 3, 27: 2}, 1, conn=conn)
        stats_gap = next(gap for gap in gap_report["gaps"] if gap["skill_id"] == 27)
        checks.append(("gap report computes Statistics as Major", stats_gap["gap_score"] == 15.0 and stats_gap["bucket"] == "Major", stats_gap))

        graph = SkillGraph(conn=conn)
        ordered = order_missing_skill_ids([
            {"skill_id": 1, "gap_score": 1},
            {"skill_id": 21, "gap_score": 20},
            {"skill_id": 22, "gap_score": 10},
        ], graph)
        checks.append(("learning path respects prerequisites before gap priority", ordered == [1, 21, 22], ordered))
    finally:
        conn.close()

    for label, ok, detail in checks:
        suffix = f"  ({detail})" if not ok else ""
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}{suffix}")
    passed = sum(ok for _, ok, _ in checks)
    print(f"\nCheckpoint 3 results: {passed}/{len(checks)} passed")
    return passed == len(checks)


if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)