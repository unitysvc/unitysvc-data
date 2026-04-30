+++
preset_name = "api_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify HTTP endpoint is reachable and returns a healthy status"
is_active = true
is_public = true
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

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — optional. Sent as `Authorization: Bearer ...` when set. Either the seller's upstream API key (local mode, when `upstream_access_config` carries one) or the customer's svcpass / BYOK secret (gateway mode).

## Versions

### v1 — initial release

- Classifies 2xx/3xx/401/403 as pass; 404/5xx/000 as fail.
- Timeout: 5 seconds.
- Works under `set -u` and `set -o pipefail` on bash 3.2 (macOS
  default).
