+++
preset_name = "llm_code_example_embed_python"
category = "code_example"
mime_type = "python"
file = "code-example-embed.py.j2"
description = "Python example: request OpenAI-compatible embeddings for a list of inputs"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-embed-python — embeddings via `requests`

Customer-facing Python example for OpenAI-compatible embedding
endpoints (`/v1/embeddings`-shaped) routed through the UnitySVC LLM
gateway.

## Environment variables

- `SERVICE_BASE_URL` — embeddings endpoint (gateway URL or upstream
  URL in local-testing mode). The gateway sets this to its own
  `/v1/embeddings` route.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional. Defaults to the listing's `offering.name`.

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
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from env.
