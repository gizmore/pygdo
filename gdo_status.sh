#!/bin/bash
cd "$(dirname "$0")"

CORE="$(pwd)"

find . -maxdepth 3 -type d -name .git -print0 |
while IFS= read -r -d '' gitdir; do
	repo="${gitdir%/.git}"
	repo_path="$(cd "$repo" && pwd)"
	status="$(LANG=en_GB LC_ALL=en_GB git -c safe.directory="$repo_path" -C "$repo_path" status --short --ignore-submodules=none)"
	sync=""
	if git -c safe.directory="$repo_path" -C "$repo_path" rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
		read -r behind ahead < <(git -c safe.directory="$repo_path" -C "$repo_path" rev-list --left-right --count '@{upstream}...HEAD')
		if ((ahead || behind)); then
			branch="$(git -c safe.directory="$repo_path" -C "$repo_path" branch --show-current)"
			sync="${branch}: ahead ${ahead}, behind ${behind}"
		fi
	fi
	[ -z "$status" ] && [ -z "$sync" ] && continue
	printf '%s\n%s\n' "--------------------------------" "$repo"
	[ -n "$status" ] && printf '%s\n' "$status"
	[ -n "$sync" ] && printf '%s\n' "$sync"
done
