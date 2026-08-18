"""Career gap-analysis endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from gap_analysis.gap_analyzer import analyze_gaps

from backend.dependencies import get_db, get_user_with_profile
from backend.schemas import GapResponse


router = APIRouter(prefix="/gap", tags=["gap"])


@router.get("/{user_id}/{career_id}", response_model=GapResponse)
def get_gap_analysis(
    career_id: int,
    user_and_profile=Depends(get_user_with_profile),
    conn=Depends(get_db),
):
    user_id, profile = user_and_profile
    report = analyze_gaps(profile, career_id, conn=conn)
    return {"user_id": user_id, **report}
