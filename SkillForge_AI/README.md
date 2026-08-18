# SkillForge AI

SkillForge AI is a deterministic resume-intelligence pipeline for turning a
resume into a structured skill profile, a career recommendation, a
proficiency-gap analysis, and a prerequisite-aware learning path. The project
is designed for an explainable final-year-project submission: the code makes
the decisions, and the API returns structured JSON rather than relying on an
LLM to rank careers or invent recommendations.

## Problem statement

Resume skill lists are often noisy, inconsistent, and disconnected from a
concrete development plan. SkillForge AI addresses that gap by parsing a PDF
resume, matching skills against a curated technology taxonomy, comparing the
profile with curated career requirements, and ordering unfinished skills
around prerequisite relationships.

## What the system does

1. Accepts a PDF resume through FastAPI.
2. Extracts structured text and deterministic dictionary matches.
3. Persists the user profile in the SQLite database.
4. Ranks the seeded career set with weighted cosine similarity.
5. Scores each selected-career requirement's proficiency deficit.
6. Produces a NetworkX-backed learning path that preserves prerequisites.
7. Returns the Phase 12 structured pipeline output through the API.

The current interaction surface is a static HTML/CSS/vanilla-JavaScript page
served by FastAPI at `/`. It visualizes the match ring, proficiency gaps, and
learning timeline without adding a frontend build step.

## Technology stack

- Python 3.12
- FastAPI and Uvicorn
- SQLite for local/development persistence through the `db_client` abstraction
- PostgreSQL-compatible source schema with SQLite initialization translation
- PyMuPDF and pdfplumber for PDF extraction
- Deterministic dictionary/regex extraction
- spaCy EntityRuler and DistilBERT NER for the Phase 6 evaluation work
- RapidFuzz and raw Transformers mean-pooled Sentence-BERT normalization
- NetworkX for the in-memory prerequisite graph
- Plain HTML, CSS, and vanilla JavaScript for the current static UI

DistilBERT is the only deep-learning component. It is evaluated as part of
Phase 6; the live Phase 14 upload route uses the deterministic dictionary
matcher.

## Run locally

From the project root:

```bash
sh artifacts/api-server/run-skillforge.sh
```

The wrapper sets the required database and Python paths and starts Uvicorn on
`PORT` (8080 by default in the artifact workflow). The equivalent explicit
command is:

```bash
SKILLFORGE_DB_PATH="$PWD/skillforge/db/skillforge.db" \
PYTHONPATH="$PWD/skillforge" \
python3.12 -m uvicorn backend.main:app \
  --app-dir skillforge --host 0.0.0.0 --port 8080
```

Then open `http://localhost:8080/` and upload a PDF resume. The health check is
available at `http://localhost:8080/health`.

The authoritative local database path is always:

```text
SKILLFORGE_DB_PATH=db/skillforge.db
```

## Documentation

- [System architecture](docs/SYSTEM_ARCHITECTURE.md)
- [API reference](docs/API_REFERENCE.md)
- [Final report](docs/FINAL_REPORT.md)

## Live deployment

[Open the deployed SkillForge AI app](https://skillforgeaitest.replit.app)

## Project status

- Phases 3–12: implemented and tested.
- Phase 13: omitted by design; no LLM client, prompt layer, or explanation
  fallback is present.
- Phase 14: FastAPI backend, static interaction surface, and live smoke flow
  are working.
- Phase 15's originally planned separate/full frontend scope is omitted from
  the accepted phase plan; the current static page is a thin API interaction
  surface rather than that deferred scope.
- Phases 16–17: evaluation documentation and basic deployment configuration
  are complete.

The evaluation corpus is synthetic and controlled. Its results demonstrate
pipeline behavior on the saved fixtures; they are not claims of real-resume
generalization or career-ranking accuracy.