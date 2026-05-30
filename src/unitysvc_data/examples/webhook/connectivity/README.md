+++
preset_name = "webhook_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify a Discord-compatible webhook endpoint by POSTing a minimal embeds payload"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook" }
+++

# webhook / connectivity — Discord-compatible webhook smoke test

Connectivity check for services whose upstream is a Discord-compatible
webhook endpoint. POSTs a minimal `embeds` payload to
`{{ service_base_url }}${__webhook_path__}` and asserts HTTP 204
(Discord's success code) in response.

The `webhook_path` parameter is overrideable per listing so the same
preset works for any service regardless of the specific webhook URL
fragment.

## Pass / fail classification

| Condition | Verdict |
|---|---|
| HTTP 204 | pass |
| HTTP 000 (connect / DNS failure) | fail |
| Any other status | fail |

## Template variables

- `{{ service_base_url }}` — upstream base URL (from `upstream_access_config.<iface>.base_url`).

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` to form the full webhook URL. Override in the listing document entry, e.g. `{"$doc_preset": {"name": "webhook_connectivity", "webhook_path": "/api/webhooks/room/token"}}`.

## Versions

### v1 — initial release

- POST `{"embeds":[{"title":"connectivity check","description":"ping"}]}`.
- Asserts HTTP 204.
- Output contains `connectivity ok`.
