# SkillForge AI — API Reference

## Base URLs

- Local development: `http://localhost:8080`
- Published app: `https://skillforgeaitest.replit.app`

The static frontend is served at `/`. The examples below use the live local
workflow and a real `resume_2_frontend.pdf` upload already exercised against
the API. Response excerpts are selected fields from those actual responses;
`…` marks omitted repeated list items, not invented values.

## Route summary

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Service health and phase |
| POST | `/profile/resume` | Upload, parse, extract, and persist a resume profile |
| GET | `/careers/{user_id}/recommendations` | Rank careers for a persisted user profile |
| GET | `/gap/{user_id}/{career_id}` | Return requirement-level proficiency gaps |
| GET | `/roadmap/{user_id}/{career_id}` | Return a prerequisite-aware learning path |
| POST | `/agent/{user_id}/run` | Run the complete deterministic Phase 12 pipeline |

## `GET /health`

Returns a small service status object.

```bash
curl http://localhost:8080/health
```

Actual response:

```json
{
  "status": "ok",
  "phase": "14"
}
```

## `POST /profile/resume`

Uploads a PDF, parses it, extracts deterministic skill matches, persists the
user/resume/profile records, and returns a `ProfileResponse`.

### Request

```bash
curl -X POST http://localhost:8080/profile/resume \
  -F "file=@skillforge/sample_resumes/resume_2_frontend.pdf"
```

The optional multipart fields are `user_id`, `username`, and `email`. If no
identity fields are supplied, the endpoint creates an anonymous user identity.
The file field is required and must end in `.pdf`.

### Actual response excerpt

```json
{
  "user_id": 1,
  "skill_count": 19,
  "sections": [
    "_header",
    "experience",
    "education",
    "skills",
    "projects"
  ],
  "skills": [
    {
      "skill_id": 45,
      "canonical_name": "React",
      "proficiency": 1,
      "source": "resume",
      "matched_text": "React",
      "section": "experience",
      "char_span": [78, 83]
    },
    {
      "skill_id": 5,
      "canonical_name": "TypeScript",
      "proficiency": 1,
      "source": "resume",
      "matched_text": "TypeScript",
      "section": "experience",
      "char_span": [89, 99]
    },
    {
      "skill_id": 53,
      "canonical_name": "Redux",
      "proficiency": 1,
      "source": "resume",
      "matched_text": "Redux",
      "section": "experience",
      "char_span": [188, 193]
    },
    …
  ]
}
```

The complete response also contains `resume_id` and the remaining extracted
skills. Resume errors return `400` for an empty file, `415` for a non-PDF,
`413` for an oversized upload, and `422` when parsing or profiling fails.

## `GET /careers/{user_id}/recommendations`

Ranks the seeded careers for the persisted profile. `top_k` is optional and
defaults to `5`; it accepts values from `1` through `15`.

### Request

```bash
curl "http://localhost:8080/careers/1/recommendations?top_k=5"
```

### Actual response excerpt

```json
{
  "user_id": 1,
  "recommendations": [
    {
      "career_id": 4,
      "career_name": "Frontend Developer",
      "score": 0.9916560553218191,
      "matched_skill_ids": [4, 5, 43, 44, 45, 49, 52, 80],
      "required_skill_count": 8
    },
    {
      "career_id": 6,
      "career_name": "Full Stack Developer",
      "score": 0.9274588618735558,
      "matched_skill_ids": [4, 5, 45, 55, 60, 80],
      "required_skill_count": 8
    },
    {
      "career_id": 14,
      "career_name": "Mobile Developer",
      "score": 0.7828094515656506,
      "matched_skill_ids": [4, 5, 52, 60, 80],
      "required_skill_count": 7
    }
  ]
}
```

The actual live request returned five recommendations; the example shows its
first three. Unknown users return `404`.

## `GET /gap/{user_id}/{career_id}`

Computes gaps for a persisted profile against one career. The `career_id` is
the seeded career identifier; `4` is Frontend Developer in the live example.

### Request

```bash
curl http://localhost:8080/gap/1/4
```

### Actual response excerpt

```json
{
  "user_id": 1,
  "career_id": 4,
  "career_name": "Frontend Developer",
  "gaps": [
    {
      "skill_id": 4,
      "skill_name": "JavaScript",
      "importance": 5,
      "current_proficiency": 1.0,
      "minimum_proficiency": 4,
      "preferred_proficiency": 5,
      "proficiency_deficit": 4.0,
      "gap_score": 20.0,
      "bucket": "Critical"
    },
    {
      "skill_id": 5,
      "skill_name": "TypeScript",
      "importance": 4,
      "current_proficiency": 1.0,
      "minimum_proficiency": 2,
      "preferred_proficiency": 4,
      "proficiency_deficit": 3.0,
      "gap_score": 12.0,
      "bucket": "Major"
    },
    …
  ],
  "missing_skills": [
    …
  ]
}
```

The live example returned eight gap records. `missing_skills` contains the
records used to build the learning path; a skill can be present in the resume
and still appear there when its proficiency is below the target.

## `GET /roadmap/{user_id}/{career_id}`

Computes a learning path from the selected career's gap report and the
in-memory NetworkX prerequisite graph.

### Request

```bash
curl http://localhost:8080/roadmap/1/4
```

### Actual response excerpt

```json
{
  "user_id": 1,
  "career_id": 4,
  "career_name": "Frontend Developer",
  "skill_count": 8,
  "learning_path": [
    {"skill_name": "JavaScript", "gap_score": 20.0, "bucket": "Critical"},
    {"skill_name": "HTML", "gap_score": 20.0, "bucket": "Critical"},
    {"skill_name": "CSS", "gap_score": 20.0, "bucket": "Critical"},
    {"skill_name": "React", "gap_score": 20.0, "bucket": "Critical"},
    {"skill_name": "TypeScript", "gap_score": 12.0, "bucket": "Major"},
    {"skill_name": "Git", "gap_score": 12.0, "bucket": "Major"},
    {"skill_name": "Tailwind CSS", "gap_score": 9.0, "bucket": "Moderate"},
    {"skill_name": "Jest", "gap_score": 6.0, "bucket": "Moderate"}
  ]
}
```

Each learning-path item is a `GapItem`. The ordering preserves prerequisites
before selecting among currently unlocked skills by larger gap score and then
skill ID.

## `POST /agent/{user_id}/run`

Runs the complete deterministic pipeline against the persisted profile. It
returns the Phase 12 structure directly and does not add a generated
explanation field.

### Request

```bash
curl -X POST http://localhost:8080/agent/1/run
```

### Actual response excerpt

```json
{
  "pipeline": "SkillForge AI",
  "pipeline_version": "phase12",
  "sequence": ["profile", "career", "gap", "learning"],
  "profile": {
    "stage": "profile",
    "skill_count": 19
  },
  "career": {
    "stage": "career",
    "selected_career": {
      "career_id": 4,
      "career_name": "Frontend Developer",
      "score": 0.9916560553218191,
      "required_skill_count": 8
    }
  },
  "skill_gap": {
    "stage": "gap",
    "career_id": 4,
    "career_name": "Frontend Developer",
    "gaps": ["…"]
  },
  "learning": {
    "stage": "learning",
    "career_name": "Frontend Developer",
    "skill_count": 8
  },
  "progress": {
    "stage": "progress",
    "career_name": "Frontend Developer"
  }
}
```

The complete response contains the full profile, recommendation list, eight
gap records, eight learning-path records, and the progress coverage fields.
The route returns `404` when the user does not exist.

## Response models

The Pydantic models in `skillforge/backend/schemas.py` define the public
contract:

- `ProfileResponse` → `ProfileSkill[]`
- `CareerRecommendationsResponse` → `CareerRecommendation[]`
- `GapResponse` → `GapItem[]`
- `RoadmapResponse` → `GapItem[]`
- `AgentRunResponse` → `pipeline`, `sequence`, and the five structured stages
