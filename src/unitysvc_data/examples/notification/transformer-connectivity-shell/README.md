+++
preset_name = "notification_transformer_connectivity_shell"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for notification transformer services: POSTs Discord embeds to the HTTP upstream in both local and gateway modes"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook" }
+++

# notification / transformer-connectivity-shell — notification transformer connectivity test

Connectivity test for transformer services that reshape inbound messages (e.g.
email via SMTP) into an HTTP upstream notification payload (e.g. Discord
`embeds`).  Both local and gateway modes POST Discord `embeds` directly to the
HTTP upstream — the inbound transport interface is not exercised here.

## Both modes

The script reads `{{ offering.upstream_access_config.discord.base_url }}` from
the offering (the upstream Discord-compatible base URL) and appends `webhook_path`.
It POSTs a minimal Discord `embeds` payload and asserts HTTP 204.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to the upstream base URL.

## Template variables

- `{{ offering.upstream_access_config.discord.base_url }}` — HTTP upstream base URL.

## Versions

### v1 — initial release

- Both modes: `curl -X POST` Discord `embeds` to `offering.upstream_access_config.discord.base_url + webhook_path`; asserts HTTP 204; prints `connectivity ok`.
