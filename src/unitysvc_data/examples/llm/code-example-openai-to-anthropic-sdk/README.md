+++
preset_name = "llm_code_example_openai_to_anthropic_sdk"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: OpenAI-format request against an openai->anthropic translation gateway (customer speaks OpenAI; upstream is Anthropic) using the official SDKs — Anthropic SDK for the direct-upstream test, OpenAI SDK for the gateway test"
is_active = true
is_public = true
meta = { requirements = ["openai", "anthropic"] }
+++

# llm / code-example-openai-to-anthropic-sdk — OpenAI-format call to an openai->anthropic translation gateway (SDK)

SDK-based counterpart of `code-example-openai-to-anthropic-requests`. The
customer speaks the OpenAI chat-completions API (`/v1/chat/completions`) and the
upstream speaks the Anthropic Messages API (`/v1/messages`); the gateway
translates between them. Each side is exercised with its official SDK. Requires
both SDKs installed (`meta.requirements = ["openai", "anthropic"]`).

Driven by the `local_testing` flag:

- **`local_testing`** — call the Anthropic **upstream** directly with the
  **Anthropic SDK** (`client.messages.create`), with no gateway/translation.
- **otherwise** — call the **gateway** with the **OpenAI SDK**
  (`client.chat.completions.create`); the gateway translates the request out to
  the Anthropic upstream and translates the response back.

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
- Posts a single `"Say this is a test"` user message; the Anthropic-shape call
  sets the required top-level `max_tokens: 64`.
