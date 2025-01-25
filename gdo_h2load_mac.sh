#!/bin/bash
h2load -n10000 -c25 --h1 -p HTTP/1.1 http://localhost:31337
