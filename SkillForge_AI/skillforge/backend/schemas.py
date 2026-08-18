"""Pydantic request and response models for the Phase 14 API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProfileSkill(BaseModel):
    skill_id: int
    canonical_name: str
    proficiency: int = Field(ge=1, le=5)
    source: str = "resume"
    matched_text: str | None = None
    section: str | None = None
    char_span: list[int] | None = None


class ProfileResponse(BaseModel):
    user_id: int
    resume_id: int
    skill_count: int
    skills: list[ProfileSkill]
    sections: list[str]


class CareerRecommendation(BaseModel):
    career_id: int
    career_name: str
    score: float
    matched_skill_ids: list[int]
    required_skill_count: int


class CareerRecommendationsResponse(BaseModel):
    user_id: int
    recommendations: list[CareerRecommendation]


class GapItem(BaseModel):
    skill_id: int
    skill_name: str
    importance: int
    current_proficiency: float
    minimum_proficiency: int
    preferred_proficiency: int
    proficiency_deficit: float
    gap_score: float
    bucket: str


class GapResponse(BaseModel):
    user_id: int
    career_id: int
    career_name: str
    gaps: list[GapItem]
    missing_skills: list[GapItem]


class RoadmapResponse(BaseModel):
    user_id: int
    career_id: int
    career_name: str
    learning_path: list[GapItem]
    skill_count: int


class AgentRunResponse(BaseModel):
    """The Phase 12 structured result, with no generated explanation field."""

    model_config = ConfigDict(extra="allow")

    pipeline: str
    pipeline_version: str
    sequence: list[str]
    profile: dict[str, Any]
    career: dict[str, Any]
    skill_gap: dict[str, Any]
    learning: dict[str, Any]
    progress: dict[str, Any]
