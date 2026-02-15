#!/bin/bash
h2load -n1000 -c8 -t3 --h1 -p HTTP/1.1 "http://py.giz.org"
h2load -n1    -c1 --h1 -p HTTP/1.1 "http://py.giz.org?__yappi=1"
