+++
preset_name = "webhook_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL example: POST a Discord embeds payload directly to a webhook endpoint"
is_active = true
is_public = true
parameters = { webhook_path = "/webhook" }
+++

# webhook / code-example-shell — Discord webhook cURL example

Customer-facing cURL example for services whose upstream is a
Discord-compatible webhook. Demonstrates the `embeds` payload shape
delivered to the webhook by POSTing directly to
`{{ service_base_url }}${__webhook_path__}`.

Useful for sellers demonstrating transformer services where the
platform reshapes an inbound message (e.g. SMTP notification) into a
Discord `embeds` payload before forwarding to the configured webhook.

## Request shape

```json
{
  "embeds": [
    {
      "title": "Hello from UnitySVC",
      "description": "Notification delivered via transformer",
      "footer": { "text": "from user@example.com" }
    }
  ]
}
```

## Parameters

- `webhook_path` (default: `/webhook`) — path appended to `service_base_url`. Override per listing to match the actual webhook URL.

## Template variables

- `{{ service_base_url }}` — upstream base URL.

## Versions

### v1 — initial release

- `curl -X POST` with Discord `embeds` JSON.
- Prints `sent` on success.
- **Amended in 0.2.2**: verification moved into the script. The runner-side
  `output_contains` sentinel it used to rely on was retired platform-side
  (unitysvc/unitysvc#2490), so the check is now a real status or
  response-shape assertion, wrapped in `{%- if not customer_display %}` to keep
  it out of the published example. The unconditional success marker is gone.

