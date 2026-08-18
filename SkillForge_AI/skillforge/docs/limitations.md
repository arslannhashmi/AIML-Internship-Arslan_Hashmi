# SkillForge AI — Limitations and Scope

## Evaluation limitations

### Synthetic and circular extraction evaluation

Phase 6 and Phase 7 evaluation is circular by construction: synthetic resumes
were generated from the same 101-skill taxonomy that the Phase 5 dictionary
matcher uses. Phase 6 weak labels were also generated from that dictionary
matcher. The reported results therefore demonstrate controlled-pipeline
behaviour, not real-resume generalization.

The four held-out resumes are from the same controlled corpus family. The
ground truth is skill-level and synthetic, not token-level annotation from
independently labelled real resumes.

### DistilBERT scope

DistilBERT is the only deep-learning component. Its saved held-out results
were precision `1.0000`, recall `0.8974`, and F1 `0.9459`; the dictionary and
spaCy baselines each achieved F1 `1.0000` on this controlled set. The
dictionary baseline therefore won this evaluation. These numbers must not be
presented as real-world model performance.

DistilBERT was trained from weak labels produced by the Phase 5 dictionary
matcher, so it does not provide an independent annotation source.

### Semantic normalization scope

The `sentence-transformers` wrapper package was unavailable, so Sentence-BERT
was implemented directly via raw Transformers plus mean pooling. The
`all-MiniLM-L6-v2` checkpoint is real, but this implementation choice and the
small calibration set limit claims about broad semantic matching.

### Recommendation evaluation scope

Phase 9 uses hand-built profiles and is explicitly **face-validity testing,
not accuracy evaluation**. It contains three illustrative cases and does not
support claims about ranking accuracy, precision, recall, or generalization.

### Knowledge-base scope

Career requirements, importance weights, proficiency targets, and prerequisite
edges are expert-curated project assumptions. They are not learned from
employment outcomes or a corpus of job advertisements.

## Product scope decisions

### Phase 13 omitted by design

The Phase 13 LLM layer was omitted intentionally. No API key is provided or
required for this project. There is no prompt-generation, LLM-client, or
explanation fallback step. Phase 12's deterministic structured JSON is the
final pipeline output.

### Phase 15 omitted by plan

The frontend is intentionally omitted from this repository and will be built
separately in Lovable.

### Deployment limitations

The basic FastAPI deployment uses the existing SQLite database abstraction and
the checked-in SQLite database path. This is intentionally simple for the FYP
checkpoint and is not a multi-instance production data architecture. A future
production system would need a durable shared database and a durable upload
store before horizontal scaling.

## Out of scope

Neo4j, K-Means clustering, the larger multi-agent framework, LLM narration,
real-resume benchmarking, and frontend implementation remain outside the
accepted project scope.