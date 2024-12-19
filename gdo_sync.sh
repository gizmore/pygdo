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

echo "Syncing core..."
pwd && git add -A . && git commit -am \"$message\" && git push
sleep 1

echo "Syncing module repositories..."
sleep 1
find gdo -iname ".git" -type d -exec sh -c "cd $CORE && cd {} && cd .. && pwd && git add -A . && git commit -am \"$message\" && git push" \;

