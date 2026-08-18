"""Thin deterministic prerequisite-aware learning-path wrapper."""

from __future__ import annotations

from knowledge_base.skill_graph import SkillGraph
from learning_path.learning_path import plan_learning_path


def learning_agent(gap_stage, *, conn=None, graph=None) -> dict:
    """Order the gap stage's missing skills through the Phase 8 graph."""
    owns_graph = graph is None
    skill_graph = graph or SkillGraph(conn=conn)
    try:
        learning_path = plan_learning_path(gap_stage, skill_graph)
        return {
            "stage": "learning",
            "career_id": gap_stage["career_id"],
            "career_name": gap_stage["career_name"],
            "learning_path": learning_path,
            "skill_count": len(learning_path),
        }
    finally:
        # SkillGraph closes connections it opens during construction. This
        # branch documents that the wrapper does not own a caller-supplied
        # graph or connection.
        if owns_graph:
            pass


run_learning_agent = learning_agent