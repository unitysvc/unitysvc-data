+++
preset_name = "smtp_transformer_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL example for SMTP→HTTP transformer services: POSTs Discord embeds to the HTTP upstream in both local and gateway modes"
is_active = true
is_public = true
meta = { output_contains = "sent" }
parameters = { webhook_path = "/webhook" }
+++

# smtp / transformer-code-example-shell — SMTP→HTTP transformer cURL example

Code example for transformer services that accept mail via the SMTP gateway and
forward a reshaped payload to an HTTP upstream (e.g. Discord webhook, Slack,
Teams).  Both local and gateway modes POST Discord `embeds` directly to the HTTP
upstream — the SMTP interface is not exercised here.

## Both modes

The script reads `{{ offering.upstream_access_config.discord.base_url }}` from
the offering (the upstream Discord-compatible base URL) and appends `webhook_path`.
It POSTs a Discord `embeds` payload with a sample notification and asserts HTTP 204.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to the upstream base URL.
  Override per listing to match the upstream webhook path.

## Template variables

- `{{ offering.upstream_access_config.discord.base_url }}` — HTTP upstream base URL.

## Versions

### v1 — initial release

- Both modes: `curl -X POST` Discord `embeds` to `offering.upstream_access_config.discord.base_url + webhook_path`; asserts HTTP 204; prints `sent` on success.
