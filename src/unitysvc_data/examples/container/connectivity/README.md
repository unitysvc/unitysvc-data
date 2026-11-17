+++
preset_name = "container_connectivity"
category = "connectivity_test"
mime_type = "python"
file = "connectivity.py.j2"
description = "Start the container instance, call every entry, then stop it"
is_active = true
is_public = false
meta = { timeout = 300 }
parameters = { probe_path = "" }
+++

# container / connectivity — generic container-service connectivity test

Python smoke test for any container service (unitysvc/unitysvc#3016). A
container service has no gateway route, so the script drives the
enrollment's instance through the customer API with
[unitysvc-py](https://github.com/unitysvc/unitysvc-py): it starts the
instance, waits for it to come up, `GET`s each of its entries, and always
stops the instance again in a `finally`. The exit status is the verdict;
stdout only narrates (the runner-side `output_contains` matcher was retired
in unitysvc/unitysvc#2490).

Under `local_testing` the script only prints a note and exits 0: the seller
CLI tests a container service locally with Docker, and there is no instance
to drive.

## Exit status

| Exit | Meaning | Rationale |
|------|---------|-----------|
| 0    | pass    | the instance came up and every entry answered |
| 75   | platform failed | the cluster is down, busy or unconfigured (the instance failed with `fault == "platform"`, it was not ready in 180 s, or the customer API did not answer or answered 5xx); retry later |
| 1    | service failed | the instance failed with a seller fault, an entry answered with a failing status, or the customer API refused the request (4xx) |

## Pass / fail classification of an entry

Each entry is probed with `GET entry.url + probe_path`, for up to 60 s while
the answer looks like a route that has not settled yet.

| HTTP status | Verdict | Rationale |
|-------------|---------|-----------|
| 2xx, 3xx    | pass    | entry responding normally |
| 401, 403    | pass    | entry is alive and enforcing auth |
| 405         | pass    | entry is alive but does not take `GET` at that path |
| 404, 502, 503, 504, no answer | retry, then fail | a fresh route settling; the service failed if it stays that way for 60 s |
| anything else | fail  | the service is broken |

The request carries the customer's `UNITYSVC_API_KEY` as a Bearer token for an
entry whose `auth` is `key`, and no credentials for `login` or `app` entries: those
enforce their own auth, and a 401/403 counts as up. There is no platform-issued
instance key; a service's own secret is an ordinary enrollment parameter
(unitysvc/unitysvc#3023).

## Template variables (filled in by the platform when rendering)

- `{{ local_testing }}` — true when the seller CLI runs the test locally.
  A container service has no `service_base_url`.

## Environment variables (read at runtime, platform mode only)

- `UNITYSVC_API_KEY` — the ops customer's API key; needs the `api:*` scope.
  Also sent as `Authorization: Bearer ...` to entries with `auth == "key"`.
- `UNITYSVC_API_URL` — the customer API the instance is driven through.
- `UNITYSVC_ENROLLMENT_ID` — the enrollment whose instance is started.

## Parameters

- `probe_path` (default `""`) — appended to each entry's URL before the
  `GET`, for a service whose entries only answer on a sub-path (a health
  route such as `/healthz`, say). The default probes the entry's URL as
  published.

## Requirements

The script runs with the backend worker's Python, which has `unitysvc-py`
(0.2.7 or later, for `Client().instance(...)`) and its dependency `httpx`
installed.

## Versions

### v1 — initial release

- Starts the instance, waits up to 180 s, probes every entry for up to 60 s
  while the route settles, stops the instance in a `finally`.
- Exit 0 on pass, 75 when the platform failed, 1 when the service failed.
- Classifies 2xx/3xx/401/403/405 as pass; 404/502/503/504 and connection
  errors are retried for 60 s, then fail; anything else fails at once.
- Timeouts: 300 s for the whole run (`meta.timeout`), 15 s per `GET`.

### v1 — amended in place (0.2.16)

- No longer fetches an instance key with `credentials()`: the endpoint was removed
  (unitysvc/unitysvc#3023), so an `app` entry is probed without credentials, like `login`.
  Published only in 0.2.15 and used by one service, so v1 had no working behaviour left to pin to.
