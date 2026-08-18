"""
SkillForge AI — Phase 4c: Resume section detection.

Baseline approach (per Section 9 "Stage 1: rule-based" philosophy applied to
this sub-problem too): resumes almost universally mark sections with short,
distinct header lines (all-caps or title-case, no trailing punctuation,
often followed by a horizontal rule/blank line). We detect header lines by:

  1. Matching against a canonical-section -> known-header-variants dictionary
     (handles "WORK EXPERIENCE" vs "EXPERIENCE" vs "PROFESSIONAL EXPERIENCE").
  2. A structural fallback heuristic (short line, mostly uppercase, no
     sentence-ending punctuation) to catch header wordings we haven't
     enumerated, so the detector degrades gracefully instead of silently
     dropping content into the wrong bucket.

This is intentionally simple and will make mistakes on unusual resume
formats — that's expected and fine for a Stage-1 baseline. We evaluate it
properly once we have skill-extraction ground truth to check against
(Phase 5's precision/recall/F1 comparison), not before.
"""

import re

CANONICAL_SECTIONS = {
    "education": ["education", "academic background", "academic qualifications"],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history",
    ],
    "skills": [
        "skills", "technical skills", "core skills", "key skills",
        "skills & tools", "technical proficiencies",
    ],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": [
        "certifications", "certificates", "licenses & certifications",
        "courses & certifications",
    ],
    "summary": ["summary", "profile", "objective", "professional summary", "about"],
}

_HEADER_LOOKUP = {}
for canonical, variants in CANONICAL_SECTIONS.items():
    for v in variants:
        _HEADER_LOOKUP[v.lower()] = canonical


def _looks_like_header(line: str) -> bool:
    """Structural fallback: short, no sentence punctuation, mostly caps/title."""
    stripped = line.strip()
    if not (2 <= len(stripped) <= 40):
        return False
    if stripped.endswith((".", ",", ";")):
        return False
    if stripped.startswith("-"):  # bullet, not a header
        return False
    letters = [c for c in stripped if c.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    return upper_ratio > 0.6  # mostly uppercase (ALL CAPS headers)


def _match_known_header(line: str):
    key = line.strip().lower()
    key = re.sub(r"[:\-–—]+$", "", key).strip()  # strip trailing colon/dash
    return _HEADER_LOOKUP.get(key)


def detect_sections(cleaned_text: str) -> dict:
    """
    Returns {canonical_section_name: "joined text block"} plus a special
    "_header" bucket for content before the first detected section
    (typically name/contact info).
    """
    lines = cleaned_text.split("\n")
    sections = {"_header": []}
    current = "_header"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched = _match_known_header(stripped)
        if matched is None and _looks_like_header(stripped):
            # Unrecognized header wording caught by the structural fallback.
            # Store it under its own literal name so nothing is silently lost.
            matched = stripped.lower().rstrip(":").strip()

        if matched is not None:
            current = matched
            sections.setdefault(current, [])
            continue

        sections.setdefault(current, [])
        sections[current].append(stripped)

    return {k: "\n".join(v) for k, v in sections.items() if v}
