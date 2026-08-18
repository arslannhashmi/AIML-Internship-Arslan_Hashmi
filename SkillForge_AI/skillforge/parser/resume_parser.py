"""
SkillForge AI — Phase 4: Resume parsing pipeline (entry point).

Pipeline: PDF -> raw text (dual extractor) -> cleaned text -> detected sections.

This is the module later phases (skill extraction) will import and call
`parse_resume(path)` against.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_extractor import extract_text       # noqa: E402
from text_cleaner import clean_text          # noqa: E402
from section_detector import detect_sections  # noqa: E402


def parse_resume(pdf_path: str) -> dict:
    extraction = extract_text(pdf_path, primary="pymupdf")
    raw_text = extraction["primary"]
    cleaned = clean_text(raw_text)
    sections = detect_sections(cleaned)

    return {
        "pdf_path": pdf_path,
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "sections": sections,
        "extraction_agreement_chars": (
            len(extraction["pymupdf"]), len(extraction["pdfplumber"])
        ),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <path_to_resume.pdf>")
        sys.exit(1)
    result = parse_resume(sys.argv[1])
    print(f"\n=== {result['pdf_path']} ===")
    print(f"PyMuPDF/pdfplumber extracted char counts: {result['extraction_agreement_chars']}")
    print(f"\nDetected sections: {list(result['sections'].keys())}\n")
    for name, text in result["sections"].items():
        print(f"--- {name} ---")
        print(text)
        print()
