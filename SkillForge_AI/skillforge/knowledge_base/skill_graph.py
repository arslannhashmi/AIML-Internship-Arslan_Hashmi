"""NetworkX wrapper over the database's prerequisite relationships."""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection  # noqa: E402


class SkillGraph:
    """In-memory directed graph where prerequisite → dependent."""

    def __init__(self, conn=None):
        own_conn = conn is None
        if own_conn:
            conn = get_connection()
        try:
            self.graph = nx.DiGraph()
            for row in conn.execute("SELECT skill_id, name FROM skills").fetchall():
                skill_id = row["skill_id"] if hasattr(row, "keys") else row[0]
                name = row["name"] if hasattr(row, "keys") else row[1]
                self.graph.add_node(int(skill_id), name=name)
            rows = conn.execute(
                "SELECT from_skill_id, to_skill_id FROM skill_prerequisites "
                "WHERE relation_type = 'prerequisite'"
            ).fetchall()
            for row in rows:
                source = row["from_skill_id"] if hasattr(row, "keys") else row[0]
                target = row["to_skill_id"] if hasattr(row, "keys") else row[1]
                self.graph.add_edge(int(source), int(target))
        finally:
            if own_conn:
                conn.close()

    def get_prerequisites(self, skill_id: int) -> list[int]:
        return sorted(self.graph.predecessors(int(skill_id)))

    def get_dependents(self, skill_id: int) -> list[int]:
        return sorted(self.graph.successors(int(skill_id)))

    def topological_order(self, skill_ids) -> list[int]:
        selected = {int(skill_id) for skill_id in skill_ids}
        unknown = selected - set(self.graph.nodes)
        if unknown:
            raise ValueError(f"Unknown skill_ids: {sorted(unknown)}")
        return list(nx.topological_sort(self.graph.subgraph(selected)))

    def has_cycle(self) -> bool:
        return not nx.is_directed_acyclic_graph(self.graph)


def build_skill_graph(conn=None) -> SkillGraph:
    return SkillGraph(conn=conn)


if __name__ == "__main__":
    graph = build_skill_graph()
    print(f"Nodes: {graph.graph.number_of_nodes()}")
    print(f"Prerequisite edges: {graph.graph.number_of_edges()}")
    print(f"has_cycle(): {graph.has_cycle()}")