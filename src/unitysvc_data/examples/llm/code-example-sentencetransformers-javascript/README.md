+++
preset_name = "llm_code_example_sentencetransformers_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-sentencetransformers.js.j2"
description = "JavaScript example: sentence-similarity via HF sentence-transformers /models/<model>"
is_active = true
is_public = true
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-sentencetransformers-javascript — sentence similarity via `fetch`

Customer-facing Node.js example for HuggingFace sentence-transformers similarity endpoints.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release
