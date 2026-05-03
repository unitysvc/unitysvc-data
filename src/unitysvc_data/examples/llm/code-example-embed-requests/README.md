+++
preset_name = "llm_code_example_embed_requests"
category = "code_example"
mime_type = "python"
file = "code-example-embed.py.j2"
description = "Python example: request OpenAI-compatible embeddings for a list of inputs"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-embed-requests — embeddings via `requests`

Customer-facing Python example for OpenAI-compatible embedding
endpoints (`/v1/embeddings`-shaped) routed through the UnitySVC LLM
gateway.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Conventions

- Posts a list of two short strings as `input` and prints the
  dimensionality + the first three components of each returned vector
  so the script verifies the response shape without dumping a wall of
  floats.
- Uses the OpenAI-compatible response shape: `data[].embedding` is a
  flat list of floats.

## Versions

### v1 — initial release

- `requests.post` against `SERVICE_BASE_URL` with `model` + `input`.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from env;
  missing any of the three fails fast with `KeyError`.
