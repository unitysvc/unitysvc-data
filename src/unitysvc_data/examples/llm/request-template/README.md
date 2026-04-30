+++
preset_name = "llm_request_template"
category = "request_template"
mime_type = "json"
file = "request-template.json"
description = "Minimal OpenAI-compatible chat completion request body"
is_active = true
is_public = true
+++

# llm / request-template — minimal chat completion payload

Canonical JSON request body for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Suitable as a test
payload for seller-side validation, and as `request_template`
metadata attached to a listing.

## Body

```json
{
  "max_tokens": 100,
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user",   "content": "Say hello in one sentence." }
  ]
}
```

## What's intentionally missing

- **No `model` field.** The gateway's routing config or the listing's
  `upstream_access_config` selects the upstream model; hard-coding
  one here would tie the template to a specific service.
- **No `stream` field.** Non-streaming responses are simpler to
  validate in tests; streaming variants belong in separate presets.

## Conventions

- `max_tokens` is kept small (≤ 100) so the request completes fast
  against any upstream regardless of per-token latency.
- Response format is standard OpenAI `chat.completions`. Tests should
  assert `choices[0].message.content` exists and is non-empty.

## Versions

### v1 — initial release

- Two messages (system + user), `max_tokens = 100`, no model field,
  non-streaming.
