#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

./gdo_adm.sh install irc,telegram,pm,markdown,blackjack,account,admin,contact,perf,math,login,register,recovery,bootstrap5,avatar,shadowdogs,vote,poll,quote,scum,slapwarz,websocket,discord,connect,whatsapp,mira,oracle,zen,rss,maps,online,favicon,icon_fa
./gdo_adm.sh admin gizmore 11113333 gizmore@wechall.net
./gdo_adm.sh admin mira ChangeMe gizmore@wechall.net
./gdo_adm.sh admin --server 2 gizmore 11113333 gizmore@wechall.net

# Persisted server topology as of 2026-08-24. Connector secrets stay in the
# corresponding module configuration and are deliberately not put in this
# normal install/update script. Provision topology only on a fresh database.
if ! PYTHONPATH=. python3 - <<'PY'
from gdo.base.Application import Application

Application.init('.')
cursor = Application.db().get_link().cursor()
cursor.execute("SELECT 1 FROM gdo_server WHERE serv_name='mogwai' LIMIT 1")
raise SystemExit(0 if cursor.fetchone() else 1)
PY
then
    ./bin/pygdo '$add_server mogwai irc tcps://mogwai.mira-gpt.org:6697'
    ./bin/pygdo '$add_server tcp tcp'
    ./bin/pygdo '$add_server wc irc tcps://irc.wechall.net:6697'
    ./bin/pygdo '$add_server euirc irc tcps://irc.lim.de.euirc.net:6697'
    ./bin/pygdo '$add_server libera irc tcps://irc.libera.chat:6697'
    ./bin/pygdo '$add_server rizon irc tcps://irc.rizon.net:6697'
    ./bin/pygdo '$add_server ircnow irc tcps://irc.ircnow.org:6697'
    ./bin/pygdo '$add_server ger irc tcps://irc.german-elite.net:6697'
fi

./gdo_adm.sh cc
