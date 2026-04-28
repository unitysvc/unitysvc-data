+++
preset_name = "llm_code_example_streaming_openai_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example.js.j2"
description = "JavaScript example: stream a chat completion from an OpenAI-compatible LLM using the openai SDK"
is_active = true
is_public = true
meta = { requirements = ["openai"] }
+++

# llm / code-example-streaming-openai-javascript — streaming chat completion via the `openai` Node.js SDK

Customer-facing Node.js example for streaming OpenAI-compatible
chat completions. Prints tokens to stdout as they arrive.

The companion preset `llm_code_example_openai_javascript` shows
the non-streaming form. Use this preset when the caller wants
incremental output (chat UIs, long-form generation, etc.) and the
upstream advertises streaming support.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier.

## Versions

### v1 — initial release

- `await client.chat.completions.create({ ..., stream: true })`
  returns an async iterator of chunks; `for await (...)` consumes
  it.
- Optional chaining (`chunk.choices[0]?.delta?.content`) so a
  malformed chunk doesn't crash the loop.
- CommonJS `require("openai")` so the file runs as plain
  `node code-example.js`.
