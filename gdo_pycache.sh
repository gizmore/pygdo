#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Clearing all python caches..."
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
echo "All Done!"
