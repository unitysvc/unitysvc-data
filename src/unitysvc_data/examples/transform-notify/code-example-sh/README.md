+++
preset_name = "transform_notify_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL example for notification transformer services: local mode POSTs the upstream payload by type, gateway mode POSTs a canonical envelope"
is_active = true
is_public = true
meta = { output_contains = "sent" }
parameters = { webhook_path = "/webhook", upstream_body_type = "discord" }
+++

# transform-notify / code-example-sh — notification transformer cURL example

Dual-mode cURL code example for services that accept a canonical notification
envelope on the gateway side and deliver to a specific HTTP notification upstream.

## Local mode (`{% if local_testing %}`)

`service_base_url` resolves to the upstream base URL.  The script selects the
sample payload for the given `upstream_body_type` and POSTs it to
`service_base_url + webhook_path`, demonstrating the exact format the transformer
delivers to the upstream.

## Gateway mode

`service_base_url` resolves to the service's HTTP gateway endpoint.  The script
POSTs a canonical notification envelope `{"title", "body", "from"}` with a
Bearer token — the same format a caller sends when dispatching through this service.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` in
  local mode.  Unique per channel instance (e.g. `/api/webhooks/123/token`).
- `upstream_body_type` (default: `discord`) — selects the upstream payload format.
  One type covers all services sharing the same API shape.

## Supported `upstream_body_type` values

| Type | Payload shape | Used by |
|---|---|---|
| `discord` | `{"embeds":[{"title":…,"description":…,"footer":…}]}` | Discord |
| `slack` | `{"text":…}` | Slack, Mattermost, Rocket.Chat, Google Chat, Flock |
| `telegram` | `{"chat_id":…,"text":…}` | Telegram |
| `msteams` | `{"type":"message","text":…}` | MS Teams (webhookb2) |
| `matrix` | `{"msgtype":"m.text","body":…}` | Matrix |
| `ntfy` | `{"message":…,"title":…}` | ntfy |
| `gotify` | `{"message":…,"title":…,"priority":5}` | Gotify |
| `json` | `{"title":…,"message":…}` | Generic JSON webhook |

## Template variables

- `{{ service_base_url }}` — upstream base URL (local) or HTTP gateway URL (gateway).

## Environment variables

- `UNITYSVC_API_KEY` — required in gateway mode (Bearer token).

## Versions

### v1 — initial release

- Local: POST type-selected sample payload to `service_base_url + webhook_path`; prints HTTP status + `sent`.
- Gateway: POST `{"title":"Hello from UnitySVC","body":"…","from":"user@example.com"}` to `service_base_url`; prints HTTP status + `sent`.
