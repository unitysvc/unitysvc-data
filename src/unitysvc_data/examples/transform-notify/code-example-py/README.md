+++
preset_name = "transform_notify_code_example_python"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python (httpx) example for notification transformer services: local mode POSTs the upstream payload by type, gateway mode POSTs a canonical envelope"
is_active = true
is_public = true
meta = { output_contains = "sent", requirements = ["httpx"] }
parameters = { webhook_path = "/webhook", upstream_body_type = "discord" }
+++

# transform-notify / code-example-py — notification transformer Python example

Dual-mode Python code example for services that accept a canonical notification
envelope on the gateway side and deliver to a specific HTTP notification upstream.
Uses `httpx` for HTTP transport.

## Local mode (`{% if local_testing %}`)

`service_base_url` resolves to the upstream base URL.  The script selects the
sample payload dict for the given `upstream_body_type` and POSTs it as JSON to
`service_base_url + webhook_path`.

## Gateway mode

`service_base_url` resolves to the service's HTTP gateway endpoint.  The script
POSTs a canonical notification envelope `{"title", "body", "from"}` with a
Bearer token.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` in
  local mode.  Unique per channel instance.
- `upstream_body_type` (default: `discord`) — selects the upstream payload format.

## Supported `upstream_body_type` values

| Type | Used by |
|---|---|
| `discord` | Discord |
| `slack` | Slack, Mattermost, Rocket.Chat, Google Chat, Flock |
| `telegram` | Telegram |
| `msteams` | MS Teams (webhookb2) |
| `matrix` | Matrix |
| `ntfy` | ntfy |
| `gotify` | Gotify |
| `json` | Generic JSON webhook |

## Template variables

- `{{ service_base_url }}` — upstream base URL (local) or HTTP gateway URL (gateway).

## Environment variables

- `UNITYSVC_API_KEY` — required in gateway mode (Bearer token).

## Versions

### v1 — initial release

- Uses `httpx.post` (sync).
- Local: POST type-selected payload dict; prints `sent (HTTP <status>)`.
- Gateway: POST canonical `{title, body, from}` with Bearer auth; prints `sent (HTTP <status>)`.
