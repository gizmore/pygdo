#!/bin/bash
#set -euo pipefail

cd "$(dirname "$0")" || exit 1
CORE="$(pwd)"

echo "Installing core requirements..."
pip3 install -r requirements.txt || exit 1

echo
echo "Installing module-specific requirements (if any)..."
echo "Thanks to greycat @ libera#bash"

for d in ./gdo/*/; do
  REQFILE="$d/requirements.txt"
  if [[ -s "$REQFILE" ]]; then
    echo "Installing in $d"
    (cd "$d" && pip3 install -r requirements.txt) || echo "Failed in $d"
  fi
done
