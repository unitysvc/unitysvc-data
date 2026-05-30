+++
preset_name = "transform_notify_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for notification transformer services: local mode POSTs the upstream payload, gateway mode POSTs a canonical envelope"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook", upstream_body = '{"embeds":[{"title":"connectivity check","description":"ping"}]}' }
+++

# transform-notify / connectivity — notification transformer connectivity test

Dual-mode connectivity test for services that accept a canonical notification
envelope on the gateway side and deliver to a specific HTTP notification upstream
(Discord, Slack, Telegram, ntfy, etc.).

## Local mode (`{% if local_testing %}`)

`service_base_url` resolves to the upstream base URL.  The script POSTs the
upstream-specific payload (`upstream_body`) to `service_base_url + webhook_path`
and asserts any HTTP 2xx, verifying the upstream accepts the format the
transformer will deliver.

## Gateway mode

`service_base_url` resolves to the service's HTTP gateway endpoint.  The script
POSTs a canonical notification envelope `{"title", "body", "from"}` with a
`Bearer` token, exercising the full inbound path: HTTP receive → body transformer
→ upstream delivery.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` in
  **local mode only**.  Override per listing to match the upstream's webhook path.
- `upstream_body` (default: Discord `embeds` ping) — JSON body posted in local
  mode.  Override per listing with the upstream-specific payload format, e.g.
  `{"text":"ping"}` for Slack, `{"message":"ping"}` for Telegram.

## Template variables

- `{{ service_base_url }}` — upstream base URL (local) or HTTP gateway URL (gateway).

## Environment variables

- `UNITYSVC_API_KEY` — required in gateway mode (Bearer token).

## Versions

### v1 — initial release

- Local: POST `upstream_body` to `service_base_url + webhook_path`; asserts HTTP 2xx.
- Gateway: POST `{"title":"connectivity check","body":"ping","from":"test@example.com"}` to `service_base_url`; asserts HTTP 2xx.
- Both modes print `connectivity ok (HTTP <status>)` on success.
