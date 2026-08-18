"""Face-validity checks for the content-based recommender.

These are hand-built illustrative profiles, not a representative dataset.
They test whether obvious profiles produce plausible top-ranked careers.
This module deliberately does not claim accuracy, precision, recall, or
generalization.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection
from recommendation.content_based_recommender import ContentBasedRecommender


EVALUATION_LABEL = "face-validity testing (not accuracy evaluation)"

HAND_BUILT_PROFILES = [
    {
        "name": "data-science profile",
        "expected_career_id": 1,
        "skills": {1: 5, 21: 5, 27: 5, 14: 4, 15: 4, 33: 4, 30: 4, 25: 4},
    },
    {
        "name": "frontend profile",
        "expected_career_id": 4,
        "skills": {43: 5, 44: 5, 4: 5, 45: 5, 5: 4, 49: 4, 80: 4, 52: 3},
    },
    {
        "name": "devops profile",
        "expected_career_id": 7,
        "skills": {65: 5, 66: 5, 71: 5, 74: 5, 67: 4, 68: 4, 80: 4, 11: 4},
    },
]


def evaluate_face_validity(*, conn=None) -> dict:
    """Run the hand-built plausibility checks and return structured results."""
    owns_connection = conn is None
    connection = conn or get_connection()
    try:
        recommender = ContentBasedRecommender(conn=connection)
        results = []
        for case in HAND_BUILT_PROFILES:
            ranking = recommender.recommend(case["skills"], top_k=3)
            top = ranking[0]
            passed = top["career_id"] == case["expected_career_id"]
            results.append(
                {
                    "profile": case["name"],
                    "expected_career_id": case["expected_career_id"],
                    "top_career_id": top["career_id"],
                    "top_career_name": top["career_name"],
                    "top_score": top["score"],
                    "passed": passed,
                }
            )
        return {
            "evaluation_type": EVALUATION_LABEL,
            "results": results,
            "passed": sum(result["passed"] for result in results),
            "total": len(results),
        }
    finally:
        if owns_connection:
            connection.close()


def run() -> bool:
    report = evaluate_face_validity()
    print(f"Recommendation evaluation: {report['evaluation_type']}")
    for result in report["results"]:
        print(
            f"  [{'PASS' if result['passed'] else 'FAIL'}] {result['profile']} → "
            f"{result['top_career_name']} (score={result['top_score']:.4f})"
        )
    print(f"Face-validity results: {report['passed']}/{report['total']} passed")
    return report["passed"] == report["total"]


if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)