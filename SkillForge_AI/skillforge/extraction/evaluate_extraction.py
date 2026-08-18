"""
SkillForge AI — Phase 6 evaluation.

Runs the Stage 1 dictionary matcher, Stage 2 spaCy EntityRuler, and Stage 3
fine-tuned DistilBERT against four held-out synthetic resumes with ground
truth written by generate_phase6_resumes.py. Metrics are skill-level micro
precision/recall/F1, computed from actual extracted skill_ids.

Run from skillforge/:
    SKILLFORGE_DB_PATH=db/skillforge.db python extraction/evaluate_extraction.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection  # noqa: E402
from extraction.bert_ner_extractor import (  # noqa: E402
    build_training_examples,
    load_metadata,
    train_model,
)
from extraction.dictionary_matcher import extract_skills as dictionary_extract  # noqa: E402
from extraction.spacy_ner_extractor import extract_skills as spacy_extract  # noqa: E402
from parser.resume_parser import parse_resume  # noqa: E402


DATA_DIR = REPO_ROOT / "data" / "labeled_resumes"
METADATA_PATH = DATA_DIR / "ground_truth.json"
MODEL_DIR = DATA_DIR / "distilbert_skill_model"
RESULTS_PATH = REPO_ROOT / "evaluation" / "phase6_extraction_results.json"


def _ensure_corpus() -> None:
    if METADATA_PATH.exists() and len(list(DATA_DIR.glob("phase6_resume_*.pdf"))) == 18:
        return
    from sample_resumes.generate_phase6_resumes import generate
    generate()


def _skill_ids(matches: list[dict]) -> set[int]:
    return {int(match["skill_id"]) for match in matches}


def _metrics(predicted: set[int], expected: set[int]) -> dict:
    tp = len(predicted & expected)
    fp = len(predicted - expected)
    fn = len(expected - predicted)
    return _metrics_from_counts(tp, fp, fn)


def _metrics_from_counts(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def run() -> dict:
    print("=" * 72)
    print("SkillForge AI — Phase 6: extraction evaluation")
    print("=" * 72)
    _ensure_corpus()
    records = load_metadata(METADATA_PATH)
    train_records = [record for record in records if record["split"] == "train"]
    heldout_records = [record for record in records if record["split"] == "heldout"]
    conn = get_connection()
    try:
        if not (MODEL_DIR / "config.json").exists():
            print(f"Training DistilBERT on {len(train_records)} synthetic resumes...")
            examples = build_training_examples(train_records, conn=conn)
            training_metrics = train_model(examples, MODEL_DIR, epochs=3)
        else:
            training_metrics = json.loads((MODEL_DIR / "training_metrics.json").read_text(encoding="utf-8"))
            print(f"Using saved DistilBERT model ({training_metrics['epochs']} epochs).")

        from extraction.bert_ner_extractor import BertSkillExtractor
        bert = BertSkillExtractor(MODEL_DIR)
        stage_matches = {"dictionary": [], "spacy": [], "distilbert": []}
        per_resume = []
        for record in heldout_records:
            pdf_path = DATA_DIR / record["filename"]
            parsed = parse_resume(str(pdf_path))
            expected_names = set(record["skills"])
            expected_ids = {
                int(row["skill_id"] if isinstance(row, dict) else row[0])
                for name in expected_names
                for row in conn.execute("SELECT skill_id FROM skills WHERE name = ?", (name,)).fetchall()
            }
            predictions = {
                "dictionary": dictionary_extract(parsed["sections"], conn=conn),
                "spacy": spacy_extract(parsed["sections"], conn=conn),
                "distilbert": bert.extract_skills(parsed["sections"], conn=conn),
            }
            row = {"filename": record["filename"], "expected_skill_count": len(expected_ids), "stages": {}}
            for stage, matches in predictions.items():
                stage_matches[stage].extend(matches)
                row["stages"][stage] = {
                    "predicted_skill_count": len(_skill_ids(matches)),
                    **_metrics(_skill_ids(matches), expected_ids),
                }
            per_resume.append(row)
            print(f"  {record['filename']}: expected={len(expected_ids)} " +
                  ", ".join(f"{stage} F1={row['stages'][stage]['f1']:.4f}" for stage in predictions))

        expected_total = sum(row["expected_skill_count"] for row in per_resume)
        # Micro-average the actual per-resume decisions. A skill mentioned in
        # two resumes counts twice, and false positives are never hidden by a
        # union over the corpus.
        aggregate = {}
        for stage in stage_matches:
            tp = sum(row["stages"][stage]["true_positive"] for row in per_resume)
            fp = sum(row["stages"][stage]["false_positive"] for row in per_resume)
            fn = sum(row["stages"][stage]["false_negative"] for row in per_resume)
            aggregate[stage] = _metrics_from_counts(tp, fp, fn)
        results = {
            "evaluation_type": "synthetic held-out skill-level micro evaluation",
            "heldout_resumes": len(heldout_records),
            "heldout_ground_truth_mentions": expected_total,
            "training": training_metrics,
            "aggregate_micro_metrics": aggregate,
            "per_resume": per_resume,
            "winner_by_f1": max(aggregate, key=lambda stage: aggregate[stage]["f1"]),
            "limitations": [
                "Ground truth is synthetic and skill-level, not token-level annotation from real resumes.",
                "DistilBERT learned weak labels produced by the Phase 5 dictionary matcher.",
                "The four held-out resumes are generated from the same controlled corpus family.",
            ],
        }
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print("\nCorpus-level micro metrics (actual held-out predictions):")
        print(f"{'Stage':<16} {'Precision':>10} {'Recall':>10} {'F1':>10}")
        print("-" * 50)
        for stage, metric in aggregate.items():
            print(f"{stage:<16} {metric['precision']:>10.4f} {metric['recall']:>10.4f} {metric['f1']:>10.4f}")
        print(f"\nWinner by F1: {results['winner_by_f1']}")
        print(f"Saved evaluation: {RESULTS_PATH}")
        return results
    finally:
        conn.close()


if __name__ == "__main__":
    run()