#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

./gdo_adm.sh wipe -a
./gdo_adm.sh install irc,telegram,pm,markdown,blackjack,account,admin,contact,perf,math,login,register,recovery,bootstrap5,avatar,shadowdogs,vote,poll,quote,scum,slapwarz,websocket,discord,connect,whatsapp,mira,oracle,zen,rss
./gdo_adm.sh admin gizmore 11113333 gizmore@wechall.net
./gdo_adm.sh admin mira ChangeMe gizmore@wechall.net
./gdo_adm.sh admin --server 2 gizmore 11113333 gizmore@wechall.net

# Persisted server topology as of 2026-08-24. Connector secrets stay in the
# corresponding module configuration and are deliberately not put in this
# wipe/reinstall script.
./bin/pygdo '$add_server mogwai irc tcps://mogwai.mira-gpt.org:6697'
./bin/pygdo '$add_server tcp tcp'
./bin/pygdo '$add_server wc irc tcps://irc.wechall.net:6697'
./bin/pygdo '$add_server euirc irc tcps://irc.lim.de.euirc.net:6697'
./bin/pygdo '$add_server libera irc tcps://irc.libera.chat:6697'
./bin/pygdo '$add_server rizon irc tcps://irc.rizon.net:6697'

./gdo_adm.sh cc
