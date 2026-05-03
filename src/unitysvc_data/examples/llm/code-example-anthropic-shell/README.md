+++
preset_name = "llm_code_example_anthropic_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-anthropic.sh.j2"
description = "curl example: POST a message to an Anthropic Messages API endpoint"
is_active = true
is_public = true
+++

# llm / code-example-anthropic-shell — Anthropic Messages API via curl

Customer-facing shell example for upstreams that speak the Anthropic
Messages API (`/v1/messages`) — primarily Claude-family models. The
Anthropic API is **not** OpenAI-compatible:

- Endpoint: `/v1/messages`, not `/v1/chat/completions`
- Auth header: `x-api-key`, not `Authorization: Bearer`
- Required: `anthropic-version` header (we pin to `2023-06-01`, the stable date)
- Required: `max_tokens` field at the top level of the body
- The `system` prompt is a top-level field, **not** an entry in `messages`
- Response shape is `content[].text`, not `choices[].message.content`

So Anthropic-shaped upstreams need their own curl preset rather than
reusing `llm_code_example_shell`.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required. Bearer token: customer's svcpass for
  gateway access, or an upstream Anthropic key when wired as a secret
  (BYOK).

## Versions

### v1 — initial release

- POST `/v1/messages` with a top-level `system` prompt, one user
  message, and `max_tokens: 1024`.
- `curl --fail-with-body` so 4xx / 5xx surface as non-zero exit + body
  in stderr.
