+++
preset_name = "llm_code_example_anthropic_to_openai_stream_sdk"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Streaming Python example: Anthropic-format SSE request against an anthropic->openai translation gateway using the official SDKs — OpenAI SDK for the direct-upstream test, Anthropic SDK for the gateway test"
is_active = true
is_public = true
meta = { variant = "Anthropic-style (streaming)", requirements = ["openai", "anthropic"] }
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-anthropic-to-openai-stream-sdk — streaming Anthropic-format call to an anthropic->openai translation gateway (SDK)

SDK-based counterpart of `code-example-anthropic-to-openai-stream-requests`:
streaming (SSE) rather than a buffered body — a distinct gateway path
(frame-by-frame translation) — exercised with the official SDKs instead of raw
`requests`. Requires both SDKs installed (`meta.requirements = ["openai",
"anthropic"]`).

Driven by the `local_testing` flag:

- **`local_testing`** — stream from the OpenAI **upstream** directly with the
  **OpenAI SDK** (`stream=True`, `chat.completion.chunk` deltas).
- **otherwise** — stream from the **gateway** with the **Anthropic SDK**
  (`client.messages.stream`); the gateway translates the OpenAI upstream stream
  into Anthropic `content_block_delta` events.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.
- `{{ local_testing }}` — set by the test harness when exercising the upstream directly.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or
  an upstream API key when wired as a secret (BYOK). The OpenAI SDK sends it as
  `Authorization: Bearer`; the Anthropic SDK sends it as `x-api-key`.

## Versions

### v1 — initial release
- Single `"Say this is a test"` message; prints the streamed text deltas as they
  arrive. The Anthropic-shape call sets the required `max_tokens: 64`.
