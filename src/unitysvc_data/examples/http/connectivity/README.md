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
| HTTP 401/403 from gateway | pass | gateway reachable, no active enrollment in ops context |
| Empty / unrendered `SERVICE_BASE_URL` | pass (skip probe) | no enrollment available in ops context |
| HTTP other than 200/401/403 | fail | unexpected gateway response |
| DNS / connect failure | fail | network unreachable |

## Environment variables

**Local testing mode** (`local_testing = true`):

- `HTTP_RELAY_BASE_URL` — upstream endpoint URL (required).
- `HTTP_RELAY_API_KEY` — optional upstream API key; omitted from
  headers when empty.

**Gateway mode** (`local_testing = false`):

- `SERVICE_BASE_URL` — gateway URL. When empty or still containing
  unrendered template syntax (e.g., `enrollment_vars.code` not resolved
  for multi-enrollment services), the probe is skipped and the test
  reports `connectivity ok`.
- Accepts 200, 401, or 403 from the gateway as connectivity success.

## Versions

### v1 — initial release

- `local_testing` branch uses `HTTP_RELAY_BASE_URL` with echo fallback.
- Gateway branch handles empty/unrendered `SERVICE_BASE_URL` and
  401/403 gateway responses by retrying against the echo endpoint.
- Prints `connectivity ok` only on HTTP 200.

### v2 — accept 401/403; remove echo fallback

- Gateway branch no longer falls back to the echo endpoint.
- Accepts 200, 401, and 403 as connectivity success (401/403 means the
  gateway is reachable but has no active enrollment in the ops testing
  context).
- When `SERVICE_BASE_URL` is empty or unrendered, skips the probe and
  exits 0 (no enrollment available in ops testing context).
