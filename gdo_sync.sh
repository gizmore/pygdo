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

echo "Creating module provider mappings..."
python3 gdoproviders.py

echo "Are you sure? Press Enter!"
read

echo "Syncing repositories..."
echo "Do: git commit & push all repos"
sleep 1
find . -iname ".git" -type d -exec sh -c "cd $CORE && cd {} && cd .. && pwd && git add -A . && git commit -am \"$message\" && git push" \;

