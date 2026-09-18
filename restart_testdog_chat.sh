#!/usr/bin/env bash
set -euo pipefail

# Restart the isolated Test Dog after Python changes that affect chat handling.
# It deliberately does not watch the normal Dog or unrelated framework modules.
project_dir=/home/gizmore/www/pygdo
restart=/home/mira/.codex/skills/testdog/scripts/restart.sh
lock_file=/run/pygdo-testdog-chat-watch.lock

watch_dirs=(
    "$project_dir/gdo/chat"
    "$project_dir/gdo/message"
    "$project_dir/gdo/irc"
    "$project_dir/gdo/telegram"
    "$project_dir/gdo/discord"
    "$project_dir/gdo/slack"
    "$project_dir/gdo/whatsapp"
    "$project_dir/gdo/net"
    "$project_dir/gdo/mira"
    "$project_dir/gdo/translate"
    "$project_dir/gdo/git"
    "$project_dir/gdo/youtube"
)

existing_dirs=()
for directory in "${watch_dirs[@]}"; do
    [[ -d "$directory" ]] && existing_dirs+=("$directory")
done

(( ${#existing_dirs[@]} )) || exit 0

while inotifywait -qr -e close_write,move,create,delete \
    --include '(^|/)[^/]+\.py$' "${existing_dirs[@]}"; do
    # Editors commonly write several related files in one short burst.
    sleep 1
    flock -n "$lock_file" "$restart" || true
done
