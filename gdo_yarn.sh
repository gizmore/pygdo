#!/bin/bash
#set -euo pipefail

cd "$(dirname "$0")"

CORE="$(dirname "$0")"

echo "All modules: yarn install"
echo "Thanks to greycat @ libera#bash"
for d in ./gdo/*/; do (cd "$d" || exit; [[ -f package.json ]] || exit; echo $d; yarn install); done
