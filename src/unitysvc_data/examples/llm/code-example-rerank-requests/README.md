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

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Conventions

- Sends a five-document candidate set with one obvious correct
  answer, so even a low-quality reranker is easy to assert against.
- Prints the raw response — the field set differs between providers
  (`results` vs `documents`), so leave parsing to the caller.

## Versions

### v1 — initial release

- POST `model` + `query` + `top_n` + `documents`.
- Required env vars fail fast with `KeyError` if missing.
