#!/bin/bash
#set -euo pipefail

cd "$(dirname "$0")"

CORE="$(dirname "$0")"

echo "Core requirements."
pip3 install -r requirements.txt

echo "All modules: pip3 install -r requirements.txt"
echo "Thanks to greycat @ libera#bash"
for d in ./gdo/*/; do (cd "$d" || exit; [[ -f requirements.txt ]] || exit; echo $d; pip3 install -r requirements.txt); done
