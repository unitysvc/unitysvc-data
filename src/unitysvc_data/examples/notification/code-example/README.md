+++
preset_name = "notification_code_example"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a notification through the UnitySVC notify gateway"
is_active = true
is_public = true
meta = { test = { status = "skip" } }
+++

# notification / code-example — notify gateway Python example

Customer-facing primary example for notification services. Sends a
POST request to `{SERVICE_BASE_URL}/send` with a target, message, and
format.

## Request shape

```json
{
  "target": "",
  "message": "Hello from UnitySVC!",
  "format": "text"
}
```

The `target` field is channel-specific: a chat ID for Telegram/Discord,
a phone number (E.164) for WhatsApp/Signal/SMS, a room ID for Matrix,
an empty string for webhook-only channels (Slack, Google Chat, Teams),
etc.

## Environment variables

- `SERVICE_BASE_URL` — gateway base URL for this service (required).
- `UNITYSVC_API_KEY` — customer gateway key (required).

## Versions

### v1 — initial release

- POSTs to `{SERVICE_BASE_URL}/send`.
- Generic `target` placeholder with a comment directing the customer
  to substitute their channel-specific value.
- Default `meta.test.status = "skip"` — live tests require an active
  enrollment with real channel credentials.
