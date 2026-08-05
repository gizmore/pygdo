#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

dry_run=0
if [[ "${1:-}" == '--dry-run' ]]; then
    dry_run=1
    shift
fi
if (($#)); then
    echo "Usage: $0 [--dry-run]" >&2
    exit 2
fi

is_gizmore_repo() {
    local repo="$1" url
    url="$(git -c safe.directory='*' -C "$repo" remote get-url origin 2>/dev/null || true)"
    [[ "$url" == *github.com/gizmore/* || "$url" == *github.com:gizmore/* ]]
}

push_repo() {
    local repo="$1" ahead
    is_gizmore_repo "$repo" || return

    echo "== $repo"
    if [[ -n "$(git -c safe.directory='*' -C "$repo" status --porcelain)" ]]; then
        echo "skip: working tree is not clean"
        return
    fi
    if ! git -c safe.directory='*' -C "$repo" rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
        echo "skip: no upstream branch"
        return
    fi
    ahead="$(git -c safe.directory='*' -C "$repo" rev-list --count '@{upstream}..HEAD')"
    if [[ "$ahead" == '0' ]]; then
        echo "up to date"
    elif ((dry_run)); then
        echo "would push $ahead commit(s)"
    else
        git -c safe.directory='*' -C "$repo" push
    fi
}

push_repo .
while IFS= read -r -d '' repo_git; do
    push_repo "${repo_git%/.git}"
done < <(find gdo -type d -name .git -print0)
