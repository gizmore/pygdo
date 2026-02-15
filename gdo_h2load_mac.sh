#!/bin/bash
h2load -n1 --h1 -p HTTP/1.1 "http://localhost:31337" > /dev/null
h2load -n10000 -c16 -t4 --h1 -p HTTP/1.1 "http://localhost:31337"
h2load -n1     -c1 --h1 -p HTTP/1.1 "http://localhost:31337?__yappi=1" > /dev/null
