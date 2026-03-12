#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 14) else 1)'; then
  "$PYTHON_BIN" -m pip install pygame-ce
else
  "$PYTHON_BIN" -m pip install pygame
fi

"$PYTHON_BIN" main.py "$@"
