+++
preset_name = "transform_notify_code_example_discord_python"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python (httpx) example for SMTP→Discord transformer services"
is_active = true
is_public = true
meta = { output_contains = "sent", requirements = ["httpx"] }
parameters = { webhook_path = "/webhook" }
+++

# transform-notify / code-example-discord-py

Python code example for transformer services whose upstream is a Discord-compatible
webhook.  Uses `httpx` for HTTP transport.

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

- Local: POST Discord `embeds` via `httpx.post`; print `sent (HTTP <status>)`.
- Gateway: POST canonical envelope with Bearer auth; print `sent (HTTP <status>)`.
