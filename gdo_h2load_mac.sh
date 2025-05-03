#!/bin/bash
h2load -n10000 -c20 --h1 -p HTTP/1.1 http://localhost:31337
h2load -n1 -c1 --h1 -p HTTP/1.1 "http://localhost:31337?__yappi=1"
