+++
preset_name = "llm_code_example_openai_to_anthropic_stream_sdk"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Streaming Python example: OpenAI-format SSE request against an openai->anthropic translation gateway using the official SDKs — Anthropic SDK for the direct-upstream test, OpenAI SDK for the gateway test"
is_active = true
is_public = true
meta = { variant = "OpenAI-style (streaming)", requirements = ["openai", "anthropic"], min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "chat", dialect = "openai", upstream = "anthropic", feature = "streaming" }
+++

# llm / code-example-openai-to-anthropic-stream-sdk — streaming OpenAI-format call to an openai->anthropic translation gateway (SDK)

SDK-based counterpart of `code-example-openai-to-anthropic-stream-requests`:
streaming (SSE) — a distinct gateway path (frame-by-frame translation) —
exercised with the official SDKs. The customer speaks OpenAI chat-completions;
the upstream speaks the Anthropic Messages API. Requires both SDKs installed
(`meta.requirements = ["openai", "anthropic"]`).

Driven by the `local_testing` flag:

- **`local_testing`** — stream from the Anthropic **upstream** directly with the
  **Anthropic SDK** (`client.messages.stream`).
- **otherwise** — stream from the **gateway** with the **OpenAI SDK**
  (`stream=True`); the gateway translates the Anthropic upstream stream into
  OpenAI `chat.completion.chunk` deltas.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.
- `{{ local_testing }}` — set by the test harness when exercising the upstream directly.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or
  an upstream API key when wired as a secret (BYOK). The Anthropic SDK sends it
  as `x-api-key`; the OpenAI SDK sends it as `Authorization: Bearer`.

## Versions

### v1 — initial release
- Single `"Say this is a test"` message; prints the streamed text deltas as they
  arrive. The Anthropic-shape call sets the required `max_tokens: 64`.
- **Amended in 0.2.2**: skips chunks whose `choices` is empty. The OpenAI API
  closes a stream with a usage-only chunk when `stream_options.include_usage` is
  set, and some compatible providers send that chunk whether you asked or not —
  indexing `[0]` unconditionally raised `IndexError` at the very end of an
  otherwise successful call. The guard stays visible: it is client code a
  customer needs, which is why the JavaScript sibling always had it.
- **Amended in 0.2.2**: asserts the stream actually produced something, wrapped
  in `{%- if not customer_display %}`. A model that accepts the request and
  ignores `stream=True` yields nothing, so the loop body never ran and the
  example exited 0 with no output verified (unitysvc/unitysvc-data#80).
- **Amended in 0.2.2**: `max_tokens` raised from 64 to 1024. A reasoning model
  spends the whole 64-token budget inside its thinking block and emits no
  visible text at all, so the example returned nothing; 1024 lets it finish and
  answer. Native Anthropic examples in this collection have always used 1024.
