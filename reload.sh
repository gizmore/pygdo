#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
#
# Needs aptitude install inotify-tools
# Dev Helper shell script to reload apache when files are changed
#
log_dir="protected/logs"
error_logs=(
    "$log_dir/apache-error.log"
    "$log_dir/exception.log"
)

show_and_clear_errors() {
    local log
    for log in "${error_logs[@]}"; do
        [ -f "$log" ] || continue
        printf '\n--- %s ---\n' "$log"
        cat -- "$log"
        : > "$log"
    done
}

show_and_clear_errors
systemctl restart apache2
rm -f temp/yappi.log
while inotifywait -r -e modify,move,create,delete --exclude '/(.yarn-integrity|temp|assets|.git|protected|files|bin|__pycache__|workspace.xml*)/.*' .; do
    echo "Changes detected, restarting Apache..."
    show_and_clear_errors
    rm -f temp/yappi.log
    systemctl restart apache2
    rm -f temp/yappi.log
done
