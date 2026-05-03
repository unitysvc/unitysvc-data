+++
preset_name = "llm_code_example_cohere"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a chat completion request via the cohere SDK (v2 chat API)"
is_active = true
is_public = true
meta = { requirements = ["cohere"] }
+++

# llm / code-example-cohere — chat via the `cohere` SDK (v2)

Customer-facing Python example for Cohere-hosted LLM services using
the official `cohere` SDK and Cohere's v2 chat API
(`client.chat(...)`).

The same model can also be reached via Cohere's
[OpenAI compatibility layer](https://docs.cohere.com/v2/docs/compatibility-api)
using `llm_code_example_openai` — sellers who configure the upstream
at `https://api.cohere.ai/compatibility/v1` get OpenAI-shape calls
for free. This preset is the idiomatic Cohere-SDK route, and is what
customers who already depend on `cohere` will copy-paste.

## Why ship a Cohere-flavored preset

Cohere's native v1/v2 surface uses Cohere-specific endpoints
(`/v1/chat`, `/v1/embed`, `/v1/rerank`, …) and SDK methods (`.chat()`,
not `.chat.completions.create()`). The compat layer only exposes a
subset (chat, embeddings, transcription); features like rerank,
citations, and connectors require the native API. Same pattern as
`llm_code_example_anthropic` and `llm_code_example_cerebras` — one
extra preset per provider whose SDK is meaningfully different.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required. Bearer token: customer's svcpass for
  gateway access, or an upstream Cohere key when wired as a secret
  (BYOK). The Cohere SDK accepts it via the `api_key` kwarg and adds
  the right auth header itself.

## Versions

### v1 — initial release

- `cohere.ClientV2(base_url=..., api_key=...)` then `client.chat(...)`
  with a system + user message pair.
- Walks `response.message.content` blocks for `type=text` and
  concatenates them — Cohere v2 returns content as typed blocks
  similar to Anthropic, not as a flat string.
- HTTP errors surface as `cohere.errors.*` exceptions (non-zero exit).
