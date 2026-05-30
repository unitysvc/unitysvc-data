+++
preset_name = "transform_notify_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for SMTP→notification transformer services"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook" }
+++

# transform-notify / connectivity

Connectivity test for transformer services that convert SMTP messages into
upstream notification payloads.  One variant file per upstream API shape;
each variant becomes its own preset (e.g. `transform_notify_connectivity_discord`).

## Local mode

`service_base_url` resolves to the upstream base URL.  Posts a minimal payload
to `service_base_url + webhook_path` and asserts a successful HTTP status.

## Gateway mode

`service_base_url` resolves to the HTTP gateway endpoint.  Posts a canonical
`{"title", "body", "from"}` envelope with a Bearer token, exercising the full
transformer path.

## Parameters

- `webhook_path` — path appended to `service_base_url` in local mode.
  Unique per channel instance (e.g. `/api/webhooks/123/token`).

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

- Local: POST upstream-format ping payload; assert success status code.
- Gateway: POST `{"title":"connectivity check","body":"ping","from":"test@example.com"}`; assert HTTP 2xx.
