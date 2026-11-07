#!/bin/bash
cd "$(dirname "$0")"

CORE="$(pwd)"

find . -maxdepth 3 -type d -name .git -print0 |
while IFS= read -r -d '' gitdir; do
	repo="${gitdir%/.git}"
	repo_path="$(cd "$repo" && pwd)"
	status="$(LANG=en_GB LC_ALL=en_GB git -c safe.directory="$repo_path" -C "$repo_path" status --short --ignore-submodules=none)"
	branch="$(git -c safe.directory="$repo_path" -C "$repo_path" branch --show-current)"
	branch_note=""
	if [ -n "$branch" ] && [ "$branch" != main ] && [ "$branch" != master ]; then
		branch_note="branch: $branch (not main/master)"
	fi
	sync=""
	if git -c safe.directory="$repo_path" -C "$repo_path" rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
		read -r behind ahead < <(git -c safe.directory="$repo_path" -C "$repo_path" rev-list --left-right --count '@{upstream}...HEAD')
		if ((ahead || behind)); then
			sync="${branch}: ahead ${ahead}, behind ${behind}"
		fi
	fi
	[ -z "$status" ] && [ -z "$sync" ] && [ -z "$branch_note" ] && continue
	remote="$(git -c safe.directory="$repo_path" -C "$repo_path" remote get-url origin 2>/dev/null)"
	maintainer="unknown"
	case "$remote" in
		git@github.com:*/*) maintainer="${remote#git@github.com:}"; maintainer="${maintainer%%/*}" ;;
		https://github.com/*/*) maintainer="${remote#https://github.com/}"; maintainer="${maintainer%%/*}" ;;
		ssh://git@github.com/*/*) maintainer="${remote#ssh://git@github.com/}"; maintainer="${maintainer%%/*}" ;;
	esac
	printf '%s\n%s (GitHub owner: %s)\n' "--------------------------------" "$repo" "$maintainer"
	[ -n "$status" ] && printf '%s\n' "$status"
	[ -n "$sync" ] && printf '%s\n' "$sync"
	[ -n "$branch_note" ] && printf '%s\n' "$branch_note"
done
