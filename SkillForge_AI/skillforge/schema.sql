-- SkillForge AI — Phase 3: Postgres-compatible schema
-- 9 tables: 5 static knowledge-base tables + 4 runtime user-data tables.
-- db/init_db.py translates Postgres syntax to SQLite at build time
-- (SERIAL → INTEGER, TEXT[] → TEXT, etc.).

-- ─── Static knowledge-base tables ────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS skills (
    skill_id    SERIAL PRIMARY KEY,
    name        TEXT    NOT NULL UNIQUE,
    category    TEXT    NOT NULL,
    subcategory TEXT,
    difficulty  INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    description TEXT
);

CREATE TABLE IF NOT EXISTS skill_aliases (
    alias_id  SERIAL PRIMARY KEY,
    skill_id  INTEGER NOT NULL REFERENCES skills (skill_id) ON DELETE CASCADE,
    alias_text TEXT   NOT NULL,
    UNIQUE (skill_id, alias_text)
);

-- relation_type: 'prerequisite' (from must be learned before to)
--                'related'      (complementary but not required)
CREATE TABLE IF NOT EXISTS skill_prerequisites (
    from_skill_id INTEGER NOT NULL REFERENCES skills (skill_id) ON DELETE CASCADE,
    to_skill_id   INTEGER NOT NULL REFERENCES skills (skill_id) ON DELETE CASCADE,
    relation_type TEXT    NOT NULL CHECK (relation_type IN ('prerequisite', 'related')),
    PRIMARY KEY (from_skill_id, to_skill_id)
);

CREATE TABLE IF NOT EXISTS careers (
    career_id   SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

-- importance/proficiency columns use a 1–5 scale throughout:
--   importance:           1 = nice-to-have … 5 = essential
--   minimum_proficiency:  the floor a candidate needs to be hireable
--   preferred_proficiency: the target for a strong candidate
CREATE TABLE IF NOT EXISTS career_skill_requirements (
    career_id            INTEGER NOT NULL REFERENCES careers (career_id) ON DELETE CASCADE,
    skill_id             INTEGER NOT NULL REFERENCES skills  (skill_id)  ON DELETE CASCADE,
    importance           INTEGER NOT NULL CHECK (importance            BETWEEN 1 AND 5),
    minimum_proficiency  INTEGER NOT NULL CHECK (minimum_proficiency   BETWEEN 1 AND 5),
    preferred_proficiency INTEGER NOT NULL CHECK (preferred_proficiency BETWEEN 1 AND 5),
    PRIMARY KEY (career_id, skill_id)
);

-- ─── Runtime user-data tables ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    user_id    SERIAL PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
    resume_id    SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    file_path    TEXT    NOT NULL,
    raw_text     TEXT,
    parsed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- proficiency: self-reported or inferred 1–5 scale
CREATE TABLE IF NOT EXISTS user_skills (
    user_id     INTEGER NOT NULL REFERENCES users  (user_id)  ON DELETE CASCADE,
    skill_id    INTEGER NOT NULL REFERENCES skills (skill_id) ON DELETE CASCADE,
    proficiency INTEGER NOT NULL DEFAULT 1 CHECK (proficiency BETWEEN 1 AND 5),
    source      TEXT    NOT NULL DEFAULT 'resume',  -- 'resume' | 'manual' | 'inferred'
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    rec_id      SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users   (user_id)   ON DELETE CASCADE,
    career_id   INTEGER NOT NULL REFERENCES careers (career_id) ON DELETE CASCADE,
    score       REAL    NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
