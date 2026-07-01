+++
preset_name = "llm_code_example_anthropic_to_openai_stream_requests"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: streaming Anthropic-format request against an anthropic->openai translation gateway (customer speaks Anthropic; upstream is OpenAI) via the requests library"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-anthropic-to-openai-stream-requests — streaming Anthropic-format call to an anthropic->openai translation gateway

Customer-facing Python (`requests`) example for a **translation** service where the
customer speaks the Anthropic Messages API (`/v1/messages`) and the upstream speaks the
OpenAI chat-completions API (`/v1/chat/completions`). The gateway translates the request out to the upstream and
translates the response (and each streamed event frame) back.

Because the same example has to render for both sides of the wire, it is
driven by the `local_testing` flag rather than an SDK:

- **`local_testing`** — call the OpenAI **upstream** directly in its
  native openai-shape (OpenAI chat-completions API (`/v1/chat/completions`)), with no gateway and no translation. Used
  by the connectivity / local-test harness to exercise the raw upstream.
- **otherwise** — call the **gateway** in anthropic-shape (Anthropic Messages API (`/v1/messages`)); the
  gateway streams server-sent events and translates to the OpenAI upstream and back.

This preset was extracted from the `unitysvc-stress` `stress-llm`
templates so translation services in any repo can reference it as a
`$doc_preset` instead of carrying inline example files.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.
- `{{ local_testing }}` — set by the test harness when exercising the upstream directly.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access,
  or an upstream API key when the seller / customer wires it as a secret (BYOK).
  Sent as `Authorization: Bearer` on OpenAI-shape calls and as `x-api-key`
  (with `anthropic-version: 2023-06-01`) on Anthropic-shape calls.

## Versions

### v1 — initial release

- Streaming variant — reads SSE lines via `requests` `iter_lines` frame by frame.
- Posts a single `"Say this is a test"` user message; Anthropic-shape
  calls set the required top-level `max_tokens: 64`.
- `response.raise_for_status()` so upstream / gateway errors surface as a non-zero exit.
