#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
#
# Needs aptitude install inotify-tools
# Dev Helper shell script to reload apache when files are changed
#
systemctl restart apache2   
while inotifywait -r -e modify,move,create,delete --exclude '/(protected|files|__pycache__)/.*' .; do
    echo "Changes detected, restarting Apache..."
    systemctl restart apache2
done
