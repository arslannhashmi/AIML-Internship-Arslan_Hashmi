"""Small adapters shared by the Phase 12 thin agent wrappers."""

from __future__ import annotations

from collections.abc import Mapping


def profile_skills(profile_or_stage):
    """Extract the JSON-friendly skill list from a raw or staged profile."""
    if isinstance(profile_or_stage, Mapping) and "skills" in profile_or_stage:
        return profile_or_stage["skills"]
    return profile_or_stage


def selected_career_id(career_stage) -> int:
    """Extract the deterministic top-career ID from the career stage."""
    selected = career_stage.get("selected_career") if isinstance(career_stage, Mapping) else None
    if selected is None:
        raise ValueError("Career stage does not contain a selected_career")
    return int(selected["career_id"])