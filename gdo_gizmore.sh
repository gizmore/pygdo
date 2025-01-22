#!/bin/bash

bash gdo_adm.sh wipe -a
bash gdo_adm.sh install irc,chatgpt4o,pm,markdown,blackjack,account,admin,contact,perf,math,login,register,bootstrap5,avatar
bash gdo_adm.sh admin gizmore 11111111 gizmore@wechall.net
bash gdo_adm.sh admin christianbusch 11111111 cb@wechall.net
bash gdo_adm.sh admin --server 2 gizmore 11111111 gizmore@wechall.net
pygdo \$add_server giz irc tcp://irc.giz.org:6667
pygdo gdo_adm.sh cc
pygdo \$cc
