#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON_FILE="gdo/base/GDO_Module.py"

sed -i -E 's/(CORE_REV\s*=\s*"PyGDOv[0-9]+\.[0-9]+\.[0-9]+-r)([0-9]+)"/echo "    \1$((\2 + 1))\""/e' "$PYTHON_FILE"