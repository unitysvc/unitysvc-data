+++
preset_name = "transform_notify_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL example for notification transformer services: local mode POSTs the upstream payload, gateway mode POSTs a canonical envelope"
is_active = true
is_public = true
meta = { output_contains = "sent" }
parameters = { webhook_path = "/webhook", upstream_body = '{"embeds":[{"title":"Hello from UnitySVC","description":"Notification delivered via transformer","footer":{"text":"from user@example.com"}}]}' }
+++

# transform-notify / code-example-sh — notification transformer cURL example

Dual-mode cURL code example for services that accept a canonical notification
envelope on the gateway side and deliver to a specific HTTP notification upstream
(Discord, Slack, Telegram, ntfy, etc.).

## Local mode (`{% if local_testing %}`)

`service_base_url` resolves to the upstream base URL.  The script POSTs the
upstream-specific payload (`upstream_body`) to `service_base_url + webhook_path`,
demonstrating the exact format the transformer delivers to the upstream.

## Gateway mode

`service_base_url` resolves to the service's HTTP gateway endpoint.  The script
POSTs a canonical notification envelope `{"title", "body", "from"}` with a
`Bearer` token — the same format an upstream caller sends when dispatching a
notification through this service.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` in
  **local mode only**.  Override per listing to match the upstream webhook path.
- `upstream_body` (default: Discord `embeds` message) — JSON body posted in local
  mode.  Override per listing with the upstream-specific payload, e.g.
  `{"text":"Hello from UnitySVC"}` for Slack,
  `{"chat_id":"...","text":"Hello"}` for Telegram.

## Template variables

- `{{ service_base_url }}` — upstream base URL (local) or HTTP gateway URL (gateway).

## Environment variables

- `UNITYSVC_API_KEY` — required in gateway mode (Bearer token).

## Versions

### v1 — initial release

- Local: POST `upstream_body` to `service_base_url + webhook_path`; prints HTTP status + `sent`.
- Gateway: POST `{"title":"Hello from UnitySVC","body":"Notification delivered via transformer.","from":"user@example.com"}` to `service_base_url`; prints HTTP status + `sent`.
