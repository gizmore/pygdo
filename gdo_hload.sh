#!/bin/bash
h2load -n10000 -c16 --h1 -p HTTP/1.1 "http://localhost"
h2load -n1     -c1  --h1 -p HTTP/1.1 "http://localhost?__yappi=1"
