"""Resume upload and structured profile endpoint."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from db.db_client import get_connection
from extraction.dictionary_matcher import extract_skills
from parser.resume_parser import parse_resume

from backend.config import MAX_UPLOAD_BYTES, UPLOAD_DIR
from backend.dependencies import get_db
from backend.schemas import ProfileResponse


router = APIRouter(prefix="/profile", tags=["profile"])


def _row_value(row, key: str, index: int):
    return row[key] if hasattr(row, "keys") else row[index]


def _resolve_or_create_user(
    conn,
    *,
    user_id: int | None,
    username: str | None,
    email: str | None,
) -> int:
    if user_id is not None:
        row = conn.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Unknown user_id: {user_id}")
        return int(_row_value(row, "user_id", 0))

    if not username or not email:
        identity = uuid.uuid4().hex
        username = username or f"anonymous-{identity[:12]}"
        email = email or f"{identity}@anonymous.skillforge.local"

    existing = conn.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    if existing is not None:
        return int(_row_value(existing, "user_id", 0))

    try:
        conn.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (username, email),
        )
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email is already registered",
        ) from exc
    created = conn.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    return int(_row_value(created, "user_id", 0))


@router.post("/resume", response_model=ProfileResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int | None = Form(default=None),
    username: str | None = Form(default=None),
    email: str | None = Form(default=None),
    conn=Depends(get_db),
):
    """Persist a PDF resume, extract skills, and return its structured profile."""
    filename = Path(file.filename or "resume.pdf").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF resume uploads are supported")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded resume is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Uploaded resume exceeds the size limit")

    saved_path: Path | None = None
    try:
        resolved_user_id = _resolve_or_create_user(
            conn,
            user_id=user_id,
            username=username,
            email=email,
        )
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{filename}"
        saved_path.write_bytes(data)

        parsed = parse_resume(str(saved_path))
        matches = extract_skills(parsed["sections"], conn=conn)

        conn.execute(
            "INSERT INTO resumes (user_id, file_path, raw_text) VALUES (?, ?, ?)",
            (resolved_user_id, str(saved_path), parsed["raw_text"]),
        )
        resume_row = conn.execute(
            "SELECT resume_id FROM resumes WHERE user_id = ? AND file_path = ?",
            (resolved_user_id, str(saved_path)),
        ).fetchone()
        resume_id = int(_row_value(resume_row, "resume_id", 0))

        for match in matches:
            conn.execute(
                """
                INSERT INTO user_skills (user_id, skill_id, proficiency, source)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, skill_id) DO UPDATE SET
                    proficiency = excluded.proficiency,
                    source = excluded.source,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (resolved_user_id, int(match["skill_id"]), 1, "resume"),
            )
        conn.commit()

        skills = [
            {
                "skill_id": int(match["skill_id"]),
                "canonical_name": match["canonical_name"],
                "proficiency": 1,
                "source": "resume",
                "matched_text": match["matched_text"],
                "section": match["section"],
                "char_span": list(match["char_span"]),
            }
            for match in matches
        ]
        return {
            "user_id": resolved_user_id,
            "resume_id": resume_id,
            "skill_count": len(skills),
            "skills": skills,
            "sections": list(parsed["sections"].keys()),
        }
    except HTTPException:
        conn.rollback()
        if saved_path and saved_path.exists():
            saved_path.unlink()
        raise
    except Exception as exc:
        conn.rollback()
        if saved_path and saved_path.exists():
            saved_path.unlink()
        raise HTTPException(
            status_code=422,
            detail=f"Resume could not be parsed or profiled: {exc}",
        ) from exc
