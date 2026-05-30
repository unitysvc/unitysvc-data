+++
preset_name = "transform_notify_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for notification transformer services: local mode POSTs the upstream payload by type, gateway mode POSTs a canonical envelope"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook", upstream_body_type = "discord" }
+++

# transform-notify / connectivity — notification transformer connectivity test

Dual-mode connectivity test for services that accept a canonical notification
envelope on the gateway side and deliver to a specific HTTP notification upstream.

## Local mode (`{% if local_testing %}`)

`service_base_url` resolves to the upstream base URL.  The script selects a
minimal ping payload for the given `upstream_body_type`, POSTs it to
`service_base_url + webhook_path`, and asserts any HTTP 2xx.

## Gateway mode

`service_base_url` resolves to the service's HTTP gateway endpoint.  The script
POSTs a canonical notification envelope `{"title", "body", "from"}` with a
Bearer token, exercising the full inbound path through the transformer.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` in
  local mode.  Unique per channel instance (e.g. `/api/webhooks/123/token`).
- `upstream_body_type` (default: `discord`) — selects the upstream payload format.
  One type covers all services sharing the same API shape.

## Supported `upstream_body_type` values

| Type | Payload shape | Used by |
|---|---|---|
| `discord` | `{"embeds":[{"title":…,"description":…}]}` | Discord |
| `slack` | `{"text":…}` | Slack, Mattermost, Rocket.Chat, Google Chat, Flock |
| `telegram` | `{"chat_id":…,"text":…}` | Telegram |
| `msteams` | `{"type":"message","text":…}` | MS Teams (webhookb2) |
| `matrix` | `{"msgtype":"m.text","body":…}` | Matrix |
| `ntfy` | `{"message":…,"title":…}` | ntfy |
| `gotify` | `{"message":…,"title":…,"priority":3}` | Gotify |
| `json` | `{"title":…,"message":…}` | Generic JSON webhook |

## Template variables

- `{{ service_base_url }}` — upstream base URL (local) or HTTP gateway URL (gateway).

## Environment variables

- `UNITYSVC_API_KEY` — required in gateway mode (Bearer token).

## Versions

### v1 — initial release

- Local: POST type-selected ping payload to `service_base_url + webhook_path`; asserts HTTP 2xx; prints `connectivity ok (HTTP <status>)`.
- Gateway: POST `{"title":"connectivity check","body":"ping","from":"test@example.com"}` to `service_base_url`; asserts HTTP 2xx; prints `connectivity ok (HTTP <status>)`.
