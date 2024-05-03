#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo Running all tests!...
python3 gdotestall.py "$@"
