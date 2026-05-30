+++
preset_name = "transform_notify_code_example_discord_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL example for SMTP→Discord transformer services"
is_active = true
is_public = true
meta = { output_contains = "sent" }
parameters = { webhook_path = "/webhook" }
+++

# transform-notify / code-example-discord-sh

cURL code example for transformer services whose upstream is a Discord-compatible
webhook.

## Local mode

Posts a Discord `embeds` payload directly to the upstream webhook, demonstrating
the exact format the transformer delivers.

## Gateway mode

Posts a canonical `{"title", "body", "from"}` envelope to the HTTP gateway
endpoint.  The transformer converts it and forwards the embeds payload upstream.

## Parameters

- `webhook_path` — path appended to `service_base_url` in local mode.

## `upstream_body_type` reference

See `transform_notify_connectivity_discord` README for the full preset-per-type
reference table.

## Versions

### v1 — initial release

- Local: POST Discord `embeds` to `service_base_url + webhook_path`; print HTTP status + `sent`.
- Gateway: POST canonical envelope with Bearer auth; print HTTP status + `sent`.
