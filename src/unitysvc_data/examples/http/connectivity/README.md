+++
preset_name = "http_relay_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify HTTP relay endpoint is reachable and returns a healthy status"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# http / connectivity — HTTP relay connectivity test

Bash smoke test for HTTP relay services (BYOE/BYOK patterns). Handles
both managed-upstream and customer-provided-endpoint cases, including
multi-enrollment services where the gateway URL contains unresolved
template syntax at ops-testing time.

## Pass / fail classification

| Condition | Verdict | Rationale |
|-----------|---------|-----------|
| HTTP 200 from upstream (local) or gateway (online) | pass | endpoint healthy |
| 401/403 from gateway with no enrollment | falls back to echo endpoint | no enrollment in ops context |
| DNS / connect failure on fallback URL | fail | network unreachable |
| HTTP != 200 on final URL | fail | endpoint broken |

## Environment variables

**Local testing mode** (`local_testing = true`):

- `HTTP_RELAY_BASE_URL` — upstream endpoint URL; defaults to the echo
  staging endpoint.
- `HTTP_RELAY_API_KEY` — optional upstream API key; omitted from
  headers when empty.

**Gateway mode** (`local_testing = false`):

- `SERVICE_BASE_URL` — gateway URL. Falls back to the echo staging
  endpoint when empty or when the URL still contains unrendered
  template syntax (e.g., `enrollment_vars.code` not resolved for
  multi-enrollment services).
- Falls back again to echo endpoint if the gateway returns 401/403
  (no active enrollment in ops-testing context).

## Versions

### v1 — initial release

- `local_testing` branch uses `HTTP_RELAY_BASE_URL` with echo fallback.
- Gateway branch handles empty/unrendered `SERVICE_BASE_URL` and
  401/403 gateway responses by retrying against the echo endpoint.
- Prints `connectivity ok` only on HTTP 200.
