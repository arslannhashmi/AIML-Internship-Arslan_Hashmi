"""
Sentence-BERT semantic fallback.

The sentence-transformers wrapper package is unavailable in this workspace's
package index, so this module uses its underlying Hugging Face checkpoint
directly: mean-pool the last hidden state from
sentence-transformers/all-MiniLM-L6-v2 and L2-normalize the embeddings.
"""

from __future__ import annotations

from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from normalization.alias_matcher import load_alias_index


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class SemanticMatcher:
    def __init__(self, *, conn=None, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        index = load_alias_index(conn)
        self.candidates = {}
        for item in index.values():
            self.candidates[item["skill_id"]] = item["canonical_name"]
        self.skill_ids = sorted(self.candidates)
        self.candidate_names = [self.candidates[skill_id] for skill_id in self.skill_ids]
        self.candidate_embeddings = self._encode(self.candidate_names)

    def _encode(self, texts: list[str]) -> torch.Tensor:
        encoded = self.tokenizer(
            texts, padding=True, truncation=True, max_length=64, return_tensors="pt"
        )
        with torch.no_grad():
            hidden = self.model(**encoded).last_hidden_state
        mask = encoded["attention_mask"].unsqueeze(-1).expand(hidden.size()).float()
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
        return F.normalize(pooled, p=2, dim=1)

    def score(self, raw_text: str) -> list[tuple[int, str, float]]:
        query = self._encode([raw_text])
        scores = torch.mm(query, self.candidate_embeddings.T)[0]
        ranked = torch.argsort(scores, descending=True).tolist()
        return [
            (self.skill_ids[index], self.candidate_names[index], float(scores[index]))
            for index in ranked
        ]

    def similarity(self, left: str, right: str) -> float:
        """Return the direct cosine similarity for a calibration pair."""
        embeddings = self._encode([left, right])
        return float(torch.mm(embeddings[0:1], embeddings[1:2].T)[0, 0])

    def match(self, raw_text: str, *, threshold: float) -> dict | None:
        if not raw_text.strip():
            return None
        skill_id, canonical, score = self.score(raw_text)[0]
        if score < threshold:
            return None
        return {
            "skill_id": skill_id,
            "canonical_name": canonical,
            "matched_text": raw_text,
            "method": "semantic",
            "confidence": round(score, 4),
            "cosine_similarity": round(score, 4),
            "model": self.model_name,
        }