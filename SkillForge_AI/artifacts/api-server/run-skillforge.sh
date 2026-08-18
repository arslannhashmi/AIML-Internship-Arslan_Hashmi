#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)

export SKILLFORGE_DB_PATH="$ROOT_DIR/skillforge/db/skillforge.db"
export PYTHONPATH="$ROOT_DIR/skillforge${PYTHONPATH:+:$PYTHONPATH}"

exec python3.12 -m uvicorn backend.main:app \
  --app-dir "$ROOT_DIR/skillforge" \
  --host 0.0.0.0 \
  --port "${PORT:-8080}"