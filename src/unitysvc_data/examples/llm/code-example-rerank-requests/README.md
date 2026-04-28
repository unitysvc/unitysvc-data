+++
preset_name = "llm_code_example_rerank_requests"
category = "code_example"
mime_type = "python"
file = "code-example-rerank.py.j2"
description = "Python example: rerank a candidate document set against a query"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-rerank-requests — rerank via `requests`

Customer-facing Python example for rerank endpoints (Cohere-style
`/v2/rerank` payload: `query` + `documents` → ranked indices with
relevance scores).

## Environment variables (all required)

- `SERVICE_BASE_URL` — rerank endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

## Conventions

- Sends a five-document candidate set with one obvious correct
  answer, so even a low-quality reranker is easy to assert against.
- Prints the raw response — the field set differs between providers
  (`results` vs `documents`), so leave parsing to the caller.

## Versions

### v1 — initial release

- POST `model` + `query` + `top_n` + `documents`.
- Required env vars fail fast with `KeyError` if missing.
- Plain Python (no `.j2` suffix) — no Jinja2 expansion.
