#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

dry_run=0
failures=0
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
    # Not every checkout belongs to gizmore (and a few have no origin).
    # This is an intentional skip, not a failure for ``set -e``.
    is_gizmore_repo "$repo" || return 0

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
        if ! git -c safe.directory='*' -C "$repo" push; then
            echo "error: push failed; continuing with remaining repositories" >&2
            ((failures += 1))
        fi
    fi
}

push_repo . || {
    echo "error: failed to inspect root repository; continuing" >&2
    ((failures += 1))
}
while IFS= read -r -d '' repo_git; do
    push_repo "${repo_git%/.git}" || {
        echo "error: failed to inspect ${repo_git%/.git}; continuing" >&2
        ((failures += 1))
    }
done < <(find gdo -type d -name .git -print0)

if ((failures)); then
    echo "Finished with $failures failed push(es)." >&2
    exit 1
fi
