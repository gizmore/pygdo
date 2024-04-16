#!/bin/bash
cd "$(dirname "$0")"

CORE="$(dirname "$0")"

clear
find . -maxdepth 3 -iname ".git" -type d -exec sh -c "cd $CORE && cd {} && cd .. && pwd && LANG=en_GB LC_ALL=en_GB git status && git submodule foreach git status" \;
