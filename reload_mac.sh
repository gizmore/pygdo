#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

pkill unit && pkill unit && sleep 1 && unitd
