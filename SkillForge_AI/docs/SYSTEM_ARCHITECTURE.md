# SkillForge AI — System Architecture

## As-built scope

This document describes the implemented Phases 3–14 pipeline. The system is
deterministic at every decision point: parsing, skill extraction,
normalization, career ranking, gap arithmetic, and learning-path ordering do
not delegate decisions to an LLM. Phase 13's explanation layer is omitted by
design.

## Three-layer architecture

```mermaid
flowchart LR
    subgraph CORE["Deterministic Core"]
        PARSE["PDF parsing<br/>PyMuPDF / pdfplumber<br/>cleaning / section detection"]
        EXTRACT["Skill extraction<br/>dictionary + regex live path<br/>spaCy / DistilBERT evaluated in Phase 6"]
        NORMALIZE["Skill normalization<br/>alias → full-string fuzzy →<br/>calibrated semantic fallback"]
        PARSE --> EXTRACT --> NORMALIZE
    end

    subgraph REASON["Recommendation & Reasoning"]
        MATCH["Career matching<br/>importance-weighted vectors<br/>cosine similarity"]
        GAP["Gap analysis<br/>importance × proficiency deficit"]
        PATH["Learning path<br/>NetworkX prerequisite order<br/>gap-priority tie-breaking"]
        MATCH --> GAP --> PATH
    end

    subgraph INTERACTION["Interaction Layer"]
        API["FastAPI routes<br/>request-scoped DB access"]
        UI["Static HTML/CSS/vanilla JS<br/>served at /"]
        API --> UI
    end

    NORMALIZE --> MATCH
    PATH --> API
    OMITTED["LLM explanation layer<br/>Phase 13 omitted by design"]:::omitted
    OMITTED -.-> API

    classDef omitted fill:#fff2f2,stroke:#b42318,color:#8b1e2d,stroke-dasharray: 5 5;
```

The live API profile route currently persists dictionary matches directly.
Phase 7 normalization and the Phase 6 NER models are real project modules and
evaluation artifacts, but they are not an unconditionally chained runtime
stage in the Phase 14 upload handler.

## Full data pipeline: Phases 3–14

The solid path below is the live resume-upload and agent path. Dashed nodes
are real offline evaluation/calibration or reusable supporting modules that
were built during the corresponding phase but are not all invoked by the
single live upload handler.

```mermaid
flowchart TD
    UPLOAD["POST /profile/resume<br/>multipart PDF"] --> P14_PROFILE["Phase 14<br/>backend.profile.upload_resume"]

    P3["Phase 3<br/>schema.sql + seed_data.py<br/>SQLite knowledge base"] --> P14_PROFILE
    P14_PROFILE --> P4["Phase 4<br/>parser.resume_parser.parse_resume"]
    P4 --> PDF["pdf_extractor.py<br/>PyMuPDF primary + pdfplumber fallback"]
    PDF --> CLEAN["text_cleaner.py"]
    CLEAN --> SECTION["section_detector.py"]
    SECTION --> P5["Phase 5<br/>extraction.dictionary_matcher.extract_skills"]
    P5 --> STORE["Persist users / resumes / user_skills<br/>db_client transaction"]
    STORE --> LOAD["Phase 14 dependencies.py<br/>load persisted user profile"]
    LOAD --> ORCH["Phase 12 agent.orchestrator.orchestrate"]
    ORCH --> PA["profile_agent.py"]
    PA --> CA["career_agent.py"]
    CA --> REC["Phase 9<br/>ContentBasedRecommender + vectorizer"]
    REC --> SGA["skill_gap_agent.py"]
    SGA --> GA["Phase 10<br/>gap_analysis.gap_analyzer"]
    GA --> LA["learning_agent.py"]
    LA --> GRAPH["Phase 8<br/>knowledge_base.skill_graph<br/>NetworkX prerequisite graph"]
    GRAPH --> LP["Phase 11<br/>learning_path.learning_path"]
    LP --> PROG["progress_agent.py"]
    PROG --> RESPONSE["AgentRunResponse<br/>profile + career + gap + learning + progress"]
    RESPONSE --> API["Phase 14<br/>POST /agent/{user_id}/run"]

    P6["Phase 6 offline/evaluation<br/>spacy_ner_extractor.py<br/>bert_ner_extractor.py<br/>evaluate_extraction.py"] -.-> P5
    P7["Phase 7 calibration/support<br/>alias_matcher.py<br/>fuzzy_matcher.py<br/>semantic_matcher.py<br/>threshold_calibration.py"] -.-> P5
    P8["Phase 8 reusable graph checks<br/>cycle detection + topological order"] -.-> GRAPH
    P13["Phase 13<br/>LLM layer omitted by design"]:::omitted -.-> RESPONSE

    classDef omitted fill:#fff2f2,stroke:#b42318,color:#8b1e2d,stroke-dasharray: 5 5;
```

## Entity-relationship diagram

The actual on-disk schema contains **nine tables**, as confirmed by
`skillforge/schema.sql` and the SQLite database. The uploaded documentation
brief listed `learning_paths` as an additional name while calling the schema
nine-table; there is no `learning_paths` table in the implementation.
Learning paths are computed in memory by the Phase 11 module and returned in
`RoadmapResponse` and `AgentRunResponse`.

```mermaid
erDiagram
    SKILLS {
        int skill_id PK
        text name UK
        text category
        text subcategory
        int difficulty
        text description
    }
    SKILL_ALIASES {
        int alias_id PK
        int skill_id FK
        text alias_text
    }
    SKILL_PREREQUISITES {
        int from_skill_id PK,FK
        int to_skill_id PK,FK
        text relation_type
    }
    CAREERS {
        int career_id PK
        text name UK
        text description
    }
    CAREER_SKILL_REQUIREMENTS {
        int career_id PK,FK
        int skill_id PK,FK
        int importance
        int minimum_proficiency
        int preferred_proficiency
    }
    USERS {
        int user_id PK
        text username UK
        text email UK
        timestamp created_at
    }
    RESUMES {
        int resume_id PK
        int user_id FK
        text file_path
        text raw_text
        timestamp parsed_at
    }
    USER_SKILLS {
        int user_id PK,FK
        int skill_id PK,FK
        int proficiency
        text source
        timestamp updated_at
    }
    RECOMMENDATIONS {
        int rec_id PK
        int user_id FK
        int career_id FK
        real score
        timestamp created_at
    }

    SKILLS ||--o{ SKILL_ALIASES : "has aliases"
    SKILLS ||--o{ SKILL_PREREQUISITES : "is prerequisite source"
    SKILLS ||--o{ SKILL_PREREQUISITES : "is dependent target"
    CAREERS ||--o{ CAREER_SKILL_REQUIREMENTS : "requires"
    SKILLS ||--o{ CAREER_SKILL_REQUIREMENTS : "is required by"
    USERS ||--o{ RESUMES : "uploads"
    USERS ||--o{ USER_SKILLS : "has profile skills"
    SKILLS ||--o{ USER_SKILLS : "appears in profiles"
    USERS ||--o{ RECOMMENDATIONS : "receives"
    CAREERS ||--o{ RECOMMENDATIONS : "is ranked"
```

## As-built module tree

```text
skillforge/
├── schema.sql                         Phase 3: nine-table source schema
├── data/
│   ├── seed_data.py                   Phase 3: curated taxonomy and careers
│   ├── *_export.json                  Phase 3: table snapshots
│   └── labeled_resumes/               Phase 6: synthetic labels and PDFs
├── db/
│   ├── init_db.py                     Phase 3: SQLite initialization/validation
│   └── db_client.py                   SQLite/Postgres access abstraction
├── parser/
│   ├── pdf_extractor.py               Phase 4: PDF text extraction
│   ├── text_cleaner.py                Phase 4: text normalization
│   ├── section_detector.py            Phase 4: resume section detection
│   └── resume_parser.py               Phase 4: parser entry point
├── extraction/
│   ├── dictionary_matcher.py          Phase 5: deterministic live extractor
│   ├── spacy_ner_extractor.py         Phase 6: EntityRuler evaluation stage
│   ├── bert_ner_extractor.py          Phase 6: DistilBERT evaluation stage
│   └── evaluate_extraction.py         Phase 6: held-out metrics
├── normalization/
│   ├── alias_matcher.py               Phase 7: exact alias resolution
│   ├── fuzzy_matcher.py               Phase 7: full-string RapidFuzz fallback
│   ├── semantic_matcher.py            Phase 7: calibrated semantic fallback
│   ├── threshold_calibration.py       Phase 7: saved cutoff calibration
│   └── normalization_pipeline.py      Phase 7: deterministic ordering
├── knowledge_base/
│   └── skill_graph.py                 Phase 8: in-memory NetworkX graph
├── recommendation/
│   ├── vectorizer.py                  Phase 9: weighted vector construction
│   ├── content_based_recommender.py   Phase 9: career ranking
│   └── evaluate_recommender.py        Phase 9: face-validity fixtures
├── gap_analysis/
│   └── gap_analyzer.py                Phase 10: gap arithmetic and buckets
├── learning_path/
│   └── learning_path.py               Phase 11: prerequisite-safe ordering
├── agent/
│   ├── profile_agent.py               Phase 12: profile stage
│   ├── career_agent.py                Phase 12: career stage
│   ├── skill_gap_agent.py             Phase 12: gap stage
│   ├── learning_agent.py              Phase 12: learning stage
│   ├── progress_agent.py              Phase 12: coverage summary
│   └── orchestrator.py                Phase 12: final structured pipeline
├── backend/
│   ├── main.py                        Phase 14: FastAPI app and static mount
│   ├── profile.py                     Phase 14: upload/profile route
│   ├── careers.py                     Phase 14: recommendations route
│   ├── gap.py                         Phase 14: gap route
│   ├── roadmap.py                     Phase 14: roadmap route
│   ├── agent.py                       Phase 14: direct Phase 12 route
│   └── static/index.html              Current lightweight interaction surface
├── [Phase 13 omitted]                 No LLM client, prompts, guardrails, or API key
└── [Phase 15 omitted by design]       Original separate/full frontend scope deferred;
                                      the current static page is not that scope
```

## Persistence and runtime boundaries

- `SKILLFORGE_DB_PATH` selects the SQLite database; this avoids accidentally
  selecting an unrelated platform `DATABASE_URL` during local runs.
- FastAPI dependencies create request-scoped connections through `db_client`.
- The learning path is not persisted in a `learning_paths` table; it is derived
  from the gap report and NetworkX graph on request.
- The artifact runner sets the repository-relative database and Python paths so
  the production command is portable.