# SkillForge AI — Project State

**Last updated:** Final checkpoint complete (Phases 16–17)

## Architecture decisions locked in
- 3-layer architecture: Deterministic Core (extraction/matching) → Recommendation
  & Reasoning Engine (career match/gap/graph/path) → Interaction Layer (LLM
  explanation only, fed structured JSON, never makes decisions).
- Neo4j, K-Means clustering, and the full multi-agent framework are **de-scoped
  to "future work"** for the FYP submission — using NetworkX (in-memory graph)
  and a single orchestration script instead.
- DL component (DistilBERT NER) is the single deep-learning claim in the
  project — not adding DL elsewhere.
- Database: SQLite for local/dev (schema.sql is Postgres-first; init_db.py
  auto-translates syntax). Migrate to real Postgres only if/when deployment
  requires it.
- **IMPORTANT**: always set `SKILLFORGE_DB_PATH=db/skillforge.db` when running
  any script locally — this prevents db_client.py from picking up Replit's
  platform DATABASE_URL and trying to connect to psycopg2.

## Phase 3 — DONE
Files under `skillforge/`:
- `schema.sql` — full Postgres-compatible schema (9 tables)
- `data/seed_data.py` — 101 skills, 15 careers, 62 prerequisite edges,
  116 career-skill requirement rows, 26 aliases (hand-curated)
- `db/init_db.py` — builds & validates SQLite db, exports JSON snapshots
- `db/query_test.py` — sanity checks (row counts, alias resolution,
  prerequisite lookups, per-career requirement coverage) — all passing
- `db/skillforge.db` — built SQLite database
- `db/db_client.py` — thin DB access abstraction (SQLite/Postgres swap point)
- `data/*_export.json` — JSON snapshots of every table

## Phase 4 — DONE
Files under `skillforge/`:
- `sample_resumes/generate_synthetic_resumes.py` — generates 3 fictional
  test-resume PDFs (Data Science / Frontend / DevOps, each with slightly
  different section header wording to stress-test parsing)
- `sample_resumes/*.pdf` — the 3 generated PDFs
- `parser/pdf_extractor.py` — dual extraction: PyMuPDF (primary) + pdfplumber
- `parser/text_cleaner.py` — whitespace/bullet normalization
- `parser/section_detector.py` — heuristic section detection (header dict +
  structural fallback for ALL-CAPS short-line headers)
- `parser/resume_parser.py` — pipeline entry point: `parse_resume(pdf_path)`
- `parser/test_parser.py` — **3/3 PASS**

## Phase 5 — DONE ✅
Files under `skillforge/`:
- `extraction/dictionary_matcher.py` — Stage 1 baseline regex/dictionary
  skill extractor.  Loads all skill names + aliases from the DB into a
  lookup dict, compiles a single IGNORECASE regex with word-boundary guards,
  and returns structured match dicts per section.
- `extraction/test_dictionary_matcher.py` — test suite

**Phase 5 test results — 56/56 PASS:**

Resume extractions:
| Resume | Skills found | Key hits confirmed |
|---|---|---|
| resume_1_data_science.pdf | 25 | Python, Pandas, NumPy, Scikit-learn, XGBoost, Machine Learning, TensorFlow, PyTorch, NLP, Time Series Analysis, ... |
| resume_2_frontend.pdf | 19 | JavaScript, TypeScript, React, Tailwind CSS, Next.js, Jest, Redux, GraphQL, HTML, CSS, CI/CD, ... |
| resume_3_devops.pdf | 19 | Docker, Kubernetes, Terraform, AWS, GCP, CI/CD, GitHub Actions, Jenkins, Prometheus, Grafana, Ansible, Go, ... |

Alias resolution (7/7 PASS): ML→Machine Learning, ReactJS→React,
sklearn→Scikit-learn, K8s→Kubernetes, REST→REST API Design,
Postgres→PostgreSQL, TF→TensorFlow

Word-boundary guards (3/3 PASS): "Go" does not fire inside "Google";
"React" does not fire inside "Reaction"; "sklearn" with hyphen still matches.

Output format is Phase 6-ready: each match includes
`{skill_id, matched_text, canonical_name, section, char_span}` — the
`char_span` + `canonical_name` fields are directly usable as weak-supervision
BIO labels for DistilBERT fine-tuning.

## Open questions still unanswered by user (defaults assumed, confirm/override anytime)
1. Full 17-phase scope vs formally reduced FYP scope — assumed reduced per above.
2. Real resumes available? — still NO; tested on synthetic PDFs only.
3. Course/rubric constraints (paper length, required metrics) — unknown.
4. Timeline to submission — unknown, phases not yet time-boxed.

## Phase 6 — DONE ✅
Files under `skillforge/`:
- `sample_resumes/generate_phase6_resumes.py` — creates 18 additional labelled
  synthetic PDFs and `data/labeled_resumes/ground_truth.json` (14 train / 4
  held out).
- `extraction/spacy_ner_extractor.py` — deterministic spaCy EntityRuler
  seeded from the database's canonical skills and aliases.
- `extraction/bert_ner_extractor.py` — fine-tunes
  `distilbert-base-uncased` for token classification using Phase 5 weak
  labels, bounded to 3 epochs, and saves the tokenizer/model.
- `extraction/evaluate_extraction.py` — held-out skill-level micro
  precision/recall/F1 evaluation for all three extraction stages.
- `evaluation/phase6_extraction_results.json` — actual saved metrics,
  per-resume results, training loss, and limitations.

**Phase 6 evaluation — 4 held-out synthetic resumes:**

| Stage | Precision | Recall | F1 |
|---|---:|---:|---:|
| Dictionary baseline | 1.0000 | 1.0000 | 1.0000 |
| spaCy EntityRuler | 1.0000 | 1.0000 | 1.0000 |
| DistilBERT NER | 1.0000 | 0.8974 | 0.9459 |

Winner by F1: dictionary baseline. DistilBERT trained for 3 epochs; its
training losses were recorded in the evaluation JSON. These are real metrics
on controlled synthetic held-out resumes, not real-resume generalization.

## Checkpoint 2 — Phases 7 + 8 DONE ✅
Files under `skillforge/normalization/`:
- `alias_matcher.py` — exact canonical/alias resolution with formatting
  normalization (`Machine-Learning` → `Machine Learning`).
- `fuzzy_matcher.py` — RapidFuzz full-string similarity fallback for near
  misses; avoids substring-driven false positives.
- `semantic_matcher.py` — direct mean-pooled Sentence-BERT embeddings using
  `sentence-transformers/all-MiniLM-L6-v2` through the installed Transformers
  stack.
- `threshold_calibration.py` — labelled equivalent/different pair calibration
  and saved empirical cutoff.
- `normalization_pipeline.py` — alias → fuzzy → semantic orchestration.

Files under `skillforge/knowledge_base/`:
- `skill_graph.py` — NetworkX directed prerequisite → dependent graph with
  prerequisite, dependent, topological-order, and cycle checks.
- `tests/test_checkpoint_2.py` — deterministic and semantic fallback checks.

**Threshold calibration result:**
- Positive similarity range: `0.3420–1.0000`
- Negative similarity range: `0.0673–0.3226`
- Empirical cutoff: `0.3323`
- Calibration F1: `1.0000`
- Saved to `evaluation/phase7_threshold_calibration.json`

**Checkpoint 2 test result: 8/8 PASS**
- `ML` → Machine Learning
- `Machine-Learning` → Machine Learning
- `ReactJS` → React
- fuzzy `Pythn` → Python
- semantic `data plotting` → Data Visualization
- Machine Learning has Python prerequisite
- `has_cycle()` → False
- Python precedes Machine Learning in topological order

## Checkpoint 3 — Phases 9 + 10 + 11 DONE ✅

### Phase 9 — Recommendation
Files under `skillforge/recommendation/`:
- `vectorizer.py` — one dimension per canonical skill; learner values are
  proficiency/5 weighted by career importance, and career target values are
  preferred proficiency/5 weighted by the same importance.
- `content_based_recommender.py` — ranks all seeded careers with cosine
  similarity over those weighted skill vectors.
- `evaluate_recommender.py` — three hand-built plausibility profiles.

The evaluator is explicitly labelled **face-validity testing (not accuracy
evaluation)**. It does not claim accuracy, precision, recall, or
generalisation from the illustrative profiles.

### Phase 10 — Gap analysis
Files under `skillforge/gap_analysis/`:
- `gap_analyzer.py` — deterministic gap records for a selected career.

Formula:
`gap_score = importance × max(preferred_proficiency − current_proficiency, 0)`

An omitted skill has current proficiency `0`. Since importance and
proficiency each use a 1–5 scale, the maximum gap score is 25. Bucket
thresholds:
- `Strong`: 0
- `Minor`: 1–5
- `Moderate`: 6–10
- `Major`: 11–15
- `Critical`: 16+

### Phase 11 — Learning path
Files under `skillforge/learning_path/`:
- `learning_path.py` — Kahn topological ordering over missing skills from the
  Phase 8 NetworkX graph. Among currently unlocked skills, larger gap scores
  are selected first; skill ID provides deterministic final tie-breaking.

### Checkpoint 3 verification
- Python compilation: PASS
- `tests/test_checkpoint_3.py`: **8/8 PASS**
- `recommendation/evaluate_recommender.py`: **3/3 PASS**
  - Data Science profile → Data Scientist
  - Frontend profile → Frontend Developer
  - DevOps profile → DevOps Engineer
- Checkpoint 2 regression: **8/8 PASS**
- Manual Data Scientist gap/path smoke test: PASS

## Phase 12 — DONE ✅

Files under `skillforge/agent/`:
- `profile_agent.py` — normalizes a raw skill profile into sorted,
  JSON-friendly skill/proficiency records.
- `career_agent.py` — thin wrapper over the deterministic career recommender.
- `skill_gap_agent.py` — thin wrapper over deterministic gap analysis.
- `learning_agent.py` — thin wrapper over the prerequisite-aware learning path.
- `progress_agent.py` — computes deterministic minimum/preferred coverage and
  remaining gap score.
- `orchestrator.py` — runs `profile → career → gap → learning` in sequence,
  appends the progress summary, validates JSON serializability, and returns the
  final structured pipeline dictionary.

Phase 12 contains no LLM calls, prompt generation, API-key access, or
explanation fallback. The structured orchestrator dictionary is the final
pipeline output.

**Phase 12 verification:**
- Python compilation: PASS
- `tests/test_phase12_agents.py`: **8/8 PASS**
- Checkpoint 3 regression: **8/8 PASS**
- No `llm_layer/` files present: PASS
- No LLM/API-key references in `agent/`: PASS

## Phase 13 — OMITTED BY PROJECT DECISION

The LLM layer is intentionally skipped. No `prompt_templates.py`,
`llm_client.py`, or `guardrails.py` will be added, and no Anthropic API key is
required for this project.

## Phase 14 — DONE ✅

FastAPI backend files under `skillforge/backend/`:
- `main.py` — application entry point, health endpoint, and router wiring.
- `config.py` — upload-size and upload-directory configuration.
- `schemas.py` — Pydantic request/response models.
- `dependencies.py` — request-scoped connections and persisted-user/profile
  lookup through `db_client.get_connection()`.
- `profile.py` — PDF upload, resume parsing, dictionary extraction, and
  persisted structured profile.
- `careers.py` — user career recommendations.
- `gap.py` — user/target-career gap analysis.
- `roadmap.py` — prerequisite-aware learning path.
- `agent.py` — direct Phase 12 orchestrator result with no LLM step.

Routes:
- `GET /health`
- `POST /profile/resume`
- `GET /careers/{user_id}/recommendations`
- `GET /gap/{user_id}/{career_id}`
- `GET /roadmap/{user_id}/{career_id}`
- `POST /agent/{user_id}/run`

The backend uses only the existing `db/db_client.py` abstraction. SQLite
connections are request-scoped and permit FastAPI's synchronous worker-thread
boundary; no second database access pattern was introduced.

### Phase 14 verification
- FastAPI/Uvicorn startup: PASS
- `/health`: `{"status":"ok","phase":"14"}`
- Real PDF upload: **200 OK**, structured profile returned with 19 extracted
  skills and persisted user/resume records.
- Recommendations: **200 OK**, Frontend Developer ranked first with score
  `0.9916560553218191`.
- Gap analysis: **200 OK**, 8 career requirements returned.
- Roadmap: **200 OK**, 8-skill prerequisite-aware path returned.
- Full agent run: **200 OK**, direct Phase 12 structure returned with no
  explanation field.
- Phase 12 regression: **8/8 PASS**
- Checkpoint 3 regression: **8/8 PASS**
- Database query sanity suite: **ALL PASS**
- Backend DB access scan: PASS — `db_client` only.

## Phase 15 — OMITTED BY PROJECT PLAN

Frontend work is intentionally skipped because it will be built separately in
Lovable.

## Final checkpoint — Phases 16 + 17 DONE ✅

### Evaluation and reporting

Added:
- `evaluation/phase9_face_validity_results.json` — captured directly from the
  existing Phase 9 evaluator.
- `docs/dataset_methodology.md` — knowledge-base, synthetic-resume, split,
  calibration, and face-validity methodology.
- `docs/limitations.md` — explicit circular-evaluation, omitted-LLM,
  direct-Transformers, synthetic-data, recommendation, and deployment limits.
- `docs/evaluation_results.md` — report-ready tables populated from the saved
  Phase 6/7 JSON artifacts and the actual Phase 9 evaluator output.

Authoritative metrics were not re-derived or invented:
- Phase 6 aggregate extraction metrics come from
  `evaluation/phase6_extraction_results.json`.
- Phase 7 calibration metrics come from
  `evaluation/phase7_threshold_calibration.json`.
- Phase 9 face-validity results come from the existing evaluator and are saved
  in `evaluation/phase9_face_validity_results.json`.

### Basic Replit deployment

Validated `.replit` deployment configuration:
- Autoscale target
- Uvicorn command using `--app-dir skillforge`
- FastAPI app `backend.main:app`
- Host `0.0.0.0`
- Port `80`
- Deployment SQLite path `skillforge/db/skillforge.db`

Production-style startup and `/health` request passed locally. The project is
configured for publishing; no publish action was executed automatically.

## Final scope status

- Phases 1–12: implemented and tested.
- Phase 13: permanently omitted by design; no API key, LLM client, prompt
  layer, or fake explanation step.
- Phase 14: implemented and live-smoke-tested.
- Phase 15: omitted by plan; frontend is built separately in Lovable.
- Phases 16–17: evaluation documentation and basic deployment configuration
  complete.

## Rule reminders (from user's own spec, keep following these)
- One phase at a time; confirm before moving to the next.
- Never fabricate evaluation results or invent skills the system didn't compute.
- `SKILLFORGE_DB_PATH=db/skillforge.db` must be set for all local runs.
