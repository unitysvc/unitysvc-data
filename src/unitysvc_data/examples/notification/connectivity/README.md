+++
preset_name = "notification_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for pass-through HTTP notification services"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook", chat_id = "" }
+++

# notification / connectivity

Connectivity test for pass-through notification services. One variant per
upstream API shape; each becomes its own preset (e.g. `notification_connectivity_discord`).

## Local mode

Posts a minimal upstream-format ping directly to the webhook at
`service_base_url + webhook_path`. Asserts the upstream-specific success code.

## Gateway mode

Posts the **same** upstream-format ping to the UnitySVC gateway endpoint.
Only adds `Authorization: Bearer ${UNITYSVC_API_KEY}`. The gateway forwards
the payload to the upstream unchanged.

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

- Local: POST upstream-format ping; assert upstream-specific success code.
- Gateway: POST same ping with Bearer auth; assert HTTP 2xx.
