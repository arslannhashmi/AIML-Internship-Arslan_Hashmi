"""
SkillForge AI — Phase 5: Stage 1 baseline skill extraction.
Module: extraction/dictionary_matcher.py

──────────────────────────────────────────────────────────────────────────────
Theory / why this approach first
──────────────────────────────────────────────────────────────────────────────
Before deploying statistical models (Phases 6's spaCy EntityRuler and
DistilBERT), we establish a deterministic baseline using exact-match
dictionary look-up with word-boundary regular expressions.

Advantages:
  • Fully interpretable — every match is explainable.
  • Zero training data required.
  • Provides weak-supervision labels for DistilBERT fine-tuning (Phase 6).
  • Sets a precision/recall floor: statistical models that don't beat this
    baseline offer no benefit.

Limitations (expect ~70–80 % recall on clean synthetic PDFs):
  • Misses paraphrases and synonyms not in the alias table.
  • Word-boundary matching on hyphenated / slash-separated terms (e.g.
    "CI/CD") requires special handling.
  • Case-insensitive matching may produce false positives in rare prose
    contexts (e.g. "go" in a sentence vs the Go language).

──────────────────────────────────────────────────────────────────────────────
Inputs
──────────────────────────────────────────────────────────────────────────────
  sections: dict[str, str]
      Output of parser.section_detector.detect_sections() — section name →
      cleaned text block.  Matches are attributed to the section they came
      from (useful for weighting: a skill in "skills" section is more
      reliable than one found in "summary").

──────────────────────────────────────────────────────────────────────────────
Output format
──────────────────────────────────────────────────────────────────────────────
  List of dicts:
  {
    "skill_id":      int,
    "matched_text":  str,    # the literal string found in the resume
    "canonical_name": str,   # canonical skill name from the skills table
    "section":       str,    # which resume section contained this match
    "char_span":     (int, int),  # (start, end) within the section text
  }

  Matches are deduplicated per (skill_id, section) pair — the first
  occurrence wins.  This ensures Phase 6's weak-supervision labels are
  compact and don't double-count skill mentions within the same section.

  The list is also suitable as a BIO-tagged NER training set for Phase 6:
  each match provides a (text, start, end, label) tuple without further
  transformation.
"""

import re
import sqlite3
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from db.db_client import get_connection  # noqa: E402


# ─── Lookup table construction ───────────────────────────────────────────────

def _load_skill_lookup(conn) -> dict[str, tuple[int, str]]:
    """
    Build a lowercase lookup dict:
        normalised_text → (skill_id, canonical_name)

    Includes both canonical skill names and all aliases.
    The longest match wins implicitly because regex alternation is built from
    longest to shortest.
    """
    lookup: dict[str, tuple[int, str]] = {}

    # Canonical names
    rows = conn.execute("SELECT skill_id, name FROM skills").fetchall()
    for row in rows:
        skill_id = row["skill_id"] if isinstance(row, dict) else row[0]
        name     = row["name"]     if isinstance(row, dict) else row[1]
        lookup[name.lower()] = (skill_id, name)

    # Aliases (may override canonical if shorter — but we sort by length later)
    rows = conn.execute(
        "SELECT sa.skill_id, sa.alias_text, s.name"
        " FROM skill_aliases sa JOIN skills s ON sa.skill_id = s.skill_id"
    ).fetchall()
    for row in rows:
        if isinstance(row, dict):
            skill_id, alias, canonical = row["skill_id"], row["alias_text"], row["name"]
        else:
            skill_id, alias, canonical = row[0], row[1], row[2]
        lookup[alias.lower()] = (skill_id, canonical)

    return lookup


def _build_pattern(lookup: dict[str, tuple[int, str]]) -> re.Pattern:
    """
    Compile a single regex that matches any skill name or alias.

    Design decisions:
      • Sort terms longest-first so multi-word skills (e.g. "Machine Learning")
        match before their substrings (e.g. "learning").
      • Use re.escape so dots, pluses, slashes in names like "Vue.js",
        "C++", "CI/CD" are treated as literals.
      • Word boundaries (\b) prevent "React" matching inside "Reaction" and
        "Go" matching inside "Google".  For terms ending/starting with non-word
        characters (e.g. "C++", "CI/CD") we use a lookahead/lookbehind that
        asserts a non-alphanumeric boundary, because \b doesn't work reliably
        adjacent to punctuation.
      • re.IGNORECASE so "python", "Python", "PYTHON" all match.
    """
    terms = sorted(lookup.keys(), key=len, reverse=True)

    parts = []
    for term in terms:
        escaped = re.escape(term)
        # Use \b where term starts/ends with a word character (letter, digit, _);
        # otherwise use a negative look-behind/ahead for alphanumeric characters.
        left_boundary  = r"\b" if re.match(r"^\w", term) else r"(?<![A-Za-z0-9])"
        right_boundary = r"\b" if re.search(r"\w$", term) else r"(?![A-Za-z0-9])"
        parts.append(f"{left_boundary}{escaped}{right_boundary}")

    pattern = "|".join(f"({p})" for p in parts)
    return re.compile(pattern, re.IGNORECASE)


# ─── Matching ─────────────────────────────────────────────────────────────────

def match_skills_in_text(
    text: str,
    section: str,
    lookup: dict[str, tuple[int, str]],
    pattern: re.Pattern,
    *,
    deduplicate: bool = True,
) -> list[dict]:
    """
    Find all skill mentions in a single text block.

    Args:
        text:          The cleaned resume section text.
        section:       The section name ("skills", "experience", …).
        lookup:        Normalised text → (skill_id, canonical_name).
        pattern:       Pre-compiled regex from _build_pattern().
        deduplicate:   If True (default), keep only the first occurrence of
                       each skill_id within this section.

    Returns:
        List of match dicts (see module docstring for schema).
    """
    results = []
    seen_in_section: set[int] = set()

    for m in pattern.finditer(text):
        matched_text = m.group(0)
        key = matched_text.lower()
        if key not in lookup:
            continue
        skill_id, canonical_name = lookup[key]

        if deduplicate and skill_id in seen_in_section:
            continue

        results.append({
            "skill_id":       skill_id,
            "matched_text":   matched_text,
            "canonical_name": canonical_name,
            "section":        section,
            "char_span":      (m.start(), m.end()),
        })

        if deduplicate:
            seen_in_section.add(skill_id)

    return results


# ─── Pipeline entry point ─────────────────────────────────────────────────────

def extract_skills(
    sections: dict[str, str],
    *,
    conn=None,
    deduplicate_per_section: bool = True,
) -> list[dict]:
    """
    Run the dictionary matcher across all resume sections.

    Args:
        sections:                The dict returned by detect_sections().
        conn:                    Optional open DB connection (for testing/batching).
                                 If None, opens + closes its own connection.
        deduplicate_per_section: De-duplicate per (skill_id, section) pair.

    Returns:
        Combined, ordered list of match dicts across all sections.
        Sections are processed in the order they appear in the dict.
    """
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    try:
        lookup  = _load_skill_lookup(conn)
        pattern = _build_pattern(lookup)

        all_matches = []
        # Deduplicate globally across sections: a skill_id seen in "skills"
        # shouldn't be re-reported for every sentence in "experience".
        # We keep the FIRST section occurrence for each skill_id.
        seen_globally: set[int] = set()

        for section_name, section_text in sections.items():
            if not section_text.strip():
                continue
            section_matches = match_skills_in_text(
                section_text, section_name, lookup, pattern,
                deduplicate=deduplicate_per_section,
            )
            for match in section_matches:
                if match["skill_id"] not in seen_globally:
                    all_matches.append(match)
                    seen_globally.add(match["skill_id"])

        return all_matches

    finally:
        if own_conn:
            conn.close()


# ─── Convenience: as weak-supervision BIO labels ─────────────────────────────

def to_bio_labels(
    section_text: str,
    section_matches: list[dict],
) -> list[tuple[str, str]]:
    """
    Convert match dicts for a single section to BIO token labels.
    Splits on whitespace; tokens overlapping a match span get B-SKILL / I-SKILL.

    Returns: [(token_str, label), ...]
    Useful for Phase 6 DistilBERT fine-tuning data preparation.
    """
    span_set: set[int] = set()
    span_begins: set[int] = set()
    for m in section_matches:
        start, end = m["char_span"]
        span_set.update(range(start, end))
        span_begins.add(start)

    tokens = []
    cursor = 0
    for word_match in re.finditer(r"\S+", section_text):
        word = word_match.group(0)
        wstart = word_match.start()
        if wstart in span_begins:
            label = "B-SKILL"
        elif wstart in span_set:
            label = "I-SKILL"
        else:
            label = "O"
        tokens.append((word, label))
    return tokens


# ─── CLI smoke test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    sample_sections = {
        "skills": (
            "Python, Machine Learning, Scikit-learn, PyTorch, TensorFlow, "
            "NumPy, Pandas, XGBoost, SQL, Docker, Git"
        ),
        "experience": (
            "Built ML pipelines using Python and Pandas. Deployed models with "
            "Docker on AWS. Wrote REST API in FastAPI."
        ),
    }

    matches = extract_skills(sample_sections)
    print(json.dumps(matches, indent=2))
    print(f"\nTotal unique skills found: {len(matches)}")
