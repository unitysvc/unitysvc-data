+++
preset_name = "api_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify HTTP endpoint is reachable and returns a healthy status"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# api / connectivity — generic HTTP connectivity test

Bash smoke test for any HTTP-based service (echo relays, mock LLMs,
proxy variants, any endpoint fronted by an HTTP gateway). The script
`curl`s the endpoint and classifies the response.

## Pass / fail classification

| HTTP status | Verdict | Rationale |
|-------------|---------|-----------|
| 2xx, 3xx    | pass    | endpoint responding normally |
| 401, 403    | pass    | endpoint is alive and enforcing auth |
| 404         | fail    | wrong path — misconfigured |
| 5xx         | fail    | upstream broken |
| 000         | fail    | connect / DNS / timeout |

## Environment variables

Provided identically by the test harness in both local and gateway
modes, so the script does not branch on `local_testing`:

- `SERVICE_BASE_URL` — upstream URL (local) or gateway URL (online).
- `UNITYSVC_API_KEY` — optional. Seller's upstream api key if present
  in `upstream_access_config` (local mode), or the customer's gateway
  key (online mode). Sent as `Authorization: Bearer ...` when set.

## Versions

### v1 — initial release

- Classifies 2xx/3xx/401/403 as pass; 404/5xx/000 as fail.
- Timeout: 5 seconds.
- Works under `set -u` and `set -o pipefail` on bash 3.2 (macOS
  default).
