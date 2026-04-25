+++
preset_name = "uptime_code_example_python"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: trigger an uptime check and read the bridge's status / response-time metrics"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# uptime / code-example-python — trigger an uptime check

Customer-facing Python example for uptime-monitoring bridges. POSTs
to the bridge endpoint to trigger a check on demand and prints the
returned `status` plus the `metrics.response_ms` timing.

## Modes

| Mode | Body |
|------|------|
| local | `listing.service_options.ops_testing_parameters` rendered as JSON |
| gateway | empty (the bridge fills in parameters from enrollment) |

## Environment variables

- `SERVICE_BASE_URL` — bridge endpoint.
- `UNITYSVC_API_KEY` — bearer token.

## Conventions

- Reads two fields from the bridge response: top-level `status`
  (`up` / `down` / `degraded`) and nested `metrics.response_ms`.
- `raise_for_status()` so non-2xx exits with a stack trace.

## Versions

### v1 — initial release

- POST to `SERVICE_BASE_URL`, optionally with
  `ops_testing_parameters` body in local mode.
- Prints `Status: …` and `Response time: …ms`.
