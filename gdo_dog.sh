#!/bin/bash
set -euo pipefail

bash gdo_adm.sh wipe -a
bash gdo_adm.sh install irc,telegram,pm,markdown,blackjack,account,admin,contact,perf,math,login,register,recovery,bootstrap5,avatar,shadowdogs,vote,poll,quote,scum,slapwarz,websocket,discord,connect,whatsapp,mira
bash gdo_adm.sh admin gizmore 11113333 gizmore@wechall.net
bash gdo_adm.sh admin mira ChangeMe gizmore@wechall.net
bash gdo_adm.sh admin --server 2 gizmore 11113333 gizmore@wechall.net
pygdo \$add_server giz irc tcp://localhost:6667
pygdo \$add_server nc tcp
pygdo gdo_adm.sh cc
