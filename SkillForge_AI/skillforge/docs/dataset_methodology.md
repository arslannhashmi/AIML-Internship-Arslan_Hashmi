# SkillForge AI — Dataset Methodology

## Scope

SkillForge is evaluated as a deterministic resume-skill extraction and career
reasoning pipeline. The knowledge base and resume corpus are controlled,
hand-built project data rather than a statistically sampled labour-market
dataset.

## Knowledge-base construction

The seeded SQLite knowledge base contains:

| Resource | Count | Construction |
|---|---:|---|
| Canonical skills | 101 | Hand-curated technology taxonomy |
| Skill aliases | 26 | Hand-curated abbreviations and alternate forms |
| Careers | 15 | Hand-curated role set |
| Prerequisite edges | 62 | Domain-judged learning relationships |
| Career-skill requirements | 116 | Expert-assigned importance and proficiency targets |

Skills were selected from widely used technology taxonomies, including the
LinkedIn Skills taxonomy and Stack Overflow Developer Survey 2023, then
reduced to a scope that is defensible for a single FYP project.

Career-skill importance values are assigned on a 1–5 scale:

- `1`: nice-to-have
- `5`: essential

Career requirements also contain a 1–5 minimum proficiency and preferred
proficiency. These values represent a transparent expert-curated rubric; they
are not mined from job-posting frequencies.

Prerequisite edges are represented in NetworkX as prerequisite → dependent.
They are domain-expert learning-order judgements, not relationships learned
from learner histories.

## Resume corpus

Phase 4 created three synthetic PDF resumes covering Data Science, Frontend,
and DevOps profiles. Phase 6 added 18 labelled synthetic resumes:

| Split | Count | Use |
|---|---:|---|
| Training | 14 | Weak-supervision training data |
| Held out | 4 | Skill-level extraction evaluation |

The held-out evaluation contains 39 ground-truth skill mentions. The labels
were generated from the Phase 5 dictionary matcher and then stored in
`data/labeled_resumes/ground_truth.json`.

## Normalization data

Phase 7 calibration uses labelled equivalent/different skill pairs. The
semantic model is `sentence-transformers/all-MiniLM-L6-v2`, loaded directly
through raw Transformers with mean pooling because the `sentence-transformers`
wrapper package was unavailable in the package index.

## Recommendation evaluation data

Phase 9 uses three hand-built profiles:

- Data Science → Data Scientist
- Frontend → Frontend Developer
- DevOps → DevOps Engineer

These fixtures test face validity only: whether obvious profiles produce
plausible top-ranked careers. They are not a representative sample and are
not an accuracy benchmark.

## Reproducibility

Local runs use:

```text
SKILLFORGE_DB_PATH=db/skillforge.db
```

The authoritative metric files are:

- `evaluation/phase6_extraction_results.json`
- `evaluation/phase7_threshold_calibration.json`
- `evaluation/phase9_face_validity_results.json`