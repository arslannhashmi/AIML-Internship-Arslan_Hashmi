"""
SkillForge AI — Phase 4 test run.

Runs the full parse pipeline against every sample resume and checks:
  1. Both extractors produced non-trivial, roughly similar amounts of text.
  2. Section detection found the expected canonical sections for each resume
     (we know what we put in them, since we authored the synthetic fixtures).
  3. No content silently disappeared (spot check: a known skill string
     appears somewhere in the cleaned text).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resume_parser import parse_resume  # noqa: E402

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"

# (filename, expected canonical sections, a skill string that must survive extraction)
TEST_CASES = [
    ("resume_1_data_science.pdf",
     {"education", "experience", "projects", "skills", "certifications"},
     "XGBoost"),
    ("resume_2_frontend.pdf",
     {"experience", "education", "skills", "projects"},  # "TECHNICAL SKILLS" -> canonical "skills"
     "Tailwind CSS"),
    ("resume_3_devops.pdf",
     {"summary", "experience", "education", "skills"},
     "Terraform"),
]


def run():
    all_pass = True

    for filename, expected_sections, must_contain in TEST_CASES:
        pdf_path = SAMPLE_DIR / filename
        print("=" * 70)
        print(filename)
        print("=" * 70)

        result = parse_resume(str(pdf_path))
        pymupdf_len, pdfplumber_len = result["extraction_agreement_chars"]
        found_sections = set(result["sections"].keys())

        print(f"  PyMuPDF chars: {pymupdf_len}   pdfplumber chars: {pdfplumber_len}")
        len_ratio = min(pymupdf_len, pdfplumber_len) / max(pymupdf_len, pdfplumber_len)
        extractor_ok = len_ratio > 0.85
        print(f"  Extractor agreement ratio: {len_ratio:.2f}  "
              f"{'OK' if extractor_ok else 'DIVERGENT - investigate'}")

        missing = expected_sections - found_sections
        sections_ok = not missing
        print(f"  Expected sections found: {sorted(expected_sections & found_sections)}")
        if missing:
            print(f"  MISSING sections: {sorted(missing)}")
        print(f"  All detected sections: {sorted(found_sections)}")

        content_ok = must_contain in result["cleaned_text"]
        print(f"  Content spot-check ('{must_contain}' present): "
              f"{'OK' if content_ok else 'FAIL - content lost'}")

        case_pass = extractor_ok and sections_ok and content_ok
        print(f"  RESULT: {'PASS' if case_pass else 'FAIL'}\n")
        all_pass = all_pass and case_pass

    print("=" * 70)
    print(f"OVERALL: {'ALL PASS' if all_pass else 'SOME FAILURES - see above'}")
    print("=" * 70)


if __name__ == "__main__":
    run()
