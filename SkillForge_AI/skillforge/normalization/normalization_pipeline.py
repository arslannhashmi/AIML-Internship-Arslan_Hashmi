"""Alias → fuzzy → calibrated Sentence-BERT normalization chain."""

from __future__ import annotations

import json
from pathlib import Path

from normalization.alias_matcher import match_alias
from normalization.fuzzy_matcher import match_fuzzy
from normalization.semantic_matcher import SemanticMatcher


DEFAULT_THRESHOLD_PATH = (
    Path(__file__).resolve().parent.parent / "evaluation" / "phase7_threshold_calibration.json"
)


class SkillNormalizer:
    def __init__(self, *, conn=None, semantic_threshold: float | None = None):
        self.conn = conn
        self.semantic = None
        self.semantic_threshold = semantic_threshold

    def _semantic_matcher(self) -> SemanticMatcher:
        if self.semantic is None:
            self.semantic = SemanticMatcher(conn=self.conn)
            if self.semantic_threshold is None:
                if DEFAULT_THRESHOLD_PATH.exists():
                    data = json.loads(DEFAULT_THRESHOLD_PATH.read_text(encoding="utf-8"))
                    self.semantic_threshold = float(data["chosen_threshold"])
                else:
                    raise FileNotFoundError(
                        "Run normalization/threshold_calibration.py before semantic normalization"
                    )
        return self.semantic

    def resolve(self, raw_text: str) -> dict | None:
        exact = match_alias(raw_text, conn=self.conn)
        if exact:
            return exact
        fuzzy = match_fuzzy(raw_text, conn=self.conn)
        if fuzzy:
            return fuzzy
        return self._semantic_matcher().match(
            raw_text, threshold=float(self.semantic_threshold)
        )

    def resolve_many(self, raw_texts: list[str]) -> list[dict]:
        results = []
        seen = set()
        for raw_text in raw_texts:
            result = self.resolve(raw_text)
            if result and result["skill_id"] not in seen:
                results.append(result)
                seen.add(result["skill_id"])
        return results