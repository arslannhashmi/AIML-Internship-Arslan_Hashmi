"""Thin deterministic progress-summary wrapper."""

from __future__ import annotations

from agent._common import profile_skills
from recommendation.vectorizer import normalize_skill_profile


def progress_agent(profile_stage, gap_stage) -> dict:
    """Summarize current, minimum-target, and preferred-target coverage."""
    profile = normalize_skill_profile(profile_skills(profile_stage))
    gaps = gap_stage["gaps"]
    required_count = len(gaps)
    minimum_met = sum(
        profile.get(gap["skill_id"], 0.0) >= gap["minimum_proficiency"]
        for gap in gaps
    )
    preferred_met = sum(
        profile.get(gap["skill_id"], 0.0) >= gap["preferred_proficiency"]
        for gap in gaps
    )
    return {
        "stage": "progress",
        "career_id": gap_stage["career_id"],
        "career_name": gap_stage["career_name"],
        "required_skill_count": required_count,
        "skills_at_minimum": minimum_met,
        "skills_at_preferred": preferred_met,
        "minimum_coverage": minimum_met / required_count if required_count else 0.0,
        "preferred_coverage": preferred_met / required_count if required_count else 0.0,
        "remaining_gap_score": sum(gap["gap_score"] for gap in gaps),
    }


run_progress_agent = progress_agent