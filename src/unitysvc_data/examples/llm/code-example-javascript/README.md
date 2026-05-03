+++
preset_name = "llm_code_example_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example.js.j2"
description = "JavaScript example: send a chat completion request to an OpenAI-compatible LLM"
is_active = true
is_public = true
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-javascript — chat completion via `fetch`

Customer-facing Node.js example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses the built-in
`fetch` API (Node 18+, no `node-fetch` dependency) so it runs without
installing anything extra.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release

- `fetch` POST against `SERVICE_BASE_URL` with `model` + two-message
  `messages` array.
- A small loop checks the three required env vars before the request
  and exits 1 on any missing one.
- Non-2xx responses are surfaced with status + body and exit code 1.
