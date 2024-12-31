#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
#
# Needs aptitude install inotify-tools
# Dev Helper shell script to reload apache when files are changed
#
#pkill unit
#sleep 1
unitd
while inotifywait -r -e modify,move,create,delete --exclude '/(protected|files|__pycache__|workspace.xml*)/.*' .; do
    echo "Changes detected, restarting Apache..."
    pkill unit
    sleep 1
    unitd
done
