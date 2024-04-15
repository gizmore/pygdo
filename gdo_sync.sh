#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

CORE="$(dirname "$0")"
message="'$*'"
echo "PyGDOv8 sync.sh: Sync message: $message"

echo "Updating core submodules."
git submodule foreach git reset --hard
git submodule foreach git pull
echo

echo "Are you sure?"
sleep 5

echo "Creating module provider mappings..."
#sleep 1
#php provider_update.php

echo "Syncing repositories..."
echo "Do: git commit & push all repos"
sleep 1
find . -iname ".git" -type d -exec sh -c "cd $CORE && cd {} && cd .. && pwd && git add -A . && git commit -am \"$message\" && git push" \;

