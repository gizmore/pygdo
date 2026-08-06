#!/usr/bin/env bash
# Export tracked files from PyGDO core and direct gdo module repositories.
set -euo pipefail

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
workspace_dir=$(cd -- "$project_dir/.." && pwd)
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
archive=${1:-"$workspace_dir/pygdo-export-$timestamp.zip"}

files=()

collect_repo() {
  local repo=$1 prefix=$2 path lower
  while IFS= read -r -d '' path; do
    lower=${path,,}
    case "$lower" in
      */dbimg/*|*.jpg|*.jpeg|*.png|*.ttf|*.otf|*.woff|*.woff2|*.eot) continue ;;
    esac
    test -e "$repo/$path" || continue
    files+=("$prefix/$path")
  done < <(git -c safe.directory="$repo" -C "$repo" ls-files -z)
}

collect_repo "$project_dir" pygdo

for repo in "$project_dir"/gdo/*; do
  test -d "$repo" || continue
  repo=$(realpath "$repo")
  top=$(git -c safe.directory="$repo" -C "$repo" rev-parse --show-toplevel 2>/dev/null || true)
  test "$top" = "$repo" || continue
  collect_repo "$repo" "pygdo/gdo/$(basename "$repo")"
done

test "${#files[@]}" -gt 0
mkdir -p "$(dirname -- "$archive")"
(
  cd "$workspace_dir"
  zip -q "$archive" "${files[@]}"
)
printf 'Exported %d tracked files to %s\n' "${#files[@]}" "$archive"
