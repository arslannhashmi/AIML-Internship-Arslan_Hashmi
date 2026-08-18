"""
SkillForge AI — Phase 4b: Text cleaning.

Raw PDF extraction is noisy: inconsistent whitespace, stray page-break
artifacts, bullet characters that vary by font, and blank lines. This module
normalizes that before section detection / skill extraction run on it.

Deliberately conservative: we normalize whitespace and bullets but do NOT
lowercase, strip punctuation aggressively, or remove numbers here — that
kind of normalization belongs in the skill-extraction stage (Phase 5), where
we know exactly what we're preparing the text for. Doing it here would throw
away information (e.g. dates, version numbers) that later stages might need.
"""

import re

_BULLET_CHARS = ["•", "◦", "▪", "‣", "●", "-", "–", "—"]


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # collapse runs of 3+ blank lines to a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # collapse runs of horizontal whitespace
    text = re.sub(r"[ \t]{2,}", " ", text)
    # strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip()


def normalize_bullets(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        for ch in _BULLET_CHARS:
            if stripped.startswith(ch):
                stripped = "- " + stripped[len(ch):].strip()
                break
        lines.append(stripped)
    return "\n".join(lines)


def clean_text(raw_text: str) -> str:
    text = normalize_whitespace(raw_text)
    text = normalize_bullets(text)
    return text
