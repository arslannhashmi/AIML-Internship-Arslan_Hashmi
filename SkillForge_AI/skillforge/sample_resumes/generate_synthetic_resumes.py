"""
SkillForge AI — Phase 4: Synthetic resume PDF generator.

Generates 3 fictional candidate resumes:
  resume_1_data_science.pdf   — Data Science / ML profile
  resume_2_frontend.pdf       — Frontend / React profile
  resume_3_devops.pdf         — DevOps / Cloud profile

Each resume uses slightly different section header wording and layout to
stress-test section_detector.py.  Ground-truth skill content is known so
test_parser.py can run deterministic assertions.

Run from the repo root:
    python sample_resumes/generate_synthetic_resumes.py
"""

from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

OUT_DIR = Path(__file__).resolve().parent


def _doc(filename: str):
    path = OUT_DIR / filename
    return SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )


def _styles():
    ss = getSampleStyleSheet()
    name_style = ParagraphStyle("Name", parent=ss["Title"],
                                fontSize=18, spaceAfter=2)
    contact_style = ParagraphStyle("Contact", parent=ss["Normal"],
                                   fontSize=10, spaceAfter=6, textColor=colors.grey)
    heading_style = ParagraphStyle("SectionHead", parent=ss["Heading2"],
                                   fontSize=12, spaceBefore=10, spaceAfter=2,
                                   textColor=colors.HexColor("#1a1a2e"))
    body_style = ParagraphStyle("Body", parent=ss["Normal"],
                                fontSize=10, spaceAfter=3, leading=13)
    bullet_style = ParagraphStyle("Bullet", parent=ss["Normal"],
                                  fontSize=10, spaceAfter=2, leading=13,
                                  leftIndent=12, firstLineIndent=-12)
    return name_style, contact_style, heading_style, body_style, bullet_style


def hr():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor("#cccccc"), spaceAfter=4)


# ─── Resume 1: Data Science / ML ─────────────────────────────────────────────

def build_resume_1():
    doc = _doc("resume_1_data_science.pdf")
    ns, cs, hs, bs, bls = _styles()
    story = []

    story += [
        Paragraph("Alexandra Chen", ns),
        Paragraph("alex.chen@email.com  •  (555) 123-4567  •  linkedin.com/in/alexchen", cs),
        hr(),

        Paragraph("EDUCATION", hs), hr(),
        Paragraph("M.Sc. Computer Science — Stanford University, 2022", bs),
        Paragraph("B.Sc. Mathematics & Statistics — UC Berkeley, 2020", bs),
        Spacer(1, 6),

        Paragraph("EXPERIENCE", hs), hr(),
        Paragraph("<b>Senior Data Scientist — Apex Analytics, 2022–Present</b>", bs),
        Paragraph("- Built end-to-end Machine Learning pipelines using Python, Pandas, and Scikit-learn to predict customer churn (AUC 0.91).", bls),
        Paragraph("- Developed XGBoost and LightGBM ensemble models, reducing false-positive rate by 18%.", bls),
        Paragraph("- Deployed models via Docker containers on AWS using FastAPI for real-time inference.", bls),
        Paragraph("- Maintained Data Visualization dashboards with Matplotlib and Seaborn.", bls),
        Spacer(1, 4),
        Paragraph("<b>Data Analyst Intern — DataVault Inc., Summer 2021</b>", bs),
        Paragraph("- Wrote complex SQL queries against PostgreSQL databases to support product analytics.", bls),
        Paragraph("- Cleaned and wrangled 50 GB datasets with NumPy and Pandas.", bls),
        Spacer(1, 6),

        Paragraph("SKILLS", hs), hr(),
        Paragraph("<b>Languages:</b> Python, R, SQL, Bash Scripting", bs),
        Paragraph("<b>ML/DL:</b> Machine Learning, Deep Learning, Scikit-learn, TensorFlow, PyTorch, XGBoost, NumPy, Pandas", bs),
        Paragraph("<b>Statistics:</b> Statistics, Probability Theory, Linear Algebra, Feature Engineering", bs),
        Paragraph("<b>Infrastructure:</b> Docker, AWS, Git, FastAPI", bs),
        Spacer(1, 6),

        Paragraph("PROJECTS", hs), hr(),
        Paragraph("<b>NLP Sentiment Classifier</b>", bs),
        Paragraph("Fine-tuned a DistilBERT model for Natural Language Processing on product reviews (F1=0.88). Used PyTorch, Transformers.", bls),
        Paragraph("<b>Time Series Forecasting</b>", bs),
        Paragraph("Built LSTM model for Time Series Analysis of energy consumption data. Used TensorFlow, Pandas.", bls),
        Spacer(1, 6),

        Paragraph("CERTIFICATIONS", hs), hr(),
        Paragraph("AWS Certified Machine Learning — Specialty, 2023", bs),
        Paragraph("Google Professional Data Engineer, 2022", bs),
    ]

    doc.build(story)
    print(f"Generated: {OUT_DIR / 'resume_1_data_science.pdf'}")


# ─── Resume 2: Frontend / React ───────────────────────────────────────────────

def build_resume_2():
    doc = _doc("resume_2_frontend.pdf")
    ns, cs, hs, bs, bls = _styles()

    # Deliberately use "WORK EXPERIENCE" and "TECHNICAL SKILLS" header variants
    hs_variant = ParagraphStyle("SH2", parent=hs)
    story = []

    story += [
        Paragraph("Marcus Williams", ns),
        Paragraph("marcus.w@devmail.io  •  +1 (415) 987-6543  •  github.com/mwilliams", cs),
        hr(),

        Paragraph("WORK EXPERIENCE", hs), hr(),
        Paragraph("<b>Frontend Developer — Streamline UI, 2021–Present</b>", bs),
        Paragraph("- Built component library in React with TypeScript, cutting UI development time by 40%.", bls),
        Paragraph("- Migrated legacy jQuery codebase to React 18 with Redux state management.", bls),
        Paragraph("- Wrote Jest unit tests achieving 85% coverage across all React components.", bls),
        Paragraph("- Integrated GraphQL API with Apollo Client, replacing REST API Design patterns.", bls),
        Spacer(1, 4),
        Paragraph("<b>Junior Web Developer — ByteForge Labs, 2019–2021</b>", bs),
        Paragraph("- Built responsive landing pages with HTML, CSS, and vanilla JavaScript.", bls),
        Paragraph("- Adopted Tailwind CSS and SASS for consistent design systems.", bls),
        Paragraph("- Set up Webpack bundling and GitHub Actions CI/CD pipeline.", bls),
        Spacer(1, 6),

        Paragraph("EDUCATION", hs), hr(),
        Paragraph("B.Sc. Computer Science — University of Toronto, 2019", bs),
        Spacer(1, 6),

        Paragraph("TECHNICAL SKILLS", hs), hr(),
        Paragraph("<b>Languages:</b> JavaScript, TypeScript, HTML, CSS", bs),
        Paragraph("<b>Frameworks:</b> React, Next.js, Vue.js, Node.js, Express.js", bs),
        Paragraph("<b>Styling:</b> Tailwind CSS, SASS, CSS Modules", bs),
        Paragraph("<b>Tools:</b> Git, Webpack, Jest, Redux, GraphQL", bs),
        Spacer(1, 6),

        Paragraph("PROJECTS", hs), hr(),
        Paragraph("<b>Portfolio Dashboard</b>", bs),
        Paragraph("Personal finance tracker built with Next.js, TypeScript, and Tailwind CSS. REST API Design backend in Node.js.", bls),
        Paragraph("<b>Open-Source Component Kit</b>", bs),
        Paragraph("50-component React library with full Jest test suite, bundled with Webpack and published on npm.", bls),
    ]

    doc.build(story)
    print(f"Generated: {OUT_DIR / 'resume_2_frontend.pdf'}")


# ─── Resume 3: DevOps / Cloud ─────────────────────────────────────────────────

def build_resume_3():
    doc = _doc("resume_3_devops.pdf")
    ns, cs, hs, bs, bls = _styles()

    # Uses "SUMMARY" and "PROFESSIONAL EXPERIENCE" header variants
    story = []

    story += [
        Paragraph("Priya Nair", ns),
        Paragraph("priya.nair@cloudops.io  •  (669) 234-1122  •  linkedin.com/in/priyanair", cs),
        hr(),

        Paragraph("SUMMARY", hs), hr(),
        Paragraph(
            "DevOps Engineer with 5 years of experience designing CI/CD pipelines and "
            "cloud infrastructure on AWS and GCP. Expert in Kubernetes, Docker, and "
            "Terraform. Passionate about Site Reliability Engineering and observability.",
            bs,
        ),
        Spacer(1, 6),

        Paragraph("PROFESSIONAL EXPERIENCE", hs), hr(),
        Paragraph("<b>Senior DevOps Engineer — Cloudnest, 2020–Present</b>", bs),
        Paragraph("- Automated infrastructure provisioning with Terraform across AWS and GCP, reducing deployment time by 60%.", bls),
        Paragraph("- Orchestrated microservice deployments on Kubernetes clusters (200+ pods).", bls),
        Paragraph("- Built GitHub Actions CI/CD pipelines; previously migrated Jenkins jobs.", bls),
        Paragraph("- Set up Prometheus + Grafana observability stack for real-time alerting.", bls),
        Paragraph("- Wrote Ansible playbooks for Linux Administration configuration management.", bls),
        Spacer(1, 4),
        Paragraph("<b>Systems Engineer — NetPulse, 2018–2020</b>", bs),
        Paragraph("- Managed Docker containers and transitioned monolith to Microservices.", bls),
        Paragraph("- Wrote Bash Scripting automation for log rotation and backup tasks.", bls),
        Paragraph("- Maintained Nginx reverse proxies and Load Balancing configurations.", bls),
        Spacer(1, 6),

        Paragraph("EDUCATION", hs), hr(),
        Paragraph("B.Eng. Information Technology — IIT Bombay, 2018", bs),
        Spacer(1, 6),

        Paragraph("SKILLS", hs), hr(),
        Paragraph("<b>Cloud:</b> AWS, GCP, Azure, Terraform", bs),
        Paragraph("<b>Containers:</b> Docker, Kubernetes", bs),
        Paragraph("<b>CI/CD:</b> CI/CD, GitHub Actions, Jenkins", bs),
        Paragraph("<b>Monitoring:</b> Prometheus, Grafana", bs),
        Paragraph("<b>Systems:</b> Linux Administration, Nginx, Ansible, Bash Scripting", bs),
        Paragraph("<b>Languages:</b> Python, Go, Bash Scripting", bs),
    ]

    doc.build(story)
    print(f"Generated: {OUT_DIR / 'resume_3_devops.pdf'}")


if __name__ == "__main__":
    build_resume_1()
    build_resume_2()
    build_resume_3()
    print("All 3 resumes generated.")
