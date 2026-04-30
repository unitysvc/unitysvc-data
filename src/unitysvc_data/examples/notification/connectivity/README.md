+++
preset_name = "notification_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify notification delivery via POST /send through the notify gateway"
is_active = true
is_public = false
meta = { test = { status = "skip" } }
+++

# notification / connectivity — notify gateway connectivity test

Bash smoke test for notification services that speak the UnitySVC
notify protocol. Sends a POST to `/send` with an empty target and
a test message, then checks for an `"ok"` field in the JSON response.

## Pass / fail classification

| Condition | Verdict | Rationale |
|-----------|---------|-----------|
| Response body contains `"ok"` | pass | notify worker delivered or accepted the message |
| curl fails (non-zero exit) | fail | endpoint unreachable or returned non-2xx |
| Response body missing `"ok"` | fail | unexpected response shape |

## Environment variables

- `SERVICE_BASE_URL` — gateway base URL for this service (required).
- `UNITYSVC_API_KEY` — customer or ops-testing gateway key (required).

## Versions

### v1 — initial release

- POSTs `{"target":"","message":"unitysvc connectivity test","format":"text"}`.
- Checks for `"ok"` in the response body.
- Default `meta.test.status = "skip"` — tests require active enrollment
  with real channel credentials.
