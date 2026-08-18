"""Empirically choose the semantic cosine cutoff from labelled pairs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection  # noqa: E402
from normalization.semantic_matcher import SemanticMatcher  # noqa: E402

POSITIVE_PAIRS = [
    ("ML", "Machine Learning"),
    ("Machine-Learning", "Machine Learning"),
    ("ReactJS", "React"),
    ("Postgres", "PostgreSQL"),
    ("K8s", "Kubernetes"),
    ("TF", "TensorFlow"),
    ("REST API", "REST API Design"),
    ("data visualization", "Data Visualization"),
]
NEGATIVE_PAIRS = [
    ("Machine Learning", "HTML"),
    ("React", "Kubernetes"),
    ("PostgreSQL", "TensorFlow"),
    ("Docker", "Statistics"),
    ("Python", "CSS"),
    ("GraphQL", "Prometheus"),
    ("AWS", "Natural Language Processing"),
    ("Jest", "Terraform"),
]


def _best_f1(positive: list[float], negative: list[float]) -> tuple[float, float]:
    scores = sorted(set(positive + negative))
    candidates = [0.0] + [(scores[i] + scores[i + 1]) / 2 for i in range(len(scores) - 1)] + [1.0]
    best = (0.0, -1.0)
    for threshold in candidates:
        tp = sum(score >= threshold for score in positive)
        fp = sum(score >= threshold for score in negative)
        fn = len(positive) - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        if f1 > best[1]:
            best = (threshold, f1)
    return best


def calibrate(matcher: SemanticMatcher) -> dict:
    positive_scores = [
        matcher.similarity(left, right) for left, right in POSITIVE_PAIRS
    ]
    negative_scores = [
        matcher.similarity(left, right) for left, right in NEGATIVE_PAIRS
    ]
    threshold, f1 = _best_f1(positive_scores, negative_scores)
    result = {
        "model": matcher.model_name,
        "positive_scores": [round(value, 4) for value in positive_scores],
        "negative_scores": [round(value, 4) for value in negative_scores],
        "positive_min": round(min(positive_scores), 4),
        "positive_max": round(max(positive_scores), 4),
        "negative_min": round(min(negative_scores), 4),
        "negative_max": round(max(negative_scores), 4),
        "chosen_threshold": round(threshold, 4),
        "calibration_f1": round(f1, 4),
        "reasoning": "Threshold chosen by the candidate cutoff with the best F1 on labelled equivalent/different pairs, not by an arbitrary constant.",
    }
    return result


if __name__ == "__main__":
    conn = get_connection()
    try:
        matcher = SemanticMatcher(conn=conn)
        result = calibrate(matcher)
    finally:
        conn.close()
    output = REPO_ROOT / "evaluation" / "phase7_threshold_calibration.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Sentence-BERT threshold calibration")
    print(f"  Positive score range: {result['positive_min']:.4f}–{result['positive_max']:.4f}")
    print(f"  Negative score range: {result['negative_min']:.4f}–{result['negative_max']:.4f}")
    print(f"  Chosen cutoff: {result['chosen_threshold']:.4f}")
    print(f"  Calibration F1: {result['calibration_f1']:.4f}")
    print(f"  Reason: {result['reasoning']}")
    print(f"  Saved: {output}")