+++
preset_name = "s3_relay_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "relay-connectivity.sh.j2"
description = "Verify S3 relay endpoint is reachable via HTTP status check"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# s3 / relay-connectivity — S3 relay connectivity test

Bash smoke test for S3 relay services (BYOE bucket patterns). Verifies
the S3 endpoint is reachable by checking that the HTTP response code
indicates the server is alive (2xx, 3xx, or 403 all confirm reachability).

## Modes

| Mode | Variable | Behaviour |
|------|----------|-----------|
| Local | `S3_ENDPOINT` or `SERVICE_BASE_URL` | curls the endpoint directly |
| Gateway | `SERVICE_BASE_URL` | curls `$SERVICE_BASE_URL/` |

In local mode, `S3_ENDPOINT` takes precedence over `SERVICE_BASE_URL`
(supports multi-enrollment services). The status codes 200, 301, and
403 all indicate connectivity — a 403 means the endpoint is alive and
enforcing auth, which is expected for secured S3 upstreams.

## Versions

### v1 — initial release

- Local-mode endpoint: `S3_ENDPOINT` or `SERVICE_BASE_URL`, defaulting
  to the staging S3 endpoint.
- Accepts 200/301/403 as connectivity ok; all other codes are failure.
