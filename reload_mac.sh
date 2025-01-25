#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

rm -f temp/yappi.log
while pgrep unit >/dev/null; do kill -9 $(pgrep unit); sleep 0.5; done
unitd
