+++
preset_name = "llm_code_example_embed_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-embed.js.j2"
description = "JavaScript example: request OpenAI-compatible embeddings via fetch"
is_active = true
is_public = true
+++

# llm / code-example-embed-javascript — embeddings via `fetch`

Customer-facing Node.js example for OpenAI-compatible embedding
endpoints. Uses the built-in `fetch` API (Node 18+).

## Environment variables

- `SERVICE_BASE_URL` — embeddings endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional; defaults to `offering.name`.

## Versions

### v1 — initial release

- `fetch` POST with `model` + two-element `input` array.
- Prints the dimensionality and first three components of each
  returned vector.
