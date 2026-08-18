"""Content-based career recommender using weighted skill-vector cosine scores."""

from __future__ import annotations

from collections.abc import Mapping

from db.db_client import get_connection
from recommendation.vectorizer import (
    build_weighted_career_vector,
    build_weighted_profile_vector,
    cosine_similarity,
)


def _row_value(row, key: str, index: int):
    return row[key] if hasattr(row, "keys") else row[index]


class ContentBasedRecommender:
    """Rank the seeded careers against a learner's skill profile."""

    def __init__(self, *, conn=None):
        self._owns_connection = conn is None
        self.conn = conn or get_connection()
        try:
            self.skill_ids = [
                int(_row_value(row, "skill_id", 0))
                for row in self.conn.execute("SELECT skill_id FROM skills ORDER BY skill_id")
            ]
            self.careers = self._load_careers()
        except Exception:
            if self._owns_connection:
                self.conn.close()
            raise

    def close(self) -> None:
        if self._owns_connection and self.conn is not None:
            self.conn.close()
            self.conn = None

    def _load_careers(self) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT c.career_id, c.name AS career_name, c.description,
                   csr.skill_id, s.name AS skill_name,
                   csr.importance, csr.minimum_proficiency,
                   csr.preferred_proficiency
            FROM careers c
            JOIN career_skill_requirements csr ON csr.career_id = c.career_id
            JOIN skills s ON s.skill_id = csr.skill_id
            ORDER BY c.career_id, csr.skill_id
            """
        ).fetchall()
        careers: dict[int, dict] = {}
        for row in rows:
            career_id = int(_row_value(row, "career_id", 0))
            career = careers.setdefault(
                career_id,
                {
                    "career_id": career_id,
                    "career_name": _row_value(row, "career_name", 1),
                    "description": _row_value(row, "description", 2),
                    "requirements": [],
                },
            )
            career["requirements"].append(
                {
                    "skill_id": int(_row_value(row, "skill_id", 3)),
                    "skill_name": _row_value(row, "skill_name", 4),
                    "importance": int(_row_value(row, "importance", 5)),
                    "minimum_proficiency": int(_row_value(row, "minimum_proficiency", 6)),
                    "preferred_proficiency": int(
                        _row_value(row, "preferred_proficiency", 7)
                    ),
                }
            )
        return list(careers.values())

    def recommend(self, profile, *, top_k: int | None = None) -> list[dict]:
        """Return career rankings with deterministic ID tie-breaking."""
        if top_k is not None and top_k < 1:
            raise ValueError("top_k must be positive when provided")

        results = []
        for career in self.careers:
            weights = {
                int(requirement["skill_id"]): float(requirement["importance"])
                for requirement in career["requirements"]
            }
            learner_vector = build_weighted_profile_vector(
                profile, self.skill_ids, weights=weights
            )
            career_vector = build_weighted_career_vector(
                career["requirements"], self.skill_ids
            )
            matched = [
                requirement["skill_id"]
                for requirement in career["requirements"]
                if float(
                    profile.get(requirement["skill_id"], 0)
                    if isinstance(profile, Mapping)
                    else next(
                        (
                            item["proficiency"]
                            for item in profile
                            if item["skill_id"] == requirement["skill_id"]
                        ),
                        0,
                    )
                )
                > 0
            ]
            results.append(
                {
                    "career_id": career["career_id"],
                    "career_name": career["career_name"],
                    "score": cosine_similarity(learner_vector, career_vector),
                    "matched_skill_ids": sorted(matched),
                    "required_skill_count": len(career["requirements"]),
                }
            )

        results.sort(key=lambda result: (-result["score"], result["career_id"]))
        return results if top_k is None else results[:top_k]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def recommend_careers(profile, *, conn=None, top_k: int | None = None) -> list[dict]:
    """Convenience wrapper for one recommendation call."""
    recommender = ContentBasedRecommender(conn=conn)
    try:
        return recommender.recommend(profile, top_k=top_k)
    finally:
        recommender.close()