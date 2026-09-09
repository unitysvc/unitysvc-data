+++
preset_name = "msg_request_template"
category = "request_template"
mime_type = "json"
file = "request-template.json"
description = "Minimal msg envelope request body"
is_active = true
is_public = true
+++

# msg / request-template — minimal msg envelope payload

Canonical JSON request body for services that accept the unified
UnitySVC `msg` envelope (`title`, `body`, `type`, `format`) — the
input format shared by `notify`, `msg-to-mailbox`, and the whole
`msg-to-<channel>` family of notification-relay services. Suitable as
a test payload for seller-side validation, and as `request_template`
metadata attached to a listing so the Test Request playground has a
working starting point.

## Body

```json
{
  "title": "t",
  "body": "hi",
  "type": "info",
  "format": "text"
}
```

## Conventions

- `title` and `body` are kept short so the example is easy to scan and
  the request completes fast regardless of the destination.
- `type` is one of `info` / `success` / `warning` / `failure` — chosen
  here as the harmless default (`info`).
- `format` is `text`; services that also accept `markdown` or `html`
  bodies still validate a plain `text` request.

## Versions

### v1 — initial release

- Four fields (`title`, `body`, `type`, `format`), matching the
  envelope every `msg`-format notification service already documents
  in its own connectivity test / code example.
