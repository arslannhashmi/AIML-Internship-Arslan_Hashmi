"""Career gap scoring.

Gap score is explicitly:

    importance × max(preferred_proficiency - current_proficiency, 0)

An omitted skill has current proficiency zero. Because importance and
proficiency both use a 1–5 scale, the maximum possible gap score is 25.
Bucket thresholds use that range so a score is not labelled Critical merely
because it is above the midpoint.
"""

from __future__ import annotations

from db.db_client import get_connection
from recommendation.vectorizer import normalize_skill_profile


GAP_BUCKETS = (
    ("Strong", 0, 0),
    ("Minor", 1, 5),
    ("Moderate", 6, 10),
    ("Major", 11, 15),
    ("Critical", 16, float("inf")),
)


def bucket_for_gap_score(gap_score: float) -> str:
    """Map a non-negative gap score to Strong/Minor/Moderate/Major/Critical."""
    if gap_score < 0:
        raise ValueError("gap_score must be non-negative")
    for label, minimum, maximum in GAP_BUCKETS:
        if minimum <= gap_score <= maximum:
            return label
    raise ValueError(f"Unsupported gap_score: {gap_score}")


def calculate_gap_score(importance: int, current_proficiency: float, preferred_proficiency: int) -> float:
    """Calculate importance-weighted proficiency deficit."""
    deficit = max(float(preferred_proficiency) - float(current_proficiency), 0.0)
    return float(importance) * deficit


def _row_value(row, key: str, index: int):
    return row[key] if hasattr(row, "keys") else row[index]


class GapAnalyzer:
    """Analyze all required skills for one seeded career."""

    def __init__(self, *, conn=None):
        self._owns_connection = conn is None
        self.conn = conn or get_connection()

    def close(self) -> None:
        if self._owns_connection and self.conn is not None:
            self.conn.close()
            self.conn = None

    def analyze(self, profile, career_id: int) -> dict:
        profile_values = normalize_skill_profile(profile)
        rows = self.conn.execute(
            """
            SELECT c.career_id, c.name AS career_name,
                   csr.skill_id, s.name AS skill_name,
                   csr.importance, csr.minimum_proficiency,
                   csr.preferred_proficiency
            FROM careers c
            JOIN career_skill_requirements csr ON csr.career_id = c.career_id
            JOIN skills s ON s.skill_id = csr.skill_id
            WHERE c.career_id = ?
            ORDER BY csr.skill_id
            """,
            (int(career_id),),
        ).fetchall()
        if not rows:
            raise ValueError(f"Unknown career_id: {career_id}")

        gaps = []
        for row in rows:
            skill_id = int(_row_value(row, "skill_id", 2))
            current = profile_values.get(skill_id, 0.0)
            preferred = int(_row_value(row, "preferred_proficiency", 6))
            importance = int(_row_value(row, "importance", 4))
            deficit = max(preferred - current, 0.0)
            gap_score = calculate_gap_score(importance, current, preferred)
            gaps.append(
                {
                    "skill_id": skill_id,
                    "skill_name": _row_value(row, "skill_name", 3),
                    "importance": importance,
                    "current_proficiency": current,
                    "minimum_proficiency": int(_row_value(row, "minimum_proficiency", 5)),
                    "preferred_proficiency": preferred,
                    "proficiency_deficit": deficit,
                    "gap_score": gap_score,
                    "bucket": bucket_for_gap_score(gap_score),
                }
            )

        return {
            "career_id": int(_row_value(rows[0], "career_id", 0)),
            "career_name": _row_value(rows[0], "career_name", 1),
            "gaps": gaps,
            "missing_skills": [gap for gap in gaps if gap["gap_score"] > 0],
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def analyze_gaps(profile, career_id: int, *, conn=None) -> dict:
    """Convenience wrapper for one career gap analysis."""
    analyzer = GapAnalyzer(conn=conn)
    try:
        return analyzer.analyze(profile, career_id)
    finally:
        analyzer.close()