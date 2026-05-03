+++
preset_name = "llm_request_template_anthropic"
category = "request_template"
mime_type = "json"
file = "request-template-anthropic.json"
description = "Minimal Anthropic Messages API request body"
is_active = true
is_public = true
+++

# llm / request-template-anthropic — minimal Messages API payload

Canonical JSON request body for Anthropic Messages API endpoints
(`/v1/messages`). Suitable as a test payload for seller-side
validation and as `request_template` metadata attached to a listing.

## Body

```json
{
  "max_tokens": 100,
  "system": "You are a helpful assistant.",
  "messages": [
    { "role": "user", "content": "Say hello in one sentence." }
  ]
}
```

## Differences from `llm_request_template`

- **`max_tokens` is required** — Anthropic 4xxs without it; OpenAI
  treats it as optional.
- **`system` is a top-level field**, not a `role: "system"` entry in
  `messages`. Anthropic doesn't support a system-role message.
- No `model` field — the gateway's routing config or the listing's
  `upstream_access_config` selects it (same convention as the OpenAI
  template).

## Conventions

- `max_tokens` kept small (≤ 100) so the request completes fast.
- Response shape is `content[0].text` rather than
  `choices[0].message.content`. Tests should assert
  `content[0].text` exists and is non-empty.

## Versions

### v1 — initial release

- One user message, top-level `system`, `max_tokens = 100`, no model field.
