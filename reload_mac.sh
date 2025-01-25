#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

while pgrep unitd >/dev/null; do kill -9 $(pgrep unitd); sleep 0.5; done
