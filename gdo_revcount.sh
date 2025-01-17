#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON_FILE="gdo/base/GDO_Module.py"

if [ "$(uname -s)" == "Darwin" ]; then
    REVISION=$(grep -oE 'r\d{4}' "$PYTHON_FILE" | head -1 | sed 's/r//')
else
    REVISION=$(grep -oP 'r\d{4}' "$PYTHON_FILE" | head -1 | sed 's/r//')
fi

if [[ "$REVISION" =~ ^[0-9]{4}$ ]]; then
    NEW_REVISION=$((REVISION + 1))
    sed -i -E "s/r$REVISION/r$NEW_REVISION/" "$PYTHON_FILE"
    echo "Updated revision from r$REVISION to r$NEW_REVISION"
else
    echo "Error: Could not extract a valid revision number."
    exit 1
fi
