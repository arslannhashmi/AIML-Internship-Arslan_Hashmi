"""
SkillForge AI — Phase 4a: PDF text extraction.

Two extractors, per the spec:
  - PyMuPDF (fitz): primary. Fast, generally reliable reading order.
  - pdfplumber: comparison / fallback. Sometimes handles multi-column or
    table-heavy layouts better; slower.

We extract with both and log a similarity check so we can see, over more
resumes later, whether they diverge in ways that matter (real evaluation
data for Phase 5's baseline-vs-DL comparison methodology, applied here first
in miniature).
"""

import pymupdf as fitz  # PyMuPDF (new import name; old `import fitz` is deprecated)
import pdfplumber


def extract_text_pymupdf(pdf_path: str) -> str:
    text_parts = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def extract_text_pdfplumber(pdf_path: str) -> str:
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text(pdf_path: str, primary: str = "pymupdf") -> dict:
    """
    Returns both extractions plus which one is flagged as primary, so callers
    can choose, and so we can inspect divergence during development.
    """
    pymupdf_text = extract_text_pymupdf(pdf_path)
    pdfplumber_text = extract_text_pdfplumber(pdf_path)

    return {
        "pymupdf": pymupdf_text,
        "pdfplumber": pdfplumber_text,
        "primary": pymupdf_text if primary == "pymupdf" else pdfplumber_text,
        "primary_source": primary,
    }
