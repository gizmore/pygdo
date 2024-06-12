#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
echo "Calling post install hooks on all modules."

find ./gdo/ -iname "post_install.sh" -exec sh -c '
  for script; do
    echo "install $script"
    cd "$(dirname "$script")"
    ./$(basename "$script")
    cd - > /dev/null
  done
' sh {} +
