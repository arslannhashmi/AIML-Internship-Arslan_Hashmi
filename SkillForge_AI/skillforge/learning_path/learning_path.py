"""Order missing skills with prerequisite constraints and gap-score priorities."""

from __future__ import annotations

import heapq
from collections.abc import Mapping, Sequence

from knowledge_base.skill_graph import SkillGraph


def _gap_entry_values(missing_skills) -> tuple[set[int], dict[int, float], dict[int, dict]]:
    skill_ids: set[int] = set()
    scores: dict[int, float] = {}
    details: dict[int, dict] = {}
    for item in missing_skills:
        if isinstance(item, Mapping):
            skill_id = int(item["skill_id"])
            score = float(item.get("gap_score", 0.0))
            details[skill_id] = dict(item)
        else:
            skill_id = int(item)
            score = 0.0
        skill_ids.add(skill_id)
        scores[skill_id] = score
    return skill_ids, scores, details


def order_missing_skill_ids(missing_skills, graph: SkillGraph) -> list[int]:
    """Return a Kahn topological order, preferring larger gaps when unlocked."""
    selected, scores, _ = _gap_entry_values(missing_skills)
    unknown = selected - set(graph.graph.nodes)
    if unknown:
        raise ValueError(f"Unknown skill_ids: {sorted(unknown)}")

    indegree = {
        skill_id: sum(1 for prerequisite in graph.graph.predecessors(skill_id)
                      if prerequisite in selected)
        for skill_id in selected
    }
    ready = [(-scores[skill_id], skill_id) for skill_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    ordered: list[int] = []

    while ready:
        _, skill_id = heapq.heappop(ready)
        ordered.append(skill_id)
        for dependent in graph.graph.successors(skill_id):
            if dependent not in indegree:
                continue
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, (-scores[dependent], dependent))

    if len(ordered) != len(selected):
        raise ValueError("Cannot build learning path because the selected skills contain a cycle")
    return ordered


def build_learning_path(missing_skills, graph: SkillGraph) -> list[dict]:
    """Return missing-skill gap records in prerequisite-safe learning order."""
    _, _, details = _gap_entry_values(missing_skills)
    ordered_ids = order_missing_skill_ids(missing_skills, graph)
    return [details.get(skill_id, {"skill_id": skill_id}) for skill_id in ordered_ids]


def plan_learning_path(gap_analysis: Mapping, graph: SkillGraph) -> list[dict]:
    """Plan directly from the ``GapAnalyzer.analyze`` result."""
    return build_learning_path(gap_analysis["missing_skills"], graph)