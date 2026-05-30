+++
preset_name = "smtp_canonical_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL example: POST the canonical SMTP envelope to an SMTP→HTTP transformer endpoint"
is_active = true
is_public = true
meta = { output_contains = "sent" }
+++

# smtp / canonical-code-example-shell — canonical envelope cURL example

Customer-facing cURL example for SMTP→HTTP transformer services. Demonstrates
the canonical Apprise-shaped envelope that the UnitySVC SMTP gateway produces
from an inbound email and forwards to the transformer route.

The transformer (APISIX `request_transformer`) receives this envelope, reshapes
it into whatever format the downstream channel expects (e.g. Discord `embeds`),
and forwards the result to the configured upstream.

## Request shape

```json
{
  "title": "Hello from UnitySVC",
  "body": "Notification delivered via transformer",
  "body_format": "text",
  "notify_type": "info",
  "from": "user@example.com",
  "to": [],
  "headers": {},
  "attachments": []
}
```

Fields match the output of the Haraka `email_to_http` parser (PR #1121 /
`gateway/smtp/plugins/lib/email_to_http.js`).

## Local-testing behaviour

In `local_testing` mode the `service_base_url` resolves to the upstream (e.g.
the mock Discord webhook), which does not run the transformer pipeline. This
preset therefore exits 0 immediately in local mode — upstream connectivity is
verified by the companion `webhook_connectivity` preset. The gateway-mode path
exercises the full canonical-envelope → transformer → downstream roundtrip.

## Template variables

- `{{ service_base_url }}` — transformer route base URL (set by the gateway
  when rendering for a deployed access interface).

## Versions

### v1 — initial release

- `curl -X POST` with canonical SMTP envelope JSON.
- Checks for HTTP 2xx response from the transformer route.
- Prints `sent` on success; exits non-zero with HTTP status on failure.
- In `local_testing` mode: prints `sent` and exits 0 (upstream test covered
  separately by `webhook_connectivity`).
