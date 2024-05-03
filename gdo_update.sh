#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Running the gdo_fix.sh because argh. This will take a while"
#bash gdo_fix.sh

# THREADS: number of parallel executing  processes
# default: THREADS=15
#  - THREADS=0 (unlimited)
THREADS=15
if [ $# -gt 0 ]; then
  THREADS=$1
fi;

XARGS_OPTIONS="-P $THREADS -0 -I {}"
if [ $(uname -s) == "FreeBSD" ]; then
        XARGS_OPTIONS="-S 1024 -R 2 $XARGS_OPTIONS"
fi

echo "Resetting sourcecode to factory defaults for preprocessor."
bash gdo_reset.sh

echo "Updating all core modules and submodules in the phpgdo repo."
find ./ -maxdepth 1 -type d -iname '.git' -print0 | xargs $XARGS_OPTIONS bash -c "cd \"{}\"/../ && OUT=\"\$(echo \"{}\" | cut -f 3 -d '/')\" && git submodule foreach git pull >> temp/git_pull_\$OUT && echo -e \"-----------------------------\nupdating repo [ \\\"\$(pwd)\\\" ]:\" >> temp/git_pull_\$OUT && LANG=en_GB LC_ALL=en_GB git pull &>> temp/git_pull_\$OUT && git submodule update --recursive --remote &>> temp/git_pull_\$OUT  ; cat temp/git_pull_\$OUT && rm temp/git_pull_\$OUT "

echo "Updating all extension modules and submodules in $THREADS parallel threads."
find ./GDO -maxdepth 2 -type d -iname '.git' -print0 | xargs $XARGS_OPTIONS bash -c "cd \"{}\"/../ && OUT=\"\$(echo \"{}\" | cut -f 3 -d '/')\" && echo -e \"-----------------------------\nupdating repo [ \\\"\$(pwd)\\\" ]:\" >> ../../temp/git_pull_\$OUT && LANG=en_GB LC_ALL=en_GB git pull &>> ../../temp/git_pull_\$OUT && git submodule foreach git pull >> ../../temp/git_pull_\$OUT && git submodule update --recursive --remote &>> ../../temp/git_pull_\$OUT  ; cat ../../temp/git_pull_\$OUT && rm ../../temp/git_pull_\$OUT "

cd "$(dirname "$0")"

echo "Triggering 'gdo_adm.sh confgrade'."
bash gdo_adm.sh confgrade

echo "Triggering 'gdo_adm.sh update'."
bash gdo_adm.sh update

echo "Triggering 'gdo_yarn.sh'."
bash gdo_yarn.sh
