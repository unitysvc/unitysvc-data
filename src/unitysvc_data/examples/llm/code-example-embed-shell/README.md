+++
preset_name = "llm_code_example_embed_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-embed.sh.j2"
description = "Shell example: request OpenAI-compatible embeddings via curl"
is_active = true
is_public = true
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-embed-shell — embeddings via `curl`

Customer-facing shell example for OpenAI-compatible embedding
endpoints. Sends two short strings as `input` and prints the raw
JSON response.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release

- `curl` POST with `model` + two-element `input` array.
- Heredoc JSON so no `jq` dependency is required.
- `${VAR:?msg}` guards on the three required env vars so a missing
  one fails before the request is sent.
