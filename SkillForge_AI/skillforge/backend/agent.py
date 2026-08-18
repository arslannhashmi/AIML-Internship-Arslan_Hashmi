"""Full deterministic Phase 12 orchestration endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from agent.orchestrator import orchestrate

from backend.dependencies import get_db, get_user_with_profile
from backend.schemas import AgentRunResponse


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/{user_id}/run", response_model=AgentRunResponse)
def run_agent_pipeline(
    user_and_profile=Depends(get_user_with_profile),
    conn=Depends(get_db),
):
    """Return the Phase 12 structured result directly, without LLM narration."""
    _, profile = user_and_profile
    return orchestrate(profile, conn=conn)
