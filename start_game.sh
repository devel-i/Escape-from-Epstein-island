#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install pygame
python3 main.py "$@"
