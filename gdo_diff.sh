#!/usr/bin/env bash
set -euo pipefail

core_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd -- "$core_dir"

command -v git >/dev/null 2>&1 || {
    printf 'ERROR: git was not found\n' >&2
    exit 127
}

if [[ -t 1 ]]; then
    clear || true
fi
echo "Starting gdo_diff.sh"

# Scan nested repositories without changing into their .git directories.
# The scoped safe.directory setting supports the shared gizmore/mira checkout
# without modifying either user's global Git configuration.
while IFS= read -r -d '' git_dir; do
    repo_dir=$(cd -- "${git_dir%/.git}" && pwd)
    reported=0
    if ! LANG=en_GB LC_ALL=en_GB git -c "safe.directory=$repo_dir" -C "$repo_dir" diff --quiet; then
        printf '\n=== %s ===\n' "$repo_dir"
        reported=1
        LANG=en_GB LC_ALL=en_GB git -c "safe.directory=$repo_dir" -C "$repo_dir" --no-pager diff
    fi
    while IFS= read -r -d '' file; do
        # Restrict output to source/documentation names and never follow links.
        # Names alone cannot guarantee that a source file contains no secrets.
        lower=${file,,}
        case "/$lower" in
            */protected/*|*/private/*|*secret*|*credential*|*/.env|*/.env.*) continue ;;
        esac
        case "$lower" in
            *.py|*.sh|*.js|*.ts|*.css|*.html|*.htm|*.md|*.rst|*.txt|*.toml|*.yaml|*.yml|*.json|*.sql|*.php|*.c|*.h|*.cpp|*.rs|*.go|*/makefile|makefile|*/dockerfile|dockerfile) ;;
            *) continue ;;
        esac
        path="$repo_dir/$file"
        [[ -f "$path" && ! -L "$path" ]] || continue
        # Git identifies binary files with its normal diff rules. --numstat
        # prints only metadata, so skipped binary content is never emitted.
        numstat=$(git -c "safe.directory=$repo_dir" -C "$repo_dir" diff --no-index --numstat -- /dev/null "$path") || rc=$?
        if [[ ${rc:-0} -gt 1 ]]; then
            printf 'Could not inspect untracked file: %q\n' "$file" >&2
            exit "$rc"
        fi
        unset rc
        [[ "$numstat" == $'-\t-'* ]] && continue
        if (( ! reported )); then
            printf '\n=== %s ===\n' "$repo_dir"
            reported=1
        fi
        git -c "safe.directory=$repo_dir" -C "$repo_dir" --no-pager diff --no-index -- /dev/null "$path" || {
            rc=$?
            (( rc == 1 )) || exit "$rc"
        }
    done < <(git -c "safe.directory=$repo_dir" -C "$repo_dir" ls-files --others --exclude-standard -z)
done < <(find . -type d -name .git -prune -print0)
