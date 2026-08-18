"""Thin deterministic skill-gap wrapper."""

from __future__ import annotations

from gap_analysis.gap_analyzer import analyze_gaps

from agent._common import profile_skills, selected_career_id


def skill_gap_agent(profile_stage, career_stage, *, conn=None) -> dict:
    """Analyze the selected career's proficiency gaps."""
    report = analyze_gaps(
        profile_skills(profile_stage),
        selected_career_id(career_stage),
        conn=conn,
    )
    return {
        "stage": "gap",
        **report,
    }


run_skill_gap_agent = skill_gap_agent