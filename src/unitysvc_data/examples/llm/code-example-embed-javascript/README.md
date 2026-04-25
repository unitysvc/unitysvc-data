+++
preset_name = "llm_code_example_embed_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-embed.js"
description = "JavaScript example: request OpenAI-compatible embeddings via fetch"
is_active = true
is_public = true
+++

# llm / code-example-embed-javascript — embeddings via `fetch`

Customer-facing Node.js example for OpenAI-compatible embedding
endpoints. Uses the built-in `fetch` API (Node 18+).

## Environment variables (all required)

- `SERVICE_BASE_URL` — embeddings endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

## Versions

### v1 — initial release

- `fetch` POST with `model` + two-element `input` array.
- A small loop checks the three required env vars before the request
  and exits 1 on any missing one.
- Prints the dimensionality and first three components of each
  returned vector.
- Plain JavaScript (no `.j2` suffix) — no Jinja2 expansion.
