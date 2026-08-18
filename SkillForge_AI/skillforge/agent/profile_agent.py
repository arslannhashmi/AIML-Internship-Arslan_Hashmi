"""Thin deterministic profile-stage wrapper."""

from __future__ import annotations

from recommendation.vectorizer import normalize_skill_profile


def profile_agent(profile) -> dict:
    """Normalize a profile into a JSON-friendly, sorted skill list."""
    normalized = normalize_skill_profile(profile)
    skills = [
        {
            "skill_id": skill_id,
            "proficiency": int(proficiency) if proficiency.is_integer() else proficiency,
        }
        for skill_id, proficiency in sorted(normalized.items())
    ]
    return {
        "stage": "profile",
        "skills": skills,
        "skill_count": len(skills),
    }


run_profile_agent = profile_agent