+++
preset_name = "llm_code_example_streaming_openai"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: stream a chat completion from an OpenAI-compatible LLM using the openai SDK"
is_active = true
is_public = true
meta = { requirements = ["openai"] }
+++

# llm / code-example-streaming-openai — streaming chat completion via the `openai` SDK

Customer-facing Python example for OpenAI-compatible upstreams
that support server-sent-events streaming on
`/v1/chat/completions`. Prints tokens as they arrive instead of
waiting for the full response.

The companion preset `llm_code_example_openai` shows the
non-streaming form. Use this preset when the caller wants
incremental output (chat UIs, long-form generation, etc.) and the
upstream advertises streaming support.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release

- `client.chat.completions.create(..., stream=True)` returns a
  generator of `ChatCompletionChunk` objects.
- Each chunk's `delta.content` is `None` between tokens; the
  example skips empty deltas to avoid printing `None`.
- `print(..., end="", flush=True)` so tokens appear immediately
  rather than buffered to a newline.
