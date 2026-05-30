+++
preset_name = "transform_notify_code_example_py"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python (httpx) code example for SMTP→notification transformer services"
is_active = true
is_public = true
meta = { output_contains = "sent", requirements = ["httpx"] }
parameters = { webhook_path = "/webhook", chat_id = "" }
+++

# transform-notify / code-example-py

Python (httpx) code examples for transformer services that convert SMTP messages
into upstream notification payloads.  One variant file per upstream API shape;
each variant becomes its own preset (e.g. `transform_notify_code_example_py_discord`).

## Local mode

Posts an upstream-format payload directly to the webhook, demonstrating
the exact format the transformer delivers.

## Gateway mode

Posts a canonical `{"title", "body", "from"}` envelope to the HTTP gateway
endpoint.  The transformer converts it and forwards the payload upstream.

## Parameters

- `webhook_path` — path appended to `service_base_url` in local mode.

## `upstream_body_type` reference

One variant per upstream API shape.  Use the variant whose suffix matches the
upstream of the service being listed.

| Preset suffix | Key body fields | Channels |
|---|---|---|
| `discord` | `embeds` / `content` / `file` | discord |
| `slack` | `text` / `blocks` | slack, mattermost, rocketchat, gchat, flock, webex, join, groupme, notifico |
| `telegram` | `chat_id`, `text` | telegram |
| `msteams` | `@type`, `@context` | msteams (webhookb2) |
| `matrix` | `msgtype`, `body` | matrix |
| `ryver` | `body` | ryver |
| `ntfy` | `message` | ntfy |
| `gotify` | `message` | gotify |
| `json` | `message` | json (generic sink) |

## Versions

### v1 — initial release

- Local: POST upstream-format payload via `httpx.post`; print `sent (HTTP <status>)`.
- Gateway: POST canonical envelope with Bearer auth; print `sent (HTTP <status>)`.
