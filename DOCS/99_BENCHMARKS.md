# Benchmarks

This page is a starting point for comparing PyGDO with other frameworks,
including the Django demo on Mogwai. No comparative benchmark results have
been recorded here yet.

## Mogwai comparison setup

Snapshot of the Django demo configuration on 2026-11-26; check the current
configuration again before a run. Django is 6.1.4 development code, running
HTTP through Apache mod_wsgi with SQLite; WebSockets use Daphne. The Python environment is shared
with other Mogwai software. The demo enables these Django apps:

| App | Role |
| --- | --- |
| admin | Administrative interface. |
| auth | Authentication and permissions. |
| contenttypes | Django model/content-type registry. |
| sessions | Session storage. |
| messages | One-time messages for web requests. |
| staticfiles | Static asset management. |
| channels | ASGI and WebSocket support. |
| corsheaders | Cross-origin request headers. |
| guardian | Object-level permissions. |
| forum | Demo's local forum and presence implementation; not a third-party app. |

Other packages installed in the shared environment but **not enabled in the
demo's `INSTALLED_APPS`** include `django-telegram-app`, `django-filer`,
`django-paypal`, `django-postman`, `django-online-users`, `django-jazzmin`,
and `django-bootstrap5`. Installation alone does not provide an active feature.
Postman's message-query test failed against this Django version; the old
online-users test suite imports a removed Django API. Photologue was not
installed: its published dependency requires Django below 6.1.

The PyGDO checkout contains separate modules such as `forum`, `online`,
`websocket`, `telegram`, `downloads`, and `payment_paypal`. Their presence in
the checkout does not prove that each is installed or enabled on a given site;
record actual module configuration and compare equivalent behavior per test.

## Logging on Mogwai

The Django demo has no custom `LOGGING` setting; its WebSocket Daphne service
runs under systemd. The Apache vhosts for both Django and PyGDO specify separate access
and error logs. Apache access logging is distinct from application request
logging: PyGDO request logging is off per the operator, but its Apache vhost
still specifies an access log. PyGDO's exception logger writes to its configured
log directory. This describes configuration, not a verification that every
request or error reaches a particular log.

## Make comparisons fair

- Compare equivalent pages and features, including authentication, database
  reads, caching, and response content. Record the versions and configuration.
- Keep the machine, request concurrency, warm-up, test duration, and load
  generator consistent. Repeat runs and report latency percentiles, throughput,
  error rate, and resource usage rather than a single best result.
- Record the database engine and dataset size, and whether caches are cold or
  warm. Separate an empty page from a database-backed page.
- Check application and web-server access logging independently: on Mogwai,
  the Apache configurations for both sites specify access and error logs. Do
  not assume disabling PyGDO request logging disables Apache access logs.
  Record logging settings for both sides; keep error logging enabled.
- Run load tests only against an authorized target and at a rate that will not
  disrupt other services. Never include credentials or private log contents in
  published results.

## Results

No comparison was measured when this document was created. For each run,
record the date, revision, environment, workload, commands, configuration,
results, and known limitations.

## Running a comparison

`gdo_benchmark.sh` uses ApacheBench (`ab`) and runs PyGDO first, then Django.
Both URLs must be explicitly supplied; use equivalent pages on authorized
targets. It defaults to 100 requests at concurrency 5, for example:

```sh
./gdo_benchmark.sh -n 100 -c 5 https://pygdo.example/ https://django.example/
```

Successful runs append both raw reports and local version information to this
file. The default Python for version detection is `python3`; set
`BENCHMARK_PYTHON` to the Python interpreter used by Django when needed. This
reports the local checkout and installed Django package, which may differ from
the versions actually serving the URLs. Results can include requested paths;
do not use URLs containing secrets, and review the report before publishing.

The raw ApacheBench reports include response failures, non-2xx responses, and
latency percentiles. Review those before comparing results. This is a sequential
HTTP/1.x test, not an HTTP/2 test, and does not automatically equalize content,
logging, caching, or authentication. Test order and warm-up may affect results.


### Run 2026-11-26 12:31:50 UTC

```text
Benchmark started: 2026-11-26 12:31:22 UTC
Requests: 2500; concurrency: 4
PyGDO revision: 362d935
PyGDO tracked worktree: modified
Python: 3.14.7 (/home/gizmore/.pyenv/versions/3.14.7/bin/python3)
Django package: 6.1.4.dev20261126104209

=== PyGDO ===
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking mogwai.mira-gpt.org (be patient)


Server Software:        Apache/2.4.58
Server Hostname:        mogwai.mira-gpt.org
Server Port:            443
SSL/TLS Protocol:       TLSv1.3,TLS_AES_256_GCM_SHA384,256,256
Server Temp Key:        X25519 253 bits
TLS Server Name:        mogwai.mira-gpt.org

Document Path:          /
Document Length:        15444 bytes

Concurrency Level:      4
Time taken for tests:   10.451 seconds
Complete requests:      2500
Failed requests:        1715
   (Connect: 0, Receive: 0, Length: 1715, Exceptions: 0)
Total transferred:      39334033 bytes
HTML transferred:       38611533 bytes
Requests per second:    239.22 [#/sec] (mean)
Time per request:       16.721 [ms] (mean)
Time per request:       4.180 [ms] (mean, across all concurrent requests)
Transfer rate:          3675.54 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        3    5   1.0      5       9
Processing:     5   12   1.3     12      25
Waiting:        5   11   1.3     11      25
Total:          8   17   1.4     17      31

Percentage of the requests served within a certain time (ms)
  50%     17
  66%     17
  75%     17
  80%     18
  90%     18
  95%     19
  98%     19
  99%     20
 100%     31 (longest request)

=== Django ===
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking django.mogwai.mira-gpt.org (be patient)


Server Software:        Apache/2.4.58
Server Hostname:        django.mogwai.mira-gpt.org
Server Port:            443
SSL/TLS Protocol:       TLSv1.3,TLS_AES_256_GCM_SHA384,256,256
Server Temp Key:        X25519 253 bits
TLS Server Name:        django.mogwai.mira-gpt.org

Document Path:          /
Document Length:        1694 bytes

Concurrency Level:      4
Time taken for tests:   17.768 seconds
Complete requests:      2500
Failed requests:        2498
   (Connect: 0, Receive: 0, Length: 2498, Exceptions: 0)
Total transferred:      5010002 bytes
HTML transferred:       4232502 bytes
Requests per second:    140.70 [#/sec] (mean)
Time per request:       28.429 [ms] (mean)
Time per request:       7.107 [ms] (mean, across all concurrent requests)
Transfer rate:          275.36 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        8   13  10.5     12     134
Processing:     6   15  12.1     14     148
Waiting:        6   14  11.1     13     134
Total:         17   28  15.9     26     161

Percentage of the requests served within a certain time (ms)
  50%     26
  66%     26
  75%     27
  80%     28
  90%     29
  95%     33
  98%     63
  99%    143
 100%    161 (longest request)

```
