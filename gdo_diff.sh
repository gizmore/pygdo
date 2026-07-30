#!/usr/bin/env bash
set -euo pipefail

core_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd -- "$core_dir"

command -v git >/dev/null 2>&1 || {
    printf 'ERROR: git was not found\n' >&2
    exit 127
}

clear
echo "Starting gdo_diff.sh"

# Scan nested repositories without changing into their .git directories.
# The scoped safe.directory setting supports the shared gizmore/mira checkout
# without modifying either user's global Git configuration.
while IFS= read -r -d '' git_dir; do
    repo_dir=$(cd -- "${git_dir%/.git}" && pwd)
    printf '\n=== %s ===\n' "$repo_dir"
    LANG=en_GB LC_ALL=en_GB git \
        -c "safe.directory=$repo_dir" \
        -C "$repo_dir" --no-pager diff
done < <(find . -type d -name .git -prune -print0)
