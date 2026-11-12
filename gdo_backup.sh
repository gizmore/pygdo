#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd -- "$project_dir"
umask 077
exec python3 "$project_dir/bin/gdo_backup.py" "$@"
