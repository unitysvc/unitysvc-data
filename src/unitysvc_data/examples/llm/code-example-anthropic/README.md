+++
preset_name = "llm_code_example_anthropic"
category = "code_example"
mime_type = "python"
file = "code-example.py"
description = "Python example: send a message to an Anthropic-API-compatible LLM using the anthropic SDK"
is_active = true
is_public = true
meta = { requirements = ["anthropic"] }
+++

# llm / code-example-anthropic — Anthropic Messages API via the `anthropic` SDK

Customer-facing Python example for upstreams that speak the
Anthropic Messages API (`/v1/messages`) — primarily Claude-family
models. The Anthropic API is **not** OpenAI-compatible: the
endpoint differs (`/v1/messages` vs `/v1/chat/completions`),
`max_tokens` is required, the `system` prompt is a top-level field
rather than a message, and the response shape is `content[].text`
rather than `choices[].message.content`. So Anthropic-shaped
upstreams need their own preset rather than reusing
`llm_code_example_openai`.

## Environment variables (all required)

- `SERVICE_BASE_URL` — Messages endpoint, passed as the SDK's
  `base_url`.
- `UNITYSVC_API_KEY` — passed as the SDK's `api_key`.
- `MODEL` — interface-specific model identifier.

## Versions

### v1 — initial release

- `Anthropic(base_url=..., api_key=...)` then
  `client.messages.create(...)` with `max_tokens=1024` and a
  top-level `system` prompt.
- HTTP errors surface as `anthropic.APIStatusError` (non-zero
  exit), so no explicit status check is needed.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from the
  environment; missing any of the three fails fast with `KeyError`.
