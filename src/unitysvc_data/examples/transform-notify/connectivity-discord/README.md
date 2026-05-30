+++
preset_name = "transform_notify_connectivity_discord"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for SMTP→Discord transformer services"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook" }
+++

# transform-notify / connectivity-discord

Connectivity test for transformer services whose upstream is a Discord-compatible
webhook.

## Local mode

`service_base_url` resolves to the upstream base URL.  Posts a minimal Discord
`embeds` payload to `service_base_url + webhook_path` and asserts HTTP 204.

## Gateway mode

`service_base_url` resolves to the HTTP gateway endpoint.  Posts a canonical
`{"title", "body", "from"}` envelope with a Bearer token, exercising the full
transformer path.

## Parameters

- `webhook_path` — path appended to `service_base_url` in local mode.
  Unique per channel instance (e.g. `/api/webhooks/123/token`).

## `upstream_body_type` reference

One preset per upstream API shape.  Use the preset whose suffix matches the
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

- Local: POST `{"embeds":[{"title":"connectivity check","description":"ping"}]}`; assert HTTP 204.
- Gateway: POST `{"title":"connectivity check","body":"ping","from":"test@example.com"}`; assert HTTP 2xx.
