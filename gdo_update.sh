#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# THREADS: number of parallel processes
# Default: 15
# 0 means unlimited where supported by xargs.
THREADS="${1:-15}"

mkdir -p temp

update_repo() {
	local git_dir="$1"
	local repo_dir="${git_dir%/.git}"
	local repo_name
	local log_file

	repo_name="$(basename "$repo_dir")"
	log_file="$(pwd)/temp/git_pull_${repo_name}_$$"

	(
		cd "$repo_dir"

		{
			printf '%s\n' "-----------------------------"
			printf 'updating repo [ "%s" ]:\n' "$(pwd)"

			LANG=en_GB LC_ALL=en_GB git pull
			git submodule foreach git pull
			git submodule update --recursive --remote
		} >"$log_file" 2>&1
	)

	cat "$log_file"
	rm -f "$log_file"
}

export -f update_repo

echo "Resetting sourcecode to factory defaults for preprocessor."
bash gdo_reset.sh

echo "Updating the main phpgdo repository and its submodules."
update_repo "./.git"

echo "Updating all extension modules and submodules in $THREADS parallel threads."
find ./gdo \
	-mindepth 2 \
	-maxdepth 2 \
	-type d \
	-name '.git' \
	-print0 |
	xargs -0 -n 1 -P "$THREADS" \
		bash -c 'update_repo "$1"' _

cd "$(dirname "$0")"

echo "Triggering 'gdo_adm.sh confgrade'."
bash gdo_adm.sh configure

echo "Triggering 'gdo_adm.sh update'."
bash gdo_adm.sh update

echo "Triggering 'gdo_yarn.sh'."
bash gdo_yarn.sh
```
