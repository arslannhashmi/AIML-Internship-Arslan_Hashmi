#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)

export SKILLFORGE_DB_PATH="$ROOT_DIR/skillforge/db/skillforge.db"
export PYTHONPATH="$ROOT_DIR/skillforge${PYTHONPATH:+:$PYTHONPATH}"

python3.12 -m py_compile \
  "$ROOT_DIR/skillforge/backend/main.py" \
  "$ROOT_DIR/skillforge/backend/profile.py"

python3.12 -c 'from backend.main import app; assert app is not None'