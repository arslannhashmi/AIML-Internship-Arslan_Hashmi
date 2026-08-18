"""
SkillForge AI — Phase 6: labelled synthetic resume corpus.

Creates 18 additional fictional resumes.  The canonical skill list is written
alongside the PDFs so the held-out split has independently known ground truth;
the training labels used by BERT still come from dictionary_matcher.py.

Run from skillforge/:
    python sample_resumes/generate_phase6_resumes.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer


OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "labeled_resumes"

ALIASES = {
    "Machine Learning": "ML",
    "React": "ReactJS",
    "Scikit-learn": "sklearn",
    "Kubernetes": "K8s",
    "PostgreSQL": "Postgres",
    "TensorFlow": "TF",
    "REST API Design": "REST",
}


PROFILES = [
    ("Aisha Rahman", "data_scientist", ["Python", "Pandas", "NumPy", "SQL", "Machine Learning", "Scikit-learn", "Statistics", "Feature Engineering", "XGBoost", "Data Visualization"]),
    ("Daniel Ortiz", "data_engineer", ["Python", "SQL", "PostgreSQL", "Apache Spark", "Apache Kafka", "ETL", "Data Warehousing", "Docker", "AWS", "Git"]),
    ("Mei Tanaka", "ml_engineer", ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Model Deployment", "Docker", "FastAPI", "Git", "Linux Administration"]),
    ("Noah Williams", "analytics", ["R", "SQL", "Statistics", "Probability Theory", "Pandas", "Data Visualization", "Time Series Analysis", "Git", "PostgreSQL"]),
    ("Sofia Petrova", "nlp", ["Python", "Natural Language Processing", "Machine Learning", "Scikit-learn", "PyTorch", "Deep Learning", "Feature Engineering", "SQL", "Git"]),
    ("Omar Khan", "frontend", ["JavaScript", "TypeScript", "React", "Next.js", "HTML", "CSS", "Tailwind CSS", "Redux", "Jest", "Git"]),
    ("Chloe Martin", "web_platform", ["JavaScript", "Vue.js", "HTML", "CSS", "SASS", "Webpack", "GraphQL", "Node.js", "Express.js", "Jest"]),
    ("Ethan Brooks", "full_stack", ["JavaScript", "TypeScript", "React", "Node.js", "Express.js", "REST API Design", "PostgreSQL", "Docker", "Git", "Unit Testing"]),
    ("Fatima Ali", "mobile", ["Java", "Android Development", "React Native", "JavaScript", "Mobile UI Design", "REST API Design", "Git", "Unit Testing", "Debugging"]),
    ("Lucas Silva", "backend", ["Python", "Django", "Flask", "FastAPI", "REST API Design", "SQL", "PostgreSQL", "Docker", "API Authentication", "Git"]),
    ("Grace Lee", "devops", ["Linux Administration", "Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Jenkins", "Prometheus", "Grafana", "Ansible"]),
    ("Hassan Ahmed", "cloud", ["AWS", "GCP", "Azure", "Terraform", "Kubernetes", "Docker", "Microservices", "Load Balancing", "Nginx", "Linux Administration"]),
    ("Emma Johnson", "sre", ["Python", "Go", "Linux Administration", "Docker", "Kubernetes", "Prometheus", "Grafana", "Nginx", "Load Balancing", "Git"]),
    ("Yusuf Malik", "security", ["Python", "Cybersecurity", "OAuth/JWT", "HTTPS/TLS", "Penetration Testing", "OWASP", "Linux Administration", "SQL", "Git"]),
    ("Isabella Rossi", "software", ["Java", "Object-Oriented Programming", "Algorithms & Data Structures", "Design Patterns", "Unit Testing", "Integration Testing", "Code Review", "Git", "SQL"]),
    ("William Chen", "api", ["Java", "Object-Oriented Programming", "REST API Design", "gRPC", "WebSockets", "Docker", "Kubernetes", "SQL", "Database Design", "Git"]),
    ("Nadia Hassan", "data_platform", ["Python", "Apache Airflow", "dbt", "ETL", "Data Warehousing", "SQL", "PostgreSQL", "Redis", "Docker", "AWS"]),
    ("Jack Taylor", "qa", ["JavaScript", "TypeScript", "Jest", "Unit Testing", "Integration Testing", "Debugging", "GitHub Actions", "CI/CD", "Git", "Agile/Scrum"]),
]


def _styles():
    ss = getSampleStyleSheet()
    return (
        ParagraphStyle("Name6", parent=ss["Title"], fontSize=18, spaceAfter=2),
        ParagraphStyle("Contact6", parent=ss["Normal"], fontSize=9, spaceAfter=6, textColor=colors.grey),
        ParagraphStyle("Heading6", parent=ss["Heading2"], fontSize=11, spaceBefore=8, spaceAfter=2, textColor=colors.HexColor("#1a1a2e")),
        ParagraphStyle("Body6", parent=ss["Normal"], fontSize=9, spaceAfter=3, leading=12),
        ParagraphStyle("Bullet6", parent=ss["Normal"], fontSize=9, spaceAfter=2, leading=12, leftIndent=12, firstLineIndent=-12),
    )


def _safe(value: str) -> str:
    return html.escape(value, quote=False)


def _display_skill(skill: str, index: int) -> str:
    # Vary surface forms while keeping canonical ground truth in metadata.
    if index % 7 == 0 and skill in ALIASES:
        return ALIASES[skill]
    return skill


def _build_pdf(filename: str, name: str, profile: str, skills: list[str], index: int) -> None:
    path = OUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path), pagesize=LETTER,
        leftMargin=0.72 * inch, rightMargin=0.72 * inch,
        topMargin=0.65 * inch, bottomMargin=0.65 * inch,
    )
    ns, cs, hs, bs, bls = _styles()
    shown = [_display_skill(skill, index + position) for position, skill in enumerate(skills)]
    first = ", ".join(shown[:5])
    second = ", ".join(shown[5:])
    headers = [
        ("SUMMARY", "EXPERIENCE", "TECHNICAL SKILLS", "PROJECTS"),
        ("PROFILE", "WORK EXPERIENCE", "SKILLS", "PERSONAL PROJECTS"),
        ("PROFESSIONAL SUMMARY", "PROFESSIONAL EXPERIENCE", "CORE SKILLS", "KEY PROJECTS"),
    ][index % 3]
    story = [
        Paragraph(_safe(name), ns),
        Paragraph(f"{name.lower().replace(' ', '.')}@example.org  •  +1 (555) 010-{index + 20:04d}", cs),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=4),
        Paragraph(headers[0], hs),
        Paragraph(
            f"{profile.replace('_', ' ').title()} professional delivering reliable systems with "
            f"{_safe(first)} and {_safe(second[:45])}.", bs
        ),
        Spacer(1, 4),
        Paragraph(headers[1], hs),
        Paragraph(f"<b>{profile.replace('_', ' ').title()} Engineer — Example Labs</b>", bs),
        Paragraph(f"- Delivered production features using {_safe(first)}.", bls),
        Paragraph(f"- Automated testing, documentation, and releases with {_safe(second)}.", bls),
        Spacer(1, 4),
        Paragraph(headers[2], hs),
        Paragraph(f"<b>Core:</b> {_safe(', '.join(shown[:5]))}", bs),
        Paragraph(f"<b>Tools:</b> {_safe(', '.join(shown[5:]))}", bs),
        Spacer(1, 4),
        Paragraph(headers[3], hs),
        Paragraph(f"<b>{profile.replace('_', ' ').title()} Delivery Platform</b>", bs),
        Paragraph(f"Implemented an end-to-end project using {_safe(', '.join(shown))}.", bls),
        Paragraph("Education: B.Sc. Computer Science — Synthetic University", bs),
    ]
    doc.build(story)


def generate() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for index, (name, profile, skills) in enumerate(PROFILES, start=1):
        filename = f"phase6_resume_{index:02d}_{profile}.pdf"
        _build_pdf(filename, name, profile, skills, index)
        records.append({
            "filename": filename,
            "name": name,
            "profile": profile,
            "skills": skills,
            "split": "train" if index <= 14 else "heldout",
        })
    metadata_path = OUT_DIR / "ground_truth.json"
    metadata_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Generated {len(records)} labelled resumes in {OUT_DIR}")
    print(f"Ground truth: {metadata_path}")
    print(f"Split: {sum(r['split'] == 'train' for r in records)} train / {sum(r['split'] == 'heldout' for r in records)} heldout")
    return {"records": records, "metadata_path": metadata_path}


if __name__ == "__main__":
    generate()