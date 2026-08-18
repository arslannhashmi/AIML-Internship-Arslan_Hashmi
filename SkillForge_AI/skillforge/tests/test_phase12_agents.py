"""Phase 12 tests for deterministic wrappers and orchestration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agent.career_agent import career_agent  # noqa: E402
from agent.learning_agent import learning_agent  # noqa: E402
from agent.orchestrator import PIPELINE_SEQUENCE, orchestrate  # noqa: E402
from agent.profile_agent import profile_agent  # noqa: E402
from agent.progress_agent import progress_agent  # noqa: E402
from agent.skill_gap_agent import skill_gap_agent  # noqa: E402
from db.db_client import get_connection  # noqa: E402
from knowledge_base.skill_graph import SkillGraph  # noqa: E402


FRONTEND_PROFILE = {
    43: 5,  # HTML
    44: 5,  # CSS
    4: 5,   # JavaScript
    45: 5,  # React
    5: 4,   # TypeScript
    49: 4,  # Tailwind CSS
    80: 4,  # Git
    52: 3,  # Jest
}


def run() -> bool:
    checks = []
    conn = get_connection()
    try:
        profile_stage = profile_agent(FRONTEND_PROFILE)
        career_stage = career_agent(profile_stage, conn=conn, top_k=3)
        gap_stage = skill_gap_agent(profile_stage, career_stage, conn=conn)
        learning_stage = learning_agent(
            gap_stage,
            graph=SkillGraph(conn=conn),
        )
        progress_stage = progress_agent(profile_stage, gap_stage)

        checks.append((
            "profile_agent returns sorted JSON-friendly skills",
            profile_stage["stage"] == "profile"
            and profile_stage["skills"][0] == {"skill_id": 4, "proficiency": 5},
            profile_stage,
        ))
        checks.append((
            "career_agent selects Frontend Developer",
            career_stage["stage"] == "career"
            and career_stage["selected_career"]["career_id"] == 4,
            career_stage["selected_career"],
        ))
        checks.append((
            "skill_gap_agent targets the selected career",
            gap_stage["stage"] == "gap"
            and gap_stage["career_id"] == 4
            and len(gap_stage["gaps"]) == 8,
            gap_stage,
        ))
        checks.append((
            "learning_agent returns a deterministic path",
            learning_stage["stage"] == "learning"
            and learning_stage["career_id"] == 4
            and isinstance(learning_stage["learning_path"], list),
            learning_stage,
        ))
        checks.append((
            "progress_agent reports full minimum coverage",
            progress_stage["stage"] == "progress"
            and progress_stage["skills_at_minimum"] == 8
            and progress_stage["minimum_coverage"] == 1.0,
            progress_stage,
        ))

        final_output = orchestrate(FRONTEND_PROFILE, conn=conn, top_k=3)
        json.dumps(final_output)
        checks.append((
            "orchestrator uses the required four-stage sequence",
            final_output["sequence"] == list(PIPELINE_SEQUENCE)
            and list(final_output) == [
                "pipeline",
                "pipeline_version",
                "sequence",
                "profile",
                "career",
                "skill_gap",
                "learning",
                "progress",
            ],
            final_output["sequence"],
        ))
        checks.append((
            "orchestrator bundles all five deterministic agent outputs",
            set(final_output) >= {
                "profile", "career", "skill_gap", "learning", "progress"
            }
            and final_output["career"]["selected_career"]["career_id"] == 4,
            final_output.keys(),
        ))
        checks.append((
            "orchestrator has no LLM explanation stage",
            "llm" not in json.dumps(final_output).lower()
            and "explanation" not in final_output,
            None,
        ))
    finally:
        conn.close()

    for label, ok, detail in checks:
        suffix = f"  ({detail})" if not ok else ""
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}{suffix}")
    passed = sum(ok for _, ok, _ in checks)
    print(f"\nPhase 12 agent results: {passed}/{len(checks)} passed")
    return passed == len(checks)


if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)