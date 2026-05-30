+++
preset_name = "smtp_transformer_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL example for SMTP→HTTP transformer services: HTTP upstream in local mode, SMTP gateway in gateway mode"
is_active = true
is_public = true
meta = { output_contains = "sent" }
parameters = { webhook_path = "/webhook" }
+++

# smtp / transformer-code-example-shell — SMTP→HTTP transformer cURL example

Dual-mode code example for transformer services that accept mail via the SMTP
gateway and forward a reshaped payload to an HTTP upstream (e.g. Discord webhook,
Slack, Teams).

## Local-testing mode (`{% if local_testing %}`)

`service_base_url` resolves to the HTTP upstream base URL.  The script POSTs the
transformer's expected **output** format (Discord `embeds`) directly to
`service_base_url + webhook_path`, verifying the upstream endpoint is reachable
and accepts the payload the transformer will deliver.

## Gateway mode

`service_base_url` resolves to the SMTP gateway base URL (`smtp://` or
`smtps://`). The script sends an email via curl's built-in SMTP client,
exercising the customer-facing interface end-to-end. The gateway transformer
converts the email into the downstream format and forwards it to the upstream.

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url` in
  **local mode only**. Override per listing to match the upstream webhook path.

## Template variables

- `{{ service_base_url }}` — upstream base URL (local) or gateway SMTP URL (gateway).
- `{{ routing_key.username }}` — SMTP username (gateway mode only).

## Versions

### v1 — initial release

- Local mode: `curl -X POST` Discord `embeds` to `service_base_url + webhook_path`; asserts HTTP 204.
- Gateway mode: `curl smtp[s]://` with `--mail-from`, `--mail-rcpt`, `-T` (inline temp-file email); reads `UNITYSVC_API_KEY` for SMTP password.
- Both modes print `sent` on success.
