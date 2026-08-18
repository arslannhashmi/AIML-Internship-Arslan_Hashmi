"""Career recommendation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from recommendation.content_based_recommender import ContentBasedRecommender

from backend.dependencies import get_db, get_user_with_profile
from backend.schemas import CareerRecommendationsResponse


router = APIRouter(prefix="/careers", tags=["careers"])


@router.get("/{user_id}/recommendations", response_model=CareerRecommendationsResponse)
def get_recommendations(
    user_and_profile=Depends(get_user_with_profile),
    top_k: int = Query(default=5, ge=1, le=15),
    conn=Depends(get_db),
):
    user_id, profile = user_and_profile
    recommendations = ContentBasedRecommender(conn=conn).recommend(
        profile,
        top_k=top_k,
    )
    for recommendation in recommendations:
        conn.execute(
            "INSERT INTO recommendations (user_id, career_id, score) VALUES (?, ?, ?)",
            (user_id, recommendation["career_id"], recommendation["score"]),
        )
    conn.commit()
    return {"user_id": user_id, "recommendations": recommendations}
