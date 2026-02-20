#!/bin/bash
set -euo pipefail

bash gdo_adm.sh wipe -a
bash gdo_adm.sh install account,admin,avatar,blackjack,bootstrap5,chess,chatgpt4o,connect,contact,favicon,gogol,icon_fa,irc,login,markdown,math,perf,pm,poll,quote,register,scum,shadowdogs,slapwarz,vote,websocket,wechall
bash gdo_adm.sh admin gizmore 11111111 giz@wechall.net
bash gdo_adm.sh admin christianbusch 11111111 cb@wechall.net
bash gdo_adm.sh admin --server 2 gizmore 11111111 gizmore@wechall.net
pygdo \$add_server giz irc tcp://irc.giz.org:6667
bash gdo_adm.sh admin --server 3 gizmore 11111111 gizmore@wechall.net
pygdo \$add_server nc tcp
pygdo gdo_adm.sh cc
