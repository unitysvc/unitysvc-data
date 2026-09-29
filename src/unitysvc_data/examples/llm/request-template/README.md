+++
preset_name = "llm_request_template"
category = "request_template"
mime_type = "json"
file = "request-template.json"
description = "Minimal chat request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "chat" }
+++

# llm / request-template — minimal chat payload, per request format

The default request body the Test Request playground offers for a chat
service. From v2 it carries one body per request format, keyed by the
gateway's format names (`input_formats` / `request_formats`), so every
chat service ships the same document whatever formats it accepts. The
playground uses `template[format]` for the format the customer picked
(unitysvc/unitysvc#2508); entries for formats a service doesn't accept are
ignored.

## Body (v2)

| Key                | Wire shape                                     |
|--------------------|------------------------------------------------|
| `openai`           | OpenAI Chat Completions                        |
| `anthropic`        | Anthropic Messages (`system` is top-level)     |
| `cohere`           | Cohere v2 Chat (native `/v2/chat`)             |
| `dashscope`        | DashScope native (`input.messages` + `parameters`) |
| `bedrock_converse` | Bedrock Converse (content blocks, `inferenceConfig`) |

```json
{
  "openai":    { "max_tokens": 100, "messages": [ system, user ] },
  "anthropic": { "max_tokens": 100, "system": "...", "messages": [ user ] },
  "cohere":    { "max_tokens": 100, "messages": [ system, user ] },
  "dashscope": { "input": { "messages": [ system, user ] },
                 "parameters": { "max_tokens": 100, "result_format": "message" } },
  "bedrock_converse": { "system": [ { "text": "..." } ],
                        "messages": [ { "role": "user", "content": [ { "text": "..." } ] } ],
                        "inferenceConfig": { "maxTokens": 100 } }
}
```

Every entry says the same thing: system prompt "You are a helpful
assistant.", user prompt "Say hello in one sentence.", at most 100 tokens.

## What's intentionally missing

- **No `model` field.** The gateway's routing config or the listing's
  `upstream_access_config` selects the upstream model; the playground merges
  the service's routing key into the body it sends. Bedrock Converse takes the
  model id in the path instead.
- **No `stream` field.** Non-streaming responses are simpler to
  validate in tests; streaming variants belong in separate presets.
- **No `bedrock_invoke` entry.** InvokeModel's body is the model family's own
  (Anthropic-on-Bedrock, Llama, Titan, …), so there is no one body to offer.
  The playground falls back to a blank body for it.

## Conventions

- `max_tokens` is kept small (≤ 100) so the request completes fast
  against any upstream regardless of per-token latency.
- A new request format gets a new key here, in a new version.

## Versions

### v2 — one body per request format

- Keyed by format: `openai`, `anthropic`, `cohere`, `dashscope`,
  `bedrock_converse`. The `openai` entry is v1's body.
- `applies_to` no longer requires an OpenAI upstream: every chat service gets
  this template, and `llm_request_template_anthropic` is superseded by it.
- Needs a playground that picks a format's entry (unitysvc/unitysvc#2508).
  An older one shows the whole map as the body.

### v1 — initial release

- Two messages (system + user), `max_tokens = 100`, no model field,
  non-streaming.
