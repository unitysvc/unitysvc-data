+++
preset_name = "llm_code_example_anthropic_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-anthropic.js.j2"
description = "JavaScript example: send a message to an Anthropic Messages API endpoint via built-in fetch"
is_active = true
is_public = true
+++

# llm / code-example-anthropic-javascript — Anthropic Messages API via built-in fetch

Customer-facing JavaScript example for upstreams that speak the
Anthropic Messages API. Uses node's built-in `fetch` (≥ Node 18) so
the example runs in any sandbox without installing the
`@anthropic-ai/sdk` package — production code typically wants the
SDK, but the example needs to be standalone.

The Anthropic API is **not** OpenAI-compatible; the OpenAI JS preset
posts to `/chat/completions` with a different request shape and would
404 against any Anthropic endpoint.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required. Bearer token: customer's svcpass for
  gateway access, or an upstream Anthropic key when wired as a secret
  (BYOK).

## Versions

### v1 — initial release

- `fetch("{base}/v1/messages")` with `x-api-key`, `anthropic-version:
  2023-06-01`, top-level `system`, and required `max_tokens: 1024`.
- HTTP non-2xx surfaces the response body and exits non-zero.
- Concatenates text from any `content[type=text]` blocks for output.
