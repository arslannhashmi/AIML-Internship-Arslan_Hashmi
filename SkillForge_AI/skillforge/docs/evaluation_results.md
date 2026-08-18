# SkillForge AI — Evaluation Results

All numbers in this report are copied from saved evaluation artifacts or from
the existing Phase 9 evaluator output. No metrics were re-derived or
fabricated.

## Phase 6 — Extraction

Source: `evaluation/phase6_extraction_results.json`

Evaluation type: synthetic held-out skill-level micro evaluation  
Held-out resumes: 4  
Ground-truth mentions: 39  
DistilBERT training examples: 70  
Training epochs: 3

### Aggregate metrics

| Stage | True positive | False positive | False negative | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Dictionary baseline | 39 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| spaCy EntityRuler | 39 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| DistilBERT NER | 35 | 0 | 4 | 1.0000 | 0.8974 | 0.9459 |

Winner by F1: **dictionary baseline**.

### DistilBERT training loss

| Epoch | Loss |
|---:|---:|
| 1 | 0.1931835584756401 |
| 2 | 0.0733108561899927 |
| 3 | 0.04826043359935284 |

These are controlled synthetic results and are not real-resume
generalization metrics.

## Phase 7 — Normalization calibration

Source: `evaluation/phase7_threshold_calibration.json`

Model: `sentence-transformers/all-MiniLM-L6-v2`, implemented through raw
Transformers with mean pooling.

| Measurement | Value |
|---|---:|
| Positive score minimum | 0.3420 |
| Positive score maximum | 1.0000 |
| Negative score minimum | 0.0673 |
| Negative score maximum | 0.3226 |
| Chosen threshold | 0.3323 |
| Calibration F1 | 1.0000 |

The threshold was selected using the candidate cutoff with the best F1 on the
labelled equivalent/different pairs.

## Phase 9 — Career recommendation

Source: `evaluation/phase9_face_validity_results.json`, generated from the
existing hand-built evaluator.

Evaluation type: **face-validity testing (not accuracy evaluation)**.

| Profile | Expected career | Top career | Cosine score | Result |
|---|---|---|---:|---|
| Data Science | Data Scientist | Data Scientist | 1.0 | PASS |
| Frontend | Frontend Developer | Frontend Developer | 0.9999999999999998 | PASS |
| DevOps | DevOps Engineer | DevOps Engineer | 1.0 | PASS |

Face-validity result: **3/3 passed**.

## Functional checkpoint outputs

| Checkpoint | Verification | Actual result |
|---|---|---|
| Phase 5 | Dictionary extraction tests | 56/56 passed |
| Checkpoint 2 | Normalization and graph tests | 8/8 passed |
| Checkpoint 3 | Recommendation, gap, and learning tests | 8/8 passed |
| Phase 12 | Deterministic agent tests | 8/8 passed |
| Phase 14 | Python compilation | PASS |
| Phase 14 | Database query sanity suite | ALL PASS |
| Phase 14 | Live FastAPI health/upload/recommendation/gap/roadmap/agent flow | PASS |

## Phase 14 live API smoke result

The FastAPI backend started under Uvicorn. A real synthetic frontend PDF
returned HTTP 200 with a structured profile containing 19 extracted skills.
The live recommendation endpoint ranked Frontend Developer first with score
`0.9916560553218191`. Gap analysis, roadmap, and the direct Phase 12 agent
endpoint each returned HTTP 200.

## Interpretation boundary

No accuracy, precision, recall, or F1 number is claimed for career
recommendation. No real-resume generalization claim is made for extraction or
normalization. Phase 13 LLM evaluation does not exist because that phase was
intentionally omitted.