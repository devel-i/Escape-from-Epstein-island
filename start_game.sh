#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

# 1) Prefer pygame-ce wheels (works for Python 3.14+ and usually older versions too).
# 2) Fallback to pygame only for older Python installs where pygame-ce wheel is unavailable.
if ! "$PYTHON_BIN" -m pip install --only-binary=:all: pygame-ce; then
  "$PYTHON_BIN" -m pip install --only-binary=:all: "pygame<2.7"
fi

"$PYTHON_BIN" main.py "$@"
