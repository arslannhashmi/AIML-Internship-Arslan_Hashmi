"""Weighted skill-vector construction and cosine similarity.

The recommendation representation uses one dimension per canonical skill:

* a learner value is ``proficiency / 5`` multiplied by that career's
  importance weight;
* a career target value is ``preferred_proficiency / 5`` multiplied by the
  same importance weight.

Using the same importance weights on both vectors makes essential skills
contribute more strongly while preserving a standard cosine-similarity score.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def normalize_skill_profile(profile) -> dict[int, float]:
    """Return ``skill_id -> proficiency`` from common profile shapes.

    Profiles may be mappings such as ``{1: 5, 21: 3}``, or sequences of
    ``{"skill_id": 1, "proficiency": 5}`` records. Missing skills are
    represented by zero later, not by a fabricated proficiency.
    """
    if isinstance(profile, Mapping):
        items = profile.items()
    else:
        items = []
        for item in profile:
            if isinstance(item, Mapping):
                items.append((item["skill_id"], item["proficiency"]))
            else:
                skill_id, proficiency = item
                items.append((skill_id, proficiency))

    normalized: dict[int, float] = {}
    for raw_skill_id, raw_proficiency in items:
        skill_id = int(raw_skill_id)
        proficiency = float(raw_proficiency)
        if not 0 <= proficiency <= 5:
            raise ValueError(
                f"Proficiency for skill_id {skill_id} must be between 0 and 5"
            )
        normalized[skill_id] = proficiency
    return normalized


def normalize_requirements(requirements) -> dict[int, dict[str, float]]:
    """Normalize career requirements into a skill-indexed dictionary."""
    normalized: dict[int, dict[str, float]] = {}
    for requirement in requirements:
        if isinstance(requirement, Mapping):
            skill_id = int(requirement["skill_id"])
            importance = float(requirement["importance"])
            preferred = float(requirement["preferred_proficiency"])
        else:
            skill_id, importance, preferred = requirement
            skill_id = int(skill_id)
            importance = float(importance)
            preferred = float(preferred)
        if not 1 <= importance <= 5:
            raise ValueError(f"Importance for skill_id {skill_id} must be between 1 and 5")
        if not 1 <= preferred <= 5:
            raise ValueError(
                f"Preferred proficiency for skill_id {skill_id} must be between 1 and 5"
            )
        normalized[skill_id] = {
            "importance": importance,
            "preferred_proficiency": preferred,
        }
    return normalized


def build_weighted_profile_vector(
    profile,
    skill_ids: Sequence[int],
    *,
    weights: Mapping[int, float] | None = None,
) -> list[float]:
    """Build a weighted learner vector in the supplied skill-id order."""
    values = normalize_skill_profile(profile)
    weights = weights or {}
    return [
        (values.get(int(skill_id), 0.0) / 5.0) * float(weights.get(int(skill_id), 0.0))
        for skill_id in skill_ids
    ]


def build_weighted_career_vector(
    requirements,
    skill_ids: Sequence[int],
) -> list[float]:
    """Build a weighted target vector in the supplied skill-id order."""
    normalized = normalize_requirements(requirements)
    return [
        (
            normalized.get(int(skill_id), {}).get("preferred_proficiency", 0.0)
            / 5.0
        )
        * normalized.get(int(skill_id), {}).get("importance", 0.0)
        for skill_id in skill_ids
    ]


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity, with a defined zero-vector result of 0."""
    if len(left) != len(right):
        raise ValueError("Cosine vectors must have the same dimensionality")
    numerator = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) ** 2 for value in left))
    right_norm = math.sqrt(sum(float(value) ** 2 for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)