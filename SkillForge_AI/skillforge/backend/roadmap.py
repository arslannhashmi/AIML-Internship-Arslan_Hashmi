"""Prerequisite-aware learning-roadmap endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from gap_analysis.gap_analyzer import analyze_gaps
from knowledge_base.skill_graph import SkillGraph
from learning_path.learning_path import plan_learning_path

from backend.dependencies import get_db, get_user_with_profile
from backend.schemas import RoadmapResponse


router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get("/{user_id}/{career_id}", response_model=RoadmapResponse)
def get_roadmap(
    career_id: int,
    user_and_profile=Depends(get_user_with_profile),
    conn=Depends(get_db),
):
    user_id, profile = user_and_profile
    gap_report = analyze_gaps(profile, career_id, conn=conn)
    learning_path = plan_learning_path(gap_report, SkillGraph(conn=conn))
    return {
        "user_id": user_id,
        "career_id": gap_report["career_id"],
        "career_name": gap_report["career_name"],
        "learning_path": learning_path,
        "skill_count": len(learning_path),
    }
