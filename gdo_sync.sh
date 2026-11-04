#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

CORE="$(pwd)"

rev=0
msg=""
owner="gizmore"
# GNU xargs is inconsistent across developer machines. Keep the worker pool in
# Bash instead; this also works with the Bash 3.2 that ships with macOS.
THREADS="${THREADS:-8}"

# Parse args: [--owner=<git-username>] [--rev] "commit message"
while (($#)); do
  case "$1" in
    --rev) rev=1; shift ;;
    --owner=*) owner="${1#--owner=}"; shift ;;
    --) shift; break ;;
    -*) echo "Usage: $0 [--owner=<git-username>] [--rev] \"commit message\"" >&2; exit 2 ;;
    *)  if [[ -n "$msg" ]]; then
          echo "Error: commit message must be the only non-option arg (wrap it in quotes)." >&2
          echo "Usage: $0 [--owner=<git-username>] [--rev] \"commit message\"" >&2
          exit 2
        fi
        msg="$1"
        shift
        ;;
  esac
done

if [[ -z "$msg" ]] || (($#)); then
  echo "Usage: $0 [--owner=<git-username>] [--rev] \"commit message\"" >&2
  exit 2
fi

if ! [[ "$owner" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]*$ ]]; then
  echo "Error: --owner must be a non-empty Git username." >&2
  exit 2
fi

# Select by the actual push destination, not by local directory or author.
# Multiple push URLs are ambiguous and are skipped rather than partly synced.
matches_owner() {
  local repo="$1" urls url repo_owner
  urls=$(git -C "$repo" remote get-url --push --all origin 2>/dev/null) || return 1
  [[ -n "$urls" && "$urls" != *$'\n'* ]] || return 1
  url="${urls%/}"
  if [[ "$url" =~ [:/]([^/:]+)/[^/]+$ ]]; then
    repo_owner="${BASH_REMATCH[1]}"
    [[ "$(printf '%s' "$repo_owner" | tr '[:upper:]' '[:lower:]')" == "$(printf '%s' "$owner" | tr '[:upper:]' '[:lower:]')" ]]
  else
    return 1
  fi
}

echo "PyGDOv8 sync.sh: Owner: $owner; sync message: $msg"

echo "Are you sure? Press Enter!"
read

if matches_owner "$CORE"; then
  echo "Creating module provider mappings..."
  python3 gdoproviders.py
  if ((rev)); then
    echo "Counting up revision number."
    bash gdo_revcount.sh
  fi
  echo "Syncing core..."
  git add -A .
  git commit -m "$msg" || true
  git pull --rebase
  git push
else
  echo "Skipping core: push remote does not match owner $owner."
  if ((rev)); then
    echo "Skipping revision update because core is not selected."
  fi
fi

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
repos=()
logs=()
failed=0
LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pygdo-sync.XXXXXX")"
trap 'rm -rf "$LOG_DIR"' EXIT

wait_for_worker() {
  local pid="${pids[0]}"
  local repo="${repos[0]}"
  local log="${logs[0]}"
  local status=0

  # Each repository keeps its own transcript while it runs.  Printing it
  # only once the worker ends preserves readable, non-interleaved output.
  if ! wait "$pid"; then
    status=1
    failed=1
  fi
  printf '\n===== Sync: %s =====\n' "$repo"
  cat "$log"
  if ((status)); then
    printf '===== FAILED: %s =====\n' "$repo" >&2
  fi
  rm -f "$log"
  pids=("${pids[@]:1}")
  repos=("${repos[@]:1}")
  logs=("${logs[@]:1}")
}

repo_num=0
while IFS= read -r -d '' repo_git; do
  repo="$CORE/$repo_git/.."
  if ! matches_owner "$repo"; then
    continue
  fi
  log="$LOG_DIR/$repo_num.log"
  sync_repo "$repo" >"$log" 2>&1 &
  pids+=("$!")
  repos+=("$repo")
  logs+=("$log")
  repo_num=$((repo_num + 1))
  if ((${#pids[@]} >= THREADS)); then
    wait_for_worker
  fi
done < <(find gdo -iname ".git" -type d -print0)

while ((${#pids[@]})); do
  wait_for_worker
done

exit "$failed"
