+++
preset_name = "notification_code_example"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a notification via the UnitySVC notify gateway"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# notification / code-example — notify gateway Python example

Customer-facing primary example for notification services.  Sends a
`POST /send` to the gateway with a target, a message, and a content
format.

## Request shape

```json
{
  "target": "",
  "message": "Hello from UnitySVC!",
  "format": "text"
}
```

The `target` field is **channel-specific** — sellers shipping a
notification service should override the rendered example's `target`
default to a value that exercises their channel:

| Channel | `target` example |
|---|---|
| Telegram, Discord, Matrix | chat / room ID |
| WhatsApp, Signal, SMS | E.164 phone number |
| Slack, Google Chat, Teams (incoming-webhook style) | empty string — the webhook URL is baked into the routing key |
| Email | RFC-5322 address |

`format` accepts `"text"`, `"markdown"`, or `"html"` depending on what
the upstream channel supports.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — gateway base URL.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required.  Bearer token: customer's svcpass
  for gateway access, or an upstream key when wired as a secret
  (BYOK).

## Versions

### v1 — initial release

- POST `/send` with a placeholder target, fixed message, `format: text`.
- `response.raise_for_status()` — non-2xx raises and exits non-zero.
- Prints the response JSON on success.
