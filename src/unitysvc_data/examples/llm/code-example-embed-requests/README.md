+++
preset_name = "llm_code_example_embed_requests"
category = "code_example"
mime_type = "python"
file = "code-example-embed.py.j2"
description = "Python example: request OpenAI-compatible embeddings for a list of inputs"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-embed-requests — embeddings via `requests`

Customer-facing Python example for OpenAI-compatible embedding
endpoints (`/v1/embeddings`-shaped) routed through the UnitySVC LLM
gateway.

## Environment variables (all required)

- `SERVICE_BASE_URL` — embeddings endpoint (gateway URL or upstream
  URL in local-testing mode). The gateway sets this to its own
  `/v1/embeddings` route.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

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
- Plain Python (no `.j2` suffix) — no Jinja2 expansion.
