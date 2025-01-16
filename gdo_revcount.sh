#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON_FILE="gdo/base/GDO_Module.py"

sed -i -E 's/(CORE_REV\s*=\s*\x22PyGDOv[0-9]+\.[0-9]+\.[0-9]+-r)([0-9]+)(\x22)/echo "    \1$((\2 + 1))\3"/e' "$PYTHON_FILE"
