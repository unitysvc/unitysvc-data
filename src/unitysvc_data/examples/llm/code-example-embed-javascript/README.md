+++
preset_name = "llm_code_example_embed_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-embed.js.j2"
description = "JavaScript example: request OpenAI-compatible embeddings via fetch"
is_active = true
is_public = true
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-embed-javascript — embeddings via `fetch`

Customer-facing Node.js example for OpenAI-compatible embedding
endpoints. Uses the built-in `fetch` API (Node 18+).

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release

- `fetch` POST with `model` + two-element `input` array.
- A small loop checks the three required env vars before the request
  and exits 1 on any missing one.
- Prints the dimensionality and first three components of each
  returned vector.
