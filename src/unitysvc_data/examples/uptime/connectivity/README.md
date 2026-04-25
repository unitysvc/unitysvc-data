+++
preset_name = "uptime_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify an uptime-monitoring bridge accepts a check request and returns a status field"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# uptime / connectivity — bridge smoke test

Bash smoke test for uptime-monitoring bridge services. Triggers a
single check via the bridge endpoint and accepts any JSON object
that contains a `status` field as proof the bridge is alive — the
exact value (`up`, `down`, `degraded`, ...) reflects the monitored
target's health, not the bridge's, so we don't gate on it.

## Modes

| Mode | Body |
|------|------|
| local | `listing.service_options.ops_testing_parameters` rendered to JSON |
| gateway | `{}` (the bridge fills in parameters from the enrollment) |

## Environment variables

- `SERVICE_BASE_URL` — bridge endpoint.
- `UNITYSVC_API_KEY` — bearer token.

## Versions

### v1 — initial release

- POST a small JSON body, 10-second timeout.
- Asserts `"status"` appears anywhere in the response.
