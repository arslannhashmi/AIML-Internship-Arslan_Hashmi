"""
SkillForge AI — Phase 5 test: extraction/test_dictionary_matcher.py

Runs the dictionary matcher against all 3 sample resumes and verifies that
the expected skills are extracted from each profile.

Ground-truth expectations are based on the skill names we wrote into each
synthetic resume in generate_synthetic_resumes.py.

Success criteria (from the spec):
  • resume_1 (Data Science): Python, Pandas, NumPy, Scikit-learn, XGBoost,
    Machine Learning should all be found.
  • resume_2 (Frontend): JavaScript, TypeScript, React, Tailwind CSS, Next.js,
    Jest should all be found.
  • resume_3 (DevOps): Docker, Kubernetes, Terraform, AWS, CI/CD, GitHub Actions
    should all be found.

Additionally, we verify:
  • No match references a skill_id that doesn't exist in the database.
  • Word-boundary safety: "Go" language does NOT fire inside "Google".
  • Alias resolution: "ML" → Machine Learning, "ReactJS" → React,
    "Postgres" → PostgreSQL, "sklearn" → Scikit-learn.

Run from the repo root:
    python extraction/test_dictionary_matcher.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from parser.resume_parser import parse_resume           # noqa: E402
from extraction.dictionary_matcher import extract_skills  # noqa: E402
from db.db_client import get_connection                  # noqa: E402

SAMPLE_DIR = REPO_ROOT / "sample_resumes"


# ─── Ground-truth expectations ────────────────────────────────────────────────

EXPECTED_BY_RESUME = {
    "resume_1_data_science.pdf": {
        "must_find": [
            "Python", "Pandas", "NumPy", "Scikit-learn", "XGBoost",
            "Machine Learning", "TensorFlow", "PyTorch",
            "Statistics", "Docker", "SQL", "AWS",
            "Natural Language Processing", "Time Series Analysis",
        ],
        "must_not_find": [],   # nothing we explicitly prohibit in resume 1
    },
    "resume_2_frontend.pdf": {
        "must_find": [
            "JavaScript", "TypeScript", "React", "Tailwind CSS",
            "Next.js", "Jest", "Redux", "GraphQL", "HTML", "CSS",
            "Node.js", "Git", "CI/CD",
        ],
        "must_not_find": [],
    },
    "resume_3_devops.pdf": {
        "must_find": [
            "Docker", "Kubernetes", "Terraform", "AWS", "GCP",
            "CI/CD", "GitHub Actions", "Jenkins", "Prometheus",
            "Grafana", "Ansible", "Linux Administration",
            "Python", "Go", "Bash Scripting", "Nginx",
        ],
        "must_not_find": [],
    },
}

# Alias resolution: these strings should appear in resume text and
# resolve to the named canonical skill.
ALIAS_TESTS = [
    # alias_text, expected_canonical_name (case-insensitive comparison)
    ("ML",        "Machine Learning"),
    ("ReactJS",   "React"),
    ("sklearn",   "Scikit-learn"),
    ("K8s",       "Kubernetes"),
    ("REST",      "REST API Design"),
    ("Postgres",  "PostgreSQL"),
    ("TF",        "TensorFlow"),
]

# Word-boundary tests: these strings should NOT trigger a false match.
BOUNDARY_TESTS = [
    # text_snippet, skill_name_that_must_NOT_match
    ("Working at Google on data engineering", "Go"),      # 'Go' inside 'Google'
    ("Reaction time is critical in systems", "React"),    # 'React' inside 'Reaction'
    ("sklearn-based pipeline", "Scikit-learn"),           # alias 'sklearn' with hyphen after — should STILL match
]


def _canonical_names(matches: list[dict]) -> set[str]:
    return {m["canonical_name"] for m in matches}


def _check_alias_resolution(conn) -> list[tuple[str, bool, str]]:
    """
    Build a synthetic section containing each alias and confirm the
    canonical name comes back.
    """
    results = []
    for alias, expected_canonical in ALIAS_TESTS:
        sections = {"skills": alias}
        matches = extract_skills(sections, conn=conn)
        found = {m["canonical_name"].lower() for m in matches}
        ok = expected_canonical.lower() in found
        results.append((f"Alias '{alias}' → '{expected_canonical}'", ok,
                        f"got: {found}" if not ok else ""))
    return results


def _check_word_boundaries(conn) -> list[tuple[str, bool, str]]:
    """Verify false-positive suppression at word boundaries."""
    results = []
    for snippet, must_not_match in BOUNDARY_TESTS:
        sections = {"experience": snippet}
        matches  = extract_skills(sections, conn=conn)
        found    = _canonical_names(matches)
        # Special case: 'sklearn' with hyphen *should* match Scikit-learn
        if must_not_match == "Scikit-learn":
            ok = must_not_match in found
            results.append((f"'sklearn' in '{snippet}' SHOULD match Scikit-learn", ok,
                            f"got: {found}" if not ok else ""))
        else:
            ok = must_not_match not in found
            results.append((f"'{must_not_match}' must NOT fire in: '{snippet}'", ok,
                            f"false-positive match detected"))
    return results


def run() -> bool:
    print("=" * 70)
    print("SkillForge AI — Phase 5: test_dictionary_matcher.py")
    print("=" * 70)

    conn = get_connection()

    # Verify all skill_ids in DB
    all_skill_ids = {
        row["skill_id"] if isinstance(row, dict) else row[0]
        for row in conn.execute("SELECT skill_id FROM skills").fetchall()
    }

    all_results: list[tuple[str, bool, str]] = []
    all_match_data: dict[str, list[dict]] = {}

    # ── Per-resume tests ──────────────────────────────────────────────────────
    for filename, expectations in EXPECTED_BY_RESUME.items():
        pdf_path = SAMPLE_DIR / filename
        print(f"\n{'─' * 60}")
        print(f"Resume: {filename}")
        print(f"{'─' * 60}")

        if not pdf_path.exists():
            print(f"  [SKIP] File not found: {pdf_path}")
            all_results.append((f"{filename} — file exists", False, "not found"))
            continue

        parsed   = parse_resume(str(pdf_path))
        sections = parsed["sections"]
        matches  = extract_skills(sections, conn=conn)
        all_match_data[filename] = matches

        found_canonicals = _canonical_names(matches)
        print(f"  Sections parsed: {list(sections.keys())}")
        print(f"  Skills found ({len(matches)}): {sorted(found_canonicals)}")

        # Check invalid skill_ids
        bad_ids = [m["skill_id"] for m in matches if m["skill_id"] not in all_skill_ids]
        all_results.append((f"{filename}: all match skill_ids valid",
                            len(bad_ids) == 0,
                            f"bad ids: {bad_ids}" if bad_ids else ""))

        # Check must_find
        for skill_name in expectations["must_find"]:
            ok = skill_name in found_canonicals
            all_results.append((f"{filename}: found '{skill_name}'", ok,
                                f"not in {sorted(found_canonicals)[:5]}…" if not ok else ""))

        # Check must_not_find
        for skill_name in expectations.get("must_not_find", []):
            ok = skill_name not in found_canonicals
            all_results.append((f"{filename}: '{skill_name}' correctly absent", ok, ""))

    # ── Alias resolution tests ─────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("Alias resolution tests")
    print(f"{'─' * 60}")
    alias_results = _check_alias_resolution(conn)
    for label, ok, detail in alias_results:
        all_results.append((label, ok, detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  ← {detail}" if detail else ""))

    # ── Word boundary tests ────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("Word boundary tests")
    print(f"{'─' * 60}")
    boundary_results = _check_word_boundaries(conn)
    for label, ok, detail in boundary_results:
        all_results.append((label, ok, detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  ← {detail}" if detail else ""))

    conn.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    total  = len(all_results)
    passed = sum(1 for _, ok, _ in all_results if ok)
    failed = total - passed
    for label, ok, detail in all_results:
        if not ok:
            print(f"  [FAIL] {label}" + (f"  ← {detail}" if detail else ""))
    print(f"\nResults: {passed}/{total} passed, {failed} failed")
    print(f"OVERALL: {'ALL PASS' if failed == 0 else 'SOME FAILURES — see above'}")
    print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
