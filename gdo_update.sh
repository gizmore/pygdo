#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Update source checkouts without discarding local work. Pass a positive
# integer to select the parallelism (default: 15). Runtime-affecting hooks
# are deliberately opt-in via --apply.
THREADS=15
APPLY=0
for arg in "$@"; do
	case "$arg" in
		--apply) APPLY=1 ;;
		*[!0-9]*|'')
			echo "Usage: $0 [threads] [--apply]" >&2
			exit 2
			;;
		*) THREADS="$arg" ;;
	esac
done

mkdir -p temp

repo_dirs() {
	printf '%s\0' .
	find ./gdo -mindepth 2 -maxdepth 2 -type d -name '.git' -printf '%h\0'
}

ensure_clean() {
	local repo_dir="$1"
	if [[ -n "$(git -C "$repo_dir" status --porcelain)" ]]; then
		echo "Refusing to update dirty checkout: $repo_dir" >&2
		return 1
	fi
}

update_repo() {
	local repo_dir="$1"
	local repo_name
	local log_file

	repo_name="$(basename "$repo_dir")"
	log_file="$(pwd)/temp/git_pull_${repo_name}_$$"

	(
		cd "$repo_dir"
		{
			printf '%s\n' "-----------------------------"
			printf 'updating repo [ "%s" ]:\n' "$(pwd)"
			LANG=en_GB LC_ALL=en_GB git pull --ff-only
		} >"$log_file" 2>&1
	)

	cat "$log_file"
	rm -f "$log_file"
}

export -f update_repo

echo "Checking that every checkout is clean. No reset will be performed."
while IFS= read -r -d '' repo_dir; do
	ensure_clean "$repo_dir"
done < <(repo_dirs)

echo "Updating the main PyGDO repository and extension modules."
update_repo .
repo_dirs | tail -z -n +2 | xargs -0 -r -n 1 -P "$THREADS" bash -c 'update_repo "$1"' _

if (( ! APPLY )); then
	echo "Source update completed. Skipped configure, database update, yarn, and service restart."
	echo "Run '$0 --apply' only after reviewing the updated source."
	exit 0
fi

echo "Applying explicit maintenance hooks."
bash gdo_adm.sh configure
bash gdo_adm.sh update
bash gdo_yarn.sh
