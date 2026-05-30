+++
preset_name = "notify_relay_code_example_sh"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL code example for pass-through HTTP notification services"
is_active = true
is_public = true
meta = { output_contains = "sent" }
parameters = { webhook_path = "/webhook", chat_id = "" }
+++

# notification / code-example-sh

cURL code examples for pass-through notification services. One variant per
upstream API shape; each becomes its own preset (e.g. `notification_code_example_sh_discord`).

## Local mode

Posts an upstream-format payload directly to the webhook via curl.

## Gateway mode

Posts the **same** upstream-format payload to the UnitySVC gateway.
Only adds `Authorization: Bearer ${UNITYSVC_API_KEY}`.

## Parameters

- `webhook_path` — path appended to `service_base_url` in local mode.
- `chat_id` — receiver ID used by telegram variant.

## Upstream type reference

| Variant | Key body fields | Channels |
|---|---|---|
| `discord` | `embeds` / `content` | discord |
| `slack` | `text` / `blocks` | slack, mattermost, rocketchat, gchat, flock, webex, notifico |
| `telegram` | `chat_id`, `text` | telegram |
| `msteams` | `@type`, `@context` | msteams (webhookb2) |
| `matrix` | `msgtype`, `body` | matrix |
| `ntfy` | `message` | ntfy |
| `gotify` | `message` | gotify (token via webhook_path `?token=...`) |
| `ryver` | `body` | ryver |
| `json` | `message` | json (generic Apprise webhook) |

## Versions

### v1 — initial release

- Local: POST upstream-format payload; print HTTP status + `sent`.
- Gateway: POST same payload with Bearer auth; print HTTP status + `sent`.
