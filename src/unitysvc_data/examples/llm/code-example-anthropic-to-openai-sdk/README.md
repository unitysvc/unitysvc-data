+++
preset_name = "llm_code_example_anthropic_to_openai_sdk"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: Anthropic-format request against an anthropic->openai translation gateway (customer speaks Anthropic; upstream is OpenAI) using the official SDKs — OpenAI SDK for the direct-upstream test, Anthropic SDK for the gateway test"
is_active = true
is_public = true
meta = { requirements = ["openai", "anthropic"] }
+++

# llm / code-example-anthropic-to-openai-sdk — Anthropic-format call to an anthropic->openai translation gateway (SDK)

SDK-based counterpart of `code-example-anthropic-to-openai-requests`. Same
**translation** service — the customer speaks the Anthropic Messages API
(`/v1/messages`) and the upstream speaks the OpenAI chat-completions API
(`/v1/chat/completions`) — but each side is exercised with its official SDK
instead of raw `requests`. This reads more clearly at the cost of requiring
both SDKs installed (hence `meta.requirements = ["openai", "anthropic"]`).

Driven by the `local_testing` flag rather than a single library:

- **`local_testing`** — call the OpenAI **upstream** directly with the **OpenAI
  SDK** (`client.chat.completions.create`), with no gateway and no translation.
  Used by the connectivity / local-test harness to exercise the raw upstream.
- **otherwise** — call the **gateway** with the **Anthropic SDK**
  (`client.messages.create`); the gateway translates the request out to the
  OpenAI upstream and translates the response back.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.
- `{{ local_testing }}` — set by the test harness when exercising the upstream directly.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or
  an upstream API key when wired as a secret (BYOK). The OpenAI SDK sends it as
  `Authorization: Bearer`; the Anthropic SDK sends it as `x-api-key` (with
  `anthropic-version`).

## Versions

### v1 — initial release
- Posts a single `"Say this is a test"` user message; the Anthropic-shape call
  sets the required top-level `max_tokens: 64`.
