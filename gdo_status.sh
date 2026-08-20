#!/bin/bash
cd "$(dirname "$0")"

CORE="$(pwd)"

find . -maxdepth 3 -type d -name .git -print0 |
while IFS= read -r -d '' gitdir; do
	repo="${gitdir%/.git}"
	repo_path="$(cd "$repo" && pwd)"
	status="$(LANG=en_GB LC_ALL=en_GB git -c safe.directory="$repo_path" -C "$repo_path" status --short --ignore-submodules=none)"
	[ -z "$status" ] && continue
	printf '%s\n%s\n%s\n' "--------------------------------" "$repo" "$status"
done
