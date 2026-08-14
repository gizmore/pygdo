#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

CORE="$(dirname "$0")"

rev=0
msg=""
# GNU xargs is inconsistent across developer machines. Keep the worker pool in
# Bash instead; this also works with the Bash 3.2 that ships with macOS.
THREADS="${THREADS:-8}"

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

echo "Reattaching and synchronizing submodules."
git submodule sync --recursive
git submodule update --init --recursive
echo

echo "Creating module provider mappings..."
./.venv/bin/python gdoproviders.py

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
git pull --rebase
git push

echo "Syncing module repositories..."
if ! [[ "$THREADS" =~ ^[1-9][0-9]*$ ]]; then
  echo "THREADS must be a positive integer, got: $THREADS" >&2
  exit 2
fi

sync_repo() {
  local repo="$1"
  (
    cd "$repo"
    pwd
    git add -A .
    git commit -m "$msg" || true
    git pull --rebase
    git push
  )
}

pids=()
failed=0
wait_for_worker() {
  local pid="${pids[0]}"
  if ! wait "$pid"; then
    failed=1
  fi
  pids=("${pids[@]:1}")
}

while IFS= read -r -d '' repo_git; do
  sync_repo "$CORE/$repo_git/.." &
  pids+=("$!")
  if ((${#pids[@]} >= THREADS)); then
    wait_for_worker
  fi
done < <(find gdo -iname ".git" -type d -print0)

while ((${#pids[@]})); do
  wait_for_worker
done

exit "$failed"
