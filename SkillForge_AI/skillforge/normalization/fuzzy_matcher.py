"""RapidFuzz fallback for close spelling and formatting misses."""

from __future__ import annotations

from rapidfuzz import fuzz, process

from normalization.alias_matcher import load_alias_index, normalize_text


FUZZY_CUTOFF = 80.0


def match_fuzzy(
    raw_text: str,
    *,
    conn=None,
    score_cutoff: float = FUZZY_CUTOFF,
) -> dict | None:
    index = load_alias_index(conn)
    query = normalize_text(raw_text)
    if not query:
        return None
    result = process.extractOne(
        query,
        list(index),
        # Ratio compares the complete normalized strings. WRatio can reward
        # short substrings, which caused "statistical learning" to resolve
        # incorrectly to "Deep Learning" before semantic fallback ran.
        scorer=fuzz.ratio,
        score_cutoff=score_cutoff,
    )
    if result is None:
        return None
    matched_key, score, _ = result
    candidate = index[matched_key]
    return {
        **candidate,
        "matched_text": raw_text,
        "method": "fuzzy",
        "confidence": round(float(score) / 100.0, 4),
        "fuzzy_score": round(float(score), 2),
        "matched_term": matched_key,
    }