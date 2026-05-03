+++
preset_name = "notification_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify a notification gateway endpoint by issuing a tiny POST /send"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# notification / connectivity — notify gateway smoke test

Connectivity check for notification services routed through the
UnitySVC notify gateway.  POSTs a one-token notification to `/send`
with an empty `target` (channels that ignore target on connectivity
probes — webhooks — accept this; channels that need a real target
will reject with a 4xx, which is also a valid signal that the gateway
is reachable, but we don't try to be clever about that here — sellers
can override the rendered request body via per-listing parameters in
a future revision if needed).

Captures the HTTP status separately from the body so the response
surfaces in stderr on failure.  The bare
`curl --fail-with-body | grep -q` shortcut eats the body and leaves
operators with just an exit code; this preset's failure output tells
them exactly what the upstream said.

## Pass / fail classification

| Condition | Verdict |
|---|---|
| HTTP 2xx with non-empty response body | pass |
| HTTP 2xx with empty body | fail (upstream returned no payload — protocol regression) |
| HTTP non-2xx | fail |

The check is intentionally loose on body content because notification
upstreams differ widely in their response shape — ntfy returns a
message receipt, the mock upstream echoes the request, the
notification gateway wraps with its own envelope.  HTTP 2xx + non-zero
body length is the lowest common denominator for "the upstream
accepted and processed the request."

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — gateway base URL.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required.

## Versions

### v1 — initial release

- POST `/send` with `{target: "", message: "unitysvc connectivity test", format: "text"}`.
- Status-capture + body-on-failure pattern.
- Output contains `connectivity ok` — paired with the
  `output_contains = "connectivity ok"` meta so the run-tests flow
  can confirm a real round-trip.
