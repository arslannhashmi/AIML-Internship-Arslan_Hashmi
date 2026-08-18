"""
SkillForge AI — Phase 6: Stage 3 DistilBERT token-classification extractor.

Training labels are weak supervision from dictionary_matcher.py.  The model
predicts generic SKILL spans; predicted spans are resolved back to canonical
database skills using the same alias vocabulary for evaluation and downstream
use.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from db.db_client import get_connection  # noqa: E402
from extraction.dictionary_matcher import extract_skills as dictionary_extract_skills  # noqa: E402
from parser.resume_parser import parse_resume  # noqa: E402


MODEL_NAME = "distilbert-base-uncased"
LABELS = {"O": 0, "B-SKILL": 1, "I-SKILL": 2}
ID_TO_LABEL = {value: key for key, value in LABELS.items()}


def load_metadata(metadata_path: str | Path) -> list[dict]:
    return json.loads(Path(metadata_path).read_text(encoding="utf-8"))


def _section_examples(pdf_path: str | Path, conn) -> list[dict]:
    parsed = parse_resume(str(pdf_path))
    matches = dictionary_extract_skills(parsed["sections"], conn=conn)
    examples = []
    for section, text in parsed["sections"].items():
        if not text.strip():
            continue
        examples.append({
            "section": section,
            "text": text,
            "matches": [match for match in matches if match["section"] == section],
        })
    return examples


def build_training_examples(records: Iterable[dict], conn=None) -> list[dict]:
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        examples = []
        for record in records:
            pdf_path = REPO_ROOT / "data" / "labeled_resumes" / record["filename"]
            examples.extend(_section_examples(pdf_path, conn))
        return examples
    finally:
        if own_conn:
            conn.close()


def _labels_for_offsets(offsets, matches: list[dict]) -> list[int]:
    labels = [LABELS["O"]] * len(offsets)
    for match in matches:
        start, end = match["char_span"]
        overlapping = [
            index for index, (token_start, token_end) in enumerate(offsets)
            if token_end > token_start and token_start < end and token_end > start
        ]
        if not overlapping:
            continue
        labels[overlapping[0]] = LABELS["B-SKILL"]
        for index in overlapping[1:]:
            labels[index] = LABELS["I-SKILL"]
    return labels


class _TokenDataset(torch.utils.data.Dataset):
    def __init__(self, rows: list[dict]):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        return {key: torch.tensor(value, dtype=torch.long) for key, value in row.items()}


def _tokenize_examples(examples: list[dict], tokenizer, max_length: int = 256) -> list[dict]:
    rows = []
    for example in examples:
        encoded = tokenizer(
            example["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_offsets_mapping=True,
        )
        labels = _labels_for_offsets(encoded.pop("offset_mapping"), example["matches"])
        labels = labels[:max_length] + [LABELS["O"]] * max(0, max_length - len(labels))
        rows.append({
            "input_ids": encoded["input_ids"],
            "attention_mask": encoded["attention_mask"],
            "labels": labels,
        })
    return rows


def train_model(
    training_examples: list[dict],
    output_dir: str | Path,
    *,
    epochs: int = 3,
    batch_size: int = 4,
    max_length: int = 256,
) -> dict:
    """Fine-tune DistilBERT once and save the tokenizer/model locally."""
    if not 1 <= epochs <= 5:
        raise ValueError("Phase 6 training is bounded to 1–5 epochs")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label=ID_TO_LABEL,
        label2id=LABELS,
    )
    rows = _tokenize_examples(training_examples, tokenizer, max_length=max_length)
    if not rows:
        raise ValueError("No training examples were produced")
    loader = torch.utils.data.DataLoader(_TokenDataset(rows), batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
    model.train()
    losses = []
    for epoch in range(epochs):
        epoch_losses = []
        for batch in loader:
            optimizer.zero_grad()
            output = model(**batch)
            output.loss.backward()
            optimizer.step()
            epoch_losses.append(float(output.loss.detach().cpu()))
        losses.append(sum(epoch_losses) / len(epoch_losses))
        print(f"  BERT epoch {epoch + 1}/{epochs}: loss={losses[-1]:.4f}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    metrics = {
        "model_name": MODEL_NAME,
        "epochs": epochs,
        "training_examples": len(rows),
        "loss_by_epoch": losses,
        "max_length": max_length,
    }
    (output_dir / "training_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


class BertSkillExtractor:
    def __init__(self, model_dir: str | Path):
        self.model_dir = Path(model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, use_fast=True)
        self.model = AutoModelForTokenClassification.from_pretrained(self.model_dir)
        self.model.eval()

    def extract_skills(self, sections: dict[str, str], *, conn=None) -> list[dict]:
        own_conn = conn is None
        if own_conn:
            conn = get_connection()
        try:
            rows = []
            locations = []
            for section, text in sections.items():
                if text.strip():
                    encoded = self.tokenizer(
                        text,
                        truncation=True,
                        max_length=256,
                        return_offsets_mapping=True,
                        return_tensors="pt",
                    )
                    offsets = encoded.pop("offset_mapping")[0].tolist()
                    rows.append(encoded)
                    locations.append((section, text, offsets))
            results = []
            seen: set[int] = set()
            with torch.no_grad():
                for encoded, (section, text, offsets) in zip(rows, locations):
                    logits = self.model(**encoded).logits[0]
                    predictions = logits.argmax(dim=-1).tolist()
                    spans = []
                    current = None
                    for index, (label_id, (start, end)) in enumerate(zip(predictions, offsets)):
                        if end <= start:
                            continue
                        if label_id == LABELS["B-SKILL"] or (label_id == LABELS["I-SKILL"] and current is None):
                            if current:
                                spans.append(current)
                            current = [start, end]
                        elif label_id == LABELS["I-SKILL"] and current:
                            current[1] = end
                        elif current:
                            spans.append(current)
                            current = None
                    if current:
                        spans.append(current)
                    for start, end in spans:
                        candidate = text[start:end]
                        matches = dictionary_extract_skills({"section": candidate}, conn=conn)
                        if not matches:
                            continue
                        match = matches[0]
                        skill_id = match["skill_id"]
                        if skill_id in seen:
                            continue
                        results.append({
                            "skill_id": skill_id,
                            "matched_text": candidate,
                            "canonical_name": match["canonical_name"],
                            "section": section,
                            "char_span": (start, end),
                        })
                        seen.add(skill_id)
            return results
        finally:
            if own_conn:
                conn.close()


def extract_skills(sections: dict[str, str], model_dir: str | Path, *, conn=None) -> list[dict]:
    return BertSkillExtractor(model_dir).extract_skills(sections, conn=conn)