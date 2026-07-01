+++
preset_name = "llm_code_example_openai_to_anthropic_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "Shell example: OpenAI-format request against an openai->anthropic translation gateway (customer speaks OpenAI; upstream is Anthropic) via curl"
is_active = true
is_public = true
+++

# llm / code-example-openai-to-anthropic-shell — OpenAI-format call to an openai->anthropic translation gateway

Customer-facing shell (`curl`) example for a **translation** service where the
customer speaks the OpenAI chat-completions API (`/v1/chat/completions`) and the upstream speaks the
Anthropic Messages API (`/v1/messages`). The gateway translates the request out to the upstream and
translates the response back.

Because the same example has to render for both sides of the wire, it is
driven by the `local_testing` flag rather than an SDK:

- **`local_testing`** — call the Anthropic **upstream** directly in its
  native anthropic-shape (Anthropic Messages API (`/v1/messages`)), with no gateway and no translation. Used
  by the connectivity / local-test harness to exercise the raw upstream.
- **otherwise** — call the **gateway** in openai-shape (OpenAI chat-completions API (`/v1/chat/completions`)); the
  gateway translates to the Anthropic upstream and back.

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
- Posts a single `"Say this is a test"` user message; Anthropic-shape
  calls set the required top-level `max_tokens: 64`.
- `curl --fail-with-body` so upstream / gateway errors surface as a non-zero exit.
