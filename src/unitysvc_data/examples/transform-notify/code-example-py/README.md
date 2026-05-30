+++
preset_name = "transform_notify_code_example_python"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python (httpx) example for notification transformer services: local mode POSTs the upstream payload, gateway mode POSTs a canonical envelope"
is_active = true
is_public = true
meta = { output_contains = "sent", requirements = ["httpx"] }
parameters = { webhook_path = "/webhook", upstream_body = '{"embeds":[{"title":"Hello from UnitySVC","description":"Notification delivered via transformer","footer":{"text":"from user@example.com"}}]}' }
+++

# transform-notify / code-example-py — notification transformer Python example

Dual-mode Python code example for services that accept a canonical notification
envelope on the gateway side and deliver to a specific HTTP notification upstream
(Discord, Slack, Telegram, ntfy, etc.).

## Local mode (`{% if local_testing %}`)

`service_base_url` resolves to the upstream base URL.  The script POSTs the
upstream-specific payload (`upstream_body`) to `service_base_url + webhook_path`.

## Gateway mode

`service_base_url` resolves to the service's HTTP gateway endpoint.  The script
POSTs a canonical notification envelope with a `Bearer` token via `httpx`.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` in
  **local mode only**.
- `upstream_body` (default: Discord `embeds` message) — JSON body posted in local
  mode.  Override per listing with the upstream-specific payload.

## Template variables

- `{{ service_base_url }}` — upstream base URL (local) or HTTP gateway URL (gateway).

## Environment variables

- `UNITYSVC_API_KEY` — required in gateway mode (Bearer token).

## Versions

### v1 — initial release

- Uses `httpx.post` (sync).
- Local: POST parsed `upstream_body` JSON; prints `sent (HTTP <status>)`.
- Gateway: POST canonical `{title, body, from}` with Bearer auth; prints `sent (HTTP <status>)`.
