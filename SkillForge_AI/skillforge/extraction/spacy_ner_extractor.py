"""
SkillForge AI — Phase 6: Stage 2 spaCy EntityRuler extractor.

The ruler uses the same canonical skills and aliases as the Phase 5 matcher.
It is deliberately deterministic: spaCy validates the NER pipeline and does
not introduce an untrained statistical model.
"""

from __future__ import annotations

import sys
from pathlib import Path

import spacy

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection  # noqa: E402
from extraction.dictionary_matcher import _load_skill_lookup  # noqa: E402


def build_entity_ruler(conn=None):
    """Build a blank English pipeline containing the database-backed ruler."""
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        lookup = _load_skill_lookup(conn)
        nlp = spacy.blank("en")
        ruler = nlp.add_pipe("entity_ruler", config={"phrase_matcher_attr": "LOWER"})
        patterns = [
            {
                "label": "SKILL",
                "pattern": term,
                "id": str(skill_id),
            }
            for term, (skill_id, _canonical) in sorted(
                lookup.items(), key=lambda item: len(item[0]), reverse=True
            )
        ]
        ruler.add_patterns(patterns)
        return nlp
    finally:
        if own_conn:
            conn.close()


def extract_skills(
    sections: dict[str, str],
    *,
    conn=None,
    deduplicate_globally: bool = True,
) -> list[dict]:
    """Return Stage 2 matches in the same schema as dictionary_matcher."""
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        lookup = _load_skill_lookup(conn)
        nlp = build_entity_ruler(conn=conn)
        results = []
        seen: set[int] = set()
        for section, text in sections.items():
            if not text.strip():
                continue
            doc = nlp(text)
            for ent in doc.ents:
                try:
                    skill_id = int(ent.ent_id_)
                except (TypeError, ValueError):
                    continue
                if deduplicate_globally and skill_id in seen:
                    continue
                canonical = lookup.get(ent.text.lower(), (skill_id, ent.text))[1]
                results.append({
                    "skill_id": skill_id,
                    "matched_text": ent.text,
                    "canonical_name": canonical,
                    "section": section,
                    "char_span": (ent.start_char, ent.end_char),
                })
                seen.add(skill_id)
        return results
    finally:
        if own_conn:
            conn.close()


if __name__ == "__main__":
    sample = {"skills": "Python, ML, ReactJS, K8s, Postgres, CI/CD"}
    print(extract_skills(sample))