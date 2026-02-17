#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

CORE="$(dirname "$0")"

rev=0
msg=""

# Parse args: [--rev] "commit message"
while (($#)); do
  case "$1" in
    --rev) rev=1; shift ;;
    --) shift; break ;;
    -*) echo "Usage: $0 [--rev] \"commit message\"" >&2; exit 2 ;;
    *)  if [[ -n "$msg" ]]; then
          echo "Error: commit message must be the only non-option arg (wrap it in quotes)." >&2
          echo "Usage: $0 [--rev] \"commit message\"" >&2
          exit 2
        fi
        msg="$1"
        shift
        ;;
  esac
done

if [[ -z "$msg" ]] || (($#)); then
  echo "Usage: $0 [--rev] \"commit message\"" >&2
  exit 2
fi

echo "PyGDOv8 sync.sh: Sync message: $msg"

echo "Updating core submodules."
git submodule foreach git reset --hard
git submodule foreach git pull
echo

echo "Creating module provider mappings..."
python3 gdoproviders.py

echo "Are you sure? Press Enter!"
read

if ((rev)); then
  echo "Counting up revision number."
  bash gdo_revcount.sh
fi

echo "Syncing core..."
pwd
git add -A .
git commit -m "$msg" || true
git pull
git push
sleep 1

echo "Syncing module repositories..."
sleep 1
find gdo -iname ".git" -type d -exec bash -c '
  CORE="$1"; MSG="$2"; repo_git="$3"
  cd "$CORE"
  cd "$repo_git/.."
  pwd
  git add -A .
  git commit -m "$MSG" || true
  git pull
  git push
' _ "$CORE" "$msg" {} \;
