#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
#
# Needs aptitude install inotify-tools
# Dev Helper shell script to reload apache when files are changed
#
systemctl restart apache2   
rm temp/yappi.log
while inotifywait -r -e modify,move,create,delete --exclude '/(.yarn-integrity|temp|assets|.git|protected|files|__pycache__|workspace.xml*)/.*' .; do
    echo "Changes detected, restarting Apache..."
    systemctl restart apache2
    rm temp/yappi.log
done
