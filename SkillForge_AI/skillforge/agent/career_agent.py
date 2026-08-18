"""Thin deterministic career-recommendation wrapper."""

from __future__ import annotations

from recommendation.content_based_recommender import recommend_careers

from agent._common import profile_skills


def career_agent(profile_stage, *, conn=None, top_k: int = 5) -> dict:
    """Rank careers from the profile stage and select the top result."""
    recommendations = recommend_careers(
        profile_skills(profile_stage),
        conn=conn,
        top_k=top_k,
    )
    if not recommendations:
        raise ValueError("Career recommender returned no careers")
    return {
        "stage": "career",
        "recommendations": recommendations,
        "selected_career": recommendations[0],
    }


run_career_agent = career_agent