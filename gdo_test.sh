#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo Running all tests!...
./.venv/bin/python gdotestall.py "$@"
