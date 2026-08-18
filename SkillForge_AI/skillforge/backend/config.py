"""Small environment-backed configuration for the Phase 14 API."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(
    os.environ.get("SKILLFORGE_UPLOAD_DIR", str(PROJECT_ROOT / "uploads"))
)
MAX_UPLOAD_BYTES = int(os.environ.get("SKILLFORGE_MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
API_TITLE = "SkillForge AI API"
API_VERSION = "phase14"
