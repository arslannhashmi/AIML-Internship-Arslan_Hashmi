"""Deterministic Phase 12 pipeline orchestrator.

The returned dictionary is the final pipeline output. It is intentionally
JSON-serializable and contains no generated explanation or LLM-derived field.
"""

from __future__ import annotations

import json

from db.db_client import get_connection
from knowledge_base.skill_graph import SkillGraph

from agent.career_agent import career_agent
from agent.learning_agent import learning_agent
from agent.profile_agent import profile_agent
from agent.progress_agent import progress_agent
from agent.skill_gap_agent import skill_gap_agent


PIPELINE_SEQUENCE = ("profile", "career", "gap", "learning")


def orchestrate(profile, *, conn=None, top_k: int = 5) -> dict:
    """Run profile → career → gap → learning and bundle structured results."""
    owns_connection = conn is None
    connection = conn or get_connection()
    try:
        profile_stage = profile_agent(profile)
        career_stage = career_agent(profile_stage, conn=connection, top_k=top_k)
        gap_stage = skill_gap_agent(profile_stage, career_stage, conn=connection)
        graph = SkillGraph(conn=connection)
        learning_stage = learning_agent(gap_stage, graph=graph)
        progress_stage = progress_agent(profile_stage, gap_stage)

        result = {
            "pipeline": "SkillForge AI",
            "pipeline_version": "phase12",
            "sequence": list(PIPELINE_SEQUENCE),
            "profile": profile_stage,
            "career": career_stage,
            "skill_gap": gap_stage,
            "learning": learning_stage,
            "progress": progress_stage,
        }
        # Fail at the boundary if a future wrapper introduces a non-JSON
        # object. This keeps the pipeline's public contract explicit.
        json.dumps(result)
        return result
    finally:
        if owns_connection:
            connection.close()


run_pipeline = orchestrate


if __name__ == "__main__":
    sample_profile = {
        43: 5,  # HTML
        44: 5,  # CSS
        4: 5,   # JavaScript
        45: 5,  # React
        5: 4,   # TypeScript
        49: 4,  # Tailwind CSS
        80: 4,  # Git
        52: 3,  # Jest
    }
    print(json.dumps(orchestrate(sample_profile), indent=2))