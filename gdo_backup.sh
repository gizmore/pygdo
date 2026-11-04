#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd -- "$project_dir"
umask 077
python_bin="$project_dir/.venv/bin/python"
if [[ ! -x "$python_bin" ]]; then
    python_bin=python3
fi
exec "$python_bin" "$project_dir/bin/gdo_backup.py" "$@"
